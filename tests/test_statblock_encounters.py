"""Private adapter tests; normal server wiring is intentionally not activated yet."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage, public_payload


def snapshot(label='Source'):
    return dict(model_version=1, source_label=label, subtitle='', completeness='available',
        definitions=[], facts=[], warnings=[], nodes=[], provenance=[dict(position=0,
        role='selected', provider='file', entity_id='fixture', adapter_version='1', credits=[])])


class ProjectionTests(unittest.TestCase):
    def test_nested_private_content_is_removed(self):
        value = {PRIVATE_KEY: {'m': 'secret'}, 'items': [{PRIVATE_KEY: 'secret', 'hp': 7}], 'pair': ({PRIVATE_KEY: 'secret'},)}
        result = public_payload(value)
        self.assertNotIn('secret', json.dumps(result))
        self.assertEqual(result, {'items': [{'hp': 7}], 'pair': ({},)})
        self.assertEqual(value[PRIVATE_KEY], {'m': 'secret'})

    def test_projection_does_not_alias_or_rewrite_strings(self):
        value = {'notes': PRIVATE_KEY, 'items': [{'name': 'Goblin'}]}
        result = public_payload(value)
        result['items'][0]['name'] = 'Changed'
        self.assertEqual(value['items'][0]['name'], 'Goblin')
        self.assertEqual(result['notes'], PRIVATE_KEY)


class EncounterAdapterTests(unittest.TestCase):
    def setUp(self):
        from python.scrying_glass_storage import SQLiteStorage
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'db.sqlite3'
        self.storage = SQLiteStorage(self.path)
        self.addCleanup(lambda: self.storage.close())
        self.campaign = self.storage.create_campaign('Fixture', '', 'now')
        self.storage.save_setup(self.campaign, 'one', {'monsters': [{'id': 'm', 'hp': 7}]})
        self.encounter = self.storage.connection.execute('SELECT encounter_id FROM battle_setups WHERE name=?', ('one',)).fetchone()[0]
        self.api = PrivateEncounterStorage(self.storage)

    def put(self, label='Source'):
        state = self.api.load(self.encounter)
        state[PRIVATE_KEY]['m'] = snapshot(label)
        return self.api.save(self.encounter, state)

    def test_roundtrip_reopen_and_no_revision_bump_for_tracker_changes(self):
        saved = self.put()
        original = copy.deepcopy(saved[PRIVATE_KEY]['m'])
        ordinary = self.storage._load_encounter(self.encounter)
        self.assertNotIn(PRIVATE_KEY, ordinary)
        ordinary['monsters'][0]['hp'] = 2
        result = self.api.save(self.encounter, ordinary)
        self.assertEqual(result[PRIVATE_KEY]['m'], original)
        self.assertEqual(result['monsters'][0]['hp'], 2)
        self.assertEqual(self.put('Changed')[PRIVATE_KEY]['m']['revision'], 2)
        self.storage.close()
        from python.scrying_glass_storage import SQLiteStorage
        self.storage = SQLiteStorage(self.path)
        self.api = PrivateEncounterStorage(self.storage)
        self.assertEqual(self.api.load(self.encounter)[PRIVATE_KEY]['m']['revision'], 2)

    def test_rebuilt_rows_preserve_reference_revision(self):
        self.put()
        before = self.put('Changed')
        old_id = self.storage.connection.execute('SELECT id FROM monsters').fetchone()[0]
        original = self.storage._save_entities
        def rebuild(table, owner_name, owner, items):
            if table == 'monsters':
                self.storage.connection.execute('DELETE FROM monsters WHERE encounter_id=?', (owner,))
            return original(table, owner_name, owner, items)
        with patch.object(self.storage, '_save_entities', side_effect=rebuild):
            after = self.api.save(self.encounter, before)
        self.assertNotEqual(self.storage.connection.execute('SELECT id FROM monsters').fetchone()[0], old_id)
        self.assertEqual(after[PRIVATE_KEY], before[PRIVATE_KEY])

    def test_scope_omission_and_deletion_cascade(self):
        before = self.put()
        invalid = copy.deepcopy(before)
        invalid[PRIVATE_KEY]['foreign'] = snapshot()
        with self.assertRaises(ValueError): self.api.save(self.encounter, invalid)
        invalid = copy.deepcopy(before)
        invalid[PRIVATE_KEY] = {}
        with self.assertRaises(ValueError): self.api.save(self.encounter, invalid)
        self.assertEqual(self.api.load(self.encounter), before)
        deleted = copy.deepcopy(before)
        deleted['monsters'] = []
        after = self.api.save(self.encounter, deleted)
        self.assertEqual(after[PRIVATE_KEY], {})
        self.assertEqual(self.storage.connection.execute('SELECT count(*) FROM monster_statblocks').fetchone()[0], 0)

    def test_invalid_graph_and_write_failure_roll_back_tracker_and_content(self):
        before = self.put()
        invalid = copy.deepcopy(before)
        invalid[PRIVATE_KEY]['m']['model_version'] = 2
        with self.assertRaises(ValueError): self.api.save(self.encounter, invalid)
        self.assertEqual(self.api.load(self.encounter), before)
        changed = copy.deepcopy(before)
        changed['monsters'][0]['hp'] = 1
        changed[PRIVATE_KEY]['m'] = snapshot('Replacement')
        with patch('python.scrying_glass_statblock_storage.StatblockStorage.save', side_effect=OSError('injected')):
            with self.assertRaises(OSError): self.api.save(self.encounter, changed)
        self.assertEqual(self.api.load(self.encounter), before)
        with self.assertRaises(RuntimeError):
            with self.storage.transaction():
                self.api.save(self.encounter, changed)
                raise RuntimeError('outer rollback')
        self.assertEqual(self.api.load(self.encounter), before)


if __name__ == '__main__':
    unittest.main()
