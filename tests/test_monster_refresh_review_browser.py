"""Chromium refresh UI with intercepted endpoints; not authenticated browser/server acceptance."""
import copy
import json
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright
from feedback_browser_fixture import install_feedback

ROOT = Path(__file__).resolve().parents[1]


class RefreshReviewBrowserTests(unittest.TestCase):
    def setUp(self):
        browser_runtime = sync_playwright().start()
        self.addCleanup(browser_runtime.stop)
        browser = browser_runtime.chromium.launch(headless=True)
        self.addCleanup(browser.close)
        self.page = browser.new_page(viewport={'width': 1440, 'height': 900})
        self.page.set_default_timeout(5000)
        self.calls = []
        self.errors = []
        self.fail_apply = False
        self.fail_preview = False
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        def field(current, proposed, enabled=True):
            return dict(current=current, proposed=proposed, enabled=enabled,
                status='available' if enabled else 'missing', checked=False)
        self.review = dict(review_id='review-A', rows=[
            dict(id='a', status='resolved', source_fields={'monster_source_provider': 'D&D Beyond'}, fields={
                'initiative_bonus': field(2, 12), 'ac': field(10, 18),
                'max_hp': field(20, '3d8+3'), 'hp': field(4, '3d8+3')}),
            dict(id='b', status='resolved', source_fields={}, fields={
                'initiative_bonus': field(0, None, False), 'ac': field(10, 15),
                'max_hp': field(7, '10'), 'hp': field(3, '10')})])
        self.page.route('http://fixture.test/', lambda route: route.fulfill(content_type='text/html', body=
            '<select id="monsterBulkAction"><option value="">Actions</option></select><div id="monsters"></div><div id="monsterAddNotification"></div>'))
        def endpoint(route):
            payload = route.request.post_data_json
            self.calls.append((route.request.url, payload))
            if route.request.url.endswith('/apply'):
                route.fulfill(status=409 if self.fail_apply else 200,
                    json={'detail': 'Review stale'} if self.fail_apply else {'applied': payload['selected']})
            elif self.fail_preview:
                route.fulfill(status=503, json={'detail': 'Preview unavailable'})
            else:
                result = copy.deepcopy(self.review)
                if 'choices' in payload and payload['choices']:
                    result['review_id'] = 'review-B'
                    result['rows'][1].pop('candidates', None)
                    result['rows'][1]['status'] = 'resolved'
                route.fulfill(json=result)
        self.page.route('**/api/monsters/refresh/*', endpoint)
        self.page.goto('http://fixture.test/')
        install_feedback(self.page)
        self.page.add_script_tag(content="""
            let latest = {monsters: [{id:'a',name:'Alpha'}, {id:'b',name:'Beta'}]};
            const chosen = new Set();
            function selectedIds() {return [...chosen];}
            function updateRowSelection(kind,id,value) {if(value) chosen.add(id); else chosen.delete(id);}
            function setAllSelected(kind,value) {chosen.clear(); if(value) for(const m of latest.monsters) chosen.add(m.id);}
            async function runBulkAction() {throw new Error('Unexpected legacy bulk call');}
            async function request(url,options) {const response=await fetch(url,options); const data=await response.json();
                if(!response.ok) throw new Error(data.detail); return data;}
            async function load() {if(window.rejectRefresh) throw new Error('Refresh unavailable'); window.reloaded=true;}
            function paneNotification(kind,text) {window.notice=text;}
            function monsterSourceLabel(c) {return c.provider+' / '+c.source;}
        """)
        self.page.add_style_tag(content=(ROOT/'static/monster-refresh-review.css').read_text())
        for file in ('monster-refresh-selection.js', 'monster-refresh-review.js'):
            self.page.add_script_tag(content=(ROOT/'static'/file).read_text())

    def open(self):
        self.page.evaluate("setAllSelected('monsters', true); window.opening=runBulkAction('monsters','refresh-source-review'); void 0")
        self.page.get_by_role('button', name='Reload review', exact=True).wait_for()
        self.page.wait_for_function("document.querySelector('dialog').getAttribute('aria-busy') === 'false'")

    def test_disabled_without_selection_and_cancel_never_applies(self):
        self.assertTrue(self.page.locator('option[value="refresh-source-review"]').is_disabled())
        self.open()
        self.assertEqual(self.calls[0][1], {'ids': ['a', 'b']})
        self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.page.locator('dialog').count(), 0)

    def test_partial_headers_skip_disabled_cells_and_apply_explicit_fields(self):
        self.open()
        self.assertFalse(self.page.get_by_role('checkbox', name='Current HP for Alpha', exact=True).is_checked())
        self.page.get_by_role('checkbox', name='Select column Armor Class', exact=True).check()
        self.page.get_by_role('checkbox', name='Armor Class for Beta', exact=True).uncheck()
        header = self.page.get_by_role('checkbox', name='Select column Armor Class', exact=True)
        self.assertTrue(header.evaluate('node => node.indeterminate'))
        self.page.get_by_role('checkbox', name='Select column Initiative bonus', exact=True).check()
        self.assertTrue(self.page.get_by_role('checkbox', name='Initiative bonus for Beta', exact=True).is_disabled())
        self.assertEqual(len(self.calls), 1)
        self.page.get_by_role('button', name='Apply selected changes', exact=True).click()
        self.page.wait_for_function('window.reloaded === true')
        self.assertEqual(self.calls[-1][1]['selected'], {'a': ['initiative_bonus', 'ac']})
        self.assertEqual(set(self.calls[-1][1]), {'review_id', 'selected'})

    def test_narrow_cards_row_keyboard_selection_and_no_overflow(self):
        self.page.set_viewport_size({'width': 375, 'height': 900})
        self.open()
        row = self.page.get_by_role('checkbox', name='Select row Alpha', exact=True)
        row.focus()
        self.page.keyboard.press('Space')
        self.assertTrue(self.page.get_by_role('checkbox', name='Current HP for Alpha', exact=True).is_checked())
        self.assertIn('3d8+3', self.page.locator('dialog').inner_text())
        box = self.page.locator('dialog').bounding_box()
        self.assertGreaterEqual(box['x'], 0)
        self.assertLessEqual(box['x']+box['width'], 375)
        self.assertTrue(self.page.locator('dialog').evaluate('n => n.scrollWidth <= n.clientWidth+1'))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.errors, [])

    def test_candidate_resolution_preserves_other_checked_fields(self):
        self.review['rows'][1]['status'] = 'selection_required'
        self.review['rows'][1]['candidates'] = [dict(name='Goblin', provider='5e.tools', source='MM', selection_token='candidate-B')]
        self.open()
        self.page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).check()
        self.page.get_by_label('Source candidate for Beta', exact=True).select_option('0')
        self.page.get_by_role('button', name='Use candidate for Beta', exact=True).click()
        self.page.wait_for_function("document.querySelector('dialog').getAttribute('aria-busy') === 'false'")
        self.assertEqual(self.calls[-1][1], {'review_id': 'review-A', 'choices': {'b': 'candidate-B'}})
        self.assertTrue(self.page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).is_checked())
        self.page.get_by_role('button', name='Apply selected changes', exact=True).click()
        self.page.wait_for_function('window.reloaded === true')
        self.assertEqual(self.calls[-1][1]['review_id'], 'review-B')

    def test_stale_apply_requires_reload_and_does_not_repeat(self):
        self.fail_apply = True
        self.open()
        self.page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).check()
        self.page.get_by_role('button', name='Apply selected changes', exact=True).click()
        self.page.get_by_role('status').filter(has_text='Review stale').wait_for()
        self.assertTrue(self.page.get_by_role('button', name='Apply selected changes', exact=True).is_disabled())
        self.assertEqual(len([call for call in self.calls if call[0].endswith('/apply')]), 1)
        self.assertEqual(self.errors, [])

    def records(self):
        return self.page.evaluate("window.scryingAdminFeedback.snapshot()")

    def change_scope(self):
        self.assertTrue(self.page.evaluate("""() => {
          const f=window.scryingAdminFeedback;
          const sequence=f.stateRequest();
          return f.observeState({active_campaign_id:'other',active_setup:{campaign_id:'other',name:'other'}},sequence);
        }"""))

    def test_preview_error_is_local_and_keyboard_dismissal_has_safe_focus(self):
        self.fail_preview = True
        self.open()
        error = self.page.locator('#sgMonsterRefreshFeedback [data-severity="error"]')
        self.assertEqual(error.count(), 1)
        self.assertEqual(self.records()[0]['region'], 'monsterRefreshReview')
        self.assertEqual(self.page.locator('#monsterAddNotification [data-severity="error"]').count(), 0)
        button = self.page.get_by_role('button', name='Dismiss Load source review error message', exact=True)
        button.focus()
        self.page.keyboard.press('Enter')
        self.assertEqual(self.records(), [])
        self.assertTrue(self.page.get_by_role('button', name='Reload review', exact=True).evaluate('node => node === document.activeElement'))
        self.assertTrue(self.page.get_by_role('button', name='Apply selected changes', exact=True).is_disabled())
        self.assertEqual(self.errors, [])

    def test_preview_retry_preserves_independent_error_node(self):
        self.page.evaluate("""const f=window.scryingAdminFeedback;
          f.publish(f.begin({region:'monsters',operation:'independent',target:'m',label:'Independent'}),
          {severity:'error',text:'Keep this error'});
          window.independentNode=document.querySelector('#monsterAddNotification [data-severity="error"]');""")
        self.fail_preview = True
        self.open()
        self.assertEqual(len(self.records()), 2)
        self.fail_preview = False
        self.page.get_by_role('button', name='Reload review', exact=True).click()
        self.page.wait_for_function("document.querySelector('dialog').getAttribute('aria-busy') === 'false'")
        self.assertEqual([record['operation'] for record in self.records()], ['independent'])
        self.assertTrue(self.page.evaluate("independentNode === document.querySelector('#monsterAddNotification [data-severity=error]')"))
        self.assertEqual(self.errors, [])

    def test_close_reopen_reuses_mounted_root_without_old_errors(self):
        self.fail_preview = True
        self.open()
        self.page.evaluate("window.originalFeedbackRoot=document.querySelector('#sgMonsterRefreshFeedback')")
        self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.assertEqual(self.records(), [])
        self.fail_preview = False
        self.open()
        self.assertEqual(self.page.locator('#sgMonsterRefreshFeedback').count(), 1)
        self.assertTrue(self.page.evaluate("originalFeedbackRoot === document.querySelector('#sgMonsterRefreshFeedback')"))
        self.assertEqual(self.page.locator('#sgMonsterRefreshFeedback').get_attribute('data-sg-feedback-mounted'), 'true')
        self.assertEqual(self.records(), [])
        self.assertEqual(self.errors, [])

    def test_apply_refresh_failure_has_persistent_distinct_feedback_without_replay(self):
        self.open()
        self.page.evaluate('window.rejectRefresh=true')
        self.page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).check()
        self.page.get_by_role('button', name='Apply selected changes', exact=True).click()
        self.page.wait_for_function("window.scryingAdminFeedback.snapshot().some(r=>r.operation==='monster.refresh.apply.refresh')")
        self.assertEqual(self.page.locator('dialog').count(), 0)
        self.assertEqual({record['severity'] for record in self.records()}, {'success', 'error'})
        self.page.wait_for_timeout(3100)
        self.assertEqual(len(self.records()), 1)
        self.assertEqual(self.records()[0]['operation'], 'monster.refresh.apply.refresh')
        self.assertIn('do not apply again', self.records()[0]['text'])
        self.assertEqual(len([call for call in self.calls if call[0].endswith('/apply')]), 1)
        self.assertEqual(self.errors, [])

    def test_old_apply_completion_cannot_close_dialog_or_reload_new_scope(self):
        self.open()
        self.page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).check()
        self.page.add_script_tag(content="""
          const savedRefreshRequest=request;
          request=async function(url,options) {
            if(url.endsWith('/apply')) {
              window.applyStarted=true;
              await new Promise(resolve=>{window.releaseApply=resolve;});
            }
            return savedRefreshRequest(url,options);
          };
        """)
        self.page.get_by_role('button', name='Apply selected changes', exact=True).click()
        self.page.wait_for_function('window.applyStarted === true')
        self.change_scope()
        self.page.evaluate('window.releaseApply(); void 0')
        self.page.wait_for_function("document.querySelector('dialog').getAttribute('aria-busy') === 'false'")
        self.assertEqual(self.page.locator('dialog').count(), 1)
        self.assertFalse(self.page.evaluate('Boolean(window.reloaded)'))
        self.assertEqual(self.records(), [])
        self.assertIn('encounter changed', self.page.locator('dialog').inner_text())
        self.assertEqual(len([call for call in self.calls if call[0].endswith('/apply')]), 1)
        self.assertEqual(self.errors, [])

    def test_candidate_continuation_cannot_send_after_scope_transition(self):
        self.review['rows'][1]['status'] = 'selection_required'
        self.review['rows'][1]['candidates'] = [dict(name='Goblin', provider='5e.tools', source='MM', selection_token='candidate-B')]
        self.open()
        self.page.get_by_label('Source candidate for Beta', exact=True).select_option('0')
        self.change_scope()
        self.page.get_by_role('button', name='Use candidate for Beta', exact=True).click()
        self.assertEqual(len(self.calls), 1)
        self.assertTrue(self.page.get_by_role('button', name='Apply selected changes', exact=True).is_disabled())
        self.assertIn('encounter changed', self.page.locator('dialog').inner_text())
        self.assertEqual(self.errors, [])

    def test_failed_continuation_disables_stale_candidate_controls(self):
        self.review['rows'][1]['status'] = 'selection_required'
        self.review['rows'][1]['candidates'] = [dict(name='Goblin', provider='5e.tools', source='MM', selection_token='candidate-B')]
        self.open()
        self.page.get_by_label('Source candidate for Beta', exact=True).select_option('0')
        self.fail_preview = True
        self.page.get_by_role('button', name='Use candidate for Beta', exact=True).click()
        self.page.wait_for_function("document.querySelector('dialog').getAttribute('aria-busy') === 'false'")
        self.assertTrue(self.page.get_by_role('button', name='Use candidate for Beta', exact=True).is_disabled())
        self.assertTrue(self.page.get_by_label('Source candidate for Beta', exact=True).is_disabled())
        self.assertEqual(self.records()[0]['operation'], 'monster.refresh.preview')
        self.assertEqual(self.errors, [])


if __name__ == '__main__':
    unittest.main()
