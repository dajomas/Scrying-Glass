"""Production setup/runtime saves preserving encounter-local snapshots and counters.

Read projections stay unchanged. Ordinary save entry points reject private input;
copy/clear/restore semantics are separate trusted contracts.
"""
import copy
import time
import uuid
from .scrying_glass_storage_operations import StorageOperationsMixin


class StatblockOperationsMixin(StorageOperationsMixin):
    """Wrap public save boundaries, leaving the plain encounter callback nonrecursive."""

    def _save_preserving_statblocks(self, encounter, state, *, runtime=False):
        from .scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
        if not isinstance(state, dict) or PRIVATE_KEY in state:
            return self._save_encounter(encounter, state, runtime=runtime)
        version = self.connection.execute('PRAGMA user_version').fetchone()[0]
        if version != 9:
            return self._save_encounter(encounter, state, runtime=runtime)
        from .scrying_glass_statblock_revisions import REVISION_FIELD
        present = self.connection.execute(
            'SELECT 1 FROM monsters m WHERE m.encounter_id=? AND ('
            'EXISTS(SELECT 1 FROM monster_statblocks s WHERE s.monster_id=m.id) OR '
            'EXISTS(SELECT 1 FROM monsters_attributes a WHERE a.parent_id=m.id AND a.field_name=?)) LIMIT 1',
            (encounter, REVISION_FIELD)).fetchone()
        if present is None or not isinstance(state.get('monsters', []), list):
            return self._save_encounter(encounter, state, runtime=runtime)
        candidate = copy.deepcopy(dict(state))
        # The plain backend allocates missing IDs; do that once before the adapter
        # compares identities, without mutating the caller's legacy dictionaries.
        for item in candidate.get('monsters', []):
            if isinstance(item, dict) and 'id' not in item:
                item['id'] = uuid.uuid4().hex
        PrivateEncounterStorage(self, save_plain=self._save_encounter,
                                load_plain=self._load_encounter).save(
            encounter, candidate, runtime=runtime)

    def save_setup(self, campaign, name, snapshot, updated_at=None):
        with self.transaction():
            row = self.connection.execute(
                'SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',
                (campaign, name)).fetchone()
            if row:
                encounter = row[0]
            else:
                encounter = self.connection.execute('INSERT INTO encounters DEFAULT VALUES').lastrowid
                self.connection.execute(
                    'INSERT INTO battle_setups(campaign_id,name,encounter_id,updated_at) VALUES (?,?,?,?)',
                    (campaign, name, encounter, time.time() if updated_at is None else updated_at))
            self._save_preserving_statblocks(encounter, snapshot)
            self.connection.execute(
                'UPDATE battle_setups SET updated_at=? WHERE campaign_id=? AND name=?',
                (time.time() if updated_at is None else updated_at, campaign, name))

    def set_value(self, key, value):
        if key != 'runtime_state':
            return super().set_value(key, value)
        with self.transaction():
            encounter = self.connection.execute(
                'SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()[0]
            if encounter is None:
                encounter = self.connection.execute('INSERT INTO encounters DEFAULT VALUES').lastrowid
                self.connection.execute(
                    'UPDATE application_state SET runtime_encounter_id=? WHERE id=1', (encounter,))
            self._save_preserving_statblocks(encounter, value, runtime=True)
