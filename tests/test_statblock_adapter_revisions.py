"""Adapter regressions with real SQLiteStorage; production services are not wired."""
import copy
import unittest
from unittest.mock import patch
import test_statblock_encounters as fixtures
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage


class AdapterRevisionTests(unittest.TestCase):
    setUp = fixtures.EncounterAdapterTests.setUp
    put = fixtures.EncounterAdapterTests.put

    def rebuild(self, table, owner_name, owner, items):
        if table == 'monsters':
            self.storage.connection.execute('DELETE FROM monsters WHERE encounter_id=?', (owner,))
        return self.original_save_entities(table, owner_name, owner, items)

    def test_rebuild_uses_final_metadata_without_revision_update(self):
        self.put(); before = self.put('Changed')
        self.original_save_entities = self.storage._save_entities
        statements = []
        self.storage.connection.set_trace_callback(statements.append)
        try:
            with patch.object(self.storage, '_save_entities', side_effect=self.rebuild):
                after = self.api.save(self.encounter, before)
        finally:
            self.storage.connection.set_trace_callback(None)
        self.assertEqual(after[PRIVATE_KEY], before[PRIVATE_KEY])
        self.assertFalse(any('UPDATE MONSTER_STATBLOCKS' in sql.upper() for sql in statements))

    def test_changed_content_during_rebuild_advances_once(self):
        self.put(); before = self.put('Changed')
        candidate = copy.deepcopy(before)
        candidate[PRIVATE_KEY]['m'] = fixtures.snapshot('Replacement')
        self.original_save_entities = self.storage._save_entities
        with patch.object(self.storage, '_save_entities', side_effect=self.rebuild):
            after = self.api.save(self.encounter, candidate)
        self.assertEqual(after[PRIVATE_KEY]['m']['revision'], 3)
        self.assertEqual(after[PRIVATE_KEY]['m']['source_label'], 'Replacement')
        self.assertEqual(self.api.load(self.encounter), after)

    def test_stale_snapshot_rejects_tracker_change_before_plain_save(self):
        stale = self.put(); latest = self.put('Latest')
        stale['monsters'][0]['hp'] = 1
        with patch.object(self.api, 'save_plain', side_effect=AssertionError('must not write')):
            with self.assertRaisesRegex(ValueError, 'Stale'):
                self.api.save(self.encounter, stale)
        self.assertEqual(self.api.load(self.encounter), latest)

    def test_same_combatant_id_in_another_encounter_is_isolated(self):
        before = self.put()
        self.storage.save_setup(self.campaign, 'two', {'monsters':[{'id':'m','hp':9}]})
        other = self.storage.connection.execute("SELECT encounter_id FROM battle_setups WHERE name='two'").fetchone()[0]
        state = self.api.load(other)
        state[PRIVATE_KEY]['m'] = fixtures.snapshot('Other encounter')
        other_before = self.api.save(other, state)
        changed = copy.deepcopy(before); changed['monsters'][0]['hp'] = 2
        self.api.save(self.encounter, changed)
        self.assertEqual(self.api.load(other), other_before)
        self.assertEqual(self.api.load(self.encounter)[PRIVATE_KEY], before[PRIVATE_KEY])

    def test_tracker_edit_does_not_save_or_retime_snapshot(self):
        before = self.put()
        changed = copy.deepcopy(before); changed['monsters'][0]['hp'] = 2
        with patch.object(self.api.snapshots, 'save', side_effect=AssertionError('must not replace')):
            after = self.api.save(self.encounter, changed)
        self.assertEqual(after[PRIVATE_KEY], before[PRIVATE_KEY])

    def test_reattach_failure_rolls_back_rebuilt_rows_and_content(self):
        before = self.put()
        self.original_save_entities = self.storage._save_entities
        with patch.object(self.storage, '_save_entities', side_effect=self.rebuild):
            with patch.object(self.api, '_reattach', side_effect=OSError('injected')):
                with self.assertRaises(OSError): self.api.save(self.encounter, before)
        self.assertEqual(self.api.load(self.encounter), before)


if __name__ == '__main__': unittest.main()
