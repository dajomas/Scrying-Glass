"""Trusted service-load metadata, deliberately outside serialized state fields."""
import copy
from .scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage, _policy
from .scrying_glass_statblock_state import prepare_private_state


class PrivateEncounterState(dict):
    """Internal dict-compatible state; JSON encoders see only ordinary fields.

    Deepcopy retains metadata. Explicit JSON/recovery/bundle serialization does
    not; those lifecycle contracts must be implemented separately before release.
    """
    def __init__(self, plain, snapshots):
        super().__init__(plain)
        self._statblocks = copy.deepcopy(snapshots)


def carry_private(source, normalized):
    """Retain validated metadata, including explicit absence, from trusted state."""
    plain = dict(normalized)
    if not isinstance(source, PrivateEncounterState):
        return plain
    snapshots = prepare_private_state(
        source._statblocks, {item['id'] for item in plain.get('monsters', [])}, _policy(None))
    return PrivateEncounterState(plain, snapshots)


def _attach(storage, encounter, plain):
    private = PrivateEncounterStorage(storage).load(encounter)
    snapshots = private.pop(PRIVATE_KEY)
    if private != plain:
        raise ValueError('Encounter changed during private-state load')
    return carry_private(PrivateEncounterState(plain, snapshots), plain)


def load_setup_private(storage, campaign, name):
    """Caller must authorize campaign first; never infer a campaign from a name."""
    from .scrying_glass_storage import SQLiteStorage
    if not isinstance(storage, SQLiteStorage):
        return storage.load_setup(campaign, name)
    with storage.transaction():
        plain = storage.load_setup(campaign, name)
        row = storage.connection.execute(
            'SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',
            (campaign, name)).fetchone()
        if row is None:
            raise FileNotFoundError(f'{campaign}/{name}')
        return _attach(storage, row[0], plain)


def load_runtime_private(storage):
    """Read the singleton runtime binding and content in one storage transaction."""
    from .scrying_glass_storage import SQLiteStorage
    if not isinstance(storage, SQLiteStorage):
        return storage.get_value('runtime_state')
    with storage.transaction():
        plain = storage.get_value('runtime_state')
        if plain is None:
            return None
        row = storage.connection.execute(
            'SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()
        if row is None or row[0] is None:
            raise ValueError('Runtime encounter binding is missing')
        return _attach(storage, row[0], plain)
