"""Revised 009.6: production Admin/assets with intercepted HTTP, not live-server evidence."""
import os
from pathlib import Path
import tempfile
import unittest
import test_admin_workflow_navigation as navigation

ROOT=Path(__file__).resolve().parents[1]


class LiveWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        navigation.WorkflowNavigationTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        navigation.WorkflowNavigationTests.tearDownClass.__func__(cls)

    choose=navigation.WorkflowNavigationTests.choose

    def open_page(self,width=1440):
        page,errors,mutations=navigation.WorkflowNavigationTests.open_page(self,width)
        page.wait_for_function("document.body.dataset.liveWorkspace==='ready'")
        return page,errors,mutations

    def active_state(self,page):
        state=page.evaluate('latest')
        monster,character=state['monsters'][0],state['characters'][0]
        monster.update(active=True,in_turn=True,hp=0,max_hp=20,initiative=19,
                       life_state='down',concentrating=True,
                       effects=[{'name':'<Poisoned>','mechanical':False}])
        character.update(active=True,in_turn=False,initiative=12)
        state.update(battle_order=[monster['id'],character['id']],battle_round=2)
        page.route('**/api/state',lambda route:route.fulfill(json=state))
        page.evaluate('() => load(true)')
        return state

    def test_full_width_no_duplicate_overview_and_dialog_geometry(self):
        directory=Path(os.environ.get('SG_VISUAL_ARTIFACTS',str(Path(tempfile.gettempdir())/'sg-admin-foundations')))
        directory.mkdir(parents=True,exist_ok=True)
        for width in (1440,375):
            page,errors,mutations=self.open_page(width)
            self.active_state(page)
            self.choose(page,'live')
            self.assertEqual(page.locator('#liveEncounterWorkspace,#liveTurnOrder,#liveCurrentTurn').count(),0)
            self.assertFalse(page.locator('#encounterToolsModal').is_visible())
            self.assertTrue(page.evaluate("!document.querySelector('#adminScroll').contains(document.querySelector('#encounterFeatures'))"))
            self.assertTrue(page.evaluate("""() => {
                const battle=document.querySelector('#battleInfo').closest('section').getBoundingClientRect();
                const log=document.querySelector('#activityLog').closest('section').getBoundingClientRect();
                return Math.abs(battle.left-log.left)<=1 && Math.abs(battle.right-log.right)<=1;
            }"""))
            page.locator('#toggleEncounterTools').click()
            self.assertTrue(page.locator('#encounterToolsModal').is_visible())
            box=page.locator('.sg-tools-dialog').bounding_box()
            self.assertGreaterEqual(box['x'],0)
            self.assertLessEqual(box['x']+box['width'],width+1)
            self.assertLessEqual(box['height'],1000*.94)
            page.screenshot(path=str(directory/f'0096-{width}-tools-dialog.png'))
            page.locator('#closeEncounterTools').click()
            page.evaluate("document.querySelector('#adminScroll').scrollTop=0")
            page.screenshot(path=str(directory/f'0096-{width}-full-width-main.png'))
            self.assertEqual(errors,[])
            self.assertEqual(mutations,[])
            page.close()

    def test_original_controls_drafts_focus_and_idempotence(self):
        page,errors,mutations=self.open_page()
        self.choose(page,'live')
        page.evaluate("window.originalTools=document.querySelector('#encounterFeatures');window.originalEffect=document.querySelector('#effectName')")
        opener=page.locator('#toggleEncounterTools')
        opener.click()
        self.assertTrue(page.locator('#closeEncounterTools').evaluate('n=>n===document.activeElement'))
        self.assertTrue(page.locator('#adminScroll').evaluate('n=>n.inert'))
        page.locator('#encounterFeatures .et-effects-panel > summary').click()
        page.locator('#effectName').fill('Unsaved condition')
        page.locator('#closeEncounterTools').focus()
        page.keyboard.press('Shift+Tab')
        self.assertTrue(page.locator('#encounterToolsModal').evaluate('n=>n.contains(document.activeElement)'))
        page.keyboard.press('Escape')
        self.assertFalse(page.locator('#encounterToolsModal').is_visible())
        self.assertFalse(page.locator('#adminScroll').evaluate('n=>n.inert'))
        self.assertTrue(opener.evaluate('n=>n===document.activeElement'))
        opener.click()
        self.assertEqual(page.locator('#effectName').input_value(),'Unsaved condition')
        self.assertTrue(page.evaluate("originalTools===document.querySelector('#encounterFeatures')&&originalEffect===document.querySelector('#effectName')"))
        page.locator('#closeEncounterTools').click()
        page.add_script_tag(content=(ROOT/'static/admin-live-workspace.js').read_text(encoding='utf-8'))
        self.assertEqual(page.locator('#encounterToolsModal').count(),1)
        self.assertEqual(page.locator('#liveActivityDisclosure').count(),1)
        self.assertEqual(errors,[])
        self.assertEqual(mutations,[])

    def test_busy_and_nested_modal_block_parent_dismissal(self):
        page,errors,mutations=self.open_page()
        self.choose(page,'live')
        page.locator('#toggleEncounterTools').click()
        page.locator('#encounterFeatures .et-health-panel > summary').click()
        held=[]
        page.route('**/api/combatants/*/features',lambda route:held.append(route))
        page.locator('#setTempHp').click()
        page.wait_for_function('window.scryingEncounterToolsBusy()')
        page.locator('#closeEncounterTools').click()
        self.assertTrue(page.locator('#encounterToolsModal').is_visible())
        page.keyboard.press('Escape')
        self.assertTrue(page.locator('#encounterToolsModal').is_visible())
        self.assertEqual(len(held),1)
        held[0].fulfill(json={})
        page.wait_for_function('!window.scryingEncounterToolsBusy()')
        page.evaluate("document.querySelector('#editModal').hidden=false")
        self.assertFalse(page.evaluate('scryingCloseEncounterTools()'))
        page.keyboard.press('Escape')
        self.assertFalse(page.locator('#editModal').is_visible())
        self.assertTrue(page.locator('#encounterToolsModal').is_visible())
        page.keyboard.press('Escape')
        self.assertFalse(page.locator('#encounterToolsModal').is_visible())
        self.assertEqual(errors,[])
        self.assertEqual(mutations,[])

    def test_native_next_and_history_behavior_retained(self):
        page,errors,mutations=self.open_page()
        state=self.active_state(page)
        self.choose(page,'live')
        posts=[]
        def advance(route):
            posts.append(route.request.method)
            state['monsters'][0]['in_turn']=False
            state['characters'][0]['in_turn']=True
            route.fulfill(json={})
        page.route('**/api/battle/next',advance)
        page.locator('#nextBattle').click()
        page.wait_for_function("id=>document.querySelector('#battleInfo [data-battle-actor]')?.dataset.battleActor===id",arg=state['characters'][0]['id'])
        self.assertEqual(posts,['POST'])
        self.assertFalse(page.locator('#encounterToolsModal').is_visible())
        page.locator('#battleInfo [data-battle-actor]').click()
        self.assertTrue(page.locator('#battleActionModal').is_visible())
        self.assertTrue(page.locator('#nextBattleActions').is_visible())
        page.locator('#closeBattleActions').click()
        page.locator('#liveActivityDisclosure > summary').focus()
        page.keyboard.press('Enter')
        self.assertFalse(page.locator('#liveActivityDisclosure').evaluate('n=>n.open'))
        page.evaluate('() => load(true)')
        self.assertFalse(page.locator('#liveActivityDisclosure').evaluate('n=>n.open'))
        self.assertEqual(errors,[])
        self.assertEqual(mutations,[])


if __name__=='__main__':unittest.main()
