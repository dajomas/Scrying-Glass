"""Protected save-handler private persistence and destination metadata refresh."""
from .scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from .scrying_glass_statblock_loading import PrivateEncounterState
from .scrying_glass_statblock_recovery import prepare_capture
from .scrying_glass_statblock_save_as import save_new_setup


def save_setup_with_private(context, campaign, name):
    """Return saved destination metadata, or None for legacy storage.

    Caller authorizes the active campaign and owns the protected outer transaction,
    roster save, reference/last-setup updates and live metadata assignment. Existing
    private omission still rejects; this function supplies no clearing authority.
    """
    from .scrying_glass_storage import SQLiteStorage
    storage = context.STORAGE
    snapshot = context.setup_snapshot(context.STATE)
    if not isinstance(storage, SQLiteStorage):
        storage.save_setup(campaign, name, snapshot)
        return None
    if not storage.connection.in_transaction:
        raise RuntimeError('Private setup save requires a protected outer transaction')
    if str(campaign) != str(context.active_campaign()):
        raise ValueError('Private setup save belongs to another campaign')
    prepared = prepare_capture(snapshot)
    with storage.transaction():
        if not storage.setup_exists(campaign, name):
            return save_new_setup(storage, campaign, name, snapshot)
        reference = context.active_setup_reference()
        same_owner = reference is not None and str(reference['campaign_id']) == str(campaign) and reference['name'] == name
        if not same_owner:
            for value in prepared.values():
                value.pop('revision', None)
                value.pop('prepared_at', None)
        storage.save_setup(campaign, name, dict(snapshot))
        row = storage.connection.execute(
            'SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',
            (campaign, name)).fetchone()
        if row is None:
            raise ValueError('Saved setup binding is missing')
        api = PrivateEncounterStorage(storage)
        candidate = api.load(row[0])
        if isinstance(snapshot, PrivateEncounterState):
            candidate[PRIVATE_KEY] = prepared
        saved = api.save(row[0], candidate)
        return saved[PRIVATE_KEY]
