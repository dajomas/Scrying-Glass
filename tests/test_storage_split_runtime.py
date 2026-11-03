"""Native facade activation: real file-backed constructor/reopen/upgrade checks."""
import ast
from contextlib import closing
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from python import scrying_glass_storage as module
from python.scrying_glass_storage import SQLiteStorage
from storage_split_reference import ROOT, base_storage, reference_class, reference_methods


class StorageSplitRuntimeTests(unittest.TestCase):
    def test_native_dispatch_surface_and_complete_file_limits(self):
        reference = reference_class()
        self.assertEqual(SQLiteStorage.SCHEMA_VERSION, 8)
        for name in reference_methods():
            self.assertTrue(callable(getattr(SQLiteStorage, name)))
        self.assertIsInstance(__import__('inspect').getattr_static(SQLiteStorage, 'convert_campaign_references'), staticmethod)
        self.assertIsInstance(__import__('inspect').getattr_static(SQLiteStorage, '_typed'), staticmethod)
        self.assertEqual(SQLiteStorage.__module__, 'python.scrying_glass_storage')
        self.assertEqual(SQLiteStorage._upgrade.__module__, 'python.scrying_glass_storage_schema')
        self.assertEqual(SQLiteStorage._save_entities.__module__, 'python.scrying_glass_storage_records')
        self.assertEqual(SQLiteStorage.save_setup.__module__, 'python.scrying_glass_storage_operations')
        for suffix in ('', '_fields', '_schema', '_records', '_operations'):
            data = (ROOT/f'python/scrying_glass_storage{suffix}.py').read_bytes()
            self.assertLessEqual(len(data), 20000)
            tree = ast.parse(data.decode())
            self.assertFalse(any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ('exec','eval','compile') for n in ast.walk(tree)))
        self.assertEqual(set(reference_methods()), {n for n in vars(reference) if not n.startswith('__') and callable(getattr(reference,n))} | {'__init__'})

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
