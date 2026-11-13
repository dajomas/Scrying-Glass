# SG-TODO-009.7 Stage 1 Step 3. Loaded Admin with intercepted HTTP, not live-server evidence.
import json
import unittest
import test_admin_global_feedback_composition as composed


class SetupTransferBackgroundCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        composed.GlobalFeedbackCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        composed.GlobalFeedbackCompositionTests.tearDownClass.__func__(cls)

    open_page = composed.GlobalFeedbackCompositionTests.open_page
    records = composed.GlobalFeedbackCompositionTests.records

    def prepare(self):
        page, h = self.open_page()
        campaign = h['state']['active_campaign_id']
        listing = {'active': campaign, 'moved': [], 'campaigns': [
            {'id': campaign, 'name': 'Default', 'description': '', 'setups': ['default'], 'last_setup': 'default'},
            {'id': 'other', 'name': 'Other', 'description': '', 'setups': ['Ambush'], 'last_setup': 'Ambush'}]}
        h['replies']['/api/campaigns'] = (200, listing)
        page.evaluate("() => setups()")
        return page, h, campaign, listing

    def open_modal(self, page):
        page.evaluate("() => document.querySelector('#openCampaignSetup').onclick()")
        self.assertTrue(page.locator('#campaignSetupModal').is_visible())

    def submit(self, page, values):
        page.evaluate("""v => {
            const form = document.querySelector('#campaignSetupForm');
            if (v.from_campaign) {form.elements.from_campaign.value = v.from_campaign; renderCampaignSetupNames();}
            for (const [name, value] of Object.entries(v)) form.elements[name].value = value;
            if (form.elements.setup.value !== v.setup) throw new Error('fixture setup option missing');
            return form.onsubmit({preventDefault() {}, target: form});
        }""", values)

    def test_loaded_copy_posts_once_and_reports_campaign_pane_success(self):
        page, h, campaign, listing = self.prepare()
        self.open_modal(page)
        self.assertEqual(page.locator('#campaignSetupFrom').input_value(), 'other')
        self.assertEqual(page.locator('#campaignSetupTo').input_value(), campaign)
        result = json.loads(json.dumps(listing))
        result['campaigns'][0]['setups'] = ['default', 'Ambush']
        result.update(setup='Ambush', campaign=campaign, mode='copy')
        path = f'/api/campaigns/{campaign}/setups'
        h['replies'][path] = (200, result)
        self.submit(page, {'setup': 'Ambush', 'mode': 'copy'})
        success = self.records(page, 'setup.transfer')[0]
        self.assertEqual((success['severity'], success['region']), ('success', 'campaign'))
        self.assertIn('Copied setup Ambush to campaign Default', page.locator('#campaignNotification').text_content())
        self.assertFalse(page.locator('#campaignSetupModal').is_visible())
        self.assertEqual(self.records(page, 'setup.transfer.refresh'), [])
        self.assertEqual([(w['path'], w['method']) for w in h['writes']], [(path, 'POST')])
        self.assertEqual(json.loads(h['writes'][0]['body']), {'setup': 'Ambush', 'from_campaign': 'other', 'mode': 'copy'})

    def test_loaded_move_of_active_setup_refreshes_unloaded_scope_and_rejection_persists(self):
        page, h, campaign, listing = self.prepare()
        self.open_modal(page)
        path = '/api/campaigns/other/setups'
        h['replies'][path] = (400, {'detail': 'Setup is already in this campaign'})
        self.submit(page, {'from_campaign': campaign, 'setup': 'default', 'to_campaign': 'other', 'mode': 'move'})
        self.assertEqual(self.records(page, 'setup.transfer')[0]['severity'], 'error')
        self.assertIn('Setup is already in this campaign', page.locator('#campaignNotification').text_content())
        self.assertTrue(page.locator('#campaignSetupModal').is_visible())
        h['replies'][path] = (200, dict(listing, setup='default', campaign='other', mode='move'))
        h['state']['active_setup'] = None
        self.submit(page, {'from_campaign': campaign, 'setup': 'default', 'to_campaign': 'other', 'mode': 'move'})
        self.assertEqual(self.records(page, 'setup.transfer')[0]['text'], 'Moved setup default to campaign Other')
        self.assertEqual(self.records(page, 'setup.transfer.refresh'), [])
        self.assertIsNone(page.evaluate('latest.active_setup'))
        self.assertEqual(len(h['writes']), 2)

    def test_loaded_background_apply_upload_and_refresh_failure(self):
        page, h, campaign, listing = self.prepare()
        h['replies']['/api/display/background'] = (200, {})
        page.eval_on_selector('#backgroundValue', "n => {n.value = '#123456';}")
        page.evaluate("() => document.querySelector('#applyBackground').onclick()")
        self.assertEqual(self.records(page, 'background.apply')[0]['text'],
                         'View screen background updated. Save the setup to keep it.')
        self.assertIn('View screen background updated', page.locator('#battleSetupNotification').text_content())
        self.assertEqual(json.loads(h['writes'][0]['body']), {'background': '#123456'})
        h['replies']['/api/display/background-image'] = (200, {'background': '/uploads/map.png'})
        h['state'].setdefault('display', {})['background'] = '/uploads/map.png'  # server state after upload
        page.set_input_files('#backgroundImage', files=[{'name': 'map.png', 'mimeType': 'image/png', 'buffer': b'\x89PNG'}])
        page.wait_for_function("scryingAdminFeedback.snapshot().some(x => x.operation === 'background.upload')")
        self.assertEqual(page.locator('#backgroundValue').input_value(), '/uploads/map.png')
        self.assertEqual(page.locator('#backgroundImage').input_value(), '')
        h['replies']['/api/state'] = (503, {'detail': 'Reload unavailable'})
        page.evaluate("() => document.querySelector('#clearBackgroundImage').onclick()")
        error = self.records(page, 'background.clear.refresh')[0]
        self.assertIn('do not repeat the background change', error['text'])
        del h['replies']['/api/state']
        page.evaluate('() => load(true)')
        self.assertEqual([w['path'] for w in h['writes']], ['/api/display/background',
                         '/api/display/background-image', '/api/display/background'])


if __name__ == '__main__':
    unittest.main()
