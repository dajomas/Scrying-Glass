"""Critical-hit modifiers apply only to negative HP-delta updates."""
import copy
import unittest
from python.scrying_glass_classes import CharacterUpdate,MonsterUpdate
import test_bughunt_round19 as fixtures

class CriticalHpModelTests(unittest.TestCase):
    def rejected(self,model):
        for values in ({},{'hp_delta':None},{'hp_delta':0},{'hp_delta':1},{'hp':0}):
            with self.subTest(model=model.__name__,values=values):
                with self.assertRaises(ValueError):model(critical_hit=True,**values)

    def test_character_critical_flag_requires_damage(self):self.rejected(CharacterUpdate)
    def test_monster_critical_flag_requires_damage(self):self.rejected(MonsterUpdate)

    def test_critical_negative_deltas_remain_valid(self):
        for model in (CharacterUpdate,MonsterUpdate):
            for delta in (-1,-99999,'-1'):
                value=model(hp_delta=delta,critical_hit=True)
                self.assertLess(value.hp_delta,0)
                self.assertTrue(value.critical_hit)

    def test_noncritical_healing_zero_and_partial_updates_remain_valid(self):
        for model in (CharacterUpdate,MonsterUpdate):
            model(name='Renamed')
            for delta in (None,0,1):model(hp_delta=delta,critical_hit=False)

    def test_delta_bounds_remain_enforced(self):
        for model in (CharacterUpdate,MonsterUpdate):
            for delta in (-100000,100000):
                with self.assertRaises(ValueError):model(hp_delta=delta)

    def test_validation_methods_do_not_become_payload_fields(self):
        for model in (CharacterUpdate,MonsterUpdate):
            self.assertEqual(model(name='Renamed').model_dump(exclude_unset=True),{'name':'Renamed'})
            self.assertNotIn('_critical_hit_requires_damage',model.model_json_schema()['properties'])

class CriticalHpHandlerCompatibilityTests(unittest.TestCase):
    setUp=fixtures.InlineHpOutcomeLogTests.setUp
    tearDown=fixtures.InlineHpOutcomeLogTests.tearDown
    call=fixtures.InlineHpOutcomeLogTests.call
    update=fixtures.InlineHpOutcomeLogTests.update

    def test_invalid_critical_healing_is_rejected_before_state_changes(self):
        before=copy.deepcopy(self.c.STATE);revision=self.f.store.revision()
        with self.assertRaises(ValueError):self.update(1,critical=True)
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.f.store.revision(),revision)
        self.assertEqual(self.c.STORAGE.load_characters(self.c.active_campaign())[0]['hp'],20)

    def test_valid_critical_damage_preserves_failed_save_logic_and_log(self):
        self.call('edit_features','c',{'life_state':'down'})
        rows=self.update(-1,critical=True)
        self.assertEqual(self.c.entity('c')['death_failures'],2)
        events=[r for r in rows if r['action']=='death-save-failure']
        self.assertEqual(len(events),1)
        self.assertEqual(events[0]['amount'],2)
        self.assertIn('critical',events[0].get('note','').lower())

if __name__=='__main__':unittest.main()
