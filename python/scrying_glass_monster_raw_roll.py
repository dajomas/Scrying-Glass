"""Strict raw-roll input and mutation; callers provide route transactions."""
from .scrying_glass_monster_initiative import initiative_patch

MIN_INTEGER = -(2 ** 63)
MAX_INTEGER = 2 ** 63 - 1


def raw_roll_patch(monster, body):
    if not isinstance(body, dict) or set(body) != {"initiative_roll"}:
        raise ValueError("Expected only initiative_roll (integer or null)")
    roll = body["initiative_roll"]
    if roll is not None and (type(roll) is not int or not MIN_INTEGER <= roll <= MAX_INTEGER):
        raise ValueError("Initiative roll must be a signed 64-bit integer or null")
    values = initiative_patch(monster, roll=roll)
    total = values["initiative"]
    if total is not None and not MIN_INTEGER <= total <= MAX_INTEGER:
        raise ValueError("Calculated initiative exceeds the signed 64-bit storage range")
    return values


async def apply_raw_roll(context, ident, body):
    monster = next((item for item in context.STATE["monsters"] if item["id"] == ident), None)
    if monster is None:
        raise context.HTTPException(404, "Monster not found")
    try:
        values = raw_roll_patch(monster, body)
    except ValueError as exc:
        raise context.HTTPException(422, str(exc)) from exc
    if monster.get("active") and values["initiative"] is None:
        raise context.HTTPException(400, "Leave battle before clearing initiative")
    from .scrying_glass_monster_initiative_order import order_for_monster_change
    candidate = dict(monster, **values)
    try:
        order = order_for_monster_change(context.STATE, ident, candidate)
    except ValueError as exc:
        raise context.HTTPException(409, str(exc)) from exc
    monster.update(values)
    context.STATE["battle_order"] = order
    await context.combatants_changed(monsters=True, characters=False)
    return monster
