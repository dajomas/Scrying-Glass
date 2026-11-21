"""Trusted loaded-setup detachment; no ordinary save/JSON replacement authority."""
import copy
from .scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from .scrying_glass_statblock_loading import PrivateEncounterState
from .scrying_glass_statblock_recovery import prepare_capture


def detach_loaded_setup(context):
    """Caller authorizes the move and owns its protected outer transaction.

    The moved setup keeps its encounter and history. The still-live battle gets
    fresh runtime ownership, never another encounter's revision/counter history.
    Plain state supplies no private content. Ordinary save/clear rules are unchanged.
    """
    from .scrying_glass_storage import SQLiteStorage
    storage = context.STORAGE
    if not isinstance(storage, SQLiteStorage):
        context.clear_active_setup()
        return
    db = storage.connection
    if not db.in_transaction:
        raise RuntimeError('Loaded setup detachment requires an outer transaction')
    reference = context.active_setup_reference()
    if reference is None or str(reference['campaign_id']) != str(context.active_campaign()):
        raise ValueError('Loaded setup detachment requires an active-campaign reference')
    prepared = prepare_capture(context.STATE)
    for value in prepared.values():
        value.pop('revision', None)
        value.pop('prepared_at', None)
    plain = copy.deepcopy(dict(context.STATE)); plain['active_setup'] = None
    candidate = copy.deepcopy(plain); candidate['characters'] = []; candidate[PRIVATE_KEY] = prepared
    with storage.transaction():
        row = db.execute('SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()
        if row is None:
            raise ValueError('Runtime singleton is missing')
        previous = row[0]
        if previous is not None and (
            db.execute('SELECT 1 FROM battle_setups WHERE encounter_id=?', (previous,)).fetchone()
            or db.execute('SELECT 1 FROM encounter_snapshots WHERE encounter_id=?', (previous,)).fetchone()
        ):
            raise ValueError('Runtime encounter has shared setup or recovery ownership')
        encounter = db.execute('INSERT INTO encounters DEFAULT VALUES').lastrowid
        saved = PrivateEncounterStorage(storage).save(encounter, candidate, runtime=True)
        db.execute('UPDATE application_state SET runtime_encounter_id=? WHERE id=1', (encounter,))
        if previous is not None:
            db.execute('DELETE FROM encounters WHERE id=?', (previous,))
        storage._check_foreign_keys()
        refreshed = PrivateEncounterState(plain, saved[PRIVATE_KEY])
    context.STATE = refreshed
