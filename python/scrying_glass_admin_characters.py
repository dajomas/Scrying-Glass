"""Admin characters endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form

class AdminCharactersMixin:
    """Implement admin characters handlers using the shared server context."""

    async def import_characters_csv(self, csv_file: UploadFile=File(...)) -> dict[str, int]:
        """Import characters csv."""
        if not (csv_file.filename or "").lower().endswith(".csv"):
            raise self.context.HTTPException(400, "Upload a .csv file")

        rows = self.context.csv_rows(await csv_file.read())
        imported = [
            self.context.csv_character(row, row_number)
            for row_number, row in enumerate(rows, start=2)
        ]

        ids = [character["id"] for character in imported]
        existing_ids = {monster["id"] for monster in self.context.STATE["monsters"]}
        existing_ids.update(character["id"] for character in self.context.STATE["characters"])

        if len(ids) != len(set(ids)):
            raise self.context.HTTPException(400, "CSV contains duplicate IDs")

        conflicting = set(ids) & existing_ids
        if conflicting:
            raise self.context.HTTPException(
                400,
                "CSV ID already exists in the active campaign encounter: "
                + ", ".join(sorted(conflicting)[:5]),
            )

        self.context.STATE["characters"].extend(imported)
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=False, characters=True)

        return {"count": len(imported)}

    async def create_character(self, character: CharacterCreate):
        """Create character."""
        c = {'id': self.context.uuid.uuid4().hex, **character.model_dump(), 'max_hp': character.hp, 'original_hp': character.hp, 'original_initiative': character.initiative, 'active': False, 'alive': character.hp >= 0, 'visible': False, 'in_turn': False}
        self.context.STATE["characters"].append(c)
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=False, characters=True)

        return c

    async def update_character(self, ident: str, update: CharacterUpdate) -> dict[str, Any]:
        """Update character."""
        character = next(
            (item for item in self.context.STATE["characters"] if item["id"] == ident),
            None,
        )

        if not character:
            raise self.context.HTTPException(404, "Character not found")

        values = update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        hp_delta = values.pop("hp_delta", None)

        for key, value in values.items():
            if key != "in_turn":
                character[key] = value

        if hp_delta is not None:
            character["hp"] += hp_delta

        if "max_hp" in values:
            character["original_hp"] = values["max_hp"]

        if character["hp"] <= 0:
            character["alive"] = False
            character["visible"] = True
            character["in_turn"] = False
        else:
            character["alive"] = True

        if hp_delta is not None:
            self.context.log_hp_change(character, hp_delta)

        if values.get("active") is True:
            self.context.insert_into_battle_order(character)

        if values.get("alive") is False:
            character["visible"] = True
            character["in_turn"] = False

        if values.get("active") is False:
            character["in_turn"] = False

        self.context.set_turn(character, values.get("in_turn"))
        self.context.clean_order()
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=False, characters=True)

        return character

    async def bulk_characters(self, body: BulkCombatantAction) -> dict[str, int]:
        """Apply one validated bulk action to selected campaign characters."""
        allowed = {"join-battle", "leave-battle", "reset", "remove"}

        if body.action not in allowed:
            raise self.context.HTTPException(400, "Unsupported bulk character action")

        targets = self.context.selected_entities("characters", body.ids)

        if body.action == "join-battle":
            for character in targets:
                character["active"] = True

        elif body.action == "leave-battle":
            for character in targets:
                character["active"] = False
                character["in_turn"] = False
            self.context.STATE["battle_order"] = [
                ident for ident in self.context.STATE["battle_order"]
                if ident not in {character["id"] for character in targets}
            ]

        elif body.action == "reset":
            for character in targets:
                self.context.reset_entity(character)

            self.context.clean_order()

        else:  # remove
            removed_ids = {character["id"] for character in targets}
            self.context.STATE["characters"] = [
                character for character in self.context.STATE["characters"]
                if character["id"] not in removed_ids
            ]
            self.context.STATE["battle_order"] = [
                ident for ident in self.context.STATE["battle_order"]
                if ident not in removed_ids
            ]

        # Character records are owned by the active campaign.
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=False, characters=True)
        return {"count": len(targets)}
