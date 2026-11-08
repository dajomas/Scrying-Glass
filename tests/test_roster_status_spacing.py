"""Compact roster status-gap checks in assembled Admin with intercepted HTTP."""
import unittest
import test_stage_b_rosters as fixture


class CompactRosterSpacingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture.StageBRosterTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        fixture.StageBRosterTests.tearDownClass.__func__(cls)

    open_page = fixture.StageBRosterTests.open_page
    assert_status_line = fixture.StageBRosterTests.assert_status_line

    def test_status_follows_name_block_without_a_blank_line(self):
        for width in (375, 768, 1440):
            for root_size in (16, 20):
                with self.subTest(width=width, root_size=root_size):
                    page, state, calls, fail, errors, mutations = self.open_page(width)
                    page.add_style_tag(content=f'html {{font-size:{root_size}px}}')
                    for cycle in range(3):
                        state['monsters'][0]['name'] = 'Poddy' if cycle != 1 else 'Long monster name ' * 8
                        state['monsters'][0]['monster_species'] = 'noble prodigy' if cycle != 1 else 'Long species ' * 8
                        state['characters'][0]['name'] = 'Hero' if cycle != 1 else 'Long character name ' * 8
                        page.evaluate('load(true)')
                        for kind in ('monsters', 'characters'):
                            self.assert_status_line(page, kind)
                            metrics = page.locator('#'+kind+' .sg-roster-state').first.evaluate("""node => {
                                const cell=node.closest('td'), range=document.createRange();
                                range.selectNodeContents(cell);range.setEndBefore(node);
                                return {gap:node.getBoundingClientRect().top-range.getBoundingClientRect().bottom,
                                    maxGap:parseFloat(getComputedStyle(document.documentElement).fontSize)*.5};
                            }""")
                            self.assertGreaterEqual(metrics['gap'], 0)
                            self.assertLessEqual(metrics['gap'], metrics['maxGap'])
                    self.assertEqual(calls, [])
                    self.assertEqual(mutations, [])
                    self.assertEqual(errors, [])
                    page.close()


if __name__ == '__main__':
    unittest.main()
