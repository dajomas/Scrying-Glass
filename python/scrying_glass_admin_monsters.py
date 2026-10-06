"""Admin monsters endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form

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
        image_url = (
            self.context.save_image(image)
            if image is not None and image.filename
            else self.context.dnd_image(fields["monster_species"])
        )

        created = []

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

    async def import_monster(self, monster_file: UploadFile=File(...), color: str=Form(...), quantity: int=Form(1, ge=1, le=50), image: UploadFile | None=File(None)):
        """Import monster."""
        if not (monster_file.filename or '').lower().endswith('.monster'):
            raise self.context.HTTPException(400, 'Upload a .monster file')
        fields = self.context.parse_monster(await monster_file.read())
        image_url = (
            self.context.save_image(image)
            if image and image.filename
            else self.context.dnd_image(fields['monster_species'])
        )

        created = self.context.make_monsters(fields, color, quantity, image_url)

        self.context.STATE['monsters'].extend(created)
        await self.context.combatants_changed(monsters=True, characters=False)
        return created

    async def import_monsters_csv(self, csv_file: UploadFile=File(...)) -> dict[str, int]:
        """Import monsters csv."""
        if not (csv_file.filename or "").lower().endswith(".csv"):
            raise self.context.HTTPException(400, "Upload a .csv file")

        rows = self.context.csv_rows(await csv_file.read())
        imported = [
            self.context.csv_monster(row, row_number)
            for row_number, row in enumerate(rows, start=2)
        ]

        ids = [monster["id"] for monster in imported]
        existing_ids = {monster["id"] for monster in self.context.STATE["monsters"]}
        existing_ids.update(character["id"] for character in self.context.STATE["characters"])

        if len(ids) != len(set(ids)):
            raise self.context.HTTPException(400, "CSV contains duplicate IDs")

        conflicting = set(ids) & existing_ids
        if conflicting:
            raise self.context.HTTPException(
                400,
                "CSV ID already exists in the current setup: "
                + ", ".join(sorted(conflicting)[:5]),
            )

        self.context.STATE["monsters"].extend(imported)
        await self.context.combatants_changed(monsters=True, characters=False)

        return {"count": len(imported)}

    async def edit_monster(self, ident: str, name: str=Form(...), monster_species: str=Form(...), ac: int=Form(...), hp: int=Form(...), max_hp: int=Form(...), original_hp: int=Form(...), color: str=Form(...), initiative: str=Form(''), ally: str=Form('false'), image: UploadFile | None=File(None)):
        """Edit monster."""
        m = next((x for x in self.context.STATE['monsters'] if x['id'] == ident), None)
        if not m:
            raise self.context.HTTPException(404, 'Monster not found')
        parsed_initiative = None if initiative.strip() == '' else int(initiative)
        if parsed_initiative is not None and (not -100 <= parsed_initiative <= 100):
            raise self.context.HTTPException(400, 'Initiative must be between -100 and 100')
        m.update({'name': name.strip(), 'monster_species': monster_species.strip(), 'ac': ac, 'hp': hp, 'max_hp': max_hp, 'original_hp': original_hp, 'color': color, 'initiative': parsed_initiative, 'ally': ally.lower() == 'true'})
        if image and image.filename:
            m['image_url'] = self.context.save_image(image)
        if m['hp'] <= 0:
            m['alive'] = False
            m['visible'] = True
            m['in_turn'] = False
        self.context.clean_order()
        await self.context.combatants_changed(monsters=True, characters=False)
        return m

    async def update_monster(self, ident: str, update: MonsterUpdate) -> dict[str, Any]:
        """Update monster."""
        monster = next(
            (item for item in self.context.STATE["monsters"] if item["id"] == ident),
            None,
        )

        if not monster:
            raise self.context.HTTPException(404, "Monster not found")

        values = update.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        hp_delta = values.pop("hp_delta", None)

        for key, value in values.items():
            if key != "in_turn":
                monster[key] = value

        if hp_delta is not None:
            monster["hp"] += hp_delta

        if monster["hp"] <= 0:
            monster["alive"] = False
            monster["visible"] = True
            monster["in_turn"] = False
        else:
            monster["alive"] = True

        if hp_delta is not None:
            self.context.log_hp_change(monster, hp_delta)

        if values.get("active") is True:
            self.context.insert_into_battle_order(monster)

        if values.get("active") is False:
            monster["in_turn"] = False

        self.context.set_turn(monster, values.get("in_turn"))
        self.context.clean_order()

        await self.context.combatants_changed(monsters=True, characters=False)
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

        if body.action in fields:
            field, value = fields[body.action]

            if body.action == "join-battle":
                for monster in targets:
                    # Prefer the existing activation helper where available.
                    monster[field] = value
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
