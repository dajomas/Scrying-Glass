"""Browser UI fixtures; requires Playwright and its Chromium browser."""
import json
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
CHOICES=[{'id':'1','name':'First campaign'},{'id':'2','name':'Second campaign'}]

class ViewerBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=sync_playwright().start();cls.browser=cls.p.chromium.launch(headless=True)
    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.p.stop()
    def setUp(self):
        self.page=self.browser.new_page()
        self.page.route('http://viewer.test/**',lambda route:route.fulfill(body='<html><body></body></html>',content_type='text/html'))
        self.page.goto('http://viewer.test/display')
        self.page.set_content('<button id="clientCampaign">Campaign</button><div id="stage"></div>')
        self.page.add_style_tag(content=(ROOT/'static/viewer-campaigns.css').read_text())
        self.page.add_script_tag(content=(ROOT/'static/viewer-campaigns.js').read_text())
    def tearDown(self):self.page.close()
    def render(self,choices=CHOICES,selected=None,required=True,message=''):
        self.page.evaluate('state=>window.renderViewerCampaignSelection(state)',{
            'viewer_campaigns':choices,'campaign':selected,'viewer_selection_required':required,'viewer_access_message':message})
    def test_multiple_choices_open_required_popup(self):
        self.render();self.assertTrue(self.page.locator('#viewerCampaignDialog').is_visible())
        self.assertEqual(self.page.locator('.viewer-campaign-list button').count(),2)
        self.page.keyboard.press('Escape');self.assertTrue(self.page.locator('#viewerCampaignDialog').is_visible())
    def test_single_choice_does_not_open_popup(self):
        self.render(choices=CHOICES[:1],selected=CHOICES[0],required=False)
        self.assertFalse(self.page.locator('#viewerCampaignDialog').is_visible())
        self.assertTrue(self.page.locator('#clientCampaign').is_disabled())
    def test_campaign_heading_reopens_switcher_for_multiple_grants(self):
        self.render(selected=CHOICES[0],required=False);self.page.locator('#clientCampaign').click()
        self.assertTrue(self.page.locator('#viewerCampaignDialog').is_visible())
        self.page.get_by_role('button',name='Cancel').click()
        self.assertFalse(self.page.locator('#viewerCampaignDialog').is_visible())
    def test_selection_changes_only_viewer_url(self):
        self.render();self.page.get_by_role('button',name='Second campaign',exact=True).click()
        self.page.wait_for_url('**/display?campaign_id=2')
        self.assertEqual(self.page.url,'http://viewer.test/display?campaign_id=2')
    def test_revocation_forces_selection_from_remaining_grants(self):
        self.render(selected=CHOICES[0],required=False)
        self.render(choices=CHOICES[1:],required=True,message='Viewer access was removed.')
        self.assertTrue(self.page.locator('#viewerCampaignDialog').is_visible())
        self.assertEqual(self.page.locator('.viewer-campaign-list button').count(),1)
        self.assertIn('Viewer access was removed.',self.page.locator('#viewerCampaignDialog').inner_text())
    def test_no_grants_show_access_message_without_popup(self):
        self.render(choices=[],required=False,message='No campaign access has been granted.')
        self.assertTrue(self.page.locator('#clientCampaign').is_disabled())
        self.assertEqual(self.page.locator('#clientCampaign').inner_text(),'No campaign access has been granted.')
        self.assertFalse(self.page.locator('#viewerCampaignDialog').is_visible())
    def test_campaign_names_render_as_text_not_html(self):
        self.render(choices=[{'id':'1','name':'<img src=x onerror=alert(1)>'}],required=True)
        self.assertEqual(self.page.locator('.viewer-campaign-list img').count(),0)
    def test_admin_can_save_multiple_client_viewers(self):
        html=(ROOT/'templates/admin/030_campaign_input.html').read_text()
        self.page.set_content(html)
        self.page.evaluate("""() => {
            window.savedGrant=null;
            window.fetch=async(url,options={})=>{
                if(options.method==='PUT'){window.savedGrant={url,body:JSON.parse(options.body)};return {ok:true,json:async()=>({})};}
                if(url==='/api/campaigns')return {ok:true,json:async()=>({active:'1'})};
                return {ok:true,json:async()=>({campaign:{id:'1',name:'First campaign'},users:[
                    {id:'10',username:'alice',granted:true},{id:'11',username:'bob',granted:false}]})};
            };
        }""")
        self.page.add_script_tag(content=(ROOT/'static/campaign-viewer-admin.js').read_text())
        self.page.locator('#campaignViewerAccess').evaluate('(node)=>node.open=true')
        self.page.wait_for_function("document.querySelectorAll('#campaignViewerUsers input').length===2")
        self.page.locator('#campaignViewerUsers input[value="11"]').check()
        self.page.locator('#saveCampaignViewers').click()
        self.page.wait_for_function('window.savedGrant!==null')
        self.assertEqual(self.page.evaluate('window.savedGrant'),{'url':'/api/campaigns/1/viewers','body':{'user_ids':['10','11']}})

if __name__=='__main__':unittest.main()
