"""Real pane-controller/CSS Chromium fixtures; no authenticated live transport."""
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from python.scrying_glass_admin_source import read_admin_script

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ("toggleCampaignPane", "campaignInputPane"),
    ("toggleCharacterPane", "characterInputPane"),
    ("toggleBattleSetupPane", "battleSetupInputPane"),
    ("toggleMonsterPane", "monsterInputPane"),
    ("toggleLairPane", "lairTools"),
    ("toggleCharacterDisplayPane", "characterDisplayPane"),
    ("toggleMonsterDisplayPane", "monsterDisplayPane"),
]
GROUPS = [("toggleCampaignPane", "toggleCharacterPane", "campaignInputPane", "characterInputPane"),
          ("toggleBattleSetupPane", "toggleMonsterPane", "battleSetupInputPane", "monsterInputPane")]


class DependentControlTests(unittest.TestCase):
    def setUp(self):
        playwright = sync_playwright().start()
        self.addCleanup(playwright.stop)
        browser = playwright.chromium.launch(headless=True)
        self.addCleanup(browser.close)
        self.page = browser.new_page()
        buttons = "".join(f'<button id="{button}" aria-expanded="true">Hide</button>' for button, _ in PAIRS)
        panes = "".join(f'<section id="{pane}" class="pane">Input</section>' for _, pane in PAIRS)
        self.page.set_content('<body class="admin-shell"><header id="adminHeader"><section id="adminButtonBar">' +
                              buttons + '</section></header><main id="adminScroll">' + panes + '</main></body>')
        self.page.add_style_tag(path=str(ROOT / "static/admin-shell.css"))
        source = read_admin_script(ROOT / "static").decode("utf-8")
        start = source.index("const hideablePanes =")
        end = source.index("document.querySelector('#editForm').onsubmit", start)
        self.page.add_script_tag(content="let latest = {battle_order: []}; window.scryingLairsRender = () => {};\n" + source[start:end])

    def assert_dependent_buttons_hidden(self):
        for parent, child, pane, _ in GROUPS:
            self.assertTrue(self.page.locator('#' + pane).evaluate('node => node.hidden'))
            self.assertFalse(self.page.locator('#' + child).is_visible(), child)
            self.assertEqual(self.page.locator('#' + child).evaluate('node => getComputedStyle(node).display'), 'none')
            self.assertTrue(self.page.locator('#' + parent).is_visible(), parent)
        for button in ['toggleCharacterDisplayPane', 'toggleMonsterDisplayPane']:
            self.assertTrue(self.page.locator('#' + button).is_visible())

    def test_manual_hide_and_reopen_preserve_visible_children(self):
        for parent, child, pane, child_pane in GROUPS:
            self.page.locator('#' + parent).click()
            self.assertFalse(self.page.locator('#' + child).is_visible())
            self.page.locator('#' + parent).click()
            self.assertTrue(self.page.locator('#' + child).is_visible())
            self.assertFalse(self.page.locator('#' + child_pane).evaluate('node => node.hidden'))

    def test_independent_child_preferences_survive_parent_cycle(self):
        for parent, child, pane, child_pane in GROUPS:
            self.page.locator('#' + child).click()
            self.page.locator('#' + parent).click()
            self.assertFalse(self.page.locator('#' + child).is_visible())
            self.page.locator('#' + parent).click()
            self.assertTrue(self.page.locator('#' + child).is_visible())
            self.assertTrue(self.page.locator('#' + child_pane).evaluate('node => node.hidden'))
            self.assertEqual(self.page.locator('#' + child).get_attribute('aria-expanded'), 'false')

    def test_battle_collapse_and_repeated_refresh(self):
        self.page.evaluate("latest.battle_order = ['actor']; updatePaneVisibilityForBattle();")
        self.assert_dependent_buttons_hidden()
        self.page.evaluate('updatePaneVisibilityForBattle()')
        self.assert_dependent_buttons_hidden()
        for parent, child, _, _ in GROUPS:
            self.page.locator('#' + parent).click()
            self.assertTrue(self.page.locator('#' + child).is_visible())
        self.page.evaluate('updatePaneVisibilityForBattle()')
        for _, child, _, _ in GROUPS:
            self.assertTrue(self.page.locator('#' + child).is_visible())
        self.page.evaluate('latest.battle_order = []; updatePaneVisibilityForBattle();')
        for parent, child, _, _ in GROUPS:
            self.assertTrue(self.page.locator('#' + parent).is_visible())
            self.assertTrue(self.page.locator('#' + child).is_visible())

    def test_initialization_followed_by_global_collapse(self):
        self.page.evaluate("latest.active_campaign_id = 'campaign'; latest.active_setup = {campaign_id: 'campaign', name: 'saved'};")
        self.page.add_script_tag(path=str(ROOT / 'static/admin-initial-visibility.js'))
        self.assert_dependent_buttons_hidden()
        self.page.evaluate('setAllHideablePanesHidden(true)')
        self.assert_dependent_buttons_hidden()
        self.page.evaluate('setAllHideablePanesHidden(false)')
        for parent, child, _, _ in GROUPS:
            self.assertTrue(self.page.locator('#' + parent).is_visible())
            self.assertTrue(self.page.locator('#' + child).is_visible())

    def test_parent_hidden_state_alone_controls_availability(self):
        for parent, child, pane, _ in GROUPS:
            self.page.locator('#' + pane).evaluate('node => node.hidden = true')
            self.assertFalse(self.page.locator('#' + child).is_visible())
            self.page.locator('#' + pane).evaluate('node => node.hidden = false')
            self.assertTrue(self.page.locator('#' + child).is_visible())
        self.page.locator('#toggleLairPane').evaluate('node => node.hidden = true')
        self.page.locator('#toggleBattleSetupPane').click()
        self.page.locator('#toggleBattleSetupPane').click()
        self.assertFalse(self.page.locator('#toggleLairPane').is_visible())


if __name__ == '__main__':
    unittest.main()
