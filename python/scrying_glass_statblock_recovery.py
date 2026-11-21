"""Trusted recovery capture/read helpers; restore/apply semantics belong to 2B."""
from .scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage, _policy
from .scrying_glass_statblock_loading import PrivateEncounterState
from .scrying_glass_statblock_state import prepare_private_state


def prepare_capture(state):
    """Validate private graphs before the capture transaction; never infer a source."""
    if not isinstance(state, dict):
        raise ValueError('Recovery state must be an object')
    if PRIVATE_KEY in state:
        raise ValueError('Recovery requires internal private metadata, not a serialized private field')
    if not isinstance(state, PrivateEncounterState):
        return {}
    monsters = state.get('monsters', [])
    if not isinstance(monsters, list) or any(
        not isinstance(item, dict) or not isinstance(item.get('id'), str) for item in monsters
    ):
        raise ValueError('Invalid recovery monster identities')
    return prepare_private_state(state._statblocks, {item['id'] for item in monsters}, _policy(None))


def write_capture(storage, encounter, prepared):
    """Attach independent typed records to a newly allocated recovery encounter.

    Caller holds a transaction. Historical revisions/times are captured exactly;
    restoring into a current encounter must apply its own revision policy later.
    """
    if not prepared:
        return
    api = PrivateEncounterStorage(storage)
    rows = api._rows(encounter)
    if set(prepared) - set(rows) or api._snapshots(rows):
        raise ValueError('Recovery capture target is not an empty matching encounter')
    policy = _policy(None)
    for ident, value in prepared.items():
        api._reattach(rows[ident], value, value.get('revision', 1), policy)
    storage._check_foreign_keys()


def read_capture(storage, encounter, plain):
    """Retain an explicit empty map too: a recovery image represents absence."""
    version = storage.connection.execute('PRAGMA user_version').fetchone()[0]
    if version < 9:
        return PrivateEncounterState(plain, {})
    loaded = PrivateEncounterStorage(storage).load(encounter)
    snapshots = loaded.pop(PRIVATE_KEY)
    if loaded != plain:
        raise ValueError('Recovery encounter changed during private read')
    return PrivateEncounterState(plain, snapshots)
