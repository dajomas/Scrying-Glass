"""First 2C.3c slice: combined native protected operations, not HTTP acceptance.

Each handler call owns its transaction. A failed final Save As must not roll back
already committed copy/move operations. Native execution is delegated to CI.
"""
import asyncio
import copy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import test_statblock_setup_saving as saving
import test_statblock_stage2_contracts as contracts
from python.scrying_glass_admin_campaigns import AdminCampaignsMixin
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_restore import restore_bindings


class CombinedSetupOperationTests(unittest.TestCase):
    setUp = saving.SetupSavingIntegrationTests.setUp
    tearDown = saving.SetupSavingIntegrationTests.tearDown
    encounter = saving.SetupSavingIntegrationTests.encounter
    seed = saving.SetupSavingIntegrationTests.seed
    stored = saving.SetupSavingIntegrationTests.stored
    save = saving.SetupSavingIntegrationTests.save
    dump = saving.SetupSavingIntegrationTests.dump
    call = contracts.StatblockStage2ContractTests.call
    assert_content = contracts.StatblockStage2ContractTests.assert_content
    secret = 'PRIVATE_2C_SEQUENCE'

    def transfer(self, target, name, mode):
        handler = AdminCampaignsMixin(); handler.context = self.c
        payload = SimpleNamespace(from_campaign=self.c.active_campaign(), setup=name, mode=mode)
        return asyncio.run(transactional_handler(self.c, handler.add_setup_to_campaign)(target, payload))

    def runtime(self):
        return self.c.STORAGE.connection.execute(
            'SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()[0]

    def assert_private(self, value):
        text = json.dumps(value)
        for marker in (self.secret, 'Retain this supporting rule.', PRIVATE_KEY, 'content_digest'):
            self.assertNotIn(marker, text)

    def assert_saved_sources(self, sequence):
        db = self.c.STORAGE
        for campaign, name, owner, metadata, bindings in sequence['saved']:
            self.assertEqual(self.encounter(campaign, name), owner)
            self.assertEqual(self.stored(campaign, name), metadata)
            self.assertEqual(restore_bindings(db, owner), bindings)
        checkpoint = self.f.store.load(sequence['checkpoint'], sequence['source'], 'checkpoint')
        self.assertEqual(checkpoint._statblocks, sequence['original'])
        moved_checkpoint = self.f.store.load(sequence['moved_checkpoint'], sequence['source'], 'checkpoint')
        self.assertEqual(moved_checkpoint._statblocks, sequence['first'])

    def through_loaded_move(self):
        db = self.c.STORAGE; source = self.c.active_campaign()
        self.seed(self.secret+' earlier'); self.seed(self.secret+' source')
        original = copy.deepcopy(self.stored()); original_owner = self.encounter()
        original_bindings = restore_bindings(db, original_owner)
        checkpoint = self.call('save_checkpoint', {'name':'Before sequence'})['id']
        self.c.STATE['monsters'][0]['hp'] = 7
        self.c.STATE._statblocks['m'].pop('content_digest', None)
        self.c.STATE._statblocks['m']['source_label'] = self.secret+' live Save As'
        result = self.save('sequence-first'); self.assert_private(result)
        self.assertEqual(result, {'name':'sequence-first', 'campaign':source})
        first_owner = self.encounter(name='sequence-first'); first = copy.deepcopy(self.stored(name='sequence-first'))
        first_bindings = restore_bindings(db, first_owner)
        self.assertNotEqual(first_owner, original_owner)
        self.assertNotEqual(first_bindings['m'][0], original_bindings['m'][0])
        self.assertEqual(first['m']['revision'], 1)
        self.assertNotEqual(first['m']['prepared_at'], original['m']['prepared_at'])
        self.assertEqual(first['m']['source_label'], self.secret+' live Save As')
        for key in ('definitions','nodes','facts','warnings','provenance'):
            self.assertEqual(first['m'][key], original['m'][key])
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, first)
        moved_checkpoint = self.call('save_checkpoint', {'name':'Before moving Save As'})['id']
        target = db.create_campaign('Sequence destination', '', 'now')
        state = copy.deepcopy(self.c.STATE)
        copied = self.transfer(target, 'sequence-first', 'copy'); self.assert_private(copied)
        self.assertEqual(dict(self.c.STATE), dict(state)); self.assertEqual(self.c.STATE._statblocks, state._statblocks)
        copy_name = copied['setup']; copy_owner = self.encounter(target, copy_name)
        copy_metadata = copy.deepcopy(self.stored(target, copy_name)); copy_bindings = restore_bindings(db, copy_owner)
        self.assertNotEqual(copy_owner, first_owner)
        self.assertNotEqual(copy_bindings['m'][0], first_bindings['m'][0])
        self.assert_content(copy_metadata['m'], first['m']); self.assertEqual(copy_metadata['m']['revision'], 1)
        self.assertNotEqual(copy_metadata['m']['prepared_at'], first['m']['prepared_at'])
        moved = self.transfer(target, 'sequence-first', 'move'); self.assert_private(moved)
        self.assertNotEqual(moved['setup'], copy_name)
        self.assertFalse(db.setup_exists(source, 'sequence-first'))
        self.assertEqual(self.encounter(target, moved['setup']), first_owner)
        self.assertEqual(self.c.active_campaign(), source); self.assertIsNone(self.c.active_setup_reference())
        runtime = self.runtime(); self.assertNotIn(runtime, (original_owner, first_owner, copy_owner))
        runtime_metadata = PrivateEncounterStorage(db).load(runtime)[PRIVATE_KEY]
        self.assert_content(runtime_metadata['m'], first['m'])
        self.assertEqual(runtime_metadata['m']['revision'], 1)
        self.assertNotEqual(runtime_metadata['m']['prepared_at'], first['m']['prepared_at'])
        self.assertNotIn(restore_bindings(db, runtime)['m'][0],
                         (original_bindings['m'][0], first_bindings['m'][0], copy_bindings['m'][0]))
        self.assertEqual(self.c.STATE._statblocks, runtime_metadata)
        self.assertEqual(self.c.STATE['monsters'][0]['hp'], 7)
        self.assertIsNone(self.f.summary()['undo'])
        self.c.load_state(); self.assertIsNone(self.c.active_setup_reference())
        self.assertEqual(self.c.STATE._statblocks, runtime_metadata)
        sequence = dict(source=source, checkpoint=checkpoint, moved_checkpoint=moved_checkpoint,
            original=original, first=first, runtime=runtime, saved=[
                (source, 'default', original_owner, original, original_bindings),
                (target, copy_name, copy_owner, copy_metadata, copy_bindings),
                (target, moved['setup'], first_owner, first, first_bindings)])
        self.assert_saved_sources(sequence)
        return sequence

    def test_save_as_copy_loaded_move_runtime_save_as_keep_independent_owners(self):
        sequence = self.through_loaded_move(); db = self.c.STORAGE
        self.c.STATE['monsters'][0]['hp'] = 5
        self.c.STATE._statblocks['m'].pop('content_digest', None)
        self.c.STATE._statblocks['m']['source_label'] = self.secret+' runtime Save As'
        result = self.save('sequence-final'); self.assert_private(result)
        self.assertEqual(result, {'name':'sequence-final', 'campaign':sequence['source']})
        owner = self.encounter(name='sequence-final'); metadata = self.stored(name='sequence-final')
        self.assertNotIn(owner, [sequence['runtime'], *(row[2] for row in sequence['saved'])])
        self.assertEqual(metadata['m']['revision'], 1)
        self.assertEqual(metadata['m']['source_label'], self.secret+' runtime Save As')
        self.assertEqual(self.c.STATE._statblocks, metadata)
        self.assertEqual(self.c.active_setup_reference(), {'campaign_id':sequence['source'], 'name':'sequence-final'})
        self.assertEqual(self.c.read_campaigns()['campaigns'][sequence['source']]['last_setup'], 'sequence-final')
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, metadata)
        self.assertEqual(self.c.STATE['monsters'][0]['hp'], 5)
        self.assert_saved_sources(sequence)
        before = self.dump(); state = copy.deepcopy(self.c.STATE)
        with self.assertRaises(self.c.HTTPException) as raised:
            self.call('restore_checkpoint', sequence['moved_checkpoint'],
                      {'confirm':True, 'revision':self.f.store.revision()})
        self.assertEqual(raised.exception.status_code, 409)
        self.assertEqual(self.dump(), before); self.assertEqual(dict(self.c.STATE), dict(state))
        self.assertEqual(self.c.STATE._statblocks, state._statblocks)
        self.assert_private(self.c.public_state()); self.assert_private(self.c.display_state())
        self.assertEqual(list(db.connection.execute('PRAGMA foreign_key_check')), [])

    def test_final_save_as_late_history_failure_preserves_committed_sequence(self):
        sequence = self.through_loaded_move()
        self.call('edit_features', 'm', {'temp_hp':3})
        self.assertIsNotNone(self.f.summary()['undo'])
        before = self.dump(); state = copy.deepcopy(self.c.STATE); revision = self.f.store.revision()
        after = self.f.after_transaction; observed = []
        def fail_after_history(*args):
            after(*args)
            observed.append((self.c.STORAGE.connection.in_transaction,
                self.c.active_setup_reference()['name'], self.stored(name='sequence-failed')['m']['revision'],
                self.f.store.revision(), self.f.summary()['undo']))
            raise OSError('injected after final Save As history')
        with patch.object(self.f, 'after_transaction', side_effect=fail_after_history):
            with self.assertRaisesRegex(OSError, 'final Save As history'): self.save('sequence-failed')
        self.assertEqual(observed, [(True, 'sequence-failed', 1, revision+1, None)])
        self.assertEqual(self.dump(), before); self.assertEqual(dict(self.c.STATE), dict(state))
        self.assertEqual(self.c.STATE._statblocks, state._statblocks)
        self.assertFalse(self.c.STORAGE.setup_exists(sequence['source'], 'sequence-failed'))
        self.assertIsNone(self.c.active_setup_reference()); self.assertEqual(self.runtime(), sequence['runtime'])
        self.assert_saved_sources(sequence)
        self.assertFalse(self.c.STORAGE.connection.in_transaction)
        self.assertFalse(self.c._database_broadcast_pending); self.assertFalse(self.c._defer_database_broadcast)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, state._statblocks)
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])


if __name__ == '__main__': unittest.main()
