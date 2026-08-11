#!/usr/bin/env python3
"""Run optional local secret scanners without printing candidate secrets."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Result:
    tool: str
    status: str
    findings: int | None = None


def _run(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def audit(root: Path, run_tools: bool) -> list[Result]:
    results: list[Result] = []
    commands = {
        "gitleaks": [
            "gitleaks",
            "dir",
            "--redact=100",
            "--no-banner",
            "--exit-code=1",
            str(root),
        ],
        "trufflehog": [
            "trufflehog",
            "filesystem",
            str(root),
            "--no-verification",
            "--no-update",
            "--fail",
            "--json",
        ],
        "detect-secrets": [
            "detect-secrets",
            "scan",
            "--all-files",
            "--no-verify",
            "--exclude-lines",
            r'"sha256"\s*:',
            str(root),
        ],
    }
    for name, command in commands.items():
        if shutil.which(command[0]) is None:
            results.append(Result(name, "missing"))
            continue
        if not run_tools:
            results.append(Result(name, "available-not-run"))
            continue
        completed = _run(command)
        if name == "gitleaks":
            status = "pass" if completed.returncode == 0 else "fail" if completed.returncode == 1 else "error"
            results.append(Result(name, status))
        elif name == "trufflehog":
            status = "pass" if completed.returncode == 0 else "fail" if completed.returncode == 183 else "error"
            count = sum(1 for line in completed.stdout.splitlines() if line.strip())
            results.append(Result(name, status, count if status == "fail" else 0))
        else:
            try:
                payload = json.loads(completed.stdout.decode("utf-8"))
                count = sum(len(items) for items in payload.get("results", {}).values())
                status = "pass" if completed.returncode == 0 and count == 0 else "fail"
                results.append(Result(name, status, count))
            except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
                results.append(Result(name, "error"))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument("--run", action="store_true", help="run installed tools in offline/redacted mode")
    parser.add_argument("--strict", action="store_true", help="treat missing or not-run tools as incomplete")
    args = parser.parse_args()
    results = audit(args.root.resolve(), args.run)
    print(json.dumps([asdict(item) for item in results], ensure_ascii=False, indent=2))
    if any(item.status in {"fail", "error"} for item in results):
        return 1
    if args.strict and any(item.status in {"missing", "available-not-run"} for item in results):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
