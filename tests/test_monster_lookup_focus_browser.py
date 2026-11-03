"""Production typing/blur wiring with Chromium and intercepted lookup HTTP.

The fixture executes the real lookup function, species event listeners and
candidate extension, not the entire Admin page or a live provider.
"""
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

class LookupFocusRegressionTests(unittest.TestCase):
    def setUp(self):
        playwright = sync_playwright().start()
        self.addCleanup(playwright.stop)
        browser = playwright.chromium.launch(headless=True)
        self.addCleanup(browser.close)
        self.page = browser.new_page()
        self.page.set_default_timeout(5000)
        self.calls = []
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.route('http://fixture.test/', lambda route: route.fulfill(content_type='text/html', body='''
            <form id="monsterForm"><input id="monsterSpecies" name="monster_species">
            <input id="monsterAc"><input id="monsterHpRangeStart"><input id="monsterHpRangeEnd">
            <button type="button" id="outside">Outside</button></form>
            <input type="checkbox" id="monsterSpeciesLookupOverwrite">
            <p id="monsterAddNotification"></p>'''))
        def lookup(route):
            self.calls.append(route.request.url)
            route.fulfill(json={'status': 'ok', 'candidates': [
                {'found': True, 'name': 'Crawling Claw', 'species': 'Crawling Claw',
                 'provider': '5e.tools', 'source': source, 'legacy': source == 'MM',
                 'ac': 12 + index, 'hp': str(7 + index), 'selection_token': f'token-{index}'}
                for index, source in enumerate(['MM', 'XMM'])]})
        self.page.route('**/api/monsters/lookup?*', lookup)
        self.page.goto('http://fixture.test/')
        source = (ROOT / 'static/admin.js').read_text(encoding='utf-8')
        prefix = source.split('function setColorPreview', 1)[0]
        start = source.index("document.querySelector('#monsterSpecies').addEventListener(")
        end = source.index("document.querySelector('#monsterUpload').onsubmit", start)
        # Keep production blur wiring if reintroduced: that is what this test detects.
        listeners = source[start:end]
        self.page.add_script_tag(content=prefix + """
            const paneNotificationTimeouts = {monsters: null};
            const paneNotification = (kind, text) => document.querySelector('#monsterAddNotification').textContent = text;
            async function request(url, options) {return (await fetch(url, options)).json();}
        """ + listeners)
        self.page.add_script_tag(content=(ROOT / 'static/monster-candidate-selection.js').read_text(encoding='utf-8'))
        self.page.evaluate("""() => {
            window.dialogOpens = 0;
            const original = HTMLDialogElement.prototype.showModal;
            HTMLDialogElement.prototype.showModal = function() {
                window.dialogOpens++; return original.call(this);
            };
        }""")
        self.assertEqual(self.page.evaluate('window.dialogOpens'), 0)

    def assert_no_extra_requests(self):
        # Longer than two 600 ms debounce periods; allow blur work to surface.
        self.page.wait_for_timeout(1500)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.page.evaluate('window.dialogOpens'), 1)
        self.assertEqual(self.errors, [])

    def type_and_open(self):
        species = self.page.locator('#monsterSpecies')
        species.click()
        species.press_sequentially('Crawling Claw', delay=15)
        self.page.get_by_role('dialog').wait_for(state='visible')
        self.page.wait_for_function("document.querySelector('dialog').contains(document.activeElement)")
        self.assert_no_extra_requests()
        self.assertEqual(self.page.get_by_role('dialog').count(), 1)

    def token(self):
        return self.page.evaluate("new FormData(document.querySelector('#monsterForm')).get('selection_token')")

    def test_typing_opens_stable_popup_and_selection_does_not_relookup(self):
        self.type_and_open()
        self.page.get_by_role('button', name='2. Crawling Claw', exact=False).click()
        self.page.wait_for_function("document.querySelector('#monsterAc').value === '13'")
        self.assertEqual(self.page.locator('#monsterHpRangeStart').input_value(), '8')
        self.assertEqual(self.token(), 'token-1')
        self.assert_no_extra_requests()
        self.assertEqual(self.page.get_by_role('dialog').count(), 0)
        self.assertTrue(self.page.locator('#monsterSpecies').evaluate('node => node === document.activeElement'))
        self.page.locator('#outside').click()
        self.assert_no_extra_requests()

    def test_cancel_restores_focus_without_relookup(self):
        self.type_and_open()
        self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.page.wait_for_function("!document.querySelector('dialog')")
        self.assert_no_extra_requests()
        self.assertEqual(self.token(), 'manual')
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '')
        self.assertTrue(self.page.locator('#monsterSpecies').evaluate('node => node === document.activeElement'))

    def test_escape_restores_focus_without_relookup(self):
        self.type_and_open()
        self.page.keyboard.press('Escape')
        self.page.wait_for_function("!document.querySelector('dialog')")
        self.assert_no_extra_requests()
        self.assertEqual(self.token(), 'manual')
        self.assertTrue(self.page.locator('#monsterSpecies').evaluate('node => node === document.activeElement'))

if __name__ == '__main__':
    unittest.main()
