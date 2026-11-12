# Full Admin, intercepted HTTP; success/refresh feedback migration remains 1C.2.
import unittest
import test_admin_global_feedback_composition as composed


class SwitchRequestCompositionTests(unittest.TestCase):
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
        old = page.evaluate('campaignData.active')
        page.evaluate('''() => {
            campaignData.campaigns.push({id:'target',name:'Target',description:'',setups:['default']});
            renderCampaigns();
        }''')
        result = {'active': 'target', 'opened_setup': 'default', 'campaigns': [
            {'id': old, 'name': 'Default', 'description': '', 'setups': ['default']},
            {'id': 'target', 'name': 'Target', 'description': '', 'setups': ['default']}]}
        return page, h, old, result

    def change(self, page, value):
        return page.evaluate('''value => {
            const s=document.querySelector('#campaignSelect');s.value=value;
            return s.onchange();
        }''', value)

    def test_validation_and_request_error_preserve_edit_feedback(self):
        page, h, old, result = self.prepare()
        self.change(page, '')
        self.assertEqual(self.records(page, 'campaign.switch.validation')[0]['severity'], 'error')
        self.assertEqual(page.locator('#campaignSelect').input_value(), old)
        h['replies']['/api/campaigns/target/activate'] = (403, {'detail': 'Switch denied'})
        self.change(page, 'target')
        self.assertEqual(self.records(page, 'campaign.switch.validation'), [])
        self.assertEqual(self.records(page, 'campaign.switch')[0]['text'], 'Switch denied')
        self.assertEqual(page.locator('#campaignSelect').input_value(), old)
        self.assertFalse(page.locator('#switchCampaign').is_disabled())
        h['replies']['/api/campaigns/' + old] = (422, {'detail': 'Edit denied'})
        page.evaluate('''() => {
            openCampaignModal(activeCampaign());const f=document.querySelector('#campaignForm');
            f.elements.name.value='Keep edit draft';return f.onsubmit({preventDefault(){}});
        }''')
        self.assertEqual(self.records(page, 'campaign.edit')[0]['text'], 'Edit denied')
        self.assertEqual(self.records(page, 'campaign.switch')[0]['text'], 'Switch denied')
        self.assertEqual(page.locator('#campaignForm input[name="name"]').input_value(), 'Keep edit draft')

    def test_successful_retry_preserves_existing_activation_setup_flow(self):
        page, h, old, result = self.prepare()
        path = '/api/campaigns/target/activate'
        h['replies'][path] = (422, {'detail': 'Retry explicitly'})
        self.change(page, 'target')
        h['replies'][path] = (200, result)
        h['state']['active_campaign_id'] = 'target'
        h['state']['active_setup'] = {'campaign_id': 'target', 'name': 'default'}
        self.change(page, 'target')
        self.assertEqual(self.records(page, 'campaign.switch'), [])
        self.assertEqual(page.evaluate('campaignData.active'), 'target')
        self.assertEqual(page.evaluate('latest.active_campaign_id'), 'target')
        self.assertEqual(page.locator('#setupName').input_value(), 'default')
        self.assertIn('Switched to campaign: Target; opened battle setup default', page.locator('#campaignNotification').text_content())
        self.assertEqual(len(h['writes']), 2)
        self.assertEqual(h['writes'][1], {'path': path, 'method': 'POST', 'body': None})

    def test_changed_and_returned_selection_suppresses_held_response(self):
        page, h, old, result = self.prepare()
        held = []
        page.route('**/api/campaigns/target/activate', lambda route: held.append(route))
        page.evaluate('''() => {
            const s=document.querySelector('#campaignSelect');s.value='target';
            window.pendingSwitch=s.onchange();
        }''')
        for _ in range(100):
            if held:
                break
            page.wait_for_timeout(10)
        self.assertEqual(len(held), 1)
        self.change(page, old)
        self.change(page, 'target')
        held[0].fulfill(status=200, json=result)
        page.evaluate('() => pendingSwitch')
        self.assertEqual(page.evaluate('campaignData.active'), old)
        self.assertEqual(page.locator('#campaignSelect').input_value(), 'target')
        self.assertEqual(self.records(page, 'campaign.switch'), [])
        self.assertFalse(page.locator('#switchCampaign').is_disabled())


if __name__ == '__main__':
    unittest.main()
