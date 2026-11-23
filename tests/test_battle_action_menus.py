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

    GEOMETRY = """() => {
        const list = [...document.querySelectorAll('.sg-menu-list')].find(n => !n.hidden);
        const t = document.querySelector(`[aria-controls="${list.id}"]`).getBoundingClientRect();
        const b = list.getBoundingClientRect();
        const item = list.querySelector('[role=option]').getBoundingClientRect();
        const hit = document.elementFromPoint(item.left + item.width / 2, item.top + item.height / 2);
        return {top: b.top, bottom: b.bottom, height: innerHeight, below: b.top - t.bottom,
                above: t.top - b.bottom, onTop: list.contains(hit), up: list.classList.contains('sg-menu-up')};
    }"""

    def test_list_stays_visible_at_the_modal_edge_and_while_scrolling(self):
        page, errors, mutations = self.open_page()
        try:
            page.set_viewport_size({'width': 1440, 'height': 640})
            page.evaluate("""() => {  // enough combatants that the list cannot fit below the last row
                const base = latest.monsters[0];
                for (let i = 1; i <= 10; i++) latest.monsters.push({...base, id: `extra-${i}`, name: `Extra ${i}`});
            }""")
            for _ in range(6):
                page.locator('#addBattleReaction').click()
            dialog = page.locator('#battleActionModal > div')
            self.assertTrue(dialog.evaluate('n => n.scrollHeight > n.clientHeight'))  # the modal scrolls
            dialog.evaluate('n => { n.scrollTop = n.scrollHeight; }')
            last = page.locator('.battle-reaction-row').last.locator('.sg-menu-trigger').first
            last.click()
            listbox = page.locator('.battle-reaction-row').last.locator('[role="listbox"]').first
            g = page.evaluate(self.GEOMETRY)
            self.assertTrue(g['bottom'] <= g['height'] and g['top'] >= 0, g)  # not cut off by the modal or the window
            self.assertTrue(g['onTop'], g)                                       # not hidden behind the modal's edge
            self.assertTrue(g['up'] and 0 <= g['above'] <= 4, g)                 # no room below: opens upwards
            # Scrolling the modal keeps the list open and attached to its menu.
            dialog.evaluate('n => { n.scrollTop -= 40; }')
            page.wait_for_timeout(50)
            self.assertTrue(listbox.is_visible())
            g = page.evaluate(self.GEOMETRY)
            self.assertTrue(0 <= g['above'] <= 4 or 0 <= g['below'] <= 4, g)
            # A press on the modal's scrollbar does not close it. Playwright's headless Chromium
            # hides scrollbars, so dispatch the press in the strip right of the modal's content
            # box, where a browser draws the vertical scrollbar.
            pressed = dialog.evaluate("""n => {
                const b = n.getBoundingClientRect(), right = b.left + n.clientLeft + n.clientWidth;
                if (b.right - right < 1) return false;
                n.dispatchEvent(new PointerEvent('pointerdown', {bubbles: true,
                    clientX: (right + b.right) / 2, clientY: b.top + b.height / 2}));
                return true;
            }""")
            self.assertTrue(pressed)
            self.assertTrue(listbox.is_visible())
            box = dialog.bounding_box()
            # A press elsewhere in the modal does close it.
            page.mouse.click(box['x'] + 10, box['y'] + 10)
            self.assertTrue(listbox.is_hidden())
            last.click()
            self.assertTrue(listbox.is_visible())
            # Scrolled out of the modal's view, it closes.
            dialog.evaluate('n => { n.scrollTop = 0; }')
            page.wait_for_timeout(50)
            self.assertTrue(listbox.is_hidden())
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
