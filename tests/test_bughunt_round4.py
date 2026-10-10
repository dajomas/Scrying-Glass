"""Round-four cross-campaign setup-transfer regressions."""
import copy
import unittest
import test_encounter_features as fixture
from python.scrying_glass_lair_rules import normalize_lairs

class SetupTransferTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown
    call=fixture.FeatureTests.call
    item=fixture.FeatureTests.item
    effect=fixture.FeatureTests.effect

    def prepare(self, concentration=False):
        self.call('add_effect','m',{**self.effect(),'concentration':concentration,
                  'timing':'end','anchor_id':'c','turns':2})
        self.source=self.c.active_campaign()
        self.target=self.c.STORAGE.create_campaign('Destination','','now')
        character=copy.deepcopy(self.item('c'))
        character['name']='Unrelated character with the same ID'
        self.c.STORAGE.save_characters(self.target,[character])

    def transfer(self, mode):
        name=self.c.STORAGE.transfer_setup(self.source,self.target,'default',mode)
        return name,self.c.STORAGE.load_setup(self.target,name)

    def test_copy_drops_foreign_concentration_source(self):
        self.prepare(True)
        _,state=self.transfer('copy')
        self.assertEqual(state['monsters'][0]['effects'],[])

    def test_move_drops_foreign_concentration_source(self):
        self.prepare(True)
        _,state=self.transfer('move')
        self.assertEqual(state['monsters'][0]['effects'],[])

    def test_copy_clears_foreign_source_and_makes_anchor_manual(self):
        self.prepare()
        _,state=self.transfer('copy')
        effect=state['monsters'][0]['effects'][0]
        self.assertIsNone(effect['source_id'])
        self.assertIsNone(effect['anchor_id'])
        self.assertEqual(effect['timing'],'manual')
        self.assertIsNone(effect['turns'])
        self.assertEqual(effect['notes'],'private note')

    def test_move_clears_foreign_source_and_makes_anchor_manual(self):
        self.prepare()
        _,state=self.transfer('move')
        self.assertEqual(state['monsters'][0]['effects'][0]['timing'],'manual')

    def test_internal_monster_and_lair_references_survive(self):
        self.prepare()
        self.c.STATE['lairs']=normalize_lairs([{'id':'lair-test','name':'Volcano'}])
        self.call('add_effect','m',{**self.effect(),'name':'Internal','source_id':'m',
                  'anchor_id':'lair-test','timing':'start','turns':3,'concentration':True})
        _,state=self.transfer('copy')
        effect=next(e for e in state['monsters'][0]['effects'] if e['name']=='Internal')
        self.assertEqual(effect['source_id'],'m')
        self.assertEqual(effect['anchor_id'],'lair-test')
        self.assertEqual(effect['turns'],3)
        self.assertTrue(effect['concentration'])

    def test_copy_does_not_change_source(self):
        self.prepare(True)
        before=self.c.STORAGE.load_setup(self.source,'default')
        self.transfer('copy')
        self.assertEqual(self.c.STORAGE.load_setup(self.source,'default'),before)

    def test_same_campaign_copy_keeps_roster_links(self):
        self.prepare(True)
        name=self.c.STORAGE.transfer_setup(self.source,self.source,'default','copy')
        effect=self.c.STORAGE.load_setup(self.source,name)['monsters'][0]['effects'][0]
        self.assertEqual(effect['source_id'],'c')
        self.assertEqual(effect['anchor_id'],'c')
        self.assertEqual(effect['timing'],'end')

    def test_same_campaign_move_handles_renamed_self_reference(self):
        self.prepare(True)
        name=self.c.STORAGE.transfer_setup(self.source,self.source,'default','move')
        state=self.c.STORAGE.load_setup(self.source,name)
        self.assertEqual(state['monsters'][0]['effects'][0]['source_id'],'c')
        self.assertIsNone(state['active_setup'])

    def test_move_failure_rolls_back_transfer_and_cleanup(self):
        self.prepare()
        before=self.c.STORAGE.load_setup(self.source,'default')
        with self.assertRaises(RuntimeError):
            with self.c.STORAGE.transaction():
                self.transfer('move')
                raise RuntimeError('abort')
        self.assertEqual(self.c.STORAGE.load_setup(self.source,'default'),before)
        self.assertEqual(self.c.STORAGE.list_setups(self.target),[])

if __name__=='__main__':unittest.main()
