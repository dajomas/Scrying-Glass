# Loaded Admin with intercepted HTTP, not authenticated live-server evidence.
import json
import unittest
import test_admin_global_feedback_composition as composed


class CampaignCreateCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        composed.GlobalFeedbackCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        composed.GlobalFeedbackCompositionTests.tearDownClass.__func__(cls)

    open_page = composed.GlobalFeedbackCompositionTests.open_page
    records = composed.GlobalFeedbackCompositionTests.records

    def submit(self, page):
        page.evaluate('''() => {
            openCampaignModal();
            const f=document.querySelector('#campaignForm');
            f.elements.name.value=' Created '; f.elements.description.value=' Details ';
            return f.onsubmit({target:f,currentTarget:f,preventDefault(){}});
        }''')

    def configure(self, h):
        result = {'active': 'created', 'opened_setup': 'default', 'moved': [], 'campaigns': [
            {'id': 'created', 'name': 'Created', 'description': 'Details', 'setups': ['default']}]}
        h['replies']['/api/campaigns'] = (200, result)
        h['state']['active_campaign_id'] = 'created'
        h['state']['active_setup'] = {'campaign_id': 'created', 'name': 'default'}

    def test_loaded_creation_survives_activation_and_keeps_exact_payload(self):
        page, h = self.open_page()
        self.configure(h)
        self.submit(page)
        self.assertEqual(self.records(page, 'campaign.create')[0]['severity'], 'success')
        self.assertEqual(self.records(page, 'campaign.create.refresh'), [])
        self.assertEqual(page.evaluate('latest.active_campaign_id'), 'created')
        self.assertEqual(page.locator('#setupName').input_value(), 'default')
        self.assertTrue(page.locator('#campaignModal').is_hidden())
        self.assertEqual(len(h['writes']), 1)
        self.assertEqual(h['writes'][0]['path'], '/api/campaigns')
        self.assertEqual(h['writes'][0]['method'], 'POST')
        self.assertEqual(json.loads(h['writes'][0]['body']),
                         {'name': 'Created', 'description': 'Details', 'activate': True})

    def test_loaded_request_rejection_retains_draft_and_modal(self):
        page, h = self.open_page()
        h['replies']['/api/campaigns'] = (422, {'detail': 'Creation denied'})
        self.submit(page)
        self.assertEqual(self.records(page, 'campaign.create')[0]['severity'], 'error')
        self.assertIn('Creation denied', page.locator('#campaignNotification').text_content())
        self.assertFalse(page.locator('#campaignModal').is_hidden())
        self.assertEqual(page.locator('#campaignForm input[name="name"]').input_value(), ' Created ')
        self.assertFalse(page.locator('#campaignSubmit').is_disabled())
        self.assertEqual(len(h['writes']), 1)

    def test_loaded_applied_creation_refresh_failure_never_replays_post(self):
        page, h = self.open_page()
        self.configure(h)
        h['replies']['/api/state'] = (503, {'detail': 'Reload unavailable'})
        self.submit(page)
        self.assertEqual(self.records(page, 'campaign.create')[0]['severity'], 'success')
        error = self.records(page, 'campaign.create.refresh')[0]
        self.assertEqual(error['severity'], 'error')
        self.assertIn('do not create the campaign again', error['text'])
        self.assertEqual(page.evaluate('campaignData.active'), 'created')
        del h['replies']['/api/state']
        page.evaluate('() => load(true)')
        self.assertEqual(len(h['writes']), 1)


if __name__ == '__main__':
    unittest.main()
