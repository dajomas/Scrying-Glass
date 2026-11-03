"""Production static adapter via fixture apps, not authenticated server startup."""
import ast
from pathlib import Path
import shutil
import tempfile
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from python.scrying_glass_admin_source import ADMIN_SCRIPT_PARTS, read_admin_script
from python.scrying_glass_admin_static import AdminScriptStaticFiles

ROOT = Path(__file__).resolve().parents[1]


class AdminSplitRuntimeTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.static = Path(temporary.name) / "static"
        shutil.copytree(ROOT / "static/admin", self.static / "admin")
        (self.static / "admin.js").write_text("throw new Error('marker must not be served');")
        (self.static / "other.css").write_text("body{color:red}")
        self.bundle = read_admin_script(self.static)

    def client(self):
        app = FastAPI()
        adapter = AdminScriptStaticFiles(directory=str(self.static))
        self.addCleanup(adapter._admin_bundle_directory.cleanup)
        app.mount("/static", adapter)
        client = TestClient(app)
        self.addCleanup(client.close)
        return client, adapter

    def test_get_head_conditional_range_and_delegation(self):
        for interface in ("admin", "client"):
            with self.subTest(interface=interface):
                client, adapter = self.client()
                response = client.get("/static/admin.js?_cb=test")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.content, self.bundle)
                self.assertIn("javascript", response.headers["content-type"])
                head = client.head("/static/admin.js")
                self.assertEqual(head.status_code, 200)
                self.assertEqual(head.content, b"")
                self.assertEqual(int(head.headers["content-length"]), len(self.bundle))
                cached = client.get("/static/admin.js", headers={"If-None-Match": response.headers["etag"]})
                self.assertEqual(cached.status_code, 304)
                ranged = client.get("/static/admin.js", headers={"Range": "bytes=10-31"})
                self.assertEqual(ranged.status_code, 206)
                self.assertEqual(ranged.content, self.bundle[10:32])
                self.assertEqual(client.get("/static/other.css").text, "body{color:red}")
                self.assertEqual(client.get("/static/missing.js").status_code, 404)
                self.assertEqual(client.get("/static/%2e%2e/secret.txt").status_code, 404)

    def test_refresh_and_stable_unchanged_mtime(self):
        client, adapter = self.client()
        before = client.get("/static/admin.js")
        mtime = adapter._admin_bundle_path.stat().st_mtime_ns
        self.assertEqual(client.get("/static/admin.js").content, self.bundle)
        self.assertEqual(adapter._admin_bundle_path.stat().st_mtime_ns, mtime)
        last = self.static / "admin" / ADMIN_SCRIPT_PARTS[-1]
        last.write_bytes(last.read_bytes() + b"\n")
        after = client.get("/static/admin.js")
        self.assertEqual(after.content, self.bundle + b"\n")
        self.assertNotEqual(before.headers["etag"], after.headers["etag"])

    def test_server_mount_wiring_and_script_include(self):
        tree = ast.parse((ROOT / "scrying_glass_server.py").read_text())
        mounts = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "mount":
                if isinstance(node.func.value, ast.Name) and node.args and isinstance(node.args[0], ast.Constant):
                    mounts[(node.func.value.id, node.args[0].value)] = node.args[1].func.id
        for interface in ("admin", "client"):
            self.assertEqual(mounts[(interface, "/static")], "AdminScriptStaticFiles")
            self.assertEqual(mounts[(interface, "/media")], "StaticFiles")
        html = (ROOT / "templates/admin/190_document_end.html").read_text()
        self.assertEqual(html.count('src="/static/admin.js" defer'), 1)
        self.assertNotIn('/static/admin/0', html)


if __name__ == "__main__":
    unittest.main()
