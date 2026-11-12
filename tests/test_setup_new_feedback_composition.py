# SG-TODO-009.7 Stage 1 Step 2A. Loaded Admin with intercepted HTTP, not live-server evidence.
import json
import unittest
import test_admin_global_feedback_composition as composed


class SetupNewCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        composed.GlobalFeedbackCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        composed.GlobalFeedbackCompositionTests.tearDownClass.__func__(cls)

    open_page = composed.GlobalFeedbackCompositionTests.open_page
    records = composed.GlobalFeedbackCompositionTests.records

    def create(self, page, name=' Fresh '):
        # The setup pane may be collapsed during a battle; dispatch real input events.
        page.eval_on_selector('#setupName', "(n, v) => {n.value = v; n.dispatchEvent(new Event('input', {bubbles: true}));}", name)
        page.evaluate("() => document.querySelector('#newSetup').onclick()")

    def configure(self, h):
        campaign = h['state']['active_campaign_id']
        h['replies']['/api/setups/new'] = (200, {'name': 'Fresh', 'campaign': campaign})
        h['replies']['/api/campaigns'] = (200, {'active': campaign, 'moved': [], 'campaigns': [
            {'id': campaign, 'name': 'Default', 'description': '', 'setups': ['default', 'Fresh'], 'last_setup': 'Fresh'}]})
        h['state']['active_setup'] = {'campaign_id': campaign, 'name': 'Fresh'}
        return campaign

    def test_loaded_creation_posts_once_and_reports_pane_success(self):
        page, h = self.open_page()
        campaign = self.configure(h)
        self.create(page)
        success = self.records(page, 'setup.new')[0]
        self.assertEqual(success['severity'], 'success')
        self.assertEqual(success['region'], 'battleSetup')
        self.assertIn('Created and saved empty battle setup', page.locator('#battleSetupNotification').text_content())
        self.assertEqual(self.records(page, 'setup.new.refresh'), [])
        self.assertEqual(page.locator('#setupName').input_value(), 'Fresh')
        self.assertEqual(page.locator('#setupSelect').input_value(), 'Fresh')
        self.assertEqual(page.evaluate('latest.active_setup.name'), 'Fresh')
        self.assertFalse(page.locator('#newSetup').is_disabled())
        self.assertEqual([(w['path'], w['method']) for w in h['writes']], [('/api/setups/new', 'POST')])
        self.assertEqual(json.loads(h['writes'][0]['body']), {'name': 'Fresh', 'campaign': campaign})

    def test_loaded_duplicate_name_and_request_rejection_persist(self):
        page, h = self.open_page()
        self.create(page, ' DEFAULT ')
        validation = self.records(page, 'setup.new.validation')[0]
        self.assertEqual(validation['severity'], 'error')
        self.assertIn('already exists', page.locator('#battleSetupNotification').text_content())
        self.assertEqual(h['writes'], [])
        h['replies']['/api/setups/new'] = (409, {'detail': 'Activate this campaign before creating its setup'})
        self.create(page)
        self.assertEqual(self.records(page, 'setup.new.validation'), [])
        error = self.records(page, 'setup.new')[0]
        self.assertEqual(error['severity'], 'error')
        self.assertIn('Activate this campaign', page.locator('#battleSetupNotification').text_content())
        self.assertEqual(page.locator('#setupName').input_value(), ' Fresh ')
        self.assertEqual(len(h['writes']), 1)

    def test_loaded_refresh_failure_never_replays_creation(self):
        page, h = self.open_page()
        self.configure(h)
        h['replies']['/api/state'] = (503, {'detail': 'Reload unavailable'})
        self.create(page)
        self.assertEqual(self.records(page, 'setup.new')[0]['severity'], 'success')
        error = self.records(page, 'setup.new.refresh')[0]
        self.assertEqual(error['severity'], 'error')
        self.assertIn('do not create the setup again', error['text'])
        del h['replies']['/api/state']
        page.evaluate('() => load(true)')
        self.assertEqual(len(h['writes']), 1)


if __name__ == '__main__':
    unittest.main()
