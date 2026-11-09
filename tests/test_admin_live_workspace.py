"""SG-TODO-009.6: full Admin/assets with intercepted HTTP, not live-server evidence."""
import os
from pathlib import Path
import tempfile
import unittest
import test_admin_workflow_navigation as navigation

ROOT = Path(__file__).resolve().parents[1]


class LiveWorkspaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        navigation.WorkflowNavigationTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        navigation.WorkflowNavigationTests.tearDownClass.__func__(cls)

    choose = navigation.WorkflowNavigationTests.choose

    def open_page(self, width=1440):
        page, errors, mutations = navigation.WorkflowNavigationTests.open_page(self, width)
        page.wait_for_function("document.body.dataset.liveWorkspace === 'ready'")
        return page, errors, mutations

    def active_state(self, page):
        state = page.evaluate('latest')
        monster, character = state['monsters'][0], state['characters'][0]
        monster.update(active=True, in_turn=True, hp=0, max_hp=20, initiative=19,
                       life_state='down', concentrating=True,
                       effects=[{'name':'<Poisoned>', 'mechanical':False}])
        character.update(active=True, in_turn=False, initiative=12)
        state.update(battle_order=[monster['id'], character['id']], battle_round=2)
        page.route('**/api/state', lambda route: route.fulfill(json=state))
        page.evaluate('() => load(true)')
        return state

    def test_live_geometry_history_keyboard_and_screenshots(self):
        directory = Path(os.environ.get('SG_VISUAL_ARTIFACTS', str(Path(tempfile.gettempdir()) / 'sg-admin-foundations')))
        directory.mkdir(parents=True, exist_ok=True)
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                self.active_state(page)
                self.choose(page, 'live')
                primary = page.locator('.sg-live-primary').bounding_box()
                side = page.locator('.sg-live-tools').bounding_box()
                if width > 1000:
                    self.assertGreater(primary['width'], side['width'])
                    self.assertGreaterEqual(side['x'], primary['x'] + primary['width'] - 1)
                    self.assertAlmostEqual(side['y'], primary['y'], delta=1)
                else:
                    self.assertGreaterEqual(side['y'], primary['y'] + primary['height'] - 1)
                    self.assertTrue(page.locator('#liveEncounterWorkspace').evaluate('n => n.scrollWidth<=n.clientWidth+1'))
                self.assertTrue(page.locator('#encounterFeatures').is_visible())
                self.assertFalse(page.locator('#battleSetupInputPane').is_visible())
                self.assertTrue(page.locator('#nextBattle').is_visible())
                self.assertIn('sg-primary-action', page.locator('#nextBattle').get_attribute('class'))
                history = page.locator('#liveActivityDisclosure')
                self.assertTrue(page.locator('#activityLog').is_visible())
                history.locator(':scope > summary').focus()
                page.keyboard.press('Enter')
                self.assertFalse(history.evaluate('n => n.open'))
                page.evaluate('() => load(true)')
                self.assertFalse(history.evaluate('n => n.open'))
                page.keyboard.press('Enter')
                self.assertTrue(history.evaluate('n => n.open'))
                boundary = page.evaluate("({h:document.querySelector('#adminHeader').getBoundingClientRect().bottom,m:document.querySelector('#adminScroll').getBoundingClientRect().top})")
                self.assertAlmostEqual(boundary['h'], boundary['m'], delta=1)
                page.screenshot(path=str(directory / f'0096-{width}-live.png'))
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()

    def test_original_nodes_drafts_hidden_state_and_idempotence_survive(self):
        page, errors, mutations = self.open_page()
        page.evaluate("""() => {
            const ids=['encounterFeatures','characterDisplayPane','monsterDisplayPane','lairTools'];
            window.liveHomes=ids.map(id=>{const n=document.getElementById(id);return [n,n.parentNode,n.hidden];});
            window.liveNext=document.getElementById('nextBattle');window.liveNextHandler=liveNext.onclick;
            document.querySelector('#effectName').value='Unsaved condition';
            document.querySelector('#setupName').value='Unsaved setup';
        }""")
        for key in ('live', 'preparation', 'live', 'campaign'):
            self.choose(page, key)
        self.assertTrue(page.evaluate("liveHomes.every(([n,p,h])=>n.parentNode===p&&n.hidden===h)"))
        self.assertTrue(page.evaluate("liveNext===document.querySelector('#nextBattle')&&liveNext.onclick===liveNextHandler"))
        self.assertEqual(page.locator('#effectName').input_value(), 'Unsaved condition')
        self.assertEqual(page.locator('#setupName').input_value(), 'Unsaved setup')
        page.add_script_tag(content=(ROOT / 'static/admin-live-workspace.js').read_text(encoding='utf-8'))
        self.assertEqual(page.locator('#liveEncounterWorkspace').count(), 1)
        self.assertEqual(page.locator('#liveActivityDisclosure').count(), 1)
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])

    def test_authoritative_order_zero_effect_text_lair_and_end(self):
        page, errors, mutations = self.open_page()
        self.choose(page, 'live')
        self.assertIn('No battle order set', page.locator('#liveCurrentTurn').inner_text())
        state = self.active_state(page)
        self.assertEqual(page.locator('#liveTurnOrder > li').count(), 2)
        self.assertIn('HP 0/20', page.locator('#liveTurnOrder > li').first.inner_text())
        self.assertIn('<Poisoned>', page.locator('#liveTurnOrder > li').first.inner_text())
        self.assertEqual(page.locator('#liveTurnOrder poisoned').count(), 0)
        self.assertEqual(page.locator('#liveTurnOrder [aria-current=step]').count(), 1)
        self.assertIn(state['monsters'][0]['name'], page.locator('#liveCurrentTurn').inner_text())
        lair = {'id':'workspace-lair','name':'Lair','active':True,'in_turn':True,'visible':True,'color':'#8064a2'}
        state['monsters'][0]['in_turn'] = False
        state['lairs'] = [lair]
        state['battle_order'].insert(0, lair['id'])
        page.evaluate('() => load(true)')
        self.assertIn('No HP or AC', page.locator('#liveTurnOrder > li').first.inner_text())
        self.assertEqual(page.locator('#liveTurnOrder > li').first.get_attribute('data-combatant-id'), lair['id'])
        state.update(battle_order=[], battle_round=0)
        page.evaluate('() => load(true)')
        self.assertEqual(page.locator('#liveTurnOrder > li').count(), 0)
        self.assertIn('No battle order set', page.locator('#liveCurrentTurn').inner_text())
        self.assertEqual(page.locator('body').get_attribute('data-workflow-view'), 'live')
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])

    def test_native_next_keeps_single_request_and_battle_actions(self):
        page, errors, mutations = self.open_page()
        state = self.active_state(page)
        self.choose(page, 'live')
        posts = []
        def advance(route):
            posts.append(route.request.method)
            state['monsters'][0]['in_turn'] = False
            state['characters'][0]['in_turn'] = True
            route.fulfill(json={})
        page.route('**/api/battle/next', advance)
        page.locator('#nextBattle').click()
        page.wait_for_function("name => document.querySelector('#liveCurrentTurn').textContent.includes(name)", arg=state['characters'][0]['name'])
        self.assertEqual(posts, ['POST'])
        page.locator('#battleInfo [data-battle-actor]').click()
        self.assertTrue(page.locator('#battleActionModal').is_visible())
        self.assertTrue(page.locator('#nextBattleActions').is_visible())
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])


if __name__ == '__main__':
    unittest.main()
