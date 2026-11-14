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
        self.posts, self.lookups, self.errors, self.urls = [], [], [], []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.route('http://fixture.test/', lambda route: route.fulfill(content_type='text/html', body=(
            '<select id="monsterBulkAction"><option value="">Actions</option>'
            '<option value="remove">Remove</option></select><div id="monsterAddNotification"></div>'
            '<div id="editModal" hidden><form id="editForm" class="edit-form" style="width:640px"></form></div>')))
        self.page.route('**/api/img-stub/**', lambda route: route.fulfill(status=204))
        self.page.route('https://img.test/**', lambda route: route.fulfill(status=200, content_type='image/png', body=b''))

        def lookup(route):
            species = route.request.url.split('species=')[1]
            self.lookups.append(species)
            self.urls.append(route.request.url)
            body = {'status': 'ok', 'candidates': CANDIDATES.get(species, [])}
            if species == 'orc':
                body['warning'] = 'Not available right now: Open5e. Showing images from the other sources.'
            route.fulfill(json=body)
        self.page.route('**/api/monsters/lookup?*', lookup)

        def apply(route):
            self.posts.append(json.loads(route.request.post_data_buffer.decode()))
            route.fulfill(json={'count': 1})
        self.page.route('**/api/monsters/source-image', apply)
        self.page.goto('http://fixture.test/')
        install_feedback(self.page)
        self.page.add_script_tag(content="""
            let latest = {monsters: [{id:'a',name:'Goblin 1',monster_species:'goblin'},
                                     {id:'b',name:'Orc 1',monster_species:'orc'},
                                     {id:'c',name:'Goblin 2',monster_species:'goblin'}]};
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
                    '<label>Ally <select><option>No</option></select></label>' +
                    '<label>Replace image <input name="image" type="file"></label>' +
                    '<div class="actions"><button>Save monster</button></div>';
                editModal.hidden = false;
            }
        """)
        self.page.add_style_tag(content=(ROOT / 'static/admin.css').read_text())
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

    def test_edit_button_is_bottom_aligned_and_status_is_below(self):
        """Edit button bottom-aligns with the file input and the Selected text sits under it."""
        self.page.evaluate("openEdit('monsters', 'a')")
        self.page.get_by_role('button', name='Select image from sources').click()
        self.page.get_by_role('button', name='Use image: 5e.tools / MM').click()
        box = lambda selector: self.page.locator(selector).bounding_box()
        button, file = box('.monster-source-image-edit button'), box('#editForm input[name="image"]')
        status = box('.monster-source-image-status')
        self.assertAlmostEqual(button['y'] + button['height'], file['y'] + file['height'], delta=1.5)
        self.assertGreaterEqual(status['y'], button['y'] + button['height'])
        self.assertAlmostEqual(status['x'], box('.monster-source-image-edit')['x'], delta=1.5)

    def test_bulk_offers_one_row_per_monster_with_one_lookup_per_species(self):
        """Monster action shows a row per selected monster, looks up each species once and applies per-monster choices."""
        self.page.evaluate("chosen = ['a', 'b', 'c']; window.running = runBulkAction('monsters', 'select-source-image'); void 0")
        dialog = self.page.locator('dialog')
        self.page.wait_for_function("document.querySelector('dialog')?.getAttribute('aria-busy') === 'false'")
        self.assertIn('Image lookup finished for 2 species', dialog.get_by_role('status').text_content())
        self.assertEqual(sorted(self.lookups), ['goblin', 'orc'])
        self.assertEqual(dialog.locator('.monster-source-image-row').count(), 3)
        for ident, count in (('a', 3), ('b', 2), ('c', 3)):
            row = dialog.locator(f'.monster-source-image-row[data-monster-id="{ident}"] .monster-image-option')
            self.assertEqual(row.count(), count)
        apply = dialog.get_by_role('button', name='Apply images')
        self.assertTrue(apply.is_disabled())
        dialog.get_by_role('button', name='Use image for Goblin 1: 5e.tools / XMM').click()
        dialog.get_by_role('button', name='Use image for Orc 1: 5e.tools / MM').click()
        self.assertEqual(apply.text_content(), 'Apply images (2)')
        apply.click()
        self.page.evaluate('window.running')
        self.assertEqual(self.posts, [{'items': [
            {'id': 'a', 'image_selection_token': 'tok-g2', 'image_species': 'goblin'},
            {'id': 'b', 'image_selection_token': 'tok-o1', 'image_species': 'orc'}]}])
        self.assertTrue(self.page.evaluate('window.reloaded'))
        self.assertEqual(self.errors, [])

    def test_bulk_shows_progress_and_reuses_lookups(self):
        """Monster action reports the lookup in progress and a second run reuses the species lookups."""
        release = []
        def slow(route):
            release.append(route)
        self.page.unroute('**/api/monsters/lookup?*')
        self.page.route('**/api/monsters/lookup?*', slow)
        self.page.evaluate("chosen = ['a', 'c']; window.running = runBulkAction('monsters', 'select-source-image'); void 0")
        status = self.page.locator('dialog').get_by_role('status')
        status.wait_for()
        self.assertIn('Looking up images', status.text_content())
        self.assertIn('Looking up images for goblin', self.page.locator('.monster-source-image-row-status').first.text_content())
        self.page.wait_for_function('true')
        while not release:
            self.page.wait_for_timeout(50)
        self.assertEqual(len(release), 1)
        release[0].fulfill(json={'status': 'ok', 'candidates': CANDIDATES['goblin']})
        self.page.wait_for_function("document.querySelector('dialog')?.getAttribute('aria-busy') === 'false'")
        self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.page.evaluate('window.running')
        self.page.evaluate("window.running = runBulkAction('monsters', 'select-source-image'); void 0")
        self.page.wait_for_function("document.querySelector('dialog')?.getAttribute('aria-busy') === 'false'")
        self.assertEqual(len(release), 1)
        self.assertEqual(self.posts, [])

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


    def test_bulk_shows_partial_lookup_warning_and_retries_it_later(self):
        """A partial lookup shows its warning in the row and is not reused next time."""
        self.page.evaluate("chosen = ['a', 'b']; window.running = runBulkAction('monsters', 'select-source-image'); void 0")
        self.page.wait_for_function("document.querySelector('dialog')?.getAttribute('aria-busy') === 'false'")
        self.assertTrue(all('images=true' in url for url in self.urls))
        orc = self.page.locator('.monster-source-image-row[data-monster-id="b"]')
        self.assertIn('Not available right now: Open5e', orc.locator('.monster-source-image-row-status').text_content())
        self.assertEqual(orc.locator('.monster-image-option').count(), 2)
        self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.page.evaluate("window.running = runBulkAction('monsters', 'select-source-image'); void 0")
        self.page.wait_for_function("document.querySelector('dialog')?.getAttribute('aria-busy') === 'false'")
        self.assertEqual(sorted(self.lookups), ['goblin', 'orc', 'orc'])
        self.assertEqual(self.errors, [])

if __name__ == '__main__':
    unittest.main()
