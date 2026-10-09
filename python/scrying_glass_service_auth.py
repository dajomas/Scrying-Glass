"""Database-backed authentication and live session authorization."""
from typing import Any
from fastapi import HTTPException
from .scrying_glass_init import password_hash
import re
import secrets

ROLES = {"superadmin", "admin", "client"}

class AuthService:
    def __init__(self, context: Any):
        self.context = context

    @property
    def db(self):
        return self.context.STORAGE.connection

    def user(self, name):
        row = self.db.execute("SELECT id, username, role, password_hash AS password FROM users WHERE username=?", (name,)).fetchone()
        return dict(row) if row else None

    def session(self, token):
        session = self.context.SESSIONS.get(token)
        if not session:
            return None
        user = self.user(session["username"])
        if not user or user["role"] != session["role"]:
            self.context.SESSIONS.pop(token, None)
            return None
        return session

    def require(self, role, cookie_name):
        from fastapi import Request
        async def dependency(request: Request):
            session = self.session(request.cookies.get(cookie_name, ""))
            if not session:
                raise HTTPException(401, "Sign in required")
            if role == "superadmin" and session["role"] != "superadmin":
                raise HTTPException(403, "Superadmin role required")
            if role == "admin" and session["role"] not in {"admin", "superadmin"}:
                raise HTTPException(403, "Admin role required")
            return session
        return dependency

    @staticmethod
    def validate(username, role, password=None):
        if not isinstance(username, str) or not 1 <= len(username) <= 64 or username != username.strip() or any(ord(c) < 32 or ord(c) == 127 for c in username):
            raise HTTPException(422, "Username must be 1-64 characters without control characters or surrounding whitespace")
        if not isinstance(role, str) or role not in ROLES:
            raise HTTPException(422, "Invalid role")
        if password is not None and (not isinstance(password, str) or not 8 <= len(password) <= 1024):
            raise HTTPException(422, "Password must be 8-1024 characters")

    def initialize_users(self):
        if self.db.execute("SELECT 1 FROM account_migration").fetchone():
            self.context.CONFIG.get("security", {}).pop("users", None)
            return
        legacy = self.context.CONFIG.get("security", {}).get("users", [])
        if not isinstance(legacy, list):
            raise ValueError("security.users must be a list")
        prepared = []
        for item in legacy:
            name, role, password = item.get("username"), item.get("role"), item.get("password")
            self.validate(name, role)
            if not isinstance(password, str) or not password:
                raise ValueError("Legacy users require nonempty passwords")
            if password.startswith("scrypt$"):
                parts = password.split("$")
                if len(parts) != 3 or not re.fullmatch(r"(?:[0-9a-fA-F]{2})+", parts[1]) or not re.fullmatch(r"[0-9a-fA-F]{128}", parts[2]):
                    raise ValueError("Malformed legacy password hash")
                hashed = password
            else:
                hashed = password_hash(password)
            prepared.append([name, role, hashed])
        if prepared and not any(u[1] == "superadmin" for u in prepared):
            first = next((u for u in prepared if u[1] == "admin"), None)
            if first is not None:
                first[1] = "superadmin"
                print(f"Promoted legacy administrator {first[0]} to superadmin")
        bootstrap = None
        if not any(u[1] == "superadmin" for u in prepared):
            names = {u[0] for u in prepared}
            name = "superadmin"
            while name in names:
                name += "_"
            bootstrap = (name, secrets.token_urlsafe(24))
            prepared.append([name, "superadmin", password_hash(bootstrap[1])])
        with self.context.STORAGE.transaction():
            for name, role, hashed in prepared:
                self.db.execute("INSERT INTO users(username,role,password_hash) VALUES (?,?,?)", (name, role, hashed))
            self.db.execute("INSERT INTO account_migration VALUES (1,1)")
        self.context.CONFIG.get("security", {}).pop("users", None)
        if bootstrap:
            print(f"Initial superadmin: {bootstrap[0]} / {bootstrap[1]} (change this password at /users)", flush=True)

    async def invalidate(self, username):
        import asyncio
        tokens = {token for token, session in self.context.SESSIONS.items() if session["username"] == username}
        for token in tokens:
            self.context.SESSIONS.pop(token, None)
        for socket in list(self.context.SOCKETS):
            if socket.cookies.get(self.context.CLIENT_SESSION_COOKIE) in tokens:
                self.context.SOCKETS.discard(socket)
                try:
                    await asyncio.wait_for(socket.close(code=1008), timeout=1)
                except Exception:
                    pass
