"""Chromium regressions for grants on selected authorized campaigns."""
import json
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

class ViewerSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.playwright.stop()
    def setUp(self):
        self.page = self.browser.new_page()
        self.page.route('http://tracker.test/**', lambda route: route.fulfill(body='<html><body></body></html>', content_type='text/html'))
        self.page.goto('http://tracker.test/')
    def tearDown(self): self.page.close()
    def install(self, allowed=None, active=None, selected='1', denied=None, delays=None):
        allowed = [{'id':'1','name':'Campaign one'}] if allowed is None else allowed
        self.page.set_content("""<span id="activeCampaignInfo">Campaign information</span>
<select id="campaignSelect"><option value="1">Campaign one</option><option value="2">Campaign two</option></select>
<details id="campaignViewerAccess" open><summary id="campaignViewerAccessTitle">Viewer access</summary>
<div id="campaignViewerUsers"></div><button id="saveCampaignViewers" disabled>Save viewer access</button>
<p id="campaignViewerNotice"></p></details>""")
        self.page.select_option('#campaignSelect', selected)
        self.page.evaluate(r"""config => {
            window._campaignData={active:config.active,campaigns:config.allowed};
            window._denied=config.denied;window._delays=config.delays||{};
            window._calls=[];window._saves=[];
            window.fetch=async(url,options={})=>{
                const method=options.method||'GET';window._calls.push({url,method});
                if(url==='/api/campaigns')return {ok:true,status:200,json:async()=>JSON.parse(JSON.stringify(window._campaignData))};
                const match=url.match(/^\/api\/campaigns\/(\d+)\/viewers$/);
                if(!match)throw new Error('Unexpected URL '+url);
                const id=match[1];
                if(window._delays[id])await new Promise(resolve=>setTimeout(resolve,window._delays[id]));
                if(window._denied===id)return {ok:false,status:403,json:async()=>({detail:'This campaign is not assigned to your admin account'})};
                if(method==='PUT')window._saves.push({id,body:JSON.parse(options.body)});
                return {ok:true,status:200,json:async()=>({campaign:{id,name:id==='1'?'Campaign one':'Campaign two'},users:[
                    {id:'10',username:'client-one',granted:true},{id:'11',username:'client-two',granted:false}]})};
            };
        }""", {'allowed':allowed,'active':active,'denied':denied,'delays':delays})
        self.page.add_script_tag(content=(ROOT/'static/campaign-viewer-admin.js').read_text())
    def wait_users(self):
        self.page.wait_for_function("document.querySelectorAll('#campaignViewerUsers input').length===2", timeout=5000)
    def test_user1_owned_campaign_shows_clients_with_no_global_active_access(self):
        self.install(active=None,selected='1');self.wait_users()
        self.assertEqual(self.page.locator('#campaignViewerAccessTitle').inner_text(),'Viewer access: Campaign one')
        self.assertIn('client-one',self.page.locator('#campaignViewerUsers').inner_text())
    def test_user2_globally_active_owned_campaign_still_shows_clients(self):
        self.install(allowed=[{'id':'2','name':'Campaign two'}],active='2',selected='2');self.wait_users()
        self.assertEqual(self.page.locator('#campaignViewerAccessTitle').inner_text(),'Viewer access: Campaign two')
    def test_selected_owned_campaign_takes_priority_over_global_active(self):
        self.install(allowed=[{'id':'1','name':'Campaign one'},{'id':'2','name':'Campaign two'}],active='2',selected='1');self.wait_users()
        self.assertEqual(self.page.locator('#campaignViewerAccessTitle').inner_text(),'Viewer access: Campaign one')
    def test_save_targets_selected_campaign_and_does_not_activate_it(self):
        self.install(active=None,selected='1');self.wait_users()
        self.page.locator('#campaignViewerUsers input[value="11"]').check()
        self.page.locator('#saveCampaignViewers').click()
        self.page.wait_for_function('window._saves.length===1')
        self.assertEqual(self.page.evaluate('window._saves'),[{'id':'1','body':{'user_ids':['10','11']}}])
        self.assertFalse(any('/activate' in call['url'] for call in self.page.evaluate('window._calls')))
    def test_no_assigned_campaigns_does_not_fetch_client_list(self):
        self.install(allowed=[],active=None)
        self.page.wait_for_function("document.getElementById('campaignViewerNotice').textContent.includes('No campaigns are assigned')")
        self.assertEqual(self.page.locator('#campaignViewerUsers input').count(),0)
        self.assertTrue(self.page.locator('#saveCampaignViewers').is_disabled())
        self.assertFalse(any('/viewers' in call['url'] for call in self.page.evaluate('window._calls')))
    def test_dropdown_change_reloads_grants_for_new_selected_campaign(self):
        self.install(allowed=[{'id':'1','name':'Campaign one'},{'id':'2','name':'Campaign two'}],active='1');self.wait_users()
        self.page.select_option('#campaignSelect','2')
        self.page.wait_for_function("document.getElementById('campaignViewerAccessTitle').textContent==='Viewer access: Campaign two'")
    def test_slow_previous_response_cannot_overwrite_new_selection(self):
        self.install(allowed=[{'id':'1','name':'Campaign one'},{'id':'2','name':'Campaign two'}],delays={'1':200,'2':5})
        self.page.wait_for_function("window._calls.some(call=>call.url==='/api/campaigns/1/viewers')")
        self.page.select_option('#campaignSelect','2');self.wait_users();self.page.wait_for_timeout(250)
        self.assertEqual(self.page.locator('#campaignViewerAccessTitle').inner_text(),'Viewer access: Campaign two')
    def test_forbidden_campaign_shows_error_instead_of_no_client_users(self):
        self.install(denied='1')
        self.page.wait_for_function("document.getElementById('campaignViewerNotice').textContent.includes('not assigned')")
        self.assertEqual(self.page.locator('#campaignViewerUsers input').count(),0)
        self.assertTrue(self.page.locator('#saveCampaignViewers').is_disabled())
    def test_selector_cannot_choose_campaign_outside_authorized_list(self):
        self.install(allowed=[{'id':'1','name':'Campaign one'}],active=None,selected='2');self.wait_users()
        self.assertEqual(self.page.locator('#campaignViewerAccessTitle').inner_text(),'Viewer access: Campaign one')
        self.assertFalse(any(call['url']=='/api/campaigns/2/viewers' for call in self.page.evaluate('window._calls')))
    def test_background_refresh_preserves_unsaved_checkbox_changes(self):
        self.install();self.wait_users();self.page.locator('#campaignViewerUsers input[value="11"]').check()
        count=len(self.page.evaluate('window._calls'))
        self.page.locator('#activeCampaignInfo').evaluate("node=>node.textContent='Refreshed campaign information'")
        self.page.wait_for_function('(count)=>window._calls.length>count',arg=count)
        self.assertTrue(self.page.locator('#campaignViewerUsers input[value="11"]').is_checked())

if __name__=='__main__':unittest.main()
