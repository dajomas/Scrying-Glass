"""Pinned original migration behavior, plus native facade schema dispatch."""
import copy
import json
import unittest
from unittest.mock import patch
from python.scrying_glass_storage import SQLiteStorage
from storage_split_reference import base_storage, reference_class, reference_methods


class StorageSchemaPreparationTests(unittest.TestCase):
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

    def test_schema_and_empty_legacy_parity(self):
        self.assertEqual(len(reference_methods()), 38)
        for version in (1, 2):
            dumps = []
            for kind in (reference_class(), SQLiteStorage):
                s = base_storage(self, kind)
                self.legacy(s, version)
                with patch('time.time', return_value=123):
                    s._upgrade(version)
                self.assertEqual(s.connection.execute('PRAGMA user_version').fetchone()[0], 3)
                self.assertEqual(list(s.connection.execute('PRAGMA foreign_key_check')), [])
                dumps.append(list(s.connection.iterdump()))
            self.assertEqual(*dumps)

    def test_failed_legacy_upgrade_restores_schema(self):
        for version in (1, 2):
            for kind in (reference_class(), SQLiteStorage):
                s = base_storage(self, kind)
                self.legacy(s, version, bad=True)
                before = list(s.connection.iterdump())
                with self.assertRaises(ValueError):
                    s._upgrade(version)
                self.assertEqual(list(s.connection.iterdump()), before)
                self.assertFalse(s.connection.in_transaction)

    def test_reference_copy_errors_and_static_descriptor(self):
        original = reference_class()
        for strict in (False, True):
            state = {'active_setup': {'campaign': 'old'}, 'nested': [1]}
            result = SQLiteStorage.convert_campaign_references(state, {'old': 7}, strict=strict)
            self.assertEqual(result, original.convert_campaign_references(state, {'old': 7}, strict=strict))
            result['nested'].append(2)
            self.assertEqual(state['nested'], [1])
        self.assertIsNone(SQLiteStorage.convert_campaign_references({'active_setup': {'campaign': 'missing'}}, {}, strict=False)['active_setup'])
        for state in (None, {'active_setup': []}, {'active_setup': {'campaign': 'missing'}}):
            with self.assertRaises(ValueError):
                SQLiteStorage.convert_campaign_references(state, {})
