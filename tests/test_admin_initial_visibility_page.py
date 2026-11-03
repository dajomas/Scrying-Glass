"""Assembled Admin page/scripts with intercepted HTTP, not authenticated live HTTP."""
from pathlib import Path
from urllib.parse import urlsplit
import json
import unittest
from playwright.sync_api import sync_playwright
import test_encounter_features as fixtures
from web_html.admin_html import ADMIN_HTML

ROOT = Path(__file__).resolve().parents[1]

class InitialVisibilityPageTests(unittest.TestCase):
    def test_real_page_boot_and_refresh_preserve_manual_visibility(self):
        fixture = fixtures.FeatureTests(methodName='test_death_saves')
        fixture.setUp()
        try:
            snapshot = fixture.c.public_state()
            summary = fixture.f.summary()
        finally:
            fixture.tearDown()
        campaign = snapshot['active_campaign_id']
        snapshot['active_setup'] = {'campaign_id': campaign, 'name': 'default'}
        apis = {
            '/api/state': snapshot, '/api/features': summary,
            '/api/campaigns': {'active': campaign, 'campaigns': [
                {'id': campaign, 'name': 'Default', 'description': '', 'setups': ['default'], 'last_setup': 'default'}], 'moved': []},
            '/api/setups': {'campaign': campaign, 'names': ['default']},
            '/api/me': {'username': 'dm', 'role': 'superadmin'},
            '/api/users': [{'id': 1, 'username': 'dm', 'role': 'superadmin'}],
        }
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page(viewport={'width': 1440, 'height': 1000})
                page.set_default_timeout(5000)
                errors = []
                mutations = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                def route(request):
                    path = urlsplit(request.request.url).path
                    if path == '/':
                        request.fulfill(content_type='text/html', body=ADMIN_HTML)
                    elif path.startswith('/static/'):
                        target = ROOT / path.lstrip('/')
                        if not target.is_file():
                            request.fulfill(status=404)
                        else:
                            kind = 'text/javascript' if target.suffix == '.js' else 'text/css' if target.suffix == '.css' else 'image/x-icon'
                            request.fulfill(content_type=kind, body=target.read_bytes())
                    elif path.startswith('/api/'):
                        if request.request.method != 'GET':
                            mutations.append(path)
                        request.fulfill(content_type='application/json', body=json.dumps(apis.get(path, {})))
                    else:
                        request.fulfill(status=404)
                page.route('**/*', route)
                page.goto('http://fixture.test/', wait_until='load')
                ids = ['campaignInputPane','characterInputPane','battleSetupInputPane','monsterInputPane','lairTools']
                page.wait_for_function('(ids) => ids.every(id => document.getElementById(id).hidden)', arg=ids)
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [], 'Initialization must not switch campaign/setup or mutate state')
                for button in ['toggleCampaignPane','toggleCharacterPane','toggleBattleSetupPane','toggleMonsterPane','toggleLairPane']:
                    self.assertEqual(page.locator('#'+button).get_attribute('aria-expanded'), 'false')
                page.locator('#toggleCampaignPane').click()
                page.wait_for_function("!document.querySelector('#campaignInputPane').hidden")
                page.evaluate('load(true)')
                self.assertFalse(page.locator('#campaignInputPane').evaluate('node => node.hidden'))
                self.assertTrue(page.locator('#characterInputPane').evaluate('node => node.hidden'))
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
            finally:
                browser.close()

if __name__ == '__main__':
    unittest.main()
