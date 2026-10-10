"""Admin battle endpoint handlers; route registration stays in AdminAPI."""

from __future__ import annotations
from typing import Any
from fastapi import File, Form
from .scrying_glass_feature_rules import apply_hp
from .scrying_glass_turn_rules import permanently_dead,can_take_turn

class AdminBattleMixin:
    """Implement admin battle handlers using the shared server context."""

    async def battle_end(self) -> dict[str, str]:
        """Battle end."""
        self.context.clear_turns()
        self.context.STATE["battle_round"] = 0
        self.context.STATE["turn_successors_before_wrap"] = []
        self.context.STATE["battle_order"] = []
        self.context.STATE["turn_successors"] = []

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {"status": "ended"}

    async def reset_all(self):
        """Reset all."""
        for combatant in self.context.entities():
            self.context.reset_entity(combatant)

        for lair in self.context.STATE.get('lairs', []):
            lair.update(active=False, visible=False, in_turn=False)
        self.context.sort_admin_by_max_hp()
        self.context.STATE["battle_round"] = 0
        self.context.STATE["turn_successors_before_wrap"] = []
        self.context.STATE["battle_order"] = []
        self.context.STATE["turn_successors"] = []

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {"status": "reset"}

    async def battle_start(self, payload: BattleStart):
        """Battle start."""
        if getattr(self.context,'features',None):
            self.context.features.store.save_snapshot(self.context.active_campaign(),self.context.STATE,'checkpoint','Before battle')
        self.context.begin_battle(payload.order)
        self.context.sort_admin_by_initiative()

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return self.context.public_state()

    async def battle_next(self):
        """Battle next."""
        previous=self.context.active_combatant()
        remembered=self.context.STATE.get('turn_successors',[])
        if getattr(self.context,'features',None):
            self.context.features.expire(previous['id'] if previous else (remembered[-1] if remembered else None),'end')
        current = self.context.advance_turn()
        if getattr(self.context,'features',None) and current:
            self.context.features.expire(current['id'],'start')

        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {"current": current}

    async def apply_battle_actions(self, payload: BattleActions) -> dict[str, Any]:
        """Apply battle actions."""
        actor = self.context.entity(payload.actor_id)

        if actor is not None and actor.get('kind') == 'lair':
            raise self.context.HTTPException(400, 'Use the lair action endpoint')
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
        prepared = []

        # Validate all rows before changing state, so a malformed row cannot leave
        # prior rows partially applied.
        for row in payload.actions:
            if row.action not in valid_actions:
                raise self.context.HTTPException(400, "Unsupported battle action")

            target = self.context.entity(row.target_id)

            if target is not None and target.get('kind') == 'lair':
                raise self.context.HTTPException(400, 'Lairs cannot be targeted')
            if target is None:
                raise self.context.HTTPException(404, "Target combatant was not found")

            if not target.get("active"):
                raise self.context.HTTPException(
                    400,
                    f"Target {target['name']} must be active",
                )

            if permanently_dead(target):
                raise self.context.HTTPException(400,'Explicitly recover a dead combatant before applying battle actions')
            if row.action not in {'damage','heal'} and not target.get("alive", True):
                raise self.context.HTTPException(
                    400,
                    f"Target {target['name']} must be alive for {row.action}",
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

            critical=getattr(row,'critical_hit',False)
            if critical and row.action!='damage':
                raise self.context.HTTPException(422,'Critical hit applies only to damage')
            prepared.append((target,row.action,amount,critical))

        # Apply only after every row passed validation.
        self.context.remember_turn_successors()

        for target, action, amount, critical in prepared:
            if action == "damage":
                result=apply_hp(target,-amount,critical=critical)
                if getattr(self.context,'features',None):
                    if result['instant_death']:
                        self.context.features.log('instant-death',target,note=f"Excess damage {result['excess']} ≥ maximum HP {target['max_hp']}")
                    elif result['failed_saves']:
                        self.context.features.log('death-save-failure',target,result['failed_saves'],note=f"Damage at 0 HP; failures now {target['death_failures']}/3"+(' (critical hit)' if critical else ''))
                    if target.get('concentrating'):
                        self.context.features.log('concentration-reminder',target,note='Resolve concentration manually')
            elif action == "heal":
                apply_hp(target,amount)

                if can_take_turn(target):
                    self.context.insert_into_battle_order(target)

            self.context.log_battle_action(actor, target, action, amount)

        self.context.clean_order()
        self.context.save_active_campaign_characters()
        await self.context.combatants_changed(monsters=True, characters=True)

        return {
            "applied": len(prepared),
            "activity_log": self.context.STATE["activity_log"],
        }
