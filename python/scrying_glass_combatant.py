import copy
import uuid
from typing import Any 

def combatant_state(combatant: dict[str, Any] | None) -> str:
    """Combatant state."""
    if combatant is None:
        return "unknown"

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

def admin_initiative_key(x: dict[str, Any]) -> tuple[int, str]:
    """Admin initiative key."""
    value = x.get('initiative')
    initiative = value if isinstance(value, int) and (not isinstance(value, bool)) else -999
    return (-initiative, str(x.get('name', '')).casefold())

def admin_max_hp_key(x: dict[str, Any]) -> tuple[int, str]:
    """Admin max hp key."""
    return (-int(x.get('max_hp', 0)), str(x.get('name', '')).casefold())

def numeric_initiative(x: dict[str, Any]) -> int:
    """Numeric initiative."""
    v = x.get('initiative')
    return v if isinstance(v, int) and (not isinstance(v, bool)) else -999
