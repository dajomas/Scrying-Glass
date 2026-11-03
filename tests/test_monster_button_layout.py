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
        monster = snapshot['monsters'][0]
        monster.update(active=active, ally=active, visible=active,
                       in_turn=active, show_ac=active, show_hp=active,
                       show_initiative=active)
        campaign = snapshot['active_campaign_id']
        apis = {
            '/api/state': snapshot,
            '/api/features': self.summary,
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
        page.wait_for_function("document.querySelectorAll('#monsters td button').length === 13")
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])
        return page, errors, mutations

    def test_single_line_geometry_and_local_overflow(self):
        for width in (1440, 768, 375):
            for active in (False, True):
                with self.subTest(width=width, active=active):
                    page, errors, mutations = self.open_page(width, active)
                    buttons = page.locator('#monsters td button')
                    expected = ['Edit', 'In Battle' if active else 'Join Battle',
                                'Ally', 'Visible', 'Turn',
                                'AC on' if active else 'AC off',
                                'HP on' if active else 'HP off',
                                'Init on' if active else 'Init off',
                                'Reset', 'Restore statistics', 'Remove', 'Damage', 'Heal']
                    self.assertEqual([s.strip() for s in buttons.all_text_contents()], expected)
                    boxes = [buttons.nth(i).bounding_box() for i in range(13)]
                    self.assertTrue(all(box is not None for box in boxes))
                    for index, box in enumerate(boxes):
                        self.assertAlmostEqual(box['y'], boxes[0]['y'], delta=1)
                        self.assertGreaterEqual(box['height'], 30)
                        self.assertGreater(box['width'], 20)
                        if index:
                            self.assertGreaterEqual(box['x'], boxes[index-1]['x'] + boxes[index-1]['width'])
                    self.assertEqual(page.locator('#monsters td:nth-child(6) button').count(), 11)
                    self.assertEqual(page.locator('#monsters td:nth-child(7) button').count(), 2)
                    for attr in ('data-ma', 'data-mally', 'data-mv', 'data-mt'):
                        classes = page.locator('#monsters [' + attr + ']').get_attribute('class') or ''
                        self.assertEqual('on' in classes.split(), active)
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
                buttons = page.locator('#monsters td button')
                for index in range(13):
                    page.keyboard.press('Tab')
                    self.assertTrue(buttons.nth(index).evaluate('node => node === document.activeElement'))
                    self.assertTrue(buttons.nth(index).evaluate("""node => {
                        const b = node.getBoundingClientRect();
                        const r = document.querySelector('#monsters').getBoundingClientRect();
                        return b.left >= r.left - 1 && b.right <= r.right + 1;
                    }"""))
                self.assertGreater(region.evaluate('node => node.scrollLeft'), 0)
                page.keyboard.press('Shift+Tab')
                self.assertTrue(buttons.nth(11).evaluate('node => node === document.activeElement'))
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


if __name__ == '__main__':
    unittest.main()
