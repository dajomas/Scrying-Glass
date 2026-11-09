"""Battle, rosters and log retain equal widths with tools outside the workspace."""
import unittest
import test_admin_live_workspace as live


class FullWidthRosterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):live.LiveWorkspaceTests.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls):live.LiveWorkspaceTests.tearDownClass.__func__(cls)
    open_page=live.LiveWorkspaceTests.open_page
    choose=live.LiveWorkspaceTests.choose
    active_state=live.LiveWorkspaceTests.active_state

    def show_rosters(self,page):
        for pane,toggle in (('characterDisplayPane','toggleCharacterDisplayPane'),('monsterDisplayPane','toggleMonsterDisplayPane')):
            if page.locator('#'+pane).evaluate('n=>n.hidden'):page.locator('#'+toggle).click()

    def assert_full_width(self,page):
        self.assertTrue(page.evaluate("""() => {
            const main=document.querySelector('#adminScroll');
            const battle=document.querySelector('#battleInfo').closest('section');
            const c=document.querySelector('#characterDisplayPane'),m=document.querySelector('#monsterDisplayPane');
            const log=document.querySelector('#activityLog').closest('section'),r=log.getBoundingClientRect();
            return [battle,c,m].every(n=>{const b=n.getBoundingClientRect();return n.parentNode===main && Math.abs(b.left-r.left)<=1 && Math.abs(b.right-r.right)<=1;}) &&
                [battle,c,m,log].every((n,i,a)=>!i || Boolean(a[i-1].compareDocumentPosition(n)&Node.DOCUMENT_POSITION_FOLLOWING)) &&
                ['characters','monsters'].every(id=>getComputedStyle(document.getElementById(id)).overflowX==='auto');
        }"""))

    def test_widths_unchanged_by_dialog_open_close_and_refresh(self):
        for width in (1440,768,375):
            page,errors,mutations=self.open_page(width)
            self.active_state(page);self.choose(page,'live');self.show_rosters(page)
            self.assert_full_width(page)
            page.locator('#toggleEncounterTools').click()
            self.assert_full_width(page)
            page.evaluate('() => load(true)');self.assert_full_width(page)
            page.locator('#closeEncounterTools').click();self.assert_full_width(page)
            self.assertEqual(errors,[]);self.assertEqual(mutations,[]);page.close()

    def test_native_panels_and_selection_survive_view_round_trip(self):
        page,errors,mutations=self.open_page()
        self.choose(page,'preparation');self.show_rosters(page)
        page.locator('#selectAllMonsters').click()
        selected=page.locator('#monsters input[type=checkbox]:checked').count()
        page.evaluate("window.homes=['characterDisplayPane','monsterDisplayPane'].map(id=>{const n=document.getElementById(id);return [n,n.parentNode,n.nextSibling,n.hidden]})")
        for key in ('live','campaign','preparation','live'):self.choose(page,key)
        self.assert_full_width(page)
        self.choose(page,'preparation')
        self.assertTrue(page.evaluate('homes.every(([n,p,next,h])=>n.parentNode===p&&n.nextSibling===next&&n.hidden===h)'))
        self.assertEqual(page.locator('#monsters input[type=checkbox]:checked').count(),selected)
        self.assertEqual(errors,[]);self.assertEqual(mutations,[])


if __name__=='__main__':unittest.main()
