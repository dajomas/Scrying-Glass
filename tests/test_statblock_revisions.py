"""Ledger unit tests and separately pending production writer integration tests."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from python import scrying_glass_statblock_revisions as subject


class RevisionLedgerTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:', isolation_level=None); self.db.row_factory = sqlite3.Row
        self.addCleanup(self.db.close); self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript("""
            CREATE TABLE monsters(id INTEGER PRIMARY KEY);
            INSERT INTO monsters VALUES(1),(2);
            CREATE TABLE monster_statblocks(monster_id INTEGER UNIQUE REFERENCES monsters(id) ON DELETE CASCADE,revision INTEGER);
            CREATE TABLE monsters_attributes(id INTEGER PRIMARY KEY,parent_id INTEGER NOT NULL REFERENCES monsters(id) ON DELETE CASCADE,
                field_name TEXT NOT NULL,value_kind TEXT NOT NULL,text_value TEXT,integer_value INTEGER,real_value REAL,UNIQUE(parent_id,field_name));
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
        self.db.execute("UPDATE monsters_attributes SET value_kind='integer' WHERE parent_id=1")
        with self.assertRaises(ValueError): subject.revision_head(self.db, 1)
        reader = subject.StatblockRevisionMixin(); reader.connection = self.db
        with self.assertRaises(ValueError): reader._read_attributes('monsters', 1)


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


if __name__ == '__main__': unittest.main()
