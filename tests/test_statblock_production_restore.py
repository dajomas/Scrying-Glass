"""Production recovery service tests; no authenticated HTTP/browser claims."""
import copy
import json
import unittest
from unittest.mock import AsyncMock, patch
import test_statblock_stage2_contracts as contracts
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_restore import restore_encounter


class ProductionRestoreTests(unittest.TestCase):
    setUp = contracts.StatblockStage2ContractTests.setUp
    tearDown = contracts.StatblockStage2ContractTests.tearDown
    call = contracts.StatblockStage2ContractTests.call
    item = contracts.StatblockStage2ContractTests.item
    encounter = contracts.StatblockStage2ContractTests.encounter
    stored = contracts.StatblockStage2ContractTests.stored
    seed = contracts.StatblockStage2ContractTests.seed
    assert_content = contracts.StatblockStage2ContractTests.assert_content

    def checkpoint(self, name):
        return self.call('save_checkpoint', {'name':name})['id']

    def restore(self, ident):
        return self.call('restore_checkpoint', ident, {'confirm':True,'revision':self.f.store.revision()})

    def chain(self):
        first = self.seed(); a = self.checkpoint('First')
        second = self.seed('Second'); b = self.checkpoint('Second')
        self.restore(a); self.restore(b)
        return first, second

    def test_checkpoint_calls_kernel_and_refreshes_live_metadata(self):
        original = self.seed(); ident = self.checkpoint('Before'); latest = self.seed('Latest')
        with patch('python.scrying_glass_statblock_restore.restore_encounter', wraps=restore_encounter) as kernel:
            self.restore(ident)
        self.assertEqual(kernel.call_count, 1)
        self.assert_content(self.stored()['m'], original)
        self.assertGreater(self.stored()['m']['revision'], latest['revision'])
        self.assertEqual(self.c.STATE._statblocks, self.stored())
        self.assertNotIn(PRIVATE_KEY, json.dumps(self.c.public_state()))
        self.assertNotIn('Retain this supporting rule.', json.dumps(self.c.display_state()))

    def test_two_private_replacements_can_be_undone_in_sequence(self):
        first, second = self.chain(); revision = self.stored()['m']['revision']
        self.call('undo', {'id':self.f.summary()['undo']['id']})
        self.assert_content(self.stored()['m'], first)
        self.assertGreater(self.stored()['m']['revision'], revision)
        self.assertIsNotNone(self.f.summary()['undo'])
        self.call('undo', {'id':self.f.summary()['undo']['id']})
        self.assert_content(self.stored()['m'], second)
        self.assertEqual(self.c.STATE._statblocks, self.stored())

    def test_mismatched_undo_predecessor_is_not_rebased(self):
        self.chain(); entries = self.f.store.list(self.c.active_campaign(), 'undo')
        predecessor = entries[1]['id']; bad = '0'*64
        with self.c.STORAGE.transaction():
            self.c.STORAGE.connection.execute('UPDATE encounter_snapshots SET after_digest=? WHERE id=?', (bad, predecessor))
        self.call('undo', {'id':self.f.summary()['undo']['id']})
        self.assertEqual(self.f.store.latest_undo(self.c.active_campaign())['after_digest'], bad)
        self.assertIsNone(self.f.summary()['undo'])

    def test_tracker_undo_preserves_existing_private_metadata(self):
        original = self.seed()
        self.call('edit_features', 'm', {'temp_hp':7})
        self.call('edit_features', 'm', {'hp_delta':-2})
        for _ in range(2): self.call('undo', {'id':self.f.summary()['undo']['id']})
        self.assertEqual(self.stored()['m'], original)
        self.assertEqual(self.item()['hp'], 12)

    def test_clear_rejection_rolls_back_memory_content_revision_and_history(self):
        ident = self.checkpoint('Empty'); self.seed('Added later')
        before = copy.deepcopy(self.c.STATE); content = self.stored(); revision = self.f.store.revision()
        history = self.f.store.list(self.c.active_campaign(), 'undo'); self.c.broadcast = AsyncMock()
        with self.assertRaises(self.c.HTTPException) as caught: self.restore(ident)
        self.assertEqual(caught.exception.status_code, 409)
        self.assertEqual(self.c.STATE, before); self.assertEqual(self.c.STATE._statblocks, before._statblocks)
        self.assertEqual(self.stored(), content); self.assertEqual(self.f.store.revision(), revision)
        self.assertEqual(self.f.store.list(self.c.active_campaign(), 'undo'), history)
        self.c.broadcast.assert_not_awaited()

    def test_late_runtime_save_failure_rolls_back_kernel_write(self):
        self.seed(); ident = self.checkpoint('Original'); self.seed('Current')
        before = copy.deepcopy(self.c.STATE); content = self.stored(); revision = self.f.store.revision()
        self.c.broadcast = AsyncMock()
        with patch.object(self.c, 'save_state', side_effect=OSError('injected')):
            with self.assertRaises(OSError): self.restore(ident)
        self.assertEqual(self.c.STATE._statblocks, before._statblocks); self.assertEqual(self.c.STATE, before)
        self.assertEqual(self.stored(), content); self.assertEqual(self.f.store.revision(), revision)
        self.assertFalse(self.c.STORAGE.connection.in_transaction); self.c.broadcast.assert_not_awaited()

    def test_unsaved_runtime_restore_does_not_modify_saved_setup(self):
        setup = self.seed(); self.c.clear_active_setup(); db = self.c.STORAGE
        encounter = db.connection.execute('SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()[0]
        api = PrivateEncounterStorage(db); state = copy.deepcopy(dict(self.c.STATE)); state['characters'] = []
        state[PRIVATE_KEY] = {'m':contracts.reference_snapshot('Runtime original')}
        original = api.save(encounter, state, runtime=True)[PRIVATE_KEY]['m']
        self.c.save_state(); self.c.load_state(); ident = self.checkpoint('Runtime')
        state = api.load(encounter); state[PRIVATE_KEY]['m'] = contracts.reference_snapshot('Runtime changed')
        current = api.save(encounter, state, runtime=True)[PRIVATE_KEY]['m']; self.c.load_state()
        self.restore(ident)
        self.assertIsNone(self.c.STATE['active_setup'])
        self.assert_content(api.load(encounter)[PRIVATE_KEY]['m'], original)
        self.assertGreater(self.c.STATE._statblocks['m']['revision'], current['revision'])
        self.assertEqual(self.stored()['m'], setup)




if __name__ == '__main__': unittest.main()
