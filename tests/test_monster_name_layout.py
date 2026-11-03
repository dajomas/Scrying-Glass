"""Name-column regression checks on the intercepted-HTTP Admin page."""
import copy
import unittest
import test_monster_button_layout as layout


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
                    self.assertGreaterEqual(geometry['width'], geometry['minimum'])
                    self.assertEqual(cell.locator('small').inner_text(), name)
                    expected_name = name + (' - Ally' if active else '')
                    self.assertIn(expected_name, cell.inner_text())
                    self.assertEqual(page.locator('#monsters td button').count(), 11)
                    self.assertEqual(errors, [])
                    self.assertEqual(mutations, [])
                    page.close()


if __name__ == '__main__':
    unittest.main()
