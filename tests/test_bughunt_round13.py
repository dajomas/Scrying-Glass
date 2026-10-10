"""Setup transfers must remain compatible with the destination roster."""
import asyncio
import copy
import types
import unittest
import test_encounter_features as fixture
from test_sqlite_storage import HTTPError
from python.scrying_glass_admin_campaigns import AdminCampaignsMixin
from python.scrying_glass_database_transactions import transactional_handler

class TransferDestinationIdentityTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown

    def prepare(self,kind='monsters',ident='c'):
        self.target=self.c.active_campaign()
        self.source=self.c.STORAGE.create_campaign('Source','','now')
        self.c.STORAGE.save_characters(self.source,[])
        item={'id':ident,'name':'Transferred participant'}
        if kind=='monsters':item['hp']=10
        state=self.c.normalize_state({kind:[item]})
        self.c.STORAGE.save_setup(self.source,'fight',self.c.setup_snapshot(state))

    def untouched(self,before_source,before_target,state):
        self.assertEqual(self.c.STORAGE.load_setup(self.source,'fight'),before_source)
        self.assertEqual(self.c.STORAGE.list_setups(self.target),before_target)
        self.assertEqual(self.c.STATE,state)
        self.assertTrue(self.c.STORAGE.campaign_exists(self.source))

    def reject_storage(self,mode,kind):
        self.prepare(kind)
        source=self.c.STORAGE.load_setup(self.source,'fight')
        target=self.c.STORAGE.list_setups(self.target);state=copy.deepcopy(self.c.STATE)
        with self.assertRaises(ValueError):self.c.STORAGE.transfer_setup(self.source,self.target,'fight',mode)
        self.untouched(source,target,state)

    def test_copy_rejects_monster_roster_collision(self):self.reject_storage('copy','monsters')
    def test_move_rejects_lair_roster_collision(self):self.reject_storage('move','lairs')

    def test_admin_transfer_conflict_returns_409_without_mutation(self):
        self.prepare()
        handler=AdminCampaignsMixin();handler.context=self.c
        payload=types.SimpleNamespace(setup='fight',from_campaign=self.source,mode='copy')
        source=self.c.STORAGE.load_setup(self.source,'fight')
        target=self.c.STORAGE.list_setups(self.target);state=copy.deepcopy(self.c.STATE)
        revision=self.c.features.store.revision()
        with self.assertRaises(HTTPError) as error:
            asyncio.run(transactional_handler(self.c,handler.add_setup_to_campaign)(self.target,payload))
        self.assertEqual(error.exception.status_code,409)
        self.untouched(source,target,state)
        self.assertEqual(self.c.features.store.revision(),revision)

    def test_campaign_delete_rolls_back_prior_moves_on_conflict(self):
        self.prepare()
        safe=self.c.normalize_state({'monsters':[{'id':'safe-id','name':'Safe','hp':5}]})
        self.c.STORAGE.save_setup(self.source,'a-safe',self.c.setup_snapshot(safe))
        before=self.c.read_campaigns();source=self.c.STORAGE.load_setup(self.source,'fight')
        target=self.c.STORAGE.list_setups(self.target);state=copy.deepcopy(self.c.STATE)
        handler=AdminCampaignsMixin();handler.context=self.c
        with self.assertRaises(HTTPError) as error:
            asyncio.run(transactional_handler(self.c,handler.delete_campaign)(self.source,move_to=self.target))
        self.assertEqual(error.exception.status_code,409)
        self.untouched(source,target,state)
        self.assertEqual(self.c.read_campaigns(),before)
        self.assertEqual(self.c.STORAGE.list_setups(self.source),['a-safe','fight'])

    def test_valid_transfer_loads_with_destination_roster(self):
        self.prepare(ident='new-monster')
        name=self.c.STORAGE.transfer_setup(self.source,self.target,'fight','copy')
        state=self.c.load_setup_state(name,self.target)
        self.assertEqual(state['characters'][0]['id'],'c')
        self.assertEqual(state['monsters'][0]['id'],'new-monster')

    def test_empty_destination_roster_does_not_use_active_roster(self):
        self.prepare()
        empty=self.c.STORAGE.create_campaign('Empty','','now')
        self.c.STORAGE.save_characters(empty,[])
        name=self.c.STORAGE.transfer_setup(self.source,empty,'fight','copy')
        state=self.c.load_setup_state(name,empty)
        self.assertEqual(state['characters'],[])
        self.assertEqual(state['monsters'][0]['id'],'c')

    def test_same_campaign_copy_remains_valid(self):
        campaign=self.c.active_campaign()
        name=self.c.STORAGE.transfer_setup(campaign,campaign,'default','copy')
        state=self.c.load_setup_state(name,campaign)
        self.assertEqual(state['characters'][0]['id'],'c')
        self.assertEqual(state['monsters'][0]['id'],'m')

    def test_unrelated_value_error_keeps_its_type(self):
        async def broken():raise ValueError('programming failure')
        with self.assertRaisesRegex(ValueError,'programming failure'):
            asyncio.run(transactional_handler(self.c,broken)())

if __name__=='__main__':unittest.main()
