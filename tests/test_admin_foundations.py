"""SG-TODO-009.1: source contracts and intercepted-HTTP browser fixtures."""
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FoundationSourceTests(unittest.TestCase):
    def test_asset_order(self):
        head = (ROOT / 'templates/admin/000_document_start.html').read_text(encoding='utf-8')
        asset = '/static/admin-foundations.css?v=1'
        self.assertEqual(head.count(asset), 1)
        self.assertLess(head.index('/static/admin-shell.css'), head.index(asset))
        self.assertLess(head.index(asset), head.index('/static/monster-button-layout.css'))

    def test_notification_layout_asset(self):
        end = (ROOT / 'templates/admin/190_document_end.html').read_text(encoding='utf-8')
        asset = '/static/admin-notification-layout.js?v=1'
        self.assertEqual(end.count(asset), 1)
        self.assertIn(f'<script src="{asset}" defer></script>', end)
        self.assertLess(end.index('/static/admin.js'), end.index(asset))
        self.assertLess(end.index(asset), end.index('/static/combatant-row-layout.js'))

    def test_scoped_rules_and_compatibility_boundaries(self):
        import re
        css = (ROOT / 'static/admin-foundations.css').read_text(encoding='utf-8')
        self.assertLessEqual(len(css.encode('utf-8')), 20000)
        plain = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
        for rule in plain.split('}'):
            if not rule.strip():
                continue
            selector, declarations = rule.split('{', 1)
            self.assertTrue(selector.strip().startswith('body.admin-shell'), selector)
            self.assertNotRegex(declarations, r'(?:^|;)\s*(?:display|visibility|overflow(?:-[xy])?|width|min-width|max-width|position)\s*:')
        for token in ('space-1', 'space-2', 'space-3', 'space-4', 'space-6', 'space-8',
                      'panel', 'control-height', 'control-radius', 'focus', 'font'):
            self.assertIn('--admin-' + token + ':', css)
        self.assertNotIn('!important', plain)
        self.assertNotIn('@import', plain)
        self.assertNotIn(':root', plain)


class FoundationBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def open_page(self, width):
        return self.rows.open_page(self, width, workflow='campaign')

    def open_inputs(self, page, workflow):
        page.locator('#adminWorkflow-' + workflow).click()
        self.assertEqual(page.locator('body').get_attribute('data-workflow-view'), workflow)
        ids = ('Campaign', 'Character') if workflow == 'campaign' else ('BattleSetup', 'Monster')
        for name in ids:
            button = page.locator('#toggle' + name + 'Pane')
            if button.get_attribute('aria-expanded') == 'false':
                button.click()
            pane = button.get_attribute('aria-controls')
            self.assertTrue(page.locator('#' + pane).is_visible())

    def set_foundations(self, page, enabled):
        page.evaluate("""enabled => {
            const sheets = [...document.styleSheets].filter(s =>
                s.href && new URL(s.href).pathname === '/static/admin-foundations.css');
            if (sheets.length !== 1) throw new Error('Expected one foundations stylesheet');
            sheets[0].disabled = !enabled;
        }""", enabled)
        page.evaluate('document.body.getBoundingClientRect()')

    def state(self, page):
        return page.evaluate("""() => ({
            panes: [...document.querySelectorAll('.pane')].map(n => [n.id, n.hidden]),
            inputs: [...document.querySelectorAll('input, select, textarea')].map(n =>
                [n.id, n.name, n.value, n.checked, n.disabled]),
            actions: [...document.querySelectorAll('button')].map(n =>
                [n.id, n.textContent.trim(), n.hidden, n.disabled]),
            colours: [...document.querySelectorAll('input[type=color]')].map(n => [n.id, n.value])
        })""")

    def screenshot_at_top(self, page, target):
        page.evaluate("document.querySelector('#adminScroll').scrollTop = 0")
        page.wait_for_function("document.querySelector('#adminScroll').scrollTop === 0")
        geometry = page.evaluate("""() => ({
            headerBottom: document.querySelector('#adminHeader').getBoundingClientRect().bottom,
            workspaceTop: document.querySelector('#adminScroll').getBoundingClientRect().top,
            scrollTop: document.querySelector('#adminScroll').scrollTop
        })""")
        self.assertEqual(geometry['scrollTop'], 0)
        self.assertGreaterEqual(geometry['workspaceTop'], geometry['headerBottom'] - 1)
        page.screenshot(path=str(target))

    def test_visual_fixture_and_css_only_state_preservation(self):
        directory = Path(os.environ.get('SG_VISUAL_ARTIFACTS',
                         str(Path(tempfile.gettempdir()) / 'sg-admin-foundations')))
        directory.mkdir(parents=True, exist_ok=True)
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                initial = self.state(page)
                self.set_foundations(page, False)
                self.assertEqual(self.state(page), initial)
                self.set_foundations(page, True)
                self.assertEqual(self.state(page), initial)
                self.open_inputs(page, 'campaign')
                self.open_inputs(page, 'preparation')
                self.open_inputs(page, 'campaign')
                page.locator('#characterName').fill('Unsaved visual-review character')
                before = self.state(page)
                self.set_foundations(page, False)
                self.screenshot_at_top(page, directory / f'{width}-before.png')
                self.set_foundations(page, True)
                self.screenshot_at_top(page, directory / f'{width}-after.png')
                self.assertEqual(self.state(page), before)
                self.assertEqual(page.locator('#monsters td button').count(), 11)
                self.assertEqual(page.locator('#monsters [data-d], #monsters [data-h]').count(), 0)
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()

    def test_blank_notices_collapse_and_real_messages_reappear(self):
        groups = (
            ('campaign', ['campaignNotification', 'characterAddNotification'], ['campaign', 'characters']),
            ('preparation', ['battleSetupNotification', 'monsterAddNotification'], ['battleSetup', 'monsters']),
        )
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                # Exercise each notice in its rendered destination, not a hidden view.
                for workflow, ids, kinds in groups:
                    self.open_inputs(page, workflow)
                    page.wait_for_function("ids => ids.every(id => document.getElementById(id).hidden)", arg=ids)
                    for ident in ids:
                        notice = page.locator('#' + ident)
                        self.assertEqual(notice.get_attribute('role'), 'status')
                        self.assertEqual(notice.get_attribute('aria-live'), 'polite')
                        self.assertEqual(notice.evaluate('n => n.getBoundingClientRect().height'), 0)
                    page.evaluate("""kinds => kinds.forEach(kind => {
                        const ticket = scryingAdminFeedback.begin({region:kind,operation:'fixture.foundations.notice',target:'notice',label:'Visual review'});
                        paneNotification(kind, '  Visual review: message remains readable.  ', {ticket,severity:'error'});
                    })""", kinds)
                    page.wait_for_function("ids => ids.every(id => !document.getElementById(id).hidden)", arg=ids)
                    for ident in ids:
                        notice = page.locator('#' + ident)
                        self.assertTrue(notice.is_visible())
                        self.assertEqual(notice.locator('.sg-feedback-text').text_content(), 'Error:   Visual review: message remains readable.  ')
                        self.assertEqual(notice.locator('[data-severity="error"]').count(), 1)
                        self.assertEqual(notice.locator('.sg-feedback-dismiss').count(), 1)
                    page.evaluate("""kinds => kinds.forEach(kind => {
                        const ticket = scryingAdminFeedback.begin({region:kind,operation:'fixture.foundations.notice',target:'notice',label:'Visual review'});
                        scryingAdminFeedback.resolve(ticket);
                    })""", kinds)
                    page.wait_for_function("ids => ids.every(id => document.getElementById(id).hidden)", arg=ids)
                page.evaluate("""() => {
                    const ticket = scryingAdminFeedback.beginLookup('fixture monster');
                    setMonsterSpeciesLookupStatus('Looking up a monster...', {ticket,severity:'info'});
                }""")
                page.wait_for_function("!document.querySelector('#monsterAddNotification').hidden")
                self.assertTrue(page.locator('#monsterAddNotification').is_visible())
                page.evaluate("setMonsterSpeciesLookupStatus('')")
                page.wait_for_function("document.querySelector('#monsterAddNotification').hidden")
                page.add_script_tag(content=(ROOT / 'static/admin-notification-layout.js').read_text(encoding='utf-8'))
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()

    def test_computed_foundations_focus_and_modal(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                self.open_inputs(page, 'campaign')
                panel = page.locator('#campaignInputPane')
                values = panel.evaluate("""n => {
                    const s = getComputedStyle(n);
                    return [s.backgroundColor, s.borderLeftColor, s.boxShadow, s.borderRadius];
                }""")
                self.assertEqual(values, ['rgb(26, 32, 44)', 'rgb(132, 197, 192)', 'none', '8px'])
                self.open_inputs(page, 'preparation')
                button = page.locator('#monsters [data-edit]')
                self.assertTrue(button.is_visible())
                button.focus()
                page.keyboard.press('Tab')
                page.keyboard.press('Shift+Tab')
                focus = button.evaluate("""n => {
                    const s = getComputedStyle(n);
                    return [n === document.activeElement, s.outlineStyle, s.outlineWidth];
                }""")
                self.assertEqual(focus, [True, 'solid', '2px'])
                page.keyboard.press('Enter')
                page.wait_for_function("!document.querySelector('#editModal').hidden")
                dialog = page.locator('#editModal > div')
                self.assertEqual(dialog.evaluate('n => getComputedStyle(n).borderRadius'), '8px')
                self.assertEqual(dialog.evaluate('n => getComputedStyle(n).backgroundColor'), 'rgb(26, 32, 44)')
                page.locator('#cancelEdit').click()
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()


if __name__ == '__main__':
    unittest.main()
