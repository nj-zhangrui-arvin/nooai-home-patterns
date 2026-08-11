#!/usr/bin/env python3
"""Compatibility entrypoint for the public-release-audit Skill."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "public-release-audit"
    / "scripts"
    / "audit_public_release.py"
)
SPEC = importlib.util.spec_from_file_location("public_release_audit", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load public release audit: {SCRIPT}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

Finding = MODULE.Finding
rules = MODULE.rules
scan = MODULE.scan
main = MODULE.main


if __name__ == "__main__":
    raise SystemExit(main())
