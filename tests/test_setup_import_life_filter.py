"""Setup import filters saved monster state before cloning/remapping."""
import asyncio
import copy
import unittest
from pydantic import ValidationError
import test_encounter_features as fixture
from test_bughunt_round10 import load_class
from python.scrying_glass_classes import SetupImport
from python.scrying_glass_database_transactions import transactional_handler

class ImportLifeFilterTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown

    def source(self):
        alive=copy.deepcopy(self.c.entity('m'))
        alive.update(id='alive-source',name='Alive monster',hp=7,effects=[])
        dead=copy.deepcopy(alive)
        dead.update(id='dead-source',name='Dead monster',hp=0,alive=False,life_state='dead')
        state=self.c.normalize_state({'monsters':[dead,alive]})
        self.c.STORAGE.save_setup(self.c.active_campaign(),'filter-source',state)
        return state

    def run_import(self,life_filter=None):
        cls=load_class('scrying_glass_admin_setups.py','AdminSetupsMixin')
        handler=cls();handler.context=self.c
        data=dict(name='filter-source',kind='monsters')
        if life_filter is not None:data['life_filter']=life_filter
        before={x['id'] for x in self.c.STATE['monsters']}
        result=asyncio.run(transactional_handler(self.c,handler.import_setup)(SetupImport(**data)))
        clones=[x for x in self.c.STATE['monsters'] if x['id'] not in before]
        self.assertEqual(result['monsters'],len(clones))
        return clones

    def test_default_alive(self):
        self.source();clones=self.run_import()
        self.assertEqual([x['name'] for x in clones],['Alive monster'])
        self.assertEqual(clones[0]['hp'],7)

    def test_dead(self):
        self.source();clones=self.run_import('dead')
        self.assertEqual([x['name'] for x in clones],['Dead monster'])
        self.assertEqual(clones[0]['hp'],0)
        self.assertFalse(clones[0]['alive'])
        self.assertEqual(clones[0]['life_state'],'dead')

    def test_all_and_runtime_reset(self):
        self.source();order=list(self.c.STATE['battle_order'])
        clones=self.run_import('all')
        self.assertEqual(len(clones),2)
        for clone in clones:
            self.assertNotIn(clone['id'],{'dead-source','alive-source'})
            self.assertFalse(clone['active'])
            self.assertFalse(clone['in_turn'])
        self.assertEqual(self.c.STATE['battle_order'],order)

    def test_filtered_self_reference_uses_correct_original(self):
        state=self.source()
        state['monsters'][1]['effects']=[dict(id='effect',name='Self',notes='',public=False,
            concentration=False,source_id='alive-source',anchor_id='alive-source',timing='end',turns=1)]
        self.c.STORAGE.save_setup(self.c.active_campaign(),'filter-source',state)
        clone=self.run_import('alive')[0]
        self.assertEqual(clone['effects'][0]['source_id'],clone['id'])
        self.assertEqual(clone['effects'][0]['anchor_id'],clone['id'])

    def test_excluded_reference_does_not_bind_existing_monster(self):
        state=self.source()
        state['monsters'][1]['effects']=[dict(id='effect',name='Linked',notes='',public=False,
            concentration=False,source_id='dead-source',anchor_id='dead-source',timing='end',turns=1)]
        self.c.STORAGE.save_setup(self.c.active_campaign(),'filter-source',state)
        clone=self.run_import('alive')[0]
        self.assertIsNone(clone['effects'][0]['source_id'])
        self.assertEqual(clone['effects'][0]['timing'],'manual')

    def test_empty_match_and_source_unchanged(self):
        state=self.source();state['monsters']=state['monsters'][1:]
        campaign=self.c.active_campaign()
        self.c.STORAGE.save_setup(campaign,'filter-source',state)
        before=self.c.STORAGE.load_setup(campaign,'filter-source')
        self.assertEqual(self.run_import('dead'),[])
        self.assertEqual(self.c.STORAGE.load_setup(campaign,'filter-source'),before)

    def test_invalid_filter_rejected(self):
        with self.assertRaises(ValidationError):
            SetupImport(name='x',kind='monsters',life_filter='invalid')

if __name__=='__main__':unittest.main()
