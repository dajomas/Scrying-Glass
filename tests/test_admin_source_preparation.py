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
BUNDLE_BYTES = 114400
DIGESTS = (
    "174b907526607ab534c4ec34f04624906fe52a771bda4115807f28462458275f",
    "a85ac3628d46516447e2e99761e2c02ac5f255c16e470a2645445ac749a435db",
    "943f2c753cd3104842221ed039141647d3010ba1a03f51755dac8eb912b13a66",
    "cb296e6c87e0e582d71806d05db1fa82311f85ff351ea30cdd161523669d0dff",
    "be6f9bc4180d854c28b9f734aab4479b0157c30c97eac2b6fc3815d59db05f8e",
    "354046a35ef7916aa11c83da886f8634b695d6591c3d5c2ff33cf2db30ad8568",
    "276a31e9b1d00cb7b9d7bc1495b85dce3d9fd5268d3376c3521f77bb40334d91",
    "4cce8120028dc97e6de16e4dac71a01be63a79f29080d556b4e04d1168ed4a46",
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
