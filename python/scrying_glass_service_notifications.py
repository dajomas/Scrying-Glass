"""Notifications services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path


class NotificationsService:
    """Group notifications operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context

    async def broadcast(self) -> None:
        """Send ordered snapshots concurrently, dropping stalled clients."""
        import asyncio
        import logging

        if getattr(self.context, "_defer_database_broadcast", False):
            self.context._database_broadcast_pending = True
            return

        logger = logging.getLogger(__name__)

        broadcast_lock = getattr(
            self.context,
            "_display_broadcast_lock",
            None,
        )

        if broadcast_lock is None:
            broadcast_lock = asyncio.Lock()
            self.context._display_broadcast_lock = broadcast_lock

        async def send_one(
            websocket: Any,
            message: str,
        ) -> None:
            try:
                await asyncio.wait_for(
                    websocket.send_text(message),
                    timeout=2.0,
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.context.SOCKETS.discard(websocket)

                logger.debug(
                    "Removing failed or stalled display WebSocket: %s",
                    exc,
                )

                try:
                    await asyncio.wait_for(
                        websocket.close(code=1011),
                        timeout=0.5,
                    )
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass

        async with broadcast_lock:
            sockets = tuple(self.context.SOCKETS)

            if not sockets:
                return

            message = self.context.json.dumps({
                "type": "state",
                "state": self.context.display_state(),
            })

            await asyncio.gather(
                *(
                    send_one(websocket, message)
                    for websocket in sockets
                )
            )

    async def changed(self) -> None:
        """Persist shared state and broadcast the updated public state under the lock."""
        async with self.context.LOCK:
            with self.context.STORAGE.transaction():
                self.context.save_state()
        await self.context.broadcast()

    async def monster_changed(self) -> None:
        """Monster changed."""
        async with self.context.LOCK:
            with self.context.STORAGE.transaction():
                self.context.save_active_setup_monsters()
                self.context.save_state()

        await self.context.broadcast()

    async def character_changed(self) -> None:
        """Character changed."""
        async with self.context.LOCK:
            with self.context.STORAGE.transaction():
                self.context.save_active_campaign_characters()
                self.context.save_state()

        await self.context.broadcast()

    async def combatants_changed(self, *, monsters: bool=False, characters: bool=False) -> None:
        """Combatants changed."""
        async with self.context.LOCK:
            with self.context.STORAGE.transaction():
                if monsters:
                    self.context.save_active_setup_monsters()

                if characters:
                    self.context.save_active_campaign_characters()

                self.context.save_state()

        await self.context.broadcast()
