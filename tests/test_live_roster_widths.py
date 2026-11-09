"""Roster/log geometry using production Admin/assets and intercepted HTTP."""
import os
from pathlib import Path
import tempfile
import unittest
import test_admin_live_workspace as live


class FullWidthRosterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        live.LiveWorkspaceTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        live.LiveWorkspaceTests.tearDownClass.__func__(cls)

    open_page = live.LiveWorkspaceTests.open_page
    choose = live.LiveWorkspaceTests.choose
    active_state = live.LiveWorkspaceTests.active_state

    def show_rosters(self, page):
        for pane, toggle in (('characterDisplayPane','toggleCharacterDisplayPane'),
                             ('monsterDisplayPane','toggleMonsterDisplayPane')):
            if page.locator('#'+pane).evaluate('n => n.hidden'):
                page.locator('#'+toggle).click()
            self.assertTrue(page.locator('#'+pane).is_visible())

    def assert_full_width(self, page):
        result = page.evaluate("""() => {
            const main=document.querySelector('#adminScroll');
            const workspace=document.querySelector('#liveEncounterWorkspace');
            const characters=document.querySelector('#characterDisplayPane');
            const monsters=document.querySelector('#monsterDisplayPane');
            const log=document.querySelector('#activityLog').closest('section');
            const reference=log.getBoundingClientRect();
            return {aligned:[characters,monsters].every(n=>{
                const b=n.getBoundingClientRect();
                return n.parentNode===main && !workspace.contains(n) &&
                    Math.abs(b.left-reference.left)<=1 && Math.abs(b.right-reference.right)<=1 &&
                    Math.abs(b.width-reference.width)<=1;
            }),ordered:[workspace,characters,monsters,log].every((n,i,a)=>
                !i || Boolean(a[i-1].compareDocumentPosition(n)&Node.DOCUMENT_POSITION_FOLLOWING)),
                regions:['characters','monsters'].every(id=>
                    getComputedStyle(document.getElementById(id)).overflowX==='auto')};
        }""")
        self.assertTrue(result['aligned'], result)
        self.assertTrue(result['ordered'], result)
        self.assertTrue(result['regions'], result)

    def test_equal_log_edges_with_tools_open_hidden_and_after_refresh(self):
        directory=Path(os.environ.get('SG_VISUAL_ARTIFACTS', str(Path(tempfile.gettempdir())/'sg-admin-foundations')))
        directory.mkdir(parents=True,exist_ok=True)
        for width in (1440,768,375):
            with self.subTest(width=width):
                page,errors,mutations=self.open_page(width)
                self.active_state(page)
                self.choose(page,'live')
                self.show_rosters(page)
                for visible in (True,False,True):
                    if page.locator('#encounterFeatures').is_visible()!=visible:
                        page.locator('#toggleEncounterTools').click()
                    self.assert_full_width(page)
                    page.evaluate('() => load(true)')
                    self.assert_full_width(page)
                page.locator('#characterDisplayPane').scroll_into_view_if_needed()
                page.screenshot(path=str(directory/f'0096-{width}-full-width-rosters.png'))
                self.assertEqual(errors,[])
                self.assertEqual(mutations,[])
                page.close()

    def test_original_panels_preferences_and_selection_survive_view_round_trip(self):
        page,errors,mutations=self.open_page()
        self.choose(page,'preparation')
        self.show_rosters(page)
        page.locator('#selectAllMonsters').click()
        selected=page.locator('#monsters input[type=checkbox]:checked').count()
        self.assertGreater(selected,0)
        page.evaluate("""() => {
            window.rosterHomes=['characterDisplayPane','monsterDisplayPane'].map(id=>{
                const n=document.getElementById(id);return [n,n.parentNode,n.nextSibling,n.hidden];
            });
            document.querySelector('#effectName').value='Unsaved condition';
        }""")
        for key in ('live','campaign','preparation','live'):
            self.choose(page,key)
        self.assert_full_width(page)
        self.choose(page,'preparation')
        self.assertTrue(page.evaluate('rosterHomes.every(([n,p,next,h])=>n.parentNode===p&&n.nextSibling===next&&n.hidden===h)'))
        self.assertEqual(page.locator('#monsters input[type=checkbox]:checked').count(),selected)
        self.assertEqual(page.locator('#effectName').input_value(),'Unsaved condition')
        self.assertEqual(errors,[])
        self.assertEqual(mutations,[])


if __name__=='__main__':
    unittest.main()
