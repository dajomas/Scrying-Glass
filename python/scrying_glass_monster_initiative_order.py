"""Stable ordering proposal for an existing monster initiative change."""
from .scrying_glass_lair_rules import initiative_key


def order_for_monster_change(state, ident, candidate):
    """Return a new order without changing membership, turn flags or other state."""
    order = list(state.get("battle_order", []))
    if ident not in order:
        return order
    if candidate.get("id") != ident:
        raise ValueError("Initiative candidate does not match the monster")
    if len(order) != len(set(order)):
        raise ValueError("Battle order contains duplicate participants")
    items = [item for kind in ("monsters", "characters", "lairs")
             for item in state.get(kind, [])]
    by_id = {item["id"]: item for item in items}
    if len(by_id) != len(items) or any(key not in by_id for key in order):
        raise ValueError("Battle order contains ambiguous or missing participants")
    if not any(item["id"] == ident for item in state.get("monsters", [])):
        raise ValueError("Initiative target is not a monster")
    by_id[ident] = candidate
    return sorted(order, key=lambda participant_id: initiative_key(by_id[participant_id]))
