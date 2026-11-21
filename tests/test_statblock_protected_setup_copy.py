"""2C.2c.1 protected copy tests; native fixture execution pending.

Gate-denial injection tests routing, not real authenticated HTTP authorization.
Loaded moves and Save As are outside this increment.
"""
import asyncio
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import test_statblock_private_transaction_saves as fixtures
from python.scrying_glass_admin_campaigns import AdminCampaignsMixin
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_statblock_cloning import clone_private_snapshots
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_restore import restore_bindings


class ProtectedSetupCopyTests(unittest.TestCase):
    setUp = fixtures.PrivateTransactionSaveTests.setUp
    tearDown = fixtures.PrivateTransactionSaveTests.tearDown
    encounter = fixtures.PrivateTransactionSaveTests.encounter
    seed = fixtures.PrivateTransactionSaveTests.seed
    stored = fixtures.PrivateTransactionSaveTests.stored

    def transfer(self, target):
        handler = AdminCampaignsMixin(); handler.context = self.c
        payload = SimpleNamespace(from_campaign=self.c.active_campaign(), setup='default', mode='copy')
        return asyncio.run(transactional_handler(self.c, handler.add_setup_to_campaign)(target,payload))

    def dump(self):
        return '\n'.join(self.c.STORAGE.connection.iterdump())

    def test_protected_copy_keeps_live_source_and_loads_independent_destination(self):
        self.seed('First'); expected = self.seed('Latest')
        db = self.c.STORAGE; source = self.c.active_campaign(); source_owner = self.encounter()
        target = db.create_campaign('Other', '', 'now')
        db.save_setup(target, 'default', {'monsters':[{'id':'existing','hp':1}]})
        occupied = db.load_setup(target,'default'); before = copy.deepcopy(self.c.STATE)
        bindings = restore_bindings(db,source_owner)
        result = self.transfer(target)
        self.assertEqual((result['setup'],result['campaign'],result['mode']), ('default-2',target,'copy'))
        self.assertEqual(self.c.active_campaign(), source)
        self.assertEqual(dict(self.c.STATE), dict(before))
        self.assertEqual(self.c.STATE._statblocks, before._statblocks)
        self.assertEqual(self.stored()['m'], expected)
        self.assertEqual(restore_bindings(db,source_owner), bindings)
        self.assertEqual(db.load_setup(target,'default'), occupied)
        destination = self.encounter(target,result['setup'])
        self.assertNotEqual(destination,source_owner)
        self.assertNotEqual(restore_bindings(db,destination)['m'][0], bindings['m'][0])
        loaded = self.c.load_setup_state(result['setup'],target)
        self.assertEqual(loaded._statblocks, self.stored(target,result['setup']))
        self.assertEqual(loaded._statblocks['m']['revision'],1)
        self.assertNotEqual(loaded._statblocks['m']['prepared_at'],expected['prepared_at'])
        for key in ('content_digest','definitions','nodes','facts','warnings','provenance'):
            self.assertEqual(loaded._statblocks['m'][key], expected[key])
        self.assertEqual(self.c.STATE._statblocks, before._statblocks)
        self.assertEqual(dict(self.c.STATE), dict(before))
        db._check_foreign_keys()

    def test_failure_after_real_clone_rolls_back_destination_and_live_source(self):
        self.seed(); db = self.c.STORAGE; target = db.create_campaign('Other', '', 'now')
        before = self.dump(); state = copy.deepcopy(self.c.STATE); observed = []
        def fail_after_clone(storage, source, destination):
            clone_private_snapshots(storage,source,destination)
            observed.append(PrivateEncounterStorage(storage).load(destination)[PRIVATE_KEY]['m']['revision'])
            raise OSError('injected after private clone')
        with patch('python.scrying_glass_statblock_cloning.clone_private_snapshots', side_effect=fail_after_clone):
            with self.assertRaises(OSError): self.transfer(target)
        self.assertEqual(observed,[1]); self.assertEqual(self.dump(),before)
        self.assertEqual(dict(self.c.STATE),dict(state))
        self.assertEqual(self.c.STATE._statblocks,state._statblocks)
        self.assertFalse(db.connection.in_transaction)

    def test_denied_campaign_gate_never_calls_storage_transfer(self):
        self.seed(); db = self.c.STORAGE; source = self.c.active_campaign()
        target = db.create_campaign('Other', '', 'now'); require = self.c.require_campaign
        for denied in (target,source):
            with self.subTest(denied=denied):
                before = self.dump(); state = copy.deepcopy(self.c.STATE)
                def require_allowed(campaign):
                    if campaign == denied: raise self.c.HTTPException(403,'injected denied campaign')
                    return require(campaign)
                with patch.object(self.c,'require_campaign',side_effect=require_allowed), patch.object(db,'transfer_setup',wraps=db.transfer_setup) as transfer:
                    with self.assertRaises(self.c.HTTPException) as error: self.transfer(target)
                    self.assertEqual(error.exception.status_code,403); transfer.assert_not_called()
                self.assertEqual(self.dump(),before)
                self.assertEqual(dict(self.c.STATE),dict(state))
                self.assertEqual(self.c.STATE._statblocks,state._statblocks)


if __name__ == '__main__': unittest.main()
