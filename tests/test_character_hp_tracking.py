"""SG-TODO-024: optional HP tracking per character (real SQLite, real services).

An untracked character's current, maximum and temporary HP never change through damage
or healing; the amount is still logged and the DM sets life state and death saves by
hand. Monsters are not affected. The setting is kept per character and persists.
"""
import asyncio
import importlib
import importlib.util
import types
import unittest
from unittest.mock import patch

import test_encounter_features as feature_tests
from python.scrying_glass_classes import BattleActionRow, BattleActions, BulkCombatantAction, CharacterCreate, CharacterUpdate
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_feature_rules import apply_hp, normalize_features, tracks_hp
from python.scrying_glass_statistics import reduce_stat


def mixin(module, name):
    if importlib.util.find_spec('fastapi') is None:  # CI has FastAPI; this keeps local runs possible
        fake = types.ModuleType('fastapi')
        fake.File = fake.Form = lambda *a, **k: None
        fake.HTTPException = feature_tests.HTTPError
        fake.Request = fake.UploadFile = object
        with patch.dict('sys.modules', {'fastapi': fake}):
            return getattr(importlib.import_module(module), name)
    return getattr(importlib.import_module(module), name)


class RuleTests(unittest.TestCase):
    def character(self, **values):
        return normalize_features({'id': 'c', 'name': 'Cleric', 'hp': 5, 'max_hp': 20, 'temp_hp': 4,
                                   'track_hp': False, **values})

    def test_monsters_always_track_and_characters_by_default(self):
        self.assertTrue(tracks_hp({'monster_species': 'goblin', 'track_hp': False}))
        self.assertTrue(tracks_hp({'name': 'Cleric'}))
        self.assertFalse(tracks_hp({'name': 'Cleric', 'track_hp': False}))

    def test_damage_and_healing_change_nothing(self):
        for delta in (-50, -3, 7):
            item = self.character()
            result = apply_hp(item, delta, critical=delta < -10)
            self.assertTrue(result['untracked'])
            self.assertEqual((item['hp'], item['max_hp'], item['temp_hp'], item['life_state'],
                              item['death_failures']), (5, 20, 4, 'standing', 0), delta)

    def test_life_state_is_not_derived_from_hp(self):
        self.assertEqual(self.character(hp=0, life_state='standing')['life_state'], 'standing')
        self.assertEqual(self.character(hp=12, life_state='down')['life_state'], 'down')
        dead = self.character(hp=12, death_failures=3, life_state='down')
        self.assertEqual((dead['life_state'], dead['hp']), ('dead', 12))  # stored HP is kept
        with self.assertRaises(ValueError):
            self.character(track_hp='no')

    def test_switching_tracking_on_uses_the_stored_hp(self):
        item = self.character(hp=0, life_state='standing')
        item['track_hp'] = True
        normalize_features(item)
        self.assertEqual(item['life_state'], 'down')

    def test_max_hp_reduction_is_refused_but_abilities_are_not(self):
        with self.assertRaisesRegex(ValueError, 'HP is not tracked for Cleric'):
            reduce_stat(self.character(), 'max_hp', 3)
        reduce_stat(self.character(base_strength=12), 'strength', 1)
        monster = normalize_features({'id': 'm', 'name': 'Goblin', 'monster_species': 'goblin', 'hp': 7,
                                      'max_hp': 7, 'track_hp': False})
        reduce_stat(monster, 'max_hp', 2)
        self.assertEqual(monster['max_hp'], 5)


class EndpointTests(unittest.TestCase):
    tearDown = feature_tests.FeatureTests.tearDown

    def setUp(self):
        feature_tests.FeatureTests.setUp(self)
        unique_ids = mixin('python.scrying_glass_tools', 'unique_ids')
        activity = mixin('python.scrying_glass_service_activity', 'ActivityService')(self.c)
        self.c.log_battle_action = activity.log_battle_action
        self.c.log_hp_change = activity.log_hp_change
        self.c.unique_ids = unique_ids
        import datetime, uuid
        for name, value in (('datetime', datetime.datetime), ('timezone', datetime.timezone), ('uuid', uuid)):
            if not hasattr(self.c, name):
                setattr(self.c, name, value)
    call = feature_tests.FeatureTests.call
    item = feature_tests.FeatureTests.item

    def handler(self, module, name):
        handler = mixin(module, name)()
        handler.context = self.c
        return handler

    def run_handler(self, method, *args):
        return asyncio.run(transactional_handler(self.c, method)(*args))

    def characters(self):
        return self.handler('python.scrying_glass_admin_characters', 'AdminCharactersMixin')

    def untrack(self):
        self.run_handler(self.characters().update_character, 'c', CharacterUpdate(track_hp=False))
        self.c.load_state()

    def test_create_without_hp_and_the_setting_persists(self):
        created = self.run_handler(self.characters().create_character,
                                   CharacterCreate(name='Rogue', color='#123456', track_hp=False))
        self.c.load_state()
        stored = self.c.entity(created['id'])
        self.assertEqual((stored['track_hp'], stored['alive']), (False, True))
        self.assertEqual(self.item('c').get('track_hp', True), True)  # default stays on

    def test_encounter_tools_log_the_amount_and_keep_hp(self):
        self.untrack()
        self.call('edit_features', 'c', {'hp_delta': -50})
        self.call('edit_features', 'c', {'hp_delta': 9})
        self.assertEqual((self.item('c')['hp'], self.item('c')['life_state']), (20, 'standing'))
        logged = [(e['action'], e['amount'], e.get('note')) for e in self.c.STATE['activity_log'][-2:]]
        self.assertEqual(logged, [('damage', 50, 'Cleric: HP not tracked'), ('heal', 9, 'Cleric: HP not tracked')])
        with self.assertRaises(feature_tests.HTTPError) as caught:
            self.call('edit_features', 'c', {'temp_hp': 5})
        self.assertEqual(caught.exception.status_code, 422)

    def test_manual_life_state_and_death_saves_leave_hp_alone(self):
        self.untrack()
        self.call('edit_features', 'c', {'life_state': 'down'})
        self.call('edit_features', 'c', {'death_failures': 2})
        self.assertEqual((self.item('c')['hp'], self.item('c')['life_state'], self.item('c')['death_failures']),
                         (20, 'down', 2))
        self.call('edit_features', 'c', {'life_state': 'standing'})
        self.assertEqual((self.item('c')['hp'], self.item('c')['death_failures']), (20, 0))

    def test_battle_actions_damage_is_logged_and_hp_kept(self):
        self.untrack()
        battle = self.handler('python.scrying_glass_admin_battle', 'AdminBattleMixin')
        self.run_handler(battle.apply_battle_actions, BattleActions(actor_id='c', actions=[
            BattleActionRow(target_id='c', action='damage', amount=40, critical_hit=True),
            BattleActionRow(target_id='m', action='damage', amount=5)]))
        self.assertEqual((self.item('c')['hp'], self.item('c')['life_state']), (20, 'standing'))
        self.assertEqual(self.item('m')['hp'], 7)  # monsters are not affected
        logged = [(e['action'], e['amount'], e['target_combatant_id']) for e in self.c.STATE['activity_log'][-2:]]
        self.assertEqual(logged, [('damage', 40, 'c'), ('damage', 5, 'm')])

    def test_bulk_track_and_do_not_track(self):
        characters = self.characters()
        self.run_handler(characters.bulk_characters, BulkCombatantAction(action='untrack-hp', ids=['c']))
        self.c.load_state()
        self.assertIs(self.item('c')['track_hp'], False)
        self.run_handler(characters.bulk_characters, BulkCombatantAction(action='track-hp', ids=['c']))
        self.c.load_state()
        self.assertIs(self.item('c')['track_hp'], True)
        self.assertEqual(self.item('c')['hp'], 20)

    def test_edit_toggles_alive_without_hp(self):
        self.untrack()
        characters = self.characters()
        self.run_handler(characters.update_character, 'c', CharacterUpdate(alive=False))
        self.assertEqual(self.item('c')['life_state'], 'dead')
        self.run_handler(characters.update_character, 'c', CharacterUpdate(alive=True))
        self.assertEqual((self.item('c')['life_state'], self.item('c')['hp']), ('standing', 20))


if __name__ == '__main__':
    unittest.main()
