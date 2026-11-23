"""Battle Actions source and target menus with colour markers (static/battle-action-menus.js).

Full Admin assets with intercepted HTTP (the SG-TODO-015 statistics fixture); not live-server evidence.
"""
from pathlib import Path
import unittest

import test_battle_action_statistics as stats

ROOT = Path(__file__).resolve().parents[1]
FIRST = '#battleActionRows .battle-action-row:first-child'
RED, GREEN = 'rgb(255, 0, 0)', 'rgb(0, 170, 0)'


class MenuSourceTests(unittest.TestCase):
    def test_assets_load_after_the_statistics_summaries(self):
        end = (ROOT / 'templates/admin/190_document_end.html').read_text(encoding='utf-8')
        self.assertEqual(end.count('/static/battle-action-menus.js?v=1'), 1)
        self.assertEqual(end.count('/static/battle-action-menus.css?v=1'), 1)
        self.assertLess(end.index('/static/battle-action-statistics.js'), end.index('/static/battle-action-menus.js'))


class MenuBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stats.ActionStatisticsBrowserTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        stats.ActionStatisticsBrowserTests.tearDownClass.__func__(cls)

    def open_page(self, width=1440):
        page, errors, mutations = stats.ActionStatisticsBrowserTests.open_page(self, width)
        page.evaluate("""() => {
            latest.monsters[0].color = '#ff0000';
            latest.characters[0].color = '#00aa00';
            scryingLairsRender(latest);
        }""")
        return page, errors, mutations

    @staticmethod
    def dot_color(locator):
        return locator.locator('.sg-menu-dot').first.evaluate('n => getComputedStyle(n).backgroundColor')

    def test_closed_menu_list_and_mouse_choice(self):
        page, errors, mutations = self.open_page()
        try:
            select = page.locator(stats.TARGET)
            trigger = page.locator(f'{FIRST} .sg-menu-trigger')
            self.assertEqual(select.get_attribute('aria-hidden'), 'true')
            self.assertEqual(select.evaluate('n => n.tabIndex'), -1)
            self.assertEqual(page.locator(FIRST).get_by_role('combobox', name='Target', exact=True).count(), 1)
            self.assertEqual(trigger.text_content().strip(), 'Select target…')
            self.assertEqual(trigger.locator('.sg-menu-dot-empty').count(), 1)
            trigger.click()
            listbox = page.locator(f'{FIRST} [role="listbox"]')
            self.assertEqual(trigger.get_attribute('aria-expanded'), 'true')
            options = listbox.locator('[role="option"]')
            names = [n.strip() for n in options.all_text_contents()]
            self.assertEqual(len(names), select.locator('option:not([disabled])').count())
            monster = options.filter(has_text=page.evaluate('latest.monsters[0].name')).first
            character = options.filter(has_text=page.evaluate('latest.characters[0].name')).first
            self.assertEqual(self.dot_color(monster), RED)
            self.assertEqual(self.dot_color(character), GREEN)
            monster.click()
            self.assertTrue(listbox.is_hidden())
            self.assertEqual(select.input_value(), page.evaluate('statsMonster'))
            self.assertEqual(self.dot_color(trigger), RED)
            self.assertIn(page.evaluate('latest.monsters[0].name'), trigger.text_content())
            stats.ActionStatisticsBrowserTests.assert_summary(self, page, stats.TARGET, 'AC 14 · HP 9 · HP MAX 20')
            self.assertIn(page.locator(stats.TARGET).get_attribute('aria-describedby'),
                          trigger.get_attribute('aria-describedby'))
            self.assertEqual(errors, [])
            self.assertEqual(mutations, [])
        finally:
            page.close()

    def test_keyboard_escape_and_following_the_select(self):
        page, errors, mutations = self.open_page()
        try:
            trigger = page.locator(f'{FIRST} .sg-menu-trigger')
            listbox = page.locator(f'{FIRST} [role="listbox"]')
            trigger.focus()
            page.keyboard.press('ArrowDown')
            self.assertTrue(listbox.is_visible())
            page.keyboard.press('Escape')
            self.assertTrue(listbox.is_hidden())
            self.assertTrue(page.locator('#battleActionModal').is_visible())  # Escape closed only the menu
            page.keyboard.press('Enter')
            page.keyboard.press('End')
            last = listbox.locator('[role="option"]').last
            self.assertEqual(trigger.get_attribute('aria-activedescendant'), last.get_attribute('id'))
            value = last.get_attribute('data-value')
            page.keyboard.press('Enter')
            self.assertEqual(page.locator(stats.TARGET).input_value(), value)
            self.assertTrue(trigger.evaluate('n => n === document.activeElement'))
            # Set on the select itself (as the tests and the apply code do): the menu follows.
            page.locator(stats.TARGET).select_option(page.evaluate('statsCharacter'))
            self.assertEqual(self.dot_color(trigger), GREEN)
            page.locator(stats.TARGET).evaluate('n => { n.disabled = true; }')
            page.wait_for_function('s => document.querySelector(s).disabled', arg=f'{FIRST} .sg-menu-trigger')
            page.locator(stats.TARGET).evaluate('n => { n.disabled = false; }')
            # Colours follow a state refresh.
            page.evaluate("latest.characters[0].color = '#ff0000'; scryingLairsRender(latest)")
            self.assertEqual(self.dot_color(trigger), RED)
            self.assertEqual(errors, [])
            self.assertEqual(mutations, [])
        finally:
            page.close()

    def test_reaction_source_and_other_rows_get_menus(self):
        page, errors, mutations = self.open_page()
        try:
            page.locator('#addBattleReaction').click()
            reaction = page.locator('.battle-reaction-row')
            self.assertEqual(reaction.locator('.sg-menu-trigger').count(), 2)
            reaction.get_by_role('combobox', name='Reaction source', exact=True).click()
            source = reaction.locator('[role="listbox"]').first
            source.locator('[role="option"]').filter(has_text=page.evaluate('latest.characters[0].name')).first.click()
            self.assertEqual(page.locator(stats.SOURCE).input_value(), page.evaluate('statsCharacter'))
            page.locator('#addStatisticsReduction').click()
            page.locator('#addMaxHpIncrease').click()
            for row in ('.statistics-reduction-row', '.max-hp-increase-row'):
                self.assertEqual(page.locator(f'{row} .sg-menu-trigger').count(), 1, row)
            self.assertEqual(errors, [])
            self.assertEqual(mutations, [])
        finally:
            page.close()

    def test_unanswered_menu_is_marked_instead_of_a_hidden_bubble(self):
        page, errors, mutations = self.open_page()
        try:
            posts = []
            page.route('**/api/battle/actions', lambda route: (posts.append(route.request), route.abort()))
            page.locator('#battleActionForm button[type="submit"]').click()
            trigger = page.locator(f'{FIRST} .sg-menu-trigger')
            page.wait_for_function('s => document.querySelector(s).getAttribute("aria-invalid") === "true"',
                                   arg=f'{FIRST} .sg-menu-trigger')
            self.assertTrue(trigger.evaluate('n => n === document.activeElement'))
            self.assertEqual(page.locator('#battleActionNotice').text_content(), 'Choose a target for every row.')
            self.assertEqual(posts, [])
            page.locator(stats.TARGET).select_option(page.evaluate('statsMonster'))
            self.assertIsNone(trigger.get_attribute('aria-invalid'))
            self.assertEqual(errors, [])
        finally:
            page.close()


if __name__ == '__main__':
    unittest.main()
