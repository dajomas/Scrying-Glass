"""SG-TODO-014/009.5: concise source wording and intercepted full Admin."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LABEL = 'Overwrite AC, HP range and initiative bonus with source values. Missing initiative bonus defaults to 0.'
LOOKUP_HELP = ('While entering Monster species, D&D Beyond and configured 5e.tools sources will be searched. '
               'Choose a version when prompted. Uploaded images override source images.')


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, value):
        self.parts.append(value)


class SourceHelpTests(unittest.TestCase):
    def test_lookup_help_is_concise_and_preserves_essential_guidance(self):
        source = (ROOT / 'templates/admin/060_monster_input.html').read_text(encoding='utf-8')
        parser = Text()
        parser.feed(source)
        text = ' '.join(' '.join(parser.parts).split())
        self.assertIn(LOOKUP_HELP, text)
        self.assertIn(LABEL, text)
        fragment = source.split('<p id="monsterLookupHelp" class="field-help">', 1)[1].split('</p>', 1)[0]
        lookup_parser = Text()
        lookup_parser.feed(fragment)
        lookup = ' '.join(' '.join(lookup_parser.parts).split())
        self.assertEqual(lookup, LOOKUP_HELP)
        self.assertLessEqual(len(lookup.split()), 40)
        self.assertNotIn('fivetools_fallback', lookup)
        self.assertNotIn('with found D&amp;D Beyond values', source)
        self.assertNotIn('D&D Beyond first.', text)
        self.assertNotIn('they do not trigger fallback.', text)
        for ident in ('monsterForm', 'monsterUpload', 'monsterSpeciesLookupOverwrite', 'monsterHpRangeHelp', 'monsterLookupHelp', 'monsterImage', 'monsterFileImage'):
            self.assertEqual(source.count('id="' + ident + '"'), 1)

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
                for ident in ('toggleBattleSetupPane', 'toggleMonsterPane'):
                    button = page.locator('#' + ident)
                    if button.get_attribute('aria-expanded') == 'false':
                        button.click()
                pane = page.locator('#monsterInputPane')
                text = ' '.join(pane.inner_text().split())
                lookup = page.locator('#monsterLookupHelp')
                self.assertTrue(lookup.is_visible())
                self.assertEqual(' '.join(lookup.inner_text().split()), LOOKUP_HELP)
                self.assertLessEqual(len(lookup.inner_text().split()), 40)
                self.assertIn(LOOKUP_HELP, text)
                self.assertNotIn('The fivetools_fallback setting', text)
                self.assertNotIn('D&D Beyond first.', text)
                checkbox = page.get_by_role('checkbox', name=LABEL, exact=True)
                self.assertTrue(checkbox.is_visible())
                self.assertEqual(checkbox.get_attribute('id'), 'monsterSpeciesLookupOverwrite')
                self.assertEqual(page.locator('#monsterForm').count(), 1)
                self.assertEqual(page.locator('#monsterUpload').count(), 1)
                self.assertEqual(page.locator('#monsterInitiativeBonusHelp').count(), 0)
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()


if __name__ == '__main__':
    unittest.main()
