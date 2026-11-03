"""Native facade record behavior compared with the pinned original methods."""
import unittest
from python.scrying_glass_storage import SQLiteStorage
from storage_split_reference import base_storage, reference_class


class StorageRecordsPreparationTests(unittest.TestCase):
    def test_scalar_encodings_and_rejections(self):
        for kind in (reference_class(), SQLiteStorage):
            self.assertEqual(kind._typed(True), ('boolean', None, 1, None))
            self.assertEqual(kind._typed(2.5), ('real', None, None, 2.5))
            for value in ({}, [], float('inf'), float('nan')):
                with self.assertRaises(ValueError):
                    kind._typed(value)

    def test_records_presence_order_identity_and_deletion(self):
        for kind in (reference_class(), SQLiteStorage):
            s = base_storage(self, kind)
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
        outputs = []
        for kind in (reference_class(), SQLiteStorage):
            s = base_storage(self, kind)
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
            outputs.append(s.get_value('runtime_state'))
            self.assertIsNone(outputs[-1]['active_turn_id'])
            del state['active_turn_id']
            s.set_value('runtime_state', state)
            self.assertNotIn('active_turn_id', s.get_value('runtime_state'))
            self.assertEqual(list(s.connection.execute('PRAGMA foreign_key_check')), [])
        self.assertEqual(*outputs)
