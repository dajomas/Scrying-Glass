"""Preparation-only checks; runtime still uses the original static/admin.js."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
PARTS = (
    ("010-source.js", 17605, "23c91e7d66db0260f09a33d992489ceba2b9bf966ad5030623f293a5e936f6cd"),
    ("020-source.js", 18043, "a85ac3628d46516447e2e99761e2c02ac5f255c16e470a2645445ac749a435db"),
    ("030-source.js", 19585, "c8a8904b31b079ee73919d050506a62b57ad984a2be2def36236874ca1344140"),
    ("040-source.js", 11336, "cb296e6c87e0e582d71806d05db1fa82311f85ff351ea30cdd161523669d0dff"),
    ("050-source.js", 15145, "be6f9bc4180d854c28b9f734aab4479b0157c30c97eac2b6fc3815d59db05f8e"),
    ("060-source.js", 11921, "354046a35ef7916aa11c83da886f8634b695d6591c3d5c2ff33cf2db30ad8568"),
    ("070-source.js", 18831, "276a31e9b1d00cb7b9d7bc1495b85dce3d9fd5268d3376c3521f77bb40334d91"),
    ("080-source.js", 1739, "4cce8120028dc97e6de16e4dac71a01be63a79f29080d556b4e04d1168ed4a46"),
)


class AdminSourcePreparationTests(unittest.TestCase):
    def staged(self):
        directory = ROOT / "static/admin"
        present = {p.name for p in directory.iterdir()}
        names = [name for name, _, _ in PARTS if name in present]
        self.assertGreaterEqual(len(names), 2)
        self.assertEqual(names, [p[0] for p in PARTS[:len(names)]])
        self.assertEqual(present, set(names))
        return [(directory / name, size, digest)
                for name, size, digest in PARTS if name in present]

    def test_fragment_sizes_and_identity(self):
        for path, size, digest in self.staged():
            with self.subTest(path=path.name):
                data = path.read_bytes()
                data.decode("utf-8")
                self.assertLessEqual(len(data), 20000)
                self.assertEqual(len(data), size)
                self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_staged_prefix_matches_current_runtime(self):
        original = (ROOT / "static/admin.js").read_bytes()
        self.assertEqual(len(original), 114205)
        self.assertEqual(hashlib.sha256(original).hexdigest(),
                         "b97c2a3fda01aa8d3fa4cfa619939909a3c797c678c60a19512aa50c0d05fef5")
        staged = b"".join(path.read_bytes() for path, _, _ in self.staged())
        self.assertEqual(staged, original[:len(staged)])

    @unittest.skipUnless(shutil.which("node"), "Node is required for JavaScript parsing")
    def test_fragment_syntax(self):
        for path, _, _ in self.staged():
            with self.subTest(path=path.name):
                result = subprocess.run(["node", "--check", str(path)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
