"""Role-specific administration pages; registration stays in AdminAPI."""
from __future__ import annotations
from fastapi import Form, Request as FastAPIRequest


class AdminPagesMixin:
    """Show user management to superadmins and battle controls to admins."""

    async def admin_login_get(self, request: FastAPIRequest):
        session = self.context.auth_session(
            request.cookies.get(self.context.ADMIN_SESSION_COOKIE, "")
        )
        if session and session["role"] in {"admin", "superadmin"}:
            destination = "/users" if session["role"] == "superadmin" else "/"
            return self.context.RedirectResponse(destination, 303)
        return self.context.login()

    async def admin_login_post(self, username: str=Form(...), password: str=Form(...)):
        user = self.context.user(username)
        if not user or user.get("role") not in {"admin", "superadmin"} or not self.context.password_ok(password, str(user.get("password", ""))):
            return self.context.login("Invalid admin credentials")
        token = self.context.secrets.token_urlsafe(32)
        self.context.SESSIONS[token] = {"username": username, "role": user["role"]}
        destination = "/users" if user["role"] == "superadmin" else "/"
        response = self.context.RedirectResponse(destination, 303)
        response.set_cookie(self.context.ADMIN_SESSION_COOKIE, token, httponly=True, samesite="lax", secure=False)
        for legacy in self.context.LEGACY_SESSION_COOKIES:
            response.delete_cookie(legacy)
        return response

    async def admin_home(self, request: FastAPIRequest):
        session = self.context.auth_session(
            request.cookies.get(self.context.ADMIN_SESSION_COOKIE, "")
        )
        if not session:
            return self.context.RedirectResponse("/login", 303)
        if session["role"] == "superadmin":
            return self.context.RedirectResponse("/users", 303)
        if session["role"] == "admin":
            return self.context.HTMLResponse(self.context.ADMIN_HTML)
        return self.context.RedirectResponse("/login", 303)

    def admin_get_state(self):
        return self.context.public_state()
