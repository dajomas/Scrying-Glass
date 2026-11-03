"""Current identities of the eight Admin fragments after intentional UI changes."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import unittest
from python.scrying_glass_admin_source import ADMIN_SCRIPT_PARTS, read_admin_script

ROOT = Path(__file__).resolve().parents[1]
DIGESTS = (
    "85e469e2073cd957bddd54b4de5e979b516fe6efc8e4c56a09244e49886b15d2",
    "a85ac3628d46516447e2e99761e2c02ac5f255c16e470a2645445ac749a435db",
    "c8a8904b31b079ee73919d050506a62b57ad984a2be2def36236874ca1344140",
    "cb296e6c87e0e582d71806d05db1fa82311f85ff351ea30cdd161523669d0dff",
    "be6f9bc4180d854c28b9f734aab4479b0157c30c97eac2b6fc3815d59db05f8e",
    "354046a35ef7916aa11c83da886f8634b695d6591c3d5c2ff33cf2db30ad8568",
    "276a31e9b1d00cb7b9d7bc1495b85dce3d9fd5268d3376c3521f77bb40334d91",
    "4cce8120028dc97e6de16e4dac71a01be63a79f29080d556b4e04d1168ed4a46",
)


class AdminSourcePreparationTests(unittest.TestCase):
    def test_fragment_sizes_and_identity(self):
        self.assertEqual(len(ADMIN_SCRIPT_PARTS), 8)
        for name, digest in zip(ADMIN_SCRIPT_PARTS, DIGESTS):
            with self.subTest(part=name):
                data = (ROOT / "static/admin" / name).read_bytes()
                data.decode("utf-8")
                self.assertLessEqual(len(data), 20000)
                self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_complete_identity(self):
        data = read_admin_script(ROOT / "static")
        self.assertEqual(len(data), 114814)
        self.assertEqual(hashlib.sha256(data).hexdigest(),
                         "40fca092f989bcd85eaf7f06dc02b962b662a28827864df68c998919cdf87b46")

    @unittest.skipUnless(shutil.which("node"), "Node is required for JavaScript parsing")
    def test_fragment_syntax(self):
        for name in ADMIN_SCRIPT_PARTS:
            result = subprocess.run(["node", "--check", str(ROOT / "static/admin" / name)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
