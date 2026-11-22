"""SG-TODO-025 and 026: Max HP increase in battle; current HP follows maximum HP increases.

- The increase is its own mechanical effect; reductions and increases combine against
  base_max_hp, and Restore statistics removes both (current HP is then only capped).
- Current HP rises by the increase: in battle, in the Edit dialogs when only the maximum
  changes, and on a monster refresh. Removing a reduction does not raise current HP.
- A downed creature that gets HP above 0 is up again; a dead one stays dead. Characters
  whose HP is not tracked are left alone.
"""
import importlib.util
import unittest

import test_character_hp_tracking as tracking
from python.scrying_glass_classes import BattleActionRow, BattleActions, CharacterUpdate, MonsterUpdate
from python.scrying_glass_feature_rules import normalize_features
from python.scrying_glass_health_limits import MAX_STORED_HP
from python.scrying_glass_statistics import (MAX_HP_INCREASE, follow_max_increase, increase_max_hp,
                                             legacy_max_edit, reduce_stat, restore_stat)


def creature(**values):
    return normalize_features({'id': 'm', 'name': 'Goblin', 'monster_species': 'goblin',
                               'hp': 12, 'max_hp': 20, **values})


def character(**values):
    return normalize_features({'id': 'c', 'name': 'Cleric', 'hp': 12, 'max_hp': 20, **values})


class IncreaseRuleTests(unittest.TestCase):
    def test_increase_raises_maximum_and_current_hp(self):
        item = creature()
        effect = increase_max_hp(item, 5, 'c')
        self.assertEqual((item['max_hp'], item['hp'], item['base_max_hp']), (25, 17, 20))
        self.assertEqual((effect['name'], effect['mechanical']), ('Max HP increase',
                         {'version': 1, 'stat': MAX_HP_INCREASE, 'amount': 5}))

    def test_increases_and_reductions_combine(self):
        item = creature(hp=20)
        reduce_stat(item, 'max_hp', 6)
        self.assertEqual((item['max_hp'], item['hp']), (14, 14))
        increase_max_hp(item, 10)
        self.assertEqual((item['max_hp'], item['hp']), (24, 24))

    def test_restore_removes_both_and_only_caps_current_hp(self):
        item = creature(hp=20)
        reduce_stat(item, 'max_hp', 6)        # 14/14
        restore_stat(item, 'max_hp')
        self.assertEqual((item['max_hp'], item['hp']), (20, 14))  # no rise from ending a reduction (5e)
        increase_max_hp(item, 10)              # 30/24
        self.assertEqual(restore_stat(item, 'max_hp'), 1)
        self.assertEqual((item['max_hp'], item['hp']), (20, 20))  # removing an increase caps
        self.assertEqual(item['effects'], [])

    def test_downed_character_gets_back_up(self):
        item = character(hp=0, life_state='down', death_successes=1, death_failures=2)
        increase_max_hp(item, 4)
        self.assertEqual((item['hp'], item['life_state'], item['death_failures'], item['alive']),
                         (4, 'standing', 0, True))

    def test_refused_for_dead_untracked_and_over_the_limit(self):
        for item, message in ((character(hp=0, life_state='dead'), 'is dead'),
                              (creature(hp=0, life_state='dead'), 'is dead'),  # damage to 0 kills a monster
                              (character(track_hp=False), 'HP is not tracked'),
                              (creature(max_hp=MAX_STORED_HP, hp=1), 'must not exceed')):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                increase_max_hp(item, 1)
        with self.assertRaises(ValueError):
            increase_max_hp(creature(), 0)

    def test_follow_max_increase(self):
        before = creature()
        cases = (
            (dict(max_hp=26), False, 18),          # only the maximum: current rises
            (dict(max_hp=26, hp=15), True, 15),    # both typed: the typed values win
            (dict(max_hp=10), False, 12),          # a decrease is left to the usual cap
        )
        for change, given, expected in cases:
            candidate = {**before, **change}
            follow_max_increase(before, candidate, given)
            self.assertEqual(candidate['hp'], expected, change)
        dead = character(hp=0, life_state='dead')
        candidate = {**dead, 'max_hp': 30}
        follow_max_increase(dead, candidate)
        self.assertEqual(candidate['hp'], 0)
        untracked = character(track_hp=False)
        candidate = {**untracked, 'max_hp': 30}
        follow_max_increase(untracked, candidate)
        self.assertEqual(candidate['hp'], 12)

    def test_edit_with_an_active_increase_must_keep_the_effective_maximum(self):
        item = creature()
        increase_max_hp(item, 5)
        legacy_max_edit(item, {'max_hp': 25})
        with self.assertRaisesRegex(ValueError, 'Active Max HP reductions or increases'):
            legacy_max_edit(item, {'max_hp': 30})


class IncreaseEndpointTests(tracking.EndpointTests):
    """Real SQLite and services; reuses the SG-TODO-024 fixture."""
    # Only the tests below; the inherited SG-TODO-024 tests run in their own module.
    for name in [n for n in dir(tracking.EndpointTests) if n.startswith('test_')]:
        locals()[name] = None
    del name

    def battle(self, *rows):
        battle = self.handler('python.scrying_glass_admin_battle', 'AdminBattleMixin')
        return self.run_handler(battle.apply_battle_actions, BattleActions(actor_id='c', actions=list(rows)))

    def test_battle_actions_increase_is_logged_and_persists(self):
        self.battle(BattleActionRow(target_id='m', action='increase-max-hp', amount=5))
        self.c.load_state()
        monster = self.item('m')
        self.assertEqual((monster['max_hp'], monster['hp'], monster['base_max_hp']), (17, 17, 12))
        self.assertEqual([e['mechanical']['stat'] for e in monster['effects']], [MAX_HP_INCREASE])
        entry = self.c.STATE['activity_log'][-1]
        self.assertEqual((entry['action'], entry['amount']), ('max-hp-increased', 5))
        self.assertEqual(entry['note'], 'Goblin: Max HP 12 → 17; HP 12 → 17; source: Cleric')

    def test_battle_actions_raise_a_downed_character_and_refuse_untracked(self):
        self.call('edit_features', 'c', {'hp_delta': -20})  # Cleric is down at 0
        self.c.STATE['characters'].append(normalize_features(
            {'id': 'p', 'name': 'Bard', 'hp': 8, 'max_hp': 8, 'active': True, 'track_hp': False}))
        self.item('c')['in_turn'], self.item('m')['in_turn'] = False, True  # the Goblin acts
        battle = self.handler('python.scrying_glass_admin_battle', 'AdminBattleMixin')
        act = lambda *rows: self.run_handler(battle.apply_battle_actions, BattleActions(actor_id='m', actions=list(rows)))
        with self.assertRaises(tracking.feature_tests.HTTPError) as caught:
            act(BattleActionRow(target_id='c', action='increase-max-hp', amount=3),
                BattleActionRow(target_id='p', action='increase-max-hp', amount=3))
        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(self.item('c')['hp'], 0)  # nothing applied from the refused batch
        act(BattleActionRow(target_id='c', action='increase-max-hp', amount=3))
        self.assertEqual((self.item('c')['hp'], self.item('c')['max_hp'], self.item('c')['life_state']),
                         (3, 23, 'standing'))

    def test_edit_dialogs_raise_current_hp_when_only_the_maximum_rises(self):
        characters = self.characters()
        self.call('edit_features', 'c', {'hp_delta': -5})  # 15/20
        self.run_handler(characters.update_character, 'c', CharacterUpdate(hp=15, max_hp=24))
        self.assertEqual((self.item('c')['hp'], self.item('c')['max_hp']), (19, 24))
        self.run_handler(characters.update_character, 'c', CharacterUpdate(hp=10, max_hp=30))
        self.assertEqual((self.item('c')['hp'], self.item('c')['max_hp']), (10, 30))  # typed values win
        monsters = self.handler('python.scrying_glass_admin_monsters', 'AdminMonstersMixin')
        self.run_handler(monsters.update_monster, 'm', MonsterUpdate(hp=12, max_hp=15))
        self.assertEqual((self.item('m')['hp'], self.item('m')['max_hp']), (15, 15))


@unittest.skipIf(importlib.util.find_spec('fastapi') is None, 'the secured refresh route needs FastAPI')
class RefreshIncreaseTests(unittest.IsolatedAsyncioTestCase):
    """Monster refresh from source through the real secured route (SG-TODO-026)."""

    @classmethod
    def setUpClass(cls):
        import test_monster_refresh_review as review
        base = review.MonsterRefreshReviewTests
        for name in ('request', 'lookup', 'form', 'snapshot', 'setUp', 'json_request', 'seed', 'preview', 'apply'):
            setattr(cls, name, getattr(base, name))
        if 'tearDown' in vars(base):
            cls.tearDown = base.tearDown

    async def damaged(self, hp, max_hp):
        ident = await self.seed()
        item = self.context.STATE['monsters'][0]
        item.update(hp=hp, max_hp=max_hp, original_hp=max_hp)
        item.pop('base_max_hp', None)
        await self.context.combatants_changed(monsters=True)
        return ident, item

    async def test_refresh_of_max_hp_only_counts_as_an_increase(self):
        ident, _ = await self.damaged(4, 6)
        status, _ = await self.apply(await self.preview(ident), {ident: ['max_hp']})
        self.assertEqual(status, 200)
        item = self.context.STATE['monsters'][0]
        self.assertEqual((item['hp'], item['max_hp']), (8, 10))  # 2 damage taken stays taken

    async def test_refresh_of_hp_and_max_hp_sets_both(self):
        ident, _ = await self.damaged(4, 6)
        status, _ = await self.apply(await self.preview(ident), {ident: ['hp', 'max_hp']})
        self.assertEqual(status, 200)
        item = self.context.STATE['monsters'][0]
        self.assertEqual((item['hp'], item['max_hp']), (10, 10))


class MaxHpIncreaseAdminTests(unittest.TestCase):
    """Battle Actions row and Restore statistics wording (assembled Admin, intercepted HTTP)."""

    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def test_battle_actions_row_sends_an_increase(self):
        import json
        page, errors, _ = self.rows.open_page(self, 1440, active=True, workflow='live')
        monster = self.snapshot['monsters'][0]
        page.wait_for_function("typeof openBattleActions === 'function' && !!document.getElementById('addMaxHpIncrease')")
        bodies = []

        def capture(route):
            bodies.append(json.loads(route.request.post_data or '{}'))
            route.fulfill(content_type='application/json', body=json.dumps({'applied': 1, 'activity_log': []}))
        page.route('**/api/battle/actions', capture)
        page.evaluate("id => openBattleActions(id)", monster['id'])
        page.evaluate("document.getElementById('battleActionRows').replaceChildren()")  # drop the default damage row
        page.locator('#addMaxHpIncrease').click()
        row = page.locator('.max-hp-increase-row')
        row.locator('select[data-action-target]').select_option(monster['id'])
        row.locator('[data-action-amount]').fill('6')
        self.assertIn('Current HP rises by the same amount', row.text_content())
        page.locator('#battleActionForm button[type="submit"]').click()
        page.wait_for_timeout(300)
        actions = bodies[0]['actions']
        self.assertEqual([(a['action'], a['target_id'], a['amount']) for a in actions],
                         [('increase-max-hp', monster['id'], 6)])
        self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
