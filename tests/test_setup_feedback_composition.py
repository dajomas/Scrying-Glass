"""Setup new, save/load/rename/delete, transfer and background feedback on the loaded Admin page.

Intercepted HTTP; not authenticated live-server evidence.
"""
import json
import unittest
import test_admin_global_feedback_composition as composed


class SetupNewCompositionTests(unittest.TestCase):
    """SG-TODO-009.7 Stage 1 Step 2A. Loaded Admin with intercepted HTTP, not live-server evidence."""

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


class SetupOperationsCompositionTests(unittest.TestCase):
    """SG-TODO-009.7 Stage 1 Steps 2B-2E. Loaded Admin with intercepted HTTP, not live-server evidence."""

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


class SetupTransferBackgroundCompositionTests(unittest.TestCase):
    """SG-TODO-009.7 Stage 1 Step 3. Loaded Admin with intercepted HTTP, not live-server evidence."""

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
