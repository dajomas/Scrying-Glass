"""Complete Admin scripts with intercepted HTTP; not authenticated live-server evidence."""
from pathlib import Path
from urllib.parse import urlsplit
import unittest
from playwright.sync_api import sync_playwright
import test_encounter_features as fixtures
from web_html.admin_html import ADMIN_HTML

ROOT = Path(__file__).resolve().parents[1]


def assert_script_inventory(test_case, scripts):
    test_case.assertEqual(len(scripts), 43)
    core = '/static/admin.js'
    character = '/static/character-edit-feedback.js?v=1'
    monster = '/static/monster-initiative-edit.js?v=1'
    for source in (core, character, monster):
        test_case.assertEqual(scripts.count(source), 1, source)
    test_case.assertLess(scripts.index(core), scripts.index(character))
    test_case.assertLess(scripts.index(character), scripts.index(monster))


class ScriptInventoryTests(unittest.TestCase):
    def valid_scripts(self):
        return ['/static/admin.js', '/static/character-edit-feedback.js?v=1',
                '/static/monster-initiative-edit.js?v=1'] + [f'/fixture-{i}.js' for i in range(40)]

    def test_accepts_exact_current_inventory(self):
        assert_script_inventory(self, self.valid_scripts())

    def test_rejects_missing_or_extra_script(self):
        for scripts in (self.valid_scripts()[:-1], self.valid_scripts() + ['/extra.js']):
            with self.subTest(count=len(scripts)), self.assertRaises(AssertionError):
                assert_script_inventory(self, scripts)

    def test_rejects_missing_or_duplicate_required_assets_at_same_total(self):
        for index in range(3):
            for duplicate in (False, True):
                scripts = self.valid_scripts()
                if duplicate:
                    scripts[-1] = scripts[index]
                else:
                    scripts[index] = '/unexpected.js'
                with self.subTest(index=index, duplicate=duplicate), self.assertRaises(AssertionError):
                    assert_script_inventory(self, scripts)

    def test_rejects_incorrect_owner_order(self):
        for left, right in ((0, 1), (1, 2)):
            scripts = self.valid_scripts()
            scripts[left], scripts[right] = scripts[right], scripts[left]
            with self.subTest(left=left, right=right), self.assertRaises(AssertionError):
                assert_script_inventory(self, scripts)

    def test_rejects_wrong_character_asset_version(self):
        scripts = self.valid_scripts()
        scripts[1] = '/static/character-edit-feedback.js?v=0'
        with self.assertRaises(AssertionError):
            assert_script_inventory(self, scripts)


class GlobalFeedbackCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def open_page(self):
        fixture = fixtures.FeatureTests(methodName='test_death_saves')
        fixture.setUp()
        try:
            snapshot, summary = fixture.c.public_state(), fixture.f.summary()
        finally:
            fixture.tearDown()
        campaign = snapshot['active_campaign_id']
        snapshot['active_setup'] = {'campaign_id': campaign, 'name': 'default'}
        snapshot['characters'][0]['initiative'] = 12
        snapshot['monsters'][0].update(life_state='dead', alive=False, active=False)
        snapshot['battle_order'] = ['c']
        apis = {
            '/api/state': snapshot, '/api/features': summary,
            '/api/campaigns': {'active': campaign, 'campaigns': [
                {'id': campaign, 'name': 'Default', 'description': '',
                 'setups': ['default'], 'last_setup': 'default'}], 'moved': []},
            '/api/setups': {'campaign': campaign, 'names': ['default']},
            '/api/me': {'username': 'dm', 'role': 'superadmin'},
            '/api/users': [{'id': 1, 'username': 'dm', 'role': 'superadmin'}],
        }
        page = self.browser.new_page(viewport={'width': 1440, 'height': 1000})
        self.addCleanup(page.close)
        page.set_default_timeout(5000)
        h = {'state': snapshot, 'replies': {}, 'writes': [], 'errors': [],
             'missing': [], 'alerts': [], 'held': [], 'hold_end': False}
        page.on('pageerror', lambda error: h['errors'].append(str(error)))
        def dialog(d):
            if d.type == 'alert':
                h['alerts'].append(d.message)
            d.accept()
        page.on('dialog', dialog)
        def route(r):
            path = urlsplit(r.request.url).path
            if path == '/':
                r.fulfill(content_type='text/html', body=ADMIN_HTML)
            elif path.startswith('/static/'):
                target = ROOT / path.lstrip('/')
                if not target.is_file():
                    h['missing'].append(path)
                    r.fulfill(status=404)
                else:
                    kind = 'text/javascript' if target.suffix == '.js' else 'text/css' if target.suffix == '.css' else 'application/octet-stream'
                    r.fulfill(content_type=kind, body=target.read_bytes())
            elif path.startswith('/api/'):
                if r.request.method != 'GET':
                    h['writes'].append({'path': path, 'method': r.request.method,
                                        'body': r.request.post_data})
                if path == '/api/battle/end' and h['hold_end']:
                    h['held'].append(r)
                    return
                status, payload = h['replies'].get(path, (200, apis.get(path, {})))
                if r.request.method != 'GET' and path not in h['replies']:
                    status, payload = 422, {'detail': 'Unexpected fixture mutation: ' + path}
                r.fulfill(status=status, json=payload)
            else:
                r.fulfill(status=404)
        page.route('**/*', route)
        page.goto('http://fixture.test/', wait_until='load')
        page.wait_for_function("typeof latest!=='undefined' && latest?.characters?.some(x=>x.id==='c') && document.querySelector('#characters [data-ca]')")
        self.assertGreater(len((ROOT/'static/admin.js').read_bytes()), 100000,
                           'Run through tools/run_split_tests.py to assemble production Admin')
        scripts = page.locator('script[src]').evaluate_all(
            "nodes => nodes.map(node => node.getAttribute('src'))")
        assert_script_inventory(self, scripts)
        self.assertEqual(h['errors'], [])
        self.assertEqual(h['missing'], [])
        self.assertEqual(h['writes'], [], 'Boot must not mutate')
        self.addCleanup(lambda: self.assertEqual(h['errors'], []))
        self.addCleanup(lambda: self.assertEqual(h['alerts'], []))
        return page, h

    def records(self, page, operation):
        return page.evaluate('op=>scryingAdminFeedback.snapshot().filter(x=>x.operation===op)', operation)

    def no_global_legacy(self, page):
        self.assertNotIn('global', page.evaluate('scryingAdminFeedback.legacyRegions()'))

    def test_end_reset_renderer_and_late_bulk_delegation(self):
        page, h = self.open_page()
        page.eval_on_selector('#monsterName', "n=>{n.value='Keep monster draft';n.dispatchEvent(new Event('input',{bubbles:true}))}")
        awaitable = "() => runBulkAction('monsters','select-dead')"
        page.evaluate(awaitable)
        self.assertEqual(page.evaluate("selectedIds('monsters')"), ['m'])
        self.assertEqual(h['writes'], [])
        h['replies']['/api/battle/end'] = (422, {'detail': 'End failed'})
        h['replies']['/api/battle/reset-all'] = (422, {'detail': 'Reset failed'})
        page.evaluate("() => document.querySelector('#endBattle').onclick()")
        page.evaluate("() => document.querySelector('#resetAll').onclick()")
        self.assertEqual(self.records(page, 'battle.end')[0]['text'], 'End failed')
        self.assertEqual(self.records(page, 'battle.reset-all')[0]['text'], 'Reset failed')
        h['replies']['/api/battle/end'] = (200, {})
        page.evaluate("() => document.querySelector('#endBattle').onclick()")
        self.assertEqual(self.records(page, 'battle.end')[0]['severity'], 'success')
        self.assertEqual(self.records(page, 'battle.reset-all')[0]['text'], 'Reset failed')
        page.evaluate('() => load(true)')
        self.assertEqual(page.locator('#monsterName').input_value(), 'Keep monster draft')
        self.assertEqual(page.evaluate("selectedIds('monsters')"), ['m'])
        self.assertEqual([x['path'] for x in h['writes']],
                         ['/api/battle/end', '/api/battle/reset-all', '/api/battle/end'])
        h['replies']['/api/monsters/refresh/preview'] = (422, {'detail': 'Preview failed'})
        page.evaluate("() => runBulkAction('monsters','refresh-source-review')")
        self.assertIn('Preview failed', page.locator('dialog.sg-refresh-review').text_content())
        self.assertEqual(self.records(page, 'battle.reset-all')[0]['text'], 'Reset failed')
        page.locator('dialog.sg-refresh-review').get_by_role('button', name='Cancel', exact=True).click()
        self.assertEqual(len(h['writes']), 4)
        self.no_global_legacy(page)

    def test_late_join_bulk_and_next_request_wrappers(self):
        page, h = self.open_page()
        h['replies']['/api/characters/c'] = (422, {'detail': 'Single Join failed'})
        h['replies']['/api/characters/bulk'] = (422, {'detail': 'Bulk Join failed'})
        page.evaluate("() => patch('characters','c',{active:true})")
        page.evaluate("updateRowSelection('characters','c',true)")
        page.evaluate("() => runBulkAction('characters','join-battle')")
        self.assertEqual(sorted(x['text'] for x in self.records(page, 'roster.join')),
                         ['Bulk Join failed', 'Single Join failed'])
        h['replies']['/api/characters/c'] = (200, {})
        page.evaluate("() => patch('characters','c',{active:true})")
        self.assertEqual([x['text'] for x in self.records(page, 'roster.join')], ['Bulk Join failed'])
        h['replies']['/api/battle/next'] = (503, {'detail': 'Next unavailable'})
        page.evaluate("() => document.querySelector('#nextBattle').onclick()")
        self.assertIn('No automatic retry', self.records(page, 'battle.next')[0]['text'])
        self.assertEqual([x['text'] for x in self.records(page, 'roster.join')], ['Bulk Join failed'])
        self.assertEqual([x['path'] for x in h['writes']],
                         ['/api/characters/c', '/api/characters/bulk', '/api/characters/c', '/api/battle/next'])
        self.assertFalse(page.locator('#nextBattle').is_disabled())
        self.no_global_legacy(page)

    def test_pending_end_cannot_publish_after_real_scope_refresh(self):
        page, h = self.open_page()
        h['hold_end'] = True
        page.evaluate("() => {window.pendingEnd=document.querySelector('#endBattle').onclick()}")
        for _ in range(500):
            if h['held']:
                break
            page.wait_for_timeout(10)
        self.assertEqual(len(h['held']), 1)
        h['state']['active_setup']['name'] = 'other'
        page.evaluate('() => load(true)')
        page.evaluate("() => {const a=scryingAdminFeedback; a.publish(a.begin({region:'global',operation:'fixture.current',target:'current',label:'Current'}),{severity:'error',text:'New scope error'})}")
        h['held'][0].fulfill(status=422, json={'detail': 'Old End rejection'})
        page.evaluate('() => window.pendingEnd')
        self.assertEqual(self.records(page, 'battle.end'), [])
        self.assertEqual(self.records(page, 'fixture.current')[0]['text'], 'New scope error')
        self.assertEqual(len(h['writes']), 1)
        self.no_global_legacy(page)

    def test_statistics_and_bundle_import_coexist_on_loaded_page(self):
        page, h = self.open_page()
        h['replies']['/api/state'] = (503, {'detail': 'Statistics unavailable'})
        page.eval_on_selector('[data-statistics="c"]', 'n=>n.click()')
        page.wait_for_function("scryingAdminFeedback.snapshot().some(x=>x.operation==='statistics.open')")
        self.assertEqual(self.records(page, 'statistics.open')[0]['text'], 'Statistics unavailable')
        del h['replies']['/api/state']
        page.eval_on_selector('[data-statistics="c"]', 'n=>n.click()')
        page.wait_for_function("!document.querySelector('#statisticsModal').hidden")
        self.assertEqual(self.records(page, 'statistics.open'), [])
        page.eval_on_selector('#statisticsClose', 'n=>n.click()')
        h['replies']['/api/battle/reset-all'] = (422, {'detail': 'Keep Reset error'})
        page.evaluate("() => document.querySelector('#resetAll').onclick()")
        h['replies']['/api/campaign-bundle'] = (200, {'name': '<Imported & campaign>'})
        page.locator('#importBundle').set_input_files({'name': 'campaign.zip', 'mimeType': 'application/zip', 'buffer': b'fixture bundle'})
        page.wait_for_function("!window.scryingEncounterToolsBusy() && scryingAdminFeedback.snapshot().some(x=>x.operation==='campaign-bundle.import')")
        self.assertEqual(self.records(page, 'campaign-bundle.import')[0]['text'],
                         'Imported <Imported & campaign>. Switch campaigns, then restore the "Imported encounter" checkpoint to resume its runtime state.')
        self.assertEqual(self.records(page, 'battle.reset-all')[0]['text'], 'Keep Reset error')
        self.assertEqual(page.locator('#message img').count(), 0)
        self.assertEqual([x['path'] for x in h['writes']], ['/api/battle/reset-all', '/api/campaign-bundle'])
        self.assertEqual(page.locator('#importBundle').input_value(), '')
        self.no_global_legacy(page)


if __name__ == '__main__':
    unittest.main()
