"""Explicit legacy recovery must clear terminal failed-save counters."""
import asyncio
import unittest
import test_bughunt_round18 as fixture
import test_bughunt_round10 as helpers
from python.scrying_glass_classes import CharacterUpdate
from python.scrying_glass_turn_rules import can_take_turn
from python.scrying_glass_database_transactions import transactional_handler

class ExplicitCharacterRecoveryTests(unittest.TestCase):
    setUp=fixture.InlineConcentrationLogTests.setUp
    tearDown=fixture.InlineConcentrationLogTests.tearDown
    call=fixture.InlineConcentrationLogTests.call

    def dead_from_saves(self):
        self.call('edit_features','c',{'life_state':'down'})
        self.call('edit_features','c',{'death_failures':3})
        self.c.set_turn(self.c.entity('m'),True)
        self.assertEqual(self.c.entity('c')['life_state'],'dead')

    def update(self,**fields):
        cls=helpers.load_class('scrying_glass_admin_characters.py','AdminCharactersMixin',
            dict(can_take_turn=can_take_turn,__package__='python'))
        handler=cls();handler.context=self.c
        return asyncio.run(transactional_handler(self.c,handler.update_character)('c',CharacterUpdate(**fields)))

    def test_failed_save_death_explicit_recovery_with_hp_stands(self):
        self.dead_from_saves();self.update(alive=True,hp=5)
        item=self.c.entity('c')
        self.assertEqual((item['life_state'],item['hp'],item['death_failures']),('standing',5,0))
        self.assertTrue(item['alive'])

    def test_failed_save_death_zero_hp_recovery_returns_to_down(self):
        self.dead_from_saves();self.update(alive=True)
        item=self.c.entity('c')
        self.assertEqual((item['life_state'],item['hp'],item['death_failures']),('down',0,0))
        self.assertIn('c',self.c.STATE['battle_order'])

    def test_recovery_does_not_steal_current_turn(self):
        self.dead_from_saves();self.update(alive=True,hp=5)
        self.assertIn('c',self.c.STATE['battle_order'])
        self.assertEqual(self.c.active_combatant()['id'],'m')

    def test_instant_death_recovery_behavior_is_preserved(self):
        self.call('edit_features','c',{'hp_delta':-40})
        self.update(alive=True,hp=5)
        self.assertEqual(self.c.entity('c')['life_state'],'standing')

    def test_nonterminal_down_counter_is_not_reset_by_alive_flag(self):
        self.call('edit_features','c',{'life_state':'down'})
        self.call('edit_features','c',{'death_failures':2})
        self.update(alive=True)
        self.assertEqual(self.c.entity('c')['death_failures'],2)

    def test_dead_character_is_not_recovered_by_hp_edit_without_flag(self):
        self.dead_from_saves();self.update(hp=5)
        self.assertEqual(self.c.entity('c')['life_state'],'dead')
        self.assertEqual(self.c.entity('c')['hp'],0)

    def test_recovery_counters_persist_after_reload(self):
        self.dead_from_saves();self.update(alive=True,hp=5);self.c.load_state()
        item=self.c.entity('c')
        self.assertEqual((item['hp'],item['death_failures'],item['life_state']),(5,0,'standing'))

    def test_recovery_undo_restores_terminal_counters(self):
        self.dead_from_saves();self.update(alive=True,hp=5)
        self.call('undo',{'id':self.f.summary()['undo']['id']})
        self.assertEqual(self.c.entity('c')['life_state'],'dead')
        self.assertEqual(self.c.entity('c')['death_failures'],3)

if __name__=='__main__':unittest.main()
