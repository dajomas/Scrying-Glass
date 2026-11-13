"""SG-TODO-009.5 navigation, with 009.6 on-demand tools dialog contract."""
import copy
import os
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]


class WorkflowNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows=rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls):cls.rows.tearDownClass.__func__(cls)

    def open_page(self,width=1440):
        page,errors,mutations=self.rows.open_page(self,width,workflow=None)
        page.wait_for_function("document.body.dataset.workflowNavigation==='ready'")
        self.assertEqual(page.locator('body').get_attribute('data-workflow-view'),'campaign')
        return page,errors,mutations

    def choose(self,page,key):
        page.locator('#adminWorkflow-'+key).click()
        self.assertEqual(page.locator('body').get_attribute('data-workflow-view'),key)

    def test_view_mapping_preserves_native_visibility_and_nodes(self):
        for width in (1440,375):
            page,errors,mutations=self.open_page(width)
            page.evaluate("window.originalCharacterForm=document.querySelector('#characterForm')")
            original=page.evaluate("Object.fromEntries([...document.querySelectorAll('.pane,#encounterFeatures')].map(n=>[n.id,n.hidden]))")
            for key,excluded in [('campaign','monsterInputPane'),('preparation','campaignInputPane'),('live','battleSetupInputPane')]:
                self.choose(page,key)
                self.assertFalse(page.locator('#'+excluded).is_visible())
                self.assertEqual(page.locator('#'+excluded).get_attribute('data-workflow-excluded'),'true')
                self.assertTrue(page.locator('#startBattle').is_visible())
                self.assertTrue(page.locator('#adminContextCampaign').is_visible())
                self.assertTrue(page.locator('#adminContextSetup').is_visible())
                self.assertEqual(original,page.evaluate("Object.fromEntries([...document.querySelectorAll('.pane,#encounterFeatures')].map(n=>[n.id,n.hidden]))"))
                self.assertTrue(page.evaluate("originalCharacterForm===document.querySelector('#characterForm')"))
            self.assertTrue(page.locator('#activityLog').is_visible())
            self.choose(page,'campaign');self.assertFalse(page.locator('#activityLog').is_visible())
            self.assertEqual(errors,[]);self.assertEqual(mutations,[]);page.close()

    def test_drafts_selection_and_manual_collapse_survive_view_changes(self):
        page,errors,mutations=self.open_page()
        for selector in ('#toggleCampaignPane','#toggleCharacterPane'):
            if page.locator(selector).get_attribute('aria-expanded')=='false':page.locator(selector).click()
        page.locator('#characterName').fill('Unsaved character')
        self.choose(page,'preparation')
        if page.locator('#toggleBattleSetupPane').get_attribute('aria-expanded')=='false':page.locator('#toggleBattleSetupPane').click()
        page.locator('#setupName').fill('Unsaved setup')
        page.locator('#selectAllMonsters').click()
        selected=page.locator('#monsters input[type=checkbox]:checked').count()
        self.assertGreater(selected,0)
        page.locator('#toggleMonsterDisplayPane').click();self.choose(page,'live')
        self.assertTrue(page.locator('#monsterDisplayPane').evaluate('n=>n.hidden'))
        self.choose(page,'campaign');self.assertEqual(page.locator('#characterName').input_value(),'Unsaved character')
        self.choose(page,'preparation');self.assertEqual(page.locator('#setupName').input_value(),'Unsaved setup')
        self.assertEqual(page.locator('#monsters input[type=checkbox]:checked').count(),selected)
        page.locator('#toggleMonsterDisplayPane').click();self.assertTrue(page.locator('#monsters').is_visible())
        self.assertEqual(errors,[]);self.assertEqual(mutations,[])

    def test_keyboard_tabs_roving_focus_and_idempotence(self):
        page,errors,mutations=self.open_page(375)
        page.locator('#adminWorkflow-campaign').focus()
        for key,expected in [('ArrowRight','preparation'),('End','live'),('ArrowRight','campaign'),('ArrowLeft','live'),('Home','campaign')]:
            page.keyboard.press(key);tab=page.locator('#adminWorkflow-'+expected)
            self.assertEqual(tab.get_attribute('aria-selected'),'true')
            self.assertTrue(tab.evaluate('n=>n===document.activeElement'))
            self.assertEqual(page.locator('#adminWorkflowTabs [tabindex="0"]').count(),1)
            self.assertEqual(page.locator('#adminScroll').get_attribute('aria-labelledby'),'adminWorkflow-'+expected)
            self.assertTrue(tab.evaluate('n=>{const b=n.getBoundingClientRect();return b.left>=0&&b.right<=innerWidth+1}'))
        page.add_script_tag(content=(ROOT/'static/admin-workflow-navigation.js').read_text(encoding='utf-8'))
        self.assertEqual(page.locator('#adminWorkflowTabs').count(),1)
        self.assertEqual(page.locator('#adminWorkflowTabs [role=tab]').count(),3)
        self.assertEqual(errors,[]);self.assertEqual(mutations,[])

    def test_refresh_and_battle_transitions_do_not_open_tools_or_steal_tab(self):
        for width in (1440,375):
            page,errors,mutations=self.open_page(width)
            state=copy.deepcopy(self.snapshot);state.update(battle_round=0,battle_order=[])
            page.route('**/api/state',lambda route:route.fulfill(json=state))
            page.evaluate('() => load(true)');self.choose(page,'live')
            self.assertFalse(page.locator('#encounterToolsModal').is_visible())
            state['battle_round']=1;page.evaluate('() => load(true)')
            self.assertFalse(page.locator('#encounterToolsModal').is_visible())
            page.locator('#toggleEncounterTools').click()
            self.assertTrue(page.locator('#encounterToolsModal').is_visible())
            state['battle_round']=2;page.evaluate('() => load(true)')
            self.assertTrue(page.locator('#encounterToolsModal').is_visible())
            page.keyboard.press('Escape')
            state['battle_round']=3;page.evaluate('() => load(true)')
            self.assertFalse(page.locator('#encounterToolsModal').is_visible())
            self.choose(page,'preparation')
            self.assertFalse(page.locator('#toggleEncounterTools').is_visible())
            state['battle_round']=0;page.evaluate('() => load(true)')
            self.assertEqual(page.locator('body').get_attribute('data-workflow-view'),'preparation')
            self.choose(page,'live');self.assertFalse(page.locator('#encounterToolsModal').is_visible())
            self.assertEqual(errors,[]);self.assertEqual(mutations,[]);page.close()

    def test_lair_gate_remains_independent_and_header_boundary(self):
        directory=Path(os.environ.get('SG_VISUAL_ARTIFACTS',str(Path(tempfile.gettempdir())/'sg-admin-foundations')))
        directory.mkdir(parents=True,exist_ok=True)
        for width in (1440,375):
            page,errors,mutations=self.open_page(width)
            for key in ('campaign','preparation','live'):
                self.choose(page,key);self.assertFalse(page.locator('#lairTools').is_visible())
                boundary=page.evaluate("({h:document.querySelector('#adminHeader').getBoundingClientRect().bottom,m:document.querySelector('#adminScroll').getBoundingClientRect().top,height:document.querySelector('#adminScroll').clientHeight})")
                self.assertAlmostEqual(boundary['h'],boundary['m'],delta=1)
                self.assertGreater(boundary['height'],0)
                page.screenshot(path=str(directory/f'0095-{width}-{key}.png'))
            self.assertEqual(errors,[]);self.assertEqual(mutations,[]);page.close()


if __name__=='__main__':unittest.main()
