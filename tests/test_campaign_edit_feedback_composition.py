# Loaded Admin campaign edit paths with intercepted HTTP, not a live server.
import json
import unittest
import test_admin_global_feedback_composition as composed


class CampaignEditCompositionTests(unittest.TestCase):
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
        campaign = page.evaluate('campaignData.active')
        result = {'active': campaign, 'campaigns': [
            {'id': campaign, 'name': 'Updated', 'description': 'Description',
             'setups': ['default'], 'last_setup': 'default'}], 'moved': []}
        page.evaluate('() => openCampaignModal(activeCampaign())')
        page.locator('#campaignForm input[name="name"]').fill(' Updated ')
        page.locator('#campaignForm input[name="description"]').fill(' Description ')
        return page, h, campaign, result

    def submit(self, page):
        return page.evaluate('''() => {
            const f=document.querySelector('#campaignForm');
            return f.onsubmit({target:f,currentTarget:f,preventDefault(){}});
        }''')

    def test_success_payload_and_pane_expiry(self):
        page, h, campaign, result = self.prepare()
        h['replies']['/api/campaigns/' + campaign] = (200, result)
        self.submit(page)
        self.assertEqual(self.records(page, 'campaign.edit')[0]['text'], 'Updated campaign: Updated')
        self.assertTrue(page.locator('#campaignModal').is_hidden())
        self.assertEqual(page.locator('#campaignSelect').input_value(), campaign)
        self.assertEqual(h['writes'][0]['method'], 'PATCH')
        self.assertEqual(json.loads(h['writes'][0]['body']), {'name': 'Updated', 'description': 'Description'})
        self.assertEqual(len(h['writes']), 1)
        page.wait_for_function("scryingAdminFeedback.snapshot().every(r=>r.operation!=='campaign.edit')", timeout=4500)
        self.assertEqual(self.records(page, 'campaign.edit'), [])

    def test_error_draft_and_matching_retry(self):
        page, h, campaign, result = self.prepare()
        h['replies']['/api/campaigns/' + campaign] = (422, {'detail': 'Save denied'})
        self.submit(page)
        self.assertEqual(self.records(page, 'campaign.edit')[0]['text'], 'Save denied')
        self.assertFalse(page.locator('#campaignModal').is_hidden())
        self.assertEqual(page.locator('#campaignForm input[name="name"]').input_value(), ' Updated ')
        h['replies']['/api/campaigns/' + campaign] = (200, result)
        self.submit(page)
        self.assertEqual([r['severity'] for r in self.records(page, 'campaign.edit')], ['success'])
        self.assertEqual(len(h['writes']), 2)

    def test_old_response_cannot_close_reopened_edit(self):
        page, h, campaign, result = self.prepare()
        held = []
        def hold(route):
            held.append(route)
        page.route('**/api/campaigns/' + campaign, hold)
        page.evaluate('''() => {
            const f=document.querySelector('#campaignForm');
            window.pendingCampaignEdit=f.onsubmit({target:f,currentTarget:f,preventDefault(){}});
        }''')
        for _ in range(100):
            if held:
                break
            page.wait_for_timeout(10)
        self.assertEqual(len(held), 1)
        page.evaluate('''() => {
            closeCampaignModal();openCampaignModal(activeCampaign());
            document.querySelector('#campaignForm').elements.name.value='Keep newer draft';
        }''')
        held[0].fulfill(status=200, json=result)
        page.evaluate('() => pendingCampaignEdit')
        self.assertEqual(self.records(page, 'campaign.edit'), [])
        self.assertFalse(page.locator('#campaignModal').is_hidden())
        self.assertEqual(page.locator('#campaignForm input[name="name"]').input_value(), 'Keep newer draft')
        self.assertFalse(page.locator('#campaignSubmit').is_disabled())


if __name__ == '__main__':
    unittest.main()
