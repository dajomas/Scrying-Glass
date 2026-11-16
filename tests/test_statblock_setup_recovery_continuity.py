"""2C.3c destination ledger and recovery continuity after protected transfers.

Native fixture seeding prepares historical content/markers; operations under test
use production protected Save As and recovery services. Not HTTP/network coverage.
"""
import copy
import json
from pathlib import Path
import unittest
import test_statblock_combined_setup_operations as combined
import test_statblock_stage2_contracts as contracts
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_restore import restore_bindings
from python.scrying_glass_statblock_revisions import MAX_REVISION, REVISION_FIELD


class SetupRecoveryContinuityTests(unittest.TestCase):
    setUp = combined.CombinedSetupOperationTests.setUp
    tearDown = combined.CombinedSetupOperationTests.tearDown
    encounter = combined.CombinedSetupOperationTests.encounter
    seed = combined.CombinedSetupOperationTests.seed
    stored = combined.CombinedSetupOperationTests.stored
    save = combined.CombinedSetupOperationTests.save
    dump = combined.CombinedSetupOperationTests.dump
    call = combined.CombinedSetupOperationTests.call
    assert_content = combined.CombinedSetupOperationTests.assert_content
    transfer = combined.CombinedSetupOperationTests.transfer
    runtime = combined.CombinedSetupOperationTests.runtime
    assert_private = combined.CombinedSetupOperationTests.assert_private
    assert_saved_sources = combined.CombinedSetupOperationTests.assert_saved_sources
    through_loaded_move = combined.CombinedSetupOperationTests.through_loaded_move
    secret = 'PRIVATE_2C_CONTINUITY'

    def checkpoint(self, name):
        return self.call('save_checkpoint', {'name':name})['id']

    def restore(self, ident):
        return self.call('restore_checkpoint', ident,
                         {'confirm':True,'revision':self.f.store.revision()})

    def reopen(self):
        db = self.c.STORAGE
        path = Path(db.connection.execute('PRAGMA database_list').fetchone()[2])
        db.close(); self.c.STORAGE = db.__class__(path); self.c.load_state()

    def assert_head(self, owner, binding, revision, expected):
        actual = PrivateEncounterStorage(self.c.STORAGE).load(owner)[PRIVATE_KEY]
        self.assertEqual(restore_bindings(self.c.STORAGE, owner)['m'], (binding,revision))
        self.assertEqual(actual['m']['revision'], revision)
        self.assert_content(actual['m'], expected['m'])
        self.assertEqual(self.c.STATE._statblocks, actual)
        self.assertFalse(self.c.STORAGE.connection.in_transaction)
        self.assert_private(self.c.public_state()); self.assert_private(self.c.display_state())
        self.assertNotIn(REVISION_FIELD, json.dumps(self.c.STATE))
        return copy.deepcopy(actual)

    def test_runtime_checkpoints_and_sequential_undo_after_copy_move_keep_advancing(self):
        sequence = self.through_loaded_move(); owner = sequence['runtime']
        binding, revision = restore_bindings(self.c.STORAGE, owner)['m']
        first = copy.deepcopy(self.c.STATE._statblocks); first_checkpoint = self.checkpoint('Runtime before')
        api = PrivateEncounterStorage(self.c.STORAGE); state = api.load(owner)
        state[PRIVATE_KEY]['m'] = contracts.reference_snapshot(self.secret+' runtime replacement')
        state['monsters'][0]['hp'] = 4
        api.save(owner, state, runtime=True); self.c.load_state()
        second = copy.deepcopy(self.c.STATE._statblocks); second_checkpoint = self.checkpoint('Runtime after')
        self.assertEqual(second['m']['revision'], revision+1)
        actions = [(first_checkpoint,first,7), (second_checkpoint,second,4), (None,first,7), (None,second,4)]
        revision = second['m']['revision']
        for checkpoint, expected, hp in actions:
            with self.subTest(checkpoint=checkpoint, expected=expected['m']['source_label']):
                if checkpoint is None:
                    undo = self.f.summary()['undo']; self.assertIsNotNone(undo)
                    self.call('undo', {'id':undo['id']})
                else:
                    self.restore(checkpoint)
                revision += 1
                self.assert_head(owner, binding, revision, expected)
                self.assertIsNone(self.c.active_setup_reference())
                self.assertEqual(self.c.STATE['monsters'][0]['hp'], hp)
                self.assert_saved_sources(sequence)
        self.assertIsNone(self.f.summary()['undo'])
        for ident, expected in ((first_checkpoint,first), (second_checkpoint,second)):
            self.assertEqual(self.f.store.load(ident, sequence['source'], 'checkpoint')._statblocks, expected)
        final = copy.deepcopy(self.c.STATE._statblocks); feature_revision = self.f.store.revision()
        self.reopen(); self.assertEqual(self.runtime(), owner)
        self.assertEqual(self.c.STATE._statblocks, final); self.assertEqual(self.f.store.revision(), feature_revision)
        self.assert_head(owner, binding, revision, second); self.assert_saved_sources(sequence)
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])

    def test_overwrite_same_owner_stale_save_checkpoint_and_undo_keep_destination_history(self):
        sequence = self.through_loaded_move(); db = self.c.STORAGE
        db.save_setup(sequence['source'], 'continuity-target', self.c.setup_snapshot(self.c.STATE))
        owner = self.encounter(name='continuity-target'); api = PrivateEncounterStorage(db)
        for index in range(4):
            state = api.load(owner); state[PRIVATE_KEY]['m'] = contracts.reference_snapshot(self.secret+' historical '+str(index))
            api.save(owner, state)
        binding, head = restore_bindings(db, owner)['m']; self.assertEqual(head, 4)
        old = copy.deepcopy(self.stored(name='continuity-target'))
        image = self.c.load_setup_state('continuity-target', sequence['source'])
        image['active_setup'] = {'campaign_id':sequence['source'],'name':'continuity-target'}
        checkpoint = self.f.store.save_snapshot(sequence['source'], image, 'checkpoint', 'Destination history')
        self.save('continuity-target')
        overwritten = self.assert_head(owner, binding, 5, sequence['first'])
        self.save('continuity-target'); self.assertEqual(self.stored(name='continuity-target'), overwritten)
        value = self.c.STATE._statblocks['m']; value.pop('content_digest', None)
        value['source_label'] = self.secret+' same-owner edit'
        self.save('continuity-target'); current = copy.deepcopy(self.stored(name='continuity-target'))
        self.assert_head(owner, binding, 6, current)
        self.c.STATE._statblocks = copy.deepcopy(overwritten)
        before = self.dump(); live = copy.deepcopy(self.c.STATE)
        with self.assertRaisesRegex(ValueError, 'Stale'): self.save('continuity-target')
        self.assertEqual(self.dump(), before); self.assertEqual(dict(self.c.STATE), dict(live))
        self.assertEqual(self.c.STATE._statblocks, live._statblocks)
        self.assertEqual(self.stored(name='continuity-target'), current)
        self.c.load_state(); self.restore(checkpoint)
        self.assert_head(owner, binding, 7, old)
        undo = self.f.summary()['undo']; self.assertIsNotNone(undo)
        self.call('undo', {'id':undo['id']}); final = self.assert_head(owner, binding, 8, current)
        self.assertEqual(self.f.store.load(checkpoint, sequence['source'], 'checkpoint')._statblocks, old)
        self.assert_saved_sources(sequence)
        self.reopen(); self.assertEqual(self.c.STATE._statblocks, final)
        self.assertEqual(self.c.active_setup_reference()['name'], 'continuity-target')
        self.assert_head(owner, binding, 8, current); self.assert_saved_sources(sequence)
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])

    def test_counter_only_overwrite_after_reopen_advances_and_exhaustion_rolls_back(self):
        sequence = self.through_loaded_move(); db = self.c.STORAGE
        db.save_setup(sequence['source'], 'ledger-target', self.c.setup_snapshot(self.c.STATE))
        owner = self.encounter(name='ledger-target'); binding = restore_bindings(db, owner)['m'][0]
        with db.transaction(): db._record_statblock_revision(binding, 7)
        self.assertEqual(self.stored(name='ledger-target'), {})
        self.reopen(); db = self.c.STORAGE
        self.assertEqual(restore_bindings(db, owner)['m'], (binding,7))
        self.assertEqual(self.stored(name='ledger-target'), {})
        self.save('ledger-target'); current = self.assert_head(owner, binding, 8, sequence['first'])
        db.save_setup(sequence['source'], 'exhausted-target', self.c.setup_snapshot(self.c.STATE))
        exhausted = self.encounter(name='exhausted-target'); exhausted_binding = restore_bindings(db, exhausted)['m'][0]
        with db.transaction(): db._record_statblock_revision(exhausted_binding, MAX_REVISION)
        before = self.dump(); live = copy.deepcopy(self.c.STATE); feature_revision = self.f.store.revision()
        with self.assertRaisesRegex(ValueError, 'revision limit reached'): self.save('exhausted-target')
        self.assertEqual(self.dump(), before); self.assertEqual(dict(self.c.STATE), dict(live))
        self.assertEqual(self.c.STATE._statblocks, live._statblocks)
        self.assertEqual(self.f.store.revision(), feature_revision)
        self.assertEqual(self.c.active_setup_reference()['name'], 'ledger-target')
        self.assertEqual(self.stored(name='exhausted-target'), {})
        self.assertEqual(restore_bindings(db, exhausted)['m'], (exhausted_binding,MAX_REVISION))
        self.assertFalse(db.connection.in_transaction)
        self.assertFalse(self.c._database_broadcast_pending); self.assertFalse(self.c._defer_database_broadcast)
        self.assert_saved_sources(sequence)
        self.reopen(); self.assertEqual(self.c.STATE._statblocks, current)
        self.assert_head(owner, binding, 8, sequence['first'])
        self.assertEqual(self.stored(name='exhausted-target'), {})
        self.assertEqual(restore_bindings(self.c.STORAGE, exhausted)['m'], (exhausted_binding,MAX_REVISION))
        self.assert_saved_sources(sequence)
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])


if __name__ == '__main__': unittest.main()
