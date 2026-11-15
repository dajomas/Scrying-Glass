"""Trusted recovery replacement/clearing; ordinary save omission is not authority."""
import copy
from .scrying_glass_statblock_loading import PrivateEncounterState
from .scrying_glass_statblock_recovery import prepare_capture
from .scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage, _policy


def restore_bindings(storage, encounter, monster_ids=()):
    """Capture row IDs and highest revisions, including counter-only absence.

    These are internal comparison tokens, not historical content revisions.
    Header-only protocols remain usable for replacement, never trusted clearing.
    """
    with storage.transaction():
        api = PrivateEncounterStorage(storage)
        rows = api._rows(encounter); snapshots = api._snapshots(rows)
        read, _ = api._counter_protocol()
        heads = {ident: read(row) if read is not None else snapshots.get(ident, {}).get('revision', 0)
                 for ident, row in rows.items()}
        return {ident:(rows[ident], heads[ident]) if ident in rows else (None, 0)
                for ident in set(rows) | set(monster_ids)}


def _clear_survivors(storage, encounter, ids, prepared, bindings):
    """Caller holds the restoration transaction and has checked all bindings."""
    db = storage.connection
    read = getattr(storage, '_statblock_revision_head', None)
    allocate = getattr(storage, '_next_statblock_revision', None)
    record = getattr(storage, '_record_statblock_revision', None)
    plan = []
    for ident in sorted(set(ids) - set(prepared)):
        owner, head = bindings[ident]
        if owner is None:
            continue
        row = db.execute('SELECT encounter_id,combatant_id FROM monsters WHERE id=?', (owner,)).fetchone()
        if row is None or row['encounter_id'] != encounter or row['combatant_id'] != ident:
            raise ValueError('Stale clearing scope')
        header = db.execute('SELECT revision FROM monster_statblocks WHERE monster_id=?', (owner,)).fetchone()
        if header is None:
            continue
        if not all(callable(hook) for hook in (read, allocate, record)):
            raise ValueError('Trusted clearing requires durable revision counters')
        if read(owner) != head:
            raise ValueError('Stale clearing revision')
        revision = allocate(owner)
        if type(revision) is not int or not 0 < revision < 2**63 or revision != head + 1:
            raise ValueError('Invalid clearing revision')
        plan.append((owner, header[0], revision))
    for owner, previous, revision in plan:
        record(owner, revision)
        if read(owner) != revision:
            raise ValueError('Counter recording failed during clearing')
        deleted = db.execute('DELETE FROM monster_statblocks WHERE monster_id=? AND revision=?', (owner, previous))
        if deleted.rowcount != 1 or read(owner) != revision:
            raise ValueError('Stale clearing revision')


def restore_encounter(storage, encounter, state, *, expected_bindings, runtime=False):
    """Restore tracker/reference content and explicit absence atomically.

    Caller owns campaign/recovery authorization, global confirmation revision,
    character-roster persistence and live-state assignment. No HTTP route is added.
    Only the internal recovery carrier authorizes absence. Clear advances a durable
    counter before deleting content; later content cannot reuse its old revision.
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
    for value in prepared.values():
        value.pop('revision', None)
    candidate[PRIVATE_KEY] = prepared
    api = PrivateEncounterStorage(storage)
    with storage.transaction():
        current = restore_bindings(storage, encounter, ids)
        if current != expected_bindings:
            raise ValueError('Stale restoration bindings')
        _clear_survivors(storage, encounter, ids, prepared, current)
        return api.save(encounter, candidate, runtime=runtime, limits=_policy(None))
