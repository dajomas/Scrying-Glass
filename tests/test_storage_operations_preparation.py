"""Native operations parity; base-schema fixtures and a mocked effect boundary."""
import copy
import sqlite3
import unittest
from unittest.mock import patch
from python.scrying_glass_storage import SQLiteStorage
from storage_split_reference import base_storage, reference_class


class StorageOperationsPreparationTests(unittest.TestCase):
    def fixture(self, kind):
        s = base_storage(self, kind)
        s.connection.execute("CREATE TABLE encounter_snapshots(id INTEGER PRIMARY KEY,campaign_id INTEGER,kind TEXT,setup_name TEXT)")
        a = s.create_campaign('Alpha', '', 'now', metadata={'flag':True})
        b = s.create_campaign('Beta', '', 'now')
        return s, a, b

    def test_campaign_roster_state_and_nested_rollback(self):
        outputs = []
        for kind in (reference_class(), SQLiteStorage):
            s, a, b = self.fixture(kind)
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
            outputs.append((s.read_campaigns(),s.get_value('legacy_campaign_id_map'),s.get_value('legacy_import_complete')))
        self.assertEqual(*outputs)

    def test_setup_names_checkpoint_references_move_and_copy(self):
        for kind in (reference_class(), SQLiteStorage):
            s, a, b = self.fixture(kind)
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
        for kind in (reference_class(), SQLiteStorage):
            s, a, b = self.fixture(kind)
            s.save_setup(a,'saved',{},updated_at=12)
            external = {'source_id':'roster','anchor_id':'roster','timing':'end','turns':2,'concentration':False}
            internal = dict(external,source_id='monster',anchor_id='monster')
            state = {'monsters':[{'id':'monster','effects':[external,dict(external,concentration=True),internal]}]}
            with patch.object(s,'load_setup',return_value=copy.deepcopy(state)), patch.object(s,'save_setup') as save:
                s.transfer_setup(a,b,'saved','copy')
            result = save.call_args.args[2]
            self.assertIsNone(result['active_setup'])
            self.assertEqual(result['monsters'][0]['effects'],[dict(external,source_id=None,anchor_id=None,timing='manual',turns=None),internal])
