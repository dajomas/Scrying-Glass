"""Admin characters endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form
import copy

class AdminCharactersMixin:
    """Implement admin characters handlers using the shared server context."""

    async def import_characters_csv(
        self,
        csv_file: UploadFile = File(...),
    ) -> dict[str, int]:
        """Import CSV characters only into the encounter where the request started."""
        working_state = self.context.STATE

        if not (csv_file.filename or "").lower().endswith(".csv"):
            raise self.context.HTTPException(
                400,
                "Upload a .csv file",
            )

        rows = self.context.csv_rows(await csv_file.read())

        imported = [
            self.context.csv_character(row, row_number)
            for row_number, row in enumerate(rows, start=2)
        ]

        if self.context.STATE is not working_state:
            raise self.context.HTTPException(
                409,
                "The encounter changed while this request was running. Retry.",
            )

        ids = [character["id"] for character in imported]

        existing_ids = {
            monster["id"]
            for monster in working_state["monsters"]
        }
        existing_ids.update(
            character["id"]
            for character in working_state["characters"]
        )

        if len(ids) != len(set(ids)):
            raise self.context.HTTPException(
                400,
                "CSV contains duplicate IDs",
            )

        conflicting = set(ids) & existing_ids
        if conflicting:
            raise self.context.HTTPException(
                400,
                "CSV ID already exists in the active campaign encounter: "
                + ", ".join(sorted(conflicting)[:5]),
            )

        working_state["characters"].extend(imported)
        for combatant in imported:
            self.context.insert_into_battle_order(combatant)

        await self.context.combatants_changed(
            monsters=False,
            characters=True,
        )

        return {"count": len(imported)}

    async def create_character(self, character: CharacterCreate):
        """Create character."""
        c = {'id': self.context.uuid.uuid4().hex, **character.model_dump(), 'max_hp': character.hp, 'original_hp': character.hp, 'original_initiative': character.initiative, 'active': False, 'alive': character.hp > 0, 'visible': False, 'in_turn': False}
        self.context.STATE["characters"].append(c)
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=False, characters=True)

        return c

    async def update_character(
        self,
        ident: str,
        update: CharacterUpdate,
    ) -> dict[str, Any]:
        """Validate the update and log HP changes before changing the turn."""
        import copy

        character = next(
            (
                item
                for item in self.context.STATE["characters"]
                if item["id"] == ident
            ),
            None,
        )

        if character is None:
            raise self.context.HTTPException(
                404,
                "Character not found",
            )

        values = {
            key: value
            for key, value in update.model_dump(
                exclude_unset=True,
            ).items()
            if value is not None or key == "initiative"
        }

        hp_delta = values.pop("hp_delta", None)
        requested_turn = values.get("in_turn")

        candidate = copy.deepcopy(character)

        for key, value in values.items():
            if key != "in_turn":
                candidate[key] = value

        if hp_delta is not None:
            candidate["hp"] += hp_delta

        if "max_hp" in values:
            candidate["original_hp"] = values["max_hp"]

        hp_changed = "hp" in values or hp_delta is not None

        if "alive" not in values and hp_changed:
            candidate["alive"] = candidate["hp"] > 0

        if not candidate.get("alive"):
            candidate["visible"] = True
            candidate["in_turn"] = False

        if not candidate.get("active"):
            candidate["in_turn"] = False

        if requested_turn is True and (
            not candidate.get("active")
            or not candidate.get("alive")
        ):
            raise self.context.HTTPException(
                400,
                "Only an active living combatant may have the battle turn",
            )

        self.context.remember_turn_successors()

        if hp_delta is not None:
            self.context.log_hp_change(candidate, hp_delta)

        character.update(candidate)
        self.context.set_turn(character, requested_turn)

        if character.get("active") and character.get("alive"):
            self.context.insert_into_battle_order(character)

        self.context.clean_order()

        await self.context.combatants_changed(
            monsters=False,
            characters=True,
        )

        return character

    async def bulk_characters(self, body: BulkCombatantAction) -> dict[str, int]:
        """Apply one validated bulk action to selected campaign characters."""
        allowed = {"join-battle", "leave-battle", "reset", "remove"}

        if body.action not in allowed:
            raise self.context.HTTPException(400, "Unsupported bulk character action")

        targets = self.context.selected_entities("characters", body.ids)

        self.context.remember_turn_successors()

        if body.action == "join-battle":
            for character in targets:
                character["active"] = True
                self.context.insert_into_battle_order(character)

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
