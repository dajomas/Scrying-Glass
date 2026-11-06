"""SG-TODO-009.3: intercepted HTTP/Chromium fixtures, not a live server."""
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PanelFormsSourceTests(unittest.TestCase):
    def test_assets_and_presentation_only_contract(self):
        head = (ROOT / 'templates/admin/000_document_start.html').read_text(encoding='utf-8')
        end = (ROOT / 'templates/admin/190_document_end.html').read_text(encoding='utf-8')
        self.assertEqual(head.count('/static/admin-panel-forms.css?v=1'), 1)
        self.assertLess(head.index('/static/admin-foundations.css'), head.index('/static/admin-panel-forms.css'))
        self.assertEqual(end.count('/static/admin-panel-forms.js?v=1'), 1)
        self.assertLess(end.index('/static/combatant-row-layout.js'), end.index('/static/admin-panel-forms.js'))
        source = (ROOT / 'static/admin-panel-forms.js').read_text(encoding='utf-8')
        for forbidden in ('fetch(', 'innerHTML', 'cloneNode', '.reset(', '.onsubmit =', 'localStorage'):
            self.assertNotIn(forbidden, source)
        for name in ('admin-panel-forms.js', 'admin-panel-forms.css'):
            self.assertLessEqual((ROOT / 'static' / name).stat().st_size, 20000)


class PanelFormsBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def open_page(self, width=1440):
        page, errors, mutations = self.rows.open_page(self, width)
        page.wait_for_function("document.body.dataset.panelForms === 'ready'")
        for id in ('toggleCampaignPane', 'toggleCharacterPane', 'toggleBattleSetupPane', 'toggleMonsterPane'):
            button = page.locator('#' + id)
            if button.get_attribute('aria-expanded') == 'false':
                button.click()
        for id in ('campaignInputPane', 'characterInputPane', 'battleSetupInputPane', 'monsterInputPane'):
            self.assertTrue(page.locator('#' + id).is_visible())
        return page, errors, mutations

    def test_groups_required_labels_and_idempotence(self):
        page, errors, mutations = self.open_page()
        self.assertEqual(page.locator('#characterInputPane h2').inner_text(), 'Add character')
        self.assertEqual(page.locator('#monsterInputPane h2').inner_text(), 'Add monsters')
        self.assertEqual(page.locator('#characterForm legend').all_text_contents(), ['Character details', 'Starting statistics'])
        self.assertEqual(page.locator('#monsterForm legend').all_text_contents(), ['Monster identity', 'Combat statistics', 'Appearance'])
        for id in ('characterName', 'characterHp', 'monsterName', 'monsterSpecies', 'monsterAc', 'monsterHpRangeStart', 'monsterFile'):
            self.assertTrue(page.locator('#' + id).evaluate("n => n.required && n.labels.length > 0 && n.labels[0].querySelector('.field-label').getBoundingClientRect().bottom <= n.getBoundingClientRect().top + 1"))
        page.evaluate("window.sgSaved = [...document.querySelectorAll('.sg-input-panel input, .sg-input-panel button, .sg-input-panel form')].map(n => ({n, form:n.form, submit:n.onsubmit, click:n.onclick}))")
        page.add_script_tag(content=(ROOT / 'static/admin-panel-forms.js').read_text(encoding='utf-8'))
        self.assertTrue(page.evaluate('sgSaved.every(x => x.n.isConnected && x.n.form === x.form && x.n.onsubmit === x.submit && x.n.onclick === x.click)'))
        self.assertEqual(page.locator('#sgMonsterFileImport').count(), 1)
        self.assertEqual(page.locator('#characterForm fieldset').count(), 2)
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])

    def test_disclosures_drafts_files_and_common_controls(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                page.locator('#characterName').fill('Unsaved character')
                page.locator('#backgroundValue').fill('Keep background draft')
                page.locator('#monsterFile').set_input_files({'name':'draft.monster', 'mimeType':'application/json', 'buffer':b'{}'})
                for id in ('sgBackgroundOptions', 'sgMonsterFileImport'):
                    details = page.locator('#' + id)
                    summary = details.locator(':scope > summary')
                    self.assertTrue(details.evaluate('n => n.open'))
                    summary.focus()
                    page.keyboard.press('Enter')
                    self.assertFalse(details.evaluate('n => n.open'))
                    page.keyboard.press('Space')
                    self.assertTrue(details.evaluate('n => n.open'))
                    self.assertIsNone(summary.get_attribute('aria-expanded'))
                self.assertEqual(page.locator('#backgroundValue').input_value(), 'Keep background draft')
                page.evaluate('load(true)')
                page.wait_for_function("document.querySelectorAll('#monsters td button').length === 11")
                self.assertEqual(page.locator('#characterName').input_value(), 'Unsaved character')
                self.assertEqual(page.locator('#monsterFile').evaluate('n => n.files[0].name'), 'draft.monster')
                for id in ('openCharacterCsvImport', 'openImport', 'openMonsterCsvImport', 'saveSetup', 'setupSelect'):
                    self.assertTrue(page.locator('#' + id).is_visible())
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()

    def test_required_validation_and_character_submit_failure_then_success(self):
        page, errors, mutations = self.open_page()
        page.locator('#characterForm .sg-form-actions button').click()
        self.assertFalse(page.locator('#characterForm').evaluate('n => n.checkValidity()'))
        self.assertEqual(mutations, [])
        def reject(route):
            route.fulfill(status=400, content_type='application/json', body='{"detail":"Fixture rejection"}')
        page.route('**/api/characters', reject)
        page.locator('#characterName').fill('Keep on failure')
        page.locator('#characterHp').fill('17')
        with page.expect_response(lambda r: r.url.endswith('/api/characters')):
            page.locator('#characterForm .sg-form-actions button').click()
        page.wait_for_function("document.querySelector('#characterAddNotification').textContent.includes('Fixture rejection')")
        self.assertEqual(page.locator('#characterName').input_value(), 'Keep on failure')
        self.assertEqual(page.locator('#characterHp').input_value(), '17')
        page.unroute('**/api/characters', reject)
        with page.expect_response(lambda r: r.url.endswith('/api/characters')):
            page.locator('#characterForm .sg-form-actions button').click()
        page.wait_for_function("document.querySelector('#characterName').value === ''")
        self.assertEqual(mutations, ['/api/characters'])
        self.assertEqual(errors, [])

    def test_invalid_monster_hp_keeps_draft_without_mutation(self):
        page, errors, mutations = self.open_page()
        for id, value in (('monsterName','Draft'), ('monsterSpecies','goblin'), ('monsterAc','12'), ('monsterHpRangeStart','not dice')):
            page.locator('#' + id).fill(value)
        page.locator('#monsterForm .sg-form-actions button').click()
        page.wait_for_function("document.querySelector('#monsterAddNotification').textContent.trim().length > 0")
        self.assertEqual(page.locator('#monsterHpRangeStart').input_value(), 'not dice')
        self.assertTrue(page.locator('#monsterHpRangeStart').evaluate('n => n === document.activeElement'))
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])

    def test_panel_geometry_and_screenshots(self):
        directory = Path(os.environ.get('SG_VISUAL_ARTIFACTS', str(Path(tempfile.gettempdir()) / 'sg-admin-foundations')))
        directory.mkdir(parents=True, exist_ok=True)
        for width in (1440, 768, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                for group in page.locator('.sg-input-panel .sg-field-group').all():
                    self.assertTrue(group.evaluate("n => { const b=n.getBoundingClientRect(), p=n.closest('.pane').getBoundingClientRect(); return b.left >= p.left && b.right <= p.right + 1; }"))
                if width != 768:
                    for kind in ('character', 'monster'):
                        page.locator('#' + kind + 'InputPane').scroll_into_view_if_needed()
                        page.screenshot(path=str(directory / f'0093-{width}-{kind}.png'))
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()


if __name__ == '__main__':
    unittest.main()
