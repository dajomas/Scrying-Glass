"""Connection-status correction remains covered after tools move into a dialog."""
import copy
import unittest
import test_admin_live_workspace as live


class SidebarCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):live.LiveWorkspaceTests.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls):live.LiveWorkspaceTests.tearDownClass.__func__(cls)
    choose=live.LiveWorkspaceTests.choose
    open_page=live.LiveWorkspaceTests.open_page
    active_state=live.LiveWorkspaceTests.active_state

    def test_connection_compact_in_dialog_and_log_heading_single(self):
        for width in (1440,375):
            page,errors,mutations=self.open_page(width)
            self.active_state(page);self.choose(page,'live')
            page.locator('#toggleEncounterTools').click()
            connection=page.locator('#encounterFeatures .et-connection')
            self.assertEqual(connection.evaluate('n=>getComputedStyle(n).flexBasis'),'auto')
            self.assertLess(connection.bounding_box()['height'],160)
            page.locator('#closeEncounterTools').click()
            self.assertFalse(page.locator('#liveActivityDisclosure h2').is_visible())
            for selector in ('#exportActivityLogCsv','#exportActivityLogJson','#clearActivityLog'):
                self.assertTrue(page.locator(selector).is_visible())
            self.assertEqual(errors,[]);self.assertEqual(mutations,[]);page.close()

    def test_connection_one_zero_unavailable_failure_and_recovery(self):
        page,errors,mutations=self.open_page();self.choose(page,'live')
        page.locator('#toggleEncounterTools').click()
        summary=copy.deepcopy(self.summary)
        summary.update(display_scope_available=True,displays=[{'username':'viewer','status':'live'}])
        page.route('**/api/features',lambda route:route.fulfill(json=summary))
        def refresh(expected):
            page.locator('#featureRefresh').click()
            page.wait_for_function("text=>document.querySelector('#displayConnections').textContent===text",arg=expected)
        refresh('1 display(s) connected: viewer (live)')
        summary['displays']=[];refresh('0 display(s) connected')
        summary['display_scope_available']=False;refresh('Connection status unavailable')
        summary.update(display_scope_available=True,displays=[{'username':'viewer','status':'live'}])
        refresh('1 display(s) connected: viewer (live)')
        page.route('**/api/features',lambda route:route.fulfill(status=503,json={'detail':'Unavailable'}))
        refresh('Connection status unavailable');page.unroute('**/api/features')
        page.route('**/api/features',lambda route:route.fulfill(json=summary))
        refresh('1 display(s) connected: viewer (live)')
        self.assertEqual(errors,[]);self.assertEqual(mutations,[])


if __name__=='__main__':unittest.main()
