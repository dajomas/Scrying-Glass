"""Chromium source-image UI with intercepted endpoints; not authenticated browser/server acceptance."""
import json
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from feedback_browser_fixture import install_feedback

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = {
    'goblin': [dict(provider='5e.tools', source='MM', species='goblin', selection_token='tok-g1',
                    image_url='https://img.test/g1.png'),
               dict(provider='5e.tools', source='XMM', species='goblin', selection_token='tok-g2',
                    image_url='https://img.test/g2.png'),
               dict(provider='Open5e', source='SRD', species='goblin', selection_token='tok-none', image_url=None)],
    'orc': [dict(provider='5e.tools', source='MM', species='orc', selection_token='tok-o1',
                 image_url='https://img.test/o1.png')],
}


class MonsterSourceImageBrowserTests(unittest.TestCase):
    def setUp(self):
        runtime = sync_playwright().start()
        self.addCleanup(runtime.stop)
        browser = runtime.chromium.launch(headless=True)
        self.addCleanup(browser.close)
        self.page = browser.new_page(viewport={'width': 1280, 'height': 900})
        self.page.set_default_timeout(5000)
        self.posts, self.lookups, self.errors = [], [], []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.route('http://fixture.test/', lambda route: route.fulfill(content_type='text/html', body=(
            '<select id="monsterBulkAction"><option value="">Actions</option>'
            '<option value="remove">Remove</option></select><div id="monsterAddNotification"></div>'
            '<div id="editModal" hidden><form id="editForm"></form></div>')))
        self.page.route('**/api/img-stub/**', lambda route: route.fulfill(status=204))
        self.page.route('https://img.test/**', lambda route: route.fulfill(status=200, content_type='image/png', body=b''))

        def lookup(route):
            species = route.request.url.split('species=')[1]
            self.lookups.append(species)
            route.fulfill(json={'status': 'ok', 'candidates': CANDIDATES.get(species, [])})
        self.page.route('**/api/monsters/lookup?*', lookup)

        def apply(route):
            self.posts.append(json.loads(route.request.post_data_buffer.decode()))
            route.fulfill(json={'count': 1})
        self.page.route('**/api/monsters/source-image', apply)
        self.page.goto('http://fixture.test/')
        install_feedback(self.page)
        self.page.add_script_tag(content="""
            let latest = {monsters: [{id:'a',name:'Goblin 1',monster_species:'goblin'},
                                     {id:'b',name:'Orc 1',monster_species:'orc'}]};
            let editing = null;
            const editModal = document.querySelector('#editModal');
            let chosen = [];
            function selectedIds() {return chosen;}
            async function runBulkAction() {window.legacyBulk = true;}
            async function request(url, options) {const r = await fetch(url, options); const d = await r.json();
                if (!r.ok) throw new Error(d.detail); return d;}
            async function load() {window.reloaded = true;}
            function monsterSourceLabel(c) {return c.provider + ' / ' + c.source;}
            function openEdit(kind, id) {
                editing = {kind, id};
                document.querySelector('#editForm').innerHTML =
                    '<label>Monster species <input name="monster_species" value="goblin"></label>' +
                    '<label>Replace image <input name="image" type="file"></label>';
                editModal.hidden = false;
            }
        """)
        self.page.add_script_tag(content=(ROOT / 'static/monster-source-image.js').read_text())

    def test_edit_button_stores_the_chosen_source_image(self):
        """Edit modal button looks up the species and stores the chosen image token."""
        self.page.evaluate("openEdit('monsters', 'a')")
        self.page.get_by_role('button', name='Select image from sources').click()
        tiles = self.page.locator('dialog .monster-image-option')
        tiles.first.wait_for()
        self.assertEqual(tiles.count(), 2)
        self.page.get_by_role('button', name='Use image: 5e.tools / XMM').click()
        form = self.page.locator('#editForm')
        self.assertEqual(form.locator('input[name="image_selection_token"]').input_value(), 'tok-g2')
        self.assertEqual(form.locator('input[name="image_species"]').input_value(), 'goblin')
        self.assertEqual(form.locator('.monster-edit-image-preview').get_attribute('src'), 'https://img.test/g2.png')
        self.assertEqual(self.lookups, ['goblin'])
        self.assertEqual(self.errors, [])

    def test_edit_cancel_keeps_no_source_choice(self):
        """Edit modal Cancel in the image dialog leaves no source choice."""
        self.page.evaluate("openEdit('monsters', 'a')")
        self.page.get_by_role('button', name='Select image from sources').click()
        self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.assertEqual(self.page.locator('input[name="image_selection_token"]').input_value(), '')
        self.assertEqual(self.page.locator('dialog').count(), 0)

    def test_bulk_option_applies_one_image_to_the_selected_monsters(self):
        """Monster action option sets one chosen source image on all selected monsters."""
        option = self.page.locator('#monsterBulkAction option[value="select-source-image"]')
        self.assertEqual(option.text_content(), 'Select image from sources')
        self.assertEqual(self.page.eval_on_selector('#monsterBulkAction', 'el => el.options[2].value'), 'remove')
        self.page.evaluate("chosen = ['a', 'b']; window.running = runBulkAction('monsters', 'select-source-image'); void 0")
        self.page.locator('dialog .monster-image-option').first.wait_for()
        self.assertEqual(self.page.locator('dialog .monster-image-option').count(), 3)
        self.page.get_by_role('button', name='Use image: orc: 5e.tools / MM').click()
        self.page.evaluate('window.running')
        self.assertEqual(self.posts, [{'ids': ['a', 'b'], 'image_selection_token': 'tok-o1', 'image_species': 'orc'}])
        self.assertTrue(self.page.evaluate('window.reloaded'))
        self.assertEqual(sorted(self.lookups), ['goblin', 'orc'])
        self.assertEqual(self.errors, [])

    def test_bulk_without_selection_reports_an_error(self):
        """Monster action without selected monsters reports an error and posts nothing."""
        self.page.evaluate("runBulkAction('monsters', 'select-source-image')")
        self.assertEqual(self.posts, [])
        self.assertEqual(self.lookups, [])
        self.assertFalse(self.page.evaluate('Boolean(window.legacyBulk)'))

    def test_other_bulk_actions_are_delegated(self):
        """Other monster actions still go to the original handler."""
        self.page.evaluate("runBulkAction('monsters', 'remove')")
        self.assertTrue(self.page.evaluate('window.legacyBulk'))


if __name__ == '__main__':
    unittest.main()
