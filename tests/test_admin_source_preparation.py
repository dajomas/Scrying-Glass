"""Pinned identities of the eight Admin fragments after intentional UI changes."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from python.scrying_glass_admin_source import ADMIN_SCRIPT_PARTS, read_admin_script

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_PARTS = tuple(f"{number:03d}-source.js" for number in range(10, 81, 10))
BUNDLE_BYTES = 132104
DIGESTS = (
    "ee4f898ba2299bc44c5ad9d13e20069e2619e5c53711b48f1a7a499f948692d0",
    "744cc3b5bc2dfb56431d4a350f1c63db2d66145d73a5ad6407961698051794e0",
    "6cc39f53fb65672c867c0424ba5c5fcff362f53ed943ecf56c72727b64201f19",
    "f0bd34765ee2273922c075c49d2f16487c00f66cb95f8dcddef929bbcf2b54ee",
    "e710841257654aad62cc6cd48f79d944f4ebeb3dc8949d78317dbed70d79ef39",
    "0e34affe4ae4d063b4dd9faaf8b26642a2a9aa5fc7aaceb1b619f555c8c6fbda",
    "4efb2b4f779b1c5f9a70e6c3e058cca48aa40c357620a9f2413efc2d7b9ae16b",
    "ea6a51445615b3777b98e38496e6681e6431c045d62c592c9aeeab851ffedc4f",
)


def verified_admin_bundle():
    if tuple(ADMIN_SCRIPT_PARTS) != EXPECTED_PARTS or len(DIGESTS) != len(EXPECTED_PARTS):
        raise AssertionError("Admin fragment inventory/order changed")
    parts = []
    for name, digest in zip(EXPECTED_PARTS, DIGESTS):
        data = (ROOT / "static/admin" / name).read_bytes()
        data.decode("utf-8")
        if len(data) > 20000 or hashlib.sha256(data).hexdigest() != digest:
            raise AssertionError("Admin fragment size/identity changed: " + name)
        parts.append(data)
    bundle = b"".join(parts)
    if len(bundle) != BUNDLE_BYTES:
        raise AssertionError("Admin bundle size changed")
    return bundle


class AdminSourcePreparationTests(unittest.TestCase):
    def test_fragment_sizes_and_identity(self):
        self.assertEqual(tuple(ADMIN_SCRIPT_PARTS), EXPECTED_PARTS)
        self.assertEqual(len(DIGESTS), 8)
        for name, digest in zip(ADMIN_SCRIPT_PARTS, DIGESTS):
            with self.subTest(part=name):
                data = (ROOT / "static/admin" / name).read_bytes()
                data.decode("utf-8")
                self.assertLessEqual(len(data), 20000)
                self.assertEqual(hashlib.sha256(data).hexdigest(), digest)

    def test_complete_identity(self):
        data = read_admin_script(ROOT / "static")
        expected = verified_admin_bundle()
        self.assertEqual(len(data), BUNDLE_BYTES)
        self.assertEqual(data, expected)
        self.assertEqual(hashlib.sha256(data).hexdigest(), hashlib.sha256(expected).hexdigest())

    def test_pinned_guard_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "static/admin"
            directory.mkdir(parents=True)
            for name in EXPECTED_PARTS:
                shutil.copyfile(ROOT / "static/admin" / name, directory / name)
            with patch.dict(verified_admin_bundle.__globals__, {"ROOT": root}):
                self.assertEqual(len(verified_admin_bundle()), BUNDLE_BYTES)
                first = directory / EXPECTED_PARTS[0]
                first.write_bytes(first.read_bytes() + b" ")
                with self.assertRaisesRegex(AssertionError, "identity changed"):
                    verified_admin_bundle()

    @unittest.skipUnless(shutil.which("node"), "Node is required for JavaScript parsing")
    def test_fragment_syntax(self):
        for name in ADMIN_SCRIPT_PARTS:
            result = subprocess.run(["node", "--check", str(ROOT / "static/admin" / name)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
