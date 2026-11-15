"""Production SQLiteStorage startup/migration checks; no HTTP or browser claims."""
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch
from python.scrying_glass_storage import SQLiteStorage
from python import scrying_glass_statblock_storage as statblocks
from storage_migration_fixtures import pre_statblock_storage

TABLES = {'monster_statblocks', 'statblock_definitions', 'statblock_provenance',
          'statblock_credits', 'statblock_facts', 'statblock_nodes', 'statblock_warnings'}


class StatblockStartupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.path = self.directory / 'storage.sqlite3'

    def version(self, db):
        return db.execute('PRAGMA user_version').fetchone()[0]

    def legacy(self, path, version):
        with closing(pre_statblock_storage(SQLiteStorage, path)) as storage:
            c = storage.create_campaign('Legacy', '', 'before')
            storage.save_setup(c, 'fight', {'monsters': [{'id':'m', 'name':'Goblin', 'hp':7}]})
            expected = storage.load_setup(c, 'fight')
            db = storage.connection
            if version < 8:
                for table in ('characters', 'monsters', 'snapshot_characters'):
                    for column in ('mechanical_version', 'reduction_stat', 'reduction_amount'):
                        db.execute(f'ALTER TABLE {table}_effects DROP COLUMN {column}')
            if version < 7:
                db.execute('ALTER TABLE encounters DROP COLUMN has_lair')
            if version < 6:
                db.execute('DROP TABLE lairs')
            if version < 5:
                for table in ('characters_effects', 'monsters_effects', 'snapshot_characters_effects',
                              'snapshot_characters_attributes', 'snapshot_characters', 'encounter_snapshots', 'feature_state'):
                    db.execute('DROP TABLE ' + table)
            if version < 4:
                db.execute('DROP TABLE account_migration')
                db.execute('DROP TABLE users')
            db.execute(f'PRAGMA user_version={version}')
        return c, expected

    def test_fresh_schema_and_repeat_open(self):
        with closing(SQLiteStorage(self.path)) as storage:
            self.assertEqual(self.version(storage.connection), 9)
            self.assertIsNone(storage.migration_backup)
            tables = {r[0] for r in storage.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            self.assertTrue(TABLES.issubset(tables))
            storage._check_foreign_keys()
        with closing(SQLiteStorage(self.path)) as storage:
            self.assertEqual(self.version(storage.connection), 9)
            self.assertIsNone(storage.migration_backup)
        self.assertEqual(list(self.directory.glob('*.bak')), [])

    def test_supported_legacy_versions_and_single_original_backup(self):
        from test_sqlite_storage import old_database
        for version in range(1, 9):
            with self.subTest(version=version):
                path = self.directory / f'v{version}.sqlite3'
                if version in (1, 2):
                    snapshot, _ = old_database(path, version)
                    expected = snapshot['monsters']
                    campaign = None
                else:
                    campaign, snapshot = self.legacy(path, version)
                    expected = snapshot['monsters']
                with closing(SQLiteStorage(path)) as storage:
                    self.assertEqual(self.version(storage.connection), 9)
                    campaign = campaign or storage.get_value('active_campaign')
                    self.assertEqual(storage.load_setup(campaign, 'fight')['monsters'], expected)
                    self.assertEqual(storage.connection.execute('SELECT count(*) FROM monster_statblocks').fetchone()[0], 0)
                    storage._check_foreign_keys()
                    self.assertIsNotNone(storage.migration_backup)
                    with closing(sqlite3.connect(storage.migration_backup)) as backup:
                        self.assertEqual(self.version(backup), version)
                        self.assertIsNone(backup.execute("SELECT 1 FROM sqlite_master WHERE name='monster_statblocks'").fetchone())
                self.assertEqual(len(list(self.directory.glob(path.name + '.before-normalization*.bak'))), 1)
                with closing(SQLiteStorage(path)) as storage:
                    self.assertIsNone(storage.migration_backup)
                    self.assertEqual(self.version(storage.connection), 9)

    def test_v8_account_data_and_statblock_survive_reopen(self):
        campaign, expected = self.legacy(self.path, 8)
        with closing(pre_statblock_storage(SQLiteStorage, self.path)) as storage:
            storage.connection.execute("INSERT INTO users(username,role,password_hash) VALUES ('keeper','admin','hash')")
            before = list(storage.connection.iterdump())
        with closing(SQLiteStorage(self.path)) as storage:
            self.assertEqual(storage.load_setup(campaign, 'fight'), expected)
            self.assertEqual(tuple(storage.connection.execute('SELECT username,role,password_hash FROM users').fetchone()), ('keeper','admin','hash'))
            with closing(sqlite3.connect(storage.migration_backup)) as backup:
                self.assertEqual(list(backup.iterdump()), before)
            monster = storage.connection.execute("SELECT id FROM monsters WHERE combatant_id='m'").fetchone()[0]
            snapshot = dict(model_version=1, source_label='Source', subtitle='', completeness='available',
                definitions=[], facts=[], warnings=[], nodes=[],
                provenance=[dict(position=0, role='selected', provider='file', entity_id='fixture', adapter_version='1', credits=[])])
            saved = statblocks.StatblockStorage(storage).save(monster, snapshot, expected_revision=0)
            self.assertEqual(storage.load_setup(campaign, 'fight'), expected)
        with closing(SQLiteStorage(self.path)) as storage:
            self.assertIsNone(storage.migration_backup)
            self.assertEqual(statblocks.StatblockStorage(storage).load(monster), saved)
            self.assertEqual(storage.load_setup(campaign, 'fight'), expected)

    def test_existing_backup_is_not_overwritten(self):
        self.legacy(self.path, 8)
        occupied = self.path.with_name(self.path.name + '.before-normalization.bak')
        occupied.write_bytes(b'keep existing backup')
        with closing(SQLiteStorage(self.path)) as storage:
            self.assertNotEqual(storage.migration_backup, occupied)
            self.assertEqual(occupied.read_bytes(), b'keep existing backup')
            with closing(sqlite3.connect(storage.migration_backup)) as backup:
                self.assertEqual(self.version(backup), 8)

    def test_failed_ddl_rolls_back_and_constructor_closes(self):
        self.legacy(self.path, 8)
        with closing(sqlite3.connect(self.path)) as db:
            before = list(db.iterdump())
        original = statblocks.create_statblock_schema
        captured = []
        def broken(db):
            original(db)
            raise RuntimeError('injected schema failure')
        def close(storage):
            captured.append(storage.connection)
            storage.connection.close()
        with patch.object(statblocks, 'create_statblock_schema', side_effect=broken), patch.object(SQLiteStorage, 'close', autospec=True, side_effect=close):
            with self.assertRaisesRegex(RuntimeError, 'injected schema'):
                SQLiteStorage(self.path)
        self.assertEqual(len(captured), 1)
        with self.assertRaises(sqlite3.ProgrammingError):
            captured[0].execute('SELECT 1')
        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(self.version(db), 8)
            self.assertEqual(list(db.iterdump()), before)
            self.assertEqual(list(db.execute('PRAGMA foreign_key_check')), [])
        backup = self.path.with_name(self.path.name + '.before-normalization.bak')
        with closing(sqlite3.connect(backup)) as db:
            self.assertEqual(self.version(db), 8)
            self.assertEqual(list(db.iterdump()), before)
        with closing(SQLiteStorage(self.path)) as storage:
            self.assertEqual(self.version(storage.connection), 9)

    def test_backup_failure_does_not_start_migration(self):
        self.legacy(self.path, 8)
        with closing(sqlite3.connect(self.path)) as db:
            before = list(db.iterdump())
        with patch.object(SQLiteStorage, '_backup', side_effect=PermissionError('backup denied')):
            with self.assertRaises(PermissionError):
                SQLiteStorage(self.path)
        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(self.version(db), 8)
            self.assertEqual(list(db.iterdump()), before)

    def test_future_version_is_not_modified(self):
        with closing(sqlite3.connect(self.path)) as db:
            db.execute('PRAGMA user_version=10')
        with self.assertRaisesRegex(RuntimeError, 'Unsupported schema version'):
            SQLiteStorage(self.path)
        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(self.version(db), 10)
            self.assertIsNone(db.execute("SELECT 1 FROM sqlite_master WHERE name='monster_statblocks'").fetchone())
        self.assertEqual(list(self.directory.glob('*.bak')), [])


if __name__ == '__main__':
    unittest.main()
