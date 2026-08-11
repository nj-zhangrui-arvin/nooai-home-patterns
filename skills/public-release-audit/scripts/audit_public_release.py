#!/usr/bin/env python3
"""Fail-closed privacy and secret gate for a public release.

The reporter never prints matching content or denylist values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


MAX_TEXT_BYTES = 2_000_000
SKIP_DIRS = {".git"}
FORBIDDEN_DIRS = {
    ".omx",
    ".playwright-cli",
    ".storage",
    "__pycache__",
    "backups",
    "coverage",
    "data",
    "ha-backup",
    "logs",
    "node_modules",
    "out",
    "output",
    "tmp",
}
FORBIDDEN_SUFFIXES = {
    ".blend",
    ".db",
    ".dxf",
    ".fbx",
    ".gif",
    ".glb",
    ".gltf",
    ".jpeg",
    ".jpg",
    ".key",
    ".kdbx",
    ".log",
    ".mobileprovision",
    ".mov",
    ".mp3",
    ".mp4",
    ".obj",
    ".p12",
    ".pem",
    ".pfx",
    ".pyc",
    ".sqlite",
    ".sqlite3",
    ".stl",
    ".svg",
    ".wav",
    ".webp",
}
MEDIA_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}
FORBIDDEN_SUFFIXES -= MEDIA_SUFFIXES
FORBIDDEN_NAMES = {
    ".env",
    ".env." + "local",
    ".secrets.baseline",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "auth",
    "auth_provider.home-assistant",
    "core.config_entries",
    "core.device_registry",
    "core.entity_registry",
    "core.restore_state",
    "credentials.json",
    "home-assistant_v2.db",
    "id_ed25519",
    "id_rsa",
    "known_hosts",
    "secrets.yaml",
}


@dataclass(frozen=True)
class Finding:
    path: str
    rule: str
    scope: str = "tree"
    line: int | None = None
    object_id: str | None = None
    digest: str | None = None


def _joined(*parts: str) -> str:
    return "".join(parts)


def rules() -> list[tuple[str, re.Pattern[str]]]:
    patterns = {
        "private-ipv4": r"(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}",
        "private-ipv6": r"(?i)\b(?:f[cd][0-9a-f]{2}|fe[89ab][0-9a-f])(?::[0-9a-f]{0,4}){2,}\b",
        "private-local-host": r"(?i)\b[a-z0-9][a-z0-9.-]*\.local\b",
        "mac-address": r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b",
        "device-uuid": r"(?i)\b(?!0{8}-0{4}-0{4}-0{4}-0{12}\b)[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
        "mac-user-path": re.escape("/" + "Users" + "/"),
        "linux-home-path": re.escape("/" + "home" + "/"),
        "windows-user-path": re.escape("C:" + "\\" + "Users" + "\\"),
        "unc-path": r"\\\\[A-Za-z0-9._-]+\\[A-Za-z0-9$._-]+",
        "private-key": _joined(
            r"BEGIN (?:(?:OPENSSH|RSA|EC|DSA|ENCRYPTED) )?",
            _joined(r"PRIVATE ", r"KEY|BEGIN PGP PRIVATE ", r"KEY BLOCK"),
        ),
        "aws-access-key": r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
        "github-token": _joined(r"\bgh", r"[oprsu]_[A-Za-z0-9]{20,}\b"),
        "openai-token": _joined(r"\bsk", r"-[A-Za-z0-9_-]{20,}\b"),
        "slack-token": r"\bxox[baprs]-[A-Za-z0-9-]{16,}\b",
        "google-api-key": r"\bAIza[0-9A-Za-z_-]{30,}\b",
        "jwt": _joined(r"\beyJ[A-Za-z0-9_-]{8,}\.", r"[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
        "authenticated-url": r"(?i)https?://[^\s/:]+:[^\s/@]+@[^\s]+",
        "bearer-token": r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{12,}",
        "git-lfs-pointer": r"^version https://git-lfs\.github\.com/spec/v1$",
        "secret-assignment": _joined(
            r"(?i)(?:^|[^A-Za-z0-9])(?:[A-Za-z0-9_-]{0,40})?",
            r"(?:password|passwd|secret|psk|api[_-]?key|access[_-]?key|client[_-]?secret|access[_-]?token|refresh[_-]?token|webhook[_-]?id|authorization|cookie)\s*[:=]\s*[\"']?",
            r"(?!redacted\b|example\b|placeholder\b|<[^>]+>)[^\s\"']{8,}",
        ),
        "ha-cloud-url": r"(?i)https://[a-z0-9-]{8,}\.ui\.nabucasa\.com\b",
        "homekit-pairing-code": r"\b\d{3}-\d{2}-\d{3}\b",
        "home-coordinate": _joined(
            r"(?i)\b(?:latitude|longitude|home_latitude|home_longitude)\s*[:=]\s*",
            r"-?(?!0(?:\.0+)?\b)\d{1,3}\.\d{3,}\b",
        ),
        "ha-network-key": _joined(
            r"(?i)\b(?:noise[_-]?psk|encryption[_-]?key|network[_-]?key|zigbee[_-]?key|zwave[_-]?key)\s*[:=]\s*[\"']?",
            r"(?!example\b|placeholder\b|<[^>]+>)(?:[A-Za-z0-9+/]{32,}={0,2}|(?:[0-9a-f]{2}[, :_-]?){16,})",
        ),
        "email-address": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    }
    return [(name, re.compile(pattern)) for name, pattern in patterns.items()]


def _allowed_example_email(value: str) -> bool:
    lowered = value.lower()
    return lowered.endswith("@example.com")


def _allowed_example_name(value: str) -> bool:
    return value.strip().lower() in {"public example", "public release bot", "example author"}


def _path_findings(path: PurePosixPath, scope: str, object_id: str | None = None) -> list[Finding]:
    findings: list[Finding] = []
    parts = set(path.parts)
    if parts & FORBIDDEN_DIRS:
        findings.append(Finding(str(path), "forbidden-directory", scope, object_id=object_id))
    name = path.name.lower()
    if name in FORBIDDEN_NAMES or name.startswith(".env."):
        findings.append(Finding(str(path), "forbidden-file-type", scope, object_id=object_id))
    if path.suffix.lower() in FORBIDDEN_SUFFIXES:
        findings.append(Finding(str(path), "forbidden-file-type", scope, object_id=object_id))
    if any(pattern.search(str(path)) for _, pattern in rules()):
        findings.append(Finding(str(path), "sensitive-file-name", scope, object_id=object_id))
    return findings


def _load_media_manifest(path: Path | None) -> dict[str, str]:
    """Load exact, reviewable media grants as {relative_path: sha256}."""

    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("version") != 1 or not isinstance(payload.get("assets"), list):
        raise ValueError("media manifest must use version 1 and an assets list")
    approved: dict[str, str] = {}
    required = {"path", "sha256", "source", "license", "privacy_reviewed", "metadata_removed"}
    for item in payload["assets"]:
        if not isinstance(item, dict) or not required <= set(item):
            raise ValueError("media manifest asset is missing required review fields")
        relative = PurePosixPath(str(item["path"]))
        digest = str(item["sha256"]).lower()
        if relative.is_absolute() or ".." in relative.parts or len(digest) != 64:
            raise ValueError("media manifest contains an unsafe path or digest")
        if not item["privacy_reviewed"] or not item["metadata_removed"]:
            raise ValueError("media manifest asset must pass privacy and metadata review")
        if not str(item["source"]).strip() or not str(item["license"]).strip():
            raise ValueError("media manifest asset needs source and license")
        approved[str(relative)] = digest
    return approved


def _scan_bytes(
    path: PurePosixPath,
    data: bytes,
    *,
    scope: str,
    object_id: str | None = None,
    deny_literals: Iterable[str] = (),
    allowed_emails: Iterable[str] = (),
    approved_media: dict[str, str] | None = None,
) -> list[Finding]:
    digest = hashlib.sha256(data).hexdigest()
    findings = _path_findings(path, scope, object_id)
    if findings:
        return findings
    if path.suffix.lower() in MEDIA_SUFFIXES:
        expected = (approved_media or {}).get(str(path))
        if expected == digest:
            return []
        return [Finding(str(path), "media-not-approved", scope, object_id=object_id, digest=digest)]
    if len(data) > MAX_TEXT_BYTES:
        return [Finding(str(path), "oversized-file", scope, object_id=object_id, digest=digest)]
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return [Finding(str(path), "binary-or-non-utf8", scope, object_id=object_id, digest=digest)]
    if "\x00" in text:
        return [Finding(str(path), "binary-nul-byte", scope, object_id=object_id, digest=digest)]
    allowed = {item.lower() for item in allowed_emails}
    for line_number, line in enumerate(text.splitlines(), 1):
        for name, pattern in rules():
            for match in pattern.finditer(line):
                if name == "email-address":
                    email = match.group(0).lower()
                    if _allowed_example_email(email) or email in allowed:
                        continue
                findings.append(
                    Finding(str(path), name, scope, line_number, object_id, digest)
                )
        for literal in deny_literals:
            if literal and literal in line:
                findings.append(
                    Finding(str(path), "private-denylist-match", scope, line_number, object_id, digest)
                )
                break
    return findings


def scan(
    root: Path,
    *,
    deny_literals: Iterable[str] = (),
    allowed_emails: Iterable[str] = (),
    approved_media: dict[str, str] | None = None,
) -> list[Finding]:
    root = root.resolve()
    findings: list[Finding] = []
    for current, directories, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        kept: list[str] = []
        for directory in sorted(directories):
            path = current_path / directory
            relative = PurePosixPath(path.relative_to(root).as_posix())
            if path.is_symlink():
                findings.append(Finding(str(relative), "symlink-not-allowed"))
            elif directory in SKIP_DIRS:
                continue
            elif directory in FORBIDDEN_DIRS:
                findings.append(Finding(str(relative), "forbidden-directory"))
            else:
                kept.append(directory)
        directories[:] = kept
        for filename in sorted(files):
            path = current_path / filename
            relative = PurePosixPath(path.relative_to(root).as_posix())
            if path.is_symlink():
                findings.append(Finding(str(relative), "symlink-not-allowed"))
                continue
            if path.stat().st_nlink > 1:
                findings.append(Finding(str(relative), "hardlink-not-allowed"))
                continue
            findings.extend(
                _scan_bytes(
                    relative,
                    path.read_bytes(),
                    scope="tree",
                    deny_literals=deny_literals,
                    allowed_emails=allowed_emails,
                    approved_media=approved_media,
                )
            )
    return findings


def _git(root: Path, *args: str, input_data: bytes | None = None) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"git command failed: {' '.join(args)}")
    return completed.stdout


def _git_context(root: Path) -> tuple[Path, PurePosixPath]:
    top = Path(_git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    try:
        prefix = PurePosixPath(root.resolve().relative_to(top).as_posix())
    except ValueError as error:
        raise RuntimeError("public root is outside the Git repository") from error
    return top, prefix


def _in_scope(path: PurePosixPath, prefix: PurePosixPath) -> PurePosixPath | None:
    if str(prefix) == ".":
        return path
    try:
        return path.relative_to(prefix)
    except ValueError:
        return None


def scan_staged(
    root: Path,
    *,
    deny_literals: Iterable[str] = (),
    allowed_emails: Iterable[str] = (),
    approved_media: dict[str, str] | None = None,
) -> list[Finding]:
    top, prefix = _git_context(root)
    output = _git(top, "ls-files", "-s", "-z")
    findings: list[Finding] = []
    for record in output.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, object_id, stage = metadata.decode("ascii").split()
        path = PurePosixPath(raw_path.decode("utf-8", "strict"))
        relative = _in_scope(path, prefix)
        if relative is None:
            continue
        short_id = object_id[:12]
        if stage != "0":
            findings.append(Finding(str(relative), "unmerged-index-entry", "staged", object_id=short_id))
            continue
        if mode == "120000":
            findings.append(Finding(str(relative), "symlink-not-allowed", "staged", object_id=short_id))
            continue
        if mode not in {"100644", "100755"}:
            findings.append(Finding(str(relative), "unsupported-git-mode", "staged", object_id=short_id))
            continue
        data = _git(top, "cat-file", "blob", object_id)
        findings.extend(
            _scan_bytes(
                relative,
                data,
                scope="staged",
                object_id=short_id,
                deny_literals=deny_literals,
                allowed_emails=allowed_emails,
                approved_media=approved_media,
            )
        )
    return findings


def scan_history(
    root: Path,
    *,
    deny_literals: Iterable[str] = (),
    allowed_emails: Iterable[str] = (),
    allowed_names: Iterable[str] = (),
    allowed_remote_hosts: Iterable[str] = (),
    allow_signed_commits: bool = False,
    approved_media: dict[str, str] | None = None,
) -> list[Finding]:
    top, prefix = _git_context(root)
    commits = [item for item in _git(top, "rev-list", "--all").decode().splitlines() if item]
    findings: list[Finding] = []
    if root.resolve() != top:
        findings.append(Finding("<repository>", "public-root-not-git-root", "history"))
    allowed_hosts = {item.lower() for item in allowed_remote_hosts}
    for line in _git(top, "remote", "-v").decode("utf-8", "replace").splitlines():
        fields = line.split()
        if len(fields) < 2:
            continue
        remote = fields[1]
        host: str | None = None
        if "://" in remote:
            from urllib.parse import urlsplit

            parsed = urlsplit(remote)
            host = parsed.hostname
            if parsed.username is not None or parsed.password is not None:
                findings.append(Finding("<git-remote>", "authenticated-git-remote", "history"))
        elif "@" in remote and ":" in remote:
            host = remote.split("@", 1)[1].split(":", 1)[0]
        if host is None or host.lower() not in allowed_hosts:
            findings.append(Finding("<git-remote>", "unapproved-git-remote", "history"))
    seen_blobs: set[str] = set()
    allowed = {item.lower() for item in allowed_emails}
    allowed_author_names = {item.strip().lower() for item in allowed_names}
    refs = _git(top, "for-each-ref", "--format=%(refname)%00%(objecttype)%00%(objectname)")
    for raw_ref in refs.decode("utf-8", "replace").splitlines():
        if not raw_ref:
            continue
        ref_name, object_type, object_id = raw_ref.split("\0", 2)
        findings.extend(
            _scan_bytes(
                PurePosixPath("<git-ref>"),
                ref_name.encode("utf-8"),
                scope="history",
                object_id=object_id[:12],
                deny_literals=deny_literals,
                allowed_emails=allowed_emails,
            )
        )
        if object_type == "tag":
            findings.extend(
                _scan_bytes(
                    PurePosixPath("<annotated-tag>"),
                    _git(top, "cat-file", "tag", object_id),
                    scope="history",
                    object_id=object_id[:12],
                    deny_literals=deny_literals,
                    allowed_emails=allowed_emails,
                )
            )
    for commit in commits:
        metadata = _git(top, "show", "-s", "--format=%an%x00%ae%x00%cn%x00%ce%x00%B", commit).decode(
            "utf-8", "replace"
        )
        author_name, author_email, committer_name, committer_email, message = metadata.split("\0", 4)
        for role, name in (("author", author_name), ("committer", committer_name)):
            lowered_name = name.strip().lower()
            if (
                lowered_name
                and lowered_name not in allowed_author_names
                and not _allowed_example_name(lowered_name)
            ):
                findings.append(
                    Finding("<commit-metadata>", f"unapproved-{role}-name", "history", object_id=commit[:12])
                )
        for role, email in (("author", author_email), ("committer", committer_email)):
            lowered = email.strip().lower()
            if lowered and lowered not in allowed and not _allowed_example_email(lowered):
                findings.append(
                    Finding("<commit-metadata>", f"unapproved-{role}-email", "history", object_id=commit[:12])
                )
        raw_commit = _git(top, "cat-file", "commit", commit)
        commit_headers = raw_commit.split(b"\n\n", 1)[0].splitlines()
        if not allow_signed_commits and any(
            header.startswith((b"gpgsig ", b"gpgsig-sha256 "))
            for header in commit_headers
        ):
            findings.append(
                Finding("<commit-metadata>", "signed-commit-identity-review", "history", object_id=commit[:12])
            )
        findings.extend(
            _scan_bytes(
                PurePosixPath("<commit-message>"),
                message.encode("utf-8"),
                scope="history",
                object_id=commit[:12],
                deny_literals=deny_literals,
                allowed_emails=allowed_emails,
            )
        )
        tree = _git(top, "ls-tree", "-r", "-z", "--full-tree", commit)
        for record in tree.split(b"\0"):
            if not record:
                continue
            metadata_bytes, raw_path = record.split(b"\t", 1)
            mode, kind, object_id = metadata_bytes.decode("ascii").split()
            path = PurePosixPath(raw_path.decode("utf-8", "strict"))
            relative = _in_scope(path, prefix)
            if relative is None:
                continue
            if kind == "commit" or mode == "160000":
                findings.append(Finding(str(relative), "git-submodule-not-allowed", "history", object_id=object_id[:12]))
                continue
            if kind != "blob":
                continue
            if mode == "120000":
                findings.append(Finding(str(relative), "symlink-not-allowed", "history", object_id=object_id[:12]))
                continue
            path_findings = _path_findings(relative, "history", object_id[:12])
            if path_findings:
                findings.extend(path_findings)
                continue
            if relative.suffix.lower() in MEDIA_SUFFIXES:
                findings.extend(
                    _scan_bytes(
                        relative,
                        _git(top, "cat-file", "blob", object_id),
                        scope="history",
                        object_id=object_id[:12],
                        deny_literals=deny_literals,
                        allowed_emails=allowed_emails,
                        approved_media=approved_media,
                    )
                )
                continue
            if object_id in seen_blobs:
                continue
            seen_blobs.add(object_id)
            findings.extend(
                _scan_bytes(
                    relative,
                    _git(top, "cat-file", "blob", object_id),
                    scope="history",
                    object_id=object_id[:12],
                    deny_literals=deny_literals,
                    allowed_emails=allowed_emails,
                    approved_media=approved_media,
                )
            )
    return findings


def scan_unreachable(root: Path) -> list[Finding]:
    top, _ = _git_context(root)
    output = _git(top, "fsck", "--no-reflogs", "--unreachable", "--no-progress")
    findings: list[Finding] = []
    for line in output.decode("utf-8", "replace").splitlines():
        match = re.search(r"unreachable (?:blob|commit|tree|tag) ([0-9a-f]{40,64})", line)
        if match:
            findings.append(
                Finding("<git-object>", "unreachable-object", "unreachable", object_id=match.group(1)[:12])
            )
    return findings


def scan_commit_message(
    path: Path,
    *,
    deny_literals: Iterable[str] = (),
    allowed_emails: Iterable[str] = (),
) -> list[Finding]:
    return _scan_bytes(
        PurePosixPath("<commit-message>"),
        path.read_bytes(),
        scope="commit-message",
        deny_literals=deny_literals,
        allowed_emails=allowed_emails,
    )


def _load_denylist(path: Path | None) -> list[str]:
    if path is None:
        return []
    values = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        value = raw.strip()
        if value and not value.startswith("#"):
            values.append(value)
    return values


def _safe_path(value: str) -> str:
    if any(pattern.search(value) for _, pattern in rules()):
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
        return f"<redacted-path:{digest}>"
    return value


def _print(findings: list[Finding], as_json: bool) -> None:
    if as_json:
        payload = []
        for item in findings:
            record = asdict(item)
            record["path"] = _safe_path(item.path)
            payload.append(record)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    for finding in findings:
        location = f":{finding.line}" if finding.line is not None else ""
        object_part = f" object={finding.object_id}" if finding.object_id else ""
        print(f"{finding.scope}:{finding.rule}: {_safe_path(finding.path)}{location}{object_part}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--history", action="store_true")
    parser.add_argument("--unreachable", action="store_true")
    parser.add_argument("--commit-message", type=Path)
    parser.add_argument("--deny-pattern-file", type=Path)
    parser.add_argument("--media-manifest", type=Path)
    parser.add_argument("--allow-email", action="append", default=[])
    parser.add_argument("--allow-name", action="append", default=[])
    parser.add_argument("--allow-remote-host", action="append", default=[])
    parser.add_argument("--allow-signed-commits", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2
    allowed_emails = list(args.allow_email)
    configured = os.environ.get("PUBLIC_RELEASE_ALLOWED_EMAILS", "")
    allowed_emails.extend(item.strip() for item in configured.split(",") if item.strip())
    try:
        deny_literals = _load_denylist(args.deny_pattern_file)
        approved_media = _load_media_manifest(args.media_manifest)
        findings = scan(
            root,
            deny_literals=deny_literals,
            allowed_emails=allowed_emails,
            approved_media=approved_media,
        )
        if args.staged:
            findings.extend(
                scan_staged(
                    root,
                    deny_literals=deny_literals,
                    allowed_emails=allowed_emails,
                    approved_media=approved_media,
                )
            )
        if args.commit_message:
            findings.extend(
                scan_commit_message(
                    args.commit_message,
                    deny_literals=deny_literals,
                    allowed_emails=allowed_emails,
                )
            )
        if args.history:
            findings.extend(
                scan_history(
                    root,
                    deny_literals=deny_literals,
                    allowed_emails=allowed_emails,
                    allowed_names=args.allow_name,
                    allowed_remote_hosts=args.allow_remote_host,
                    allow_signed_commits=args.allow_signed_commits,
                    approved_media=approved_media,
                )
            )
        if args.unreachable:
            findings.extend(scan_unreachable(root))
    except (OSError, RuntimeError, UnicodeError, ValueError) as error:
        print(f"ERROR: audit could not complete: {error}", file=sys.stderr)
        return 2
    _print(findings, args.json)
    if findings:
        print(f"FAIL: {len(findings)} public-release finding(s)", file=sys.stderr)
        return 1
    print(f"PASS: public release gate passed ({root})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
