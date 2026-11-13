"""Chromium fixture with intercepted HTTP; not a live-provider end-to-end test."""
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from feedback_browser_fixture import install_feedback

ROOT = Path(__file__).resolve().parents[1]
UNAVAILABLE_OFFER = ' — Initiative bonus unavailable: No supported explicit source modifier. — No image available'

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
        self.page.route('http://fixture.test/', lambda route: route.fulfill(content_type='text/html', body="""
            <form id="monsterForm"><input id="monsterSpecies" name="monster_species" value="Goblin">
            <input id="monsterAc"><input id="monsterHpRangeStart"><input id="monsterHpRangeEnd">
            <input id="monsterInitiativeBonus" name="initiative_bonus" type="number" step="1">
            <p id="monsterInitiativeBonusHelp">Initiative bonus help.</p>
            <button>Add</button></form><input type="checkbox" id="monsterSpeciesLookupOverwrite">
            <p id="monsterAddNotification"></p>"""))
        self.page.route('https://img.test/**', lambda route: route.fulfill(content_type='image/svg+xml',
            body='<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"/>'))
        self.page.goto('http://fixture.test/')
        install_feedback(self.page)
        self.assertEqual(self.page.locator('[data-sg-feedback-mounted]').count(), 1)
        prefix = (ROOT / 'static/admin.js').read_text().split('function setColorPreview')[0]
        self.page.add_script_tag(content=prefix + """
            const paneNotification = (kind, text, options) => window.scryingAdminFeedback.deliver(kind, text, options);
            async function request(url, options) {
                const result = await (await fetch(url, options)).json();
                window.lastLookupPayload = result;
                window.lookupPayloadBefore = JSON.stringify(result);
                return result;
            }
        """)
        self.page.add_script_tag(content=(ROOT / 'static/monster-image-choice.js').read_text())
        self.page.add_script_tag(content=(ROOT / 'static/monster-candidate-selection.js').read_text())

    def launch_lookup(self):
        self.page.evaluate("""
            window.lookupSettled = false;
            window.lookupDone = lookupMonsterSpeciesStats().finally(() => {window.lookupSettled = true;});
            void 0;
        """)

    def begin(self, count):
        self.start_candidates([dict(found=True, name='Goblin', species='Goblin', provider='5e.tools',
            source='MM', legacy=True, ac=10+i, hp=str(5+i), selection_token=f'token-{i}')
            for i in range(1, count+1)])

    def finish(self):
        self.page.wait_for_function('() => window.lookupSettled === true', timeout=5000)
        self.page.evaluate('window.lookupDone')
        self.assertEqual(self.page.get_by_role('dialog', name='Review monster initiative bonus', exact=True).count(), 0)
        self.assertEqual(self.errors, [])

    def token(self):
        return self.page.evaluate("new FormData(document.querySelector('#monsterForm')).get('selection_token')")

    def start_candidates(self, candidates):
        self.result = {'status': 'ok', 'candidates': candidates}
        self.page.locator('#monsterSpecies').focus()
        self.launch_lookup()
        if len(candidates) > 1:
            self.page.get_by_role('dialog', name='Select monster candidate', exact=True).wait_for()

    def test_single_and_zero(self):
        self.begin(1)
        self.finish()
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '11')
        self.assertEqual(self.page.locator('dialog').count(), 0)
        self.assertEqual(self.token(), 'token-1')
        self.assertIn('overwrite option above also applies', self.page.locator('#monsterInitiativeBonusHelp').inner_text())
        self.begin(0)
        self.finish()
        self.assertEqual(self.token(), 'manual')
        self.assertIn('No usable', self.page.locator('#monsterAddNotification').inner_text())

    def test_choose_cancel_and_error(self):
        self.begin(2)
        self.page.get_by_role('button', name='2. Goblin', exact=False).click()
        self.finish()
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '12')
        self.assertEqual(self.token(), 'token-2')
        self.begin(2)
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
        self.assertTrue(self.page.evaluate("""!document.querySelector('#monsterForm').dispatchEvent(
            new Event('submit', {bubbles: true, cancelable: true}))"""))
        self.page.evaluate("document.querySelector('#monsterAc').value = '99'")
        self.page.get_by_role('button', name='1. Goblin', exact=False).click()
        self.finish()
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '99')
        self.assertEqual(self.page.locator('#monsterHpRangeStart').input_value(), '6')

    def test_species_change_closes_popup(self):
        self.begin(2)
        self.page.evaluate("const input = document.querySelector('#monsterSpecies'); input.value='Orc'; input.dispatchEvent(new Event('input', {bubbles:true}));")
        self.finish()
        self.assertEqual(self.page.locator('dialog').count(), 0)
        self.assertEqual(self.token(), 'manual')
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '')

    def test_six_book_labels_links_and_selected_raw_identity(self):
        labels = [('MM','Monster Manuals 2014'), ('XMM','Monster Manuals 2024'),
                  ('PHB','Player Handbook 2014'), ('XPHB','Player Handbook 2024'),
                  ('DMG','Dungeon Master Guide 2014'), ('XDMG','Dungeon Master Guide 2024')]
        candidates = [dict(found=True, name='Goblin', species='Goblin', provider='5e.tools',
            source=code, legacy=code=='MM', ac=10+i, hp=str(5+i), selection_token=f'token-{code}',
            source_url=f'https://example.test/books/{code}/Goblin') for i, (code, _) in enumerate(labels, 1)]
        self.start_candidates(candidates)
        # The popup sorts rows by book label within a provider (SG-TODO-017 follow-up).
        server = {code: i for i, (code, _) in enumerate(labels, 1)}
        shown = sorted(labels, key=lambda item: item[1])
        for row, (code, label) in enumerate(shown, 1):
            i = server[code]
            text = f'{row}. Goblin — 5e.tools / {label} — AC {10+i}, HP {5+i}' + UNAVAILABLE_OFFER
            self.assertEqual(self.page.get_by_role('button', name=text, exact=True).count(), 1)
            link = self.page.locator('dialog a').nth(row-1)
            self.assertEqual(link.get_attribute('href'), f'https://example.test/books/{code}/Goblin')
            self.assertEqual(link.get_attribute('target'), '_blank')
            self.assertEqual(link.get_attribute('rel'), 'noopener noreferrer')
        self.page.get_by_role('button', name='6. Goblin — 5e.tools / Player Handbook 2024', exact=False).click()
        self.finish()
        self.assertEqual(self.token(), 'token-XPHB')
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '14')
        self.assertEqual(self.page.locator('#monsterHpRangeStart').input_value(), '9')
        self.assertIn('Player Handbook 2024', self.page.locator('#monsterAddNotification').inner_text())
        self.assertEqual(self.page.evaluate('lastLookupPayload.candidates.map(x => x.source)'), [code for code, _ in labels])
        self.assertTrue(self.page.evaluate('JSON.stringify(lastLookupPayload) === lookupPayloadBefore'))
        self.assertTrue(self.page.locator('#monsterSpecies').evaluate('node => node === document.activeElement'))

    def test_unknown_codes_are_literal_without_invented_editions(self):
        codes = ['CUSTOM', 'XPBH', '__proto__', '<img src=x onerror=alert(1)>', '']
        self.start_candidates([dict(found=True, name='Goblin', species='Goblin', provider='5e.tools',
            source=code, legacy=True, ac=12, hp='7', selection_token=f'custom-{i}') for i, code in enumerate(codes)])
        # Rows are sorted by label; check each literal label appears exactly once.
        shown = self.page.locator('dialog button').all_inner_texts()
        for code in codes:
            suffix = f'. Goblin — 5e.tools / {code or "Source unavailable"} — AC 12, HP 7' + UNAVAILABLE_OFFER
            self.assertEqual(sum(1 for text in shown if text.split('.', 1)[0].isdigit()
                                 and text[text.index('.'):] == suffix), 1, code)
        self.assertEqual(self.page.locator('dialog img, dialog script').count(), 0)
        self.page.get_by_role('button', name='Goblin — 5e.tools / __proto__ —', exact=False).click()
        self.finish()
        self.assertEqual(self.token(), 'custom-2')
        self.assertTrue(self.page.evaluate('JSON.stringify(lastLookupPayload) === lookupPayloadBefore'))

    def test_popup_notes_whether_an_image_is_available(self):
        self.start_candidates([dict(found=True, name='Goblin', species='Goblin', provider='D&D Beyond',
            source=code, legacy=False, ac=12, hp='7', selection_token=code, image_url=image)
            for code, image in [('A', 'https://example.test/goblin.png'), ('B', None), ('C', '')]])
        names = self.page.locator('dialog .monster-candidate-row > button').all_inner_texts()
        self.assertEqual([name.rsplit(' — ', 1)[1] for name in names],
                         ['Image available', 'No image available', 'No image available'])
        self.assertEqual(self.page.locator('dialog img').count(), 0)
        self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.finish()

    def test_source_link_and_attribution_sit_below_the_button(self):
        self.start_candidates([
            dict(found=True, name='Goblin', species='Goblin', provider='D&D Beyond', source='X', legacy=True,
                 ac=12, hp='7', selection_token='a', source_url='https://www.dndbeyond.com/monsters/1-goblin',
                 attribution='Basic Rules (2014), pg. 138 via D&D Beyond'),
            dict(found=True, name='Goblin', species='Goblin', provider='5e.tools', source='MM', legacy=True,
                 ac=12, hp='7', selection_token='b', attribution='MM, page 166 via 5e.tools'),
            dict(found=True, name='Goblin', species='Goblin', provider='Open5e', source='SRD', ac=12, hp='7',
                 selection_token='c', source_url='https://api.open5e.com/v2/creatures/srd_goblin/')])
        details = self.page.locator('dialog .monster-candidate-details')
        self.assertEqual(details.all_inner_texts(), [
            'View source · Basic Rules (2014), pg. 138 via D&D Beyond', 'MM, page 166 via 5e.tools', 'View source'])
        for row in range(3):
            button = self.page.locator('dialog .monster-candidate-row > button').nth(row).bounding_box()
            below = details.nth(row).bounding_box()
            self.assertGreaterEqual(below['y'], button['y'] + button['height'] - 1)
        self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.finish()

    def test_dnd_beyond_source_wording_and_candidate_cancel(self):
        self.start_candidates([dict(found=True, name='Goblin', species='Goblin', provider='D&D Beyond',
            source=code, legacy=legacy, ac=12, hp='7', selection_token=code)
            for code, legacy in [('MM',True), ('XMM',False)]])
        for i, (code, edition) in enumerate([('MM','legacy'), ('XMM','current')], 1):
            text = f'{i}. Goblin — D&D Beyond / {code} / {edition} — AC 12, HP 7' + UNAVAILABLE_OFFER
            self.assertEqual(self.page.get_by_role('button', name=text, exact=True).count(), 1)
        self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.finish()
        self.assertEqual(self.token(), 'manual')
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '')
        self.assertTrue(self.page.locator('#monsterSpecies').evaluate('node => node === document.activeElement'))

    def images(self, own):
        return [dict(found=True, name='Goblin', species='Goblin', provider='5e.tools', source='MM', legacy=True,
                     ac=11, hp='6', selection_token='token-1', image_url=own),
                dict(found=True, name='Goblin', species='Goblin', provider='5e.tools', source='XMM', legacy=False,
                     ac=12, hp='7', selection_token='token-2', image_url='https://img.test/xmm.svg')]

    def form_value(self, name):
        return self.page.evaluate(f"new FormData(document.querySelector('#monsterForm')).get('{name}')")

    def test_other_image_can_replace_the_selected_image(self):
        self.start_candidates(self.images('https://img.test/mm.svg'))
        self.page.get_by_role('button', name='1. Goblin', exact=False).click()
        dialog = self.page.get_by_role('dialog', name='Select monster image', exact=True)
        dialog.wait_for()
        self.assertEqual(dialog.locator('img').count(), 2)
        self.assertEqual(dialog.locator('img').first.get_attribute('src'), 'https://img.test/mm.svg')
        self.page.get_by_role('button', name='Use image: 5e.tools / Monster Manuals 2024', exact=True).click()
        self.finish()
        self.assertEqual(self.token(), 'token-1')
        self.assertEqual(self.form_value('image_selection_token'), 'token-2')

    def test_cancel_keeps_no_image_and_choose_again_reuses_results(self):
        self.start_candidates(self.images(None))
        self.page.get_by_role('button', name='1. Goblin', exact=False).click()
        dialog = self.page.get_by_role('dialog', name='Select monster image', exact=True)
        dialog.wait_for()
        self.assertEqual(dialog.locator('img').count(), 1)
        dialog.get_by_role('button', name='Cancel', exact=True).click()
        self.finish()
        self.assertEqual(self.token(), 'token-1')
        self.assertIsNone(self.form_value('image_selection_token'))
        again = self.page.get_by_role('button', name='Choose again', exact=True)
        self.assertTrue(again.is_visible())
        self.result = {'status': 'error', 'reason': 'Should not refetch.'}
        self.page.locator('#monsterSpeciesLookupOverwrite').check()
        self.page.evaluate("window.lookupSettled = false")
        again.click()
        self.page.get_by_role('dialog', name='Select monster candidate', exact=True).wait_for()
        self.page.evaluate("window.lookupDone = new Promise(r => {window.lookupSettled = true; r();})")
        self.page.get_by_role('button', name='2. Goblin', exact=False).click()
        self.page.wait_for_function("new FormData(document.querySelector('#monsterForm')).get('selection_token') === 'token-2'")
        self.assertEqual(self.page.locator('#monsterAc').input_value(), '12')
        self.page.evaluate("const input = document.querySelector('#monsterSpecies'); input.value='Orc'; input.dispatchEvent(new Event('input', {bubbles:true}));")
        self.assertFalse(again.is_visible())
        self.assertEqual(self.errors, [])

    def test_choose_again_keeps_current_monster_and_image_until_replaced(self):
        self.page.evaluate("""window.shownImage = 'unset';
            document.addEventListener('scrying:monster-selection', e => {window.shownImage = e.detail?.image_url ?? null;});""")
        self.start_candidates(self.images('https://img.test/mm.svg'))
        self.page.get_by_role('button', name='1. Goblin', exact=False).click()
        picker = self.page.get_by_role('dialog', name='Select monster image', exact=True)
        picker.get_by_role('button', name='Cancel', exact=True).click()
        self.finish()
        self.assertEqual(self.page.evaluate('window.shownImage'), 'https://img.test/mm.svg')
        again = self.page.get_by_role('button', name='Choose again', exact=True)
        # Opening the list again and cancelling keeps monster and image.
        self.page.evaluate("window.lookupSettled = false")
        again.click()
        self.page.get_by_role('dialog', name='Select monster candidate', exact=True).wait_for()
        self.assertEqual(self.page.evaluate('window.shownImage'), 'https://img.test/mm.svg')
        self.assertEqual(self.token(), 'token-1')
        self.page.keyboard.press('Escape')
        self.page.wait_for_function("document.querySelectorAll('dialog').length === 0")
        self.assertEqual(self.token(), 'token-1')
        self.assertEqual(self.page.evaluate('window.shownImage'), 'https://img.test/mm.svg')
        # A new monster with Cancel in the image picker keeps the image shown before.
        again.click()
        self.page.get_by_role('button', name='2. Goblin', exact=False).click()
        picker.get_by_role('button', name='Cancel', exact=True).click()
        self.page.wait_for_function("new FormData(document.querySelector('#monsterForm')).get('selection_token') === 'token-2'")
        self.assertEqual(self.form_value('image_selection_token'), 'token-1')
        self.assertEqual(self.page.evaluate('window.shownImage'), 'https://img.test/mm.svg')
        self.assertEqual(self.errors, [])

if __name__ == '__main__':
    unittest.main()
