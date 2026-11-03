"""Chromium UI fixture with intercepted HTTP, not a live authenticated server."""
import copy
import json
import unittest
from pathlib import Path
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

ROOT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(sync_playwright, 'Playwright unavailable')
class StatisticsLayoutTests(unittest.TestCase):
    def test_affected_only_responsive_table_and_restoration(self):
        markup=(ROOT/'templates/admin/180_battle_action_modal.html').read_text()
        modal=markup[markup.index('  <div id="statisticsModal"'):]
        css='\n'.join((ROOT/p).read_text() for p in ('static/glass-theme.css','static/admin.css','static/statistics.css'))
        script=(ROOT/'static/statistics.js').read_text()
        state=dict(active_campaign_id='1',active_setup={'name':'test'},statistics_token='token',monsters=[],characters=[dict(id='c',name='Johan',hp=0,max_hp=0,base_max_hp=1,effects=[dict(mechanical=dict(version=1,stat='max_hp',amount=9))])])
        requests=[]
        html='<html><head><style>'+css+'</style></head><body><button data-statistics="c">Restore statistics</button>'+modal+'<script>'+script+'</script></body></html>'
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1000,'height':900})
            def route(request_route):
                request=request_route.request
                if request.url.endswith('/api/state'):
                    request_route.fulfill(json=state)
                elif request.method=='POST':
                    body=request.post_data_json;requests.append(body)
                    if body['operation']=='restore':
                        state['characters'][0]['effects']=[];state['characters'][0]['max_hp']=1
                    request_route.fulfill(json=state['characters'][0])
                else:
                    request_route.fulfill(content_type='text/html',body=html)
            page.route('http://sg.test/**',route)
            page.goto('http://sg.test/')
            page.click('[data-statistics]')
            page.wait_for_selector('#statisticsFields tbody tr')
            self.assertEqual(page.locator('#statisticsFields tbody tr').count(),1)
            self.assertEqual(page.locator('#statisticsFields tbody th').inner_text(),'Max HP')
            self.assertEqual(page.locator('#statisticsFields tbody td').all_inner_texts(),['1','9','0'])
            self.assertEqual(page.locator('#statisticsRestoreStat option').count(),1)
            self.assertEqual(page.locator('#statisticsFields input').count(),0)
            self.assertEqual(page.locator('#statisticsFields thead th').all_inner_texts(),['Statistic','Original/base','Reduction','Effective'])
            for width in (1000,697,375):
                page.set_viewport_size({'width':width,'height':900})
                self.assertTrue(page.locator('#statisticsFields').evaluate('(e)=>e.scrollWidth<=e.clientWidth+1'))
                self.assertTrue(page.locator('.statistics-dialog').evaluate('(e)=>{const r=e.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&r.height<=innerHeight;}'))
            dismiss=lambda dialog:dialog.dismiss()
            page.on('dialog',dismiss)
            page.click('#statisticsRestore');self.assertEqual(requests,[])
            page.remove_listener('dialog',dismiss);page.on('dialog',lambda dialog:dialog.accept())
            page.click('#statisticsRestore')
            page.wait_for_selector('.statistics-empty')
            self.assertTrue(page.locator('#statisticsRestore').is_disabled())
            self.assertTrue(page.locator('#statisticsRestoreStat').is_disabled())
            self.assertEqual(state['characters'][0]['hp'],0)
            page.click('#statisticsEditBases')
            self.assertEqual(page.locator('[data-base-stat]').count(),7)
            self.assertTrue(page.locator('#statisticsRestoreControls').is_hidden())
            self.assertTrue(page.locator('#statisticsSaveBases').is_visible())
            page.fill('[data-base-stat="dexterity"]','14')
            page.evaluate('window.scryingStatisticsState({active_campaign_id:"1",active_setup:{name:"test"}})')
            self.assertEqual(page.input_value('[data-base-stat="dexterity"]'),'14')
            page.click('#statisticsBack')
            self.assertEqual(page.locator('#statisticsFields tbody tr').count(),0)
            page.evaluate('window.scryingStatisticsState({active_campaign_id:"2",active_setup:null})')
            self.assertTrue(page.locator('#statisticsModal').is_hidden())
            browser.close()

if __name__=='__main__':unittest.main()
