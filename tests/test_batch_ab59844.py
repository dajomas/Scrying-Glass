"""Batch regressions: explicit recovery and campaign transition edge cases."""
import asyncio
import copy
import types
import unittest
import test_encounter_features as fixture
import test_bughunt_round10 as helpers
from test_sqlite_storage import HTTPError
from python.scrying_glass_admin_campaigns import AdminCampaignsMixin
from python.scrying_glass_classes import CharacterUpdate
from python.scrying_glass_turn_rules import can_take_turn
from python.scrying_glass_database_transactions import transactional_handler

class BatchTransitionTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown
    call=fixture.FeatureTests.call

    def campaign_call(self,name,*args,**kwargs):
        handler=AdminCampaignsMixin();handler.context=self.c
        return asyncio.run(transactional_handler(self.c,getattr(handler,name))(*args,**kwargs))

    def empty_campaign(self,name='Empty'):
        ident=self.c.STORAGE.create_campaign(name,'','now')
        self.c.STORAGE.save_characters(ident,[])
        return ident

    def failed_death(self):
        self.call('edit_features','c',{'life_state':'down'})
        self.call('edit_features','c',{'death_failures':3})
        self.c.set_turn(self.c.entity('m'),True)

    def recover(self,**values):
        cls=helpers.load_class('scrying_glass_admin_characters.py','AdminCharactersMixin',
            dict(can_take_turn=can_take_turn,__package__='python'))
        handler=cls();handler.context=self.c
        return asyncio.run(transactional_handler(self.c,handler.update_character)('c',CharacterUpdate(**values)))

    def make_active_campaign_empty_and_switch_away(self):
        original=self.c.active_campaign();destination=self.empty_campaign('Destination')
        payload=types.SimpleNamespace(from_campaign=original,setup='default',mode='move')
        self.campaign_call('add_setup_to_campaign',destination,payload)
        self.assertEqual(self.c.STORAGE.list_setups(original),[])
        self.campaign_call('activate_campaign',destination)
        return original

    def test_known_recovery_defect_positive_hp(self):
        self.failed_death();self.recover(alive=True,hp=5)
        c=self.c.entity('c')
        self.assertEqual((c['hp'],c['life_state'],c['death_failures']),(5,'standing',0))
        self.assertEqual(self.c.active_combatant()['id'],'m')

    def test_known_recovery_defect_zero_hp(self):
        self.failed_death();self.recover(alive=True)
        c=self.c.entity('c')
        self.assertEqual((c['hp'],c['life_state'],c['death_failures']),(0,'down',0))
        self.assertIn('c',self.c.STATE['battle_order'])

    def test_recovery_does_not_implicitly_resurrect(self):
        self.failed_death();self.recover(hp=5)
        self.assertEqual(self.c.entity('c')['life_state'],'dead')

    def test_recovery_undo_preserves_death_history(self):
        self.failed_death();self.recover(alive=True,hp=5)
        self.call('undo',{'id':self.f.summary()['undo']['id']})
        self.assertEqual(self.c.entity('c')['death_failures'],3)

    def test_empty_campaign_activation_does_not_restore_old_turn(self):
        original=self.make_active_campaign_empty_and_switch_away()
        self.campaign_call('activate_campaign',original)
        self.assertIsNone(self.c.active_combatant())
        self.assertEqual(self.c.STATE['battle_round'],0)
        self.assertEqual(self.c.STATE['battle_order'],[])

    def test_empty_activation_keeps_roster_health_and_persists_no_turn(self):
        original=self.make_active_campaign_empty_and_switch_away()
        self.campaign_call('activate_campaign',original)
        self.assertEqual(self.c.entity('c')['hp'],20)
        self.assertTrue(self.c.entity('c')['active'])
        self.c.load_state()
        self.assertIsNone(self.c.active_combatant())
        self.assertFalse(self.c.STORAGE.load_characters(original)[0]['in_turn'])

    def test_named_setup_activation_still_clears_turn(self):
        original=self.c.active_campaign()
        other=self.empty_campaign('Other');self.c.create_default_setup(other)
        self.campaign_call('activate_campaign',other)
        self.campaign_call('activate_campaign',original)
        self.assertIsNone(self.c.active_combatant())

    def test_deleting_active_campaign_can_move_setups_into_empty_target(self):
        original=self.c.active_campaign();target=self.empty_campaign()
        result=self.campaign_call('delete_campaign',original,move_to=target)
        self.assertFalse(self.c.STORAGE.campaign_exists(original))
        self.assertEqual(self.c.active_campaign(),target)
        self.assertEqual(result['opened_setup'],'default')
        self.assertEqual(self.c.STATE['monsters'][0]['id'],'m')
        self.assertEqual(self.c.active_setup_reference(),{'campaign_id':target,'name':'default'})

    def test_delete_move_preserves_existing_target_setup_selection(self):
        original=self.c.active_campaign();target=self.empty_campaign()
        self.c.create_default_setup(target);self.c.remember_setup(target,'default')
        result=self.campaign_call('delete_campaign',original,move_to=target)
        self.assertEqual(result['opened_setup'],'default')
        self.assertEqual(self.c.STATE['monsters'],[])
        self.assertIn('default-2',self.c.STORAGE.list_setups(target))

    def test_move_to_empty_target_conflict_rolls_back_source_deletion(self):
        original=self.c.active_campaign();target=self.empty_campaign()
        chars=self.c.normalize_state({'characters':[{'id':'m','name':'Target character','hp':10}]})['characters']
        self.c.STORAGE.save_characters(target,chars)
        before=copy.deepcopy(self.c.STATE);campaigns=self.c.read_campaigns()
        with self.assertRaises(HTTPError) as error:self.campaign_call('delete_campaign',original,move_to=target)
        self.assertEqual(error.exception.status_code,409)
        self.assertEqual(self.c.STATE,before);self.assertEqual(self.c.read_campaigns(),campaigns)
        self.assertEqual(self.c.STORAGE.list_setups(target),[])
        self.assertTrue(self.c.STORAGE.setup_exists(original,'default'))

    def test_delete_without_move_still_rejects_setup_less_replacement(self):
        original=self.c.active_campaign();self.empty_campaign()
        with self.assertRaises(HTTPError) as error:self.campaign_call('delete_campaign',original,delete_setups=True)
        self.assertEqual(error.exception.status_code,409)
        self.assertTrue(self.c.STORAGE.campaign_exists(original))

    def test_successful_empty_target_relocation_survives_reload(self):
        original=self.c.active_campaign();target=self.empty_campaign()
        self.campaign_call('delete_campaign',original,move_to=target)
        self.c.load_state()
        self.assertEqual(self.c.active_campaign(),target)
        self.assertEqual(self.c.active_setup_reference()['name'],'default')
        self.assertEqual(self.c.STATE['monsters'][0]['id'],'m')

if __name__=='__main__':unittest.main()
