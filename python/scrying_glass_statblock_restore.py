"""Trusted replacement-only recovery kernel; explicit clearing is not enabled yet."""
import copy
from .scrying_glass_statblock_loading import PrivateEncounterState
from .scrying_glass_statblock_recovery import prepare_capture
from .scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage, _policy


def restore_bindings(storage, encounter, monster_ids=()):
    """Capture exact encounter-local stored-row and content-revision descriptors."""
    with storage.transaction():
        api = PrivateEncounterStorage(storage)
        rows = api._rows(encounter); snapshots = api._snapshots(rows)
        return {ident:(rows[ident], snapshots.get(ident, {}).get('revision', 0)) if ident in rows else (None, 0)
                for ident in set(rows) | set(monster_ids)}


def restore_encounter(storage, encounter, state, *, expected_bindings, runtime=False):
    """Restore tracker/reference content atomically, rejecting unsupported clearing.

    Caller owns campaign/recovery authorization, global confirmation revision,
    character-roster persistence and live-state assignment. No HTTP route is added.
    Historical revisions never replace destination revisions. Removing a monster
    still cascades; clearing content on a surviving monster requires later work.
    """
    if not isinstance(state, PrivateEncounterState):
        raise ValueError('Restoration requires an internal private recovery image')
    prepared = prepare_capture(state)
    ids = [item['id'] for item in state.get('monsters', [])]
    if len(ids) != len(set(ids)) or any(not ident.strip() for ident in ids):
        raise ValueError('Invalid restoration monster identities')
    if type(expected_bindings) is not dict:
        raise ValueError('Expected restoration bindings must be a map')
    for ident, value in expected_bindings.items():
        if (type(ident) is not str or type(value) is not tuple or len(value) != 2
            or (value[0] is not None and (type(value[0]) is not int or not 0 < value[0] < 2**63))
            or type(value[1]) is not int or not 0 <= value[1] < 2**63):
            raise ValueError('Invalid expected restoration binding')
    candidate = copy.deepcopy(dict(state)); candidate['characters'] = []
    # Expected revisions below concern current bindings, not historical metadata.
    for value in prepared.values():
        value.pop('revision', None)
    candidate[PRIVATE_KEY] = prepared
    api = PrivateEncounterStorage(storage)
    with storage.transaction():
        current = restore_bindings(storage, encounter, ids)
        if current != expected_bindings:
            raise ValueError('Stale restoration bindings')
        needed = {ident for ident, binding in current.items() if ident in ids and binding[1] > 0}
        if needed - set(prepared):
            raise ValueError('Explicit statblock clearing is not enabled yet')
        return api.save(encounter, candidate, runtime=runtime, limits=_policy(None))
