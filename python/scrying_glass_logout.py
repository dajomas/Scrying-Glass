"""Per-interface logout without changing persisted accounts or encounter data."""
import asyncio
import logging
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse


async def logout_session(context, request, cookie_name):
    """Revoke one session and its display sockets, then expire its cookie."""
    origin = request.headers.get("origin")
    if origin and origin != str(request.base_url).rstrip("/"):
        raise HTTPException(403, "Cross-origin logout is not allowed")
    if request.headers.get("sec-fetch-site") == "cross-site":
        raise HTTPException(403, "Cross-site logout is not allowed")

    token = request.cookies.get(cookie_name, "")
    if token:
        context.SESSIONS.pop(token, None)

    async def close_socket(socket):
        try:
            await asyncio.wait_for(socket.close(code=1008), timeout=1.0)
        except asyncio.CancelledError:
            raise
        except Exception:
            logging.getLogger(__name__).debug("Unable to close logged-out socket", exc_info=True)

    if cookie_name == context.CLIENT_SESSION_COOKIE and token:
        sockets = [socket for socket in tuple(context.SOCKETS)
                   if socket.cookies.get(context.CLIENT_SESSION_COOKIE) == token]
        for socket in sockets:
            context.SOCKETS.discard(socket)
        await asyncio.gather(*(close_socket(socket) for socket in sockets))

    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(cookie_name, path="/", httponly=True, samesite="lax")
    for legacy in context.LEGACY_SESSION_COOKIES:
        response.delete_cookie(legacy, path="/")
    response.headers["Cache-Control"] = "no-store"
    return response


def install_logout(context, app, cookie_name):
    """Register POST-only, idempotent logout on one of the two applications."""
    async def logout(request: Request):
        return await logout_session(context, request, cookie_name)

    app.add_api_route("/logout", logout, methods=["POST"], name="logout")

    @app.middleware("http")
    async def prevent_session_page_caching(request: Request, call_next):
        response = await call_next(request)
        if request.url.path in {"/", "/display", "/users", "/login", "/logout"} or request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response
