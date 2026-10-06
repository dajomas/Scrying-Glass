"""Notifications services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path
from fastapi import HTTPException, Request as FastAPIRequest, UploadFile


class NotificationsService:
    """Group notifications operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context

    async def broadcast(self) -> None:
        """Broadcast."""
        message = self.context.json.dumps({'type': 'state', 'state': self.context.display_state()})
        stale = []
        for ws in tuple(self.context.SOCKETS):
            try:
                await ws.send_text(message)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self.context.SOCKETS.discard(ws)

    async def changed(self) -> None:
        """Persist shared state and broadcast the updated public state under the lock."""
        async with self.context.LOCK:
            self.context.save_state()
        await self.context.broadcast()

    async def monster_changed(self) -> None:
        """Monster changed."""
        async with self.context.LOCK:
            self.context.save_active_setup_monsters()
            self.context.save_state()

        await self.context.broadcast()

    async def character_changed(self) -> None:
        """Character changed."""
        async with self.context.LOCK:
            self.context.save_active_campaign_characters()
            self.context.save_state()

        await self.context.broadcast()

    async def combatants_changed(self, *, monsters: bool=False, characters: bool=False) -> None:
        """Combatants changed."""
        async with self.context.LOCK:
            if monsters:
                self.context.save_active_setup_monsters()

            if characters:
                self.context.save_active_campaign_characters()

            self.context.save_state()

        await self.context.broadcast()
