"""SG-TODO-009.4 increment 1: full Admin with intercepted HTTP, not live server."""
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RosterSourceTests(unittest.TestCase):
    def test_asset_order_and_no_hp_or_api_changes(self):
        head = (ROOT / 'templates/admin/000_document_start.html').read_text()
        end = (ROOT / 'templates/admin/190_document_end.html').read_text()
        self.assertEqual(head.count('/static/admin-rosters.css?v=1'), 1)
        self.assertLess(head.index('/static/admin-panel-forms.css'), head.index('/static/admin-rosters.css'))
        self.assertEqual(end.count('/static/admin-rosters.js?v=1'), 1)
        self.assertLess(end.index('/static/monster-image-previews.js'), end.index('/static/admin-rosters.js'))
        source = (ROOT / 'static/admin-rosters.js').read_text()
        for forbidden in ('fetch(', 'innerHTML', 'replaceChildren', 'data-chp', 'data-cmaxhp', 'keydown', 'localStorage'):
            self.assertNotIn(forbidden, source)
        self.assertIn('setAllSelected(kind, false)', source)
        for name in ('admin-rosters.js', 'admin-rosters.css'):
            self.assertLessEqual((ROOT / 'static' / name).stat().st_size, 20000)


class RosterBrowserTests(unittest.TestCase):
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
        page.wait_for_function("document.querySelector('#charactersSelectedCount')?.textContent === '0 selected' && document.querySelectorAll('#monsters .sg-roster-state').length > 0")
        return page, errors, mutations

    def test_selection_context_and_refresh_preserve_original_selection_sets(self):
        page, errors, mutations = self.open_page()
        for kind, singular in (('characters', 'Character'), ('monsters', 'Monster')):
            select = page.locator('#' + singular.lower() + 'BulkAction')
            self.assertTrue(select.locator('option[value="reset"]').evaluate('n => n.disabled'))
            self.assertFalse(select.locator('option[value="select-all"]').evaluate('n => n.disabled'))
            page.locator('#selectAll' + ('Characters' if kind == 'characters' else 'Monsters')).click()
            count = page.locator('#' + kind + ' [data-select-kind]').count()
            page.wait_for_function('([kind,count]) => document.getElementById(kind+"SelectedCount").textContent === count+" selected"', arg=[kind,count])
            self.assertFalse(select.locator('option[value="reset"]').evaluate('n => n.disabled'))
            self.assertEqual(page.evaluate('(kind) => selectionFor(kind).size', kind), count)
            page.evaluate('load(true)')
            page.wait_for_function('([kind,count]) => document.querySelectorAll("#"+kind+" .sg-row-selected").length === count', arg=[kind,count])
            clear = page.locator('#' + kind + 'ClearSelection')
            clear.focus()
            page.keyboard.press('Enter')
            page.wait_for_function('(kind) => document.getElementById(kind+"SelectedCount").textContent === "0 selected"', arg=kind)
            self.assertEqual(page.evaluate('(kind) => selectionFor(kind).size', kind), 0)
            self.assertTrue(clear.evaluate('n => n.disabled'))
            self.assertEqual(page.locator(':focus').get_attribute('data-select-all-kind'), kind)
        page.locator('#monsterBulkAction').select_option('select-dead')
        expected = page.evaluate('latest.monsters.filter(m => m.life_state === "dead" || m.alive === false).length')
        page.wait_for_function('(count) => document.querySelector("#monstersSelectedCount").textContent === count+" selected"', arg=expected)
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])

    def test_row_actions_inline_hp_focus_and_visual_fixtures(self):
        directory = Path(os.environ.get('SG_VISUAL_ARTIFACTS', str(Path(tempfile.gettempdir())/'sg-admin-foundations')))
        directory.mkdir(parents=True, exist_ok=True)
        for width in (1440,375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                self.assertEqual(page.locator('#monsters td button').count(), 11)
                self.assertEqual(page.locator('#characters td button').count(), 8)
                self.assertEqual(page.locator('#characters input[data-chp]').count(), 1)
                self.assertEqual(page.locator('#characters input[data-cmaxhp]').count(), 1)
                self.assertEqual(page.locator('#characters input[data-ci]').count(), 1)
                for kind in ('characters', 'monsters'):
                    self.assertIn('battle', page.locator('#'+kind+' .sg-roster-state').first.inner_text())
                    self.assertEqual(page.locator('#'+kind+' [data-d], #'+kind+' [data-h], #'+kind+' [data-cd], #'+kind+' [data-ch]').count(), 0)
                button = page.locator('#characters [data-remove-kind]')
                button.focus()
                self.assertTrue(button.evaluate("""n => {
                    const b=n.getBoundingClientRect(), r=document.querySelector('#characters');
                    const left=r.getBoundingClientRect().left+r.clientLeft;
                    return b.left >= left-1 && b.right <= left+r.clientWidth+1;
                }"""))
                page.add_script_tag(content=(ROOT/'static/admin-rosters.js').read_text())
                self.assertEqual(page.locator('#charactersClearSelection').count(), 1)
                self.assertEqual(page.locator('#monstersClearSelection').count(), 1)
                page.locator('#characterDisplayPane').scroll_into_view_if_needed()
                page.screenshot(path=str(directory/f'0094-{width}-rosters.png'))
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()


if __name__ == '__main__':
    unittest.main()
