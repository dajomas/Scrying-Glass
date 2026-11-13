# SG-TODO-009.7 Stage 1 Steps 2B-2E. Loaded Admin with intercepted HTTP, not live-server evidence.
import json
import unittest
import test_admin_global_feedback_composition as composed


class SetupOperationsCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        composed.GlobalFeedbackCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        composed.GlobalFeedbackCompositionTests.tearDownClass.__func__(cls)

    open_page = composed.GlobalFeedbackCompositionTests.open_page
    records = composed.GlobalFeedbackCompositionTests.records

    def prepare(self, setups=('default', 'Two')):
        page, h = self.open_page()
        campaign = h['state']['active_campaign_id']
        h['replies']['/api/campaigns'] = (200, {'active': campaign, 'moved': [], 'campaigns': [
            {'id': campaign, 'name': 'Default', 'description': '', 'setups': list(setups), 'last_setup': 'default'}]})
        page.evaluate("() => setups()")
        return page, h, campaign

    def activate(self, h, campaign, name):
        h['state']['active_setup'] = {'campaign_id': campaign, 'name': name}

    def select(self, page, value):
        page.eval_on_selector('#setupSelect', '(n, v) => {n.value = v;}', value)

    def type(self, page, value):
        page.eval_on_selector('#setupName', "(n, v) => {n.value = v; n.dispatchEvent(new Event('input', {bubbles: true}));}", value)

    def click(self, page, button):
        page.evaluate(f"() => document.querySelector('#{button}').onclick()")

    def test_loaded_save_posts_once_and_reports_pane_success(self):
        page, h, campaign = self.prepare(('default', 'Fresh'))
        h['replies']['/api/setups/save'] = (200, {'name': 'Fresh', 'campaign': campaign})
        self.activate(h, campaign, 'Fresh')
        self.type(page, ' Fresh ')
        self.click(page, 'saveSetup')
        success = self.records(page, 'setup.save')[0]
        self.assertEqual((success['severity'], success['region']), ('success', 'battleSetup'))
        self.assertIn('Saved setup: Fresh (campaign: Default)', page.locator('#battleSetupNotification').text_content())
        self.assertEqual(self.records(page, 'setup.save.refresh'), [])
        self.assertEqual(page.locator('#setupSelect').input_value(), 'Fresh')
        self.assertEqual([(w['path'], w['method']) for w in h['writes']], [('/api/setups/save', 'POST')])
        self.assertEqual(json.loads(h['writes'][0]['body']), {'name': 'Fresh', 'campaign': campaign})

    def test_loaded_validation_and_rejection_persist(self):
        page, h, campaign = self.prepare()
        self.type(page, '  ')
        self.click(page, 'saveSetup')
        self.assertEqual(self.records(page, 'setup.save.validation')[0]['severity'], 'error')
        self.assertEqual(h['writes'], [])
        h['replies']['/api/setups/load'] = (404, {'detail': 'Battle setup not found'})
        self.select(page, 'Two')
        page.evaluate("() => document.querySelector('#setupSelect').onchange()")
        self.assertEqual(self.records(page, 'setup.load')[0]['severity'], 'error')
        self.assertIn('Battle setup not found', page.locator('#battleSetupNotification').text_content())
        self.assertEqual(page.locator('#setupSelect').input_value(), 'default')
        self.assertFalse(page.locator('#setupSelect').is_disabled())

    def test_loaded_switch_rename_and_delete_report_success(self):
        page, h, campaign = self.prepare()
        h['replies']['/api/setups/load'] = (200, {'name': 'Two', 'campaign': campaign})
        self.activate(h, campaign, 'Two')
        self.select(page, 'Two')
        self.click(page, 'loadSetup')
        self.assertEqual(self.records(page, 'setup.load')[0]['text'], 'Loaded battle setup: Two')
        self.assertEqual(page.evaluate('latest.active_setup.name'), 'Two')
        h['replies']['/api/setups/rename'] = (200, {'old_name': 'Two', 'name': 'Main', 'campaign': campaign})
        h['replies']['/api/campaigns'][1]['campaigns'][0]['setups'] = ['default', 'Main']
        self.activate(h, campaign, 'Main')
        page.evaluate("() => {window.prompt = () => 'Main';}")
        self.click(page, 'renameSetup')
        self.assertEqual(self.records(page, 'setup.rename')[0]['text'], 'Renamed battle setup Two to Main')
        self.assertEqual(self.records(page, 'setup.rename.refresh'), [])
        self.assertEqual(page.locator('#setupSelect').input_value(), 'Main')
        path = '/api/setups/Main'
        h['replies'][path] = (200, {'deleted': 'Main', 'opened_setup': 'default', 'created_default': False, 'campaign': campaign})
        h['replies']['/api/campaigns'][1]['campaigns'][0]['setups'] = ['default']
        self.activate(h, campaign, 'default')
        self.click(page, 'deleteSetup')
        self.assertEqual(self.records(page, 'setup.delete')[0]['text'], 'Deleted battle setup Main; opened default')
        self.assertEqual(self.records(page, 'setup.delete.refresh'), [])
        self.assertEqual([(w['path'], w['method']) for w in h['writes']],
                         [('/api/setups/load', 'POST'), ('/api/setups/rename', 'POST'), (path, 'DELETE')])

    def test_loaded_refresh_failure_never_replays_delete(self):
        page, h, campaign = self.prepare()
        h['replies']['/api/setups/Two'] = (200, {'deleted': 'Two', 'opened_setup': 'default', 'campaign': campaign})
        h['replies']['/api/state'] = (503, {'detail': 'Reload unavailable'})
        self.select(page, 'Two')
        self.click(page, 'deleteSetup')
        self.assertEqual(self.records(page, 'setup.delete')[0]['severity'], 'success')
        error = self.records(page, 'setup.delete.refresh')[0]
        self.assertEqual(error['severity'], 'error')
        self.assertIn('do not repeat the deletion', error['text'])
        del h['replies']['/api/state']
        page.evaluate('() => load(true)')
        self.assertEqual(len(h['writes']), 1)


if __name__ == '__main__':
    unittest.main()
