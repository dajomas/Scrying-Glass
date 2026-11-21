"""2C.2c.2 loaded-move native fixtures; not authenticated HTTP coverage."""
import asyncio
import copy
from pathlib import Path
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import test_statblock_private_transaction_saves as fixtures
from test_statblock_stage2_contracts import reference_snapshot
from python.scrying_glass_admin_campaigns import AdminCampaignsMixin
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_revisions import MAX_REVISION
from python.scrying_glass_statblock_restore import restore_bindings


class LoadedSetupMoveTests(unittest.TestCase):
    setUp = fixtures.PrivateTransactionSaveTests.setUp
    tearDown = fixtures.PrivateTransactionSaveTests.tearDown
    encounter = fixtures.PrivateTransactionSaveTests.encounter
    seed = fixtures.PrivateTransactionSaveTests.seed
    stored = fixtures.PrivateTransactionSaveTests.stored

    def runtime(self):
        return self.c.STORAGE.connection.execute('SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()[0]

    def old_runtime(self):
        db = self.c.STORAGE
        db.set_value('runtime_state', {'monsters':[{'id':'m','hp':2}], 'active_setup':None})
        owner = self.runtime(); api = PrivateEncounterStorage(db)
        for index in range(3):
            state = api.load(owner); state[PRIVATE_KEY]['m'] = reference_snapshot('Obsolete ' + str(index))
            api.save(owner,state,runtime=True)
        return owner

    def move(self, target, name='default'):
        handler = AdminCampaignsMixin(); handler.context = self.c
        payload = SimpleNamespace(from_campaign=self.c.active_campaign(),setup=name,mode='move')
        return asyncio.run(transactional_handler(self.c,handler.add_setup_to_campaign)(target,payload))

    def dump(self):
        return '\n'.join(self.c.STORAGE.connection.iterdump())

    def test_loaded_move_keeps_saved_owner_and_creates_independent_runtime(self):
        self.seed('First'); saved = self.seed('Latest'); db = self.c.STORAGE
        source = self.c.active_campaign(); owner = self.encounter(); bindings = restore_bindings(db,owner)
        live = copy.deepcopy(self.c.STATE); old = self.old_runtime()
        target = db.create_campaign('Other','','now')
        db.save_setup(target,'default',{'monsters':[{'id':'existing','hp':1}]})
        occupied = db.load_setup(target,'default')
        result = self.move(target); runtime = self.runtime()
        self.assertEqual(result['setup'],'default-2'); self.assertEqual(self.c.active_campaign(),source)
        self.assertIsNone(self.c.active_setup_reference()); self.assertFalse(db.setup_exists(source,'default'))
        self.assertEqual(self.encounter(target,'default-2'),owner)
        self.assertEqual(restore_bindings(db,owner),bindings)
        self.assertEqual(self.stored(target,'default-2')['m'],saved)
        self.assertEqual(db.load_setup(target,'default'),occupied)
        self.assertNotIn(runtime,(old,owner)); self.assertIsNone(db.connection.execute('SELECT id FROM encounters WHERE id=?',(old,)).fetchone())
        current = PrivateEncounterStorage(db).load(runtime)[PRIVATE_KEY]['m']
        self.assertEqual(current['revision'],1); self.assertNotEqual(current['prepared_at'],saved['prepared_at'])
        for key in ('content_digest','definitions','nodes','facts','warnings','provenance'):
            self.assertEqual(current[key],saved[key])
        self.assertEqual(self.c.STATE._statblocks,{'m':current})
        self.assertEqual(self.c.STATE['monsters'],live['monsters'])
        self.assertNotEqual(restore_bindings(db,runtime)['m'][0],bindings['m'][0])
        async def edit_runtime():
            self.c.STATE['monsters'][0]['hp'] = 1
            self.c.STATE._statblocks['m'].pop('content_digest',None)
            self.c.STATE._statblocks['m']['source_label'] = 'Runtime edit'
        asyncio.run(transactional_handler(self.c,edit_runtime)())
        self.assertEqual(self.stored(target,'default-2')['m'],saved)
        expected = copy.deepcopy(self.c.STATE._statblocks)
        path = Path(db.connection.execute('PRAGMA database_list').fetchone()[2]); db.close()
        self.c.STORAGE = db.__class__(path); self.c.load_state()
        self.assertIsNone(self.c.active_setup_reference())
        self.assertEqual(self.c.STATE._statblocks,expected); self.assertEqual(self.c.STATE['monsters'][0]['hp'],1)
        self.c.STORAGE._check_foreign_keys()

    def test_counter_only_source_does_not_inherit_obsolete_runtime_content(self):
        db = self.c.STORAGE; owner = self.encounter(); self.c.load_state()
        monster = restore_bindings(db,owner)['m'][0]
        with db.transaction(): db._record_statblock_revision(monster,MAX_REVISION)
        old = self.old_runtime(); target = db.create_campaign('Other','','now')
        self.move(target); runtime = self.runtime()
        self.assertNotEqual(runtime,old); self.assertEqual(self.encounter(target),owner)
        self.assertEqual(db._statblock_revision_head(monster),MAX_REVISION)
        self.assertEqual(self.stored(target),{}); self.assertEqual(self.c.STATE._statblocks,{})
        self.assertEqual(PrivateEncounterStorage(db).load(runtime)[PRIVATE_KEY],{})
        self.assertEqual(restore_bindings(db,runtime)['m'][1],0)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks,{})

    def test_failure_after_detachment_restores_move_runtime_and_memory(self):
        self.seed(); db = self.c.STORAGE; old = self.old_runtime()
        target = db.create_campaign('Other','','now'); before = self.dump(); state = copy.deepcopy(self.c.STATE)
        seen = []
        async def fail_changed():
            seen.append(self.runtime()); raise OSError('injected after runtime detachment')
        self.c.broadcast = AsyncMock()
        with patch.object(self.c,'changed',side_effect=fail_changed):
            with self.assertRaises(OSError): self.move(target)
        self.assertEqual(len(seen),1); self.assertNotEqual(seen[0],old)
        self.assertEqual(self.dump(),before); self.assertEqual(dict(self.c.STATE),dict(state))
        self.assertEqual(self.c.STATE._statblocks,state._statblocks)
        self.c.broadcast.assert_not_awaited(); self.assertFalse(db.connection.in_transaction)

    def test_shared_runtime_binding_rejects_and_background_move_does_not_detach(self):
        self.seed(); db = self.c.STORAGE; owner = self.encounter()
        target = db.create_campaign('Other','','now')
        with db.transaction(): db.connection.execute('UPDATE application_state SET runtime_encounter_id=? WHERE id=1',(owner,))
        before = self.dump(); state = copy.deepcopy(self.c.STATE)
        with self.assertRaisesRegex(ValueError,'shared'): self.move(target)
        self.assertEqual(self.dump(),before); self.assertEqual(self.c.STATE._statblocks,state._statblocks)
        with db.transaction(): db.connection.execute('UPDATE application_state SET runtime_encounter_id=NULL WHERE id=1')
        db.save_setup(self.c.active_campaign(),'background',{'monsters':[{'id':'n','hp':2}]})
        before = copy.deepcopy(self.c.STATE)
        with patch('python.scrying_glass_statblock_detaching.detach_loaded_setup',side_effect=AssertionError('background detach')):
            self.move(target,'background')
        self.assertIsNone(self.runtime()); self.assertEqual(dict(self.c.STATE),dict(before))
        self.assertEqual(self.c.STATE._statblocks,before._statblocks)


if __name__ == '__main__': unittest.main()
