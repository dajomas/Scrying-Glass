"""2C.1 trusted private clone kernel; setup/Save As wiring is not enabled here."""
import copy
from .scrying_glass_statblock_encounters import PrivateEncounterStorage, _policy


def clone_private_snapshots(storage, source_encounter, destination_encounter):
    """Clone to already-created matching tracker rows with no private history.

    Caller authorizes both encounters and owns destination tracker creation.
    No ID remapping, plain tracker writes, source counter transfer or overwrite.
    Caller can wrap this transaction with tracker creation for an atomic copy.
    """
    if source_encounter == destination_encounter:
        raise ValueError('Private clone requires distinct encounters')
    with storage.transaction():
        api = PrivateEncounterStorage(storage)
        source = api._rows(source_encounter)
        destination = api._rows(destination_encounter)
        if set(source) != set(destination):
            raise ValueError('Private clone requires matching monster identities')
        read, record = api._counter_protocol()
        allocate = getattr(storage, '_next_statblock_revision', None)
        if not all(callable(hook) for hook in (read, record, allocate)):
            raise ValueError('Private clone requires durable revision counters')
        for owner in source.values():
            read(owner)
        if any(read(owner) != 0 for owner in destination.values()):
            raise ValueError('Private clone destination must have no private history')
        snapshots = api._snapshots(source)
        policy = _policy(None)
        for ident, value in snapshots.items():
            candidate = copy.deepcopy(value)
            candidate.pop('revision', None)
            candidate.pop('prepared_at', None)
            saved = api.snapshots.save(destination[ident], candidate, expected_revision=0, limits=policy)
            if saved['revision'] != 1 or read(destination[ident]) != 1:
                raise ValueError('Private clone must start at revision one')
        storage._check_foreign_keys()
        return api._snapshots(destination)
