"""SG-TODO-012: full Admin with intercepted HTTP, not live persistence."""
import copy
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CharacterHpDisplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def test_asset_contract(self):
        end = (ROOT / 'templates/admin/190_document_end.html').read_text()
        self.assertEqual(end.count('/static/character-hp-display.js?v=1'), 1)
        self.assertLess(end.index('/static/admin-rosters.js'), end.index('/static/character-hp-display.js'))
        source = (ROOT / 'static/character-hp-display.js').read_text()
        self.assertLessEqual(len(source.encode()), 20000)
        for forbidden in ('fetch(', 'innerHTML', 'keydown', 'localStorage', 'subtree: true'):
            self.assertNotIn(forbidden, source)

    def test_edit_rejection_retry_and_reload(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.rows.open_page(self, width)
                state = copy.deepcopy(self.snapshot)
                character = state['characters'][0]
                identifier = str(character['id'])
                attempts = []
                def serve_state(route):
                    route.fulfill(content_type='application/json', body=json.dumps(state))
                def save(route):
                    self.assertEqual(route.request.method, 'PATCH')
                    payload = route.request.post_data_json
                    attempts.append(payload)
                    if len(attempts) == 1:
                        route.fulfill(status=400, content_type='application/json', body='{"detail":"Fixture HP rejection"}')
                    else:
                        character.update(payload)
                        route.fulfill(content_type='application/json', body='{}')
                page.route('**/api/state', serve_state)
                page.route('**/api/characters/' + identifier, save)
                page.wait_for_function("document.querySelectorAll('#characters .sg-character-hp').length > 0")
                before = f"{character['hp']}/{character['max_hp']}"
                self.assertEqual(page.locator('#characters .sg-character-hp').first.inner_text(), before)
                self.assertEqual(page.locator('#characters [data-chp], #characters [data-cmaxhp]').count(), 0)
                self.assertEqual(page.locator('#characters [data-ci]').count(), len(state['characters']))
                page.locator('#characters [data-edit]').first.focus()
                page.keyboard.press('Enter')
                page.wait_for_function("!document.querySelector('#editModal').hidden")
                page.locator('#editForm [name=hp]').fill('0')
                page.locator('#editForm [name=max_hp]').fill('20')
                page.locator('#editForm button:not([type=button])').click()
                page.wait_for_function("document.querySelector('#characterAddNotification').textContent.includes('Fixture HP rejection')")
                self.assertTrue(page.locator('#editModal').is_visible())
                self.assertEqual(page.locator('#editForm [name=hp]').input_value(), '0')
                self.assertEqual(page.locator('#editForm [name=max_hp]').input_value(), '20')
                self.assertEqual(page.locator('#characters .sg-character-hp').first.inner_text(), before)
                page.locator('#editForm [name=max_hp]').fill('-1')
                page.locator('#editForm button:not([type=button])').click()
                self.assertEqual(len(attempts), 1)
                self.assertFalse(page.locator('#editForm').evaluate('n => n.checkValidity()'))
                page.locator('#editForm [name=max_hp]').fill('20')
                page.locator('#editForm button:not([type=button])').click()
                page.wait_for_function("document.querySelector('#editModal').hidden && document.querySelector('#characters .sg-character-hp')?.textContent === '0/20'")
                self.assertEqual(len(attempts), 2)
                self.assertEqual(attempts[-1]['hp'], 0)
                self.assertEqual(attempts[-1]['max_hp'], 20)
                page.reload(wait_until='load')
                page.wait_for_function("document.querySelector('#characters .sg-character-hp')?.textContent === '0/20'")
                page.add_script_tag(content=(ROOT / 'static/character-hp-display.js').read_text())
                self.assertEqual(page.locator('#characters .sg-character-hp').count(), len(state['characters']))
                self.assertEqual(page.locator('#characters [data-chp], #characters [data-cmaxhp]').count(), 0)
                self.assertEqual(len(attempts), 2)
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()


if __name__ == '__main__':
    unittest.main()
