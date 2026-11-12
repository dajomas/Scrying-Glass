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
BUNDLE_BYTES = 146586
DIGESTS = (
    "068a67ea21966ec7fd3a5ef5324be784eac5b254162a8fd655b251381ed41365",
    "a85ac3628d46516447e2e99761e2c02ac5f255c16e470a2645445ac749a435db",
    "3b09fe675ca75418826c55bbb1d3d50996817dc8ea013ac210ef844222d9efc8",
    "3de6ebd82f26283399096ada57c4bcaa130d1c35f1ea06df4c92f7eac48487ef",
    "54791ac800de038f883ea009e61091028704b12e7ae7f35af9ef2c38375db935",
    "fc9fb3d3cc8dbf1e3524848cea75924bf1e3c2e532e622cb6bc82ba74388ec2b",
    "68830a8efd3b02716c8253aeb24d4ac978d426880ce4438d1c7e0b0d4283a1ce",
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
