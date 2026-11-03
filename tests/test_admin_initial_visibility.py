"""Chromium fixtures for one-shot initial visibility; transport/state are mocked."""
from pathlib import Path
import json
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ('toggleCampaignPane', 'campaignInputPane'),
    ('toggleCharacterPane', 'characterInputPane'),
    ('toggleBattleSetupPane', 'battleSetupInputPane'),
    ('toggleMonsterPane', 'monsterInputPane'),
    ('toggleLairPane', 'lairTools'),
]

def state(campaign=True, setup=True):
    return {'active_campaign_id': 'campaign' if campaign else None,
            'active_setup': {'campaign_id': 'campaign', 'name': 'saved'} if setup else None}

class InitialVisibilityTests(unittest.TestCase):
    def setUp(self):
        self.p = sync_playwright().start()
        self.addCleanup(self.p.stop)
        browser = self.p.chromium.launch(headless=True)
        self.addCleanup(browser.close)
        self.browser = browser
        self.errors = []
        self.reset_page()

    def reset_page(self):
        if hasattr(self, 'page'):
            self.page.close()
        self.page = self.browser.new_page()
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        html = ''.join(f'<button id="{button}" aria-expanded="true">Hide</button><section id="{pane}"></section>' for button,pane in PAIRS)
        html += '<section id="characterDisplayPane"></section><section id="monsterDisplayPane"></section><section id="battleControls"></section><section id="activityLog"></section>'
        self.page.set_content(html)
        self.page.add_script_tag(content="""
            let latest;
            window.renderCalls = 0;
            window.scryingLairsRender = function(snapshot) {window.renderCalls++; return 'render-result';};
            const pairs = """ + json.dumps(PAIRS) + """;
            const hidden = {};
            window.toggleCalls = {};
            for (const [id,pane] of pairs) {
                hidden[id] = false;
                document.getElementById(id).onclick = () => {
                    hidden[id] = !hidden[id];
                    window.toggleCalls[id] = (window.toggleCalls[id] || 0) + 1;
                    document.getElementById(pane).hidden = hidden[id];
                    document.getElementById(id).setAttribute('aria-expanded', String(!hidden[id]));
                    document.getElementById(id).textContent = hidden[id] ? 'Show' : 'Hide';
                };
            }
        """)

    def install(self):
        self.page.add_script_tag(content=(ROOT / 'static/admin-initial-visibility.js').read_text(encoding='utf-8'))

    def update(self, value):
        result = self.page.evaluate('(snapshot) => {latest=snapshot;return window.scryingLairsRender(snapshot);}', value)
        self.assertEqual(result, 'render-result')

    def assert_visibility(self, campaign, setup):
        for index,(button,pane) in enumerate(PAIRS):
            expected = campaign if index < 2 else setup
            self.assertEqual(self.page.locator('#'+pane).evaluate('node => node.hidden'), expected)
            self.assertEqual(self.page.locator('#'+button).get_attribute('aria-expanded'), str(not expected).lower())
            self.assertEqual(self.page.locator('#'+button).inner_text(), 'Show' if expected else 'Hide')
        for pane in ['characterDisplayPane','monsterDisplayPane','battleControls','activityLog']:
            self.assertFalse(self.page.locator('#'+pane).evaluate('node => node.hidden'))
        self.assertEqual(self.errors, [])

    def test_all_four_initial_combinations(self):
        for campaign,setup in [(False,False),(True,False),(False,True),(True,True)]:
            with self.subTest(campaign=campaign,setup=setup):
                self.reset_page()
                self.install()
                self.update(state(campaign,setup))
                self.assert_visibility(campaign,setup)

    def test_cached_latest_is_used(self):
        self.page.evaluate('(value) => {latest=value;}', state())
        self.install()
        self.assert_visibility(True,True)
        self.assertEqual(self.page.evaluate('window.renderCalls'), 0)

    def test_invalid_or_incomplete_state_waits_for_authoritative_state(self):
        self.install()
        for value in [None, {}, {'active_campaign_id':'campaign'},
                      {'active_campaign_id':'campaign','active_setup':{'name':'unsaved'}},
                      {'active_campaign_id':False,'active_setup':None}]:
            self.update(value)
            self.assert_visibility(False,False)
        self.update(state())
        self.assert_visibility(True,True)

    def test_manual_choices_survive_updates_and_scope_changes(self):
        self.install()
        self.update(state())
        self.page.locator('#toggleCampaignPane').click()
        self.page.locator('#toggleMonsterPane').click()
        before = self.page.evaluate('JSON.stringify(window.toggleCalls)')
        self.update(state(False,False))
        self.update({'active_campaign_id':'other','active_setup':{'campaign_id':'other','name':'other'}})
        self.assertEqual(self.page.evaluate('JSON.stringify(window.toggleCalls)'), before)
        self.assertFalse(self.page.locator('#campaignInputPane').evaluate('node => node.hidden'))
        self.assertFalse(self.page.locator('#monsterInputPane').evaluate('node => node.hidden'))

    def test_interaction_before_initial_response_is_respected(self):
        self.install()
        self.page.locator('#toggleCampaignPane').click()
        self.page.locator('#toggleCampaignPane').click()
        self.update(state())
        self.assertFalse(self.page.locator('#campaignInputPane').evaluate('node => node.hidden'))
        self.assertTrue(self.page.locator('#characterInputPane').evaluate('node => node.hidden'))

    def test_hidden_lair_toggle_and_already_collapsed_pane(self):
        self.install()
        self.page.locator('#toggleLairPane').evaluate('node => node.hidden=true')
        self.page.locator('#toggleBattleSetupPane').click()
        self.update(state())
        self.assert_visibility(True,True)
        self.assertEqual(self.page.evaluate('window.toggleCalls.toggleBattleSetupPane'), 1)

    def test_no_active_initial_state_does_not_collapse_later(self):
        self.install()
        self.update(state(False,False))
        self.update(state())
        self.assert_visibility(False,False)

    def test_duplicate_asset_evaluation_is_harmless(self):
        self.install()
        self.install()
        self.update(state())
        self.assert_visibility(True,True)
        self.assertEqual(self.page.evaluate('window.renderCalls'), 1)
        self.assertEqual(self.page.evaluate('Object.values(window.toggleCalls)'), [1,1,1,1,1])

if __name__ == '__main__':
    unittest.main()
