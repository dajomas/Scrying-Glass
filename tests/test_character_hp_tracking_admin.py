"""SG-TODO-024: Admin controls for optional character HP tracking (assembled Admin, intercepted HTTP)."""
import copy
import json
import unittest


class CharacterHpTrackingAdminTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def open_page(self, untracked=False):
        self.snapshot = copy.deepcopy(type(self).snapshot)
        self.character = self.snapshot['characters'][0]
        if untracked:
            self.character['track_hp'] = False
        page, errors, _ = self.rows.open_page(self, 1440)
        page.wait_for_function("typeof window.scryingTracksHp === 'function'")
        self.bodies = []

        def capture(route):
            request = route.request
            if request.method != 'GET':
                self.bodies.append((request.method, request.url.split('/api/', 1)[1], json.loads(request.post_data or '{}')))
            route.fulfill(content_type='application/json', body='{}')
        page.route('**/api/characters**', capture)
        return page, errors

    def test_add_character_without_tracking_sends_no_hp(self):
        page, errors = self.open_page()
        shown = "() => { const hp = document.querySelector('#characterHp'); return hp.required && getComputedStyle(hp.closest('label')).display !== 'none'; }"
        self.assertTrue(page.evaluate("document.querySelector('#characterTrackHp').checked"))
        self.assertTrue(page.evaluate(shown))
        page.evaluate("""() => { const box = document.querySelector('#characterTrackHp');
            box.checked = false; box.dispatchEvent(new Event('change')); }""")
        self.assertFalse(page.evaluate(shown))
        page.evaluate("""() => { document.querySelector('#characterName').value = 'Rogue';
            document.querySelector('#characterForm').requestSubmit(); }""")
        page.wait_for_function('() => document.querySelector("#characterName").value === ""')
        method, path, body = self.bodies[0]
        self.assertEqual((method, path), ('POST', 'characters'))
        self.assertEqual(body['track_hp'], False)
        self.assertNotIn('hp', body)
        # Reset restores the default: tracking on, HP field shown again.
        page.wait_for_function('() => document.querySelector("#characterTrackHp").checked')
        page.wait_for_function(shown)
        self.assertEqual(errors, [])

    def test_untracked_character_hides_hp_in_roster_and_edit(self):
        page, errors = self.open_page(untracked=True)
        ident = self.character['id']
        cell = page.locator(f'#characters .sg-character-hp').first
        self.assertEqual(cell.text_content(), 'Not tracked')
        page.locator(f'#characters button[data-edit="{ident}"]').click()
        form = page.locator('#editForm')
        self.assertFalse(form.locator('input[name="track_hp"]').is_checked())
        self.assertFalse(form.locator('input[name="hp"]').is_visible())
        self.assertFalse(form.locator('input[name="max_hp"]').is_visible())
        form.locator('button:has-text("Save character")').click()
        page.wait_for_function('() => document.querySelector("#editModal").hidden')
        method, path, body = self.bodies[0]
        self.assertEqual((method, path), ('PATCH', f'characters/{ident}'))
        self.assertEqual(body['track_hp'], False)
        self.assertNotIn('hp', body)
        self.assertNotIn('max_hp', body)
        self.assertEqual(errors, [])

    def test_edit_track_hp_checkbox_sits_beside_its_text(self):
        for untracked in (True, False):
            with self.subTest(untracked=untracked):
                page, errors = self.open_page(untracked=untracked)
                page.locator(f'#characters button[data-edit="{self.character["id"]}"]').click()
                layout = page.locator('#editForm label.sg-track-hp-field').evaluate('''label => {
                    const box = label.querySelector('input').getBoundingClientRect();
                    const range = document.createRange(); range.selectNodeContents(label);
                    const text = [...range.getClientRects()].pop();
                    const mid = r => r.top + r.height / 2;
                    // the control in the other column of the same grid row
                    const row = label.getBoundingClientRect();
                    const peer = [...label.parentElement.querySelectorAll('label > input:not([type=checkbox])')]
                        .map(n => n.getBoundingClientRect())
                        .find(r => r.height && Math.abs(r.bottom - row.bottom) < 40 && r.left > row.right);
                    return {beside: text.left >= box.right, level: Math.abs(mid(text) - mid(box)),
                            text: label.textContent.trim(), peer: peer ? Math.abs(mid(peer) - mid(box)) : null};
                }''')
                self.assertTrue(layout['beside'], layout)          # checkbox, then its text, on one line
                self.assertLessEqual(layout['level'], 3, layout)
                self.assertEqual(layout['text'], 'Track HP')
                if layout['peer'] is not None:
                    self.assertLessEqual(layout['peer'], 3, layout)  # level with the input beside it
                self.assertEqual(errors, [])
                page.close()

    def test_tracked_character_edit_still_sends_hp(self):
        page, errors = self.open_page()
        ident = self.character['id']
        page.locator(f'#characters button[data-edit="{ident}"]').click()
        form = page.locator('#editForm')
        self.assertTrue(form.locator('input[name="track_hp"]').is_checked())
        form.locator('button:has-text("Save character")').click()
        page.wait_for_function('() => document.querySelector("#editModal").hidden')
        body = self.bodies[0][2]
        self.assertEqual((body['track_hp'], body['hp'], body['max_hp']),
                         (True, self.character['hp'], self.character['max_hp']))
        self.assertEqual(errors, [])

    def test_bulk_offers_track_and_do_not_track(self):
        page, errors = self.open_page()
        values = page.evaluate("[...document.querySelector('#characterBulkAction').options].map(o => o.value)")
        self.assertEqual(values[-3:], ['track-hp', 'untrack-hp', 'remove'])
        self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
