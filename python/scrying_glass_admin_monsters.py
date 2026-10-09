"""Admin monsters endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form
import asyncio
import copy

class AdminMonstersMixin:
    """Implement admin monsters handlers using the shared server context."""

    async def roll_monster_initiative(self):
        """Roll monster initiative."""
        for monster in self.context.STATE['monsters']:
            monster['initiative'] = self.context.random.randint(1, 20)
        await self.context.combatants_changed(monsters=True, characters=False)
        return {'count': len(self.context.STATE['monsters'])}

    async def create_monster(self, name: str=Form(...), monster_species: str=Form(...), ac: int=Form(...), hprangestart: str=Form(...), hprangeend: str=Form(''), color: str=Form(...), quantity: int=Form(1, ge=1, le=50), image: UploadFile | None=File(None)) -> list[dict[str, Any]]:
        """Create monster."""
        next_hp = self.context.hp_value_factory(hprangestart, hprangeend)

        fields = {
            "name": name.strip(),
            "monster_species": monster_species.strip(),
            "ac": ac,
        }

        working_state = self.context.STATE
        if image is not None and image.filename:
            image_url = self.context.save_image(image)
        else:
            image_url = await asyncio.to_thread(
                self.context.dnd_image,
                fields["monster_species"],
            )

        created = []

        if self.context.STATE is not working_state:
            raise self.context.HTTPException(
                409,
                "The encounter changed while this request was running. Retry.",
            )
        for number in range(1, quantity + 1):
            generated_name = (
                fields["name"]
                if quantity == 1
                else f"{fields['name']} - {number}"
            )
            rolled_hp = next_hp()

            created.append(
                self.context.make_monster(
                    {
                        **fields,
                        "name": generated_name,
                        "hp": rolled_hp,
                    },
                    color,
                    None,
                    image_url,
                )
            )

        self.context.STATE["monsters"].extend(created)
        await self.context.combatants_changed(monsters=True, characters=False)
        return created

    async def import_monster(
        self,
        monster_file: UploadFile = File(...),
        color: str = Form(...),
        quantity: int = Form(1, ge=1, le=50),
        image: UploadFile | None = File(None),
    ):
        """Import monsters only into the encounter where the request started."""
        working_state = self.context.STATE

        if not (monster_file.filename or "").lower().endswith(".monster"):
            raise self.context.HTTPException(
                400,
                "Upload a .monster file",
            )

        fields = self.context.parse_monster(
            await monster_file.read()
        )

        if image is not None and image.filename:
            image_url = self.context.save_image(image)
        else:
            image_url = await asyncio.to_thread(
                self.context.dnd_image,
                fields["monster_species"],
            )

        created = self.context.make_monsters(
            fields,
            color,
            quantity,
            image_url,
        )

        if self.context.STATE is not working_state:
            raise self.context.HTTPException(
                409,
                "The encounter changed while this request was running. Retry.",
            )

        working_state["monsters"].extend(created)

        await self.context.combatants_changed(
            monsters=True,
            characters=False,
        )

        return created

    async def import_monsters_csv(
        self,
        csv_file: UploadFile = File(...),
    ) -> dict[str, int]:
        """Import CSV monsters only into the encounter where the request started."""
        working_state = self.context.STATE

        if not (csv_file.filename or "").lower().endswith(".csv"):
            raise self.context.HTTPException(
                400,
                "Upload a .csv file",
            )

        rows = self.context.csv_rows(await csv_file.read())

        imported = [
            self.context.csv_monster(row, row_number)
            for row_number, row in enumerate(rows, start=2)
        ]

        if self.context.STATE is not working_state:
            raise self.context.HTTPException(
                409,
                "The encounter changed while this request was running. Retry.",
            )

        ids = [monster["id"] for monster in imported]

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
                "CSV ID already exists in the active encounter: "
                + ", ".join(sorted(conflicting)[:5]),
            )

        working_state["monsters"].extend(imported)
        for combatant in imported:
            self.context.insert_into_battle_order(combatant)

        await self.context.combatants_changed(
            monsters=True,
            characters=False,
        )

        return {"count": len(imported)}

    async def edit_monster(
        self,
        ident: str,
        name: str = Form(...),
        monster_species: str = Form(...),
        ac: int = Form(...),
        hp: int = Form(...),
        max_hp: int = Form(...),
        original_hp: int = Form(...),
        color: str = Form(...),
        initiative: str = Form(""),
        ally: str = Form("false"),
        image: UploadFile | None = File(None),
    ):
        """Validate all edit fields before changing the live monster."""
        import copy
        from pydantic import ValidationError

        monster = next(
            (
                item
                for item in self.context.STATE["monsters"]
                if item["id"] == ident
            ),
            None,
        )

        if monster is None:
            raise self.context.HTTPException(
                404,
                "Monster not found",
            )

        try:
            parsed_initiative = (
                None
                if not initiative.strip()
                else int(initiative)
            )
        except ValueError as exc:
            raise self.context.HTTPException(
                400,
                "Initiative must be a whole number or empty",
            ) from exc

        ally_value = ally.strip().lower()
        if ally_value not in {"true", "false"}:
            raise self.context.HTTPException(
                400,
                "Ally must be true or false",
            )

        try:
            validated = self.context.MonsterUpdate(
                name=name.strip(),
                monster_species=monster_species.strip(),
                ac=ac,
                hp=hp,
                max_hp=max_hp,
                original_hp=original_hp,
                color=color.strip(),
                initiative=parsed_initiative,
                ally=ally_value == "true",
            )
        except ValidationError as exc:
            errors = [
                {
                    "field": ".".join(
                        str(part) for part in error["loc"]
                    ),
                    "message": error["msg"],
                }
                for error in exc.errors()
            ]

            raise self.context.HTTPException(
                422,
                errors,
            ) from exc

        candidate = copy.deepcopy(monster)
        candidate.update(
            validated.model_dump(exclude_unset=True)
        )

        self.context.update_alive_state(candidate)

        if not candidate.get("active"):
            candidate["in_turn"] = False

        if image is not None and image.filename:
            candidate["image_url"] = self.context.save_image(image)

        self.context.remember_turn_successors()
        monster.update(candidate)

        if monster.get("active") and monster.get("alive"):
            self.context.insert_into_battle_order(monster)

        self.context.clean_order()

        await self.context.combatants_changed(
            monsters=True,
            characters=False,
        )

        return monster

    async def update_monster(
        self,
        ident: str,
        update: MonsterUpdate,
    ) -> dict[str, Any]:
        """Validate the update and log HP changes before changing the turn."""
        import copy

        monster = next(
            (
                item
                for item in self.context.STATE["monsters"]
                if item["id"] == ident
            ),
            None,
        )

        if monster is None:
            raise self.context.HTTPException(
                404,
                "Monster not found",
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

        candidate = copy.deepcopy(monster)

        for key, value in values.items():
            if key != "in_turn":
                candidate[key] = value

        if hp_delta is not None:
            candidate["hp"] += hp_delta

        candidate["alive"] = candidate["hp"] > 0

        if not candidate["alive"]:
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

        monster.update(candidate)
        self.context.set_turn(monster, requested_turn)

        if monster.get("active") and monster.get("alive"):
            self.context.insert_into_battle_order(monster)

        self.context.clean_order()

        await self.context.combatants_changed(
            monsters=True,
            characters=False,
        )

        return monster

    async def bulk_monsters(self, body: BulkCombatantAction) -> dict[str, int]:
        """Apply one validated bulk action to selected monsters."""
        fields = {
            "join-battle": ("active", True),
            "leave-battle": ("active", False),
            "set-ally": ("ally", True),
            "unset-ally": ("ally", False),
            "show-ac": ("show_ac", True),
            "hide-ac": ("show_ac", False),
            "show-hp": ("show_hp", True),
            "hide-hp": ("show_hp", False),
            "show-initiative": ("show_initiative", True),
            "hide-initiative": ("show_initiative", False),
        }
        allowed = {*fields, "reset", "remove"}

        if body.action not in allowed:
            raise self.context.HTTPException(400, "Unsupported bulk monster action")

        targets = self.context.selected_entities("monsters", body.ids)

        self.context.remember_turn_successors()

        if body.action in fields:
            field, value = fields[body.action]

            if body.action == "join-battle":
                for monster in targets:
                    monster[field] = value
                    self.context.insert_into_battle_order(monster)
            elif body.action == "leave-battle":
                removed_ids = {monster["id"] for monster in targets}
                for monster in targets:
                    monster[field] = value
                    monster["in_turn"] = False
                self.context.STATE["battle_order"] = [
                    ident for ident in self.context.STATE["battle_order"]
                    if ident not in removed_ids
                ]
            else:
                for monster in targets:
                    monster[field] = value

        elif body.action == "reset":
            for monster in targets:
                self.context.reset_entity(monster)

            self.context.clean_order()

        else:  # remove
            removed_ids = {monster["id"] for monster in targets}
            self.context.STATE["monsters"] = [
                monster for monster in self.context.STATE["monsters"]
                if monster["id"] not in removed_ids
            ]
            self.context.STATE["battle_order"] = [
                ident for ident in self.context.STATE["battle_order"]
                if ident not in removed_ids
            ]

        await self.context.combatants_changed(monsters=True, characters=False)
        return {"count": len(targets)}
