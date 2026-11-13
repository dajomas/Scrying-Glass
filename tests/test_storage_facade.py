"""SQLiteStorage facade: records, schema upgrades, operations and file-backed runtime.

Runs against the production class with real SQLite; there is no frozen reference copy.
"""
import ast
import copy
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from inspect import getattr_static
from pathlib import Path
from unittest.mock import patch
from python import scrying_glass_storage as facade
from python import scrying_glass_storage_fields as fields
from python.scrying_glass_storage import SQLiteStorage

ROOT = Path(__file__).resolve().parents[1]
FIELD_NAMES = ('TEXT_FIELDS', 'INT_FIELDS', 'BOOL_FIELDS', 'ENTITY_FIELDS', 'LOG_FIELDS', 'LIST_FIELDS', 'STATE_FIELDS')


def base_storage(test):
    value = object.__new__(SQLiteStorage)
    value.connection = sqlite3.connect(':memory:', isolation_level=None)
    value.connection.row_factory = sqlite3.Row
    test.addCleanup(value.close)
    value.connection.execute('PRAGMA foreign_keys=ON')
    value._create_schema()
    value.connection.execute('PRAGMA user_version=3')
    value.migration_backup = Path('fixture.backup')
    return value


class StorageFieldTests(unittest.TestCase):
    def test_facade_reexports_shared_field_sets(self):
        for name in FIELD_NAMES:
            self.assertIs(getattr(facade, name), getattr(fields, name))
        fields.STATE_FIELDS.add('__probe__')
        try:
            self.assertIn('__probe__', facade.STATE_FIELDS)
        finally:
            fields.STATE_FIELDS.discard('__probe__')


class StorageRecordTests(unittest.TestCase):
    def test_scalar_encodings_and_rejections(self):
        self.assertEqual(SQLiteStorage._typed(True), ('boolean', None, 1, None))
        self.assertEqual(SQLiteStorage._typed(2.5), ('real', None, None, 2.5))
        for value in ({}, [], float('inf'), float('nan')):
            with self.assertRaises(ValueError):
                SQLiteStorage._typed(value)

    def test_records_presence_order_identity_and_deletion(self):
        s = base_storage(self)
        c = s.create_campaign('Fixture', '', 'now')
        s.save_characters(c, [{'id':'a','hp':7,'visible':True,'ratio':2.5}, {'id':'b','hp':None,'note':None}])
        items = s.load_characters(c)
        self.assertNotIn('ac', items[0])
        self.assertIsNone(items[1]['hp'])
        ids = list(s.connection.execute('SELECT id,combatant_id FROM characters ORDER BY id'))
        s.save_characters(c, list(reversed(items)))
        self.assertEqual(list(s.connection.execute('SELECT id,combatant_id FROM characters ORDER BY id')), ids)
        self.assertEqual(s.load_characters(c), list(reversed(items)))
        s.save_characters(c, items[:1])
        self.assertEqual(s.load_characters(c), items[:1])
        before = list(s.connection.iterdump())
        with self.assertRaises(ValueError):
            s.save_characters(c, [{'id':'a','hp':1}, {'id':'bad','hp':True}])
        self.assertEqual(list(s.connection.iterdump()), before)

    def test_logs_occurrences_and_runtime_marker(self):
        s = base_storage(self)
        c = s.create_campaign('Fixture', '', 'now')
        s.save_setup(c, 'saved', {}, updated_at=1)
        state = {'active_setup':{'campaign_id':c,'name':'saved'}, 'active_turn_id':None,
                 'battle_order':['a','a','b'], 'activity_log':[{'id':'e','amount':None,'note':True}],
                 'display':{'background':'#123456','battle_order_font_size':24}, 'battle_round':3}
        s.set_value('runtime_state', state)
        before = list(s.connection.execute('SELECT id,list_kind,combatant_id,occurrence FROM ordered_combatants ORDER BY id'))
        state['battle_order'] = ['b','a','a']
        s.set_value('runtime_state', state)
        self.assertEqual(list(s.connection.execute('SELECT id,list_kind,combatant_id,occurrence FROM ordered_combatants ORDER BY id')), before)
        saved = s.get_value('runtime_state')
        self.assertIsNone(saved['active_turn_id'])
        self.assertEqual(saved['battle_order'], ['b', 'a', 'a'])
        self.assertEqual(saved['battle_round'], 3)
        del state['active_turn_id']
        s.set_value('runtime_state', state)
        self.assertNotIn('active_turn_id', s.get_value('runtime_state'))
        self.assertEqual(list(s.connection.execute('PRAGMA foreign_key_check')), [])


class StorageSchemaTests(unittest.TestCase):
    def legacy(self, s, version, bad=False):
        db = s.connection
        for name in [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='trigger'")]:
            db.execute(f'DROP TRIGGER {name}')
        db.execute('PRAGMA foreign_keys=OFF')
        for name in [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]:
            db.execute(f'DROP TABLE {name}')
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('CREATE TABLE campaigns(slug TEXT PRIMARY KEY,metadata_json TEXT)' if version==1 else 'CREATE TABLE campaigns(id INTEGER PRIMARY KEY,name TEXT,description TEXT,created TEXT,metadata_json TEXT)')
        owner = 'campaign_slug' if version==1 else 'campaign_id'
        db.execute(f'CREATE TABLE campaign_characters({owner} TEXT,characters_json TEXT)')
        db.execute(f'CREATE TABLE battle_setups({owner} TEXT,name TEXT,snapshot_json TEXT,updated_at REAL)')
        db.execute('CREATE TABLE application_state(key TEXT,value_json TEXT)')
        if bad:
            db.execute('INSERT INTO application_state VALUES (?,?)', ('runtime_state', json.dumps({'active_setup': {'campaign': 'missing'}})))
        db.execute(f'PRAGMA user_version={version}')

    def test_empty_legacy_upgrade(self):
        for version in (1, 2):
            s = base_storage(self)
            self.legacy(s, version)
            with patch('time.time', return_value=123):
                s._upgrade(version)
            self.assertEqual(s.connection.execute('PRAGMA user_version').fetchone()[0], 3)
            self.assertEqual(list(s.connection.execute('PRAGMA foreign_key_check')), [])

    def test_failed_legacy_upgrade_restores_schema(self):
        for version in (1, 2):
            s = base_storage(self)
            self.legacy(s, version, bad=True)
            before = list(s.connection.iterdump())
            with self.assertRaises(ValueError):
                s._upgrade(version)
            self.assertEqual(list(s.connection.iterdump()), before)
            self.assertFalse(s.connection.in_transaction)

    def test_campaign_reference_conversion_copies_and_rejects(self):
        for strict in (False, True):
            state = {'active_setup': {'campaign': 'old'}, 'nested': [1]}
            result = SQLiteStorage.convert_campaign_references(state, {'old': 7}, strict=strict)
            self.assertEqual(result['active_setup'], {'campaign_id': '7'})
            result['nested'].append(2)
            self.assertEqual(state['nested'], [1])
        self.assertIsNone(SQLiteStorage.convert_campaign_references({'active_setup': {'campaign': 'missing'}}, {}, strict=False)['active_setup'])
        for state in (None, {'active_setup': []}, {'active_setup': {'campaign': 'missing'}}):
            with self.assertRaises(ValueError):
                SQLiteStorage.convert_campaign_references(state, {})


class StorageOperationTests(unittest.TestCase):
    def fixture(self):
        s = base_storage(self)
        s.connection.execute("CREATE TABLE encounter_snapshots(id INTEGER PRIMARY KEY,campaign_id INTEGER,kind TEXT,setup_name TEXT)")
        a = s.create_campaign('Alpha', '', 'now', metadata={'flag':True})
        b = s.create_campaign('Beta', '', 'now')
        return s, a, b

    def test_campaign_roster_state_and_nested_rollback(self):
        s, a, b = self.fixture()
        self.assertTrue(s.campaign_name_exists('ALPHA'))
        self.assertFalse(s.campaign_name_exists('alpha', exclude=a))
        s.save_characters(a, [{'id':'hero','hp':12}])
        with s.transaction():
            with self.assertRaises(ValueError):
                s.save_characters(a, [{'id':'hero','hp':1},{'id':'bad','hp':True}])
            self.assertEqual(s.load_characters(a)[0]['hp'], 12)
            s.update_campaign(a, description='changed')
        before = list(s.connection.iterdump())
        data = s.read_campaigns()
        data['campaigns'][a]['description'] = 'rollback'
        data['active'] = '999'
        with self.assertRaises(sqlite3.IntegrityError):
            s.write_campaigns(data)
        self.assertEqual(list(s.connection.iterdump()), before)
        s.set_value('active_campaign', a)
        s.set_value('legacy_campaign_id_map', {'old':a})
        s.set_value('legacy_import_complete', {'at':'now','counts':{'campaigns':2}})
        for key in ('unknown', 'campaign_id_migration'):
            with self.assertRaises(ValueError): s.set_value(key, {})
        data = s.read_campaigns()
        del data['campaigns'][b]
        s.write_campaigns(data)
        self.assertFalse(s.campaign_exists(b))
        self.assertEqual(s.get_value('legacy_campaign_id_map'), {'old': a})
        self.assertEqual(s.get_value('legacy_import_complete'), {'at': 'now', 'counts': {'campaigns': 2, 'setups': 0, 'characters': 0}})

    def test_setup_names_checkpoint_references_move_and_copy(self):
        s, a, b = self.fixture()
        self.assertIsNone(s.newest_setup(a))
        for name in ('beta','Alpha'):
            s.save_setup(a, name, {}, updated_at=10)
        self.assertEqual(s.list_setups(a), ['Alpha','beta'])
        self.assertEqual(s.newest_setup(a), 'Alpha')
        s.connection.execute("INSERT INTO encounter_snapshots VALUES (1,?,'checkpoint','Alpha')", (a,))
        s.rename_setup(a, 'Alpha', 'renamed')
        self.assertEqual(s.connection.execute('SELECT setup_name FROM encounter_snapshots').fetchone()[0], 'renamed')
        before = list(s.connection.iterdump())
        with self.assertRaises(sqlite3.IntegrityError): s.rename_setup(a, 'renamed', 'beta')
        self.assertEqual(list(s.connection.iterdump()), before)
        s.save_setup(a, 'x'*80, {}, updated_at=0)
        self.assertEqual(s.unique_setup_name(a, 'x'*80), 'x'*78+'-2')
        ident = tuple(s.connection.execute("SELECT id,encounter_id FROM battle_setups WHERE campaign_id=? AND name='renamed'", (a,)).fetchone())
        self.assertEqual(s.transfer_setup(a,b,'renamed','copy'), 'renamed')
        self.assertEqual(s.transfer_setup(a,b,'renamed','move'), 'renamed-2')
        moved = tuple(s.connection.execute("SELECT id,encounter_id FROM battle_setups WHERE campaign_id=? AND name='renamed-2'", (b,)).fetchone())
        self.assertEqual(moved, ident)
        s.delete_setup(b,'renamed-2')
        self.assertIsNone(s.connection.execute('SELECT id FROM encounters WHERE id=?',(ident[1],)).fetchone())
        s.save_setup(a, 'collision', {'monsters':[{'id':'hero'}]}, updated_at=0)
        s.save_characters(b,[{'id':'hero'}])
        before = list(s.connection.iterdump())
        with self.assertRaisesRegex(ValueError, 'Destination roster'): s.transfer_setup(a,b,'collision','move')
        self.assertEqual(list(s.connection.iterdump()), before)

    def test_effect_rewrite_at_mocked_snapshot_boundary(self):
        s, a, b = self.fixture()
        s.save_setup(a,'saved',{},updated_at=12)
        external = {'source_id':'roster','anchor_id':'roster','timing':'end','turns':2,'concentration':False}
        internal = dict(external,source_id='monster',anchor_id='monster')
        state = {'monsters':[{'id':'monster','effects':[external,dict(external,concentration=True),internal]}]}
        with patch.object(s,'load_setup',return_value=copy.deepcopy(state)), patch.object(s,'save_setup') as save:
            s.transfer_setup(a,b,'saved','copy')
        result = save.call_args.args[2]
        self.assertIsNone(result['active_setup'])
        self.assertEqual(result['monsters'][0]['effects'],[dict(external,source_id=None,anchor_id=None,timing='manual',turns=None),internal])


class StorageRuntimeTests(unittest.TestCase):
    def test_dispatch_modules_and_file_limits(self):
        self.assertEqual(SQLiteStorage.SCHEMA_VERSION, 8)
        self.assertIsInstance(getattr_static(SQLiteStorage, 'convert_campaign_references'), staticmethod)
        self.assertIsInstance(getattr_static(SQLiteStorage, '_typed'), staticmethod)
        self.assertEqual(SQLiteStorage.__module__, 'python.scrying_glass_storage')
        self.assertEqual(SQLiteStorage._upgrade.__module__, 'python.scrying_glass_storage_schema')
        self.assertEqual(SQLiteStorage._save_entities.__module__, 'python.scrying_glass_storage_records')
        self.assertEqual(SQLiteStorage.save_setup.__module__, 'python.scrying_glass_storage_operations')
        for suffix in ('', '_fields', '_schema', '_records', '_operations'):
            data = (ROOT/f'python/scrying_glass_storage{suffix}.py').read_bytes()
            self.assertLessEqual(len(data), 20000)
            tree = ast.parse(data.decode())
            self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ('exec','eval','compile') for n in ast.walk(tree)))

    def test_v8_persistence_reopen_and_transaction_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'storage.sqlite3'
            with closing(SQLiteStorage(path)) as s:
                self.assertEqual(s.connection.execute('PRAGMA user_version').fetchone()[0],8)
                self.assertIsNone(s.migration_backup)
                c = s.create_campaign('Fixture','','now')
                s.save_characters(c,[{'id':'hero','hp':12,'effects':[]}])
                effect = dict(id='e',name='Marked',source_id='hero',notes='',public=True,
                              concentration=False,timing='manual',turns=None,anchor_id=None)
                state = {'monsters':[{'id':'m','hp':7,'effects':[effect]}], 'battle_order':['m','m'],
                         'active_turn_id':None,'has_lair':True,'lairs':[{'id':'lair','name':'Cavern'}]}
                s.save_setup(c,'saved',state,updated_at=10)
                state = s.load_setup(c,'saved')
                state['active_setup'] = {'campaign_id':c,'name':'saved'}
                s.set_value('active_campaign',c)
                s.set_value('runtime_state',state)
                with patch.object(s,'_save_encounter',side_effect=ValueError('injected')):
                    with self.assertRaises(ValueError): s.save_setup(c,'saved',{})
                self.assertEqual(s.load_setup(c,'saved')['monsters'],state['monsters'])
                self.assertEqual(list(s.connection.execute('PRAGMA foreign_key_check')),[])
            with closing(SQLiteStorage(path)) as s:
                self.assertIsNone(s.migration_backup)
                self.assertEqual(s.get_value('runtime_state'),state)
                self.assertEqual(s.load_characters(c),[{'id':'hero','hp':12,'effects':[]}])

    def test_constructor_failure_closes_connection(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'future.sqlite3'
            with closing(sqlite3.connect(path)) as db: db.execute('PRAGMA user_version=99')
            def close(s): s.connection.close()
            with patch.object(SQLiteStorage,'close',autospec=True,side_effect=close) as closed:
                with self.assertRaises(RuntimeError): SQLiteStorage(path)
            closed.assert_called_once()
            with self.assertRaises(sqlite3.ProgrammingError):
                closed.call_args.args[0].connection.execute('SELECT 1')


if __name__ == '__main__':
    unittest.main()
