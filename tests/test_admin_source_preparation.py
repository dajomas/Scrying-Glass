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
BUNDLE_BYTES = 130882
DIGESTS = (
    "e760d06ed6b762c0454c68da195bbba452cc950003a4a9d7afb181acfe4e050d",
    "744cc3b5bc2dfb56431d4a350f1c63db2d66145d73a5ad6407961698051794e0",
    "6cc39f53fb65672c867c0424ba5c5fcff362f53ed943ecf56c72727b64201f19",
    "fee22101a45ae9f6d2fd8a791ef450108b7df1cc32d3525be1086aac7227ca65",
    "41cd211dde3b12f2bd7f0f36a2b396d3d3b0569f0ce4dfb9ca6faebda462daee",
    "7e11ec9b86417d5adbf66a67bfb8686307565d57902b51b703b7211ba1e64575",
    "4efb2b4f779b1c5f9a70e6c3e058cca48aa40c357620a9f2413efc2d7b9ae16b",
    "5c5b72146278603c56412cb0a786051b222833c18ee20bfbca7157d146682c02",
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
