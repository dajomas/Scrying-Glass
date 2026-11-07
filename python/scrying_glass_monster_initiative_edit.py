"""Existing-monster bonus editing on the standard authenticated edit route."""
from fastapi import File, Form, UploadFile
from fastapi.params import Form as FormParameter
from pydantic import ValidationError
import copy
from .scrying_glass_monster_selection import CandidateMonstersMixin
from .scrying_glass_classes import BulkCombatantAction
from .scrying_glass_initiative_input import creation_bonus_fields
from .scrying_glass_monster_initiative import initiative_patch, legacy_total_patch


class InitiativeEditMonstersMixin(CandidateMonstersMixin):
    async def edit_monster(
        self, ident: str, name: str = Form(...),
        monster_species: str = Form(...), ac: int = Form(...),
        hp: int = Form(...), max_hp: int = Form(...),
        original_hp: int = Form(...), color: str = Form(...),
        initiative: str = Form(""), ally: str = Form("false"),
        image: UploadFile | None = File(None),
        initiative_bonus: str = Form(""),
    ):
        """Blank or omitted bonus preserves assignment; explicit numbers are manual."""
        monster = next((item for item in self.context.STATE["monsters"]
                        if item["id"] == ident), None)
        if monster is None:
            raise self.context.HTTPException(404, "Monster not found")
        if isinstance(initiative_bonus, FormParameter):
            initiative_bonus = initiative_bonus.default
        try:
            bonus = (None if not initiative_bonus.strip()
                     else creation_bonus_fields(initiative_bonus))
        except ValueError as exc:
            raise self.context.HTTPException(422, str(exc)) from exc
        try:
            parsed_initiative = None if not initiative.strip() else int(initiative)
        except ValueError as exc:
            raise self.context.HTTPException(400, "Initiative must be a whole number or empty") from exc
        ally_value = ally.strip().lower()
        if ally_value not in {"true", "false"}:
            raise self.context.HTTPException(400, "Ally must be true or false")
        changed_total = parsed_initiative != monster.get("initiative")
        try:
            validated = self.context.MonsterUpdate(
                name=name.strip(), monster_species=monster_species.strip(), ac=ac,
                hp=hp, max_hp=max_hp, original_hp=original_hp,
                color=color.strip(), ally=ally_value == "true",
                **({"initiative": parsed_initiative} if changed_total else {}),
            )
        except ValidationError as exc:
            errors = [{"field": ".".join(str(part) for part in error["loc"]),
                       "message": error["msg"]} for error in exc.errors()]
            raise self.context.HTTPException(422, errors) from exc
        candidate = copy.deepcopy(monster)
        values = validated.model_dump(exclude_unset=True)
        candidate.update(values)
        try:
            if changed_total:
                candidate.update(legacy_total_patch(monster, parsed_initiative))
            if bonus is not None:
                candidate.update(initiative_patch(candidate,
                    bonus=bonus["initiative_bonus"], origin=bonus["initiative_bonus_origin"]))
        except ValueError as exc:
            raise self.context.HTTPException(422, str(exc)) from exc
        from .scrying_glass_statistics import legacy_max_edit
        try:
            legacy_max_edit(candidate, values)
        except ValueError as exc:
            raise self.context.HTTPException(422, str(exc)) from exc
        from .scrying_glass_feature_rules import sync_health
        sync_health(candidate)
        if not candidate.get("active"):
            candidate["in_turn"] = False
        proposed_order = None
        if candidate.get("initiative") != monster.get("initiative"):
            from .scrying_glass_monster_initiative_order import order_for_monster_change
            try:
                proposed_order = order_for_monster_change(self.context.STATE, ident, candidate)
            except ValueError as exc:
                raise self.context.HTTPException(409, str(exc)) from exc
        if image is not None and image.filename:
            candidate["image_url"] = self.context.save_image(image)
        self.context.remember_turn_successors()
        monster.update(candidate)
        if proposed_order is not None:
            self.context.STATE["battle_order"] = proposed_order
        if monster.get("active") and monster.get("alive"):
            self.context.insert_into_battle_order(monster)
        self.context.clean_order()
        await self.context.combatants_changed(monsters=True, characters=False)
        return monster

    async def roll_monster_initiative(self):
        """Roll once per monster and update the existing active order atomically."""
        from .scrying_glass_monster_roll_order import roll_monsters_with_order
        return await roll_monsters_with_order(self.context, self.context.STATE["monsters"])

    async def bulk_monsters(self, body: BulkCombatantAction):
        """Use one shared raw roll only for selected monsters; delegate other actions."""
        if body.action != "roll-shared-initiative":
            return await super().bulk_monsters(body)
        targets = self.context.selected_entities("monsters", body.ids)
        from .scrying_glass_monster_roll_order import roll_monsters_with_order
        return await roll_monsters_with_order(self.context, targets, shared=True)
