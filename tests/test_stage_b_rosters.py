"""Full Admin stage-B presentation with intercepted HTTP; not live-server acceptance."""
import copy
import unittest
from pathlib import Path
import test_monster_button_layout as fixture

ROOT = Path(__file__).resolve().parents[1]


class StageBRosterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture.MonsterButtonLayoutTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        fixture.MonsterButtonLayoutTests.tearDownClass.__func__(cls)

    def open_page(self, width):
        page, errors, mutations = fixture.MonsterButtonLayoutTests.open_page(self, width)
        state = copy.deepcopy(self.snapshot)
        monster = state['monsters'][0]
        monster.update(active=False, ally=False, visible=False, life_state='standing',
                       show_ac=False, show_hp=False, show_initiative=False,
                       initiative_roll=None, initiative=19)
        state['characters'][0]['life_state'] = 'standing'
        calls = []
        fail = [False]
        page.route('**/api/state', lambda route: route.fulfill(json=state))
        def patch(route):
            self.assertEqual(route.request.method, 'PATCH')
            data = route.request.post_data_json
            calls.append(data)
            if fail[0]:
                route.fulfill(status=409, json={'detail': 'fixture rejected'})
            else:
                monster.update(data)
                route.fulfill(json=monster)
        page.route('**/api/monsters/'+monster['id'], patch)
        page.evaluate('load(true)')
        page.wait_for_function("document.querySelector('#monsters [data-f=show_ac]')?.getAttribute('aria-pressed') === 'false'")
        return page, state, calls, fail, errors, mutations

    def test_labels_status_layout_and_repeated_refresh_are_read_only(self):
        for width in (375, 768, 1440):
            with self.subTest(width=width):
                page, state, calls, fail, errors, mutations = self.open_page(width)
                state['monsters'][0]['name'] = 'Very long monster name ' * 8
                state['monsters'][0]['monster_species'] = 'Long species ' * 8
                state['characters'][0]['name'] = 'Very long character name ' * 8
                for cycle in range(3):
                    page.evaluate('load(true)')
                    page.wait_for_function("document.querySelector('#monsters .sg-roster-state')?.textContent.includes('alive')")
                    for kind in ('monsters', 'characters'):
                        self.assertNotIn('standing', page.locator('#'+kind+' .sg-roster-state').inner_text())
                        self.assertEqual(page.locator('#'+kind+' .sg-roster-actions').count(), 1)
                        parts = page.locator('#'+kind+' .sg-roster-state-item')
                        self.assertEqual(parts.count(), 3)
                        self.assertTrue(parts.evaluate_all("nodes => nodes.every(n=>getComputedStyle(n).whiteSpace==='nowrap')"))
                    self.assertEqual(page.locator('#characters [data-cl]').inner_text(), 'alive')
                    self.assertEqual(page.locator('#monsters [data-t]').all_text_contents(), ['AC', 'HP', 'Init'])
                    raw = page.locator('#monsters input[data-mi]')
                    self.assertTrue(raw.get_attribute('aria-label').endswith('initiative raw roll'))
                    self.assertEqual(raw.input_value(), '')
                    self.assertEqual(raw.locator('..').inner_text().strip(), '')
                    self.assertEqual(page.locator('#monsters .sg-monster-initiative-total').inner_text(), 'Total: 19')
                    self.assertEqual(page.evaluate('latest.monsters[0].life_state'), 'standing')
                    self.assertEqual(page.evaluate('latest.characters[0].life_state'), 'standing')
                    metrics = page.locator('#monsters').evaluate("""node => {
                        const table=node.querySelector('table'), root=document.documentElement;
                        const before=root.scrollWidth;table.remove();const empty=root.scrollWidth;node.append(table);
                        return {before,empty,overflow:getComputedStyle(node).overflowX};
                    }""")
                    self.assertLessEqual(metrics['before'], metrics['empty']+1)
                    self.assertEqual(metrics['overflow'], 'auto')
                self.assertEqual(calls, [])
                self.assertEqual(mutations, [])
                self.assertEqual(errors, [])
                page.close()

    def test_fixed_toggles_use_state_not_labels_and_rejection_keeps_state(self):
        page, state, calls, fail, errors, mutations = self.open_page(375)
        for field, label in (('show_ac','AC'), ('show_hp','HP'), ('show_initiative','Init')):
            for value, key in ((True,'Enter'), (False,'Space')):
                before = len(calls)
                button = page.locator('#monsters [data-f="'+field+'"]')
                button.focus()
                page.keyboard.press(key)
                page.wait_for_function("([field,value]) => document.querySelector('#monsters [data-f='+field+']').getAttribute('aria-pressed')===String(value)", arg=[field,value])
                self.assertEqual(calls[before:], [{field: value}])
                self.assertEqual(button.inner_text(), label)
                self.assertEqual('on' in (button.get_attribute('class') or '').split(), value)
                mark = button.evaluate("n=>getComputedStyle(n,'::before').content")
                self.assertIn('✓' if value else '−', mark)
        fail[0] = True
        before = copy.deepcopy(state)
        button = page.locator('#monsters [data-f=show_ac]')
        button.focus()
        page.keyboard.press('Enter')
        page.get_by_text('fixture rejected', exact=True).wait_for()
        self.assertEqual(state, before)
        self.assertEqual(button.get_attribute('aria-pressed'), 'false')
        self.assertEqual(button.inner_text(), 'AC')
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])


if __name__ == '__main__':
    unittest.main()
