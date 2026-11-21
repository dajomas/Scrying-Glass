"""2C.3b protected save integration; native execution pending."""
import asyncio
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import test_statblock_private_transaction_saves as fixtures
from test_statblock_stage2_contracts import reference_snapshot
from python.scrying_glass_admin_setups import AdminSetupsMixin
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_restore import restore_bindings


class SetupSavingIntegrationTests(unittest.TestCase):
    setUp = fixtures.PrivateTransactionSaveTests.setUp
    tearDown = fixtures.PrivateTransactionSaveTests.tearDown
    encounter = fixtures.PrivateTransactionSaveTests.encounter
    seed = fixtures.PrivateTransactionSaveTests.seed
    stored = fixtures.PrivateTransactionSaveTests.stored

    def save(self,name):
        handler = AdminSetupsMixin(); handler.context = self.c
        payload = SimpleNamespace(name=name,campaign=self.c.active_campaign())
        return asyncio.run(transactional_handler(self.c,handler.save_setup)(payload))

    def dump(self):
        return '\n'.join(self.c.STORAGE.connection.iterdump())

    def test_new_save_as_uses_live_content_and_refreshes_destination_metadata(self):
        self.seed('First'); original = self.seed('Latest'); before = self.stored()
        source = self.encounter(); bindings = restore_bindings(self.c.STORAGE,source)
        self.c.STATE['monsters'][0]['hp'] = 1
        self.c.STATE._statblocks['m'].pop('content_digest',None)
        self.c.STATE._statblocks['m']['source_label'] = 'Unsaved edit'
        result = self.save('saved-as'); destination = self.encounter(name='saved-as')
        self.assertEqual(result['name'],'saved-as'); self.assertNotEqual(destination,source)
        saved = self.stored(name='saved-as'); self.assertEqual(saved['m']['revision'],1)
        self.assertEqual(saved['m']['source_label'],'Unsaved edit')
        self.assertNotEqual(saved['m']['prepared_at'],original['prepared_at'])
        self.assertEqual(self.c.STATE._statblocks,saved)
        self.assertEqual(restore_bindings(self.c.STORAGE,source),bindings)
        self.assertEqual(self.stored(),before)
        self.assertEqual(self.c.active_setup_reference()['name'],'saved-as')
        self.assertEqual(self.c.read_campaigns()['campaigns'][self.c.active_campaign()]['last_setup'],'saved-as')
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks,saved)
        self.assertEqual(self.c.STATE['monsters'][0]['hp'],1)

    def test_unsaved_runtime_can_be_saved_to_a_new_destination(self):
        self.seed(); self.c.clear_active_setup(); self.c.save_state()
        self.c.STATE._statblocks['m'].pop('content_digest',None)
        self.c.STATE._statblocks['m']['source_label'] = 'Runtime live edit'
        before = self.stored(); self.save('from-runtime')
        saved = self.stored(name='from-runtime')
        self.assertEqual(saved['m']['source_label'],'Runtime live edit')
        self.assertEqual(saved['m']['revision'],1); self.assertEqual(self.stored(),before)
        self.assertEqual(self.c.STATE._statblocks,saved)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks,saved)

    def test_ordinary_save_keeps_owner_history_and_detects_stale_metadata(self):
        original = self.seed(); owner = self.encounter(); binding = restore_bindings(self.c.STORAGE,owner)['m'][0]
        self.save('default'); self.assertEqual(self.stored()['m'],original)
        self.c.STATE._statblocks['m'].pop('content_digest',None)
        self.c.STATE._statblocks['m']['source_label'] = 'Ordinary edit'
        self.save('default'); current = self.stored()['m']
        self.assertEqual(current['revision'],original['revision']+1)
        self.assertEqual(restore_bindings(self.c.STORAGE,owner)['m'][0],binding)
        self.assertEqual(self.c.STATE._statblocks,{'m':current})
        self.c.STATE._statblocks['m'] = copy.deepcopy(original); before = self.dump()
        with self.assertRaisesRegex(ValueError,'Stale'): self.save('default')
        self.assertEqual(self.dump(),before)

    def test_other_existing_destination_preserves_its_revision_history(self):
        self.seed('First'); self.seed('Source'); source = self.encounter(); original = self.stored()
        db = self.c.STORAGE; campaign = self.c.active_campaign()
        db.save_setup(campaign,'existing',self.c.setup_snapshot(self.c.STATE))
        destination = self.encounter(name='existing'); api = PrivateEncounterStorage(db)
        for index in range(4):
            state = api.load(destination); state[PRIVATE_KEY]['m'] = reference_snapshot('Target '+str(index)); api.save(destination,state)
        binding = restore_bindings(db,destination)['m']; self.save('existing')
        saved = self.stored(name='existing')['m']
        self.assertEqual(saved['content_digest'],original['m']['content_digest'])
        self.assertEqual(saved['revision'],binding[1]+1)
        self.assertEqual(restore_bindings(db,destination)['m'][0],binding[0])
        self.assertEqual(self.encounter(name='existing'),destination)
        self.assertEqual(self.c.STATE._statblocks,{'m':saved})
        self.assertEqual(PrivateEncounterStorage(db).load(source)[PRIVATE_KEY],original)

    def test_private_omission_does_not_clear_existing_destination(self):
        self.seed(); self.c.STATE._statblocks = {}; before = self.dump()
        with self.assertRaisesRegex(ValueError,'Omitted'): self.save('default')
        self.assertEqual(self.dump(),before); self.assertEqual(self.c.STATE._statblocks,{})

    def test_failures_after_roster_or_live_refresh_roll_back_new_destination(self):
        self.seed(); save_roster = self.c.save_campaign_characters
        for stage in ('roster','changed'):
            with self.subTest(stage=stage):
                before = self.dump(); state = copy.deepcopy(self.c.STATE)
                def fail_roster(*args): save_roster(*args); raise OSError('injected after roster')
                async def fail_changed():
                    self.assertEqual(self.c.active_setup_reference()['name'],'failed')
                    self.assertEqual(self.c.STATE._statblocks,self.stored(name='failed'))
                    raise OSError('injected after live metadata refresh')
                attribute, replacement = ('save_campaign_characters',fail_roster) if stage=='roster' else ('changed',fail_changed)
                with patch.object(self.c,attribute,side_effect=replacement):
                    with self.assertRaises(OSError): self.save('failed')
                self.assertEqual(self.dump(),before); self.assertEqual(dict(self.c.STATE),dict(state))
                self.assertEqual(self.c.STATE._statblocks,state._statblocks)
                self.assertFalse(self.c.STORAGE.connection.in_transaction)


if __name__ == '__main__': unittest.main()
