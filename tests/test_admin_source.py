"""Admin core script: the eight fragments, the production reader and assembled syntax."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from python.scrying_glass_admin_source import ADMIN_SCRIPT_PARTS, read_admin_script

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PARTS = tuple(f"{number:03d}-source.js" for number in range(10, 81, 10))
LIMIT = 20000


class AdminSourceTests(unittest.TestCase):
    def test_fragment_inventory_order_and_size(self):
        directory = ROOT / "static/admin"
        self.assertEqual(tuple(ADMIN_SCRIPT_PARTS), EXPECTED_PARTS)
        self.assertEqual({p.name for p in directory.iterdir()}, set(EXPECTED_PARTS))
        for name in EXPECTED_PARTS:
            with self.subTest(part=name):
                data = (directory / name).read_bytes()
                data.decode("utf-8")
                self.assertLessEqual(len(data), LIMIT)

    def test_reader_concatenates_fragments_in_order(self):
        directory = ROOT / "static/admin"
        expected = b"".join((directory / name).read_bytes() for name in EXPECTED_PARTS)
        self.assertEqual(read_admin_script(ROOT / "static"), expected)

    def test_reader_bounds(self):
        with tempfile.TemporaryDirectory() as temporary:
            static = Path(temporary)
            (static / "admin").mkdir()
            for name in ADMIN_SCRIPT_PARTS:
                (static / "admin" / name).write_bytes(b"x")
            first = static / "admin" / ADMIN_SCRIPT_PARTS[0]
            first.write_bytes(b"x" * LIMIT)
            self.assertEqual(len(read_admin_script(static)), LIMIT + 7)
            first.write_bytes(b"x" * (LIMIT + 1))
            with self.assertRaises(ValueError):
                read_admin_script(static)
            first.write_bytes(b"\xff")
            with self.assertRaises(UnicodeDecodeError):
                read_admin_script(static)
            first.unlink()
            with self.assertRaises(FileNotFoundError):
                read_admin_script(static)

    def test_fixture_runner_assembles_and_restores_marker(self):
        before = (ROOT / "static/admin.js").read_bytes()
        digest = hashlib.sha256(read_admin_script(ROOT / "static")).hexdigest()
        command = ("from pathlib import Path; import hashlib, sys; "
                   f"sys.exit(hashlib.sha256(Path('static/admin.js').read_bytes()).hexdigest() != {digest!r})")
        result = subprocess.run([sys.executable, str(ROOT / "tools/run_split_tests.py"),
                                 "--", sys.executable, "-c", command], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((ROOT / "static/admin.js").read_bytes(), before)

    @unittest.skipUnless(shutil.which("node"), "Node is required for JavaScript parsing")
    def test_fragment_and_assembled_syntax(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "admin.js"
            path.write_bytes(read_admin_script(ROOT / "static"))
            for target in [ROOT / "static/admin" / name for name in ADMIN_SCRIPT_PARTS] + [path]:
                with self.subTest(target=target.name):
                    result = subprocess.run(["node", "--check", str(target)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
