"""Parser/defer ordering regression using production feedback/modal/end assets.

Other Admin scripts are transport/helper stubs. The existing complete assembled
page smoke check remains the full-script integration gate.
"""
from pathlib import Path
from urllib.parse import urlsplit
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FEEDBACK_ASSETS = ('admin-feedback-controller.js', 'admin-feedback-view.js', 'admin-feedback-admin.js')

class BattleActionsNextBootTests(unittest.TestCase):
    def test_deferred_boot_binds_real_buttons_after_admin_helpers(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.set_default_timeout(4000)
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                includes = ''.join(f'<script src="/static/{name}" defer></script>' for name in FEEDBACK_ASSETS)
                markup = '<!doctype html><html><head>' + includes + '</head><body><button id="nextBattle">Next</button><p id="message" role="status" aria-live="polite"></p>'
                markup += (ROOT / 'templates/admin/180_battle_action_modal.html').read_text(encoding='utf-8')
                markup += (ROOT / 'templates/admin/190_document_end.html').read_text(encoding='utf-8')
                admin = """
                    let latest = {active_campaign_id:'c',active_setup:{campaign_id:'c',name:'s'},battle_round:1,
                        statistics_token:'old',characters:[],lairs:[],monsters:[
                            {id:'a',active:true,in_turn:true},{id:'b',active:true,in_turn:false}]};
                    function observeFixtureState(state) {
                        const feedback = window.scryingAdminFeedback;
                        const sequence = feedback.stateRequest();
                        if (!feedback.observeState(state, sequence)) throw new Error('Invalid fixture encounter scope');
                        return state;
                    }
                    latest=observeFixtureState(latest);
                    let battleActionActorId='a', battleActionsApplying=false;
                    window.server=structuredClone(latest); window.nextPosts=0; window.opened=[];
                    function message(text,options){window.scryingAdminFeedback.deliver('global',text,options);}
                    function closeBattleActions(){document.querySelector('#battleActionModal').hidden=true;
                        document.querySelector('#battleActionRows').replaceChildren();battleActionActorId=null;}
                    function openBattleActions(id){window.opened.push(id);battleActionActorId=id;
                        document.querySelector('#battleActionModal').hidden=false;}
                    async function load(){latest=observeFixtureState(structuredClone(window.server));}
                    async function request(url,options={}){
                        if(url==='/api/state')return observeFixtureState(structuredClone(window.server));
                        if(url==='/api/battle/next' && options.method==='POST'){
                            window.nextPosts++;
                            window.server.monsters.forEach(x=>x.in_turn=x.id==='b');
                            window.server.statistics_token='new';
                            return {current:window.server.monsters[1]};
                        }
                        throw Error('Unexpected request '+url);
                    }
                    document.querySelector('#battleActionModal').hidden=false;
                """
                def route(request):
                    path = urlsplit(request.request.url).path
                    if path == '/':
                        request.fulfill(content_type='text/html', body=markup)
                    elif path == '/static/admin.js':
                        request.fulfill(content_type='text/javascript', body=admin)
                    elif path == '/static/battle-actions-next.js':
                        request.fulfill(content_type='text/javascript', body=(ROOT / 'static/battle-actions-next.js').read_text(encoding='utf-8'))
                    elif path in tuple('/static/' + name for name in FEEDBACK_ASSETS):
                        request.fulfill(content_type='text/javascript', body=(ROOT / path.lstrip('/')).read_text(encoding='utf-8'))
                    else:
                        request.fulfill(content_type='text/css' if path.endswith('.css') else 'text/javascript', body='')
                page.route('**/*', route)
                page.goto('http://fixture.test/', wait_until='load')
                self.assertEqual(errors, [], 'Controller must not initialize before request exists')
                self.assertTrue(page.evaluate('Boolean(window.scryingAdminFeedback && window.ScryingFeedback && window.ScryingFeedbackView)'))
                self.assertEqual(page.evaluate('scryingAdminFeedback.snapshot().length'), 0)
                self.assertTrue(page.locator('#nextBattleActions').evaluate('node => typeof node.onclick === "function"'))
                page.locator('#nextBattleActions').click()
                page.wait_for_function('window.opened.length === 1')
                self.assertEqual(page.evaluate('window.nextPosts'), 1)
                self.assertEqual(page.evaluate('window.opened'), ['b'])
                self.assertEqual(errors, [])
            finally:
                browser.close()

if __name__ == '__main__': unittest.main()
