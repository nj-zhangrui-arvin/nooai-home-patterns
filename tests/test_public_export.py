from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


TOOL = Path(__file__).resolve().parents[1] / "tools" / "check_public_export.py"
SPEC = importlib.util.spec_from_file_location("check_public_export", TOOL)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PublicExportTests(unittest.TestCase):
    def test_clean_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("synthetic example\n", encoding="utf-8")
            self.assertEqual(MODULE.scan(root), [])

    def test_private_network_and_user_path_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.txt").write_text(
                "host=" + ".".join(("192", "168", "1", "20"))
                + "\npath=/" + "Us" + "ers/example/private\n",
                encoding="utf-8",
            )
            rules = {finding.rule for finding in MODULE.scan(root)}
            self.assertIn("private-ipv4", rules)
            self.assertIn("mac-user-path", rules)

    def test_generated_bytecode_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "module.pyc").write_bytes(b"synthetic")
            rules = {finding.rule for finding in MODULE.scan(root)}
            self.assertIn("forbidden-directory", rules)


if __name__ == "__main__":
    unittest.main()
