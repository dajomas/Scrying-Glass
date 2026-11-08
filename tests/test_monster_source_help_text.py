"""SG-TODO-014: source wording and full-Admin intercepted-HTTP fixture."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LABEL = 'Overwrite Armor Class and HP Range with values from the selected D&D Beyond or 5e.tools result'


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, value):
        self.parts.append(value)


class SourceHelpTests(unittest.TestCase):
    def test_lookup_help_explains_order_configuration_errors_and_images(self):
        source = (ROOT / 'templates/admin/060_monster_input.html').read_text(encoding='utf-8')
        parser = Text()
        parser.feed(source)
        text = ' '.join(' '.join(parser.parts).split())
        for phrase in (
                'Monster lookup searches all enabled providers: D&D Beyond and configured 5e.tools sources.',
                'Both enabled providers are searched even when D&D Beyond returns usable matches.',
                'Disabled providers and unconfigured books are not searched.',
                'If any enabled provider or configured-book search fails or is incomplete, no candidates are offered; retry or enter stats manually.',
                'Versions keep their own statistics; select the provider/book/edition you want.',
                'The fivetools_fallback setting independently enables 5e.tools candidate lookup.',
                'When a selected result includes an image, that image is used unless you choose an Image file.',
                LABEL):
            self.assertIn(phrase, text)
        self.assertNotIn('with found D&amp;D Beyond values', source)
        self.assertNotIn('D&D Beyond first.', text)
        self.assertNotIn('they do not trigger fallback.', text)
        for id in ('monsterForm', 'monsterUpload', 'monsterSpeciesLookupOverwrite', 'monsterHpRangeHelp', 'monsterImage', 'monsterFileImage'):
            self.assertEqual(source.count('id="' + id + '"'), 1)


    def test_config_comments_explain_compatibility_without_changing_defaults(self):
        config = (ROOT / 'config.example.yaml').read_text(encoding='utf-8')
        self.assertIn('Independently enable 5e.tools for combined candidate lookup', config)
        self.assertIn('failures block all candidates.', config)
        self.assertIn('fivetools_fallback: true', config)
        self.assertIn('fivetools_sources: ["MM", "XMM", "PHB", "XPHB", "DMG", "XDMG"]', config)


class SourceHelpBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def test_help_and_checkbox_label_render_without_mutation(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.rows.open_page(self, width)
                for id in ('toggleBattleSetupPane', 'toggleMonsterPane'):
                    button = page.locator('#' + id)
                    if button.get_attribute('aria-expanded') == 'false':
                        button.click()
                pane = page.locator('#monsterInputPane')
                text = ' '.join(pane.inner_text().split())
                self.assertIn('Monster lookup searches all enabled providers: D&D Beyond and configured 5e.tools sources.', text)
                self.assertIn('Both enabled providers are searched even when D&D Beyond returns usable matches.', text)
                self.assertIn('Disabled providers and unconfigured books are not searched.', text)
                self.assertIn('If any enabled provider or configured-book search fails or is incomplete, no candidates are offered; retry or enter stats manually.', text)
                self.assertIn('Versions keep their own statistics; select the provider/book/edition you want.', text)
                self.assertIn('The fivetools_fallback setting independently enables 5e.tools candidate lookup.', text)
                self.assertIn('When a selected result includes an image, that image is used unless you choose an Image file.', text)
                self.assertNotIn('D&D Beyond first.', text)
                checkbox = page.get_by_role('checkbox', name=LABEL, exact=True)
                self.assertTrue(checkbox.is_visible())
                self.assertEqual(checkbox.get_attribute('id'), 'monsterSpeciesLookupOverwrite')
                self.assertEqual(page.locator('#monsterForm').count(), 1)
                self.assertEqual(page.locator('#monsterUpload').count(), 1)
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()


if __name__ == '__main__':
    unittest.main()
