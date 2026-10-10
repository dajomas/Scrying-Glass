"""Inline HP updates log the special outcomes already computed by HP rules."""
import asyncio
import types
import unittest
import test_bughunt_round18 as fixtures
import test_bughunt_round10 as helpers
from python.scrying_glass_classes import CharacterUpdate,MonsterUpdate,BattleActions,BattleActionRow
from python.scrying_glass_turn_rules import can_take_turn,permanently_dead
from python.scrying_glass_feature_rules import apply_hp
from python.scrying_glass_database_transactions import transactional_handler

class InlineHpOutcomeLogTests(unittest.TestCase):
    setUp=fixtures.InlineConcentrationLogTests.setUp
    tearDown=fixtures.InlineConcentrationLogTests.tearDown
    call=fixtures.InlineConcentrationLogTests.call

    def update(self,delta,critical=False,kind='characters'):
        if kind=='characters':
            cls=helpers.load_class('scrying_glass_admin_characters.py','AdminCharactersMixin',
                dict(can_take_turn=can_take_turn,__package__='python'))
            model=CharacterUpdate(hp_delta=delta,critical_hit=critical);ident='c';method='update_character'
        else:
            cls=helpers.load_class('scrying_glass_admin_monsters.py','AdminMonstersMixin',dict(__package__='python'))
            model=MonsterUpdate(hp_delta=delta,critical_hit=critical);ident='m';method='update_monster'
        handler=cls();handler.context=self.c
        start=len(self.c.STATE['activity_log'])
        asyncio.run(transactional_handler(self.c,getattr(handler,method))(ident,model))
        return self.c.STATE['activity_log'][start:]

    def actions(self,rows,name):return [r for r in rows if r['action']==name]

    def test_damage_at_zero_logs_failed_save(self):
        self.call('edit_features','c',{'life_state':'down'})
        rows=self.update(-1)
        failures=self.actions(rows,'death-save-failure')
        self.assertEqual(len(failures),1);self.assertEqual(failures[0]['amount'],1)
        self.assertEqual(self.c.entity('c')['death_failures'],1)
        self.assertEqual(len(self.actions(rows,'damage')),1)

    def test_critical_damage_at_zero_logs_two_failures(self):
        self.call('edit_features','c',{'life_state':'down'})
        rows=self.update(-1,critical=True)
        failures=self.actions(rows,'death-save-failure')
        self.assertEqual(len(failures),1);self.assertEqual(failures[0]['amount'],2)
        self.assertIn('critical',failures[0].get('note','').lower())

    def test_instant_death_logs_excess_damage(self):
        rows=self.update(-40)
        events=self.actions(rows,'instant-death')
        self.assertEqual(len(events),1)
        self.assertIn('20',events[0]['note'])
        self.assertEqual(self.c.entity('c')['life_state'],'dead')

    def test_initial_drop_to_zero_has_no_failed_save_event(self):
        rows=self.update(-20)
        self.assertEqual(self.actions(rows,'death-save-failure'),[])
        self.assertEqual(self.actions(rows,'instant-death'),[])
        self.assertEqual(self.c.entity('c')['life_state'],'down')

    def test_monster_death_does_not_create_character_save_events(self):
        rows=self.update(-12,kind='monsters')
        self.assertEqual(self.actions(rows,'death-save-failure'),[])
        self.assertEqual(self.actions(rows,'instant-death'),[])

    def test_outcome_rows_survive_reload(self):
        self.call('edit_features','c',{'life_state':'down'})
        self.update(-1,critical=True);self.c.load_state()
        events=self.actions(self.c.STATE['activity_log'],'death-save-failure')
        self.assertEqual(len(events),1);self.assertEqual(events[0]['amount'],2)

    def test_battle_action_existing_outcome_is_not_duplicated(self):
        self.call('edit_features','c',{'life_state':'down'})
        self.c.set_turn(self.c.entity('m'),True)
        cls=helpers.load_class('scrying_glass_admin_battle.py','AdminBattleMixin',
            dict(apply_hp=apply_hp,permanently_dead=permanently_dead,can_take_turn=can_take_turn))
        handler=cls();handler.context=self.c
        payload=BattleActions(actor_id='m',actions=[BattleActionRow(target_id='c',action='damage',amount=1)])
        start=len(self.c.STATE['activity_log'])
        asyncio.run(transactional_handler(self.c,handler.apply_battle_actions)(payload))
        self.assertEqual(len(self.actions(self.c.STATE['activity_log'][start:],'death-save-failure')),1)

    def test_legacy_two_argument_logging_still_works(self):
        start=len(self.c.STATE['activity_log'])
        self.activity.log_hp_change(self.c.entity('c'),-1)
        rows=self.c.STATE['activity_log'][start:]
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['action'],'damage')

if __name__=='__main__':unittest.main()
