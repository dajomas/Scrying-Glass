"""Production SQLiteStorage save-boundary tests; service/transport wiring remains separate."""
import copy
import unittest
from unittest.mock import patch
import test_statblock_encounters as fixtures
from python.scrying_glass_statblock_encounters import PRIVATE_KEY


class ProductionStatblockSaveTests(unittest.TestCase):
    setUp = fixtures.EncounterAdapterTests.setUp
    put = fixtures.EncounterAdapterTests.put

    def rebuild(self, table, owner_name, owner, items):
        if table == 'monsters':
            self.storage.connection.execute('DELETE FROM monsters WHERE encounter_id=?', (owner,))
        return self.original_save_entities(table, owner_name, owner, items)

    def test_save_setup_preserves_rebuilt_snapshot_without_private_load_payload(self):
        before = self.put(); plain = self.storage.load_setup(self.campaign, 'one')
        self.assertNotIn(PRIVATE_KEY, plain)
        plain['monsters'][0]['hp'] = 2
        self.original_save_entities = self.storage._save_entities
        with patch.object(self.storage, '_save_entities', side_effect=self.rebuild):
            self.assertIsNone(self.storage.save_setup(self.campaign, 'one', plain, updated_at=123))
        self.assertEqual(self.api.load(self.encounter)[PRIVATE_KEY], before[PRIVATE_KEY])
        self.assertEqual(self.storage.load_setup(self.campaign, 'one')['monsters'][0]['hp'], 2)
        self.assertEqual(self.storage.connection.execute("SELECT updated_at FROM battle_setups WHERE name='one'").fetchone()[0], 123)

    def test_runtime_save_preserves_private_content_and_plain_get_value(self):
        self.storage.set_value('runtime_state', {'monsters':[{'id':'m','hp':7}]})
        runtime = self.storage.connection.execute('SELECT runtime_encounter_id FROM application_state').fetchone()[0]
        state = self.api.load(runtime); state[PRIVATE_KEY]['m'] = fixtures.snapshot('Runtime')
        before = self.api.save(runtime, state, runtime=True)
        plain = self.storage.get_value('runtime_state'); plain['monsters'][0]['hp'] = 3
        self.original_save_entities = self.storage._save_entities
        with patch.object(self.storage, '_save_entities', side_effect=self.rebuild):
            self.storage.set_value('runtime_state', plain)
        self.assertNotIn(PRIVATE_KEY, self.storage.get_value('runtime_state'))
        self.assertEqual(self.api.load(runtime)[PRIVATE_KEY], before[PRIVATE_KEY])
        self.assertEqual(self.storage.get_value('runtime_state')['monsters'][0]['hp'], 3)

    def test_ordinary_saves_reject_private_envelope_and_roll_back(self):
        before = self.put()
        with self.assertRaises(ValueError): self.storage.save_setup(self.campaign, 'one', before)
        self.assertEqual(self.api.load(self.encounter), before)
        runtime_before = self.storage.get_value('runtime_state')
        with self.assertRaises(ValueError): self.storage.set_value('runtime_state', before)
        self.assertEqual(self.storage.get_value('runtime_state'), runtime_before)

    def test_missing_ids_keep_legacy_allocation_without_mutating_input(self):
        self.put(); plain = self.storage.load_setup(self.campaign, 'one')
        plain['monsters'].append({'hp':4})
        original = copy.deepcopy(plain)
        self.storage.save_setup(self.campaign, 'one', plain)
        self.assertEqual(plain, original)
        loaded = self.api.load(self.encounter)
        self.assertEqual(len(loaded['monsters']), 2)
        self.assertTrue(loaded['monsters'][1]['id'])
        self.assertEqual(set(loaded[PRIVATE_KEY]), {'m'})

    def test_storage_hook_failure_rolls_back_tracker_timestamp_and_snapshot(self):
        before = self.put(); plain = self.storage.load_setup(self.campaign, 'one')
        stamp = self.storage.connection.execute("SELECT updated_at FROM battle_setups WHERE name='one'").fetchone()[0]
        plain['monsters'][0]['hp'] = 1
        self.original_save_entities = self.storage._save_entities
        with patch.object(self.storage, '_save_entities', side_effect=self.rebuild):
            with patch('python.scrying_glass_statblock_encounters.PrivateEncounterStorage._reattach', side_effect=OSError('injected')):
                with self.assertRaises(OSError): self.storage.save_setup(self.campaign, 'one', plain, updated_at=1)
        self.assertEqual(self.api.load(self.encounter), before)
        self.assertEqual(self.storage.connection.execute("SELECT updated_at FROM battle_setups WHERE name='one'").fetchone()[0], stamp)

    def test_plain_save_deletion_cascades_only_the_selected_encounter(self):
        self.put()
        self.storage.save_setup(self.campaign, 'two', {'monsters':[{'id':'m','hp':8}]})
        other = self.storage.connection.execute("SELECT encounter_id FROM battle_setups WHERE name='two'").fetchone()[0]
        state = self.api.load(other); state[PRIVATE_KEY]['m'] = fixtures.snapshot('Other')
        other_before = self.api.save(other, state)
        self.storage.save_setup(self.campaign, 'one', {'monsters':[]})
        self.assertEqual(self.api.load(self.encounter)[PRIVATE_KEY], {})
        self.assertEqual(self.api.load(other), other_before)


if __name__ == '__main__': unittest.main()
