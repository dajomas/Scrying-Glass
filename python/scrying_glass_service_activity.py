"""Activity services using the live server context."""

from __future__ import annotations
from typing import Any, Literal
from pathlib import Path
from fastapi import HTTPException, Request as FastAPIRequest, UploadFile


class ActivityService:
    """Group activity operations without owning a separate copy of runtime state."""

    def __init__(self, context: Any) -> None:
        """Retain the live server context."""
        self.context = context

    def log_battle_action(self, actor: dict[str, Any], target: dict[str, Any], action: Literal['damage', 'heal', 'buff', 'debuff'], amount: int | None) -> None:
        """Log battle action."""
        self.context.STATE["activity_log"].append({
            "id": self.context.uuid.uuid4().hex,
            "timestamp": self.context.datetime.now(self.context.timezone.utc).isoformat(),
            "active_combatant_id": actor["id"],
            "active_combatant": actor["name"],
            "active_combatant_state": self.context.combatant_state(actor),
            "target_combatant_id": target["id"],
            "target_combatant": target["name"],
            "target_combatant_state": self.context.combatant_state(target),
            "action": action,
            "amount": amount,
        })

    def log_hp_change(self, target: dict[str, Any], hp_delta: int) -> None:
        """Log hp change."""
        if hp_delta == 0:
            return

        actor = self.context.active_combatant()
        action = "heal" if hp_delta > 0 else "damage"

        self.context.STATE["activity_log"].append({
            "id": self.context.uuid.uuid4().hex,
            "timestamp": self.context.datetime.now(self.context.timezone.utc).isoformat(),
            "active_combatant_id": actor["id"] if actor else None,
            "active_combatant": actor["name"] if actor else "System",
            "active_combatant_state": self.context.combatant_state(actor),
            "target_combatant_id": target["id"],
            "target_combatant": target["name"],
            "target_combatant_state": self.context.combatant_state(target),
            "action": action,
            "amount": abs(hp_delta),
        })
