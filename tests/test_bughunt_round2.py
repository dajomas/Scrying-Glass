"""Second bug-hunt regressions against source archive 3f22b66."""
import asyncio
import copy
import types
import unittest
import test_encounter_features as fixture
from python.scrying_glass_admin_setups import AdminSetupsMixin
from python.scrying_glass_database_transactions import transactional_handler

class SecondBugHuntTests(unittest.TestCase):
    setUp = fixture.FeatureTests.setUp
    tearDown = fixture.FeatureTests.tearDown
    call = fixture.FeatureTests.call
    item = fixture.FeatureTests.item
    effect = fixture.FeatureTests.effect

    def import_monsters(self, campaign=None):
        handler = AdminSetupsMixin()
        handler.context = self.c
        before = {x['id'] for x in self.c.STATE['monsters']}
        payload = types.SimpleNamespace(name='default', kind='monsters', campaign=campaign)
        asyncio.run(transactional_handler(self.c, handler.import_setup)(payload))
        return [x for x in self.c.STATE['monsters'] if x['id'] not in before]

    def self_effect(self, concentration=False):
        self.call('add_effect', 'm', {**self.effect(), 'source_id':'m',
                  'anchor_id':'m', 'timing':'end', 'turns':2, 'concentration':concentration})

    def test_import_self_references_follow_clone(self):
        self.self_effect()
        clone = self.import_monsters()[0]
        self.assertEqual(clone['effects'][0]['source_id'], clone['id'])
        self.assertEqual(clone['effects'][0]['anchor_id'], clone['id'])

    def test_import_assigns_new_effect_ids(self):
        self.self_effect()
        original = self.item()['effects'][0]['id']
        first = self.import_monsters()[0]
        second = self.import_monsters()[0]
        self.assertEqual(len({original,first['effects'][0]['id'],second['effects'][0]['id']}),3)

    def test_original_concentration_does_not_remove_clone_effect(self):
        self.self_effect(concentration=True)
        clone_id = self.import_monsters()[0]['id']
        self.call('end_concentration', 'm')
        self.assertEqual(len(self.item(clone_id)['effects']),1)
        self.assertTrue(self.item(clone_id)['concentrating'])

    def test_import_remaps_cross_monster_references(self):
        other = copy.deepcopy(self.item())
        other.update(id='n',name='Other goblin',effects=[])
        self.c.STATE['monsters'].append(other)
        self.call('add_effect','n',{**self.effect(),'source_id':'m','anchor_id':'m','timing':'start','turns':2})
        clones = self.import_monsters()
        first = next(x for x in clones if x['name']=='Goblin')
        second = next(x for x in clones if x['name']=='Other goblin')
        self.assertEqual(second['effects'][0]['source_id'],first['id'])
        self.assertEqual(second['effects'][0]['anchor_id'],first['id'])

    def test_same_campaign_character_reference_preserved(self):
        self.call('add_effect','m',{**self.effect(),'concentration':True,'anchor_id':'c','timing':'end','turns':1})
        clone = self.import_monsters()[0]
        self.assertEqual(clone['effects'][0]['source_id'],'c')
        self.assertEqual(clone['effects'][0]['anchor_id'],'c')

    def foreign_setup(self, concentration):
        other = self.c.STORAGE.create_campaign('Foreign','','now')
        monster = copy.deepcopy(self.item())
        monster['effects']=[dict(id='foreign-effect', name='Foreign effect', source_id='c',
            anchor_id='c', timing='end', turns=1, concentration=concentration, public=False, notes='Keep note')]
        self.c.STORAGE.save_setup(other,'default',self.c.normalize_state({'monsters':[monster]}))
        character = copy.deepcopy(self.item('c'))
        character['concentrating'] = concentration
        self.c.STORAGE.save_characters(other,[character])
        return other

    def test_cross_campaign_concentration_cannot_bind_matching_id(self):
        other = self.foreign_setup(True)
        clone = self.import_monsters(other)[0]
        self.assertEqual(clone['effects'],[])

    def test_cross_campaign_missing_anchor_becomes_manual(self):
        other = self.foreign_setup(False)
        clone = self.import_monsters(other)[0]
        effect = clone['effects'][0]
        self.assertIsNone(effect['source_id'])
        self.assertIsNone(effect['anchor_id'])
        self.assertEqual(effect['timing'],'manual')
        self.assertIsNone(effect['turns'])
        self.assertEqual(effect['notes'],'Keep note')

    def test_import_does_not_change_source_setup(self):
        self.self_effect()
        campaign = self.c.active_campaign()
        self.c.STORAGE.save_setup(campaign,'source',self.c.setup_snapshot(self.c.STATE))
        before = self.c.STORAGE.load_setup(campaign,'source')
        handler = AdminSetupsMixin(); handler.context=self.c
        payload = types.SimpleNamespace(name='source',kind='monsters',campaign=campaign)
        asyncio.run(transactional_handler(self.c,handler.import_setup)(payload))
        self.assertEqual(self.c.STORAGE.load_setup(campaign,'source'),before)

    def recover(self, state):
        self.item('c')['initiative']=21
        self.item()['initiative']=10
        self.call('edit_features','c',{'life_state':'dead'})
        self.c.set_turn(self.item(),True)
        self.call('edit_features','c',{'life_state':state})

    def test_recover_down_character_reinserts_immediately(self):
        self.recover('down')
        self.assertEqual(self.c.STATE['battle_order'],['c','m'])
        self.assertTrue(self.item()['in_turn'])
        self.assertFalse(self.item('c')['in_turn'])

    def test_recover_stable_character_reinserts_immediately(self):
        self.recover('stable')
        self.assertEqual(self.c.STATE['battle_order'],['c','m'])

    def test_recover_standing_character_still_reinserts(self):
        self.recover('standing')
        self.assertEqual(self.c.STATE['battle_order'],['c','m'])

    def test_inactive_character_is_not_reinserted(self):
        self.item('c')['active']=False
        self.recover('down')
        self.assertNotIn('c',self.c.STATE['battle_order'])

if __name__ == '__main__':
    unittest.main()
