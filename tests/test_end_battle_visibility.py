"""SG-TODO-028: End battle hides monsters, characters and lairs (real SQLite, real services).

Dead or downed creatures stay hidden after End battle until the GM changes their
visibility, resets them or the next battle starts; during a battle, and before the
first one, a creature that is not alive is still shown.
"""
import asyncio
import importlib
import importlib.util
import types
import unittest
from unittest.mock import patch

import test_encounter_features as feature_tests
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_combatant import reset_entity
from python.scrying_glass_feature_rules import HIDDEN_AT_BATTLE_END, reveal_if_down


class EndBattleVisibilityTests(unittest.TestCase):
    setUp = feature_tests.FeatureTests.setUp
    tearDown = feature_tests.FeatureTests.tearDown
    call = feature_tests.FeatureTests.call
    item = feature_tests.FeatureTests.item

    def end_battle(self):
        if importlib.util.find_spec('fastapi') is None:  # CI has FastAPI; this keeps local runs possible
            fake = types.ModuleType('fastapi')
            fake.File = fake.Form = lambda *a, **k: None
            with patch.dict('sys.modules', {'fastapi': fake}):
                from python.scrying_glass_admin_battle import AdminBattleMixin
        else:
            from python.scrying_glass_admin_battle import AdminBattleMixin
        admin = AdminBattleMixin()
        admin.context = self.c
        return asyncio.run(transactional_handler(self.c, admin.battle_end)())

    def reload(self):
        self.c.load_state()

    def test_end_battle_hides_everyone_and_keeps_it_after_a_reload(self):
        self.c.STATE['lairs'] = [{'id': 'l', 'name': 'Volcano', 'notes': '', 'initiative': 20, 'active': True,
                                  'visible': True, 'in_turn': False}]
        self.c.save_state()
        self.assertEqual(self.end_battle(), {'status': 'ended'})
        self.reload()
        for ident in ('m', 'c'):
            self.assertFalse(self.item(ident)['visible'], ident)
            self.assertTrue(self.item(ident).get(HIDDEN_AT_BATTLE_END), ident)
        self.assertFalse(self.c.STATE['lairs'][0]['visible'])
        self.assertEqual((self.c.STATE['battle_round'], self.c.STATE['battle_order']), (0, []))

    def test_dead_or_downed_stay_hidden_after_end_battle_until_shown(self):
        self.end_battle()
        self.call('edit_features', 'm', {'hp_delta': -12})  # killed after the battle
        self.call('edit_features', 'c', {'hp_delta': -20})  # downed after the battle
        self.reload()
        self.assertEqual((self.item('m')['life_state'], self.item('m')['visible']), ('dead', False))
        self.assertEqual((self.item('c')['life_state'], self.item('c')['visible']), ('down', False))

    def test_the_next_battle_restores_the_usual_rule(self):
        self.end_battle()
        self.c.begin_battle(['c', 'm'])
        self.assertNotIn(HIDDEN_AT_BATTLE_END, self.item('m'))
        self.call('edit_features', 'm', {'hp_delta': -12})
        self.assertTrue(self.item('m')['visible'])  # during a battle a dead creature is shown

    def test_before_the_first_battle_the_usual_rule_applies(self):
        self.c.STATE['battle_round'] = 0
        self.item('m')['visible'] = False
        self.call('edit_features', 'm', {'hp_delta': -12})
        self.assertTrue(self.item('m')['visible'])

    def test_reset_clears_the_mark(self):
        self.end_battle()
        reset_entity(self.item('m'))
        self.assertNotIn(HIDDEN_AT_BATTLE_END, self.item('m'))

    def handler(self, module, name):
        if importlib.util.find_spec('fastapi') is None:
            fake = types.ModuleType('fastapi')
            fake.File = fake.Form = lambda *a, **k: None
            with patch.dict('sys.modules', {'fastapi': fake}):
                cls = getattr(importlib.import_module(module), name)
        else:
            cls = getattr(importlib.import_module(module), name)
        handler = cls()
        handler.context = self.c
        return handler

    def test_changing_visibility_by_hand_ends_the_hiding(self):
        from python.scrying_glass_classes import CharacterUpdate, MonsterUpdate
        self.end_battle()
        monsters = self.handler('python.scrying_glass_admin_monsters', 'AdminMonstersMixin')
        characters = self.handler('python.scrying_glass_admin_characters', 'AdminCharactersMixin')
        for target, kind, model in ((monsters.update_monster, 'm', MonsterUpdate),
                                    (characters.update_character, 'c', CharacterUpdate)):
            asyncio.run(transactional_handler(self.c, target)(kind, model(visible=True)))
            asyncio.run(transactional_handler(self.c, target)(kind, model(visible=False)))
            self.reload()
            self.assertNotIn(HIDDEN_AT_BATTLE_END, self.item(kind), kind)
        self.call('edit_features', 'm', {'hp_delta': -12})
        self.assertTrue(self.item('m')['visible'])  # the usual rule again once the GM took over

    def test_reveal_rule(self):
        down = {'alive': False, 'visible': False}
        reveal_if_down(down)
        self.assertTrue(down['visible'])
        held = {'alive': False, 'visible': False, HIDDEN_AT_BATTLE_END: True}
        reveal_if_down(held)
        self.assertFalse(held['visible'])
        standing = {'alive': True, 'visible': False}
        reveal_if_down(standing)
        self.assertFalse(standing['visible'])


if __name__ == '__main__':
    unittest.main()
