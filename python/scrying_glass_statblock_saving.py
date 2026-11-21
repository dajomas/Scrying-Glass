"""Transaction-end private writes; no JSON clearing, copy or import authority."""
import copy
from .scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from .scrying_glass_statblock_loading import PrivateEncounterState
from .scrying_glass_statblock_changes import prune_private
from .scrying_glass_statblock_recovery import prepare_capture


def flush_private_state(context):
    """Caller owns authorization, preparation limits and the outer transaction.

    Ordinary saves have already persisted tracker rows. Reuse those exact rows
    without invoking tracker writers again; publish metadata only after success.
    """
    from .scrying_glass_storage import SQLiteStorage
    storage = context.STORAGE
    if not isinstance(storage, SQLiteStorage):
        return
    if not storage.connection.in_transaction:
        raise RuntimeError('Private flush requires an outer transaction')
    source = copy.deepcopy(context.STATE)
    prune_private(source)
    prepared = prepare_capture(source)
    reference = context.active_setup_reference()
    if source.get('active_setup') is not None and reference is None:
        raise ValueError('Invalid private save setup reference')
    with storage.transaction():
        if reference is not None:
            if str(reference['campaign_id']) != str(context.active_campaign()):
                raise ValueError('Private save setup belongs to another campaign')
            row = storage.connection.execute(
                'SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',
                (reference['campaign_id'], reference['name'])).fetchone()
        else:
            row = storage.connection.execute(
                'SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()
        if row is None or row[0] is None:
            raise ValueError('Private save encounter binding is missing')
        encounter = row[0]
        api = PrivateEncounterStorage(storage, save_plain=lambda *args, **kwargs: None)
        candidate = api.load(encounter)
        if {item['id'] for item in candidate.get('monsters', [])} != {item['id'] for item in source.get('monsters', [])}:
            raise ValueError('Private save monster bindings changed')
        if isinstance(source, PrivateEncounterState):
            candidate[PRIVATE_KEY] = prepared
        saved = api.save(encounter, candidate, runtime=reference is None)
        refreshed = PrivateEncounterState(context.STATE, saved[PRIVATE_KEY])
    context.STATE = refreshed
