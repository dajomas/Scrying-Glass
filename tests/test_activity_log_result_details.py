"""SG-TODO-019: Activity log lines name the affected unit, property and result.

Real handlers, real SQLite storage and the real ActivityService/FeaturesService
loggers; browser rendering is covered by test_activity_log_result_render.py.
"""
import copy
import unittest
import test_attack_statistics as stats
import test_bughunt_round18 as inline
from python.scrying_glass_activity_details import (
    hp_note, snapshot, statistics_note, statistics_snapshot, death_failure_note, unit_name)
from python.scrying_glass_statistics import ABILITIES


class FormatterTests(unittest.TestCase):
    def test_hp_note_names_unit_and_resulting_values(self):
        before = dict(hp=12, temp_hp=3, max_hp=20, life_state='standing')
        after = dict(name='Goblin - 2', hp=5, temp_hp=0, max_hp=20, life_state='standing')
        self.assertEqual(hp_note(after, before), 'Goblin - 2: HP 12 → 5/20; temporary HP 3 → 0')

    def test_life_state_change_is_reported(self):
        item = dict(name='Cleric', hp=0, max_hp=20, life_state='down')
        self.assertEqual(hp_note(item, dict(hp=4, max_hp=20, life_state='standing')),
                         'Cleric: HP 4 → 0/20; life state standing → down')

    def test_unchanged_temporary_hp_is_omitted(self):
        item = dict(name='Hero', hp=9, temp_hp=2, max_hp=9)
        self.assertEqual(hp_note(item, dict(hp=4, temp_hp=2, max_hp=9)), 'Hero: HP 4 → 9/9')

    def test_statistics_note_lists_effective_changes_and_clamped_hp(self):
        before = dict(max_hp=20, strength=14, hp=18)
        after = dict(name='Ogre', max_hp=15, strength=14, hp=15)
        self.assertEqual(statistics_note(after, before, prefix='Restored'),
                         'Restored; Ogre: Max HP 20 → 15; HP 18 → 15')

    def test_statistics_note_reports_no_change_explicitly(self):
        item = dict(name='Ogre', strength=10)
        self.assertEqual(statistics_note(item, statistics_snapshot(item)),
                         'Ogre: no effective statistic changed')

    def test_death_failure_note_and_unit_fallback(self):
        self.assertEqual(death_failure_note(dict(name='Hero', death_failures=2), 'damage at 0 HP'),
                         'Hero: death-save failures now 2/3; damage at 0 HP')
        self.assertEqual(unit_name(None), 'Encounter')

    def test_formatting_does_not_mutate_inputs(self):
        item = dict(name='Hero', hp=3, max_hp=9, effects=[])
        before = snapshot(item); frozen = copy.deepcopy(item)
        hp_note(item, before); statistics_note(item, statistics_snapshot(item))
        self.assertEqual(item, frozen)


class ProducerTests(unittest.TestCase):
    setUp = stats.AttackStatisticsTests.setUp
    tearDown = stats.AttackStatisticsTests.tearDown
    call = stats.AttackStatisticsTests.call
    submit = stats.AttackStatisticsTests.submit
    bases = stats.AttackStatisticsTests.bases
    edit = stats.AttackStatisticsTests.edit
    reduce = stats.AttackStatisticsTests.reduce
    update = inline.InlineConcentrationLogTests.update

    def item(self, ident='m'): return self.c.entity(ident)
    def log(self): return self.c.STATE['activity_log']
    def new_rows(self, start, action=None):
        return [r for r in self.log()[start:] if action is None or r['action'] == action]

    def add_second_goblin(self):
        twin = copy.deepcopy(self.item('m'))
        twin.update(id='m2', name='Goblin - 2'); self.item('m')['name'] = 'Goblin - 1'
        self.c.STATE['monsters'].append(twin)
        self.c.save_active_setup_monsters(); self.c.save_state()

    def test_battle_damage_and_heal_rows_name_each_target_with_result(self):
        self.add_second_goblin(); start = len(self.log())
        self.submit([dict(target_id='m', action='damage', amount=5),
                     dict(target_id='m2', action='damage', amount=2),
                     dict(target_id='m', action='heal', amount=1)])
        rows = self.new_rows(start)
        self.assertEqual([(r['target_combatant_id'], r['action'], r['amount'], r['note']) for r in rows], [
            ('m', 'damage', 5, 'Goblin - 1: HP 12 → 7/12'),
            ('m2', 'damage', 2, 'Goblin - 2: HP 12 → 10/12'),
            ('m', 'heal', 1, 'Goblin - 1: HP 7 → 8/12')])
        # Logging must not apply anything again.
        self.assertEqual((self.item('m')['hp'], self.item('m2')['hp']), (8, 10))

    def test_temporary_hp_absorption_reports_both_pools(self):
        self.call('edit_features', 'm', {'temp_hp': 4}); start = len(self.log())
        self.submit([dict(target_id='m', action='damage', amount=6)])
        self.assertEqual(self.new_rows(start, 'damage')[0]['note'],
                         'Goblin: HP 12 → 10/12; temporary HP 4 → 0')

    def test_buff_rows_stay_unannotated(self):
        start = len(self.log())
        self.submit([dict(target_id='m', action='buff')])
        self.assertEqual(self.new_rows(start, 'buff')[0].get('note'), None)

    def test_inline_character_and_monster_hp_edits_report_result(self):
        start = len(self.log())
        self.update('characters', -6); self.update('monsters', 3)
        rows = self.new_rows(start)
        self.assertEqual([(r['target_combatant_id'], r['action'], r['amount'], r['note']) for r in rows], [
            ('c', 'damage', 6, 'Cleric: HP 20 → 14/20'),
            ('m', 'heal', 3, 'Goblin: HP 12 → 12/12')])

    def test_combat_feature_edits_name_unit(self):
        start = len(self.log())
        self.call('edit_features', 'c', {'hp_delta': -20})
        row = self.new_rows(start, 'combat-features')[0]
        self.assertTrue(row['note'].startswith('Cleric: HP 20 → 0'), row['note'])
        self.assertIn('Life state standing → down', row['note'])

    def test_death_save_failure_names_unit(self):
        self.update('characters', -20); start = len(self.log())
        self.update('characters', -1)
        row = self.new_rows(start, 'death-save-failure')[0]
        self.assertEqual(row['note'], 'Cleric: death-save failures now 1/3; damage at 0 HP')
        self.assertEqual(self.new_rows(start, 'damage')[0]['note'], 'Cleric: HP 0 → 0/20')

    def test_statistic_reduction_and_restore_report_effective_values(self):
        self.bases(**dict.fromkeys(ABILITIES, 12)); start = len(self.log())
        self.submit([self.reduce('strength', 2), self.reduce('max_hp', 5)])
        rows = self.new_rows(start, 'statistic-reduced')
        self.assertEqual([r['note'] for r in rows], [
            'Goblin: STR 12 → 10; source: Cleric',
            'Goblin: Max HP 12 → 7; HP 12 → 7; source: Cleric'])
        start = len(self.log())
        self.edit(operation='restore', stat='all')
        note = self.new_rows(start, 'statistics-restore')[0]['note']
        self.assertEqual(note, 'Restored all: removed 2 reductions; no healing; Goblin: Max HP 7 → 12; STR 10 → 12')

    def test_details_survive_persistence_and_existing_history_is_untouched(self):
        self.log().insert(0, {'id': 'historic', 'action': 'damage', 'amount': 1, 'note': 'Historical'})
        self.c.save_state()
        self.submit([dict(target_id='m', action='damage', amount=2)])
        self.c.load_state(); stored = self.c.STATE['activity_log']
        self.assertEqual(stored[0]['note'], 'Historical')
        self.assertEqual(stored[-1]['note'], 'Goblin: HP 12 → 10/12')


if __name__ == '__main__': unittest.main()
