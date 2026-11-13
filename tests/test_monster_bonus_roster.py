"""Roster presentation fixtures, not raw-roll/API/storage acceptance."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MonsterBonusRosterTests(unittest.TestCase):
    def test_native_signed_column_redraw_and_isolation(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for width in (375, 1440):
                    page = browser.new_page(viewport={"width": width, "height": 900})
                    page.set_content('<div id="monsters"></div><div id="characters"><table><tr><th>Character</th><th>Initiative</th></tr><tr><td>Hero</td><td><input data-ci="c" value="21"></td></tr></table></div>')
                    page.add_script_tag(content="""
                        let requests=0;
                        window.fetch=()=>{requests++;throw new Error('presentation must not fetch');};
                        const latest={monsters:[
                            {id:'a',initiative_bonus:12,initiative_bonus_origin:'source'},
                            {id:'b',initiative_bonus:-2,initiative_bonus_origin:'manual'},
                            {id:'c',initiative_bonus:0,initiative_bonus_origin:'manual'},
                            {id:'d'}, {id:'e',initiative_bonus:1.5},
                            {id:'f',initiative_bonus:null}, {id:'g',initiative_bonus:9007199254740992}
                        ]};
                        function draw(){
                            document.querySelector('#monsters').innerHTML='<table><tr><th>Select</th><th>Monster</th><th>AC</th><th>HP</th><th>Initiative</th><th>Display/status</th><th>HP change</th></tr>'+
                            latest.monsters.map((item,index)=>'<tr><td><input type="checkbox" data-select-kind="monsters" data-select-id="'+item.id+'" '+(index===0?'checked':'')+'></td><td>Monster '+item.id+'</td><td>18</td><td>20/20</td><td><input data-mi="'+item.id+'" value="28"></td><td><button data-edit="'+item.id+'">Edit</button></td><td><button data-d="'+item.id+'">Damage</button><button data-h="'+item.id+'">Heal</button></td></tr>').join('')+'</table>';
                        }
                        draw();
                        const originalInput=document.querySelector('[data-mi="a"]');
                        const characterMarkup=document.querySelector('#characters').innerHTML;
                        const stateBefore=JSON.stringify(latest);
                    """)
                    page.add_script_tag(content=(ROOT/'static/combatant-row-layout.js').read_text(encoding='utf-8'))
                    page.add_script_tag(content=(ROOT/'static/monster-initiative-roster.js').read_text(encoding='utf-8'))
                    page.wait_for_function("document.querySelectorAll('td.sg-monster-initiative-bonus').length === 7")
                    headers = page.locator('#monsters th').all_text_contents()
                    self.assertEqual(headers, ['Select','Monster','AC','HP','Initiative bonus','Initiative','Display/status'])
                    self.assertEqual(page.locator('td.sg-monster-initiative-bonus').all_text_contents(),
                                     ['+12','-2','+0','+0','Unavailable','Unavailable','Unavailable'])
                    self.assertEqual(page.locator('th.sg-monster-initiative-bonus').get_attribute('scope'), 'col')
                    self.assertEqual(page.locator('td.sg-monster-initiative-bonus input').count(), 0)
                    self.assertIn('(source)', page.locator('td.sg-monster-initiative-bonus').first.get_attribute('title'))
                    self.assertTrue(page.locator('[data-select-id="a"]').is_checked())
                    self.assertTrue(page.evaluate("originalInput === document.querySelector('[data-mi=\"a\"]')"))
                    self.assertEqual(page.locator('[data-mi="a"]').input_value(), '28')
                    self.assertEqual(page.evaluate('JSON.stringify(latest)'), page.evaluate('stateBefore'))
                    self.assertEqual(page.locator('#characters').inner_html(), page.evaluate('characterMarkup'))
                    page.evaluate('draw()')
                    page.wait_for_function("document.querySelectorAll('th.sg-monster-initiative-bonus').length === 1")
                    self.assertEqual(page.locator('td.sg-monster-initiative-bonus').count(), 7)
                    self.assertEqual(page.evaluate('requests'), 0)
                    page.close()
            finally:
                browser.close()

    def test_missing_region_and_unrecognized_header_are_noop(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for html in ('<div id="characters">Only characters</div>',
                             '<div id="monsters"><table><tr><th>Unknown</th></tr></table></div>'):
                    page=browser.new_page()
                    page.set_content(html)
                    before=page.locator('body').inner_html()
                    page.add_script_tag(content=(ROOT/'static/monster-initiative-roster.js').read_text(encoding='utf-8'))
                    self.assertEqual(page.locator('body').inner_html().split('<script>')[0], before)
                    page.close()
            finally:
                browser.close()
