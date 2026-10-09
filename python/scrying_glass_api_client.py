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
        """Server-driven heartbeat; no browser-timer inactivity disconnects."""
        import asyncio
        import logging
        import time
        from fastapi import WebSocketDisconnect

        logger=logging.getLogger(__name__)
        origin=websocket.headers.get('origin')
        scheme='https' if websocket.url.scheme=='wss' else 'http'
        if origin and origin!=f"{scheme}://{websocket.headers.get('host','')}":
            await websocket.close(code=1008,reason='Origin not allowed');return
        token=websocket.cookies.get(self.context.CLIENT_SESSION_COOKIE,'')
        session=self.context.auth_session(token)
        if not session or session.get('role') not in {'superadmin','admin','client'}:
            await websocket.close(code=1008,reason='Sign in required');return
        broadcast_lock=getattr(self.context,'_display_broadcast_lock',None)
        if broadcast_lock is None:
            broadcast_lock=asyncio.Lock();self.context._display_broadcast_lock=broadcast_lock
        features=self.context.features
        accepted=False

        async def send_state():
            # Same lock order as initial snapshots; serialize against mutations and broadcasts.
            async with operation_lock(self.context),broadcast_lock:
                if not self.context.auth_session(token):
                    await websocket.close(code=1008,reason='Sign in required');return False
                revision=features.store.revision()
                message={'type':'state','revision':revision,'state':self.context.display_state()}
                await asyncio.wait_for(websocket.send_text(self.context.json.dumps(message)),timeout=2)
                if not self.context.auth_session(token):
                    await websocket.close(code=1008,reason='Sign in required');return False
                self.context.SOCKETS.add(websocket)
                data=features.displays.setdefault(websocket,{'username':session['username'],'revision':None,'seen':time.time()})
                data['sent']=revision
                return True

        async def send_heartbeat():
            async with broadcast_lock:
                await asyncio.wait_for(websocket.send_text(self.context.json.dumps({'type':'heartbeat','revision':features.store.revision()})),timeout=2)

        try:
            await websocket.accept();accepted=True
            if not await send_state():return
            while True:
                if not self.context.auth_session(token):
                    await websocket.close(code=1008,reason='Sign in required');return
                try:
                    text=await asyncio.wait_for(websocket.receive_text(),timeout=15)
                except TimeoutError:
                    # Lack of JavaScript pings is not proof of a dead transport.
                    # Uvicorn's native WebSocket ping/pong still detects broken connections.
                    if not self.context.auth_session(token):
                        await websocket.close(code=1008,reason='Sign in required');return
                    await send_heartbeat();continue
                if len(text)>1024:
                    await websocket.close(code=1008,reason='Message too large');return
                try:message=self.context.json.loads(text)
                except ValueError:continue
                if not isinstance(message,dict):continue
                data=features.displays.get(websocket)
                if data:
                    data['seen']=time.time()
                    revision=message.get('revision')
                    if message.get('type') in {'ack','pong'} and type(revision) is int and 0<=revision<=data['sent']:
                        if data['revision'] is None or revision>=data['revision']:data['revision']=revision
                if not self.context.auth_session(token):
                    await websocket.close(code=1008,reason='Sign in required');return
                if message.get('type')=='resync':
                    if not await send_state():return
                elif message.get('type')=='ping':
                    await send_heartbeat()
                # ACK/PONG are receive-only. Responding to PONG would create a heartbeat loop.
        except WebSocketDisconnect as exc:
            logger.info('Display WebSocket closed: code=%s reason=%s user=%s',exc.code,getattr(exc,'reason',''),session['username'])
        except asyncio.CancelledError:
            raise
        except TimeoutError:
            logger.warning('Display WebSocket send timed out: user=%s',session['username'])
        except Exception:
            logger.exception('Display WebSocket failed: user=%s',session['username'])
        finally:
            self.context.SOCKETS.discard(websocket);features.displays.pop(websocket,None)
            if accepted:
                try:await asyncio.wait_for(websocket.close(),timeout=.5)
                except asyncio.CancelledError:raise
                except Exception:pass
