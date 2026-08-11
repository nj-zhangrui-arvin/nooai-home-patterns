from __future__ import annotations

import importlib.util
import os
import io
import subprocess
import sys
import tempfile
import unittest
import hashlib
import json
from contextlib import redirect_stdout
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "public-release-audit"
    / "scripts"
    / "audit_public_release.py"
)
SPEC = importlib.util.spec_from_file_location("public_release_audit_tests", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def git(root: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def init_repo(root: Path) -> None:
    git(root, "init", "-q")
    git(root, "config", "user.name", "Public Example")
    git(root, "config", "user.email", "public@example.com")


class PublicReleaseAuditTests(unittest.TestCase):
    def test_media_requires_exact_review_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset = root / "hero.png"
            data = b"synthetic-png-fixture"
            asset.write_bytes(data)
            self.assertIn("media-not-approved", {item.rule for item in MODULE.scan(root)})
            manifest = root / "media-manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "assets": [
                            {
                                "path": "hero.png",
                                "sha256": hashlib.sha256(data).hexdigest(),
                                "source": "synthetic test fixture",
                                "license": "MIT",
                                "privacy_reviewed": True,
                                "metadata_removed": True,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            approved = MODULE._load_media_manifest(manifest)
            self.assertEqual(MODULE.scan(root, approved_media=approved), [])
            asset.write_bytes(data + b"changed")
            self.assertIn(
                "media-not-approved",
                {item.rule for item in MODULE.scan(root, approved_media=approved)},
            )

    def test_history_scans_sensitive_path_even_when_blob_was_seen(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            safe = root / "safe.txt"
            safe.write_text("same synthetic content\n", encoding="utf-8")
            git(root, "add", "safe.txt")
            git(root, "commit", "-q", "-m", "safe")
            safe.rename(root / "secrets.yaml")
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", "sensitive path")
            (root / "secrets.yaml").unlink()
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", "remove path")
            rules = {
                item.rule
                for item in MODULE.scan_history(root, allowed_emails=["public@example.com"])
            }
            self.assertIn("forbidden-file-type", rules)

    def test_annotated_tag_message_is_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            (root / "README.md").write_text("synthetic\n", encoding="utf-8")
            git(root, "add", "README.md")
            git(root, "commit", "-q", "-m", "initial")
            token = "gh" + "p_" + "T" * 24
            git(root, "tag", "-a", "v0.1.0", "-m", token)
            rules = {
                item.rule
                for item in MODULE.scan_history(root, allowed_emails=["public@example.com"])
            }
            self.assertIn("github-token", rules)

    def test_authenticated_https_remote_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            (root / "README.md").write_text("synthetic\n", encoding="utf-8")
            git(root, "add", "README.md")
            git(root, "commit", "-q", "-m", "initial")
            authenticated_remote = "https://" + "user:password" + "@" + "github.com/example/repo.git"
            git(root, "remote", "add", "origin", authenticated_remote)
            rules = {
                item.rule
                for item in MODULE.scan_history(
                    root,
                    allowed_emails=["public@example.com"],
                    allowed_remote_hosts=["github.com"],
                )
            }
            self.assertIn("authenticated-git-remote", rules)

    def test_private_infrastructure_identifiers_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.txt").write_text(
                "host=node." + "loc" + "al\n"
                "ipv6=" + "fd12" + ":3456::1\n"
                "device=" + "123e4567-e89b-12d3-" + "a456-426614174000\n",
                encoding="utf-8",
            )
            found = {item.rule for item in MODULE.scan(root)}
            self.assertTrue({"private-local-host", "private-ipv6", "device-uuid"} <= found)

    def test_hidden_secret_file_and_nul_text_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / (".env" + ".production")).write_text("synthetic", encoding="utf-8")
            (root / "nul.txt").write_bytes(b"valid utf8\x00still binary")
            found = {item.rule for item in MODULE.scan(root)}
            self.assertIn("forbidden-file-type", found)
            self.assertIn("binary-nul-byte", found)

    def test_symlink_and_hardlink_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "target.txt"
            target.write_text("synthetic", encoding="utf-8")
            os.symlink(target, root / "link.txt")
            os.link(target, root / "hard.txt")
            found = {item.rule for item in MODULE.scan(root)}
            self.assertIn("symlink-not-allowed", found)
            self.assertIn("hardlink-not-allowed", found)

    def test_staged_blob_is_scanned_not_working_copy(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            path = root / "config.txt"
            path.write_text("token=" + "gh" + "p_" + "A" * 24 + "\n", encoding="utf-8")
            git(root, "add", "config.txt")
            path.write_text("synthetic clean working copy\n", encoding="utf-8")
            rules = {item.rule for item in MODULE.scan_staged(root)}
            self.assertIn("github-token", rules)

    def test_deleted_secret_remains_blocked_in_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            path = root / "old.txt"
            path.write_text("token=" + "gh" + "p_" + "B" * 24 + "\n", encoding="utf-8")
            git(root, "add", "old.txt")
            git(root, "commit", "-q", "-m", "add synthetic fixture")
            path.unlink()
            git(root, "add", "-u")
            git(root, "commit", "-q", "-m", "remove synthetic fixture")
            rules = {
                item.rule
                for item in MODULE.scan_history(root, allowed_emails=["public@example.com"])
            }
            self.assertIn("github-token", rules)

    def test_unapproved_history_identity_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            git(root, "config", "user.email", "private" + "@invalid.test")
            git(root, "config", "user.name", "Public Person")
            (root / "README.md").write_text("synthetic\n", encoding="utf-8")
            git(root, "add", "README.md")
            git(root, "commit", "-q", "-m", "initial")
            rules = {item.rule for item in MODULE.scan_history(root)}
            self.assertIn("unapproved-author-email", rules)
            self.assertIn("unapproved-committer-email", rules)
            self.assertIn("unapproved-author-name", rules)
            self.assertIn("unapproved-committer-name", rules)

    def test_github_noreply_identity_requires_explicit_approval(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            private_email = "12345+realuser" + "@users.noreply.github.com"
            git(root, "config", "user.email", private_email)
            (root / "README.md").write_text("synthetic\n", encoding="utf-8")
            git(root, "add", "README.md")
            git(root, "commit", "-q", "-m", "initial")
            blocked = {item.rule for item in MODULE.scan_history(root)}
            self.assertIn("unapproved-author-email", blocked)
            approved = {
                item.rule
                for item in MODULE.scan_history(root, allowed_emails=[private_email])
            }
            self.assertNotIn("unapproved-author-email", approved)
            self.assertNotIn("unapproved-committer-email", approved)

    def test_remote_and_nested_public_root_require_explicit_release_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            public = root / "public"
            public.mkdir()
            (public / "README.md").write_text("synthetic\n", encoding="utf-8")
            git(root, "add", "public/README.md")
            git(root, "commit", "-q", "-m", "initial")
            git(root, "remote", "add", "origin", "https://code.invalid/example/public.git")
            rules = {
                item.rule
                for item in MODULE.scan_history(
                    public,
                    allowed_emails=["public@example.com"],
                )
            }
            self.assertIn("public-root-not-git-root", rules)
            self.assertIn("unapproved-git-remote", rules)

    def test_private_denylist_does_not_echo_value(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            private_value = "household-" + "marker"
            (root / "note.txt").write_text(private_value, encoding="utf-8")
            findings = MODULE.scan(root, deny_literals=[private_value])
            self.assertEqual([item.rule for item in findings], ["private-denylist-match"])
            self.assertNotIn(private_value, repr(findings))

    def test_private_key_bearer_and_lfs_pointer_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.txt").write_text(
                "-----BEGIN " + "PRIVATE KEY-----\n"
                "Authorization: Bearer " + "C" * 24 + "\n"
                "version https://git-lfs." + "github.com/spec/v1\n",
                encoding="utf-8",
            )
            found = {item.rule for item in MODULE.scan(root)}
            self.assertTrue({"private-key", "bearer-token", "git-lfs-pointer"} <= found)

    def test_home_assistant_specific_secrets_and_text_media_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "config.yaml").write_text(
                "wifi_password: " + "S" * 20 + "\n"
                "cloud: https://" + "household-id" + ".ui.nabucasa.com\n"
                "latitude: " + "31." + "234567\n"
                "noise_psk: " + "Q" * 40 + "\n",
                encoding="utf-8",
            )
            (root / "floorplan.svg").write_text("<svg/>", encoding="utf-8")
            found = {item.rule for item in MODULE.scan(root)}
            self.assertTrue(
                {
                    "secret-assignment",
                    "ha-cloud-url",
                    "home-coordinate",
                    "ha-network-key",
                    "media-not-approved",
                }
                <= found
            )

    def test_commit_message_is_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            message = Path(directory) / "COMMIT_EDITMSG"
            message.write_text("token=" + "gh" + "p_" + "D" * 24, encoding="utf-8")
            found = {item.rule for item in MODULE.scan_commit_message(message)}
            self.assertIn("github-token", found)

    def test_commit_message_gpgsig_text_is_not_a_signature_header(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            (root / "README.md").write_text("synthetic\n", encoding="utf-8")
            git(root, "add", "README.md")
            git(root, "commit", "-q", "-m", "subject", "-m", "gpgsig note in body")
            rules = {
                item.rule
                for item in MODULE.scan_history(
                    root,
                    allowed_emails=["public@example.com"],
                )
            }
            self.assertNotIn("signed-commit-identity-review", rules)

    def test_sensitive_filename_is_redacted_in_text_and_json(self) -> None:
        secret_name = "gh" + "p_" + "E" * 24 + ".txt"
        finding = MODULE.Finding(secret_name, "sensitive-file-name")
        for as_json in (False, True):
            output = io.StringIO()
            with redirect_stdout(output):
                MODULE._print([finding], as_json)
            self.assertNotIn(secret_name, output.getvalue())
            self.assertIn("redacted-path", output.getvalue())

    def test_unreachable_git_object_blocks_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            path = root / "README.md"
            path.write_text("one\n", encoding="utf-8")
            git(root, "add", "README.md")
            git(root, "commit", "-q", "-m", "initial")
            path.write_text("two\n", encoding="utf-8")
            git(root, "add", "README.md")
            git(root, "commit", "-q", "-m", "temporary")
            git(root, "reset", "-q", "--hard", "HEAD~1")
            self.assertIn("unreachable-object", {item.rule for item in MODULE.scan_unreachable(root)})

    def test_submodule_mode_is_blocked_in_index_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            init_repo(root)
            path = root / "README.md"
            path.write_text("synthetic\n", encoding="utf-8")
            git(root, "add", "README.md")
            git(root, "commit", "-q", "-m", "initial")
            commit = subprocess.run(
                ["git", "-C", str(root), "rev-parse", "HEAD"],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            ).stdout.strip()
            git(root, "update-index", "--add", "--cacheinfo", f"160000,{commit},modules/example")
            self.assertIn(
                "unsupported-git-mode",
                {item.rule for item in MODULE.scan_staged(root)},
            )
            git(root, "commit", "-q", "-m", "add synthetic gitlink")
            self.assertIn(
                "git-submodule-not-allowed",
                {
                    item.rule
                    for item in MODULE.scan_history(
                        root,
                        allowed_emails=["public@example.com"],
                    )
                },
            )


if __name__ == "__main__":
    unittest.main()
