# Full Admin/real guarded refresh pipeline; intercepted HTTP, not live-server acceptance.
import unittest
import test_campaign_delete_request_feedback_composition as fixtures


class DeleteRefreshCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixtures.DeleteRequestCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        fixtures.DeleteRequestCompositionTests.tearDownClass.__func__(cls)

    open_page = fixtures.DeleteRequestCompositionTests.open_page
    records = fixtures.DeleteRequestCompositionTests.records
    prepare = fixtures.DeleteRequestCompositionTests.prepare
    change = fixtures.DeleteRequestCompositionTests.change
    submit = fixtures.DeleteRequestCompositionTests.submit

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
