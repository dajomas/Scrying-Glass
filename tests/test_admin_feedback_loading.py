# Production header/first-core slice, not full-Admin or live-server evidence.
from pathlib import Path
from urllib.parse import urlsplit
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class FeedbackLoadingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def open_page(self):
        page = self.browser.new_page(viewport={'width': 800, 'height': 900})
        self.addCleanup(page.close)
        page.set_default_timeout(3000)
        page.clock.install()
        errors, writes = [], []
        page.on('pageerror', lambda e: errors.append(str(e)))
        header = (ROOT/'templates/admin/010_pane_controls.html').read_text()
        html = '<!doctype html><html><body><header id="adminHeader">' + header + '''
          <button id="startBattle">Start</button><button id="nextBattle">Next</button>
          <p id="campaignNotification"> </p><p id="characterAddNotification"> </p>
          <p id="battleSetupNotification"> </p><p id="monsterAddNotification"> </p>
          <input id="draft" value="Keep this draft"><input id="monsterSpecies" value="Goblin">
          <input id="monsterAc"><input id="monsterHpRangeStart"><input id="monsterHpRangeEnd">
          <input type="checkbox" id="monsterSpeciesLookupOverwrite">
          <div id="characters"><button data-ca="c1">Join Battle</button></div><div id="monsters"></div>
          <script src="/static/admin.js" defer></script>
          <script src="/static/admin-notification-layout.js" defer></script>
          <script src="/fixture/ready.js" defer></script></main></body></html>'''
        state = {'active_campaign_id': 'campaign-a', 'active_setup': {'campaign_id': 'campaign-a', 'name': 'setup-a'},
                 'characters': [{'id': 'c1', 'name': 'Cleric', 'active': False, 'initiative': None}], 'monsters': []}

        def route(r):
            path = urlsplit(r.request.url).path
            if path == '/':
                r.fulfill(content_type='text/html', body=html)
            elif path == '/static/admin.js':
                r.fulfill(content_type='text/javascript', body=(ROOT/'static/admin/010-source.js').read_text())
            elif path.startswith('/static/'):
                file = ROOT/path.lstrip('/')
                r.fulfill(content_type='text/css' if file.suffix == '.css' else 'text/javascript', body=file.read_text())
            elif path == '/fixture/ready.js':
                r.fulfill(content_type='text/javascript', body="request('/api/state').then(s=>{latest=s;window.ready=true})")
            elif path == '/api/state':
                r.fulfill(json=state)
            elif path.startswith('/api/dndbeyond/'):
                r.fulfill(json={'found': True, 'provider': 'D&D Beyond', 'source': 'MM', 'ac': 15, 'hp': 7})
            elif path.startswith('/api/'):
                if r.request.method != 'GET':
                    writes.append(path)
                r.fulfill(status=422, json={'detail': 'Rejected fixture join'})
            else:
                r.fulfill(status=404)
        page.route('**/*', route)
        page.goto('http://fixture.test/', wait_until='load')
        page.wait_for_function('window.ready===true')
        self.assertEqual(errors, [])
        self.addCleanup(lambda: self.assertEqual(errors, []))
        return page, writes

    def emit(self, page, region='global', severity='error', operation='test.edit', text='Persistent error'):
        page.evaluate('''s=>{const a=scryingAdminFeedback;
            const ticket=a.begin({region:s.region,operation:s.operation,target:'one',label:s.operation});
            return a.deliver(s.region,s.text,{ticket,severity:s.severity})}''',
            dict(region=region, severity=severity, operation=operation, text=text))

    def test_header_order_and_original_roots(self):
        source = (ROOT/'templates/admin/010_pane_controls.html').read_text()
        paths = ['admin-feedback-controller.js', 'admin-feedback-view.js', 'admin-feedback-admin.js', 'initiative-join-gate.js']
        self.assertEqual([source.index(p) for p in paths], sorted(source.index(p) for p in paths))
        self.assertNotIn('admin-message-timeout.js', source)
        page, writes = self.open_page()
        self.assertEqual(page.locator('[data-sg-feedback-mounted]').count(), 5)
        self.assertEqual(page.locator('#draft').input_value(), 'Keep this draft')
        self.assertEqual(writes, [])

    def test_join_gate_persists_without_mutation_or_unrelated_clear(self):
        page, writes = self.open_page()
        self.emit(page, operation='independent', text='Independent error')
        page.locator('[data-ca]').click(force=True)
        page.clock.run_for(6000)
        text = page.locator('#message').text_content()
        self.assertIn('Enter initiative before joining battle: Cleric', text)
        self.assertIn('Independent error', text)
        self.assertEqual(page.locator('#message button').count(), 2)
        self.assertEqual(writes, [])

    def test_success_deadlines(self):
        page, _ = self.open_page()
        self.emit(page, severity='success', operation='global')
        self.emit(page, region='monsters', severity='success', operation='pane')
        page.clock.run_for(2999)
        self.assertTrue(page.locator('#monsterAddNotification').is_visible())
        page.clock.run_for(1)
        self.assertTrue(page.locator('#monsterAddNotification').is_hidden())
        self.assertTrue(page.locator('#message').is_visible())
        page.clock.run_for(2000)
        self.assertTrue(page.locator('#message').is_hidden())

    def test_retired_observer_is_guarded(self):
        page, _ = self.open_page()
        self.emit(page)
        page.add_script_tag(content=(ROOT/'static/admin-message-timeout.js').read_text())
        page.clock.run_for(10000)
        self.assertIn('Persistent error', page.locator('#message').text_content())

    def test_legacy_clear_cannot_clear_explicit_error(self):
        page, _ = self.open_page()
        self.emit(page, region='monsters')
        page.evaluate("paneNotification('monsters','Legacy');paneNotification('monsters','')")
        self.assertEqual(page.evaluate('scryingAdminFeedback.legacyRegions()'), ['monsters'])
        self.assertIn('Persistent error', page.locator('#monsterAddNotification').text_content())
        self.assertEqual(page.locator('#monsterAddNotification .sg-feedback-record').count(), 1)

    def test_lookup_clear_preserves_unrelated_error_and_draft(self):
        page, _ = self.open_page()
        self.emit(page, region='monsters', text='Edit failed')
        page.evaluate('lookupMonsterSpeciesStats()')
        self.assertEqual(page.locator('#monsterAc').input_value(), '15')
        self.assertEqual(page.locator('#monsterHpRangeStart').input_value(), '7')
        self.assertIn('Loaded', page.locator('#monsterAddNotification').text_content())
        page.evaluate("setMonsterSpeciesLookupStatus('')")
        self.assertIn('Edit failed', page.locator('#monsterAddNotification').text_content())
        self.assertEqual(page.locator('#monsterAddNotification .sg-feedback-record').count(), 1)
        self.assertEqual(page.locator('#draft').input_value(), 'Keep this draft')

    def test_lookup_failure_is_persistent(self):
        page, _ = self.open_page()
        page.route('**/api/dndbeyond/*', lambda r: r.fulfill(status=503, json={'detail': 'Unavailable'}))
        page.evaluate('lookupMonsterSpeciesStats()')
        page.clock.run_for(10000)
        self.assertIn('Monster lookup is unavailable', page.locator('#monsterAddNotification').text_content())
        self.assertEqual(page.locator('#monsterAddNotification [data-severity="error"]').count(), 1)
        self.assertEqual(page.locator('#monsterAc').input_value(), '')

    def hold_lookup(self, page):
        held = []
        page.route('**/api/dndbeyond/*', lambda r: held.append(r))
        page.evaluate('() => {window.pendingLookup=lookupMonsterSpeciesStats()}')
        page.wait_for_function("document.querySelector('#monsterAddNotification').textContent.includes('Looking up')")
        self.assertEqual(len(held), 1)
        return held[0]

    def change_scope(self, page):
        page.evaluate("scryingAdminFeedback.observeState({active_campaign_id:'new',active_setup:null},scryingAdminFeedback.stateRequest())")

    def test_old_lookup_cannot_change_scope_feedback_or_inputs(self):
        page, _ = self.open_page()
        held = self.hold_lookup(page)
        self.change_scope(page)
        held.fulfill(json={'found': True, 'ac': 99, 'hp': 99, 'provider': 'D&D Beyond'})
        page.evaluate('() => window.pendingLookup')
        self.assertEqual(page.locator('#monsterAc').input_value(), '')
        self.assertTrue(page.locator('#monsterAddNotification').is_hidden())

    def test_old_state_response_is_ignored_for_feedback(self):
        page, _ = self.open_page()
        held = []
        page.route('**/api/state', lambda r: held.append(r))
        page.evaluate("() => {window.first=request('/api/state');window.second=request('/api/state')}")
        page.wait_for_timeout(20)
        self.assertEqual(len(held), 2)
        held[1].fulfill(json={'active_campaign_id': 'new', 'active_setup': None})
        page.evaluate('() => window.second')
        self.emit(page, text='New scope error')
        held[0].fulfill(json={'active_campaign_id': 'old', 'active_setup': None})
        page.evaluate('() => window.first')
        self.assertIn('New scope error', page.locator('#message').text_content())
        self.assertEqual(page.evaluate('JSON.parse(scryingAdminFeedback.snapshot()[0].scope)[0]'), 'new')

    def test_keyboard_fallback(self):
        page, _ = self.open_page()
        self.emit(page)
        page.locator('#message button').focus()
        page.keyboard.press('Enter')
        self.assertTrue(page.locator('#message').is_hidden())
        self.assertTrue(page.locator('#nextBattle').evaluate('n=>n===document.activeElement'))

    def test_request_error_shape_is_preserved(self):
        page, _ = self.open_page()
        page.route('**/api/test-validation', lambda r: r.fulfill(status=422, json={'detail': [{'loc': ['body', 'name'], 'msg': 'Required'}]}))
        result = page.evaluate("() => request('/api/test-validation').catch(e=>({message:e.message,status:e.status,url:e.url}))")
        self.assertEqual(result, {'message': 'name: Required', 'status': 422, 'url': '/api/test-validation'})

    def test_bootstrap_is_idempotent(self):
        page, _ = self.open_page()
        self.emit(page)
        page.add_script_tag(content=(ROOT/'static/admin-feedback-admin.js').read_text())
        self.assertEqual(page.locator('#message .sg-feedback-record').count(), 1)
        self.assertEqual(page.locator('[data-sg-feedback-mounted]').count(), 5)

    def test_join_retry_resolves_only_related_error(self):
        page, _ = self.open_page()
        self.emit(page, operation='independent', text='Independent error')
        page.locator('[data-ca]').click(force=True)
        page.route('**/api/characters/c1', lambda r: r.fulfill(json={'id': 'c1', 'active': True}))
        result = page.evaluate("() => fetch('/api/characters/c1',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({active:true})}).then(r=>({ok:r.ok,status:r.status}))")
        self.assertEqual(result, {'ok': True, 'status': 200})
        self.assertNotIn('Enter initiative before joining battle', page.locator('#message').text_content())
        self.assertIn('Independent error', page.locator('#message').text_content())

    def test_old_join_failure_cannot_replace_new_scope_feedback(self):
        page, _ = self.open_page()
        held = []
        page.route('**/api/characters/c1', lambda r: held.append(r))
        page.evaluate("() => {window.pendingJoin=fetch('/api/characters/c1',{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({active:true})})}")
        page.wait_for_timeout(20)
        self.assertEqual(len(held), 1)
        self.change_scope(page)
        self.emit(page, text='New scope error')
        held[0].fulfill(status=422, json={'detail': 'Old scope rejection'})
        page.evaluate('() => window.pendingJoin.then(r=>r.status)')
        self.assertIn('New scope error', page.locator('#message').text_content())
        self.assertNotIn('Old scope rejection', page.locator('#message').text_content())

    def test_edits_during_lookup_are_preserved(self):
        page, _ = self.open_page()
        held = self.hold_lookup(page)
        page.locator('#monsterAc').fill('19')
        held.fulfill(json={'found': True, 'provider': 'D&D Beyond', 'ac': 15, 'hp': 7})
        page.evaluate('() => window.pendingLookup')
        self.assertEqual(page.locator('#monsterAc').input_value(), '19')
        self.assertEqual(page.locator('#monsterHpRangeStart').input_value(), '7')


if __name__ == '__main__':
    unittest.main()
