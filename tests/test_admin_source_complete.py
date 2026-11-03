"""Check the production reader's complete bundle and assembled syntax."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile
import unittest
from python.scrying_glass_admin_source import ADMIN_SCRIPT_PARTS, read_admin_script

ROOT = Path(__file__).resolve().parents[1]


class AdminSourceCompleteTests(unittest.TestCase):
    def test_complete_identity(self):
        directory = ROOT / "static/admin"
        self.assertEqual({p.name for p in directory.iterdir()}, set(ADMIN_SCRIPT_PARTS))
        data = read_admin_script(ROOT / "static")
        self.assertEqual(data, b"".join((directory / name).read_bytes() for name in ADMIN_SCRIPT_PARTS))
        self.assertEqual(len(data), 114205)
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "b97c2a3fda01aa8d3fa4cfa619939909a3c797c678c60a19512aa50c0d05fef5")

    def test_reader_bounds(self):
        with tempfile.TemporaryDirectory() as temporary:
            static = Path(temporary)
            (static / "admin").mkdir()
            for name in ADMIN_SCRIPT_PARTS:
                (static / "admin" / name).write_bytes(b"x")
            first = static / "admin" / ADMIN_SCRIPT_PARTS[0]
            first.write_bytes(b"x" * 20000)
            self.assertEqual(len(read_admin_script(static)), 20007)
            first.write_bytes(b"x" * 20001)
            with self.assertRaises(ValueError):
                read_admin_script(static)
            first.write_bytes(b"\xff")
            with self.assertRaises(UnicodeDecodeError):
                read_admin_script(static)
            first.unlink()
            with self.assertRaises(FileNotFoundError):
                read_admin_script(static)

    def test_fixture_runner_isolation(self):
        import sys
        before = (ROOT / "static/admin.js").read_bytes()
        command = "from pathlib import Path; import hashlib; d=Path('static/admin.js').read_bytes(); assert len(d)==114205; assert hashlib.sha256(d).hexdigest()=='b97c2a3fda01aa8d3fa4cfa619939909a3c797c678c60a19512aa50c0d05fef5'"
        result = subprocess.run([sys.executable, str(ROOT / "tools/run_split_tests.py"),
                                 "--", sys.executable, "-c", command], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((ROOT / "static/admin.js").read_bytes(), before)

    @unittest.skipUnless(shutil.which("node"), "Node is required for JavaScript parsing")
    def test_assembled_syntax(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "admin.js"
            path.write_bytes(read_admin_script(ROOT / "static"))
            result = subprocess.run(["node", "--check", str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
