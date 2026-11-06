"""Name-column regression checks on the intercepted-HTTP Admin page."""
import copy
import math
import unittest
import test_monster_button_layout as layout


# Bound numerical measurement slack; keep meaningful layout deficits failing.
WIDTH_TOLERANCE_PX = 1 / 32


def assert_minimum_width(case, actual, minimum):
    case.assertTrue(math.isfinite(actual) and math.isfinite(minimum),
                    "Width measurements must be finite")
    case.assertGreater(minimum, 0)
    case.assertGreaterEqual(
        actual + WIDTH_TOLERANCE_PX, minimum,
        f"Rendered width {actual}px is below minimum {minimum}px "
        f"beyond {WIDTH_TOLERANCE_PX}px measurement tolerance",
    )


class MinimumWidthToleranceTests(unittest.TestCase):
    def test_observed_fractional_rounding_is_accepted(self):
        assert_minimum_width(self, 137.265625, 137.281)

    def test_exact_and_wider_values_are_accepted(self):
        for width in (137.281, 140):
            with self.subTest(width=width):
                assert_minimum_width(self, width, 137.281)

    def test_tolerance_boundary_is_accepted(self):
        assert_minimum_width(self, 100 - WIDTH_TOLERANCE_PX, 100)

    def test_just_beyond_tolerance_is_rejected(self):
        with self.assertRaises(AssertionError):
            assert_minimum_width(self, 100 - WIDTH_TOLERANCE_PX - 0.001, 100)

    def test_real_width_deficits_are_rejected(self):
        for width in (99.9, 99, 0):
            with self.subTest(width=width), self.assertRaises(AssertionError):
                assert_minimum_width(self, width, 100)

    def test_nonfinite_measurements_are_rejected(self):
        for actual, minimum in ((math.nan, 100), (math.inf, 100),
                                (100, math.nan), (100, math.inf)):
            with self.subTest(actual=actual, minimum=minimum), self.assertRaises(AssertionError):
                assert_minimum_width(self, actual, minimum)

    def test_missing_minimum_is_rejected(self):
        with self.assertRaises(AssertionError):
            assert_minimum_width(self, 100, 0)


class MonsterNameLayoutTests(unittest.TestCase):
    setUpClass = classmethod(layout.MonsterButtonLayoutTests.setUpClass.__func__)
    tearDownClass = classmethod(layout.MonsterButtonLayoutTests.tearDownClass.__func__)
    open_page = layout.MonsterButtonLayoutTests.open_page

    def test_name_and_species_each_keep_their_own_line(self):
        for width in (1440, 768, 375):
            for name, active in (('Crawling Claw', False),
                                 ('Ancient Red Dragon Guard Captain', True)):
                with self.subTest(width=width, name=name, active=active):
                    self.snapshot = copy.deepcopy(type(self).snapshot)
                    monster = self.snapshot['monsters'][0]
                    monster.update(name=name, monster_species=name)
                    page, errors, mutations = self.open_page(width, active)
                    cell = page.locator('#monsters td:nth-child(2)')
                    geometry = cell.evaluate("""node => {
                        const rects = target => {
                            const range = document.createRange();
                            range.selectNodeContents(target);
                            return [...range.getClientRects()]
                                .filter(r => r.width > 0 && r.height > 0)
                                .map(r => ({y: r.y, width: r.width}));
                        };
                        const nameNode = [...node.childNodes].find(
                            n => n.nodeType === Node.TEXT_NODE && n.textContent.trim());
                        return {name: rects(nameNode), species: rects(node.querySelector('small')),
                                width: node.getBoundingClientRect().width,
                                minimum: parseFloat(getComputedStyle(node).minWidth),
                                whitespace: getComputedStyle(node).whiteSpace};
                    }""")
                    self.assertEqual(geometry['whitespace'], 'nowrap')
                    self.assertEqual(len(geometry['name']), 1)
                    self.assertEqual(len(geometry['species']), 1)
                    self.assertGreater(geometry['species'][0]['y'], geometry['name'][0]['y'])
                    assert_minimum_width(self, geometry['width'], geometry['minimum'])
                    self.assertEqual(cell.locator('small').inner_text(), name)
                    expected_name = name + (' - Ally' if active else '')
                    self.assertIn(expected_name, cell.inner_text())
                    self.assertEqual(page.locator('#monsters td button').count(), 11)
                    self.assertEqual(errors, [])
                    self.assertEqual(mutations, [])
                    page.close()


if __name__ == '__main__':
    unittest.main()
