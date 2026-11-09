"""Full Admin/intercepted HTTP correction checks, not authenticated live-server evidence."""
import copy
import unittest
import test_admin_live_workspace as live


class SidebarCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        live.LiveWorkspaceTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        live.LiveWorkspaceTests.tearDownClass.__func__(cls)

    choose = live.LiveWorkspaceTests.choose
    open_page = live.LiveWorkspaceTests.open_page
    active_state = live.LiveWorkspaceTests.active_state

    def test_connection_compact_panels_stacked_and_log_heading_single(self):
        for width in (1440, 375):
            page, errors, mutations = self.open_page(width)
            self.active_state(page)
            self.choose(page, 'live')
            result = page.locator('#encounterFeatures').evaluate("""root => {
                const connection=root.querySelector('.et-connection');
                const boxes=[...root.querySelectorAll('.et-panel')].map(n=>n.getBoundingClientRect());
                return {basis:getComputedStyle(connection).flexBasis,
                    compact:connection.getBoundingClientRect().height<160,
                    stacked:boxes.every((b,i)=>!i || b.top>=boxes[i-1].bottom-1)};
            }""")
            self.assertEqual(result['basis'], 'auto')
            self.assertTrue(result['compact'], result)
            self.assertTrue(result['stacked'], result)
            self.assertFalse(page.locator('#liveActivityDisclosure h2').is_visible())
            for selector in ('#exportActivityLogCsv','#exportActivityLogJson','#clearActivityLog'):
                self.assertTrue(page.locator(selector).is_visible())
            self.assertEqual(errors, [])
            self.assertEqual(mutations, [])
            page.close()

    def test_connection_one_zero_unavailable_failure_and_recovery(self):
        page, errors, mutations = self.open_page()
        self.choose(page, 'live')
        summary = copy.deepcopy(self.summary)
        summary.update(display_scope_available=True, displays=[{'username':'viewer','status':'live'}])
        page.route('**/api/features', lambda route: route.fulfill(json=summary))
        def refresh(expected):
            page.locator('#featureRefresh').click()
            page.wait_for_function("text => document.querySelector('#displayConnections').textContent===text", arg=expected)
        refresh('1 display(s) connected: viewer (live)')
        summary['displays'] = []
        refresh('0 display(s) connected')
        summary['display_scope_available'] = False
        refresh('Connection status unavailable')
        summary.update(display_scope_available=True, displays=[{'username':'viewer','status':'live'}])
        refresh('1 display(s) connected: viewer (live)')
        page.route('**/api/features', lambda route: route.fulfill(status=503, json={'detail':'Unavailable'}))
        refresh('Connection status unavailable')
        page.unroute('**/api/features')
        summary.update(display_scope_available=True, displays=[{'username':'viewer','status':'live'}])
        page.route('**/api/features', lambda route: route.fulfill(json=summary))
        refresh('1 display(s) connected: viewer (live)')
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])


if __name__ == '__main__':
    unittest.main()
