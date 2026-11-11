"""Native raw-roll transport and navigation fixtures; not live server checks."""
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from feedback_browser_fixture import install_feedback

ROOT=Path(__file__).resolve().parents[1]


class RawRollUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright=sync_playwright().start()
        cls.browser=cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def page(self,width):
        page=self.browser.new_page(viewport={"width":width,"height":900})
        self.addCleanup(page.close)
        page.set_content('<div id="monsterAddNotification"></div><div id="monsters" tabindex="0"></div><div id="characters" tabindex="0"><input data-ci="c" value="21"></div>')
        install_feedback(page)
        page.add_script_tag(content="""
            const latest={active_campaign_id:'a',active_setup:{campaign_id:'a',name:'one'},monsters:[
                {id:'m',name:'Dragon',initiative_roll:16,initiative_bonus:12,initiative:28},
                {id:'n',name:'Legacy',initiative_roll:null,initiative_bonus:-2,initiative:19}]};
            let legacyChanges=0,characterChanges=0,loads=0;
            const sent=[],notices=[];
            function monsterRow(item){return '<tr><td>'+item.name+'</td><td><input class="initiative-edit" type="number" data-mi="'+item.id+'" value="'+(item.initiative??'')+'"></td></tr>';}
            function draw(){document.querySelector('#monsters').innerHTML='<table><tr><th>Monster</th><th>Initiative</th></tr>'+latest.monsters.map(monsterRow).join('')+'</table>';}
            async function request(url,options){sent.push({url,method:options.method,body:JSON.parse(options.body)});if(window.rejectSave)throw new Error('rejected');return {};}
            async function load(){loads++;if(window.rejectRefresh)throw new Error('refresh failed');}
            function paneNotification(kind,text){notices.push(text);}
            document.addEventListener('change',event=>{if(event.target.dataset.mi)legacyChanges++;if(event.target.dataset.ci)characterChanges++;});
        """)
        page.add_script_tag(content=(ROOT/'static/initiative-keyboard-navigation.js').read_text())
        page.add_script_tag(content=(ROOT/'static/monster-initiative-roll.js').read_text())
        page.evaluate('draw()')
        return page

    def test_raw_values_separate_totals_and_only_raw_requests(self):
        for width in (375,1440):
            with self.subTest(width=width):
                page=self.page(width)
                self.assertEqual(page.locator('[data-mi="m"]').input_value(),'16')
                self.assertEqual(page.locator('[data-mi="n"]').input_value(),'')
                self.assertEqual(page.locator('.sg-monster-initiative-total').all_text_contents(),['Total: 28','Total: 19 (legacy)'])
                for index,value in enumerate(('16','10','16','0','-2','')):
                    page.eval_on_selector('[data-mi="m"]',"(input,value)=>{input.value=value;input.dispatchEvent(new Event('change',{bubbles:true}));}",value)
                    page.wait_for_function('(count)=>sent.length===count && loads===count',arg=index+1)
                    record=page.evaluate('sent.at(-1)')
                    self.assertEqual(record,dict(url='/api/monsters/m/initiative-roll',method='PATCH',body=dict(initiative_roll=None if value=='' else int(value))))
                self.assertEqual(page.evaluate('legacyChanges'),0)
                page.eval_on_selector('[data-ci="c"]',"input=>input.dispatchEvent(new Event('change',{bubbles:true}))")
                self.assertEqual(page.evaluate('characterChanges'),1)
                self.assertEqual(page.locator('[data-ci="c"]').input_value(),'21')
                before=page.evaluate('sent.length')
                page.eval_on_selector('[data-mi="m"]',"input=>{input.value='1.5';input.dispatchEvent(new Event('change',{bubbles:true}));}")
                self.assertEqual(page.evaluate('sent.length'),before)
                self.assertEqual(page.locator('.sg-monster-initiative-total').first.inner_text(),'Total: 28')
                page.close()

    def test_keyboard_draft_restoration_uses_raw_default(self):
        page=self.page(375)
        page.locator('[data-mi="m"]').focus()
        page.keyboard.press('Tab')
        self.assertEqual(page.locator(':focus').get_attribute('data-mi'),'n')
        page.locator('[data-mi="n"]').fill('7')
        page.evaluate('draw()')
        page.wait_for_function("document.activeElement.dataset.mi==='n' && document.activeElement.value==='7'")
        self.assertEqual(page.locator('[data-mi="n"]').evaluate('(input)=>input.defaultValue'),'')
        self.assertEqual(page.locator('.sg-monster-initiative-total').count(),2)
        page.keyboard.press('Shift+Tab')
        self.assertEqual(page.locator(':focus').get_attribute('data-mi'),'m')
        page.keyboard.press('Escape')
        self.assertEqual(page.locator(':focus').get_attribute('id'),'monsters')

    def test_initial_null_state_waits_for_first_render(self):
        page=self.browser.new_page()
        self.addCleanup(page.close)
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.set_content('<div id="monsters"></div>')
        install_feedback(page)
        page.add_script_tag(content="""
            let latest=null;
            function monsterRow(item){return '<tr><td><input type="number" data-mi="'+item.id+'" value="28"></td></tr>';}
            function paneNotification(){}
            async function request(){}
            async function load(){}
        """)
        page.add_script_tag(content=(ROOT/'static/monster-initiative-roll.js').read_text())
        page.evaluate("latest={monsters:[{id:'m',initiative_roll:16,initiative:28}]};document.querySelector('#monsters').innerHTML='<table>'+monsterRow(latest.monsters[0])+'</table>'")
        self.assertEqual(page.locator('[data-mi="m"]').input_value(),'16')
        self.assertEqual(page.locator('.sg-monster-initiative-total').inner_text(),'Total: 28')
        self.assertEqual(errors,[])
