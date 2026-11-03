"""Unused operations mixin: parity fixtures, not full constructor/v8 integration."""
import ast
import copy
import hashlib
import inspect
from pathlib import Path
import sqlite3
import unittest
from unittest.mock import patch
from python.scrying_glass_storage import SQLiteStorage
from python.scrying_glass_storage_operations import StorageOperationsMixin

ROOT = Path(__file__).resolve().parents[1]
METHODS = ('create_campaign', '_campaign_metadata', 'read_campaigns', 'write_campaigns',
           'update_campaign', 'campaign_exists', 'campaign_name_exists', 'load_characters',
           'save_characters', 'list_setups', 'setup_exists', 'load_setup', 'save_setup',
           'rename_setup', 'delete_setup', 'unique_setup_name', 'transfer_setup',
           'newest_setup', 'get_value', 'set_value')


class StagedStorage(StorageOperationsMixin, SQLiteStorage):
    pass


class StorageOperationsPreparationTests(unittest.TestCase):
    def storage(self, kind):
        s = object.__new__(kind)
        s.connection = sqlite3.connect(':memory:', isolation_level=None)
        s.connection.row_factory = sqlite3.Row
        self.addCleanup(s.connection.close)
        s.connection.execute('PRAGMA foreign_keys=ON')
        s._create_schema()
        s.connection.execute('PRAGMA user_version=3')
        # Actual encounter_snapshots DDL from upgrade_features; not the full v5 upgrade.
        s.connection.execute("CREATE TABLE encounter_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE, encounter_id INTEGER NOT NULL UNIQUE REFERENCES encounters(id), kind TEXT NOT NULL CHECK(kind IN ('undo','checkpoint')), name TEXT NOT NULL, created REAL NOT NULL, setup_name TEXT, after_digest TEXT)")
        a = s.create_campaign('Alpha', 'first', 'now', metadata={'flag': True})
        b = s.create_campaign('Beta', '', 'now')
        return s, a, b

    def test_ast_signatures_dependencies_and_original_identity(self):
        def methods(path, name):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
            return tree, {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
        tree, staged = methods(ROOT/'python/scrying_glass_storage_operations.py', 'StorageOperationsMixin')
        _, original = methods(ROOT/'python/scrying_glass_storage.py', 'SQLiteStorage')
        self.assertEqual(set(staged), set(METHODS))
        for name in METHODS:
            self.assertEqual(ast.dump(staged[name], include_attributes=False), ast.dump(original[name], include_attributes=False), name)
            self.assertEqual(inspect.signature(getattr(StorageOperationsMixin, name)), inspect.signature(getattr(SQLiteStorage, name)))
        self.assertEqual([n.module for n in tree.body if isinstance(n, ast.ImportFrom)], ['scrying_glass_identity_rules'])
        self.assertEqual([a.name for n in tree.body if isinstance(n, ast.Import) for a in n.names], ['time'])
        self.assertLessEqual((ROOT/'python/scrying_glass_storage_operations.py').stat().st_size, 20000)
        data = (ROOT/'python/scrying_glass_storage.py').read_bytes()
        self.assertEqual(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(), 'ea80b59cca80c6885f6ba1ba4d32b759beb187b5')

    def test_campaign_metadata_updates_and_atomic_failure(self):
        outputs = []
        for kind in (SQLiteStorage, StagedStorage):
            s, a, b = self.storage(kind)
            self.assertTrue(s.campaign_name_exists('ALPHA'))
            self.assertFalse(s.campaign_name_exists('alpha', exclude=a))
            data = s.read_campaigns()
            data['campaigns'][a]['description'] = 'changed'
            data['active'] = a
            s.write_campaigns(data)
            s.update_campaign(a, name='Renamed')
            before = list(s.connection.iterdump())
            data = s.read_campaigns()
            data['campaigns'][a]['description'] = 'must roll back'
            data['active'] = '999'
            with self.assertRaises(sqlite3.IntegrityError):
                s.write_campaigns(data)
            self.assertEqual(list(s.connection.iterdump()), before)
            data = s.read_campaigns()
            del data['campaigns'][b]
            s.write_campaigns(data)
            self.assertFalse(s.campaign_exists(b))
            outputs.append(s.read_campaigns())
        self.assertEqual(outputs[0], outputs[1])

    def test_roster_roundtrip_ids_and_nested_rollback(self):
        for kind in (SQLiteStorage, StagedStorage):
            s, a, b = self.storage(kind)
            self.assertIsNone(s.load_characters(a))
            items = [{'id': 'hero', 'hp': 12, 'visible': True}]
            s.save_characters(a, items)
            self.assertEqual(s.load_characters(a), items)
            row = tuple(s.connection.execute('SELECT id,roster_id FROM characters').fetchone())
            s.save_characters(a, [{'id': 'hero', 'hp': 10}])
            self.assertEqual(tuple(s.connection.execute('SELECT id,roster_id FROM characters').fetchone()), row)
            with s.transaction():
                with self.assertRaises(ValueError):
                    s.save_characters(a, [{'id': 'hero', 'hp': 1}, {'id': 'bad', 'hp': True}])
                self.assertEqual(s.load_characters(a), [{'id': 'hero', 'hp': 10}])
                s.save_characters(b, [])
            self.assertEqual(s.load_characters(b), [])

    def test_setup_order_names_updates_and_delete(self):
        for kind in (SQLiteStorage, StagedStorage):
            s, a, _ = self.storage(kind)
            self.assertIsNone(s.newest_setup(a))
            for name in ('beta', 'Alpha'):
                s.save_setup(a, name, {'monsters': []}, updated_at=10)
            self.assertEqual(s.list_setups(a), ['Alpha', 'beta'])
            self.assertEqual(s.newest_setup(a), 'Alpha')
            before = s.connection.execute("SELECT id,encounter_id FROM battle_setups WHERE name='Alpha'").fetchone()
            s.save_setup(a, 'Alpha', {'battle_round': 4}, updated_at=20)
            self.assertEqual(tuple(s.connection.execute("SELECT id,encounter_id FROM battle_setups WHERE name='Alpha'").fetchone()), tuple(before))
            self.assertEqual(s.load_setup(a, 'Alpha')['battle_round'], 4)
            long = 'x'*80
            s.save_setup(a, long, {}, updated_at=0)
            self.assertEqual(s.unique_setup_name(a, long), 'x'*78+'-2')
            s.delete_setup(a, 'Alpha')
            self.assertFalse(s.setup_exists(a, 'Alpha'))
            self.assertIsNone(s.connection.execute('SELECT id FROM encounters WHERE id=?', (before['encounter_id'],)).fetchone())

    def test_checkpoint_rename_and_conflict_rollback(self):
        for kind in (SQLiteStorage, StagedStorage):
            s, a, _ = self.storage(kind)
            s.save_setup(a, 'old', {}, updated_at=1)
            for tag in ('checkpoint', 'undo'):
                encounter = s.connection.execute('INSERT INTO encounters DEFAULT VALUES').lastrowid
                s.connection.execute('INSERT INTO encounter_snapshots(campaign_id,encounter_id,kind,name,created,setup_name) VALUES (?,?,?,?,?,?)', (a, encounter, tag, tag, 1, 'old'))
            s.rename_setup(a, 'old', 'new')
            self.assertEqual([tuple(r) for r in s.connection.execute('SELECT kind,setup_name FROM encounter_snapshots ORDER BY id')], [('checkpoint', 'new'), ('undo', 'old')])
            s.save_setup(a, 'occupied', {}, updated_at=2)
            before = list(s.connection.iterdump())
            with self.assertRaises(sqlite3.IntegrityError):
                s.rename_setup(a, 'new', 'occupied')
            self.assertEqual(list(s.connection.iterdump()), before)

    def test_empty_setup_copy_move_and_identity_conflict(self):
        for kind in (SQLiteStorage, StagedStorage):
            s, a, b = self.storage(kind)
            s.save_setup(a, 'saved', {}, updated_at=12)
            self.assertEqual(s.transfer_setup(a, b, 'saved', 'copy'), 'saved')
            self.assertTrue(s.setup_exists(a, 'saved'))
            original = s.connection.execute('SELECT id,encounter_id FROM battle_setups WHERE campaign_id=?', (a,)).fetchone()
            self.assertEqual(s.transfer_setup(a, b, 'saved', 'move'), 'saved-2')
            moved = s.connection.execute("SELECT id,encounter_id,updated_at FROM battle_setups WHERE campaign_id=? AND name='saved-2'", (b,)).fetchone()
            self.assertEqual(tuple(moved), (*tuple(original), 12))
            self.assertFalse(s.setup_exists(a, 'saved'))
            s.save_setup(a, 'collision', {'monsters': [{'id': 'hero'}]}, updated_at=1)
            s.save_characters(b, [{'id': 'hero'}])
            before = list(s.connection.iterdump())
            with self.assertRaisesRegex(ValueError, 'Destination roster'):
                s.transfer_setup(a, b, 'collision', 'move')
            self.assertEqual(list(s.connection.iterdump()), before)

    def test_effect_rewrite_at_mocked_snapshot_boundary(self):
        for kind in (SQLiteStorage, StagedStorage):
            s, a, b = self.storage(kind)
            s.save_setup(a, 'saved', {}, updated_at=12)
            external = {'source_id': 'roster', 'anchor_id': 'roster', 'timing': 'end', 'turns': 2, 'concentration': False}
            internal = dict(external, source_id='monster', anchor_id='monster')
            snapshot = {'monsters': [{'id': 'monster', 'effects': [external, dict(external, concentration=True), internal]}], 'active_setup': {'campaign_id': a, 'name': 'saved'}}
            with patch.object(s, 'load_setup', return_value=copy.deepcopy(snapshot)), patch.object(s, 'save_setup') as save:
                s.transfer_setup(a, b, 'saved', 'copy')
            saved = save.call_args.args[2]
            self.assertIsNone(saved['active_setup'])
            self.assertEqual(saved['monsters'][0]['effects'], [dict(external, source_id=None, anchor_id=None, timing='manual', turns=None), internal])

    def test_application_state_maps_runtime_and_failures(self):
        outputs = []
        for kind in (SQLiteStorage, StagedStorage):
            s, a, _ = self.storage(kind)
            self.assertEqual(s.get_value('runtime_state', 'default'), 'default')
            s.set_value('active_campaign', a)
            s.save_setup(a, 'saved', {}, updated_at=1)
            state = {'active_setup': {'campaign_id': a, 'name': 'saved'}, 'active_turn_id': None, 'battle_round': 2}
            s.set_value('runtime_state', state)
            first = s.connection.execute('SELECT runtime_encounter_id FROM application_state').fetchone()[0]
            s.set_value('runtime_state', state)
            self.assertEqual(s.connection.execute('SELECT runtime_encounter_id FROM application_state').fetchone()[0], first)
            s.set_value('legacy_import_complete', {'at': 'now', 'counts': {'campaigns': 2}})
            s.set_value('legacy_campaign_id_map', {'old': a})
            outputs.append((s.get_value('runtime_state'), s.get_value('legacy_import_complete'), s.get_value('legacy_campaign_id_map')))
            before = list(s.connection.iterdump())
            for key in ('unknown', 'campaign_id_migration'):
                with self.assertRaises(ValueError):
                    s.set_value(key, {})
            with self.assertRaises(ValueError):
                s.set_value('runtime_state', {'active_setup': {'campaign_id': a, 'name': 'missing'}})
            self.assertEqual(list(s.connection.iterdump()), before)
            self.assertEqual(list(s.connection.execute('PRAGMA foreign_key_check')), [])
        self.assertEqual(outputs[0], outputs[1])


if __name__ == '__main__':
    unittest.main()
