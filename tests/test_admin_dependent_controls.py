"""Independent native panel controls with real controller/CSS excerpts in Chromium."""
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from python.scrying_glass_admin_source import read_admin_script

ROOT=Path(__file__).resolve().parents[1]
PAIRS=[('toggleCampaignPane','campaignInputPane'),('toggleCharacterPane','characterInputPane'),
       ('toggleBattleSetupPane','battleSetupInputPane'),('toggleMonsterPane','monsterInputPane'),
       ('toggleLairPane','lairTools'),('toggleCharacterDisplayPane','characterDisplayPane'),
       ('toggleMonsterDisplayPane','monsterDisplayPane')]


class DependentControlTests(unittest.TestCase):
    def setUp(self):
        p=sync_playwright().start();self.addCleanup(p.stop)
        browser=p.chromium.launch(headless=True);self.addCleanup(browser.close)
        self.page=browser.new_page()
        buttons=''.join(f'<button id="{b}" aria-expanded="true">Hide</button>' for b,_ in PAIRS)
        panes=''.join(f'<section id="{n}" class="pane">Input</section>' for _,n in PAIRS)
        self.page.set_content('<body class="admin-shell"><header id="adminHeader"><div id="adminButtonBar">'+buttons+'</div></header><main id="adminScroll">'+panes+'</main></body>')
        self.page.add_style_tag(path=str(ROOT/'static/admin-shell.css'))
        source=read_admin_script(ROOT/'static').decode('utf-8')
        start=source.index('const hideablePanes =')
        end=source.index("document.querySelector('#editForm').onsubmit",start)
        self.page.add_script_tag(content="let latest={battle_order:[]};window.scryingLairsRender=()=>{};\n"+source[start:end])
        self.page.add_script_tag(path=str(ROOT/'static/admin-initial-visibility.js'))

    def states(self):
        return self.page.evaluate("Object.fromEntries([...document.querySelectorAll('.pane')].map(n=>[n.id,n.hidden]))")

    def assert_buttons_visible(self):
        for button,_ in PAIRS:
            self.assertTrue(self.page.locator('#'+button).is_visible(),button)

    def test_each_button_only_changes_its_own_panel(self):
        for button,pane in PAIRS:
            before=self.states();self.page.locator('#'+button).click();after=self.states()
            self.assertEqual(after[pane],not before[pane])
            for other in before:
                if other!=pane:self.assertEqual(after[other],before[other])
            self.assert_buttons_visible()

    def test_hidden_parent_never_hides_child_or_child_button(self):
        for parent,child,parent_pane,child_pane in [
            ('toggleCampaignPane','toggleCharacterPane','campaignInputPane','characterInputPane'),
            ('toggleBattleSetupPane','toggleMonsterPane','battleSetupInputPane','monsterInputPane')]:
            self.page.locator('#'+parent).click()
            self.assertFalse(self.page.locator('#'+child_pane).evaluate('n=>n.hidden'))
            self.page.locator('#'+child).click()
            self.assertTrue(self.page.locator('#'+parent_pane).evaluate('n=>n.hidden'))
            self.page.locator('#'+parent).click()
            self.assertTrue(self.page.locator('#'+child_pane).evaluate('n=>n.hidden'))
            self.assert_buttons_visible()

    def test_battle_collapses_once_and_manual_reopen_survives_refresh(self):
        self.page.evaluate("latest.battle_order=['actor'];updatePaneVisibilityForBattle()")
        self.assertTrue(all(self.states().values()));self.assert_buttons_visible()
        self.page.locator('#toggleCharacterPane').click()
        self.page.evaluate('updatePaneVisibilityForBattle()')
        self.assertFalse(self.states()['characterInputPane'])
        self.assertTrue(self.states()['campaignInputPane'])
        self.assert_buttons_visible()
        self.page.evaluate('latest.battle_order=[];updatePaneVisibilityForBattle()')
        self.assertFalse(any(self.states().values()))

    def test_initial_saved_context_collapses_inputs_not_controls(self):
        self.page.evaluate("latest.active_campaign_id='campaign';latest.active_setup={campaign_id:'campaign',name:'saved'};scryingLairsRender(latest)")
        for _,pane in PAIRS[:5]:self.assertTrue(self.states()[pane])
        self.assert_buttons_visible()
        self.page.locator('#toggleCharacterPane').click()
        self.page.add_script_tag(path=str(ROOT/'static/admin-initial-visibility.js'))
        self.page.evaluate('scryingLairsRender(latest)')
        self.assertFalse(self.states()['characterInputPane'])
        self.assertTrue(self.states()['campaignInputPane'])

    def test_explicit_lair_gate_is_not_overridden_by_setup_toggle(self):
        self.page.locator('#toggleLairPane').evaluate('n=>n.hidden=true')
        self.page.locator('#toggleBattleSetupPane').click()
        self.page.locator('#toggleBattleSetupPane').click()
        self.assertFalse(self.page.locator('#toggleLairPane').is_visible())
        self.assertTrue(self.page.locator('#toggleMonsterPane').is_visible())


if __name__=='__main__':unittest.main()
