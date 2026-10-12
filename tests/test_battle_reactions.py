"""Ordered reaction chains and deferred removal of the current combatant."""
import asyncio
import copy
import unittest
import test_bughunt_round18 as fixture
import test_bughunt_round10 as helpers
from python.scrying_glass_classes import BattleActions
from python.scrying_glass_feature_rules import apply_hp
from python.scrying_glass_turn_rules import can_take_turn, permanently_dead
from python.scrying_glass_database_transactions import transactional_handler

class ReactionTests(unittest.TestCase):
    setUp = fixture.InlineConcentrationLogTests.setUp
    tearDown = fixture.InlineConcentrationLogTests.tearDown

    def submit(self, rows):
        cls = helpers.load_class('scrying_glass_admin_battle.py', 'AdminBattleMixin',
            dict(apply_hp=apply_hp, can_take_turn=can_take_turn, permanently_dead=permanently_dead))
        handler = cls(); handler.context = self.c
        return asyncio.run(transactional_handler(self.c, handler.apply_battle_actions)(
            BattleActions(actor_id='m', actions=rows)))

    def start(self):
        other = copy.deepcopy(self.c.entity('m'))
        other.update(id='n', name='Mephit B', hp=4, max_hp=4, in_turn=False)
        self.c.STATE['monsters'].append(other)
        self.c.begin_battle(['m', 'n', 'c'])

    def reaction(self, source, target, amount, action='damage'):
        return dict(source_id=source, target_id=target, action=action, amount=amount)

    def kill_owner(self):
        self.submit([self.reaction('c','m',12)])

    def test_chain_and_source_attribution(self):
        self.start()
        self.submit([dict(target_id='c',action='damage',amount=1),
            self.reaction('c','m',12),self.reaction('m','n',4),self.reaction('n','c',3)])
        self.assertEqual(self.c.entity('c')['hp'],16)
        self.assertEqual(self.c.entity('m')['life_state'],'dead')
        self.assertEqual(self.c.entity('n')['life_state'],'dead')
        self.assertEqual(self.c.active_combatant()['id'],'m')
        self.assertIn('m',self.c.STATE['battle_order'])
        self.assertNotIn('n',self.c.STATE['battle_order'])
        logs=[x for x in self.c.STATE['activity_log'] if x['action']=='damage']
        self.assertEqual([x['active_combatant_id'] for x in logs],['m','c','m','n'])
        self.assertEqual(self.c.advance_turn()['id'],'c')
        self.assertNotIn('m',self.c.STATE['battle_order'])
        self.assertEqual(self.c.STATE['battle_round'],1)

    def test_dead_owner_reactions_after_reload(self):
        self.start();self.kill_owner();self.c.load_state()
        self.assertEqual(self.c.active_combatant()['id'],'m')
        self.submit([self.reaction('m','c',2)])
        self.assertEqual(self.c.entity('c')['hp'],18)

    def test_invalid_later_source_rolls_back(self):
        self.start();before=copy.deepcopy(self.c.STATE)
        with self.assertRaises(Exception):
            self.submit([self.reaction('m','c',2),self.reaction('missing','c',2)])
        self.assertEqual(self.c.STATE,before)

    def test_same_source_and_target(self):
        self.start();self.submit([self.reaction('m','m',1)])
        self.assertEqual(self.c.entity('m')['hp'],11)

    def test_dead_target_does_not_resurrect(self):
        self.start();self.kill_owner()
        self.submit([self.reaction('m','m',2,'heal')])
        self.assertEqual(self.c.entity('m')['life_state'],'dead')
        self.assertEqual(self.c.entity('m')['hp'],0)

    def test_dead_owner_cannot_use_ordinary_action(self):
        self.start();self.kill_owner()
        with self.assertRaises(Exception):
            self.submit([dict(target_id='c',action='damage',amount=2)])

    def test_last_turn_death_wraps_once(self):
        self.start();self.c.begin_battle(['c','n','m'])
        self.c.advance_turn();self.c.advance_turn();self.kill_owner()
        self.assertEqual(self.c.advance_turn()['id'],'c')
        self.assertEqual(self.c.STATE['battle_round'],2)

    def test_temporary_hp_and_healing_cap(self):
        self.start();self.c.entity('c')['temp_hp']=3
        self.submit([self.reaction('m','c',5)])
        self.assertEqual(self.c.entity('c')['hp'],18)
        self.submit([self.reaction('c','c',99,'heal')])
        self.assertEqual(self.c.entity('c')['hp'],20)

if __name__=='__main__':unittest.main()
