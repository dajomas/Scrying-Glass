import copy
import uuid
from typing import Any 

def combatant_state(combatant: dict[str, Any] | None) -> str:
    """Combatant state."""
    if combatant is None:
        return "unknown"

    life_state = combatant.get("life_state")
    if life_state in ("down", "stable", "dead"):
        return life_state

    return "alive" if combatant.get("alive", True) else "dead"

def update_alive_state(combatant: dict[str, Any]) -> None:
    """Update alive state."""
    combatant["alive"] = combatant.get("hp", 0) > 0

    if not combatant["alive"]:
        combatant["visible"] = True
        combatant["in_turn"] = False

def reset_entity(x: dict[str, Any]) -> None:
    """Restore reset values and remove the combatant from battle."""
    x["active"] = False
    x["visible"] = False
    x["in_turn"] = False
    x["initiative"] = x.get("original_initiative")

    if "monster_species" in x:
        x["hp"] = x["original_hp"]
        x["max_hp"] = x["original_hp"]
        x["show_ac"] = False
        x["show_hp"] = False
        x["show_initiative"] = False
    else:
        x["hp"] = x["max_hp"]

    x["temp_hp"] = 0
    x["death_successes"] = 0
    x["death_failures"] = 0
    x["life_state"] = "standing" if x["hp"] > 0 else "down"
    x["alive"] = x["hp"] > 0

def reset_imported_monster(source: dict[str, Any]) -> dict[str, Any]:
    """Reset imported monster."""
    item = copy.deepcopy(source)
    item['id'] = uuid.uuid4().hex

    # Keep the source setup's current HP and current Max HP.
    # Do not overwrite hp with original_hp during setup import.
    item['alive'] = item.get('hp', 0) > 0

    item['initiative'] = item.get('original_initiative')
    item['active'] = False
    item['visible'] = False
    item['in_turn'] = False
    item['show_ac'] = False
    item['show_hp'] = False
    item['show_initiative'] = False
    return item

def setup_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    """Setup snapshot."""
    snapshot = copy.deepcopy(state)
    snapshot["characters"] = []

    monster_ids = {
        monster["id"]
        for monster in snapshot["monsters"]
    }

    snapshot["battle_order"] = [
        combatant_id
        for combatant_id in snapshot["battle_order"]
        if combatant_id in monster_ids
    ]

    return snapshot

def admin_initiative_key(x: dict[str, Any]) -> tuple[int, int, str]:
    """Sort all integer initiatives before unset values, then by name."""
    value = x.get('initiative')
    is_numeric = isinstance(value, int) and not isinstance(value, bool)
    return (
        0 if is_numeric else 1,
        -value if is_numeric else 0,
        str(x.get('name', '')).casefold(),
    )

def admin_max_hp_key(x: dict[str, Any]) -> tuple[int, str]:
    """Admin max hp key."""
    return (-int(x.get('max_hp', 0)), str(x.get('name', '')).casefold())

def numeric_initiative(x: dict[str, Any]) -> int:
    """Numeric initiative."""
    v = x.get('initiative')
    return v if isinstance(v, int) and (not isinstance(v, bool)) else -999
