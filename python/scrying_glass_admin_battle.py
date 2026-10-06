"""Admin battle endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form

class AdminBattleMixin:
    """Implement admin battle handlers using the shared server context."""

    async def battle_end(self) -> dict[str, str]:
        """Battle end."""
        self.context.clear_turns()
        self.context.STATE["battle_order"] = []

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {"status": "ended"}

    async def reset_all(self):
        """Reset all."""
        for combatant in self.context.entities():
            self.context.reset_entity(combatant)

        self.context.sort_admin_by_max_hp()
        self.context.STATE["battle_order"] = []

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {"status": "reset"}

    async def battle_start(self, payload: BattleStart):
        """Battle start."""
        self.context.begin_battle(payload.order)
        self.context.sort_admin_by_initiative()

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return self.context.public_state()

    async def battle_next(self):
        """Battle next."""
        current = self.context.advance_turn()

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {"current": current}

    async def apply_battle_actions(self, payload: BattleActions) -> dict[str, Any]:
        """Apply battle actions."""
        actor = self.context.entity(payload.actor_id)

        if actor is None:
            raise self.context.HTTPException(404, "Active combatant was not found")

        if not actor.get("active") or not actor.get("alive", True):
            raise self.context.HTTPException(400, "The acting combatant must be active and alive")

        if not actor.get("in_turn"):
            raise self.context.HTTPException(
                400,
                "Only the current active combatant may apply battle actions",
            )

        valid_actions = {"damage", "heal", "buff", "debuff"}
        prepared: list[tuple[dict[str, Any], str, int | None]] = []

        # Validate all rows before changing state, so a malformed row cannot leave
        # prior rows partially applied.
        for row in payload.actions:
            if row.action not in valid_actions:
                raise self.context.HTTPException(400, "Unsupported battle action")

            target = self.context.entity(row.target_id)

            if target is None:
                raise self.context.HTTPException(404, "Target combatant was not found")

            if not target.get("active") or not target.get("alive", True):
                raise self.context.HTTPException(
                    400,
                    f"Target {target['name']} must be active and alive",
                )

            if row.action in {"damage", "heal"}:
                if row.amount is None or row.amount <= 0:
                    raise self.context.HTTPException(
                        400,
                        f"{row.action.title()} requires an amount greater than zero",
                    )
                amount: int | None = row.amount
            else:
                if row.amount is not None:
                    raise self.context.HTTPException(
                        400,
                        f"{row.action.title()} must not include an amount",
                    )
                amount = None

            prepared.append((target, row.action, amount))

        # Apply only after every row passed validation.
        for target, action, amount in prepared:
            if action == "damage":
                target["hp"] -= amount
                self.context.update_alive_state(target)
            elif action == "heal":
                target["hp"] += amount
                self.context.update_alive_state(target)

            self.context.log_battle_action(actor, target, action, amount)

        self.context.clean_order()
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {
            "applied": len(prepared),
            "activity_log": self.context.STATE["activity_log"],
        }
