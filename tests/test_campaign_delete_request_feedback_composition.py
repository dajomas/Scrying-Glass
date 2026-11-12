# Complete Admin delete request safeguards with explicit success/refresh feedback.
import unittest
import test_admin_global_feedback_composition as composed


class DeleteRequestCompositionTests(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
