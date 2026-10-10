"""Admin characters endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form
from .scrying_glass_turn_rules import can_take_turn
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

        existing_ids.update(
            lair["id"]
            for lair in working_state.get("lairs", [])
        )

        # Characters are campaign-owned and will be loaded into every saved setup.
        campaign = self.context.active_campaign()
        for setup_name in self.context.STORAGE.list_setups(campaign):
            saved = self.context.STORAGE.load_setup(campaign, setup_name)
            existing_ids.update(
                participant["id"]
                for participant in [*saved["monsters"], *saved.get("lairs", [])]
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
                "CSV ID conflicts with a participant in this campaign: "
                + ", ".join(sorted(conflicting)[:5]),
            )

        # Normalize health/life state before deciding whether rows may take turns.
        try:
            imported = self.context.normalize_state({"characters": imported})["characters"]
        except ValueError as exc:
            raise self.context.HTTPException(400, f"CSV combatant state is invalid: {exc}") from exc

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
        critical_hit = values.pop("critical_hit", False)
        requested_turn = values.get("in_turn")

        candidate = copy.deepcopy(character)

        for key, value in values.items():
            if key != "in_turn":
                candidate[key] = value

        if hp_delta is not None:
            from .scrying_glass_feature_rules import apply_hp
            apply_hp(candidate,hp_delta,critical=critical_hit)

        if "max_hp" in values:
            candidate["original_hp"] = values["max_hp"]

        hp_changed = "hp" in values or hp_delta is not None

        from .scrying_glass_feature_rules import sync_health
        if "alive" in values:
            candidate['life_state'] = ('standing' if candidate['hp']>0 else 'down') if values['alive'] else 'dead'
        if hp_changed or 'alive' in values or 'max_hp' in values:
            sync_health(candidate)

        if not candidate.get("alive"):
            candidate["visible"] = True
        if not can_take_turn(candidate):
            candidate["in_turn"] = False

        if not candidate.get("active"):
            candidate["in_turn"] = False

        if requested_turn is True and not can_take_turn(candidate):
            raise self.context.HTTPException(
                400,
                "Only an active, turn-eligible combatant may have the battle turn",
            )

        self.context.remember_turn_successors()

        if hp_delta is not None:
            self.context.log_hp_change(candidate, hp_delta)

        character.update(candidate)
        self.context.set_turn(character, requested_turn)

        if can_take_turn(character):
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
