"""SG-TODO-009.2: intercepted HTTP and real Chromium, not a live server."""
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HeaderHierarchySourceTests(unittest.TestCase):
    def test_matching_assets_load_after_foundations_and_core(self):
        head = (ROOT / 'templates/admin/000_document_start.html').read_text(encoding='utf-8')
        end = (ROOT / 'templates/admin/190_document_end.html').read_text(encoding='utf-8')
        self.assertEqual(head.count('/static/admin-header-hierarchy.css?v=1'), 1)
        self.assertLess(head.index('/static/admin-foundations.css'), head.index('/static/admin-header-hierarchy.css'))
        self.assertEqual(end.count('/static/admin-header-hierarchy.js?v=1'), 1)
        self.assertLess(end.index('/static/admin-notification-layout.js'), end.index('/static/admin-header-hierarchy.js'))
        self.assertIn('<script src="/static/admin-header-hierarchy.js?v=1" defer></script>', end)
        for name in ('admin-header-hierarchy.js', 'admin-header-hierarchy.css'):
            self.assertLessEqual((ROOT / 'static' / name).stat().st_size, 20000)


class HeaderHierarchyBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def open_page(self, width):
        page, errors, mutations = self.rows.open_page(self, width)
        page.wait_for_function("document.body.dataset.headerHierarchy === 'ready'")
        return page, errors, mutations

    def assert_boundary(self, page):
        boxes = page.evaluate("""() => ({
            header: document.querySelector('#adminHeader').getBoundingClientRect().toJSON(),
            workspace: document.querySelector('#adminScroll').getBoundingClientRect().toJSON()
        })""")
        self.assertAlmostEqual(boxes['header']['bottom'], boxes['workspace']['top'], delta=1)
        self.assertGreater(boxes['workspace']['height'], 0)
        return boxes

    def test_context_uses_active_labels_and_primary_action_tracks_state(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                page.wait_for_function("document.querySelector('#adminContextCampaign').textContent === 'Default'")
                page.evaluate("""() => {
                    document.querySelector('#activeCampaignInfo').innerHTML = 'Active: <strong>Active campaign</strong>';
                    document.querySelector('#activeBattleSetupInfo').innerHTML = 'Active: <strong>Active setup</strong>';
                    document.querySelector('#setupName').value = 'Unsaved setup name';
                    document.querySelector('#battleState').className = 'battle-state active';
                    document.querySelector('#battleState').textContent = 'Active';
                    document.querySelector('#battleRound').hidden = false;
                    document.querySelector('#battleRound').textContent = 'Round 3';
                }""")
                page.wait_for_function("document.querySelector('#adminContextState').textContent === 'Active · Round 3'")
                self.assertEqual(page.locator('#adminContextCampaign').inner_text(), 'Active campaign')
                self.assertEqual(page.locator('#adminContextSetup').inner_text(), 'Active setup')
                self.assertIn('sg-primary-action', page.locator('#nextBattle').get_attribute('class'))
                self.assertNotIn('sg-primary-action', page.locator('#startBattle').get_attribute('class'))
                page.evaluate("document.querySelector('#activeCampaignInfo').textContent = 'No active campaign'; document.querySelector('#activeBattleSetupInfo').textContent = 'No saved battle setup loaded'; document.querySelector('#battleState').className = 'battle-state inactive'; document.querySelector('#battleState').textContent = 'Inactive'; document.querySelector('#battleRound').hidden = true")
                page.wait_for_function("document.querySelector('#adminContextState').textContent === 'Inactive'")
                self.assertEqual(page.locator('#adminContextCampaign').inner_text(), 'No active campaign')
                self.assertEqual(page.locator('#adminContextSetup').inner_text(), 'No saved battle setup loaded')
                self.assertIn('sg-primary-action', page.locator('#startBattle').get_attribute('class'))
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()

    def test_more_and_danger_are_keyboard_accessible_without_mutations(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                self.assertFalse(page.locator('#adminLogout').is_visible())
                summary = page.locator('#adminMore > summary')
                summary.focus()
                page.keyboard.press('Enter')
                self.assertTrue(page.locator('#adminLogout').is_visible())
                self.assertEqual(page.locator('#adminMore form').get_attribute('method'), 'post')
                self.assertEqual(page.locator('#adminMore form').get_attribute('action'), '/logout')
                box = page.locator('.sg-more-body').bounding_box()
                self.assertGreaterEqual(box['x'], 0)
                self.assertLessEqual(box['x'] + box['width'], width + 1)
                page.locator('#battleOrderFontIncrease').focus()
                page.keyboard.press('Escape')
                self.assertFalse(page.locator('#adminMore').evaluate('n => n.open'))
                self.assertTrue(summary.evaluate('n => n === document.activeElement'))
                self.assertFalse(page.locator('#resetAll').is_visible())
                page.locator('#adminDangerZone > summary').focus()
                page.keyboard.press('Enter')
                self.assertTrue(page.locator('#resetAll').is_visible())
                page.once('dialog', lambda dialog: dialog.dismiss())
                page.locator('#resetAll').click()
                self.assertEqual(mutations, [])
                page.add_script_tag(content=(ROOT / 'static/admin-header-hierarchy.js').read_text(encoding='utf-8'))
                for id in ('adminMore', 'adminDangerZone', 'startBattle', 'nextBattle', 'endBattle', 'resetAll'):
                    self.assertEqual(page.locator('#' + id).count(), 1)
                self.assertEqual(errors, [])
                page.close()

    def test_header_scrolling_feedback_and_pane_preferences(self):
        for width in (1440, 768, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                initial = self.assert_boundary(page)
                self.assertLess(initial['header']['height'], 320)
                buttons = page.locator('.sg-pane-strip button:visible')
                for index in range(buttons.count()):
                    button = buttons.nth(index)
                    button.focus()
                    self.assertTrue(button.evaluate("""n => {
                        const b = n.getBoundingClientRect(), r = n.parentElement.getBoundingClientRect();
                        return b.left >= r.left - 1 && b.right <= r.right + 1;
                    }"""))
                for selector in ('#toggleCampaignPane', '#toggleCharacterPane'):
                    button = page.locator(selector)
                    if button.get_attribute('aria-expanded') == 'false':
                        button.click()
                self.assertFalse(page.locator('#campaignInputPane').evaluate('n => n.hidden'))
                self.assertFalse(page.locator('#characterInputPane').evaluate('n => n.hidden'))
                self.assertTrue(page.locator('#characterName').is_visible())
                page.locator('#characterName').fill('Keep my draft')
                page.locator('#toggleCampaignPane').click()
                page.locator('#toggleCampaignPane').click()
                self.assertFalse(page.locator('#characterInputPane').evaluate('n => n.hidden'))
                self.assertEqual(page.locator('#characterName').input_value(), 'Keep my draft')
                page.evaluate("message('Visible feedback: ' + 'encounter-data-'.repeat(8))")
                boxes = self.assert_boundary(page)
                message = page.locator('#message').bounding_box()
                self.assertLessEqual(message['y'] + message['height'], boxes['workspace']['top'])
                page.locator('#adminScroll').evaluate('n => n.scrollTop = n.scrollHeight')
                self.assertEqual(boxes['header'], self.assert_boundary(page)['header'])
                self.assertEqual(page.locator('#monsters td button').count(), 11)
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()

    def test_original_next_handler_and_cancelled_end_remain_intact(self):
        page, errors, mutations = self.open_page(1440)
        with page.expect_response(lambda r: r.url.endswith('/api/battle/next')):
            page.locator('#nextBattle').click()
        page.wait_for_function("document.querySelector('#adminContextState').textContent !== 'Loading…'")
        self.assertEqual(mutations, ['/api/battle/next'])
        page.evaluate("latest.battle_order = [latest.characters[0].id]; updateBattleState(latest)")
        page.once('dialog', lambda dialog: dialog.dismiss())
        page.locator('#endBattle').click()
        self.assertEqual(mutations, ['/api/battle/next'])
        self.assertEqual(errors, [])

    def test_capture_desktop_and_narrow_header(self):
        directory = Path(os.environ.get('SG_VISUAL_ARTIFACTS',
                         str(Path(tempfile.gettempdir()) / 'sg-admin-foundations')))
        directory.mkdir(parents=True, exist_ok=True)
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                page.evaluate("document.querySelector('#adminScroll').scrollTop = 0")
                self.assert_boundary(page)
                page.screenshot(path=str(directory / f'0092-{width}-inactive.png'))
                page.evaluate("document.querySelector('#battleState').className = 'battle-state active'; document.querySelector('#battleState').textContent = 'Active'; document.querySelector('#battleRound').hidden = false; document.querySelector('#battleRound').textContent = 'Round 2'")
                page.wait_for_function("document.querySelector('#nextBattle').classList.contains('sg-primary-action')")
                page.screenshot(path=str(directory / f'0092-{width}-active.png'))
                page.locator('#adminMore > summary').click()
                page.screenshot(path=str(directory / f'0092-{width}-more.png'))
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()


if __name__ == '__main__':
    unittest.main()
