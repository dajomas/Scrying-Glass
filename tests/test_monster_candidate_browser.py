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
        self.page.set_default_timeout(5000)
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
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
            async function request(url, options) {
                const result = await (await fetch(url, options)).json();
                window.lastLookupPayload = result;
                window.lookupPayloadBefore = JSON.stringify(result);
                return result;
            }
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

    def start_candidates(self, candidates):
        self.result = {'status': 'ok', 'candidates': candidates}
        self.page.locator('#monsterSpecies').focus()
        self.page.evaluate('window.lookupDone = lookupMonsterSpeciesStats(); void 0')
        self.page.get_by_role('dialog').wait_for()

    def test_six_book_labels_links_and_selected_raw_identity(self):
        labels = [('MM','Monster Manuals 2014'), ('XMM','Monster Manuals 2024'),
                  ('PHB','Player Handbook 2014'), ('XPHB','Player Handbook 2024'),
                  ('DMG','Dungeon Master Guide 2014'), ('XDMG','Dungeon Master Guide 2024')]
        candidates = [dict(found=True, name='Goblin', species='Goblin', provider='5e.tools',
                           source=code, legacy=code=='MM', ac=10+i, hp=str(5+i),
                           selection_token=f'token-{code}',
                           source_url=f'https://example.test/books/{code}/Goblin')
                      for i, (code, _) in enumerate(labels, 1)]
        self.start_candidates(candidates)
        for i, (code, label) in enumerate(labels, 1):
            text = f'{i}. Goblin — 5e.tools / {label} — AC {10+i}, HP {5+i}'
            self.assertEqual(self.page.get_by_role('button', name=text, exact=True).count(), 1)
            link = self.page.locator('dialog a').nth(i-1)
            self.assertEqual(link.get_attribute('href'), f'https://example.test/books/{code}/Goblin')
            self.assertEqual(link.get_attribute('target'), '_blank')
            self.assertEqual(link.get_attribute('rel'), 'noopener noreferrer')
        self.page.get_by_role('button', name='4. Goblin', exact=False).click()
        self.finish()
        self.assertEqual(self.token(), 'token-XPHB')
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '14')
        self.assertEqual(self.page.locator('#monsterHpRangeStart').input_value(), '9')
        self.assertIn('Player Handbook 2024', self.page.locator('#monsterAddNotification').inner_text())
        self.assertEqual(self.page.evaluate('lastLookupPayload.candidates.map(x => x.source)'), [code for code, _ in labels])
        self.assertTrue(self.page.evaluate('JSON.stringify(lastLookupPayload) === lookupPayloadBefore'))
        self.assertTrue(self.page.locator('#monsterSpecies').evaluate('node => node === document.activeElement'))
        self.assertEqual(self.errors, [])

    def test_unknown_codes_are_literal_without_invented_editions(self):
        codes = ['CUSTOM', 'XPBH', '__proto__', '<img src=x onerror=alert(1)>', '']
        self.start_candidates([dict(found=True, name='Goblin', species='Goblin', provider='5e.tools',
                                    source=code, legacy=True, ac=12, hp='7', selection_token=f'custom-{i}')
                               for i, code in enumerate(codes)])
        for i, code in enumerate(codes, 1):
            label = code or 'Source unavailable'
            text = f'{i}. Goblin — 5e.tools / {label} — AC 12, HP 7'
            self.assertEqual(self.page.get_by_role('button', name=text, exact=True).count(), 1)
        self.assertEqual(self.page.locator('dialog img, dialog script').count(), 0)
        self.page.get_by_role('button', name='3. Goblin', exact=False).click()
        self.finish()
        self.assertEqual(self.token(), 'custom-2')
        self.assertTrue(self.page.evaluate('JSON.stringify(lastLookupPayload) === lookupPayloadBefore'))
        self.assertEqual(self.errors, [])

    def test_dnd_beyond_popup_wording_and_cancel_stay_unchanged(self):
        self.start_candidates([dict(found=True, name='Goblin', species='Goblin', provider='D&D Beyond',
                                    source=code, legacy=legacy, ac=12, hp='7', selection_token=code)
                               for code, legacy in [('MM',True), ('XMM',False)]])
        for i, (code, edition) in enumerate([('MM','legacy'), ('XMM','current')], 1):
            text = f'{i}. Goblin — D&D Beyond / {code} / {edition} — AC 12, HP 7'
            self.assertEqual(self.page.get_by_role('button', name=text, exact=True).count(), 1)
        self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.finish()
        self.assertEqual(self.token(), 'manual')
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '')
        self.assertTrue(self.page.locator('#monsterSpecies').evaluate('node => node === document.activeElement'))
        self.assertEqual(self.errors, [])

if __name__ == '__main__':
    unittest.main()
