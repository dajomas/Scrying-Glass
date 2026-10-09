"""Account unit tests with real SQLite; endpoint calls bypass HTTP routing.

Minimal FastAPI response/dependency substitutes are used only if FastAPI is
not installed, so account logic can be checked without the web runtime.
"""
import asyncio
import contextlib
import importlib.util
import io
import sqlite3
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from contextlib import closing

class FakeHTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code, self.detail = status_code, detail
        super().__init__(detail)

class FakeResponse:
    def __init__(self, *args, **kwargs):
        self.args = args

class FakeApp:
    def __init__(self):
        self.handlers = {}
    def route(self, method, path, **kwargs):
        def register(handler):
            self.handlers[method, path] = handler
            return handler
        return register
    def get(self, path, **kwargs): return self.route("GET", path, **kwargs)
    def post(self, path, **kwargs): return self.route("POST", path, **kwargs)
    def patch(self, path, **kwargs): return self.route("PATCH", path, **kwargs)
    def delete(self, path, **kwargs): return self.route("DELETE", path, **kwargs)

class AccountTests(unittest.TestCase):
    def setUp(self):
        self.modules = None
        if importlib.util.find_spec("fastapi") is None:
            fastapi = types.ModuleType("fastapi")
            fastapi.HTTPException = FakeHTTPException
            fastapi.Depends = lambda value: value
            fastapi.Request = object
            fastapi.Body = lambda value: value
            responses = types.ModuleType("fastapi.responses")
            responses.HTMLResponse = responses.RedirectResponse = responses.Response = FakeResponse
            self.modules = patch.dict(sys.modules, {"fastapi": fastapi, "fastapi.responses": responses})
            self.modules.start()
        from fastapi import HTTPException
        from python.scrying_glass_service_auth import AuthService
        from python.scrying_glass_admin_users import install_user_routes
        from python.scrying_glass_storage import SQLiteStorage
        from python.scrying_glass_init import password_hash, password_ok
        self.error, self.hash, self.verify = HTTPException, password_hash, password_ok
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "accounts.sqlite3"
        self.storage = SQLiteStorage(self.path)
        self.context = types.SimpleNamespace(STORAGE=self.storage, CONFIG={"security": {"users": [
            {"username": "dm", "role": "admin", "password": "old-password"},
            {"username": "table", "role": "client", "password": "table-password"}]}},
            SESSIONS={}, SOCKETS=set(), ADMIN_SESSION_COOKIE="admin", CLIENT_SESSION_COOKIE="client")
        self.auth = AuthService(self.context)
        self.context.auth_service = self.auth
        self.context.require = self.auth.require
        self.app = FakeApp()
        install_user_routes(self.context, self.app)
        with contextlib.redirect_stdout(io.StringIO()): self.auth.initialize_users()

    def tearDown(self):
        self.storage.close()
        self.tmp.cleanup()
        if self.modules:
            self.modules.stop()

    def call(self, method, path, **kwargs):
        return asyncio.run(self.app.handlers[method, path](**kwargs))

    def test_import_promotes_first_admin_and_hashes(self):
        user = self.auth.user("dm")
        self.assertEqual(user["role"], "superadmin")
        self.assertTrue(user["password"].startswith("scrypt$"))
        self.assertTrue(self.verify("old-password", user["password"]))
        self.assertNotIn("users", self.context.CONFIG["security"])

    def test_repeat_import_does_not_resurrect_deleted_user(self):
        self.auth.db.execute("DELETE FROM users WHERE username='table'")
        self.context.CONFIG["security"]["users"] = [{"username": "table", "role": "client", "password": "changed"}]
        self.auth.initialize_users()
        self.assertIsNone(self.auth.user("table"))
        self.assertTrue(self.verify("old-password", self.auth.user("dm")["password"]))

    def test_create_update_delete_and_no_hash_in_response(self):
        user = self.call("POST", "/api/users", body={"username": "new", "role": "admin", "password": "new-password"})
        self.assertEqual(set(user), {"id", "username", "role"})
        before = self.auth.user("new")["password"]
        self.context.SESSIONS["token"] = {"username": "new", "role": "admin"}
        self.call("PATCH", "/api/users/{user_id}", user_id=user["id"], body={"username": "renamed", "role": "client"})
        self.assertEqual(self.auth.user("renamed")["password"], before)
        self.assertNotIn("token", self.context.SESSIONS)
        self.call("PATCH", "/api/users/{user_id}", user_id=user["id"], body={"password": "replacement"})
        self.assertTrue(self.verify("replacement", self.auth.user("renamed")["password"]))
        self.call("DELETE", "/api/users/{user_id}", user_id=user["id"])
        self.assertIsNone(self.auth.user("renamed"))
        self.assertTrue(all(set(u) == {"id", "username", "role"} for u in self.call("GET", "/api/users")))

    def test_last_superadmin_guard(self):
        ident = self.auth.user("dm")["id"]
        for method, kwargs in [("DELETE", {}), ("PATCH", {"body": {"role": "admin"}})]:
            with self.assertRaises(self.error) as error:
                self.call(method, "/api/users/{user_id}", user_id=ident, **kwargs)
            self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(self.auth.user("dm")["role"], "superadmin")

    def test_second_superadmin_allows_demote(self):
        self.call("POST", "/api/users", body={"username": "second", "role": "superadmin", "password": "second-password"})
        self.call("PATCH", "/api/users/{user_id}", user_id=self.auth.user("dm")["id"], body={"role": "admin"})
        self.assertEqual(self.auth.user("dm")["role"], "admin")

    def test_duplicate_and_unknown_user(self):
        with self.assertRaises(self.error) as error:
            self.call("POST", "/api/users", body={"username": "dm", "role": "admin", "password": "long-password"})
        self.assertEqual(error.exception.status_code, 409)
        with self.assertRaises(self.error) as error:
            self.call("DELETE", "/api/users/{user_id}", user_id=9999)
        self.assertEqual(error.exception.status_code, 404)

    def test_bad_fields_and_passwords(self):
        for body in [{"role": "invalid"}, {"role": []}, {"password": ""}, {"password": None}, {"password": "short"}, {"username": " bad "}, {"password_hash": "injected"}, {}]:
            with self.assertRaises(self.error) as error:
                self.call("PATCH", "/api/users/{user_id}", user_id=self.auth.user("dm")["id"], body=body)
            self.assertEqual(error.exception.status_code, 422)

    def test_role_authorization(self):
        self.context.SESSIONS["dm"] = {"username": "dm", "role": "superadmin"}
        self.context.SESSIONS["table"] = {"username": "table", "role": "client"}
        request = types.SimpleNamespace(cookies={"admin": "dm"})
        self.assertEqual(asyncio.run(self.auth.require("superadmin", "admin")(request))["username"], "dm")
        self.assertEqual(asyncio.run(self.auth.require("admin", "admin")(request))["username"], "dm")
        request.cookies["admin"] = "table"
        with self.assertRaises(self.error) as error: asyncio.run(self.auth.require("superadmin", "admin")(request))
        self.assertEqual(error.exception.status_code, 403)
        request.cookies.clear()
        with self.assertRaises(self.error) as error: asyncio.run(self.auth.require("admin", "admin")(request))
        self.assertEqual(error.exception.status_code, 401)

    def test_session_rechecks_database_role(self):
        self.context.SESSIONS["token"] = {"username": "table", "role": "client"}
        self.auth.db.execute("UPDATE users SET role='admin' WHERE username='table'")
        self.assertIsNone(self.auth.session("token"))
        self.assertNotIn("token", self.context.SESSIONS)

    def test_hash_is_retained_on_import(self):
        self.auth.db.execute("DELETE FROM account_migration")
        self.auth.db.execute("DELETE FROM users")
        hashed = self.hash("preserve-this")
        self.context.CONFIG["security"]["users"] = [{"username": "root", "role": "superadmin", "password": hashed}]
        self.auth.initialize_users()
        self.assertEqual(self.auth.user("root")["password"], hashed)

    def test_failed_import_is_atomic(self):
        self.auth.db.execute("DELETE FROM account_migration")
        self.auth.db.execute("DELETE FROM users")
        self.context.CONFIG["security"]["users"] = [
            {"username": "duplicate", "role": "admin", "password": "password"},
            {"username": "duplicate", "role": "client", "password": "password"}]
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaises(sqlite3.IntegrityError): self.auth.initialize_users()
        self.assertEqual(self.auth.db.execute("SELECT COUNT(*) FROM users").fetchone()[0], 0)
        self.assertIsNone(self.auth.db.execute("SELECT 1 FROM account_migration").fetchone())

    def test_fresh_bootstrap_only_once(self):
        self.auth.db.execute("DELETE FROM account_migration")
        self.auth.db.execute("DELETE FROM users")
        self.context.CONFIG["security"] = {}
        output = io.StringIO()
        with contextlib.redirect_stdout(output): self.auth.initialize_users()
        self.assertIn("Initial superadmin:", output.getvalue())
        self.assertEqual(self.auth.user("superadmin")["role"], "superadmin")
        output = io.StringIO()
        with contextlib.redirect_stdout(output): self.auth.initialize_users()
        self.assertEqual(output.getvalue(), "")

    def test_upgrade_v3_preserves_data_and_creates_backup(self):
        self.storage.close()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("DROP TABLE users")
            db.execute("DROP TABLE account_migration")
            for table in ('characters_effects','monsters_effects','snapshot_characters_effects','snapshot_characters_attributes','snapshot_characters','encounter_snapshots','feature_state'):
                db.execute('DROP TABLE '+table)
            db.execute('DROP TRIGGER IF EXISTS cleanup_snapshot')
            db.execute("PRAGMA user_version=3")
        from python.scrying_glass_storage import SQLiteStorage
        self.storage = SQLiteStorage(self.path)
        self.context.STORAGE = self.storage
        self.assertEqual(self.auth.db.execute("PRAGMA user_version").fetchone()[0], 5)
        self.assertTrue(self.storage.migration_backup.is_file())
        self.assertEqual(self.auth.db.execute("SELECT COUNT(*) FROM application_state").fetchone()[0], 1)
        self.assertIsNone(self.auth.db.execute("SELECT 1 FROM account_migration").fetchone())

if __name__ == "__main__": unittest.main()
