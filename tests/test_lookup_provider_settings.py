"""Superadmin lookup-provider toggles with real SQLite and FastAPI routes (SG-TODO-017)."""
import asyncio
import sqlite3
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from python import scrying_glass_provider_settings as settings
from python import scrying_glass_monster_selection as ms
from python.scrying_glass_storage import SQLiteStorage

ROOT = Path(__file__).resolve().parents[1]


def table_exists(storage):
    return storage.connection.execute("SELECT 1 FROM sqlite_master WHERE name=?",
                                      (settings.TABLE,)).fetchone() is not None


class ProviderSettingsStorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.storage = SQLiteStorage(Path(self.temp.name) / "db.sqlite3")
        self.ctx = SimpleNamespace(STORAGE=self.storage, CONFIG={"display": {
            "dndbeyond_image_lookup": True, "fivetools_fallback": True, "open5e_lookup": True}})

    def tearDown(self):
        self.storage.close()
        self.temp.cleanup()

    def test_configuration_defaults_apply_without_creating_a_table(self):
        self.assertEqual(settings.effective_display(self.ctx), self.ctx.CONFIG["display"])
        described = settings.describe(self.ctx)["providers"]
        self.assertEqual([item["provider"] for item in described], ["dndbeyond", "fivetools", "open5e"])
        self.assertTrue(all(item["enabled"] and item["saved"] is None for item in described))
        self.assertFalse(table_exists(self.storage))

    def test_saved_toggles_override_configuration_and_persist(self):
        result = settings.save(self.ctx, {"fivetools": False, "open5e": False})
        self.assertTrue(table_exists(self.storage))
        self.assertEqual([item["enabled"] for item in result["providers"]], [True, False, False])
        display = settings.effective_display(self.ctx)
        self.assertEqual((display["fivetools_fallback"], display["open5e_lookup"]), (False, False))
        self.assertIsNot(display, self.ctx.CONFIG["display"])
        self.assertTrue(self.ctx.CONFIG["display"]["fivetools_fallback"])
        settings.save(self.ctx, {"open5e": True})
        path = self.storage.path
        self.storage.close()
        self.storage = SQLiteStorage(path)
        self.ctx.STORAGE = self.storage
        found = {}
        worker = threading.Thread(target=lambda: found.update(settings.effective_display(self.ctx)))
        worker.start(); worker.join()
        self.assertEqual((found["fivetools_fallback"], found["open5e_lookup"]), (False, True))

    def test_invalid_bodies_and_missing_storage_are_rejected(self):
        for body in ({}, [], {"other": True}, {"open5e": 1}, {"open5e": "false"}, {"open5e": None}):
            with self.subTest(body=body), self.assertRaises(HTTPException) as caught:
                settings.save(self.ctx, body)
            self.assertEqual(caught.exception.status_code, 422)
        self.assertFalse(table_exists(self.storage))
        with self.assertRaises(HTTPException) as caught:
            settings.save(SimpleNamespace(CONFIG={"display": {}}), {"open5e": True})
        self.assertEqual(caught.exception.status_code, 503)

    def test_unreadable_settings_fail_closed(self):
        settings.save(self.ctx, {"open5e": True})
        with patch.object(settings, "overrides", side_effect=sqlite3.OperationalError("locked")):
            display = settings.effective_display(self.ctx)
        self.assertEqual((display["dndbeyond_image_lookup"], display["fivetools_fallback"],
                          display["open5e_lookup"]), (False, False, False))

    def test_lookup_and_image_paths_honour_saved_toggles(self):
        settings.save(self.ctx, {"dndbeyond": False, "fivetools": False, "open5e": False})
        self.ctx.dnd_monster_candidates = Mock(side_effect=AssertionError("network"))
        with patch.object(ms, "fivetools_candidates", side_effect=AssertionError("network")), \
                patch.object(ms, "open5e_candidates", side_effect=AssertionError("network")):
            result = ms.lookup_candidates(self.ctx, "Goblin")
        self.assertEqual([item["status"] for item in result["providers"]], ["disabled"] * 3)
        from python.scrying_glass_service_images import ImagesService
        service = ImagesService.__new__(ImagesService)
        service.context = self.ctx
        self.assertIsNone(service._dndbeyond_image("Goblin"))


async def _async(function, *args):
    return function(*args)


class ProviderSettingsRouteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        roles = {"root": "superadmin", "alice": "admin"}

        def require(role, cookie):
            async def guard(request: Request):
                user = request.cookies.get(cookie, "")
                if user not in roles:
                    raise HTTPException(401, "Sign in required")
                if role == "superadmin" and roles[user] != "superadmin":
                    raise HTTPException(403, "Superadmin role required")
            return guard

        self.ctx = SimpleNamespace(ADMIN_SESSION_COOKIE="admin", require=require,
                                   CONFIG={"display": {"open5e_lookup": True}})
        self.app = FastAPI()
        settings.install_provider_settings_routes(self.ctx, self.app)
        self.client = TestClient(self.app)
        self.client.__enter__()
        # The server owns its SQLite connection on the event-loop thread.
        self.storage = self.client.portal.call(
            lambda: _async(SQLiteStorage, Path(self.temp.name) / "db.sqlite3"))
        self.ctx.STORAGE = self.storage

    def tearDown(self):
        self.client.portal.call(lambda: _async(self.storage.close))
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def call(self, method, user, **kwargs):
        self.client.cookies.clear()
        if user:
            self.client.cookies.set("admin", user)
        return self.client.request(method, "/api/settings/lookup-providers", **kwargs)

    def test_superadmin_reads_and_saves(self):
        response = self.call("GET", "root")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["providers"][2]["enabled"], True)
        response = self.call("PUT", "root", json={"open5e": False})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["providers"][2], {
            "provider": "open5e", "label": "Open5e", "config_key": "open5e_lookup",
            "configured": True, "saved": False, "enabled": False})

    def test_admin_anonymous_and_cross_origin_writes_are_rejected(self):
        self.assertEqual(self.call("GET", "alice").status_code, 403)
        self.assertEqual(self.call("PUT", "alice", json={"open5e": False}).status_code, 403)
        self.assertEqual(self.call("PUT", None, json={"open5e": False}).status_code, 401)
        response = self.call("PUT", "root", json={"open5e": False}, headers={"Origin": "https://evil.example"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.call("PUT", "root", json={"open5e": "no"}).status_code, 422)
        self.assertFalse(self.client.portal.call(lambda: _async(table_exists, self.storage)))

    def test_admin_reads_enabled_provider_labels_in_lookup_order(self):
        self.client.cookies.clear()
        self.assertEqual(self.client.get("/api/monsters/lookup-providers").status_code, 401)
        self.client.cookies.set("admin", "alice")
        response = self.client.get("/api/monsters/lookup-providers")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"providers": ["D&D Beyond", "5e.tools", "Open5e"]})
        self.assertEqual(self.call("PUT", "root", json={"fivetools": False}).status_code, 200)
        self.client.cookies.set("admin", "alice")
        self.assertEqual(self.client.get("/api/monsters/lookup-providers").json(),
                         {"providers": ["D&D Beyond", "Open5e"]})


class ProviderSettingsPageTests(unittest.TestCase):
    def test_users_page_includes_section_and_script(self):
        page = (ROOT / "templates/users.html").read_text(encoding="utf-8")
        for marker in ('id="lookupProviderSection"', 'id="lookupProviderForm"', 'id="lookupProviderToggles"',
                       'id="lookupProviderNotice"', "/static/lookup-providers-admin.js?v=1"):
            self.assertEqual(page.count(marker), 1, marker)
        script = (ROOT / "static/lookup-providers-admin.js").read_text(encoding="utf-8")
        self.assertIn("/api/settings/lookup-providers", script)
        self.assertNotIn("innerHTML", script)

    def test_routes_are_registered_by_admin_api(self):
        source = (ROOT / "python/scrying_glass_api_admin.py").read_text(encoding="utf-8")
        self.assertIn("install_provider_settings_routes(context, app)", source)


if __name__ == "__main__":
    unittest.main()
