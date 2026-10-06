"""Auth services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path
from fastapi import HTTPException, Request as FastAPIRequest, UploadFile


class AuthService:
    """Group auth operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context

    def user(self, name: str) -> dict[str, Any] | None:
        """Find a configured user by username."""
        return next((x for x in self.context.CONFIG['security']['users'] if x.get('username') == name), None)

    def require(self, role: Literal['admin', 'client'], cookie_name: str):
        """Build a cookie-based authorization dependency for the requested role."""
        async def dependency(request: FastAPIRequest) -> dict[str, str]:
            """Dependency."""
            session = self.context.SESSIONS.get(
                request.cookies.get(cookie_name, "")
            )

            if not session or (
                role == "admin" and session["role"] != "admin"
            ):
                raise self.context.HTTPException(401, "Sign in required")

            return session

        return dependency
