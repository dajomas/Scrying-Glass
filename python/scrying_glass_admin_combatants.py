"""Admin combatants endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form

class AdminCombatantsMixin:
    """Implement admin combatants handlers using the shared server context."""

    async def delete_combatant(self, ident: str) -> dict[str, str]:
        """Delete combatant."""
        monster_index = next(
            (
                index
                for index, monster in enumerate(self.context.STATE["monsters"])
                if monster["id"] == ident
            ),
            None,
        )

        removed_character = False
        is_monster = monster_index is None
        is_character = not is_monster

        if monster_index is not None:
            removed = self.context.STATE["monsters"].pop(monster_index)
        else:
            character_index = next(
                (
                    index
                    for index, character in enumerate(self.context.STATE["characters"])
                    if character["id"] == ident
                ),
                None,
            )

            is_character = character_index is not None
            if character_index is None:
                raise self.context.HTTPException(404, "Combatant not found")

            removed = self.context.STATE["characters"].pop(character_index)
            removed_character = True

        self.context.STATE["battle_order"] = [
            combatant_id
            for combatant_id in self.context.STATE["battle_order"]
            if combatant_id != ident
        ]

        if removed_character:
            self.context.save_active_campaign_characters()

        await self.context.combatants_changed(monsters=is_monster, characters=is_character)

        return {
            "id": ident,
            "name": str(removed.get("name", "Combatant")),
        }

    async def reset_one_combatant(self, ident: str):
        """Reset one combatant."""
        x = self.context.entity(ident)

        if not x:
            raise self.context.HTTPException(404, "Combatant not found")

        is_character = x in self.context.STATE["characters"]

        self.context.reset_entity(x)
        self.context.clean_order()

        if is_character:
            self.context.save_active_campaign_characters()

        await self.context.combatants_changed(monsters=not is_character, characters=is_character)


        return x
