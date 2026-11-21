"""Fixture-helper isolation plus a real production-constructor compatibility check."""
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from python import scrying_glass_statblock_storage as statblocks
from storage_migration_fixtures import pre_statblock_storage


def minimal_storage(version=8, hybrid=False):
    db = sqlite3.connect(':memory:', isolation_level=None)
    db.execute(f'PRAGMA user_version={version}')
    if hybrid:
        db.execute('CREATE TABLE monster_statblocks(id INTEGER PRIMARY KEY)')
    return SimpleNamespace(connection=db, close=db.close)


class FixtureHelperTests(unittest.TestCase):
    def test_v8_gate_and_patch_restoration(self):
        original = statblocks.upgrade_statblocks
        called = []
        def future_factory(path):
            storage = minimal_storage()
            statblocks.upgrade_statblocks(storage)
            called.append(path)
            return storage
        with closing(pre_statblock_storage(future_factory, 'disposable')) as storage:
            self.assertEqual(storage.connection.execute('PRAGMA user_version').fetchone()[0], 8)
        self.assertEqual(called, ['disposable'])
        self.assertIs(statblocks.upgrade_statblocks, original)

    def test_constructor_failure_restores_patch(self):
        original = statblocks.upgrade_statblocks
        def fail(path):
            raise ValueError('constructor failure')
        with self.assertRaisesRegex(ValueError, 'constructor failure'):
            pre_statblock_storage(fail, 'disposable')
        self.assertIs(statblocks.upgrade_statblocks, original)

    def test_wrong_version_is_rejected_and_closed(self):
        for version in (7, 9):
            with self.subTest(version=version):
                storage = minimal_storage(version)
                with self.assertRaisesRegex(RuntimeError, 'schema-8'):
                    pre_statblock_storage(lambda path: storage, 'disposable')
                with self.assertRaises(sqlite3.ProgrammingError):
                    storage.connection.execute('SELECT 1')

    def test_hybrid_schema_is_rejected_and_closed(self):
        storage = minimal_storage(hybrid=True)
        with self.assertRaisesRegex(RuntimeError, 'Statblock tables'):
            pre_statblock_storage(lambda path: storage, 'disposable')
        with self.assertRaises(sqlite3.ProgrammingError):
            storage.connection.execute('SELECT 1')


class ProductionFixtureTests(unittest.TestCase):
    def test_real_constructor_builds_pre_statblock_fixture(self):
        from python.scrying_glass_storage import SQLiteStorage
        original = statblocks.upgrade_statblocks
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'legacy.sqlite3'
            with closing(pre_statblock_storage(SQLiteStorage, path)) as storage:
                self.assertEqual(storage.connection.execute('PRAGMA user_version').fetchone()[0], 8)
                tables = {row[0] for row in storage.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                self.assertTrue({'users', 'account_migration', 'feature_state', 'lairs', 'monsters'}.issubset(tables))
                self.assertNotIn('monster_statblocks', tables)
                self.assertIn('has_lair', {row[1] for row in storage.connection.execute('PRAGMA table_info(encounters)')})
                self.assertIsNone(storage.migration_backup)
                storage._check_foreign_keys()
        self.assertIs(statblocks.upgrade_statblocks, original)


if __name__ == '__main__':
    unittest.main()
