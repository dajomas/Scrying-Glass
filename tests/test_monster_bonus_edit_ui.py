"""Native Chromium Edit fixtures with recorded transport, not live HTTP/storage."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MonsterBonusEditUITests(unittest.TestCase):
    def test_script_is_loaded_after_admin(self):
        end = (ROOT / "templates/admin/190_document_end.html").read_text(encoding="utf-8")
        self.assertEqual(end.count('/static/monster-initiative-edit.js?v=1'), 1)
        self.assertLess(end.index('/static/admin.js'), end.index('/static/monster-initiative-edit.js?v=1'))

    def test_native_edit_render_submission_and_character_isolation(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for width in (375, 1440):
                    page = browser.new_page(viewport={"width": width, "height": 900})
                    page.set_content('<div id="editModal" hidden><h2 id="editTitle"></h2><form id="editForm"></form></div>')
                    page.add_script_tag(content="""
                        let editing = null;
                        const latest = {monsters: [{id:'m',name:'Dragon',monster_species:'dragon',ac:18,
                            hp:20,max_hp:20,original_hp:20,color:'#842029',initiative:112,
                            initiative_bonus:96,initiative_bonus_origin:'source',initiative_roll:16}],
                            characters:[{id:'c',name:'Hero',color:'#123456',hp:20,max_hp:20,initiative:21}]};
                        const editModal = document.querySelector('#editModal');
                        function esc(value) { const node=document.createElement('span'); node.textContent=String(value??''); return node.innerHTML.replaceAll('"','&quot;'); }
                        function setColorPreview() {}
                        function closeEdit() { editModal.hidden=true; editing=null; }
                        const sent=[]; const notices=[]; let characterSaves=0;
                        async function request(url, options) {
                            sent.push({url, method:options.method, fields:[...options.body].map(([key,value])=>[key,value instanceof File?value.name:value])});
                            if(window.rejectSave) throw new Error('rejected');
                            return {};
                        }
                        async function load() { if(window.rejectRefresh) throw new Error('refresh unavailable'); }
                        function paneNotification(kind,text) { notices.push({kind,text}); }
                        document.querySelector('#editForm').onsubmit=async event=>{event.preventDefault();characterSaves++;};
                    """)
                    page.add_script_tag(content=(ROOT / 'static/admin/020-source.js').read_text(encoding='utf-8'))
                    page.add_script_tag(content=(ROOT / 'static/monster-initiative-edit.js').read_text(encoding='utf-8'))
                    page.evaluate("openEdit('monsters','m')")
                    bonus = page.locator('[name="initiative_bonus"]')
                    self.assertEqual(bonus.input_value(), '96')
                    self.assertTrue(page.locator('[name="initiative"]').evaluate('(input)=>input.readOnly'))
                    self.assertIsNone(page.locator('[name="initiative"]').get_attribute('max'))
                    self.assertTrue(page.locator('#editForm').evaluate('(form)=>form.checkValidity()'))
                    for value in ('12', '-2', '0', '+12', '9223372036854775807'):
                        page.evaluate("openEdit('monsters','m')")
                        page.locator('[name="initiative_bonus"]').fill(value)
                        page.get_by_role('button', name='Save monster').click()
                        page.wait_for_function("editing === null")
                        fields = dict(page.evaluate('sent.at(-1).fields'))
                        self.assertEqual(fields['initiative_bonus'], value)
                        self.assertEqual(fields['initiative'], '112')
                        self.assertNotIn('initiative_bonus_origin', fields)
                        self.assertEqual(page.evaluate('sent.at(-1).url'), '/api/monsters/m/edit')
                        self.assertEqual(page.evaluate('sent.at(-1).method'), 'POST')
                    for value in ('96', ''):
                        page.evaluate("openEdit('monsters','m')")
                        page.locator('[name="initiative_bonus"]').fill(value)
                        page.get_by_role('button', name='Save monster').click()
                        page.wait_for_function("editing === null")
                        self.assertNotIn('initiative_bonus', dict(page.evaluate('sent.at(-1).fields')))
                    page.evaluate("openEdit('monsters','m')")
                    page.locator('[name="initiative_bonus"]').fill('1.5')
                    self.assertFalse(page.locator('#editForm').evaluate('(form)=>form.checkValidity()'))
                    page.evaluate("openEdit('characters','c')")
                    self.assertEqual(page.locator('[name="initiative_bonus"]').count(), 0)
                    self.assertFalse(page.locator('[name="initiative"]').evaluate('(input)=>input.readOnly'))
                    page.get_by_role('button', name='Save character').click()
                    page.wait_for_function('characterSaves === 1')
                    page.evaluate("openEdit('monsters','m')")
                    before = page.evaluate('sent.length')
                    page.get_by_role('button', name='Cancel').click()
                    self.assertEqual(page.evaluate('sent.length'), before)
                    page.close()
            finally:
                browser.close()

    def test_image_rejection_and_refresh_failure(self):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.set_content('<form id="editForm"><input name="name" value="Dragon"><input name="monster_species" value="dragon"><input name="initiative" value="28"><input name="initiative_bonus" value="10" data-assigned-bonus="12"><input name="image" type="file"><button>Save</button></form>')
                page.add_script_tag(content="""
                    let editing={kind:'monsters',id:'m'};
                    function monsterEdit(){return '';}
                    const sent=[]; const notices=[];
                    async function request(url,options){ sent.push([...options.body].map(([key,value])=>[key,value instanceof File?value.name:value])); if(window.rejectSave)throw new Error('rejected'); }
                    function closeEdit(){editing=null;}
                    async function load(){if(window.rejectRefresh)throw new Error('refresh unavailable');}
                    function paneNotification(kind,text){notices.push(text);}
                    document.querySelector('#editForm').onsubmit=()=>{};
                """)
                page.add_script_tag(content=(ROOT / 'static/monster-initiative-edit.js').read_text(encoding='utf-8'))
                page.locator('[name="image"]').set_input_files({'name':'dragon.png','mimeType':'image/png','buffer':b'image-fixture'})
                page.evaluate('window.rejectSave=true')
                page.get_by_role('button', name='Save').click()
                page.wait_for_function('notices.length === 1')
                self.assertEqual(dict(page.evaluate('sent[0]'))['image'], 'dragon.png')
                self.assertEqual(page.evaluate('editing.id'), 'm')
                self.assertFalse(page.locator('[name="initiative_bonus"]').is_disabled())
                self.assertIsNone(page.locator('#editForm').get_attribute('aria-busy'))
                page.evaluate('window.rejectSave=false; window.rejectRefresh=true')
                page.get_by_role('button', name='Save').click()
                page.wait_for_function('notices.length === 2')
                self.assertIsNone(page.evaluate('editing'))
                self.assertIn('Monster saved, but refresh failed', page.evaluate('notices[1]'))
            finally:
                browser.close()
