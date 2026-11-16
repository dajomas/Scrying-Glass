"""Constrained SQLite ledger tests; production writer/rebuild validation is separate."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from python import scrying_glass_statblock_revisions as subject
from python import scrying_glass_statblock_encounters as adapter


class RevisionLedgerTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:', isolation_level=None); self.db.row_factory = sqlite3.Row
        self.addCleanup(self.db.close); self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript("""
            CREATE TABLE monsters(id INTEGER PRIMARY KEY);
            INSERT INTO monsters VALUES(1),(2);
            CREATE TABLE monster_statblocks(monster_id INTEGER UNIQUE REFERENCES monsters(id) ON DELETE CASCADE,revision INTEGER);
            CREATE TABLE monsters_attributes(id INTEGER PRIMARY KEY,parent_id INTEGER NOT NULL REFERENCES monsters(id) ON DELETE CASCADE,
                field_name TEXT NOT NULL,value_kind TEXT NOT NULL CHECK(value_kind IN ('null','text','integer','real','boolean','present')),
                text_value TEXT,integer_value INTEGER,real_value REAL,UNIQUE(parent_id,field_name));
        """)

    def test_legacy_header_bootstraps_counter(self):
        self.assertEqual(subject.revision_head(self.db, 1), 0)
        self.db.execute('INSERT INTO monster_statblocks VALUES(1,7)')
        self.assertEqual(subject.next_revision(self.db, 1), 8)
        subject.record_revision(self.db, 1, 7)
        self.assertEqual(subject.revision_head(self.db, 1), 7)

    def test_counter_survives_header_absence(self):
        self.db.execute('INSERT INTO monster_statblocks VALUES(1,5)'); subject.record_revision(self.db, 1, 5)
        self.db.execute('DELETE FROM monster_statblocks WHERE monster_id=1')
        self.assertEqual(subject.next_revision(self.db, 1), 6)
        subject.record_revision(self.db, 1, 6)
        self.assertEqual(subject.revision_head(self.db, 1), 6)

    def test_decrease_and_invalid_integers_are_rejected(self):
        subject.record_revision(self.db, 1, 5)
        for value in (True, False, 0, -1, 4, '6', subject.MAX_REVISION+1):
            with self.assertRaises(ValueError): subject.record_revision(self.db, 1, value)
        with self.assertRaises(ValueError): subject.revision_head(self.db, True)
        self.assertEqual(subject.revision_head(self.db, 1), 5)

    def test_overflow_fails_without_wrapping(self):
        subject.record_revision(self.db, 1, subject.MAX_REVISION)
        with self.assertRaises(ValueError): subject.next_revision(self.db, 1)
        self.assertEqual(subject.revision_head(self.db, 1), subject.MAX_REVISION)

    def test_ledger_rolls_back_with_transaction(self):
        subject.record_revision(self.db, 1, 1); self.db.execute('BEGIN')
        subject.record_revision(self.db, 1, 2); self.db.execute('ROLLBACK')
        self.assertEqual(subject.revision_head(self.db, 1), 1)

    def test_ownership_and_delete_cascade(self):
        subject.record_revision(self.db, 1, 3); subject.record_revision(self.db, 2, 9)
        self.db.execute('DELETE FROM monsters WHERE id=1')
        self.assertEqual(subject.revision_head(self.db, 1), 0)
        self.assertEqual(subject.revision_head(self.db, 2), 9)
        with self.assertRaises(sqlite3.IntegrityError): subject.record_revision(self.db, 999, 1)
        self.assertEqual(list(self.db.execute('PRAGMA foreign_key_check')), [])

    def test_private_counter_is_not_decoded_as_tracker_attribute(self):
        subject.record_revision(self.db, 1, 3)
        self.db.execute("INSERT INTO monsters_attributes(parent_id,field_name,value_kind,text_value) VALUES(1,'note','text','keep')")
        reader = subject.StatblockRevisionMixin(); reader.connection = self.db
        self.assertEqual(reader._read_attributes('monsters', 1), ({'note':'keep'}, set()))
        with self.assertRaises(ValueError): reader._attributes('monsters', 1, {subject.REVISION_FIELD:99})
        with self.assertRaises(ValueError): reader._attributes('monsters', 1, {}, present=[subject.REVISION_FIELD])

    def test_counter_collision_or_corruption_fails_closed(self):
        subject.record_revision(self.db, 1, 3)
        self.db.execute('UPDATE monsters_attributes SET text_value=NULL WHERE parent_id=1')
        with self.assertRaises(ValueError): subject.revision_head(self.db, 1)
        reader = subject.StatblockRevisionMixin(); reader.connection = self.db
        with self.assertRaises(ValueError): reader._read_attributes('monsters', 1)

    def counter_adapter(self):
        storage = subject.StatblockRevisionMixin(); storage.connection = self.db
        api = object.__new__(adapter.PrivateEncounterStorage); api.storage = storage
        return api

    def test_encoding_matches_production_kind_constraint(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute('INSERT INTO monsters_attributes(parent_id,field_name,value_kind,integer_value) VALUES(?,?,?,1)',
                            (1, subject.REVISION_FIELD, subject.REVISION_KIND))
        subject.record_revision(self.db, 1, 7)
        row = self.db.execute('SELECT * FROM monsters_attributes WHERE parent_id=1').fetchone()
        self.assertEqual((row['value_kind'], row['text_value'], row['integer_value']), ('integer', subject.REVISION_KIND, 7))

    def test_counter_rebinding_and_ownership_guards(self):
        api = self.counter_adapter(); subject.record_revision(self.db, 1, 7)
        self.db.execute('DELETE FROM monsters WHERE id=1'); self.db.execute('INSERT INTO monsters VALUES(3)')
        api._rebind_counter(3, 1, 7)
        self.assertEqual(subject.next_revision(self.db, 3), 8)
        with self.assertRaises(ValueError): api._rebind_counter(3, 3, 8)
        subject.record_revision(self.db, 2, 9)
        with self.assertRaises(ValueError): api._rebind_counter(2, 1, 7)
        self.assertEqual(subject.revision_head(self.db, 2), 9)
        api.storage = type('Partial', (), {'_record_statblock_revision':lambda *args: None})()
        with self.assertRaises(RuntimeError): api._counter_protocol()

    def test_rebound_counter_and_deleted_owner_rollback_together(self):
        api = self.counter_adapter(); subject.record_revision(self.db, 1, 7)
        self.db.execute('BEGIN')
        try:
            self.db.execute('DELETE FROM monsters WHERE id=1'); self.db.execute('INSERT INTO monsters VALUES(3)')
            api._rebind_counter(3, 1, 7)
            self.assertEqual(subject.revision_head(self.db, 3), 7)
        finally: self.db.execute('ROLLBACK')
        self.assertEqual(subject.revision_head(self.db, 1), 7)
        self.assertIsNone(self.db.execute('SELECT id FROM monsters WHERE id=3').fetchone())


class ProductionRevisionTests(unittest.TestCase):
    def setUp(self):
        from python.scrying_glass_storage import SQLiteStorage
        from python.scrying_glass_statblock_storage import StatblockStorage
        from test_statblock_storage import sample
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)/'state.sqlite3'; self.storage = SQLiteStorage(self.path)
        self.addCleanup(self.storage.close); self.api = StatblockStorage(self.storage); self.sample = sample
        self.campaign = self.storage.create_campaign('Revision tests', '', 'now')
        self.storage.save_setup(self.campaign, 'one', {'monsters':[{'id':'m','hp':12}]})
        self.monster = self.storage.connection.execute('SELECT id FROM monsters').fetchone()[0]

    def saved(self):
        return self.api.save(self.monster, self.sample(), expected_revision=0)

    def test_legacy_snapshot_bootstraps_on_next_replacement(self):
        original = self.saved()
        with self.storage.transaction():
            self.storage.connection.execute('DELETE FROM monsters_attributes WHERE field_name=?', (subject.REVISION_FIELD,))
        value = self.api.save(self.monster, original, expected_revision=original['revision'])
        self.assertEqual(value['revision'], original['revision']+1)
        self.assertEqual(subject.revision_head(self.storage.connection, self.monster), value['revision'])

    def test_absent_header_counter_survives_tracker_save_and_stays_private(self):
        original = self.saved()
        with self.storage.transaction(): self.storage.connection.execute('DELETE FROM monster_statblocks WHERE monster_id=?', (self.monster,))
        self.storage.save_setup(self.campaign, 'one', {'monsters':[{'id':'m','hp':9}]})
        plain = self.storage.load_setup(self.campaign, 'one')
        self.assertNotIn(subject.REVISION_FIELD, json.dumps(plain))
        value = self.api.save(self.monster, self.sample(), expected_revision=0)
        self.assertEqual(value['revision'], original['revision']+1)
        self.assertEqual(plain['monsters'][0]['hp'], 9)

    def test_ordinary_input_cannot_supply_counter(self):
        original = self.saved()
        with self.assertRaises(ValueError):
            self.storage.save_setup(self.campaign, 'one', {'monsters':[{'id':'m','hp':1,subject.REVISION_FIELD:99}]})
        self.assertEqual(self.api.load(self.monster), original)
        self.assertEqual(self.storage.load_setup(self.campaign, 'one')['monsters'][0]['hp'], 12)

    def test_failed_write_and_outer_rollback_restore_counter_and_header(self):
        original = self.saved()
        with patch('python.scrying_glass_statblock_storage._insert', side_effect=OSError('injected')):
            with self.assertRaises(OSError): self.api.save(self.monster, self.sample(), expected_revision=1)
        with self.assertRaises(OSError):
            with self.storage.transaction():
                self.api.save(self.monster, self.sample(), expected_revision=1)
                raise OSError('outer')
        self.assertEqual(self.api.load(self.monster), original)
        self.assertEqual(subject.revision_head(self.storage.connection, self.monster), 1)
        self.assertFalse(self.storage.connection.in_transaction)

    def test_counter_survives_reopen_without_header(self):
        from python.scrying_glass_statblock_storage import StatblockStorage
        self.saved()
        with self.storage.transaction(): self.storage.connection.execute('DELETE FROM monster_statblocks WHERE monster_id=?', (self.monster,))
        self.storage.close(); self.storage = self.storage.__class__(self.path); self.addCleanup(self.storage.close)
        self.api = StatblockStorage(self.storage)
        self.assertEqual(self.api.save(self.monster, self.sample(), expected_revision=0)['revision'], 2)
        self.assertEqual(self.storage.connection.execute('PRAGMA user_version').fetchone()[0], 9)

    def encounter_api(self):
        encounter = self.storage.connection.execute('SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?', (self.campaign, 'one')).fetchone()[0]
        return encounter, adapter.PrivateEncounterStorage(self.storage)

    def counter_only(self):
        self.saved()
        with self.storage.transaction():
            self.storage.connection.execute('DELETE FROM monster_statblocks WHERE monster_id=?', (self.monster,))

    def rebuild(self, table, owner_name, owner, items):
        if table == 'monsters': self.storage.connection.execute('DELETE FROM monsters WHERE encounter_id=?', (owner,))
        return self.original_entities(table, owner_name, owner, items)

    def test_setup_counter_only_rebuild_reopen_and_next_revision(self):
        from python.scrying_glass_statblock_storage import StatblockStorage
        self.counter_only(); old = self.monster; encounter, api = self.encounter_api()
        self.original_entities = self.storage._save_entities
        with patch.object(self.storage, '_save_entities', side_effect=self.rebuild):
            self.storage.save_setup(self.campaign, 'one', {'monsters':[{'id':'m','hp':4}]})
        self.monster = api._rows(encounter)['m']; self.assertNotEqual(self.monster, old)
        self.assertEqual(subject.revision_head(self.storage.connection, self.monster), 1)
        loaded = api.load(encounter); self.assertEqual(loaded[adapter.PRIVATE_KEY], {})
        self.assertEqual(loaded['monsters'][0]['hp'], 4)
        self.assertNotIn(subject.REVISION_FIELD, json.dumps(loaded))
        self.storage.close(); self.storage = self.storage.__class__(self.path); self.addCleanup(self.storage.close)
        self.api = StatblockStorage(self.storage)
        self.assertEqual(self.api.save(self.monster, self.sample(), expected_revision=0)['revision'], 2)

    def test_runtime_counter_only_rebuild_is_separate_from_setup(self):
        self.counter_only(); self.storage.set_value('runtime_state', {'monsters':[{'id':'m','hp':30}]})
        db = self.storage.connection
        encounter = db.execute('SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()[0]
        runtime = adapter.PrivateEncounterStorage(self.storage)
        subject.record_revision(db, runtime._rows(encounter)['m'], 9)
        self.original_entities = self.storage._save_entities
        with patch.object(self.storage, '_save_entities', side_effect=self.rebuild):
            self.storage.set_value('runtime_state', {'monsters':[{'id':'m','hp':20}]})
        row = runtime._rows(encounter)['m']
        self.assertEqual(subject.revision_head(db, row), 9)
        self.assertEqual(subject.revision_head(db, self.monster), 1)
        self.assertEqual(self.api.save(row, self.sample(), expected_revision=0)['revision'], 10)
        self.assertIsNone(self.api.load(self.monster))

    def test_reattached_snapshot_preserves_then_advances_counter_once(self):
        self.saved(); encounter, api = self.encounter_api(); before = api.load(encounter)
        self.original_entities = self.storage._save_entities
        with patch.object(self.storage, '_save_entities', side_effect=self.rebuild):
            unchanged = api.save(encounter, before)
            self.assertEqual(unchanged[adapter.PRIVATE_KEY], before[adapter.PRIVATE_KEY])
            unchanged[adapter.PRIVATE_KEY]['m'].pop('content_digest', None)
            unchanged[adapter.PRIVATE_KEY]['m']['source_label'] = 'Changed'
            changed = api.save(encounter, unchanged)
        row = api._rows(encounter)['m']
        self.assertEqual(changed[adapter.PRIVATE_KEY]['m']['revision'], 2)
        self.assertEqual(subject.revision_head(self.storage.connection, row), 2)
        self.assertEqual(self.api.save(row, self.sample(), expected_revision=2)['revision'], 3)
        self.assertEqual(changed[adapter.PRIVATE_KEY]['m']['source_label'], 'Changed')
        self.assertNotEqual(changed[adapter.PRIVATE_KEY]['m']['content_digest'],
                            before[adapter.PRIVATE_KEY]['m']['content_digest'])

    def test_stale_content_digest_rejects_without_changing_tracker_or_counter(self):
        self.saved(); encounter, api = self.encounter_api()
        state = api.load(encounter)
        state['monsters'][0]['hp'] = 1
        state[adapter.PRIVATE_KEY]['m']['source_label'] = 'Changed with stale digest'
        before = list(self.storage.connection.iterdump())
        with self.assertRaisesRegex(ValueError, 'digest_mismatch'):
            api.save(encounter, state)
        self.assertEqual(list(self.storage.connection.iterdump()), before)
        self.assertEqual(subject.revision_head(self.storage.connection, self.monster), 1)
        self.assertEqual(self.api.load(self.monster)['revision'], 1)
        self.assertEqual(self.storage.load_setup(self.campaign, 'one')['monsters'][0]['hp'], 12)
        self.assertFalse(self.storage.connection.in_transaction)

    def test_late_rebuild_failure_rolls_back_counter_and_tracker(self):
        self.counter_only(); before = self.storage.load_setup(self.campaign, 'one')
        self.original_entities = self.storage._save_entities
        with patch.object(self.storage, '_save_entities', side_effect=self.rebuild), patch.object(adapter.PrivateEncounterStorage, 'load', side_effect=OSError('late refresh')):
            with self.assertRaises(OSError):
                self.storage.save_setup(self.campaign, 'one', {'monsters':[{'id':'m','hp':1}]})
        self.assertEqual(self.storage.load_setup(self.campaign, 'one'), before)
        self.assertEqual(subject.revision_head(self.storage.connection, self.monster), 1)
        self.storage._check_foreign_keys()

    def test_callback_counter_mutation_is_rejected_atomically(self):
        self.counter_only(); original = self.storage._save_encounter
        def mutate(encounter, state, *, runtime=False):
            original(encounter, state, runtime=runtime)
            subject.record_revision(self.storage.connection, self.monster, 2)
        with patch.object(self.storage, '_save_encounter', side_effect=mutate):
            with self.assertRaises(ValueError):
                self.storage.save_setup(self.campaign, 'one', {'monsters':[{'id':'m','hp':1}]})
        self.assertEqual(subject.revision_head(self.storage.connection, self.monster), 1)
        self.assertEqual(self.storage.load_setup(self.campaign, 'one')['monsters'][0]['hp'], 12)

    def test_deleted_counter_does_not_attach_to_new_identity(self):
        self.counter_only(); self.storage.save_setup(self.campaign, 'one', {'monsters':[]})
        self.assertEqual(self.storage.connection.execute('SELECT count(*) FROM monsters_attributes WHERE field_name=?', (subject.REVISION_FIELD,)).fetchone()[0], 0)
        self.storage.save_setup(self.campaign, 'one', {'monsters':[{'id':'fresh','hp':5}]})
        encounter, api = self.encounter_api(); row = api._rows(encounter)['fresh']
        self.assertEqual(subject.revision_head(self.storage.connection, row), 0)
        self.assertEqual(self.api.save(row, self.sample(), expected_revision=0)['revision'], 1)


if __name__ == '__main__': unittest.main()
