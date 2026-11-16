"""Internal setup-import preparation; caller owns authorization and transaction."""
import copy
from .scrying_glass_statblock_loading import PrivateEncounterState
from .scrying_glass_statblock_model import ModelLimits
from .scrying_glass_statblock_recovery import prepare_capture
from .scrying_glass_statblock_state import prepare_private_state


def import_limits(context):
    """Read operator budgets, never request data; unrelated limit keys coexist."""
    config = getattr(context, 'CONFIG', {})
    if not isinstance(config, dict):
        raise ValueError('Invalid statblocks configuration')
    statblocks = config.get('statblocks', {})
    if not isinstance(statblocks, dict):
        raise ValueError('Invalid statblocks configuration')
    limits = statblocks.get('limits', {})
    if not isinstance(limits, dict):
        raise ValueError('Invalid statblocks limits configuration')
    return ModelLimits.from_mapping({key: limits[key]
        for key in ModelLimits.__dataclass_fields__ if key in limits})


def _identities(items):
    if not isinstance(items, list) or any(
        not isinstance(item, dict) or type(item.get('id')) is not str
        or not item['id'].strip() for item in items
    ):
        raise ValueError('Invalid setup-import combatant identities')
    ids = [item['id'] for item in items]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate setup-import combatant identity')
    return set(ids)


def _participants(state):
    if not isinstance(state, dict):
        raise ValueError('Invalid setup-import state')
    groups = [state.get(kind, []) for kind in ('monsters', 'characters', 'lairs')]
    for group in groups:
        _identities(group)
    return _identities([item for group in groups for item in group])


def prepare_setup_import(context, source, imported_monsters, id_map):
    """Merge only graphs selected by the handler's exact clone allocation map.

    No persistence or permission checks occur here. Trusted stored reads remain
    permissive; only incoming selected graphs face current preparation budgets.
    Existing destination metadata remains destination-owned. Fresh clone revision
    and time are assigned by the protected transaction-end private flush.
    """
    destination = context.STATE
    occupied = _participants(destination)
    source_ids = _participants(source)
    originals = _identities(source.get('monsters', []))
    clones = _identities(imported_monsters)
    if type(id_map) is not dict or any(
        type(key) is not str or not key.strip()
        or type(value) is not str or not value.strip()
        for key, value in id_map.items()
    ):
        raise ValueError('Invalid setup-import allocation map')
    if (set(id_map) - originals or set(id_map.values()) != clones
            or len(id_map) != len(clones) or clones & (occupied | source_ids)):
        raise ValueError('Invalid setup-import clone allocation')
    limits = import_limits(context)
    existing = prepare_capture(destination)
    captured = prepare_capture(source)
    incoming = {new: captured[old] for old, new in id_map.items() if old in captured}
    incoming = prepare_private_state(incoming, clones, limits)
    for value in incoming.values():
        value.pop('revision', None)
        value.pop('prepared_at', None)
    plain = copy.deepcopy(dict(destination))
    plain['monsters'] = [*plain.get('monsters', []), *copy.deepcopy(imported_monsters)]
    return PrivateEncounterState(plain, {**existing, **incoming})
