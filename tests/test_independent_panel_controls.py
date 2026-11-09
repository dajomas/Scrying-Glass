"""Independent workflow buttons and native Start battle using intercepted HTTP."""
import unittest
import test_admin_workflow_navigation as navigation


class IndependentPanelPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):navigation.WorkflowNavigationTests.setUpClass.__func__(cls)
    @classmethod
    def tearDownClass(cls):navigation.WorkflowNavigationTests.tearDownClass.__func__(cls)
    open_page=navigation.WorkflowNavigationTests.open_page
    choose=navigation.WorkflowNavigationTests.choose

    def set_visible(self,page,pane,button,visible):
        if page.locator('#'+pane).evaluate('n=>!n.hidden')!=visible:
            page.locator('#'+button).click()

    def test_workflow_controls_stay_available_and_panels_are_independent(self):
        for width in (1440,375):
            page,errors,mutations=self.open_page(width)
            for view,parent,child,parent_pane,child_pane,draft in [
                ('campaign','toggleCampaignPane','toggleCharacterPane','campaignInputPane','characterInputPane','#characterName'),
                ('preparation','toggleBattleSetupPane','toggleMonsterPane','battleSetupInputPane','monsterInputPane','#monsterForm [name=name]')]:
                self.choose(page,view)
                controls=[parent,child,'toggleCharacterDisplayPane']
                if view=='preparation':controls.append('toggleMonsterDisplayPane')
                for control in controls:self.assertTrue(page.locator('#'+control).is_visible())
                self.set_visible(page,parent_pane,parent,True)
                self.set_visible(page,child_pane,child,True)
                page.locator(draft).fill('Retained independent draft')
                page.locator('#'+parent).click()
                self.assertTrue(page.locator('#'+child_pane).is_visible())
                self.assertEqual(page.locator(draft).input_value(),'Retained independent draft')
                page.locator('#'+child).click()
                self.assertTrue(page.locator('#'+parent_pane).evaluate('n=>n.hidden'))
                for control in controls:self.assertTrue(page.locator('#'+control).is_visible())
                page.locator('#'+child).click();page.evaluate('() => load(true)')
                self.assertTrue(page.locator('#'+child_pane).is_visible())
                self.assertTrue(page.locator('#'+parent_pane).evaluate('n=>n.hidden'))
                self.assertEqual(page.locator(draft).input_value(),'Retained independent draft')
            self.assertEqual(errors,[]);self.assertEqual(mutations,[]);page.close()

    def test_native_start_collapses_all_panels_but_not_their_controls(self):
        page,errors,mutations=self.open_page()
        state=page.evaluate('latest')
        for item,initiative in [(state['monsters'][0],19),(state['characters'][0],12)]:
            item.update(active=True,alive=True,in_turn=False,life_state='standing',death_failures=0,initiative=initiative)
        state.update(battle_order=[],battle_round=0)
        page.route('**/api/state',lambda route:route.fulfill(json=state))
        page.evaluate('() => load(true)')
        page.evaluate('setAllHideablePanesHidden(false)')
        posts=[]
        def start(route):
            posts.append(route.request.post_data_json)
            state['battle_order']=posts[-1]['order'];state['battle_round']=1
            for item in state['monsters']+state['characters']:item['in_turn']=item['id']==state['battle_order'][0]
            route.fulfill(json={})
        page.route('**/api/battle/start',start)
        page.locator('#startBattle').click()
        page.wait_for_function("document.querySelector('#battleState').classList.contains('active')")
        self.assertEqual(len(posts),1)
        panes=['campaignInputPane','characterInputPane','battleSetupInputPane','monsterInputPane','characterDisplayPane','monsterDisplayPane']
        self.assertTrue(page.evaluate('ids=>ids.every(id=>document.getElementById(id).hidden)',panes))
        for view,controls in [('campaign',['toggleCampaignPane','toggleCharacterPane','toggleCharacterDisplayPane']),
                              ('preparation',['toggleBattleSetupPane','toggleMonsterPane','toggleCharacterDisplayPane','toggleMonsterDisplayPane'])]:
            self.choose(page,view)
            for control in controls:self.assertTrue(page.locator('#'+control).is_visible())
        page.locator('#toggleMonsterPane').click();page.evaluate('() => load(true)')
        self.assertFalse(page.locator('#monsterInputPane').evaluate('n=>n.hidden'))
        self.assertTrue(page.locator('#battleSetupInputPane').evaluate('n=>n.hidden'))
        self.assertFalse(page.locator('#encounterToolsModal').is_visible())
        # Starting again while active must collapse a manually reopened panel too.
        page.locator('#startBattle').click()
        page.wait_for_function("document.querySelector('#monsterInputPane').hidden")
        self.assertEqual(len(posts),2)
        self.assertTrue(page.evaluate('ids=>ids.every(id=>document.getElementById(id).hidden)',panes))
        page.evaluate('setAllHideablePanesHidden(false)')
        page.route('**/api/battle/start',lambda route:route.fulfill(status=422,json={'detail':'Rejected test start'}))
        page.locator('#startBattle').click()
        page.wait_for_function("document.querySelector('#message').textContent.includes('Rejected test start')")
        self.assertFalse(page.locator('#monsterInputPane').evaluate('n=>n.hidden'))
        self.assertEqual(errors,[]);self.assertEqual(mutations,[])


if __name__=='__main__':unittest.main()
