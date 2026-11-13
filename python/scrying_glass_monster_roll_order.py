"""Stage automatic/shared monster rolls and one final battle-order proposal."""
from .scrying_glass_monster_raw_roll import raw_roll_patch
from .scrying_glass_monster_initiative_order import order_for_monster_change


class RollOrderError(ValueError):
    """The existing battle order cannot safely be updated."""


def _d20(randint):
    roll = randint(1, 20)
    if type(roll) is not int or not 1 <= roll <= 20:
        raise ValueError("Initiative dice must return an integer from 1 to 20")
    return roll


def plan_monster_rolls(state, targets, randint, *, shared=False):
    targets = list(targets)
    roster = state["monsters"]
    by_id = {monster["id"]: monster for monster in roster}
    ids = [monster["id"] for monster in targets]
    if len(by_id) != len(roster) or len(ids) != len(set(ids)):
        raise ValueError("Monster roll targets must have unique IDs")
    if any(by_id.get(monster["id"]) is not monster for monster in targets):
        raise ValueError("Monster roll target is no longer in this encounter")
    for monster in targets:
        raw_roll_patch(monster, {"initiative_roll": 0})
    common_roll = _d20(randint) if shared and targets else None
    changes = [(monster, raw_roll_patch(monster, {"initiative_roll":
                common_roll if shared else _d20(randint)})) for monster in targets]
    order = list(state.get("battle_order", []))
    anchor = next((monster["id"] for monster, _ in changes if monster["id"] in order), None)
    if anchor is not None:
        candidates = {monster["id"]: dict(monster, **values) for monster, values in changes}
        proposed_state = dict(state, monsters=[candidates.get(monster["id"], monster)
                                              for monster in roster])
        try:
            order = order_for_monster_change(proposed_state, anchor, candidates[anchor])
        except ValueError as exc:
            raise RollOrderError(str(exc)) from exc
    return changes, order


async def roll_monsters_with_order(context, targets, *, shared=False):
    try:
        changes, order = plan_monster_rolls(context.STATE, targets,
                                            context.random.randint, shared=shared)
    except RollOrderError as exc:
        raise context.HTTPException(409, str(exc)) from exc
    except ValueError as exc:
        raise context.HTTPException(422, str(exc)) from exc
    for monster, values in changes:
        monster.update(values)
    context.STATE["battle_order"] = order
    await context.combatants_changed(monsters=True, characters=False)
    return {"count": len(changes)}
