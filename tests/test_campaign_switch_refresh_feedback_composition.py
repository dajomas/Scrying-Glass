# Complete Admin with intercepted HTTP; no authenticated live-server claim.
import unittest
import test_campaign_switch_request_feedback_composition as fixtures


class SwitchRefreshCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.SwitchRequestCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        fixtures.SwitchRequestCompositionTests.tearDownClass.__func__(cls)

    open_page = fixtures.SwitchRequestCompositionTests.open_page
    records = fixtures.SwitchRequestCompositionTests.records
    prepare = fixtures.SwitchRequestCompositionTests.prepare
    change = fixtures.SwitchRequestCompositionTests.change

    def configure(self):
        page, h, old, result = self.prepare()
        h['replies']['/api/campaigns/target/activate'] = (200, result)
        h['state']['active_campaign_id'] = 'target'
        h['state']['active_setup'] = {'campaign_id': 'target', 'name': 'default'}
        return page, h, old, result

    def held_refresh(self):
        page, h, old, result = self.configure()
        held = []
        page.route('**/api/state', lambda route: held.append(route))
        page.evaluate('''() => {
            const s=document.querySelector('#campaignSelect');s.value='target';
            window.pendingRefreshSwitch=s.onchange();
        }''')
        for _ in range(100):
            if held:
                break
            page.wait_for_timeout(10)
        self.assertEqual(len(held), 1)
        return page, h, old, result, held

    def test_success_is_visible_before_held_refresh_and_busy_covers_refresh(self):
        page, h, old, result, held = self.held_refresh()
        self.assertEqual(self.records(page, 'campaign.switch')[0]['severity'], 'success')
        self.assertTrue(page.locator('#switchCampaign').is_disabled())
        page.evaluate('() => document.querySelector("#switchCampaign").onclick()')
        self.assertEqual(len(h['writes']), 1)
        held[0].fulfill(status=200, json=h['state'])
        page.evaluate('() => pendingRefreshSwitch')
        self.assertEqual(self.records(page, 'campaign.switch.refresh'), [])
        self.assertEqual(page.evaluate('latest.active_campaign_id'), 'target')
        self.assertFalse(page.locator('#switchCampaign').is_disabled())

    def test_refresh_error_persists_after_success_expiry_without_post_replay(self):
        page, h, old, result = self.configure()
        h['replies']['/api/state'] = (503, {'detail': 'Refresh offline'})
        self.change(page, 'target')
        error = self.records(page, 'campaign.switch.refresh')[0]
        self.assertIn('Refresh offline', error['text'])
        self.assertIn('do not switch the campaign again', error['text'])
        self.assertEqual(page.evaluate('campaignData.active'), 'target')
        page.wait_for_function("scryingAdminFeedback.snapshot().every(r=>r.operation!=='campaign.switch')", timeout=4500)
        self.assertEqual(self.records(page, 'campaign.switch.refresh')[0]['severity'], 'error')
        page.evaluate('() => document.querySelector("#switchCampaign").onclick()')
        self.assertEqual(len(h['writes']), 1)

    def test_late_refresh_error_does_not_overwrite_returned_selection(self):
        page, h, old, result, held = self.held_refresh()
        self.change(page, old)
        self.change(page, 'target')
        held[0].fulfill(status=503, json={'detail': 'Obsolete refresh'})
        page.evaluate('() => pendingRefreshSwitch')
        self.assertEqual(self.records(page, 'campaign.switch.refresh'), [])
        self.assertEqual(page.locator('#campaignSelect').input_value(), 'target')
        self.assertEqual(len(h['writes']), 1)
        self.assertFalse(page.locator('#switchCampaign').is_disabled())

    def test_empty_setup_switch_preserves_blank_setup_controls(self):
        page, h, old, result = self.configure()
        result['opened_setup'] = None
        h['state']['active_setup'] = None
        self.change(page, 'target')
        self.assertEqual(self.records(page, 'campaign.switch')[0]['text'], 'Switched to campaign: Target')
        self.assertEqual(self.records(page, 'campaign.switch.refresh'), [])
        self.assertEqual(page.locator('#setupName').input_value(), '')
        self.assertEqual(page.evaluate('latest.active_campaign_id'), 'target')


if __name__ == '__main__':
    unittest.main()
