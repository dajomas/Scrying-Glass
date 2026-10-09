"""Admin display endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form

class AdminDisplayMixin:
    """Implement admin display handlers using the shared server context."""

    async def dndbeyond_monster_stats(
        self,
        species: str,
    ) -> dict[str, Any]:
        """Look up optional AC/HP suggestions without blocking the event loop."""
        import asyncio
        import logging

        logger = logging.getLogger(__name__)
        monster_species = species.strip()

        if not monster_species:
            raise self.context.HTTPException(
                400,
                "Monster species is required",
            )

        if not self.context.CONFIG["display"].get(
            "dndbeyond_image_lookup",
            True,
        ):
            return {
                "found": False,
                "species": monster_species,
                "reason": "D&D Beyond lookup is disabled",
            }

        def lookup() -> dict[str, Any]:
            candidates = self.context.dnd_monster_candidates(
                monster_species,
            )

            for is_legacy, href in candidates:
                monster_html = self.context.dnd_monster_detail_html(
                    href,
                )

                ac, hp, hp_source = (
                    self.context.dnd_monster_stats_from_html(
                        monster_html,
                    )
                )

                if ac is None and hp is None:
                    continue

                return {
                    "found": True,
                    "species": monster_species,
                    "ac": ac,
                    "hp": hp,
                    "hp_source": hp_source,
                    "legacy": is_legacy,
                    "source_url": (
                        f"https://www.dndbeyond.com{href}"
                    ),
                }

            return {
                "found": False,
                "species": monster_species,
            }

        try:
            return await asyncio.to_thread(lookup)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.debug(
                "Optional D&D Beyond lookup failed for %r",
                monster_species,
                exc_info=True,
            )

            return {
                "found": False,
                "species": monster_species,
            }

    async def update_display_background(self, payload: DisplayBackgroundUpdate) -> dict[str, Any]:
        """Update display background."""
        background = payload.background.strip()

        if not background:
            raise self.context.HTTPException(400, 'Background is required')

        self.context.STATE['display']['background'] = background
        await self.context.changed()
        return self.context.public_state()

    async def upload_display_background_image(self, image: UploadFile=File(...)) -> dict[str, Any]:
        """Upload display background image."""
        image_url = self.context.save_image(image)
        self.context.STATE['display']['background'] = f'url("{image_url}")'
        await self.context.changed()

        return {
            'background': self.context.STATE['display']['background'],
            'image_url': image_url,
        }

    async def adjust_battle_order_font(
        self,
        payload: BattleOrderFontAdjust,
    ) -> dict[str, Any]:
        """Adjust and persist viewer battle-order font size."""
        async with self.context.LOCK:
            display = self.context.normalize_display(
                self.context.STATE.get("display"),
            )

            current = display["battle_order_font_size"]
            adjustment = (
                2 if payload.direction == "increase" else -2
            )
            updated = max(12, min(40, current + adjustment))

            display["battle_order_font_size"] = updated
            self.context.STATE["display"] = display

            self.context.save_state()

        await self.context.broadcast()

        return {
            "battle_order_font_size": updated,
        }