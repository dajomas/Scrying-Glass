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

    def clean_order(self) -> None:
        """Remove combatants that are no longer eligible from battle order."""
        known = {x['id'] for x in self.context.entities()}
        self.context.STATE['battle_order'] = [x for x in self.context.STATE['battle_order'] if x in known]

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
        self.context.clear_turns()
        x['in_turn'] = True
        x['visible'] = True

    def eligible(self) -> list[dict[str, Any]]:
        """Eligible."""
        return [x for x in self.context.entities() if x.get('active') and x.get('alive', True)]

    def begin_battle(self, order: list[str]) -> None:
        """Begin battle."""
        wanted = {x['id'] for x in self.context.eligible()}
        if len(order) != len(wanted) or set(order) != wanted:
            raise self.context.HTTPException(400, 'Battle order must include every active living combatant exactly once')
        self.context.STATE['battle_order'] = order
        self.context.clear_turns()
        if order:
            self.context.entity(order[0])['in_turn'] = True
            self.context.entity(order[0])['visible'] = True

    def advance_turn(self) -> dict[str, Any] | None:
        """Advance turn."""
        ids = {x['id'] for x in self.context.eligible()}
        if not ids:
            self.context.clear_turns()
            self.context.STATE['battle_order'] = []
            return None
        order = [i for i in self.context.STATE['battle_order'] if i in ids]
        order += [x['id'] for x in sorted(self.context.eligible(), key=lambda z: (-self.context.numeric_initiative(z), z['name'].lower())) if x['id'] not in order]
        self.context.STATE['battle_order'] = order
        pos = next((n for n, i in enumerate(order) if self.context.entity(i).get('in_turn')), -1)
        self.context.clear_turns()
        target = self.context.entity(order[(pos + 1) % len(order)])
        target['in_turn'] = True
        target['visible'] = True
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
