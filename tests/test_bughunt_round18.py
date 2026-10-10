"""Inline HP-delta updates must record concentration reminders consistently."""
import asyncio
import types
import unittest
from datetime import datetime,timezone
import test_encounter_features as fixture
import test_bughunt_round10 as helpers
from python.scrying_glass_classes import CharacterUpdate,MonsterUpdate,BattleActions,BattleActionRow
from python.scrying_glass_feature_rules import apply_hp
from python.scrying_glass_turn_rules import can_take_turn,permanently_dead
from python.scrying_glass_database_transactions import transactional_handler

class InlineConcentrationLogTests(unittest.TestCase):
    def setUp(self):
        fixture.FeatureTests.setUp(self)
        self.c.datetime=datetime;self.c.timezone=timezone
        self.activity=helpers.load_class('scrying_glass_service_activity.py','ActivityService')(self.c)
        self.c.log_hp_change=self.activity.log_hp_change
        self.c.log_battle_action=self.activity.log_battle_action
    tearDown=fixture.FeatureTests.tearDown
    call=fixture.FeatureTests.call

    def update(self,kind,delta):
        if kind=='characters':
            cls=helpers.load_class('scrying_glass_admin_characters.py','AdminCharactersMixin',
                                  dict(can_take_turn=can_take_turn,__package__='python'))
            model=CharacterUpdate(hp_delta=delta);ident='c';method='update_character'
        else:
            cls=helpers.load_class('scrying_glass_admin_monsters.py','AdminMonstersMixin',dict(__package__='python'))
            model=MonsterUpdate(hp_delta=delta);ident='m';method='update_monster'
        handler=cls();handler.context=self.c
        return asyncio.run(transactional_handler(self.c,getattr(handler,method))(ident,model))

    def reminders(self,rows):return [r for r in rows if r['action']=='concentration-reminder']

    def damage_case(self,kind):
        ident='c' if kind=='characters' else 'm'
        self.call('edit_features',ident,{'concentrating':True})
        start=len(self.c.STATE['activity_log'])
        self.update(kind,-2)
        rows=self.c.STATE['activity_log'][start:]
        self.assertEqual(len(self.reminders(rows)),1)
        self.assertEqual(self.reminders(rows)[0]['target_combatant_id'],ident)
        self.assertEqual(len([r for r in rows if r['action']=='damage']),1)
        self.assertTrue(self.c.entity(ident)['concentrating'])

    def test_character_inline_damage_records_reminder(self):self.damage_case('characters')
    def test_monster_inline_damage_records_reminder(self):self.damage_case('monsters')

    def test_temporary_hp_absorbed_damage_still_records_reminder(self):
        self.call('edit_features','c',{'concentrating':True,'temp_hp':5})
        start=len(self.c.STATE['activity_log']);self.update('characters',-1)
        self.assertEqual(self.c.entity('c')['hp'],20)
        self.assertEqual(self.c.entity('c')['temp_hp'],4)
        self.assertEqual(len(self.reminders(self.c.STATE['activity_log'][start:])),1)

    def test_healing_and_zero_delta_do_not_record_reminder(self):
        self.call('edit_features','c',{'concentrating':True})
        start=len(self.c.STATE['activity_log'])
        self.update('characters',1);self.update('characters',0)
        self.assertEqual(self.reminders(self.c.STATE['activity_log'][start:]),[])

    def test_downing_damage_automatically_ends_concentration(self):
        self.call('edit_features','c',{'concentrating':True})
        start=len(self.c.STATE['activity_log']);self.update('characters',-20)
        self.assertFalse(self.c.entity('c')['concentrating'])
        self.assertEqual(self.reminders(self.c.STATE['activity_log'][start:]),[])

    def test_reminder_survives_reload(self):
        self.damage_case('characters')
        self.c.load_state()
        self.assertEqual(len(self.reminders(self.c.STATE['activity_log'])),1)

    def test_ordinary_battle_action_does_not_get_duplicate_reminders(self):
        self.call('edit_features','m',{'concentrating':True})
        start=len(self.c.STATE['activity_log'])
        cls=helpers.load_class('scrying_glass_admin_battle.py','AdminBattleMixin',
              dict(apply_hp=apply_hp,can_take_turn=can_take_turn,permanently_dead=permanently_dead))
        handler=cls();handler.context=self.c
        payload=BattleActions(actor_id='c',actions=[BattleActionRow(target_id='m',action='damage',amount=1)])
        asyncio.run(transactional_handler(self.c,handler.apply_battle_actions)(payload))
        self.assertEqual(len(self.reminders(self.c.STATE['activity_log'][start:])),1)

    def test_legacy_context_without_features_still_logs_damage(self):
        self.c.features=None
        target=dict(self.c.entity('c'),concentrating=True)
        start=len(self.c.STATE['activity_log']);self.activity.log_hp_change(target,-1)
        self.assertEqual(len(self.c.STATE['activity_log'][start:]),1)
        self.assertEqual(self.c.STATE['activity_log'][-1]['action'],'damage')

if __name__=='__main__':unittest.main()
