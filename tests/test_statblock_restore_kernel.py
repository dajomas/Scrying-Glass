"""2B.2 replacement-kernel tests, not service restoration or explicit-clear support."""
import copy
import unittest
from unittest.mock import patch
import test_statblock_stage2_contracts as contracts
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_loading import PrivateEncounterState
from python.scrying_glass_statblock_restore import restore_bindings, restore_encounter


class RestoreKernelTests(unittest.TestCase):
    setUp = contracts.StatblockStage2ContractTests.setUp
    tearDown = contracts.StatblockStage2ContractTests.tearDown
    encounter = contracts.StatblockStage2ContractTests.encounter
    seed = contracts.StatblockStage2ContractTests.seed
    stored = contracts.StatblockStage2ContractTests.stored
    assert_content = contracts.StatblockStage2ContractTests.assert_content

    def bindings(self, state):
        return restore_bindings(self.c.STORAGE, self.encounter(), [m['id'] for m in state['monsters']])

    def restore(self, state, bindings=None):
        return restore_encounter(self.c.STORAGE, self.encounter(), state,
            expected_bindings=self.bindings(state) if bindings is None else bindings)

    def test_historical_replacement_uses_new_destination_revision_and_tracker_values(self):
        original = self.seed(); image = copy.deepcopy(self.c.STATE)
        replacement = self.seed('Replacement'); image['monsters'][0]['hp'] = 5
        result = self.restore(image)
        self.assert_content(result[PRIVATE_KEY]['m'], original)
        self.assertEqual(result[PRIVATE_KEY]['m']['revision'], replacement['revision'] + 1)
        self.assertEqual(result['monsters'][0]['hp'], 5)
        self.assertEqual(image._statblocks['m'], original)

    def test_identical_content_keeps_current_metadata(self):
        expected = self.seed(); image = copy.deepcopy(self.c.STATE)
        image._statblocks['m']['revision'] += 100
        result = self.restore(image)
        self.assertEqual(result[PRIVATE_KEY]['m'], expected)

    def test_surviving_content_clear_is_rejected_before_tracker_writes(self):
        self.seed(); image = PrivateEncounterState(copy.deepcopy(dict(self.c.STATE)), {})
        before = PrivateEncounterStorage(self.c.STORAGE).load(self.encounter()); bindings = self.bindings(image)
        with patch.object(self.c.STORAGE, '_save_encounter', side_effect=AssertionError('must not write')):
            with self.assertRaisesRegex(ValueError, 'clearing is not enabled'):
                self.restore(image, bindings)
        self.assertEqual(PrivateEncounterStorage(self.c.STORAGE).load(self.encounter()), before)

    def test_stale_revision_rejects_before_tracker_writes(self):
        self.seed(); image = copy.deepcopy(self.c.STATE); bindings = self.bindings(image)
        latest = self.seed('Latest')
        with patch.object(self.c.STORAGE, '_save_encounter', side_effect=AssertionError('must not write')):
            with self.assertRaisesRegex(ValueError, 'Stale'): self.restore(image, bindings)
        self.assertEqual(self.stored()['m'], latest)

    def test_another_encounters_equal_combatant_id_is_not_a_valid_binding(self):
        self.seed(); image = copy.deepcopy(self.c.STATE); campaign = self.c.active_campaign()
        self.c.STORAGE.save_setup(campaign, 'other', {'monsters':[{'id':'m','hp':9}]})
        other = self.encounter(campaign, 'other')
        foreign = restore_bindings(self.c.STORAGE, other)
        with self.assertRaisesRegex(ValueError, 'Stale'): self.restore(image, foreign)
        self.assertEqual(self.c.STORAGE.load_setup(campaign, 'other')['monsters'][0]['hp'], 9)

    def test_failed_content_write_rolls_back_tracker_and_reference_content(self):
        self.seed(); image = copy.deepcopy(self.c.STATE); self.seed('Current')
        image['monsters'][0]['hp'] = 1
        api = PrivateEncounterStorage(self.c.STORAGE); before = api.load(self.encounter())
        bindings = self.bindings(image)
        with patch('python.scrying_glass_statblock_storage.StatblockStorage.save', side_effect=OSError('injected')):
            with self.assertRaises(OSError): self.restore(image, bindings)
        self.assertEqual(api.load(self.encounter()), before)
        self.assertFalse(self.c.STORAGE.connection.in_transaction)

    def test_removed_monster_cascades_without_a_surviving_clear(self):
        self.seed(); image = PrivateEncounterState(copy.deepcopy(dict(self.c.STATE)), {})
        image['monsters'] = []
        result = self.restore(image)
        self.assertEqual(result['monsters'], []); self.assertEqual(result[PRIVATE_KEY], {})

    def test_raw_dictionary_is_not_an_authoritative_restore_image(self):
        self.seed()
        with self.assertRaises(ValueError): self.restore(dict(self.c.STATE))

    def test_invalid_graph_is_rejected_before_restoration_transaction(self):
        self.seed(); image = copy.deepcopy(self.c.STATE); bindings = self.bindings(image)
        image._statblocks['m']['model_version'] = 99
        with patch.object(self.c.STORAGE, 'transaction', side_effect=AssertionError('must validate first')):
            with self.assertRaises(ValueError): self.restore(image, bindings)


if __name__ == '__main__': unittest.main()
