"""Superadmin-only user management routes."""
import sqlite3
from pathlib import Path
from fastapi import Depends, HTTPException, Request, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from .scrying_glass_init import password_hash
from .scrying_glass_database_transactions import serialized_handler


def install_user_routes(context, app):
    auth = context.auth_service
    guard = Depends(context.require("superadmin", context.ADMIN_SESSION_COOKIE))

    def serialize(handler):
        return serialized_handler(context, handler, role="superadmin",
                                  cookie_name=context.ADMIN_SESSION_COOKIE)

    async def same_origin(request: Request):
        origin = request.headers.get("origin")
        if origin and origin != str(request.base_url).rstrip("/"):
            raise HTTPException(403, "Cross-origin user changes are not allowed")
        if request.headers.get("sec-fetch-site") == "cross-site":
            raise HTTPException(403, "Cross-site user changes are not allowed")

    @app.get("/api/me", dependencies=[Depends(context.require("admin", context.ADMIN_SESSION_COOKIE))])
    async def me(request: Request):
        return auth.session(request.cookies.get(context.ADMIN_SESSION_COOKIE, ""))

    @app.get("/users", response_class=HTMLResponse)
    async def page(request: Request):
        session = auth.session(request.cookies.get(context.ADMIN_SESSION_COOKIE, ""))
        if not session:
            return RedirectResponse("/login", 303)
        if session["role"] != "superadmin":
            raise HTTPException(403, "Superadmin role required")
        return HTMLResponse((Path(__file__).resolve().parent.parent / "templates/users.html").read_text(encoding="utf-8"))

    @app.get("/api/users", dependencies=[guard])
    async def users():
        return [dict(r) for r in auth.db.execute("SELECT id,username,role FROM users ORDER BY username")]

    def fields(body, create):
        if not isinstance(body, dict) or set(body) - {"username", "role", "password"}:
            raise HTTPException(422, "Only username, role and password are accepted")
        if create and not {"username", "role", "password"} <= set(body):
            raise HTTPException(422, "Username, role and password are required")
        if not body:
            raise HTTPException(422, "No changes supplied")
        if "password" in body and body["password"] is None:
            raise HTTPException(422, "Password cannot be null; omit to keep unchanged")

    @app.post("/api/users", status_code=201, dependencies=[guard, Depends(same_origin)])
    @serialize
    async def create(body: dict = Body(...)):
        fields(body, True)
        auth.validate(body["username"], body["role"], body["password"])
        hashed = password_hash(body["password"])
        try:
            with context.STORAGE.transaction():
                ident = auth.db.execute("INSERT INTO users(username,role,password_hash) VALUES (?,?,?)", (body["username"], body["role"], hashed)).lastrowid
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Username already exists")
        return {"id": ident, "username": body["username"], "role": body["role"]}

    @app.patch("/api/users/{user_id}", dependencies=[guard, Depends(same_origin)])
    @serialize
    async def update(user_id: int, body: dict = Body(...)):
        fields(body, False)
        with context.STORAGE.transaction():
            old = auth.db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            if not old:
                raise HTTPException(404, "User not found")
            username, role = body.get("username", old["username"]), body.get("role", old["role"])
            auth.validate(username, role, body.get("password"))
            if old["role"] == "superadmin" and role != "superadmin" and auth.db.execute("SELECT COUNT(*) FROM users WHERE role='superadmin'").fetchone()[0] <= 1:
                raise HTTPException(409, "Cannot demote the last superadmin")
            hashed = password_hash(body["password"]) if "password" in body else old["password_hash"]
            try:
                auth.db.execute("UPDATE users SET username=?,role=?,password_hash=? WHERE id=?", (username, role, hashed, user_id))
            except sqlite3.IntegrityError:
                raise HTTPException(409, "Username already exists")
        await auth.invalidate(old["username"])
        return {"id": user_id, "username": username, "role": role}

    @app.delete("/api/users/{user_id}", dependencies=[guard, Depends(same_origin)])
    @serialize
    async def delete(user_id: int):
        with context.STORAGE.transaction():
            old = auth.db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
            if not old:
                raise HTTPException(404, "User not found")
            if old["role"] == "superadmin" and auth.db.execute("SELECT COUNT(*) FROM users WHERE role='superadmin'").fetchone()[0] <= 1:
                raise HTTPException(409, "Cannot delete the last superadmin")
            auth.db.execute("DELETE FROM users WHERE id=?", (user_id,))
        await auth.invalidate(old["username"])
        return {"deleted": user_id}
