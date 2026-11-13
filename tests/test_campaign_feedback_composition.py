"""Campaign create, edit, switch and delete feedback on the loaded Admin page.

Intercepted HTTP; not authenticated live-server evidence.
"""
import json
import unittest
import test_admin_global_feedback_composition as composed


class CampaignCreateCompositionTests(unittest.TestCase):
    """Loaded Admin with intercepted HTTP, not authenticated live-server evidence."""

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


class CampaignEditCompositionTests(unittest.TestCase):
    """Loaded Admin campaign edit paths with intercepted HTTP, not a live server."""

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


class SwitchRequestCompositionTests(unittest.TestCase):
    """Full Admin, intercepted HTTP; retained 1C.1 request safeguards with 1C.2 feedback."""

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
        self.assertEqual([r['severity'] for r in self.records(page, 'campaign.switch')], ['success'])
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


class SwitchRefreshCompositionTests(unittest.TestCase):
    """Complete Admin with intercepted HTTP; no authenticated live-server claim."""

    @classmethod
    def setUpClass(cls):
        SwitchRequestCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        SwitchRequestCompositionTests.tearDownClass.__func__(cls)

    open_page = SwitchRequestCompositionTests.open_page
    records = SwitchRequestCompositionTests.records
    prepare = SwitchRequestCompositionTests.prepare
    change = SwitchRequestCompositionTests.change

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


class DeleteRequestCompositionTests(unittest.TestCase):
    """Complete Admin delete request safeguards with explicit success/refresh feedback."""

    @classmethod
    def setUpClass(cls):
        composed.GlobalFeedbackCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        composed.GlobalFeedbackCompositionTests.tearDownClass.__func__(cls)

    open_page = composed.GlobalFeedbackCompositionTests.open_page
    records = composed.GlobalFeedbackCompositionTests.records

    def prepare(self, setups=None):
        page, h = self.open_page()
        old = page.evaluate('campaignData.active')
        page.evaluate('''setups => {
            campaignData.campaigns.push({id:'victim',name:'Victim',description:'',setups:setups});
            renderCampaigns();document.querySelector('#deleteCampaign').onclick();
        }''', ['one'] if setups is None else setups)
        result = {'active': old, 'opened_setup': 'default', 'moved': ['one'], 'deleted_setups': [],
                  'campaigns': [{'id': old, 'name': 'Default', 'description': '', 'setups': ['default', 'one']}]}
        return page, h, old, result

    def change(self, page, selector, value):
        page.evaluate('''([selector,value]) => {
            const n=document.querySelector(selector);n.value=value;n.onchange?.();
        }''', [selector, value])

    def submit(self, page):
        page.evaluate('() => document.querySelector("#campaignDeleteForm").onsubmit({preventDefault(){}})')

    def test_last_campaign_selection_and_move_validation(self):
        page, h = self.open_page()
        page.evaluate('() => document.querySelector("#deleteCampaign").onclick()')
        self.assertEqual(self.records(page, 'campaign.delete.open')[0]['text'], 'The last remaining campaign cannot be deleted')
        self.assertTrue(page.locator('#campaignDeleteModal').is_hidden())
        page.evaluate('''() => {
            campaignData.campaigns.push({id:'victim',name:'Victim',setups:['one']});
            document.querySelector('#deleteCampaign').onclick();
        }''')
        self.assertEqual(self.records(page, 'campaign.delete.open'), [])
        self.assertEqual(page.locator('#campaignDeleteTarget').input_value(), 'victim')
        self.change(page, '#campaignDeleteTarget', '')
        self.submit(page)
        self.assertEqual(self.records(page, 'campaign.delete.validation')[0]['text'], 'Choose a campaign to delete')
        self.change(page, '#campaignDeleteTarget', 'victim')
        self.change(page, '#campaignDeleteMoveTo', '')
        self.submit(page)
        self.assertIn('Choose another campaign', self.records(page, 'campaign.delete.validation')[0]['text'])
        self.assertEqual(h['writes'], [])

    def test_rejected_move_preserves_options_and_successful_retry_retains_followup(self):
        page, h, old, result = self.prepare()
        urls = []
        page.on('request', lambda r: urls.append(r.url) if r.method == 'DELETE' else None)
        h['replies']['/api/campaigns/victim'] = (403, {'detail': 'Delete denied'})
        self.submit(page)
        self.assertEqual(self.records(page, 'campaign.delete')[0]['text'], 'Delete denied')
        self.assertFalse(page.locator('#campaignDeleteModal').is_hidden())
        self.assertEqual(page.locator('#campaignDeleteMoveTo').input_value(), old)
        self.assertFalse(page.locator('#campaignDeleteForm .danger').is_disabled())
        page.evaluate('''() => {
            const f=scryingAdminFeedback;
            f.publish(f.begin({lane:'page',region:'campaign',operation:'campaign.switch',target:'unrelated',label:'Other'}),
                      {severity:'error',text:'Keep switch error'});
        }''')
        h['replies']['/api/campaigns/victim'] = (200, result)
        self.submit(page)
        self.assertEqual([r['severity'] for r in self.records(page, 'campaign.delete')], ['success'])
        self.assertEqual(self.records(page, 'campaign.switch')[0]['text'], 'Keep switch error')
        self.assertTrue(page.locator('#campaignDeleteModal').is_hidden())
        self.assertIn('Deleted campaign: Victim (moved 1 setup(s))', page.locator('#campaignNotification').text_content())
        self.assertEqual(len(h['writes']), 2)
        self.assertTrue(all(url.endswith('/api/campaigns/victim?move_to=' + old) for url in urls))
        self.assertTrue(all(w['method'] == 'DELETE' and w['body'] is None for w in h['writes']))

    def test_permanent_delete_and_empty_campaign_keep_distinct_queries(self):
        for mode in ('delete', 'empty'):
            with self.subTest(mode=mode):
                page, h, old, result = self.prepare([] if mode == 'empty' else ['one'])
                urls = []
                page.on('request', lambda r: urls.append(r.url) if r.method == 'DELETE' else None)
                if mode == 'delete':
                    self.change(page, '#campaignDeleteAction', 'delete')
                    self.assertTrue(page.locator('#campaignDeleteMoveLabel').is_hidden())
                h['replies']['/api/campaigns/victim'] = (422, {'detail': 'Stop after request'})
                self.submit(page)
                self.assertEqual(len(urls), 1)
                self.assertTrue(urls[0].endswith('/api/campaigns/victim' + ('?delete_setups=true' if mode == 'delete' else '')))
                self.assertFalse(page.locator('#campaignDeleteModal').is_hidden())

    def test_cancel_reopen_suppresses_held_delete_and_blocks_duplicate(self):
        page, h, old, result = self.prepare()
        held = []
        page.route('**/api/campaigns/victim**', lambda route: held.append(route) if route.request.method == 'DELETE' else route.fallback())
        page.evaluate('''() => {
            window.pendingCampaignDelete=document.querySelector('#campaignDeleteForm').onsubmit({preventDefault(){}});
        }''')
        for _ in range(100):
            if held:
                break
            page.wait_for_timeout(10)
        self.assertEqual(len(held), 1)
        self.assertTrue(page.locator('#campaignDeleteForm .danger').is_disabled())
        page.keyboard.press('Escape')
        self.assertTrue(page.locator('#campaignDeleteModal').is_hidden())
        page.evaluate('() => document.querySelector("#deleteCampaign").onclick()')
        self.change(page, '#campaignDeleteAction', 'delete')
        self.submit(page)
        self.assertEqual(len(held), 1)
        held[0].fulfill(status=200, json=result)
        page.evaluate('() => pendingCampaignDelete')
        self.assertFalse(page.locator('#campaignDeleteModal').is_hidden())
        self.assertEqual(page.locator('#campaignDeleteAction').input_value(), 'delete')
        self.assertTrue(page.evaluate('campaignData.campaigns.some(c=>c.id==="victim")'))
        self.assertEqual(self.records(page, 'campaign.delete'), [])
        self.assertFalse(page.locator('#campaignDeleteForm .danger').is_disabled())


class DeleteRefreshCompositionTests(unittest.TestCase):
    """Full Admin/real guarded refresh pipeline; intercepted HTTP, not live-server acceptance."""

    @classmethod
    def setUpClass(cls):
        DeleteRequestCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        DeleteRequestCompositionTests.tearDownClass.__func__(cls)

    open_page = DeleteRequestCompositionTests.open_page
    records = DeleteRequestCompositionTests.records
    prepare = DeleteRequestCompositionTests.prepare
    change = DeleteRequestCompositionTests.change
    submit = DeleteRequestCompositionTests.submit

    def configure(self):
        page, h, old, result = self.prepare()
        h['replies']['/api/campaigns/victim'] = (200, result)
        return page, h, old, result

    def held(self):
        page, h, old, result = self.configure()
        held = []
        page.route('**/api/state', lambda route: held.append(route))
        page.evaluate('''() => {
            window.pendingDeleteRefresh=document.querySelector('#campaignDeleteForm').onsubmit({preventDefault(){}});
        }''')
        for _ in range(100):
            if held:
                break
            page.wait_for_timeout(10)
        self.assertEqual(len(held), 1)
        return page, h, old, result, held

    def test_success_precedes_held_refresh_and_busy_prevents_second_delete(self):
        page, h, old, result, held = self.held()
        self.assertEqual(self.records(page, 'campaign.delete')[0]['severity'], 'success')
        self.assertTrue(page.locator('#campaignDeleteForm .danger').is_disabled())
        self.submit(page)
        self.assertEqual(len(h['writes']), 1)
        held[0].fulfill(status=200, json=h['state'])
        page.evaluate('() => pendingDeleteRefresh')
        self.assertEqual(self.records(page, 'campaign.delete.refresh'), [])
        self.assertFalse(page.locator('#campaignDeleteForm .danger').is_disabled())

    def test_refresh_failure_persists_after_success_expiry_without_replay(self):
        page, h, old, result = self.configure()
        h['replies']['/api/state'] = (503, {'detail': 'Refresh offline'})
        self.submit(page)
        error = self.records(page, 'campaign.delete.refresh')[0]
        self.assertIn('Refresh offline', error['text'])
        self.assertIn('do not delete the campaign again', error['text'])
        self.assertFalse(page.evaluate('campaignData.campaigns.some(c=>c.id==="victim")'))
        page.wait_for_function("scryingAdminFeedback.snapshot().every(r=>r.operation!=='campaign.delete')", timeout=4500)
        self.assertEqual(self.records(page, 'campaign.delete.refresh')[0]['severity'], 'error')
        self.assertEqual(len(h['writes']), 1)

    def test_reopened_dialog_prevents_late_state_observation_render_and_error(self):
        for failure in (False, True):
            with self.subTest(failure=failure):
                page, h, old, result, held = self.held()
                before = page.evaluate('scryingAdminFeedback.encounterContext()')
                page.evaluate('''() => {
                    campaignData.campaigns.push({id:'new-target',name:'New target',setups:[]});
                    document.querySelector('#deleteCampaign').onclick();
                }''')
                if failure:
                    held[0].fulfill(status=503, json={'detail': 'Obsolete refresh'})
                else:
                    h['state']['active_campaign_id'] = 'obsolete-state'
                    h['state']['active_setup'] = None
                    held[0].fulfill(status=200, json=h['state'])
                page.evaluate('() => pendingDeleteRefresh')
                self.assertEqual(page.evaluate('scryingAdminFeedback.encounterContext()'), before)
                self.assertEqual(page.evaluate('latest.active_campaign_id'), old)
                self.assertFalse(page.locator('#campaignDeleteModal').is_hidden())
                self.assertEqual(page.locator('#campaignDeleteTarget').input_value(), 'new-target')
                self.assertEqual(self.records(page, 'campaign.delete.refresh'), [])
                self.assertFalse(any('Obsolete refresh' in r['text'] for r in page.evaluate('scryingAdminFeedback.snapshot()')))
                self.assertEqual(len(h['writes']), 1)

    def test_active_deletion_empty_setup_applies_expected_transition(self):
        page, h, old, result = self.prepare([])
        self.change(page, '#campaignDeleteTarget', old)
        result.update({'active': 'victim', 'opened_setup': None, 'moved': [],
                       'campaigns': [{'id': 'victim', 'name': 'Victim', 'setups': []}]})
        h['replies']['/api/campaigns/' + old] = (200, result)
        h['state']['active_campaign_id'] = 'victim'
        h['state']['active_setup'] = None
        self.submit(page)
        self.assertEqual(page.evaluate('campaignData.active'), 'victim')
        self.assertEqual(page.evaluate('latest.active_campaign_id'), 'victim')
        self.assertEqual(page.locator('#setupName').input_value(), '')
        self.assertEqual(self.records(page, 'campaign.delete.refresh'), [])
        self.assertEqual(self.records(page, 'campaign.delete')[0]['severity'], 'success')
        self.assertEqual(len(h['writes']), 1)


if __name__ == '__main__':
    unittest.main()
