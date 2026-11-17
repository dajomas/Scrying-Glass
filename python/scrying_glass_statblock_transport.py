"""Private statblock update transport on the statblock listener (SG-TODO-022.09).

WebSocket ``/ws`` on the statblock application only. Every frame is built for
one socket after authorizing its session again (regular admin, live session,
assigned to the active campaign); a failed check sends ``{"type": "revoked"}``
and closes the socket (1008), so the page clears its content. Frames carry
the statblock state projection (tile summaries, revisions, encounter token):
no statblock content, which the page reads from ``/api/statblocks/monsters``.
These sockets are never part of ``SOCKETS`` (Client Display) and display
frames never reach them.

Frames: ``state`` (``{"type", "state"}``), ``heartbeat``, ``revoked``
(``{"type", "code", "message"}``). Client messages: ``resync``, ``ping``.
"""
import asyncio
import json
import logging

from .scrying_glass_database_transactions import operation_lock
from .scrying_glass_statblock_contract import StatblockAPIError

LOG = logging.getLogger(__name__)
HEARTBEAT_SECONDS = 15
SEND_SECONDS = 2


def sockets(context):
    value = getattr(context, 'STATBLOCK_SOCKETS', None)
    if value is None:
        value = context.STATBLOCK_SOCKETS = {}
    return value


def _lock(context):
    lock = getattr(context, '_statblock_broadcast_lock', None)
    if lock is None:
        lock = context._statblock_broadcast_lock = asyncio.Lock()
    return lock


def frame(context, token):
    """(frame, authorized) for one session; never raises for authorization."""
    from .scrying_glass_statblock_service import statblock_service
    service = statblock_service(context)
    try:
        principal = service.authorize(token)
    except StatblockAPIError as exc:
        return {'type': 'revoked', 'code': exc.code, 'message': exc.message}, False
    return {'type': 'state', 'state': service.state_projection(principal)}, True


async def _send(websocket, message):
    await asyncio.wait_for(websocket.send_text(json.dumps(message)), timeout=SEND_SECONDS)


async def _close(context, websocket, code=1008, reason='Sign in required'):
    sockets(context).pop(websocket, None)
    try:
        await asyncio.wait_for(websocket.close(code=code, reason=reason), timeout=0.5)
    except asyncio.CancelledError:
        raise
    except Exception:
        pass


async def notify(context):
    """Send each statblock socket its own authorized projection, or revoke it."""
    registry = sockets(context)
    if not registry:
        return
    async with _lock(context):
        for websocket, token in list(registry.items()):
            message, authorized = frame(context, token)
            try:
                await _send(websocket, message)
            except asyncio.CancelledError:
                raise
            except Exception:
                LOG.debug('Dropping failed statblock WebSocket', exc_info=True)
                await _close(context, websocket, 1011, 'Send failed')
                continue
            if not authorized:
                await _close(context, websocket)


async def close_session(context, token):
    """Logout: close every statblock socket of this session."""
    for websocket, owner in list(sockets(context).items()):
        if owner == token:
            await _close(context, websocket)


async def statblock_socket(context, websocket, cookie):
    origin = websocket.headers.get('origin')
    scheme = 'https' if websocket.url.scheme == 'wss' else 'http'
    if origin and origin != f"{scheme}://{websocket.headers.get('host', '')}":
        await websocket.close(code=1008, reason='Origin not allowed')
        return
    token = websocket.cookies.get(cookie, '')
    message, authorized = frame(context, token)
    if not authorized:
        await websocket.close(code=1008, reason='Sign in required')
        return
    from fastapi import WebSocketDisconnect
    accepted = False
    async def send_state():
        async with operation_lock(context), _lock(context):
            message, authorized = frame(context, token)
            await _send(websocket, message)
            if not authorized:
                await _close(context, websocket)
                return False
            sockets(context)[websocket] = token
            return True
    try:
        await websocket.accept()
        accepted = True
        if not await send_state():
            return
        while True:
            try:
                text = await asyncio.wait_for(websocket.receive_text(), timeout=HEARTBEAT_SECONDS)
            except TimeoutError:
                message, authorized = frame(context, token)
                if not authorized:
                    async with _lock(context):
                        await _send(websocket, message)
                    await _close(context, websocket)
                    return
                async with _lock(context):
                    await _send(websocket, {'type': 'heartbeat'})
                continue
            if len(text) > 1024:
                await _close(context, websocket, 1008, 'Message too large')
                return
            try:
                kind = json.loads(text).get('type')
            except (ValueError, AttributeError):
                continue
            if kind == 'resync':
                if not await send_state():
                    return
            elif kind == 'ping':
                message, authorized = frame(context, token)
                async with _lock(context):
                    await _send(websocket, {'type': 'heartbeat'} if authorized else message)
                if not authorized:
                    await _close(context, websocket)
                    return
    except WebSocketDisconnect:
        pass
    except asyncio.CancelledError:
        raise
    except TimeoutError:
        LOG.warning('Statblock WebSocket send timed out')
    except Exception:
        LOG.exception('Statblock WebSocket failed')
    finally:
        sockets(context).pop(websocket, None)
        if accepted:
            try:
                await asyncio.wait_for(websocket.close(), timeout=0.5)
            except asyncio.CancelledError:
                raise
            except Exception:
                pass
