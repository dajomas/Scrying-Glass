"""Reset health regressions using actual handlers and real SQLite transactions."""
import ast
import asyncio
import copy
import unittest
from pathlib import Path
from types import SimpleNamespace
import test_encounter_features as fixtures
from python.scrying_glass_combatant import reset_entity, admin_max_hp_key
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_feature_rules import normalize_features


def handler(filename, name):
    path = Path(__file__).resolve().parents[1] / 'python' / filename
    tree = ast.parse(path.read_text())
    node = next(n for cls in tree.body if isinstance(cls, ast.ClassDef)
                for n in cls.body if isinstance(n, ast.AsyncFunctionDef) and n.name == name)
    namespace = {}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), node], type_ignores=[])), str(path), 'exec'), namespace)
    return namespace[name]


class ResetHealthTests(unittest.TestCase):
    setUp = fixtures.FeatureTests.setUp
    tearDown = fixtures.FeatureTests.tearDown
    call = fixtures.FeatureTests.call
    item = fixtures.FeatureTests.item

    def reset(self, name, *args):
        filenames = {'reset_one_combatant': 'scrying_glass_admin_combatants.py',
                     'bulk_characters': 'scrying_glass_admin_characters.py',
                     'bulk_monsters': 'scrying_glass_admin_monsters.py',
                     'reset_all': 'scrying_glass_admin_battle.py'}
        self.c.reset_entity = reset_entity
        self.c.unique_ids = lambda ids: list(dict.fromkeys(ids))
        self.c.admin_max_hp_key = admin_max_hp_key
        return asyncio.run(transactional_handler(self.c, handler(filenames[name], name))(
            SimpleNamespace(context=self.c), *args))

    def test_reset_dead_monster_restores_hp_after_reconcile(self):
        self.call('edit_features', 'm', {'hp_delta': -12})
        self.reset('reset_one_combatant', 'm')
        self.assertEqual((self.item()['hp'], self.item()['life_state']), (12, 'standing'))
        self.assertFalse(self.item()['active'])
        self.c.load_state()
        self.assertEqual((self.item()['hp'], self.item()['life_state']), (12, 'standing'))

    def test_reset_character_after_third_failed_save(self):
        self.call('edit_features', 'c', {'life_state': 'down'})
        self.call('edit_features', 'c', {'death_failures': 3})
        self.reset('reset_one_combatant', 'c')
        x = self.item('c')
        self.assertEqual((x['hp'], x['life_state'], x['death_failures'], x['death_successes']), (20, 'standing', 0, 0))
        self.assertEqual(self.c.STORAGE.load_characters(self.c.active_campaign())[0]['hp'], 20)

    def test_single_reset_clears_temporary_hp(self):
        self.call('edit_features', 'm', {'temp_hp': 7})
        self.reset('reset_one_combatant', 'm')
        self.assertEqual(self.item()['temp_hp'], 0)

    def test_bulk_character_reset_clears_temporary_hp(self):
        self.call('edit_features', 'c', {'temp_hp': 7})
        self.reset('bulk_characters', SimpleNamespace(action='reset', ids=['c']))
        self.assertEqual(self.item('c')['temp_hp'], 0)

    def test_bulk_monster_reset_revives_dead_monster(self):
        self.call('edit_features', 'm', {'hp_delta': -12})
        self.reset('bulk_monsters', SimpleNamespace(action='reset', ids=['m']))
        self.assertEqual((self.item()['hp'], self.item()['life_state']), (12, 'standing'))

    def test_reset_all_restores_both_kinds(self):
        self.call('edit_features', 'm', {'life_state': 'dead', 'temp_hp': 5})
        self.call('edit_features', 'c', {'life_state': 'dead', 'temp_hp': 8})
        self.reset('reset_all')
        for ident, baseline in [('m', 12), ('c', 20)]:
            x = self.item(ident)
            self.assertEqual((x['hp'], x['life_state'], x['temp_hp']), (baseline, 'standing', 0))
        self.assertEqual(self.c.STATE['battle_round'], 0)
        self.assertEqual(self.c.STATE['battle_order'], [])

    def test_reset_undo_restores_dead_state_and_temp_pool(self):
        self.call('edit_features', 'm', {'life_state': 'dead', 'temp_hp': 7})
        before = copy.deepcopy(self.item())
        self.reset('reset_one_combatant', 'm')
        self.assertEqual(self.item()['life_state'], 'standing')
        self.call('undo', {'id': self.f.summary()['undo']['id']})
        self.assertEqual(self.item(), before)

    def test_zero_baseline_reset_clears_failed_saves(self):
        x = copy.deepcopy(self.item('c'))
        x.update(hp=0, max_hp=0, life_state='dead', death_failures=3)
        reset_entity(x)
        normalize_features(x)
        self.assertEqual((x['hp'], x['life_state'], x['death_failures']), (0, 'down', 0))

    def test_reset_preserves_initiative_baseline_and_stat_flags(self):
        x = copy.deepcopy(self.item())
        x.update(initiative=18, original_initiative=4, show_ac=True, show_hp=True, show_initiative=True)
        reset_entity(x)
        self.assertEqual(x['initiative'], 4)
        for field in ('active', 'visible', 'in_turn', 'show_ac', 'show_hp', 'show_initiative'):
            self.assertFalse(x[field])

if __name__ == '__main__':
    unittest.main()
