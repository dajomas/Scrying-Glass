"""Shared field definitions staged for the Storage split; runtime not yet wired.

Keep the tuple order, scalar types and explicit presence semantics unchanged.
The original scrying_glass_storage module remains authoritative until activation.
"""

TEXT_FIELDS = ("name", "color", "monster_species", "image_url")
INT_FIELDS = ("ac", "hp", "max_hp", "original_hp", "initiative", "original_initiative")
BOOL_FIELDS = ("alive", "active", "visible", "in_turn", "ally", "show_ac", "show_hp", "show_initiative")
ENTITY_FIELDS = TEXT_FIELDS + INT_FIELDS + BOOL_FIELDS
LOG_FIELDS = ("timestamp", "active_combatant_id", "active_combatant", "active_combatant_state", "target_combatant_id", "target_combatant", "target_combatant_state", "action", "amount")
LIST_FIELDS = ("battle_order", "turn_successors", "turn_successors_before_wrap")
STATE_FIELDS = set(LIST_FIELDS) | {"monsters", "characters", "activity_log", "display", "active_setup", "active_turn_id", "battle_round", "lairs", "has_lair"}
