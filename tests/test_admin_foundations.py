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
        return self.rows.open_page(self, width)

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
                for toggle in ('#toggleCampaignPane', '#toggleCharacterPane',
                               '#toggleBattleSetupPane', '#toggleMonsterPane'):
                    button = page.locator(toggle)
                    if button.is_visible() and button.get_attribute('aria-expanded') == 'false':
                        button.click()
                page.locator('#characterName').fill('Unsaved visual-review character')
                before = self.state(page)
                self.set_foundations(page, False)
                page.screenshot(path=str(directory / f'{width}-before.png'))
                self.set_foundations(page, True)
                page.screenshot(path=str(directory / f'{width}-after.png'))
                self.assertEqual(self.state(page), before)
                self.assertEqual(page.locator('#monsters td button').count(), 11)
                self.assertEqual(page.locator('#monsters [data-d], #monsters [data-h]').count(), 0)
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()

    def test_computed_foundations_focus_and_modal(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                panel = page.locator('#campaignInputPane')
                values = panel.evaluate("""n => {
                    const s = getComputedStyle(n);
                    return [s.backgroundColor, s.borderLeftColor, s.boxShadow, s.borderRadius];
                }""")
                self.assertEqual(values, ['rgb(26, 32, 44)', 'rgb(132, 197, 192)', 'none', '8px'])
                button = page.locator('#monsters [data-edit]')
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
