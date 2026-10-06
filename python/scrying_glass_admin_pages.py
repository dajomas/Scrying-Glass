"""Admin pages endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form

class AdminPagesMixin:
    """Implement admin pages handlers using the shared server context."""

    def admin_login_get(self):
        """Admin login get."""
        return self.context.login()

    def admin_login_post(self, username: str=Form(...), password: str=Form(...)):
        """Admin login post."""
        u = self.context.user(username)
        if not u or u.get('role') != 'admin' or (not self.context.password_ok(password, str(u.get('password', '')))):
            return self.context.login('Invalid admin credentials')
        token = self.context.secrets.token_urlsafe(32)
        self.context.SESSIONS[token] = {'username': username, 'role': 'admin'}
        r = self.context.RedirectResponse('/', 303)
        r.set_cookie(self.context.ADMIN_SESSION_COOKIE, token, httponly=True, samesite='lax', secure=False)
        for legacy in self.context.LEGACY_SESSION_COOKIES:
            r.delete_cookie(legacy)
        return r

    def admin_home(self, request: FastAPIRequest):
        """Admin home."""
        return self.context.HTMLResponse(self.context.ADMIN_HTML) if self.context.SESSIONS.get(request.cookies.get(self.context.ADMIN_SESSION_COOKIE, ''), {}).get('role') == 'admin' else self.context.RedirectResponse('/login', 303)

    def admin_get_state(self):
        """Admin get state."""
        return self.context.public_state()
