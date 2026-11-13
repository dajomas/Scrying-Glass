"""Native Chromium/full candidate asset with real feedback dependencies; mocked transport."""
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from feedback_browser_fixture import install_feedback

ROOT = Path(__file__).resolve().parents[1]


class CandidatePendingFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.playwright = sync_playwright().start()
        self.addCleanup(self.playwright.stop)
        self.browser = self.playwright.chromium.launch(headless=True)
        self.addCleanup(self.browser.close)
        self.page = self.browser.new_page(viewport={"width": 375, "height": 900})
        self.page.set_default_timeout(4000)
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.set_content("""
          <form id="monsterForm"><input id="monsterSpecies" name="monster_species" value="Goblin">
          <input id="monsterInitiativeBonus" name="initiative_bonus">
          <p id="monsterInitiativeBonusHelp"></p><button>Add</button></form>
          <input id="monsterSpeciesLookupOverwrite" type="checkbox">
          <div id="monsterAddNotification"></div>""")
        install_feedback(self.page)
        self.page.add_script_tag(content="""
          let monsterSpeciesLookupRequest = 1;
          window.waiters = []; window.sent = []; window.submissions = 0;
          document.querySelector('#monsterForm').onsubmit = event => {
            event.preventDefault(); window.submissions++;
          };
          function monsterSourceLabel(candidate) { return candidate.provider + ' / ' + candidate.source; }
          async function request(url, options = {}) {
            window.sent.push({url, options});
            return new Promise((resolve, reject) => window.waiters.push({resolve, reject}));
          }
          window.scope = name => {
            const feedback = window.scryingAdminFeedback;
            const sequence = feedback.stateRequest();
            return feedback.observeState({active_campaign_id: name,
              active_setup: {campaign_id: name, name: 'setup'}}, sequence);
          };
          window.scope('campaign-a');
          window.startLookup = () => {
            window.lookup = request('/api/dndbeyond/monster-stats?species=Goblin');
            window.lookup.catch(() => {});
          };
        """)
        self.page.add_script_tag(content=(ROOT / "static/monster-candidate-selection.js").read_text(encoding="utf-8"))

    def submit(self):
        self.page.evaluate("document.querySelector('#monsterForm').dispatchEvent(new Event('submit', {bubbles:true, cancelable:true}))")

    def records(self):
        return self.page.evaluate("window.scryingAdminFeedback.snapshot()")

    def begin(self):
        self.page.evaluate("window.startLookup()")

    def finish_empty(self, index=0):
        self.page.evaluate("index => waiters[index].resolve({status:'ok',candidates:[]})", index)
        self.page.evaluate("window.lookup")

    def candidate(self, name="Goblin", bonus=4):
        return {"found": True, "species": "Goblin", "name": name, "provider": "5e.tools", "source": "MM",
                "ac": 12, "hp": "7", "selection_token": name + "-selection", "initiative_bonus": bonus,
                "initiative_bonus_status": "available", "initiative_bonus_offer_token": name + "-offer"}

    def test_pending_capture_prevents_creation_and_renders_persistent_error(self):
        self.begin()
        self.submit()
        self.assertEqual(self.page.evaluate("submissions"), 0)
        self.assertEqual(self.records()[0]["severity"], "error")
        self.assertEqual(self.records()[0]["operation"], "monster.lookup.pending-submit")
        self.assertEqual(self.page.locator('#monsterAddNotification [data-severity="error"]').count(), 1)
        self.page.wait_for_timeout(3100)
        self.assertEqual(len(self.records()), 1)
        self.finish_empty()
        self.assertEqual(self.records(), [])
        self.submit()
        self.assertEqual(self.page.evaluate("submissions"), 1)
        self.assertEqual(self.errors, [])

    def test_matching_settlement_preserves_independent_error_node(self):
        self.page.evaluate("""const f=window.scryingAdminFeedback;
          f.publish(f.begin({region:'monsters',operation:'independent',target:'m',label:'Independent'}),
          {severity:'error',text:'Keep this error'});
          window.keptNode=document.querySelector('[data-severity="error"]');""")
        self.begin()
        self.submit()
        self.finish_empty()
        self.assertEqual([r["operation"] for r in self.records()], ["independent"])
        self.assertTrue(self.page.evaluate("keptNode === document.querySelector('[data-severity=error]')"))

    def test_real_popup_cancel_settles_blocker_and_returns_focus(self):
        self.page.locator('#monsterSpecies').focus()
        self.begin()
        self.page.evaluate("items => waiters[0].resolve({status:'ok',candidates:items})", [self.candidate(), self.candidate("Other")])
        self.page.get_by_role("dialog", name="Select monster candidate", exact=True).wait_for()
        self.submit()
        self.page.keyboard.press("Escape")
        self.page.evaluate("window.lookup")
        self.assertEqual(self.records(), [])
        self.assertEqual(self.page.locator("dialog").count(), 0)
        self.assertEqual(self.page.evaluate("new FormData(document.querySelector('#monsterForm')).get('selection_token')"), "manual")
        self.assertTrue(self.page.locator('#monsterSpecies').evaluate("node => node === document.activeElement"))
        self.assertEqual(self.errors, [])

    def test_sole_candidate_keeps_signed_selection_and_offer_binding(self):
        self.begin()
        self.submit()
        self.page.evaluate("candidate => waiters[0].resolve({status:'ok',candidates:[candidate]})", self.candidate())
        self.page.evaluate("window.lookup")
        fields = self.page.evaluate("Object.fromEntries(new FormData(document.querySelector('#monsterForm')))")
        self.assertEqual(fields["selection_token"], "Goblin-selection")
        self.assertEqual(fields["initiative_bonus_offer_token"], "Goblin-offer")
        self.assertEqual(fields["initiative_bonus"], "4")
        self.assertEqual(self.records(), [])

    def test_transport_rejection_settles_pending_without_replaying(self):
        self.begin()
        self.submit()
        self.page.evaluate("waiters[0].reject(new Error('Offline'))")
        with self.assertRaisesRegex(Exception, "Offline"):
            self.page.evaluate("window.lookup")
        self.assertEqual(self.records(), [])
        self.assertEqual(self.page.evaluate("sent.length"), 1)
        self.submit()
        self.assertEqual(self.page.evaluate("submissions"), 1)

    def test_old_lookup_cannot_apply_bonus_or_source_after_scope_transition(self):
        self.begin()
        self.submit()
        self.assertTrue(self.page.evaluate("scope('campaign-b')"))
        self.page.evaluate("candidate => waiters[0].resolve({status:'ok',candidates:[candidate]})", self.candidate())
        self.assertFalse(self.page.evaluate("window.lookup")["found"])
        self.assertEqual(self.page.locator('#monsterInitiativeBonus').input_value(), "")
        self.assertEqual(self.page.evaluate("new FormData(document.querySelector('#monsterForm')).get('selection_token')"), "manual")
        self.assertEqual(self.records(), [])

    def test_overlapping_lookups_keep_blocker_until_both_settle(self):
        self.begin()
        self.page.evaluate("window.firstLookup = window.lookup; void 0")
        self.begin()
        self.submit()
        self.finish_empty(1)
        self.assertEqual(len(self.records()), 1)
        self.page.evaluate("waiters[0].resolve({status:'ok',candidates:[]})")
        self.page.evaluate("window.firstLookup")
        self.assertEqual(self.records(), [])
        self.assertEqual(self.page.evaluate("sent.length"), 2)

    def test_manual_bonus_edit_clears_signed_offer_without_clearing_selection(self):
        self.begin()
        self.page.evaluate("candidate => waiters[0].resolve({status:'ok',candidates:[candidate]})", self.candidate())
        self.page.evaluate("window.lookup")
        self.page.locator('#monsterInitiativeBonus').fill('9')
        fields = self.page.evaluate("Object.fromEntries(new FormData(document.querySelector('#monsterForm')))")
        self.assertEqual(fields["selection_token"], "Goblin-selection")
        self.assertNotIn("initiative_bonus_offer_token", fields)
        self.assertEqual(fields["initiative_bonus"], "9")


if __name__ == "__main__":
    unittest.main(verbosity=2)
