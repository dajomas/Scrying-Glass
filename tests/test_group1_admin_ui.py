"""SG-TODO-029..032: Admin form defaults and control order, assembled Admin with intercepted HTTP."""
import unittest

from python.scrying_glass_monster_palette import PALETTE, next_monster_color


class GroupOneAdminTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def open_page(self):
        page, errors, _ = self.rows.open_page(self, 1440)
        page.wait_for_function("typeof window.scryingMonsterColorState === 'function'")
        return page, errors

    def expected_default(self, extra=()):
        return next_monster_color([m.get('color') for m in self.snapshot['monsters']] + list(extra))

    def test_029_default_color_skips_used_colors_and_keeps_a_hand_pick(self):
        page, errors = self.open_page()
        expected = self.expected_default()
        for ident in ('#monsterColor', '#monsterFileColor'):
            page.wait_for_function('([id, c]) => document.querySelector(id).value === c', arg=[ident, expected])
        self.assertEqual(page.evaluate("getComputedStyle(document.querySelector('#monsterColorPreview')).backgroundColor"),
                         'rgb(%d, %d, %d)' % tuple(int(expected[i:i + 2], 16) for i in (1, 3, 5)))
        auto = "(id) => new FormData(document.querySelector(id)).getAll('color_auto')"
        self.assertEqual(page.evaluate(auto, '#monsterForm'), ['true'])
        self.assertEqual(page.evaluate(auto, '#monsterUpload'), ['true'])
        # A new monster in the setup moves the default on; a hand-picked color stays.
        page.evaluate("""() => { const input = document.querySelector('#monsterFileColor');
            input.value = '#00ff00'; input.dispatchEvent(new Event('input', {bubbles: true})); }""")
        page.evaluate("([c]) => window.scryingMonsterColorState({monsters: [...latest.monsters, {color: c}]})", [expected])
        following = self.expected_default([expected])
        self.assertNotEqual(following, expected)
        self.assertEqual(page.locator('#monsterColor').input_value(), following)
        self.assertEqual(page.locator('#monsterFileColor').input_value(), '#00ff00')
        self.assertEqual(page.evaluate(auto, '#monsterUpload'), [''])  # hand pick: one color for all copies
        self.assertEqual(page.evaluate(auto, '#monsterForm'), ['true'])
        # Reset ends the hand pick and restores the computed default.
        page.evaluate("document.querySelector('#monsterUpload').reset()")
        page.wait_for_function('([c]) => document.querySelector("#monsterFileColor").value === c', arg=[following])
        self.assertEqual(page.evaluate(auto, '#monsterUpload'), ['true'])
        # All twelve in use: the least used color.
        page.evaluate("([p]) => window.scryingMonsterColorState({monsters: [...p, ...p.slice(1)].map(color => ({color}))})", [list(PALETTE)])
        self.assertEqual(page.locator('#monsterColor').input_value(), PALETTE[0])
        self.assertEqual(errors, [])

    def test_030_hp_help_is_a_closed_disclosure_at_the_end_of_combat_statistics(self):
        page, errors = self.open_page()
        result = page.evaluate("""() => {
            const help = document.querySelector('#monsterHpRangeHelp');
            const details = help.closest('details');
            const fieldset = document.querySelector('#monsterHpRangeStart').closest('fieldset');
            return {inDetails: !!details, open: details?.open, last: fieldset?.lastElementChild === details,
                    legend: fieldset?.querySelector('legend')?.textContent, items: help.querySelectorAll('li').length,
                    described: document.querySelector('#monsterHpRangeStart').getAttribute('aria-describedby')};
        }""")
        self.assertEqual(result, {'inDetails': True, 'open': False, 'last': True, 'legend': 'Combat statistics',
                                  'items': 3, 'described': 'monsterHpRangeHelp'})
        self.assertEqual(errors, [])

    def test_031_refresh_from_source_sits_directly_above_remove(self):
        page, errors = self.open_page()
        values = page.evaluate("[...document.querySelector('#monsterBulkAction').options].map(o => o.value)")
        self.assertEqual(values[-2:], ['refresh-source-review', 'remove'])
        self.assertLess(values.index('reset'), values.index('refresh-source-review'))
        self.assertEqual(errors, [])

    def test_032_clear_selection_follows_select_all(self):
        page, errors = self.open_page()
        for kind, button in (('characters', 'selectAllCharacters'), ('monsters', 'selectAllMonsters')):
            order = page.evaluate("""([kind]) => [...document.getElementById(kind + 'ClearSelection').parentElement.children]
                .map(node => node.id || node.className)""", [kind])
            self.assertEqual(order[:3], [kind + 'SelectedCount', button, kind + 'ClearSelection'], kind)
            self.assertIn('bulk-control', order[3], kind)
        self.assertEqual(errors, [])


if __name__ == '__main__':
    unittest.main()
