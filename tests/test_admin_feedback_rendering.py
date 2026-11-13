# Step-2 real Chromium fixtures, not full-Admin or live-server verification.
from pathlib import Path
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class FeedbackRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        try:
            cls.browser = cls.playwright.chromium.launch(headless=True)
        except Exception:
            cls.playwright.stop()
            raise

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def page(self, width=800):
        page = self.browser.new_page(viewport={'width': width, 'height': 700})
        self.addCleanup(page.close)
        page.set_default_timeout(3000)
        page.set_content('''<!doctype html><html lang="en"><style>
            body{font:16px sans-serif;margin:8px}#adminHeader{width:100%}
            button{font:inherit}input{max-width:90%}
            </style><header id="adminHeader"><button id="fallback">Encounter actions</button>
            <p id="global" role="status" aria-live="polite"></p></header>
            <main><label>Draft<input id="draft" value="Retained draft"></label>
            <p id="pane" role="status" aria-live="polite"> </p>
            <p id="viewer" role="status" aria-live="polite"></p></main></html>''')
        page.add_style_tag(content=(ROOT/'static/admin-feedback.css').read_text())
        for name in ['admin-feedback-controller.js','admin-feedback-view.js']:
            page.add_script_tag(content=(ROOT/'static'/name).read_text())
        page.evaluate('''() => {
            let now=0, serial=0;
            const timers=new Map(); window.oldTimerCallbacks=[];
            window.controller=ScryingFeedback.createController({
                setTimeout(fn,ms){let id=++serial;timers.set(id,{fn,at:now+ms});oldTimerCallbacks.push(fn);return id},
                clearTimeout(id){timers.delete(id)}
            });
            controller.setScope('encounter','campaign-a/setup-a');
            controller.setScope('viewer','selected-campaign-z');
            window.views={};
            for(const region of ['global','pane','viewer']) views[region]=ScryingFeedbackView.mountView({
                controller,root:document.getElementById(region),region,
                focusFallback:()=>document.getElementById('fallback')
            });
            window.ticket=(operation='edit',target='m1',region='pane',extra={})=>controller.begin({
                lane:'encounter',scope:'campaign-a/setup-a',operation,target,region,
                placement:region==='global'?'global':'pane',label:operation,...extra
            });
            window.advance=ms=>{
                const until=now+ms;
                while(true){const t=[...timers].filter(([,x])=>x.at<=until).sort((a,b)=>a[1].at-b[1].at)[0];
                    if(!t)break;now=t[1].at;timers.delete(t[0]);t[1].fn()}
                now=until;
            };
        }''')
        return page

    def publish(self, page, operation='edit', severity='error', text='Action failed', region='pane', target='m1'):
        return page.evaluate('''x=>controller.publish(ticket(x.operation,x.target,x.region),
            {severity:x.severity,text:x.text})''',dict(operation=operation,target=target,region=region,severity=severity,text=text))

    def test_explicit_severity_named_native_dismiss_and_single_live_region(self):
        page=self.page()
        self.publish(page)
        self.assertEqual(page.locator('#pane').get_attribute('role'),'status')
        self.assertEqual(page.locator('#pane').get_attribute('aria-live'),'polite')
        self.assertEqual(page.locator('#pane').get_attribute('aria-atomic'),'false')
        self.assertEqual(page.locator('#pane [role], #pane [aria-live]').count(),0)
        self.assertEqual(page.get_by_role('button',name='Dismiss edit error message').count(),1)
        self.assertEqual(page.locator('#pane .sg-feedback-text').text_content(),'Error: Action failed')

    def test_only_success_expires_at_approved_deadlines(self):
        page=self.page()
        self.publish(page,severity='success',text='Pane saved')
        self.publish(page,operation='global-save',severity='success',text='Global saved',region='global')
        self.publish(page,operation='other-error',text='Persistent error')
        page.evaluate('advance(2999)')
        self.assertEqual(page.locator('.sg-feedback-record').count(),3)
        page.evaluate('advance(1)')
        self.assertEqual(page.locator('#pane .sg-feedback-record').count(),1)
        self.assertEqual(page.locator('#global .sg-feedback-record').count(),1)
        page.evaluate('advance(2000)')
        self.assertTrue(page.locator('#global').is_hidden())
        self.assertEqual(page.locator('#pane .sg-feedback-record').count(),1)

    def test_retry_resolves_only_related_error(self):
        page=self.page()
        self.publish(page,operation='edit',text='Edit failed')
        self.publish(page,operation='create',text='Create failed')
        self.publish(page,operation='edit',severity='success',text='Edit saved')
        self.assertIn('Create failed',page.locator('#pane').text_content())
        self.assertNotIn('Edit failed',page.locator('#pane').text_content())
        page.evaluate("controller.resolve(ticket('create'))")
        self.assertNotIn('Create failed',page.locator('#pane').text_content())

    def test_adding_or_expiring_feedback_does_not_steal_draft_focus(self):
        page=self.page()
        page.locator('#draft').focus()
        self.publish(page,severity='success',text='Saved')
        self.assertTrue(page.locator('#draft').evaluate('n=>n===document.activeElement'))
        page.evaluate('advance(3000)')
        self.assertTrue(page.locator('#draft').evaluate('n=>n===document.activeElement'))
        self.assertEqual(page.locator('#draft').input_value(),'Retained draft')

    def test_enter_dismisses_last_record_and_restores_explicit_fallback(self):
        page=self.page()
        self.publish(page)
        page.locator('#pane button').focus()
        page.keyboard.press('Enter')
        self.assertTrue(page.locator('#pane').is_hidden())
        self.assertTrue(page.locator('#fallback').evaluate('n=>n===document.activeElement'))

    def test_space_dismiss_moves_to_next_record_without_rebuilding_it(self):
        page=self.page()
        self.publish(page,operation='first')
        self.publish(page,operation='second')
        page.evaluate("window.retained=document.querySelectorAll('#pane button')[1]")
        page.locator('#pane button').first.focus()
        page.keyboard.press('Space')
        self.assertTrue(page.evaluate('retained===document.activeElement'))
        self.assertEqual(page.locator('#pane button').count(),1)

    def test_expiry_of_focused_success_has_deterministic_focus_recovery(self):
        page=self.page()
        self.publish(page,severity='success')
        page.locator('#pane button').focus()
        page.evaluate('advance(3000)')
        self.assertTrue(page.locator('#fallback').evaluate('n=>n===document.activeElement'))

    def test_unrelated_updates_leave_existing_error_dom_untouched(self):
        page=self.page()
        self.publish(page)
        page.evaluate('''() => {
            window.kept=document.querySelector('#pane .sg-feedback-record'); window.edits=0;
            new MutationObserver(ms=>edits+=ms.length).observe(kept,{subtree:true,childList:true,characterData:true});
        }''')
        self.publish(page,operation='other',severity='success',text='Other success')
        self.publish(page,operation='global',severity='success',text='Global success',region='global')
        page.evaluate('advance(3000)')
        self.assertEqual(page.evaluate('edits'),0)
        self.assertTrue(page.evaluate("kept===document.querySelector('#pane .sg-feedback-record')"))

    def test_html_is_literal_text_and_not_executable_markup(self):
        page=self.page()
        self.publish(page,text='<img src=x onerror="window.injected=1"><script>bad()</script>')
        self.assertEqual(page.locator('#pane img, #pane script').count(),0)
        self.assertIn('<img',page.locator('#pane .sg-feedback-text').text_content())
        self.assertIsNone(page.evaluate('window.injected'))

    def test_scope_transition_blocks_stale_response_and_old_timer(self):
        page=self.page()
        self.publish(page,severity='success')
        page.evaluate("window.stale=ticket('pending');controller.setScope('encounter','campaign-b/setup-b')")
        page.evaluate("controller.publish(ticket('current','m1','pane',{scope:'campaign-b/setup-b'}),{severity:'error',text:'Current error'})")
        self.assertFalse(page.evaluate("controller.publish(stale,{severity:'error',text:'Stale error'})"))
        page.evaluate('oldTimerCallbacks[0]()')
        self.assertIn('Current error',page.locator('#pane').text_content())
        self.assertNotIn('Stale error',page.locator('#pane').text_content())

    def test_viewer_scope_is_not_active_encounter_scope(self):
        page=self.page()
        page.evaluate("controller.publish(ticket('grants.save','campaign-z','viewer',{lane:'viewer',scope:'selected-campaign-z'}),{severity:'error',text:'Viewer save failed'})")
        page.evaluate("controller.setScope('encounter','different encounter')")
        self.assertIn('Viewer save failed',page.locator('#viewer').text_content())

    def test_hidden_and_unmount_lifecycle_preserves_live_attributes(self):
        page=self.page()
        self.assertTrue(page.locator('#pane').is_hidden())
        self.publish(page)
        page.evaluate('views.pane.destroy()')
        self.assertEqual(page.locator('#pane').get_attribute('aria-live'),'polite')
        self.assertIsNone(page.locator('#pane').get_attribute('aria-atomic'))
        self.publish(page,operation='later')
        self.assertEqual(page.locator('#pane .sg-feedback-record').count(),0)

    def test_duplicate_mount_is_rejected_without_duplicate_controls(self):
        page=self.page()
        result=page.evaluate('''() => {
            try {ScryingFeedbackView.mountView({controller,root:document.getElementById('pane'),region:'pane',focusFallback:()=>document.getElementById('fallback')});return false}
            catch{return true}
        }''')
        self.assertTrue(result)
        self.publish(page)
        self.assertEqual(page.locator('#pane button').count(),1)

    def test_header_feedback_wraps_and_scrolls_locally_at_narrow_width(self):
        page=self.page(320)
        for index in range(8):
            self.publish(page,operation=f'error-{index}',text='long-unbroken-value-'*12,region='global')
        metrics=page.locator('#global').evaluate('''n=>({height:n.clientHeight,total:n.scrollHeight,
            width:n.clientWidth,scrollWidth:n.scrollWidth,overflow:getComputedStyle(n).overflowY})''')
        self.assertEqual(metrics['overflow'],'auto')
        self.assertGreater(metrics['total'],metrics['height'])
        self.assertLessEqual(metrics['scrollWidth'],metrics['width']+1)
        page.locator('#global button').last.focus()
        self.assertGreater(page.locator('#global').evaluate('n=>n.scrollTop'),0)
        self.assertLessEqual(page.evaluate('document.documentElement.scrollWidth'),320)


if __name__=='__main__':
    unittest.main()
