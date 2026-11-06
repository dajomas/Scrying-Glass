"""SG-TODO-007: assembled Admin page with intercepted HTTP, not a live server."""
import copy
import json
from pathlib import Path
import unittest
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import test_encounter_features as fixtures
from web_html.admin_html import ADMIN_HTML

ROOT = Path(__file__).resolve().parents[1]


class MonsterButtonLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture = fixtures.FeatureTests(methodName='test_death_saves')
        fixture.setUp()
        try:
            cls.snapshot = fixture.c.public_state()
            cls.summary = fixture.f.summary()
        finally:
            fixture.tearDown()
        cls.snapshot['battle_order'] = []
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def open_page(self, width, active=False):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot['monsters'][0].update(
            active=active, ally=active, visible=active, in_turn=active,
            show_ac=active, show_hp=active, show_initiative=active)
        campaign = snapshot['active_campaign_id']
        apis = {
            '/api/state': snapshot, '/api/features': self.summary,
            '/api/campaigns': {'active': campaign, 'campaigns': [
                {'id': campaign, 'name': 'Default', 'description': '',
                 'setups': ['default'], 'last_setup': 'default'}], 'moved': []},
            '/api/setups': {'campaign': campaign, 'names': ['default']},
            '/api/me': {'username': 'dm', 'role': 'admin'},
        }
        page = self.browser.new_page(viewport={'width': width, 'height': 1000})
        self.addCleanup(page.close)
        page.set_default_timeout(5000)
        errors, mutations = [], []
        page.on('pageerror', lambda error: errors.append(str(error)))

        def route(request):
            path = urlsplit(request.request.url).path
            if path == '/':
                request.fulfill(content_type='text/html', body=ADMIN_HTML)
            elif path.startswith('/static/'):
                target = ROOT / path.lstrip('/')
                if not target.is_file():
                    request.fulfill(status=404)
                else:
                    kind = ('text/javascript' if target.suffix == '.js' else
                            'text/css' if target.suffix == '.css' else
                            'application/octet-stream')
                    request.fulfill(content_type=kind, body=target.read_bytes())
            elif path.startswith('/api/'):
                if request.request.method != 'GET':
                    mutations.append(path)
                request.fulfill(content_type='application/json',
                                body=json.dumps(apis.get(path, {})))
            else:
                request.fulfill(status=404)

        page.route('**/*', route)
        page.goto('http://fixture.test/', wait_until='load')
        # Legacy DOM includes the CSS-excluded Turn control; visible counts differ.
        page.wait_for_function("document.querySelectorAll('#monsters td button').length === 11")
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])
        return page, errors, mutations

    def test_single_line_geometry_and_local_overflow(self):
        for width in (1440, 768, 375):
            for active in (False, True):
                with self.subTest(width=width, active=active):
                    page, errors, mutations = self.open_page(width, active)
                    buttons = page.locator('#monsters td button:visible')
                    expected = ['Edit', 'In Battle' if active else 'Join Battle',
                                'Ally', 'Visible',
                                'AC on' if active else 'AC off',
                                'HP on' if active else 'HP off',
                                'Init on' if active else 'Init off',
                                'Reset', 'Restore statistics', 'Remove']
                    self.assertEqual([s.strip() for s in buttons.all_text_contents()], expected)
                    boxes = [buttons.nth(i).bounding_box() for i in range(len(expected))]
                    self.assertTrue(all(box is not None for box in boxes))
                    for index, box in enumerate(boxes):
                        self.assertAlmostEqual(box['y'], boxes[0]['y'], delta=1)
                        self.assertGreaterEqual(box['height'], 30)
                        self.assertGreater(box['width'], 20)
                        if index:
                            self.assertGreaterEqual(box['x'], boxes[index-1]['x'] + boxes[index-1]['width'])
                    self.assertEqual(page.locator('#monsters td:nth-child(6) button:visible').count(), 10)
                    self.assertEqual(page.locator('#monsters th').count(), 6)
                    for attr in ('data-ma', 'data-mally', 'data-mv'):
                        classes = page.locator('#monsters [' + attr + ']').get_attribute('class') or ''
                        self.assertEqual('on' in classes.split(), active)
                    for kind in ('monsters', 'characters'):
                        self.assertEqual(page.locator('#' + kind).get_by_role('button', name='Turn', exact=True).count(), 0)
                    region = page.get_by_role('region', name='Monsters', exact=True)
                    metrics = region.evaluate("""node => {
                        const scroll = document.querySelector('#adminScroll');
                        const table = node.firstElementChild;
                        const before = [scroll.scrollWidth, document.documentElement.scrollWidth];
                        table.remove();
                        const empty = [scroll.scrollWidth, document.documentElement.scrollWidth];
                        node.append(table);
                        return {before, empty, client: node.clientWidth,
                                total: node.scrollWidth, overflow: getComputedStyle(node).overflowX};
                    }""")
                    self.assertEqual(metrics['overflow'], 'auto')
                    if width <= 768:
                        self.assertGreater(metrics['total'], metrics['client'])
                    for before, empty in zip(metrics['before'], metrics['empty']):
                        self.assertLessEqual(before, empty + 1, 'Monster table must not widen its ancestors')
                    self.assertEqual(errors, [])
                    self.assertEqual(mutations, [])
                    page.close()

    def test_keyboard_reaches_every_button_and_scrolls_locally(self):
        for width in (1440, 768, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                region = page.get_by_role('region', name='Monsters', exact=True)
                region.focus()
                page.keyboard.press('Tab')
                self.assertEqual(page.locator(':focus').get_attribute('data-select-kind'), 'monsters')
                page.keyboard.press('Tab')
                self.assertIsNotNone(page.locator(':focus').get_attribute('data-mi'))
                buttons = page.locator('#monsters td button:visible')
                self.assertEqual(buttons.count(), 10)
                for key, indexes in (('Tab', range(10)), ('Shift+Tab', range(8, -1, -1))):
                    for index in indexes:
                        page.keyboard.press(key)
                        self.assertTrue(buttons.nth(index).evaluate('node => node === document.activeElement'))
                        self.assertTrue(buttons.nth(index).evaluate("""node => {
                            const b = node.getBoundingClientRect();
                            const region = document.querySelector('#monsters');
                            const left = region.getBoundingClientRect().left + region.clientLeft;
                            return b.left >= left - 1 && b.right <= left + region.clientWidth + 1;
                        }"""), f'{width=} {key=} {index=}')
                        if key == 'Tab' and index == 9 and region.evaluate('n => n.scrollWidth > n.clientWidth'):
                            self.assertGreater(region.evaluate('n => n.scrollLeft'), 0)
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()

    def test_edit_and_statistics_remain_keyboard_activatable(self):
        page, errors, mutations = self.open_page(375)
        page.locator('#monsters [data-edit]').focus()
        page.keyboard.press('Enter')
        page.wait_for_function("!document.querySelector('#editModal').hidden")
        self.assertTrue(page.locator('#editForm input[name=name]').is_visible())
        page.locator('#cancelEdit').focus()
        page.keyboard.press('Enter')
        page.wait_for_function("document.querySelector('#editModal').hidden")
        page.locator('#monsters [data-statistics]').focus()
        page.keyboard.press('Enter')
        page.wait_for_function("!document.querySelector('#statisticsModal').hidden")
        page.locator('#statisticsClose').focus()
        page.keyboard.press('Enter')
        page.wait_for_function("document.querySelector('#statisticsModal').hidden")
        self.assertTrue(page.locator('#monsters [data-statistics]').evaluate('node => node === document.activeElement'))
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])

    def test_removed_row_controls_stay_unavailable_after_refresh(self):
        page, errors, mutations = self.open_page(768)
        for cycle in range(3):
            for kind, columns, buttons in (('monsters', 6, 10), ('characters', 5, 7)):
                page.wait_for_function("([kind, count]) => document.querySelectorAll('#' + kind + ' th').length === count", arg=[kind, columns])
                self.assertEqual(page.locator(f'#{kind} td button:visible').count(), buttons)
                self.assertEqual(page.locator('#' + kind).get_by_role('button', name='Turn', exact=True).count(), 0)
                self.assertEqual(page.locator(f'#{kind} [data-d], #{kind} [data-h], #{kind} [data-cd], #{kind} [data-ch]').count(), 0)
                self.assertNotIn('HP change', page.locator(f'#{kind} th').all_text_contents())
                self.assertTrue(page.locator(f'#{kind} table').evaluate(
                    'table => [...table.rows].every(row => row.cells.length === table.rows[0].cells.length)'))
            if cycle < 2:
                page.evaluate('load(true)')
        page.add_script_tag(content=(ROOT / 'static/combatant-row-layout.js').read_text())
        page.evaluate('load(true)')
        page.wait_for_function("document.querySelectorAll('#monsters th').length === 6 && document.querySelectorAll('#characters th').length === 5")
        page.evaluate('closeBattleActions(); addBattleActionRow()')
        for action in ('damage', 'heal'):
            self.assertEqual(page.locator(f'#battleActionRows [data-action-kind] option[value="{action}"]').count(), 1)
        page.evaluate('closeBattleActions()')
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])


if __name__ == '__main__':
    unittest.main()
