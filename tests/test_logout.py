"""Logout unit tests; real web dependencies are optional for these tests.

Minimal FastAPI substitutes are used when unavailable. Handlers are called
directly, so this suite does not claim live HTTP or browser integration coverage.
"""
import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

class FakeHTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code, self.detail = status_code, detail
        super().__init__(detail)

class FakeRedirect:
    def __init__(self, url, status_code=307):
        self.status_code = status_code
        self.headers = {"location": url}
        self.raw_headers = []
    def delete_cookie(self, name, **kwargs):
        self.raw_headers.append((b"set-cookie", (name + '=; Max-Age=0; Path=/').encode()))

class Socket:
    def __init__(self, token, fail=False, stall=False):
        self.cookies = {"client": token}
        self.closed = []
        self.fail, self.stall = fail, stall
    async def close(self, code):
        self.closed.append(code)
        if self.fail: raise RuntimeError("Already closed")
        if self.stall: await asyncio.Event().wait()

class App:
    def __init__(self): self.routes, self.middlewares = [], []
    def add_api_route(self, path, handler, **kwargs): self.routes.append((path, handler, kwargs))
    def middleware(self, kind):
        def register(handler):
            self.middlewares.append(handler)
            return handler
        return register

class LogoutTests(unittest.TestCase):
    def setUp(self):
        self.module_patch = None
        if importlib.util.find_spec("fastapi") is None:
            fastapi = types.ModuleType("fastapi")
            fastapi.HTTPException = FakeHTTPException
            fastapi.Request = object
            responses = types.ModuleType("fastapi.responses")
            responses.RedirectResponse = FakeRedirect
            self.module_patch = patch.dict(sys.modules, {"fastapi": fastapi, "fastapi.responses": responses})
            self.module_patch.start()
        from fastapi import HTTPException
        self.error = HTTPException
        path = Path(__file__).resolve().parent.parent / "python/scrying_glass_logout.py"
        spec = importlib.util.spec_from_file_location("logout_under_test", path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.context = types.SimpleNamespace(
            SESSIONS={"a": {"username": "dm", "role": "superadmin"},
                      "c": {"username": "dm", "role": "superadmin"},
                      "other": {"username": "table", "role": "client"}},
            SOCKETS=set(), ADMIN_SESSION_COOKIE="admin", CLIENT_SESSION_COOKIE="client",
            LEGACY_SESSION_COOKIES=("legacy",))
        self.request = types.SimpleNamespace(cookies={"admin": "a", "client": "c"},
            headers={"origin": "http://server:4000", "sec-fetch-site": "same-origin"},
            base_url="http://server:4000/", url=types.SimpleNamespace(path="/logout"))

    def tearDown(self):
        if self.module_patch: self.module_patch.stop()

    def logout(self, cookie):
        return asyncio.run(self.module.logout_session(self.context, self.request, cookie))

    def deleted_cookies(self, response):
        return [value.decode().split('=', 1)[0] for name, value in response.raw_headers if name == b"set-cookie"]

    def test_admin_logout_preserves_client_session(self):
        socket = Socket("c"); self.context.SOCKETS.add(socket)
        response = self.logout("admin")
        self.assertNotIn("a", self.context.SESSIONS)
        self.assertIn("c", self.context.SESSIONS)
        self.assertIn(socket, self.context.SOCKETS)
        self.assertEqual(socket.closed, [])
        self.assertIn("admin", self.deleted_cookies(response))
        self.assertNotIn("client", self.deleted_cookies(response))

    def test_client_logout_closes_all_matching_sockets_only(self):
        first, second, other = Socket("c"), Socket("c"), Socket("other")
        self.context.SOCKETS.update([first, second, other])
        response = self.logout("client")
        self.assertNotIn("c", self.context.SESSIONS)
        self.assertIn("a", self.context.SESSIONS)
        self.assertIn("other", self.context.SESSIONS)
        self.assertEqual(self.context.SOCKETS, {other})
        self.assertEqual(first.closed, [1008]); self.assertEqual(second.closed, [1008])
        self.assertIn("client", self.deleted_cookies(response))
        self.assertNotIn("admin", self.deleted_cookies(response))

    def test_redirect_and_no_store(self):
        response = self.logout("admin")
        self.assertEqual(response.status_code, 303)
        self.assertEqual(response.headers["location"], "/login")
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertIn("legacy", self.deleted_cookies(response))

    def test_missing_cookie_is_idempotent(self):
        self.request.cookies = {}
        before = dict(self.context.SESSIONS)
        self.assertEqual(self.logout("client").status_code, 303)
        self.assertEqual(self.context.SESSIONS, before)

    def test_expired_token_still_closes_socket(self):
        del self.context.SESSIONS["c"]
        socket = Socket("c"); self.context.SOCKETS.add(socket)
        self.assertEqual(self.logout("client").status_code, 303)
        self.assertEqual(socket.closed, [1008])

    def test_repeated_logout_succeeds(self):
        self.logout("client")
        self.assertEqual(self.logout("client").status_code, 303)

    def test_cross_origin_rejected_without_revocation(self):
        self.request.headers["origin"] = "http://evil.example"
        with self.assertRaises(self.error) as error: self.logout("client")
        self.assertEqual(error.exception.status_code, 403)
        self.assertIn("c", self.context.SESSIONS)

    def test_cross_site_rejected_even_without_origin(self):
        self.request.headers = {"sec-fetch-site": "cross-site"}
        with self.assertRaises(self.error) as error: self.logout("client")
        self.assertEqual(error.exception.status_code, 403)
        self.assertIn("c", self.context.SESSIONS)

    def test_no_origin_non_browser_request_allowed(self):
        self.request.headers = {}
        self.assertEqual(self.logout("client").status_code, 303)

    def test_close_error_does_not_prevent_logout(self):
        socket = Socket("c", fail=True); self.context.SOCKETS.add(socket)
        self.assertEqual(self.logout("client").status_code, 303)
        self.assertNotIn(socket, self.context.SOCKETS)
        self.assertNotIn("c", self.context.SESSIONS)

    def test_stalled_socket_is_bounded(self):
        socket = Socket("c", stall=True); self.context.SOCKETS.add(socket)
        self.assertEqual(self.logout("client").status_code, 303)
        self.assertNotIn(socket, self.context.SOCKETS)

    def test_post_only_registration(self):
        app = App(); self.module.install_logout(self.context, app, "admin")
        self.assertEqual(len(app.routes), 1)
        path, handler, options = app.routes[0]
        self.assertEqual(path, "/logout")
        self.assertEqual(options["methods"], ["POST"])
        self.assertEqual(asyncio.run(handler(self.request)).status_code, 303)

    def test_authenticated_pages_and_apis_not_cacheable(self):
        app = App(); self.module.install_logout(self.context, app, "client")
        async def call_next(request): return types.SimpleNamespace(headers={})
        for path in ["/", "/display", "/users", "/login", "/api/state", "/api/users"]:
            self.request.url.path = path
            response = asyncio.run(app.middlewares[0](self.request, call_next))
            self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.request.url.path = "/static/client.css"
        response = asyncio.run(app.middlewares[0](self.request, call_next))
        self.assertNotIn("Cache-Control", response.headers)

    def test_markup_uses_post_logout_forms(self):
        root = Path(__file__).resolve().parent.parent
        for name in ["templates/admin/010_pane_controls.html", "templates/users.html", "web_html/client_html.py"]:
            self.assertIn('action="/logout" method="post"', (root / name).read_text())

if __name__ == "__main__": unittest.main()
