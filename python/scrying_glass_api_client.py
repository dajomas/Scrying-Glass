"""Optional extracted admin/client endpoints for Scrying Glass."""
from __future__ import annotations
from typing import Any, get_type_hints
from fastapi import Depends, FastAPI, File, Form
from .scrying_glass_database_transactions import serialized_handler, operation_lock

class ClientAPI:
    """Own client endpoints; access live state through the supplied server context."""

    def __init__(self, context: Any, app: FastAPI) -> None:
        """Bind handlers, resolve request types, and register routes on the application."""
        self.context = context
        self.app = app
        self.register_routes()
        from .scrying_glass_logout import install_logout
        install_logout(context, app, context.CLIENT_SESSION_COOKIE)

    def register_routes(self) -> None:
        """Register bound methods while preserving authentication and route metadata."""
        handler = self.client_root
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/', handler, methods=['GET'], include_in_schema=False)
        handler = self.client_login_get
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/login', handler, methods=['GET'])
        handler = self.client_login_post
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/login', handler, methods=['POST'])
        handler = self.client_home
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_route('/display', handler, methods=['GET'])
        handler = self.client_get_state
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        handler = serialized_handler(self.context, handler, role='client',
                                     cookie_name=self.context.CLIENT_SESSION_COOKIE)
        self.app.add_api_route('/api/state', handler, methods=['GET'], dependencies=[Depends(self.context.require('client', self.context.CLIENT_SESSION_COOKIE))])
        handler = self.ws
        handler.__func__.__annotations__ = get_type_hints(
            handler.__func__, globalns=vars(self.context),
        )
        self.app.add_api_websocket_route('/ws', handler)

    # ============================================================================
    # Login and HTML pages
    # ============================================================================


    async def client_root(self, request: FastAPIRequest):
        """Client root."""
        session = self.context.auth_session(request.cookies.get(self.context.CLIENT_SESSION_COOKIE, ""))

        if not session:
            return self.context.RedirectResponse("/login", status_code=303)

        return self.context.RedirectResponse("/display", status_code=303)

    def client_login_get(self):
        """Client login get."""
        return self.context.login()

    async def client_login_post(self, username: str=Form(...), password: str=Form(...)):
        """Client login post."""
        u = self.context.user(username)
        if not u or u.get('role') not in {'superadmin', 'admin', 'client'} or (not self.context.password_ok(password, str(u.get('password', '')))):
            return self.context.login('Invalid credentials')
        token = self.context.secrets.token_urlsafe(32)
        self.context.SESSIONS[token] = {'username': username, 'role': u['role']}
        r = self.context.RedirectResponse('/display', 303)
        r.set_cookie(self.context.CLIENT_SESSION_COOKIE, token, httponly=True, samesite='lax', secure=False)
        for legacy in self.context.LEGACY_SESSION_COOKIES:
            r.delete_cookie(legacy)
        return r

    async def client_home(self, request: FastAPIRequest):
        """Client home."""
        return self.context.HTMLResponse(self.context.CLIENT_HTML) if self.context.auth_session(request.cookies.get(self.context.CLIENT_SESSION_COOKIE, '')) else self.context.RedirectResponse('/login', 303)

    # ============================================================================
    # State and live updates
    # ============================================================================


    def client_get_state(self):
        """Client get state."""
        return self.context.display_state()

    async def ws(self, websocket: WebSocket):
        """Authenticate a display socket and always clean up its registration."""
        import asyncio
        import logging
        from fastapi import WebSocketDisconnect

        logger = logging.getLogger(__name__)

        origin = websocket.headers.get("origin")
        scheme = "https" if websocket.url.scheme == "wss" else "http"
        expected_origin = f"{scheme}://{websocket.headers.get('host', '')}"
        if origin and origin != expected_origin:
            await websocket.close(code=1008)
            return

        token = websocket.cookies.get(
            self.context.CLIENT_SESSION_COOKIE,
            "",
        )
        session = self.context.auth_session(token)

        if (
            not session
            or session.get("role") not in {"superadmin", "admin", "client"}
        ):
            await websocket.close(code=1008)
            return

        broadcast_lock = getattr(
            self.context,
            "_display_broadcast_lock",
            None,
        )

        if broadcast_lock is None:
            broadcast_lock = asyncio.Lock()
            self.context._display_broadcast_lock = broadcast_lock

        accepted = False

        try:
            await websocket.accept()
            accepted = True

            async with operation_lock(self.context), broadcast_lock:
                if not self.context.auth_session(token):
                    await websocket.close(code=1008)
                    return
                initial_message = self.context.json.dumps({
                    "type": "state",
                    "state": self.context.display_state(),
                })

                await asyncio.wait_for(
                    websocket.send_text(initial_message),
                    timeout=2.0,
                )

                # Logout can run while the initial send awaits network I/O.
                if not self.context.auth_session(token):
                    await websocket.close(code=1008)
                    return
                self.context.SOCKETS.add(websocket)

            while True:
                await websocket.receive_text()

        except WebSocketDisconnect:
            pass

        except asyncio.CancelledError:
            raise

        except TimeoutError:
            logger.debug(
                "Display WebSocket initial-state send timed out"
            )

        except Exception:
            logger.exception(
                "Display WebSocket handler failed"
            )

        finally:
            self.context.SOCKETS.discard(websocket)

            if accepted:
                try:
                    await asyncio.wait_for(
                        websocket.close(),
                        timeout=0.5,
                    )
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass
