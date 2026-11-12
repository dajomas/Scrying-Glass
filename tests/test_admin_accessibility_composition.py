# SG-TODO-009.7 Stage 4. Loaded Admin with intercepted HTTP, not live-server evidence.
# Integration reconciliation and accessibility hardening: document language, the
# main landmark, legacy dialog semantics/keyboard containment, nested overlays,
# retired untyped feedback, typed campaign-list feedback and named confirmations.
import unittest
import test_admin_global_feedback_composition as composed

LEGACY_MODALS = ('lairActionModal', 'tieModal', 'editModal', 'importModal', 'monsterFileHelpModal',
                 'campaignModal', 'campaignSetupModal', 'campaignDeleteModal', 'csvImportModal',
                 'battleActionModal', 'statisticsModal')

OPEN = """id => { const m = document.getElementById(id); m.hidden = false; }"""
CLOSE = """id => { document.getElementById(id).hidden = true; }"""


class AdminAccessibilityCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        composed.GlobalFeedbackCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        composed.GlobalFeedbackCompositionTests.tearDownClass.__func__(cls)

    open_page = composed.GlobalFeedbackCompositionTests.open_page
    records = composed.GlobalFeedbackCompositionTests.records

    def active_id(self, page):
        return page.evaluate('document.activeElement && document.activeElement.id')

    def test_document_language_and_single_main_landmark(self):
        page, _ = self.open_page()
        self.assertEqual(page.get_attribute('html', 'lang'), 'en')
        landmarks = page.evaluate("""() => [...document.querySelectorAll('main,[role=main]')].map(n => [n.id, n.getAttribute('role')])""")
        self.assertEqual(landmarks, [['adminScroll', None]], 'main keeps its implicit landmark role')
        labelled = page.get_attribute('#adminScroll', 'aria-labelledby')
        self.assertEqual(page.get_attribute(f'#{labelled}', 'aria-selected'), 'true')
        self.assertEqual(page.get_attribute(f'#{labelled}', 'aria-controls'), 'adminScroll')

    def test_every_legacy_overlay_is_a_named_modal_dialog(self):
        page, _ = self.open_page()
        for modal in LEGACY_MODALS:
            with self.subTest(modal=modal):
                info = page.evaluate("""id => { const m = document.getElementById(id);
                    const d = m.getAttribute('role') === 'dialog' ? m : m.querySelector('[role=dialog]');
                    const label = d && document.getElementById(d.getAttribute('aria-labelledby'));
                    return d && {modal: d.getAttribute('aria-modal'), name: label && label.textContent.trim(),
                        heading: !!(label && /^H[1-3]$/.test(label.tagName))}; }""", modal)
                self.assertIsNotNone(info)
                self.assertEqual(info['modal'], 'true')
                self.assertTrue(info['name'])
        # The Encounter tools dialog keeps its own owner and semantics.
        self.assertEqual(page.get_attribute('#encounterToolsModal', 'aria-labelledby'), 'encounterToolsTitle')

    def test_focus_moves_in_is_contained_and_returns_with_escape(self):
        page, _ = self.open_page()
        page.eval_on_selector('#startBattle', 'n => n.focus()')
        page.evaluate(OPEN, 'tieModal')
        page.wait_for_function("document.getElementById('tieModal').contains(document.activeElement)")
        ids = page.evaluate("""() => [...document.querySelectorAll('#tieModal button')].filter(b => b.getClientRects().length).map(b => b.id)""")
        self.assertEqual(ids[-2:], ['confirmOrder', 'cancelOrder'])
        page.eval_on_selector('#cancelOrder', 'n => n.focus()')
        page.keyboard.press('Tab')
        self.assertTrue(page.evaluate("document.getElementById('tieModal').contains(document.activeElement)"))
        self.assertNotEqual(self.active_id(page), 'cancelOrder')
        page.keyboard.press('Shift+Tab')
        self.assertEqual(self.active_id(page), 'cancelOrder')
        page.keyboard.press('Escape')
        self.assertTrue(page.locator('#tieModal').is_hidden())
        self.assertEqual(self.active_id(page), 'startBattle', 'focus returns to the opener')

    def test_opener_placed_focus_is_kept_and_close_does_not_steal_focus(self):
        page, _ = self.open_page()
        page.eval_on_selector('#newCampaign', 'n => n.focus()')
        page.evaluate('() => openCampaignModal()')
        self.assertEqual(page.evaluate("document.activeElement.name"), 'name', 'the existing first-field focus is kept')
        # Focus deliberately moved elsewhere before closing is not stolen back.
        page.eval_on_selector('#startBattle', 'n => n.focus()')
        page.evaluate('() => closeCampaignModal()')
        self.assertEqual(self.active_id(page), 'startBattle')

    def test_nested_overlay_over_tools_dialog_closes_alone_and_returns_inside(self):
        page, _ = self.open_page()
        page.evaluate("() => document.getElementById('adminWorkflow-live').click()")
        page.evaluate("() => document.getElementById('toggleEncounterTools').click()")
        page.wait_for_function("!document.getElementById('encounterToolsModal').hidden")
        page.eval_on_selector('#featureRefresh', 'n => n.focus()')
        # A body-level overlay above the tools dialog (the tools owner yields to it).
        page.evaluate(OPEN, 'tieModal')
        page.wait_for_function("document.getElementById('tieModal').contains(document.activeElement)")
        page.eval_on_selector('#cancelOrder', 'n => n.focus()')
        page.keyboard.press('Tab')
        self.assertTrue(page.evaluate("document.getElementById('tieModal').contains(document.activeElement)"),
                        'Tab stays in the topmost overlay, not the tools dialog beneath it')
        page.keyboard.press('Escape')
        self.assertTrue(page.locator('#tieModal').is_hidden())
        self.assertFalse(page.evaluate("document.getElementById('encounterToolsModal').hidden"),
                         'Escape closes only the topmost overlay')
        self.assertEqual(self.active_id(page), 'featureRefresh')
        page.keyboard.press('Escape')
        self.assertTrue(page.evaluate("document.getElementById('encounterToolsModal').hidden"))
        # An earlier-owner Escape (040 closeEdit) over the tools dialog also closes only that overlay.
        page.evaluate("() => document.getElementById('toggleEncounterTools').click()")
        page.wait_for_function("!document.getElementById('encounterToolsModal').hidden")
        page.eval_on_selector('#featureRefresh', 'n => n.focus()')
        page.evaluate(OPEN, 'editModal')
        page.keyboard.press('Escape')
        self.assertTrue(page.locator('#editModal').is_hidden())
        self.assertFalse(page.evaluate("document.getElementById('encounterToolsModal').hidden"))
        self.assertEqual(self.active_id(page), 'featureRefresh')

    def test_untyped_feedback_is_retired_for_every_region(self):
        page, _ = self.open_page()
        result = page.evaluate("""() => ['global', 'campaign', 'battleSetup', 'monsters', 'characters', 'tools', 'lair']
            .map(region => { try { scryingAdminFeedback.deliver(region, 'Untyped'); return 'accepted'; }
                             catch (error) { return error.message; } })""")
        self.assertTrue(all(text.startswith('Feedback requires an explicit ticket and severity') for text in result), result)
        self.assertIsNone(page.evaluate('scryingAdminFeedback.legacyRegions'))
        self.assertEqual(page.evaluate("scryingAdminFeedback.snapshot().filter(r => String(r.operation).startsWith('legacy.')).length"), 0)

    def test_campaign_list_load_error_persists_and_moved_notice_is_typed(self):
        page, h = self.open_page()
        h['replies']['/api/campaigns'] = (503, {'detail': 'Campaign list unavailable'})
        page.evaluate('() => setups()')
        page.wait_for_function("scryingAdminFeedback.snapshot().some(r => r.operation === 'campaign.setups.load')")
        error = self.records(page, 'campaign.setups.load')[0]
        self.assertEqual((error['lane'], error['region'], error['severity']), ('page', 'campaign', 'error'))
        self.assertEqual(self.records(page, 'campaign.setups.load')[0]['text'], 'Campaign list unavailable')
        listing = page.evaluate('() => structuredClone(campaignData)')
        listing['moved'] = ['old-a', 'old-b']
        h['replies']['/api/campaigns'] = (200, listing)
        page.evaluate('() => setups()')
        page.wait_for_function("!scryingAdminFeedback.snapshot().some(r => r.operation === 'campaign.setups.load')")
        moved = self.records(page, 'campaign.setups.moved')
        self.assertEqual([(r['lane'], r['region'], r['severity'], r['text']) for r in moved],
                         [('page', 'campaign', 'info', 'Moved 2 unassigned setup(s) into campaign Default: old-a, old-b')])
        self.assertIn('Information: Moved 2 unassigned setup(s)', page.locator('#campaignNotification').text_content())

    def test_destructive_confirmations_name_their_scope_and_cancel_silently(self):
        page, h = self.open_page()
        page.evaluate("() => { window.__prompts = []; window.confirm = text => { window.__prompts.push(text); return false; }; }")
        before = page.evaluate('() => scryingAdminFeedback.snapshot().length')
        page.evaluate("() => document.getElementById('resetAll').onclick()")
        page.evaluate("""() => { const select = document.getElementById('featureLifeState'); select.value = 'dead';
            return document.getElementById('setLifeState').onclick(); }""")
        prompts = page.evaluate('window.__prompts')
        setup = page.evaluate("() => typeof latest.active_setup === 'string' ? latest.active_setup : latest.active_setup?.name")
        target = page.evaluate("() => document.getElementById('featureTarget').selectedOptions[0]?.textContent || ''")
        self.assertEqual(len(prompts), 2, prompts)
        self.assertIn(f'battle setup “{setup}”' if setup else 'the current battle setup', prompts[0])
        self.assertRegex(prompts[0], r'\(\d+ monster\(s\), \d+ character\(s\)\)')
        self.assertTrue(prompts[1].startswith('Mark “'), prompts[1])
        self.assertIn(prompts[1][len('Mark “'):].split('”')[0], target)
        self.assertEqual(h['writes'], [], 'cancelled confirmations make no request')
        self.assertEqual(page.evaluate('() => scryingAdminFeedback.snapshot().length'), before, 'and publish nothing')

    def test_lair_and_checkpoint_removals_name_their_target(self):
        page, h = self.open_page()
        h['state']['has_lair'] = True
        h['state']['lairs'] = [{'id': 'l', 'kind': 'lair', 'name': 'Sunken Crypt', 'active': False, 'visible': False,
                                'in_turn': False, 'notes': '', 'color': '#8064a2'}]
        page.evaluate('() => load(true)')
        page.wait_for_function("!document.getElementById('removeLair').hidden")
        page.evaluate("""() => { window.__prompts = []; window.confirm = text => { window.__prompts.push(text); return false; };
            const select = document.getElementById('checkpointSelect');
            select.innerHTML = '<option value="cp1">Before the dragon — 1/1/2026</option>'; select.value = 'cp1'; }""")
        page.evaluate("() => document.getElementById('removeLair').onclick()")
        page.evaluate("() => document.getElementById('deleteCheckpoint').onclick()")
        page.wait_for_function('window.__prompts.length === 2')
        prompts = page.evaluate('window.__prompts')
        self.assertTrue(prompts[0].startswith('Remove lair “Sunken Crypt”?'), prompts[0])
        self.assertEqual(prompts[1], 'Permanently delete checkpoint “Before the dragon — 1/1/2026”?')
        self.assertEqual(h['writes'], [])


if __name__ == '__main__':
    unittest.main()
