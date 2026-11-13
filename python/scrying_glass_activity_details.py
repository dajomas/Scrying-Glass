"""SG-TODO-019: readable Activity log details naming the affected unit and result.

Formatting only: callers pass snapshots taken around an operation they already
performed. Nothing here mutates combatants or re-applies an operation.
"""
from .scrying_glass_statistics import STATS, LABELS

HP_FIELDS = ('hp', 'temp_hp', 'max_hp', 'life_state', 'death_failures')


def unit_name(item):
    """Return the affected unit's display name (encounter-level when absent)."""
    name = (item or {}).get('name')
    return name if isinstance(name, str) and name.strip() else 'Encounter'


def snapshot(item, fields=HP_FIELDS):
    """Copy only the plain values needed for a before/after description."""
    return {field: (item or {}).get(field) for field in fields}


def _number(value, default=0):
    return default if value is None else value


def hp_changes(before, after):
    """Describe HP-related changes; HP is always reported with the new maximum."""
    parts = [f"HP {before.get('hp')} → {after.get('hp')}/{after.get('max_hp')}"]
    old_temp = _number(before.get('temp_hp'))
    new_temp = _number(after.get('temp_hp'))
    if old_temp != new_temp:
        parts.append(f'temporary HP {old_temp} → {new_temp}')
    if before.get('life_state') and after.get('life_state') and before['life_state'] != after['life_state']:
        parts.append(f"life state {before['life_state']} → {after['life_state']}")
    return parts


def hp_note(item, before, after=None):
    """`Name: HP old → new/max[; temporary HP …][; life state …]`."""
    after = snapshot(item) if after is None else after
    return f'{unit_name(item)}: ' + '; '.join(hp_changes(before, after))


def statistic_changes(before, after):
    """Describe effective statistic changes in STATS order, plus clamped HP."""
    parts = []
    for stat in STATS:
        if before.get(stat) != after.get(stat):
            parts.append(f'{LABELS[stat]} {before.get(stat)} → {after.get(stat)}')
    if before.get('hp') != after.get('hp'):
        parts.append(f"HP {before.get('hp')} → {after.get('hp')}")
    return parts


def statistics_snapshot(item):
    return snapshot(item, STATS + ('hp',))


def statistics_note(item, before, after=None, prefix=None):
    """`Name: STR 14 → 12[; …]`, optionally preceded by a context prefix."""
    after = statistics_snapshot(item) if after is None else after
    changes = statistic_changes(before, after) or ['no effective statistic changed']
    text = f'{unit_name(item)}: ' + '; '.join(changes)
    return f'{prefix}; {text}' if prefix else text


def death_failure_note(item, reason):
    """`Name: death-save failures now N/3; reason`."""
    return f"{unit_name(item)}: death-save failures now {_number(item.get('death_failures'))}/3; {reason}"
