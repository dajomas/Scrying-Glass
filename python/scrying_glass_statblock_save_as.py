"""Internal new-destination Save As kernel; handler wiring is a later increment."""
import copy
from .scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from .scrying_glass_statblock_recovery import prepare_capture


def save_new_setup(storage, campaign, name, snapshot, *, updated_at=None):
    """Caller authorizes campaign/name and supplies the existing setup projection.

    Only trusted carrier attributes supply private snapshots. Existing destinations
    reject: ordinary saves and overwrite revision policy are separate contracts.
    Return freshly stored metadata for later caller-owned live-state refresh.
    """
    from .scrying_glass_storage import SQLiteStorage
    if not isinstance(storage, SQLiteStorage):
        raise TypeError('Private Save As requires native SQLite storage')
    if storage.connection.execute('PRAGMA user_version').fetchone()[0] != 9:
        raise RuntimeError('Private Save As requires schema 9')
    prepared = prepare_capture(snapshot)
    for value in prepared.values():
        value.pop('revision', None)
        value.pop('prepared_at', None)
    plain = copy.deepcopy(dict(snapshot))
    with storage.transaction():
        if storage.setup_exists(campaign, name):
            raise FileExistsError(f'{campaign}/{name}')
        storage.save_setup(campaign, name, plain, updated_at=updated_at)
        row = storage.connection.execute(
            'SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',
            (campaign, name)).fetchone()
        if row is None:
            raise ValueError('New setup binding is missing')
        api = PrivateEncounterStorage(storage)
        candidate = api.load(row[0]); candidate[PRIVATE_KEY] = prepared
        saved = api.save(row[0], candidate)
        storage._check_foreign_keys()
        return copy.deepcopy(saved[PRIVATE_KEY])
