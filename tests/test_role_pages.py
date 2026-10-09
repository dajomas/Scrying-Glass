"""Unit tests for role-specific landing pages, not live HTTP integration."""
import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

class Response:
    def __init__(self, content, status_code=200):
        self.content, self.status_code = content, status_code
        self.cookies = {}
        self.deleted = []
    def set_cookie(self, name, value, **kwargs): self.cookies[name] = (value, kwargs)
    def delete_cookie(self, name): self.deleted.append(name)

class RolePageTests(unittest.TestCase):
    def setUp(self):
        self.module_patch = None
        if importlib.util.find_spec("fastapi") is None:
            module = types.ModuleType("fastapi")
            module.Form = lambda value: value
            module.Request = object
            self.module_patch = patch.dict(sys.modules, {"fastapi": module})
            self.module_patch.start()
        root = Path(__file__).resolve().parent.parent
        spec = importlib.util.spec_from_file_location("role_pages_under_test", root / "python/scrying_glass_admin_pages.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.users = {role: {"username": role, "role": role, "password": "correct"}
                      for role in ("superadmin", "admin", "client")}
        self.sessions = {}
        self.context = types.SimpleNamespace(
            auth_session=lambda token: self.sessions.get(token),
            user=lambda name: self.users.get(name),
            password_ok=lambda supplied, stored: supplied == stored,
            SESSIONS=self.sessions,
            ADMIN_SESSION_COOKIE="admin_cookie", LEGACY_SESSION_COOKIES=("legacy",),
            secrets=types.SimpleNamespace(token_urlsafe=lambda size: "new_token"),
            RedirectResponse=Response, HTMLResponse=Response,
            ADMIN_HTML="battle page", login=lambda error="": Response("login:" + error),
            public_state=lambda: {"battle_round": 0})
        self.handler = module.AdminPagesMixin()
        self.handler.context = self.context
        self.request = types.SimpleNamespace(cookies={})

    def tearDown(self):
        if self.module_patch: self.module_patch.stop()

    def login(self, role, password="correct"):
        return asyncio.run(self.handler.admin_login_post(role, password))

    def signed_in(self, role):
        self.sessions["existing"] = {"username": role, "role": role}
        self.request.cookies["admin_cookie"] = "existing"

    def test_superadmin_login_goes_to_users(self):
        response = self.login("superadmin")
        self.assertEqual((response.status_code, response.content), (303, "/users"))
        self.assertEqual(self.sessions["new_token"]["role"], "superadmin")
        self.assertTrue(response.cookies["admin_cookie"][1]["httponly"])
        self.assertIn("legacy", response.deleted)

    def test_admin_login_goes_to_battle(self):
        response = self.login("admin")
        self.assertEqual((response.status_code, response.content), (303, "/"))
        self.assertEqual(self.sessions["new_token"]["role"], "admin")

    def test_superadmin_root_redirects_to_users(self):
        self.signed_in("superadmin")
        response = asyncio.run(self.handler.admin_home(self.request))
        self.assertEqual((response.status_code, response.content), (303, "/users"))

    def test_admin_root_shows_battle(self):
        self.signed_in("admin")
        response = asyncio.run(self.handler.admin_home(self.request))
        self.assertEqual((response.status_code, response.content), (200, "battle page"))

    def test_missing_session_redirects_to_login(self):
        response = asyncio.run(self.handler.admin_home(self.request))
        self.assertEqual((response.status_code, response.content), (303, "/login"))

    def test_client_session_cannot_open_battle_page(self):
        self.signed_in("client")
        response = asyncio.run(self.handler.admin_home(self.request))
        self.assertEqual((response.status_code, response.content), (303, "/login"))

    def test_login_get_redirects_existing_role_to_its_page(self):
        for role, destination in [("superadmin", "/users"), ("admin", "/")]:
            self.signed_in(role)
            response = asyncio.run(self.handler.admin_login_get(self.request))
            self.assertEqual((response.status_code, response.content), (303, destination))

    def test_anonymous_login_get_shows_form(self):
        response = asyncio.run(self.handler.admin_login_get(self.request))
        self.assertEqual(response.content, "login:")

    def test_invalid_logins_do_not_create_sessions(self):
        for username, password in [("superadmin", "wrong"), ("client", "correct"), ("missing", "correct")]:
            response = self.login(username, password)
            self.assertIn("Invalid admin credentials", response.content)
            self.assertEqual(self.sessions, {})

    def test_removed_navigation_and_preserved_logout(self):
        root = Path(__file__).resolve().parent.parent
        users = (root / "templates/users.html").read_text()
        pane = (root / "templates/admin/010_pane_controls.html").read_text()
        script = (root / "static/admin.js").read_text()
        self.assertNotIn('href="/"', users)
        self.assertNotIn("Back to battle administration", users)
        self.assertNotIn("userManagementLink", pane)
        self.assertNotIn("userManagementLink", script)
        self.assertIn('action="/logout" method="post"', users)
        self.assertIn('action="/logout" method="post"', pane)
        self.assertIn('id="userForm"', users)

if __name__ == "__main__": unittest.main()
