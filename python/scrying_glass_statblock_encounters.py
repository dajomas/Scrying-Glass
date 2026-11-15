"""Opt-in private encounter persistence; normal application wiring is a later increment."""
import copy
import json

PRIVATE_KEY = '_statblocks'


def public_payload(value):
    """Copy JSON-like payloads without reserved private state at any container depth."""
    if isinstance(value, dict):
        return {key: public_payload(item) for key, item in value.items() if key != PRIVATE_KEY}
    if isinstance(value, list):
        return [public_payload(item) for item in value]
    if isinstance(value, tuple):
        return tuple(public_payload(item) for item in value)
    return copy.deepcopy(value)


def _policy(limits):
    from .scrying_glass_statblock_model import ModelLimits
    if limits is not None:
        return limits
    # Internal stored-state round trips must survive lowered preparation limits.
    return ModelLimits(**{key: 2**63-1 for key in ModelLimits.__dataclass_fields__})


class PrivateEncounterStorage:
    """Trusted internal API; callers own authorization and import/preparation budgets.

    `_statblocks` maps monster combatant IDs to snapshots, never tracker values.
    Plain callbacks permit later storage hooks without recursive delegation.
    """
    def __init__(self, storage, *, save_plain=None, load_plain=None):
        from .scrying_glass_statblock_storage import StatblockStorage
        self.storage, self.db = storage, storage.connection
        self.snapshots = StatblockStorage(storage)
        self.save_plain = save_plain or storage._save_encounter
        self.load_plain = load_plain or storage._load_encounter

    def _rows(self, encounter):
        if type(encounter) is not int or not 0 < encounter < 2**63:
            raise ValueError('Invalid stored encounter ID')
        if self.db.execute('PRAGMA user_version').fetchone()[0] != 9:
            raise RuntimeError('Private encounters require schema 9')
        if not self.db.execute('SELECT 1 FROM encounters WHERE id=?', (encounter,)).fetchone():
            raise ValueError('Stored encounter not found')
        return {row['combatant_id']: row['id'] for row in self.db.execute(
            'SELECT id,combatant_id FROM monsters WHERE encounter_id=? ORDER BY position,id', (encounter,))}

    def _snapshots(self, rows):
        result = {}
        for ident, record in rows.items():
            value = self.snapshots.load(record)
            if value is not None:
                result[ident] = value
        return result

    def load(self, encounter):
        with self.storage.transaction():
            rows = self._rows(encounter)
            state = copy.deepcopy(self.load_plain(encounter))
            state[PRIVATE_KEY] = self._snapshots(rows)
            return state

    def save(self, encounter, state, *, runtime=False, limits=None):
        from .scrying_glass_statblock_model import canonical_bytes, content_digest, validate_snapshot
        if type(state) is not dict or type(state.get('monsters', [])) is not list:
            raise ValueError('Invalid encounter state')
        ids = []
        for item in state.get('monsters', []):
            if type(item) is not dict or type(item.get('id')) is not str or not item['id'].strip():
                raise ValueError('Invalid monster identity')
            ids.append(item['id'])
        if len(ids) != len(set(ids)):
            raise ValueError('Duplicate monster identity')
        policy = _policy(limits)
        explicit = PRIVATE_KEY in state
        requested = state.get(PRIVATE_KEY, {})
        if type(requested) is not dict or any(type(key) is not str or not key.strip() for key in requested):
            raise ValueError('Invalid private snapshot map')
        prepared = {}
        for ident, snapshot in requested.items():
            value = json.loads(canonical_bytes(snapshot, policy))
            value['content_digest'] = content_digest(value, policy)
            prepared[ident] = validate_snapshot(value, policy)
        plain = copy.deepcopy(state)
        plain.pop(PRIVATE_KEY, None)
        with self.storage.transaction():
            before_rows = self._rows(encounter)
            before = self._snapshots(before_rows)
            if set(prepared) - (set(ids) | set(before_rows)):
                raise ValueError('Snapshot target is outside this encounter')
            if explicit and (set(before) & set(ids)) - set(prepared):
                raise ValueError('Omitted existing snapshot; clearing requires a later explicit restore contract')
            desired = prepared if explicit else before
            self.save_plain(encounter, plain, runtime=runtime)
            after_rows = self._rows(encounter)
            if set(after_rows) != set(ids):
                raise ValueError('Monster identities changed during encounter save')
            for ident, record in after_rows.items():
                previous = before.get(ident)
                current = self.snapshots.load(record)
                if current is not None and (before_rows.get(ident) != record or current != previous):
                    raise ValueError('Snapshot ownership changed during encounter save')
                wanted = desired.get(ident)
                if wanted is None:
                    continue
                if current is not None and current['content_digest'] == wanted['content_digest']:
                    continue
                unchanged = previous is not None and previous['content_digest'] == wanted['content_digest']
                revision = previous['revision'] if unchanged else (previous['revision'] if previous else 0) + 1
                saved = self.snapshots.save(record, wanted, expected_revision=current['revision'] if current else 0, limits=policy)
                if saved['revision'] != revision:
                    saved['revision'] = revision
                    validate_snapshot(saved, policy)
                    self.db.execute('UPDATE monster_statblocks SET revision=? WHERE monster_id=?', (revision, record))
            self.storage._check_foreign_keys()
            return self.load(encounter)
