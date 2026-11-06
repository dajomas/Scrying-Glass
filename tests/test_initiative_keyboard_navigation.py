"""SG-TODO-013: Chromium fixtures; full Admin uses intercepted HTTP, not live storage."""
import copy
import json
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'static/initiative-keyboard-navigation.js'


class InitiativeNavigationFixtures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = sync_playwright().start()
        cls.browser = cls.p.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.p.stop()

    def setUp(self):
        self.page = self.browser.new_page()
        self.addCleanup(self.page.close)
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.set_content('<button id="before">Before</button><div id="characters"></div><input id="outside"><div id="monsters"></div>')
        self.page.add_script_tag(content="""let latest = {active_campaign_id:'1',active_setup:{campaign_id:'1',name:'first'}};
            window.saves=[];
            window.renderRoster=(kind,ids=['a','b','c'])=>{
                const attr=kind==='characters'?'data-ci':'data-mi';
                document.getElementById(kind).innerHTML='<table><tr><td>'+ids.map(id=>
                    '<input type="number" '+attr+'="'+id+'" value="10"><button>Edit</button>').join('')+'</td></tr></table>';
            };
            renderRoster('characters');renderRoster('monsters');
            document.addEventListener('change',e=>saves.push(e.target.value));""")
        self.page.add_script_tag(path=str(SCRIPT))

    def field(self, kind, ident):
        return self.page.locator('#'+kind+' input['+('data-ci' if kind=='characters' else 'data-mi')+'="'+ident+'"]')

    def focused(self, kind, ident):
        self.assertTrue(self.field(kind, ident).evaluate('n=>n===document.activeElement'))

    def test_forward_reverse_wrapping_escape_and_idempotence(self):
        for width in (1440, 375):
            self.page.set_viewport_size({'width':width,'height':900})
            self.page.add_script_tag(path=str(SCRIPT))
            for kind in ('characters','monsters'):
                self.field(kind,'a').focus()
                self.page.keyboard.press('Tab'); self.focused(kind,'b')
                self.page.keyboard.press('Tab'); self.focused(kind,'c')
                self.page.keyboard.press('Tab'); self.focused(kind,'a')
                self.page.keyboard.press('Shift+Tab'); self.focused(kind,'c')
                self.page.keyboard.press('Shift+Tab'); self.focused(kind,'b')
                self.page.keyboard.press('Shift+Tab'); self.focused(kind,'a')
                self.page.keyboard.press('Escape')
                self.assertEqual(self.page.locator(':focus').get_attribute('id'),kind)
                self.page.evaluate('(kind)=>renderRoster(kind)',kind)
                self.assertEqual(self.page.locator(':focus').get_attribute('id'),kind)
                self.page.keyboard.press('Tab'); self.focused(kind,'a')
                self.page.keyboard.press('Tab')
                self.assertEqual(self.page.locator(':focus').inner_text(),'Edit')
                self.page.locator('#outside').focus()
                self.field(kind,'c').focus(); self.page.keyboard.press('Tab'); self.focused(kind,'a')
                self.page.keyboard.press('Escape'); self.page.keyboard.press('Shift+Tab')
                self.assertEqual(self.page.locator(':focus').get_attribute('id'),'before' if kind=='characters' else 'outside')
                self.field(kind,'c').click(); self.page.keyboard.press('Tab'); self.focused(kind,'a')
        self.assertEqual(self.page.evaluate('saves'),[])
        self.assertEqual(self.errors,[])

    def test_rerender_keeps_identity_and_unsaved_destination_draft(self):
        for kind in ('characters','monsters'):
            self.field(kind,'a').fill('17')
            self.page.keyboard.press('Tab'); self.focused(kind,'b')
            self.field(kind,'b').fill('23')
            self.page.evaluate('(kind)=>renderRoster(kind,["c","b","a"])',kind)
            self.page.wait_for_function('(kind)=>document.activeElement?.getAttribute(kind==="characters"?"data-ci":"data-mi")==="b"',arg=kind)
            self.assertEqual(self.field(kind,'b').input_value(),'23')
            self.page.keyboard.press('Tab'); self.focused(kind,'a')
        self.assertEqual(self.page.evaluate('saves'),['17','23','17','23'])
        self.assertEqual(self.errors,[])

    def test_hidden_disabled_readonly_single_and_modified_keys(self):
        self.field('characters','b').evaluate('n=>n.disabled=true')
        self.field('characters','a').focus(); self.page.keyboard.press('Tab'); self.focused('characters','c')
        self.field('characters','b').evaluate('n=>{n.disabled=false;n.readOnly=true;}')
        self.field('characters','a').focus(); self.page.keyboard.press('Tab'); self.focused('characters','c')
        self.field('characters','b').evaluate('n=>{n.readOnly=false;n.hidden=true;}')
        self.field('characters','a').focus(); self.page.keyboard.press('Tab'); self.focused('characters','c')
        self.page.keyboard.press('Tab'); self.focused('characters','a')
        self.assertFalse(self.field('characters','a').evaluate('n=>{const e=new KeyboardEvent("keydown",{key:"Tab",ctrlKey:true,bubbles:true,cancelable:true});n.dispatchEvent(e);return e.defaultPrevented;}'))
        self.page.evaluate('renderRoster("characters",["a"])')
        self.field('characters','a').focus(); self.page.keyboard.press('Tab'); self.focused('characters','a')
        self.page.keyboard.press('Shift+Tab'); self.focused('characters','a')
        self.page.keyboard.press('Escape')
        self.assertEqual(self.page.locator(':focus').get_attribute('id'),'characters')
        self.page.keyboard.press('Tab'); self.focused('characters','a')
        self.page.keyboard.press('Tab')
        self.assertEqual(self.page.locator(':focus').inner_text(),'Edit')
        self.page.evaluate('renderRoster("characters",[])')
        self.assertEqual(self.errors,[])

    def test_restored_programmatic_draft_emits_one_missing_change(self):
        self.field('characters','a').focus(); self.page.keyboard.press('Tab')
        self.field('characters','b').evaluate('n=>n.value="23"')
        self.page.evaluate('renderRoster("characters")')
        self.page.wait_for_function('document.activeElement?.getAttribute("data-ci")==="b"')
        self.page.keyboard.press('Tab'); self.focused('characters','c')
        self.assertEqual(self.page.evaluate('saves'),['23'])
        self.page.evaluate('renderRoster("characters")')
        self.assertEqual(self.page.evaluate('saves'),['23'])
        self.assertEqual(self.errors,[])

    def test_pointer_scope_and_removed_target_do_not_steal_focus(self):
        self.field('characters','a').focus(); self.page.keyboard.press('Tab')
        self.page.locator('#outside').click()
        self.page.evaluate('renderRoster("characters")')
        self.assertEqual(self.page.locator(':focus').get_attribute('id'),'outside')
        self.field('characters','a').focus(); self.page.keyboard.press('Tab')
        self.page.evaluate('latest.active_setup.name="second";renderRoster("characters")')
        self.assertEqual(self.page.evaluate('document.activeElement.tagName'),'BODY')
        self.field('characters','a').focus(); self.page.keyboard.press('Tab')
        self.page.evaluate('renderRoster("characters",["a","c"])')
        self.assertEqual(self.page.evaluate('document.activeElement.tagName'),'BODY')
        self.assertEqual(self.errors,[])


class InitiativeNavigationAdminTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows=rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def test_asset_and_size_contract(self):
        end=(ROOT/'templates/admin/190_document_end.html').read_text()
        self.assertEqual(end.count('/static/initiative-keyboard-navigation.js?v=1'),1)
        self.assertLess(end.index('/static/character-hp-display.js'),end.index('/static/initiative-keyboard-navigation.js'))
        self.assertLessEqual(SCRIPT.stat().st_size,20000)
        source=SCRIPT.read_text()
        for forbidden in ('fetch(', 'localStorage', 'subtree: true'):
            self.assertNotIn(forbidden,source)

    def test_wrapping_and_escape_exit_on_full_admin(self):
        for width in (1440,375):
            page,errors,mutations=self.rows.open_page(self,width)
            for kind,attr in (('characters','data-ci'),('monsters','data-mi')):
                editor=page.locator('#'+kind+' input['+attr+']').first
                ident=editor.get_attribute(attr)
                editor.focus(); page.keyboard.press('Tab')
                self.assertEqual(page.locator(':focus').get_attribute(attr),ident)
                page.keyboard.press('Shift+Tab')
                self.assertEqual(page.locator(':focus').get_attribute(attr),ident)
                page.keyboard.press('Escape')
                self.assertEqual(page.locator(':focus').get_attribute('id'),kind)
                page.keyboard.press('Tab')
                self.assertEqual(page.locator(':focus').get_attribute('data-select-kind'),kind)
                page.keyboard.press('Tab')
                self.assertEqual(page.locator(':focus').get_attribute(attr),ident)
                page.keyboard.press('Tab')
                self.assertEqual(page.locator(':focus').inner_text(),'Edit')
            self.assertEqual(errors,[])
            self.assertEqual(mutations,[])
            page.close()

    def test_native_change_save_refresh_and_rejection(self):
        for width in (1440,375):
            for kind,attr,notice in (('characters','data-ci','characterAddNotification'),('monsters','data-mi','monsterAddNotification')):
                with self.subTest(width=width,kind=kind):
                    page,errors,mutations=self.rows.open_page(self,width)
                    state=copy.deepcopy(self.snapshot)
                    state[kind]=[dict(state[kind][0],id='sg013-'+str(i),initiative=10-i,active=False) for i in range(3)]
                    calls=[]
                    reject=[False]
                    def serve(route):
                        route.fulfill(content_type='application/json',body=json.dumps(state))
                    def save(route):
                        self.assertEqual(route.request.method,'PATCH')
                        payload=route.request.post_data_json
                        ident=route.request.url.rsplit('/',1)[-1]
                        calls.append((ident,payload))
                        if reject[0]:
                            route.fulfill(status=400,json={'detail':'Fixture initiative rejection'})
                        else:
                            next(item for item in state[kind] if item['id']==ident).update(payload)
                            route.fulfill(json={})
                    page.route('**/api/state',serve)
                    page.route('**/api/'+kind+'/sg013-*',save)
                    page.evaluate('load(true)')
                    fields=page.locator('#'+kind+' input['+attr+']')
                    self.assertEqual(fields.count(),3)
                    ids=fields.evaluate_all('(nodes)=>nodes.map(n=>n.getAttribute("'+attr+'"))')
                    page.evaluate('(kind)=>window.oldTable=document.querySelector("#"+kind+" table")',kind)
                    fields.nth(0).fill('17')
                    with page.expect_response(lambda r: '/api/'+kind+'/sg013-' in r.url and r.request.method=='PATCH'):
                        page.keyboard.press('Tab')
                    page.wait_for_function('([kind,attr,id])=>document.querySelector("#"+kind+" table")!==oldTable && document.activeElement?.getAttribute(attr)===id',arg=[kind,attr,ids[1]])
                    self.assertEqual(calls,[(ids[0],{'initiative':17})])
                    reject[0]=True
                    page.locator('#'+kind+' input['+attr+'="'+ids[1]+'"]').fill('1.5')
                    with page.expect_response(lambda r: '/api/'+kind+'/sg013-' in r.url and r.request.method=='PATCH'):
                        page.keyboard.press('Tab')
                    page.wait_for_function('(id)=>document.getElementById(id).textContent.includes("Fixture initiative rejection")',arg=notice)
                    self.assertEqual(page.locator(':focus').get_attribute(attr),ids[2])
                    self.assertEqual(calls[-1],(ids[1],{'initiative':1.5}))
                    self.assertEqual(len(calls),2)
                    self.assertEqual(errors,[])
                    self.assertEqual(mutations,[])
                    page.close()


if __name__=='__main__':
    unittest.main()
