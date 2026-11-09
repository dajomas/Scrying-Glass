"""Primary row alignment and compact status checks in assembled Admin with intercepted HTTP."""
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

    def test_primary_centres_and_compact_status_after_refresh(self):
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
                                const cell=node.closest('td'), row=cell.closest('tr');
                                const mid=box=>(box.top+box.bottom)/2;
                                const textMid=target=>{
                                    const range=document.createRange();range.selectNodeContents(target);
                                    return mid(range.getBoundingClientRect());
                                };
                                const name=[...cell.childNodes].find(n=>n.nodeType===Node.TEXT_NODE&&n.textContent.trim());
                                const nameRange=document.createRange();nameRange.selectNodeContents(name);
                                const nameBoxes=[...nameRange.getClientRects()].filter(box=>box.width>0&&box.height>0);
                                if(!nameBoxes.length)throw new Error('Name has no rendered text fragment');
                                const centres={name:mid(nameBoxes[0]),
                                    selection:mid(row.querySelector('input[data-select-id]').getBoundingClientRect()),
                                    initiative:mid(row.querySelector('input.initiative-edit').getBoundingClientRect())};
                                const headers=[...row.closest('table').rows[0].cells].map(n=>n.textContent.trim());
                                for(const caption of ['AC','HP','Initiative bonus']){
                                    const index=headers.indexOf(caption);
                                    if(index>=0)centres[caption]=textMid(row.cells[index]);
                                }
                                const hp=row.querySelector('.sg-character-hp');
                                if(hp)centres.hp=textMid(hp);
                                const bottoms=[...row.cells].map(target=>{
                                    const range=document.createRange();range.selectNodeContents(target);
                                    if(target===cell)range.setEndBefore(node);
                                    return range.getBoundingClientRect().bottom;
                                });
                                const root=parseFloat(getComputedStyle(document.documentElement).fontSize);
                                return {gap:node.getBoundingClientRect().top-Math.max(...bottoms),maxGap:root*.5,
                                    centres,nameLines:nameBoxes.length,tolerance:root*.2,
                                    reference:mid(row.querySelector('button[data-edit]').getBoundingClientRect())};
                            }""")
                            if kind == 'characters' and cycle == 1 and width <= 768:
                                self.assertGreater(metrics['nameLines'], 1, 'Long-name case must exercise wrapping')
                            self.assertGreaterEqual(metrics['gap'], 0)
                            self.assertLessEqual(metrics['gap'], metrics['maxGap'])
                            for label, centre in metrics['centres'].items():
                                self.assertAlmostEqual(centre, metrics['reference'], delta=metrics['tolerance'], msg=kind+' '+label)
                    self.assertEqual(calls, [])
                    self.assertEqual(mutations, [])
                    self.assertEqual(errors, [])
                    page.close()


if __name__ == '__main__':
    unittest.main()
