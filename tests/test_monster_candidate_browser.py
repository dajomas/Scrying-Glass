"""Chromium fixture with intercepted HTTP; not a live-provider end-to-end test."""
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

class CandidateBrowserTests(unittest.TestCase):
    def setUp(self):
        self.playwright = sync_playwright().start()
        self.addCleanup(self.playwright.stop)
        self.browser = self.playwright.chromium.launch(headless=True)
        self.addCleanup(self.browser.close)
        self.page = self.browser.new_page()
        self.result = {'status': 'ok', 'candidates': []}
        self.page.route('**/api/monsters/lookup?*', lambda route: route.fulfill(json=self.result))
        self.page.route('http://fixture.test/', lambda route: route.fulfill(content_type='text/html', body='''
            <form id="monsterForm"><input id="monsterSpecies" name="monster_species" value="Goblin">
            <input id="monsterAc"><input id="monsterHpRangeStart"><input id="monsterHpRangeEnd">
            <button>Add</button></form><input type="checkbox" id="monsterSpeciesLookupOverwrite">
            <p id="monsterAddNotification"></p>'''))
        self.page.goto('http://fixture.test/')
        prefix = (ROOT / 'static/admin.js').read_text().split('function setColorPreview')[0]
        self.page.add_script_tag(content=prefix + """
            const paneNotificationTimeouts = {monsters: null};
            const paneNotification = (kind, text) => document.querySelector('#monsterAddNotification').textContent = text;
            async function request(url, options) {return (await fetch(url, options)).json();}
        """)
        self.page.add_script_tag(content=(ROOT / 'static/monster-candidate-selection.js').read_text())

    def begin(self, count):
        self.result = {'status': 'ok', 'candidates': [
            dict(found=True, name='Goblin', species='Goblin', provider='5e.tools', source='MM',
                 legacy=True, ac=10+i, hp=str(5+i), selection_token=f'token-{i}') for i in range(1, count+1)]}
        self.page.evaluate('window.lookupDone = lookupMonsterSpeciesStats(); void 0')

    def finish(self):
        self.page.evaluate('window.lookupDone')

    def token(self):
        return self.page.evaluate("new FormData(document.querySelector('#monsterForm')).get('selection_token')")

    def test_single_and_zero(self):
        self.begin(1)
        self.finish()
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '11')
        self.assertEqual(self.page.locator('dialog').count(), 0)
        self.assertEqual(self.token(), 'token-1')
        self.begin(0)
        self.finish()
        self.assertEqual(self.token(), 'manual')
        self.assertIn('No usable', self.page.locator('#monsterAddNotification').inner_text())

    def test_choose_cancel_and_error(self):
        self.begin(2)
        self.page.get_by_role('dialog').wait_for()
        self.page.get_by_role('button', name='2. Goblin', exact=False).click()
        self.finish()
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '12')
        self.assertEqual(self.token(), 'token-2')
        self.begin(2)
        self.page.get_by_role('dialog').wait_for()
        self.page.keyboard.press('Escape')
        self.finish()
        self.assertEqual(self.token(), 'manual')
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '12')
        self.result = {'status': 'error', 'reason': 'Provider failed; retry.'}
        self.page.evaluate('lookupMonsterSpeciesStats()')
        self.assertIn('Provider failed', self.page.locator('#monsterAddNotification').inner_text())

    def test_edit_preservation_and_pending_submit(self):
        self.page.locator('#monsterSpeciesLookupOverwrite').check()
        self.begin(2)
        self.page.get_by_role('dialog').wait_for()
        self.assertTrue(self.page.evaluate("""!document.querySelector('#monsterForm').dispatchEvent(
            new Event('submit', {bubbles: true, cancelable: true}))"""))
        self.page.evaluate("document.querySelector('#monsterAc').value = '99'")
        self.page.get_by_role('button', name='1. Goblin', exact=False).click()
        self.finish()
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '99')
        self.assertEqual(self.page.locator('#monsterHpRangeStart').input_value(), '6')

    def test_species_change_closes_popup(self):
        self.begin(2)
        self.page.get_by_role('dialog').wait_for()
        self.page.evaluate("""const input = document.querySelector('#monsterSpecies');
            input.value = 'Orc'; input.dispatchEvent(new Event('input', {bubbles: true}));""")
        self.finish()
        self.assertEqual(self.page.locator('dialog').count(), 0)
        self.assertEqual(self.token(), 'manual')
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '')

if __name__ == '__main__':
    unittest.main()
