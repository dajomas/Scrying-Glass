"""Real Chromium smoke checks for the Admin, User management and Client display pages.

Intercepted HTTP and a mocked WebSocket transport; does not test the FastAPI server.
(Formerly tests/browser_smoke_272cc73.py.)
"""
import json
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright
import test_encounter_features as fixtures
from web_html.admin_html import ADMIN_HTML
from web_html.client_html import CLIENT_HTML

ROOT = Path(__file__).resolve().parents[1]


class BrowserSmokeTests(unittest.TestCase):
    def test_admin_users_and_client_pages(self):
        fixture = fixtures.FeatureTests(methodName='test_death_saves')
        fixture.setUp()
        try:
            state=fixture.c.public_state()
            display=fixture.c.display_state()
            # Mock the complete authorized single-campaign viewer transport payload.
            assert display['campaign'] and display['campaign']['name']=='Default'
            display.update(viewer_campaigns=[dict(display['campaign'])],
                           viewer_selection_required=False,viewer_access_message='')
            summary=fixture.f.summary()
        finally:
            fixture.tearDown()
        state['monsters'][0]['initiative']=10
        state['characters'][0]['initiative']=15
        apis={
         '/api/state':state,'/api/features':summary,
         '/api/campaigns':{'active':'1','campaigns':[{'id':'1','name':'Default','description':'','setups':['default'],'last_setup':'default'}],'moved':[]},
         '/api/setups':{'campaign':'1','names':['default']},
         '/api/me':{'username':'dm','role':'superadmin'},
         '/api/users':[{'id':1,'username':'dm','role':'superadmin'}],
        }
        errors = []
        checks = []
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True,args=['--no-sandbox'])
            context=browser.new_context(viewport={'width':1440,'height':1000})
            context.set_default_timeout(4000)
            def route(request):
                path=urlsplit(request.request.url).path
                if path=='/admin':return request.fulfill(content_type='text/html',body=ADMIN_HTML)
                if path=='/display':return request.fulfill(content_type='text/html',body=CLIENT_HTML)
                if path=='/users':return request.fulfill(content_type='text/html',body=(ROOT/'templates/users.html').read_text())
                if path.startswith('/static/'):
                    target=ROOT/path.lstrip('/')
                    if not target.is_file():return request.fulfill(status=404)
                    kind='text/javascript' if target.suffix=='.js' else ('text/css' if target.suffix=='.css' else 'image/x-icon')
                    return request.fulfill(content_type=kind,body=target.read_bytes())
                if path.startswith('/api/'):
                    return request.fulfill(content_type='application/json',body=json.dumps(apis.get(path,{})))
                return request.fulfill(status=404)
            context.route('**/*',route)
            admin=context.new_page();admin.on('pageerror',lambda error:errors.append('admin: '+str(error)))
            admin.goto('http://audit.test/admin');admin.wait_for_function("typeof latest !== 'undefined' && latest && latest.monsters.length === 1")
            assert admin.locator('#startBattle').count()==1
            assert admin.locator('button[data-select-all-kind="monsters"]').count()==1
            admin.wait_for_function("document.body.dataset.workflowNavigation === 'ready'")
            assert admin.locator('#adminWorkflow-campaign').get_attribute('aria-selected')=='true'
            admin.locator('#adminWorkflow-preparation').click()
            assert admin.locator('body').get_attribute('data-workflow-view')=='preparation'
            if not admin.locator('#monsterDisplayPane').is_visible():
                admin.locator('#toggleMonsterDisplayPane').click()
            assert admin.locator('#monsterDisplayPane').is_visible()
            admin.locator('button[data-select-all-kind="monsters"]').click()
            assert admin.locator('input[data-select-kind="monsters"]').first.is_checked()
            checks.append('admin assembled page, scripts, state load and select-all')
            users=context.new_page();users.on('pageerror',lambda error:errors.append('users: '+str(error)))
            users.goto('http://audit.test/users');users.wait_for_selector('#userRows tr')
            users.get_by_role('button',name='Edit',exact=True).click()
            assert users.locator('#username').input_value()=='dm'
            checks.append('user-management page load and edit selection')
            client=context.new_page();client.on('pageerror',lambda error:errors.append('client: '+str(error)))
            client.add_init_script("""
            window.__sockets=[];
            window.WebSocket=class {
              static OPEN=1;static CONNECTING=0;
              constructor(){this.readyState=0;window.__sockets.push(this);setTimeout(()=>{this.readyState=1;this.onopen?.({});},0);}
              send(message){(this.sent??=[]).push(JSON.parse(message));}
              close(){this.readyState=3;this.onclose?.({code:1006,reason:'simulated drop',wasClean:false});}
            };
            """)
            client.goto('http://audit.test/display');client.wait_for_function('window.__sockets[0]?.readyState === 1')
            client.evaluate('(state)=>window.__sockets.at(-1).onmessage({data:JSON.stringify({type:"state",revision:1,state})})',display)
            assert client.locator('#stage .monster').count()==1
            assert 'Goblin' in client.locator('#stage').inner_text()
            assert 'Default' in client.locator('#clientCampaign').inner_text()
            client.evaluate('window.__card=document.querySelector("#stage .monster");window.__sockets.at(-1).close()')
            assert client.locator('#stage .monster').count()==1
            client.wait_for_function('window.__sockets.length === 2 && window.__sockets[1].readyState === 1')
            client.evaluate('(state)=>window.__sockets.at(-1).onmessage({data:JSON.stringify({type:"state",revision:1,state})})',display)
            assert client.evaluate('window.__card===document.querySelector("#stage .monster")')
            checks.append('client snapshot, retained card during disconnect, unchanged reconnect preserves DOM identity')
            client.set_viewport_size({'width':390,'height':844})
            assert client.locator('#stage .monster').bounding_box()['width']>0
            checks.append('client card has a positive layout width at mobile viewport')
            browser.close()
        self.assertEqual(errors, [])
        self.assertEqual(len(checks), 4)


if __name__ == '__main__':
    unittest.main()
