"""SG-TODO-027: granting temporary HP in Battle Actions, following the 5e rules.

Temporary HP never stack: by default the higher value is kept; "replace" takes the new
amount. Granting is not healing: at 0 HP the life state and death saves do not change.
Healing never changes temporary HP and damage uses them first (unchanged). Untracked
characters and dead creatures cannot get them. End battle leaves them.
"""
import unittest

import test_character_hp_tracking as tracking
from python.scrying_glass_classes import BattleActionRow, BattleActions
from python.scrying_glass_feature_rules import apply_hp, grant_temp_hp, normalize_features


def character(**values):
    return normalize_features({'id': 'c', 'name': 'Cleric', 'hp': 12, 'max_hp': 20, **values})


class GrantRuleTests(unittest.TestCase):
    def test_no_stacking_keep_higher_or_replace(self):
        item = character()
        self.assertEqual(grant_temp_hp(item, 5), (0, 5))   # empty: granted
        self.assertEqual(grant_temp_hp(item, 8), (5, 8))   # higher: taken
        self.assertEqual(grant_temp_hp(item, 3), (8, 8))   # lower: kept, never added
        self.assertEqual(grant_temp_hp(item, 3, replace=True), (8, 3))
        self.assertEqual(item['hp'], 12)

    def test_at_zero_hp_no_life_state_change_but_damage_is_absorbed(self):
        item = character(hp=0, life_state='down', death_failures=1)
        grant_temp_hp(item, 6)
        self.assertEqual((item['hp'], item['life_state'], item['death_failures'], item['temp_hp']), (0, 'down', 1, 6))
        apply_hp(item, -4)
        # Absorbed, but a hit at 0 HP still fails a death save (existing, documented rule).
        self.assertEqual((item['temp_hp'], item['hp'], item['death_failures']), (2, 0, 2))

    def test_healing_never_changes_temporary_hp(self):
        item = character(temp_hp=5)
        apply_hp(item, 6)
        self.assertEqual((item['hp'], item['temp_hp']), (18, 5))

    def test_refused_for_dead_untracked_and_bad_amounts(self):
        for item, message in ((character(hp=0, life_state='dead'), 'is dead'),
                              (character(track_hp=False), 'HP is not tracked')):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                grant_temp_hp(item, 3)
        for amount in (0, 100000, '5', True):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                grant_temp_hp(character(), amount)


class GrantEndpointTests(tracking.EndpointTests):
    """Battle Actions with real SQLite and services; reuses the SG-TODO-024 fixture."""
    for name in [n for n in dir(tracking.EndpointTests) if n.startswith('test_')]:
        locals()[name] = None  # the inherited tests run in their own module
    del name

    def act(self, *rows, actor='c'):
        battle = self.handler('python.scrying_glass_admin_battle', 'AdminBattleMixin')
        return self.run_handler(battle.apply_battle_actions, BattleActions(actor_id=actor, actions=list(rows)))

    def test_grant_keep_higher_then_replace_is_logged_and_persists(self):
        self.act(BattleActionRow(target_id='m', action='temp-hp', amount=6))
        self.act(BattleActionRow(target_id='m', action='temp-hp', amount=4))
        self.act(BattleActionRow(target_id='m', action='temp-hp-replace', amount=2))
        self.c.load_state()
        self.assertEqual((self.item('m')['temp_hp'], self.item('m')['hp']), (2, 12))
        notes = [e['note'] for e in self.c.STATE['activity_log'] if e['action'] == 'temp-hp']
        self.assertEqual(notes, ['Goblin: Temporary HP 0 → 6 (granted); source: Cleric',
                                 'Goblin: Temporary HP 6 → 6 (kept higher); source: Cleric',
                                 'Goblin: Temporary HP 6 → 2 (replaced); source: Cleric'])

    def test_downed_target_keeps_its_state_and_untracked_is_only_logged(self):
        self.call('edit_features', 'c', {'hp_delta': -20})  # Cleric is down at 0
        self.c.STATE['characters'].append(normalize_features(
            {'id': 'p', 'name': 'Bard', 'hp': 8, 'max_hp': 8, 'active': True, 'track_hp': False}))
        self.item('c')['in_turn'], self.item('m')['in_turn'] = False, True
        self.act(BattleActionRow(target_id='c', action='temp-hp', amount=5),
                 BattleActionRow(target_id='p', action='temp-hp-replace', amount=5), actor='m')
        self.assertEqual((self.item('c')['temp_hp'], self.item('c')['hp'], self.item('c')['life_state']), (5, 0, 'down'))
        self.assertEqual((self.item('p')['temp_hp'], self.item('p')['hp']), (0, 8))  # HP not tracked: unchanged
        entry = self.c.STATE['activity_log'][-1]
        self.assertEqual((entry['action'], entry['amount'], entry['note']),
                         ('temp-hp', 5, 'Bard: HP not tracked; source: Goblin'))
        with self.assertRaises(tracking.feature_tests.HTTPError) as caught:
            self.act(BattleActionRow(target_id='c', action='temp-hp', amount=None), actor='m')
        self.assertEqual(caught.exception.status_code, 400)  # an amount is required

    def test_reactions_cannot_grant(self):
        with self.assertRaises(tracking.feature_tests.HTTPError) as caught:
            self.act(BattleActionRow(source_id='m', target_id='c', action='temp-hp', amount=5))
        self.assertEqual(caught.exception.status_code, 400)


class GrantAdminTests(unittest.TestCase):
    """Battle Actions choices (assembled Admin, intercepted HTTP)."""

    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def test_target_rows_offer_temporary_hp_and_send_it(self):
        import json
        page, errors, _ = self.rows.open_page(self, 1440, active=True, workflow='live')
        monster = self.snapshot['monsters'][0]
        page.wait_for_function("typeof openBattleActions === 'function' && window.scryingTempHpGrantInstalled")
        bodies = []

        def capture(route):
            bodies.append(json.loads(route.request.post_data or '{}'))
            route.fulfill(content_type='application/json', body=json.dumps({'applied': 1, 'activity_log': []}))
        page.route('**/api/battle/actions', capture)
        page.evaluate("id => openBattleActions(id)", monster['id'])
        page.evaluate("document.getElementById('battleActionRows').replaceChildren()")
        page.locator('#addBattleReaction').click()
        reaction = page.locator('.battle-reaction-row select[data-action-kind] option')
        self.assertEqual(reaction.evaluate_all('o => o.map(x => x.value)'), ['damage', 'heal'])
        page.evaluate("document.getElementById('battleActionRows').replaceChildren()")
        page.locator('#addBattleActionTarget').click()
        row = page.locator('.battle-action-row').first
        values = row.locator('select[data-action-kind] option').evaluate_all('o => o.map(x => x.value)')
        self.assertEqual(values[-2:], ['temp-hp', 'temp-hp-replace'])
        row.locator('select[data-action-target]').select_option(monster['id'])
        row.locator('select[data-action-kind]').select_option('temp-hp-replace')
        self.assertTrue(row.locator('.amount-field').is_visible())
        self.assertFalse(row.locator('.critical-option').is_visible())
        row.locator('[data-action-amount]').fill('7')
        page.locator('#battleActionForm button[type="submit"]').click()
        page.wait_for_timeout(300)
        self.assertEqual([(a['action'], a['target_id'], a['amount']) for a in bodies[0]['actions']],
                         [('temp-hp-replace', monster['id'], 7)])
        self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
