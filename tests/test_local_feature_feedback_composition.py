# SG-TODO-009.7 Stage 3. Loaded Admin with intercepted HTTP, not live-server evidence.
import json
import unittest
import test_admin_global_feedback_composition as composed


class LocalFeatureFeedbackCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        composed.GlobalFeedbackCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        composed.GlobalFeedbackCompositionTests.tearDownClass.__func__(cls)

    open_page = composed.GlobalFeedbackCompositionTests.open_page
    records = composed.GlobalFeedbackCompositionTests.records

    def text(self, page, region):
        return page.locator(f'#{region} .sg-feedback-text').all_text_contents()

    def no_stage3_legacy(self, page):
        legacy = page.evaluate('scryingAdminFeedback.snapshot().filter(r=>String(r.operation).startsWith("legacy.")).map(r=>r.region)')
        for region in ('tools', 'lair', 'lairAction', 'campaignViewer'):
            self.assertNotIn(region, legacy)

    def test_regions_are_mounted_once_with_live_status_semantics(self):
        page, h = self.open_page()
        for node in ('featureFeedback', 'lairNotice', 'lairActionNotice', 'campaignViewerFeedback'):
            with self.subTest(node=node):
                self.assertEqual(page.get_attribute(f'#{node}', 'data-sg-feedback-mounted'), 'true')
                self.assertEqual(page.get_attribute(f'#{node}', 'role'), 'status')
                self.assertTrue(page.locator(f'#{node}').is_hidden())
        self.assertTrue(page.locator('#featureNotice').count() == 1)
        self.assertIsNone(page.get_attribute('#featureNotice', 'data-sg-feedback-mounted'))
        self.assertIsNone(page.get_attribute('#campaignViewerNotice', 'data-sg-feedback-mounted'))

    def test_tools_success_error_and_refresh_failure_use_tools_region(self):
        page, h = self.open_page()
        page.wait_for_function("document.querySelector('#featureTarget').value")
        target = page.locator('#featureTarget').input_value()
        path = f'/api/combatants/{target}/features'
        h['replies'][path] = (422, {'detail': 'Temporary HP rejected'})
        # Panes may be collapsed in the fixture viewport; set values as the input handlers would.
        page.eval_on_selector('#featureTempHp', "n => {n.value = '5'; n.dispatchEvent(new Event('input'));}")
        page.evaluate("() => document.querySelector('#setTempHp').onclick()")
        page.wait_for_function("scryingAdminFeedback.snapshot().some(x=>x.operation==='tools.temp-hp')")
        error = self.records(page, 'tools.temp-hp')[0]
        self.assertEqual((error['region'], error['severity']), ('tools', 'error'))
        self.assertEqual(self.text(page, 'featureFeedback'), ['Error: Temporary HP rejected'])
        self.assertEqual(page.locator('#featureTempHp').input_value(), '5', 'Draft survives a rejection')
        self.assertEqual(page.locator('#featureNotice').text_content(), '')
        h['replies'][path] = (200, {})
        page.evaluate("() => document.querySelector('#setTempHp').onclick()")
        page.wait_for_function("scryingAdminFeedback.snapshot().some(x=>x.operation==='tools.temp-hp'&&x.severity==='success')")
        self.assertEqual(self.text(page, 'featureFeedback'), ['Success: Saved.'])
        h['replies']['/api/features'] = (503, {'detail': 'Features unavailable'})
        page.evaluate("() => document.querySelector('#featureRefresh').onclick()")
        page.wait_for_function("scryingAdminFeedback.snapshot().some(x=>x.operation==='tools.refresh')")
        self.assertEqual(self.records(page, 'tools.refresh')[0]['text'], 'Features unavailable')
        del h['replies']['/api/features']
        page.evaluate("() => document.querySelector('#featureRefresh').onclick()")
        page.wait_for_function("!scryingAdminFeedback.snapshot().some(x=>x.operation==='tools.refresh')")
        self.assertEqual([w['path'] for w in h['writes']], [path, path])
        self.no_stage3_legacy(page)

    def test_lair_toggle_save_and_has_lair_feedback(self):
        page, h = self.open_page()
        h['state']['has_lair'] = True
        h['state']['lairs'] = [{'id': 'l', 'kind': 'lair', 'name': 'Lair', 'active': False, 'visible': False,
                                'in_turn': False, 'notes': '', 'color': '#8064a2'}]
        page.evaluate('() => load(true)')
        page.wait_for_function("document.querySelector('#lairJoinBattle').textContent==='Join Battle' && !document.querySelector('#lairJoinBattle').disabled")
        h['replies']['/api/lairs/l'] = (200, dict(h['state']['lairs'][0], active=True))
        page.evaluate("() => document.querySelector('#lairJoinBattle').onclick()")
        page.wait_for_function("scryingAdminFeedback.snapshot().some(x=>x.operation==='lair.toggle')")
        self.assertEqual(self.text(page, 'lairNotice'), ['Success: Lair updated.'])
        h['replies']['/api/lairs/l'] = (422, {'detail': 'Lair name rejected'})
        page.eval_on_selector('#lairName', "n => {n.value = 'Draft name'; n.dispatchEvent(new Event('input'));}")
        page.evaluate("() => document.querySelector('#lairConfigForm').onsubmit({preventDefault() {}})")
        page.wait_for_function("scryingAdminFeedback.snapshot().some(x=>x.operation==='lair.save')")
        self.assertEqual(self.records(page, 'lair.save')[0]['severity'], 'error')
        self.assertIn('Error: Lair name rejected', self.text(page, 'lairNotice'))
        self.assertEqual(page.locator('#lairName').input_value(), 'Draft name')
        h['replies']['/api/setups/has-lair'] = (409, {'detail': 'Setup changed'})
        page.evaluate("() => {const box = document.querySelector('#setupHasLair'); box.checked = false; box.dispatchEvent(new Event('change'));}")
        page.wait_for_function("scryingAdminFeedback.snapshot().some(x=>x.operation==='setup.has-lair')")
        self.assertIn('Error: Setup changed', self.text(page, 'battleSetupNotification'))
        page.wait_for_function("!document.querySelector('#setupHasLair').disabled")
        self.assertTrue(page.locator('#setupHasLair').is_checked(), 'Server state is restored')
        self.assertNotIn('battleSetup', page.evaluate('scryingAdminFeedback.snapshot().filter(r=>String(r.operation).startsWith("legacy.")).map(r=>r.region)'))
        self.no_stage3_legacy(page)

    def test_viewer_access_feedback_uses_selected_campaign_region(self):
        page, h = self.open_page()
        campaign = h['state']['active_campaign_id']
        path = f'/api/campaigns/{campaign}/viewers'
        h['replies'][path] = (200, {'campaign': {'id': campaign, 'name': 'Default'},
                                    'users': [{'id': '10', 'username': 'alice', 'granted': False}]})
        page.evaluate("() => {const d = document.querySelector('#campaignViewerAccess'); d.open = true;}")
        page.wait_for_function("document.querySelectorAll('#campaignViewerUsers input').length===1")
        page.eval_on_selector('#campaignViewerUsers input', 'n => {n.checked = true;}')
        page.evaluate("() => document.querySelector('#saveCampaignViewers').click()")
        page.wait_for_function("scryingAdminFeedback.snapshot().some(x=>x.operation==='viewer.save')")
        saved = self.records(page, 'viewer.save')[0]
        self.assertEqual((saved['lane'], saved['region'], saved['severity']), ('page', 'campaignViewer', 'success'))
        self.assertEqual(self.text(page, 'campaignViewerFeedback'), ['Success: Viewer access saved.'])
        self.assertEqual(page.locator('#campaignViewerNotice').text_content(), '')
        self.assertEqual(json.loads(h['writes'][-1]['body']), {'user_ids': ['10']})
        self.no_stage3_legacy(page)


if __name__ == '__main__':
    unittest.main()
