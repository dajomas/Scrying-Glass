"""Complete split-source identity checks, before runtime activation."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = tuple(f"{number:03d}-source.js" for number in range(10, 81, 10))


class AdminSourceCompleteTests(unittest.TestCase):
    def assembled(self):
        directory = ROOT / "static/admin"
        self.assertEqual({p.name for p in directory.iterdir()}, set(NAMES))
        parts = [(directory / name).read_bytes() for name in NAMES]
        for name, data in zip(NAMES, parts):
            with self.subTest(part=name):
                self.assertLessEqual(len(data), 20000)
                data.decode("utf-8")
        return b"".join(parts)

    def test_complete_identity(self):
        data = self.assembled()
        self.assertEqual(len(data), 114205)
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "b97c2a3fda01aa8d3fa4cfa619939909a3c797c678c60a19512aa50c0d05fef5")
        self.assertEqual(data, (ROOT / "static/admin.js").read_bytes())

    @unittest.skipUnless(shutil.which("node"), "Node is required for JavaScript parsing")
    def test_assembled_syntax(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "admin.js"
            path.write_bytes(self.assembled())
            result = subprocess.run(["node", "--check", str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
