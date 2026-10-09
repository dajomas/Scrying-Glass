"""Battle services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path
from fastapi import HTTPException, Request as FastAPIRequest, UploadFile


class BattleService:
    """Group battle operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context

    def clear_turns(self) -> None:
        """Clear turns."""
        for x in self.context.entities():
            x['in_turn'] = False

    def remember_turn_successors(self) -> None:
        """Remember successors and the boundary between this and next round."""
        current = self.context.active_combatant()

        if current is None:
            return

        order = list(self.context.STATE["battle_order"])
        current_id = current["id"]

        if current_id not in order:
            return

        position = order.index(current_id)
        remaining_this_round = order[position + 1:]

        self.context.STATE["turn_successors"] = (
            remaining_this_round
            + order[:position + 1]
        )

        self.context.STATE["turn_successors_before_wrap"] = (
            remaining_this_round
        )

    def clean_order(self) -> None:
        """Keep each active living combatant at most once in battle order."""
        eligible_ids = {
            combatant["id"]
            for combatant in self.context.eligible()
        }

        seen: set[str] = set()
        cleaned: list[str] = []

        for ident in self.context.STATE["battle_order"]:
            if ident in eligible_ids and ident not in seen:
                cleaned.append(ident)
                seen.add(ident)

        self.context.STATE["battle_order"] = cleaned

    def insert_into_battle_order(self, combatant: dict[str, Any]) -> None:
        'Insert a newly activated living combatant into an existing battle order.\n\n    Higher numeric initiative acts first. On equal initiative, the newly added\n    combatant is placed after all existing combatants with that same initiative.\n    Combatants without initiative are placed after numeric initiatives.\n    '
        if not self.context.STATE['battle_order']:
            return
        if not combatant.get('active') or not combatant.get('alive', True):
            return
        combatant_id = combatant['id']
        if combatant_id in self.context.STATE['battle_order']:
            return
        combatant_initiative = combatant.get('initiative')
        has_numeric_initiative = isinstance(combatant_initiative, int) and (not isinstance(combatant_initiative, bool))
        insert_at = len(self.context.STATE['battle_order'])
        for index, existing_id in enumerate(self.context.STATE['battle_order']):
            existing = self.context.entity(existing_id)
            if existing is None:
                continue
            existing_initiative = existing.get('initiative')
            existing_has_numeric_initiative = isinstance(existing_initiative, int) and (not isinstance(existing_initiative, bool))
            if not has_numeric_initiative:
                continue
            if not existing_has_numeric_initiative:
                insert_at = index
                break
            if existing_initiative < combatant_initiative:
                insert_at = index
                break
        self.context.STATE['battle_order'].insert(insert_at, combatant_id)

    def sort_admin_by_initiative(self) -> None:
        """Sort admin by initiative."""
        self.context.STATE['monsters'].sort(key=self.context.admin_initiative_key)
        self.context.STATE['characters'].sort(key=self.context.admin_initiative_key)

    def sort_admin_by_max_hp(self) -> None:
        """Sort admin by max hp."""
        self.context.STATE['monsters'].sort(key=self.context.admin_max_hp_key)
        self.context.STATE['characters'].sort(key=self.context.admin_max_hp_key)

    def set_turn(self, x: dict[str, Any], requested: bool | None) -> None:
        """Set turn."""
        if requested is False:
            x['in_turn'] = False
            return
        if requested is not True:
            return
        if not x.get('active') or not x.get('alive', True):
            raise self.context.HTTPException(400, 'Only an active living combatant may have the battle turn')
        self.context.STATE["turn_successors"] = []
        self.context.STATE["turn_successors_before_wrap"] = []
        self.context.clear_turns()
        x['in_turn'] = True
        x['visible'] = True

    def eligible(self) -> list[dict[str, Any]]:
        """Eligible."""
        return [x for x in self.context.entities() if x.get('active') and x.get('alive', True)]

    def begin_battle(self, order: list[str]) -> None:
        """Start the supplied turn order at round one."""
        wanted = {
            combatant["id"]
            for combatant in self.context.eligible()
        }

        if len(order) != len(wanted) or set(order) != wanted:
            raise self.context.HTTPException(
                400,
                "Battle order must include every active living "
                "combatant exactly once",
            )

        if not order:
            raise self.context.HTTPException(400, "Activate at least one living combatant before starting a battle")

        self.context.STATE["battle_order"] = list(order)
        self.context.STATE["battle_round"] = 1
        self.context.STATE["turn_successors"] = []
        self.context.STATE["turn_successors_before_wrap"] = []

        self.context.clear_turns()

        if order:
            target = self.context.entity(order[0])
            target["in_turn"] = True
            target["visible"] = True

    def advance_turn(self) -> dict[str, Any] | None:
        """Advance the turn and increment the round when order wraps."""
        eligible = self.context.eligible()
        eligible_ids = {
            combatant["id"]
            for combatant in eligible
        }

        if not eligible_ids:
            self.context.clear_turns()
            self.context.STATE["battle_order"] = []
            self.context.STATE["turn_successors"] = []
            self.context.STATE["turn_successors_before_wrap"] = []
            return None

        current = self.context.active_combatant()
        current_id = current["id"] if current is not None else None

        remembered_successors = list(
            self.context.STATE.get("turn_successors", [])
        )
        before_wrap = set(
            self.context.STATE.get(
                "turn_successors_before_wrap",
                [],
            )
        )

        self.context.clean_order()
        order = list(self.context.STATE["battle_order"])

        ordered_ids = set(order)

        for combatant in sorted(
            eligible,
            key=self.context.admin_initiative_key,
        ):
            ident = combatant["id"]

            if ident not in ordered_ids:
                order.append(ident)
                ordered_ids.add(ident)

        self.context.STATE["battle_order"] = order
        wrapped = False

        if current_id in order:
            position = order.index(current_id)
            next_position = (position + 1) % len(order)
            next_id = order[next_position]
            wrapped = next_position == 0
        else:
            next_id = next(
                (
                    ident
                    for ident in remembered_successors
                    if ident in eligible_ids
                ),
                None,
            )

            if next_id is not None:
                wrapped = next_id not in before_wrap
            else:
                next_id = order[0]
                wrapped = bool(remembered_successors)

        battle_round = self.context.STATE.get("battle_round", 0)

        if type(battle_round) is not int or battle_round < 1:
            battle_round = 1
        elif wrapped:
            battle_round += 1

        self.context.STATE["battle_round"] = battle_round

        self.context.clear_turns()
        self.context.STATE["turn_successors"] = []
        self.context.STATE["turn_successors_before_wrap"] = []

        target = self.context.entity(next_id)
        target["in_turn"] = True
        target["visible"] = True

        return target

    def selected_entities(self, kind: Literal['characters', 'monsters'], ids: list[str]) -> list[dict[str, Any]]:
        """Selected entities."""
        selected_ids = self.context.unique_ids(ids)
        items = self.context.STATE[kind]
        by_id = {item["id"]: item for item in items}
        missing = [ident for ident in selected_ids if ident not in by_id]

        if missing:
            raise self.context.HTTPException(404, f"Selected {kind[:-1]} no longer exists")

        return [by_id[ident] for ident in selected_ids]
