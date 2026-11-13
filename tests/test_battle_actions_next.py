"""Chromium interaction tests with production action helpers and mocked transport.

Backend turn/round/effect rules remain covered by existing server tests; this
fixture verifies composition, not a new turn engine or live authenticated server.
"""
from pathlib import Path
import re
import unittest
from playwright.sync_api import sync_playwright
from feedback_browser_fixture import install_feedback

ROOT = Path(__file__).resolve().parents[1]

class BattleActionsNextTests(unittest.TestCase):
    def setUp(self):
        p = sync_playwright().start()
        self.addCleanup(p.stop)
        browser = p.chromium.launch(headless=True)
        self.addCleanup(browser.close)
        self.page = browser.new_page()
        self.page.set_default_timeout(4000)
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        markup = (ROOT / 'templates/admin/180_battle_action_modal.html').read_text(encoding='utf-8')
        markup = re.sub(r'<script\b[^>]*>.*?</script>|<link\b[^>]*>', '', markup, flags=re.S)
        self.page.set_content('<button id="nextBattle">Next</button><p id="message" role="status" aria-live="polite"></p>' + markup)
        install_feedback(self.page)
        source = (ROOT / 'static/admin.js').read_text(encoding='utf-8')
        start = source.index('function activeBattleTargets()')
        end = source.index("document.addEventListener('click', async event => {", start)
        self.page.add_script_tag(content='''
            let latest, battleActionActorId = null, battleActionsApplying = false, battleStatisticsToken = null;
            const battleActionModal = document.querySelector('#battleActionModal');
            const battleActionRows = document.querySelector('#battleActionRows');
            const battleActionForm = document.querySelector('#battleActionForm');
            const message = (text, options) => window.scryingAdminFeedback.deliver('global', text, options);
            function observeFixtureState(state) {
                const feedback = window.scryingAdminFeedback;
                const sequence = feedback.stateRequest();
                if (!feedback.observeState(state, sequence)) throw new Error('Invalid fixture encounter scope');
                return state;
            }
            const esc = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
            window.posts = []; window.opens = []; window.failNext = false; window.failRefresh = false;
            window.holdNext = false; window.holdApply = false; window.switchScope = false;
            const participant = (id, turn) => ({id, name:id, active:true, alive:true,
                in_turn:turn, hp:10, max_hp:10, temp_hp:0});
            window.serverState = {active_campaign_id:'campaign', active_setup:{campaign_id:'campaign',name:'setup'},
                battle_round:1, statistics_token:'token-1', lairs:[],
                monsters:[participant('a',true),participant('b',false)], characters:[]};
            latest = observeFixtureState(structuredClone(window.serverState));
            async function request(url, options={}) {
                if (url === '/api/state') return observeFixtureState(structuredClone(window.serverState));
                if (url === '/api/battle/actions') {
                    window.posts.push({url, body:JSON.parse(options.body)});
                    if (window.holdApply) await new Promise(resolve => {window.releaseApply=resolve;});
                    return {applied:1};
                }
                if (url === '/api/battle/next') {
                    window.posts.push({url});
                    if (window.holdNext) await new Promise(resolve => {window.releaseNext=resolve;});
                    const state = window.serverState;
                    const all = [...state.monsters,...state.characters,...state.lairs];
                    all.forEach(item => {item.in_turn = item.id === window.nextId;});
                    state.battle_round = window.nextRound || state.battle_round;
                    state.statistics_token = 'token-next';
                    if (window.switchScope) state.active_setup = {campaign_id:'campaign',name:'other'};
                    if (window.failNext) throw new Error('Response lost');
                    return {current:all.find(item => item.in_turn) || null};
                }
                throw new Error('Unexpected request: ' + url);
            }
            async function load() {
                if (window.failRefresh) throw new Error('Refresh offline');
                latest = observeFixtureState(structuredClone(window.serverState));
            }
            window.scryingOpenLairAction = id => {window.opens.push(id);};
            window.nextId = 'b';
        ''' + source[start:end])
        self.page.add_script_tag(content='''
            const originalOpen = openBattleActions;
            openBattleActions = id => {window.opens.push('normal:' + id); return originalOpen(id);};
            openBattleActions('a'); window.opens = [];
        ''')
        self.page.add_script_tag(content=(ROOT / 'static/battle-actions-next.js').read_text(encoding='utf-8'))

    def start_next(self):
        self.page.evaluate("window.operation = document.querySelector('#nextBattleActions').onclick(); void 0")

    def finish(self):
        self.page.evaluate('window.operation')
        self.assertEqual(self.errors, [])

    def next_posts(self):
        return self.page.evaluate("window.posts.filter(p => p.url === '/api/battle/next').length")

    def test_discards_all_rows_and_opens_fresh_next_actor(self):
        self.page.evaluate("""addBattleActionRow(true); addStatisticsReductionRow();
            document.querySelector('[data-action-critical]').checked = true;
            document.querySelectorAll('.battle-action-row')[0].dataset.applied = 'true';""")
        self.start_next()
        self.finish()
        self.assertEqual(self.next_posts(), 1)
        self.assertEqual(self.page.evaluate('window.posts.length'), 1)
        self.assertEqual(self.page.evaluate('battleActionActorId'), 'b')
        self.assertEqual(self.page.evaluate('battleStatisticsToken'), 'token-next')
        self.assertEqual(self.page.locator('.battle-action-row').count(), 1)
        self.assertEqual(self.page.locator('[data-action-target]').input_value(), '')
        self.assertFalse(self.page.locator('[data-action-critical]').is_checked())
        self.assertEqual(self.page.locator('[data-action-source]').count(), 0)
        self.assertEqual(self.page.locator('[data-action-stat]').count(), 0)
        self.assertIsNone(self.page.locator('.battle-action-row').get_attribute('data-applied'))

    def test_double_click_and_main_next_do_not_overlap(self):
        self.page.evaluate('window.holdNext = true')
        self.start_next()
        self.page.wait_for_function('typeof window.releaseNext === "function"')
        self.page.evaluate("document.querySelector('#nextBattleActions').onclick(); document.querySelector('#nextBattle').onclick(); void 0")
        self.assertEqual(self.next_posts(), 1)
        self.page.evaluate('window.releaseNext(); void 0')
        self.finish()
        self.assertEqual(self.next_posts(), 1)

    def test_apply_in_flight_blocks_next(self):
        self.page.evaluate("""window.holdApply = true;
            document.querySelector('[data-action-target]').value = 'b';
            window.applyOperation = battleActionForm.onsubmit({preventDefault(){}}); void 0;""")
        self.page.wait_for_function('typeof window.releaseApply === "function"')
        self.start_next()
        self.finish()
        self.assertEqual(self.next_posts(), 0)
        self.page.evaluate('window.releaseApply(); void 0')
        self.page.evaluate('window.applyOperation')
        self.assertEqual(self.page.locator('.battle-action-row').get_attribute('data-applied'), 'true')

    def test_start_of_turn_apply_refresh_blocks_next(self):
        self.page.evaluate("document.querySelector('#battleTurnEffectsForm button[type=submit]').disabled = true")
        self.start_next()
        self.finish()
        self.assertEqual(self.next_posts(), 0)
        self.assertFalse(self.page.locator('#battleActionModal').evaluate('node => node.hidden'))

    def test_next_blocks_action_submission(self):
        self.page.evaluate('window.holdNext = true')
        self.start_next()
        self.page.wait_for_function('typeof window.releaseNext === "function"')
        self.assertTrue(self.page.evaluate("""!battleActionForm.dispatchEvent(new Event('submit',
            {bubbles:true,cancelable:true}))"""))
        self.assertEqual(self.page.evaluate('window.posts.length'), 1)
        self.page.evaluate('window.releaseNext(); void 0')
        self.finish()

    def test_round_wrap_and_lair_use_authoritative_normal_open(self):
        self.page.evaluate("""window.serverState.lairs = [{id:'lair',name:'Lair',active:true,in_turn:false}];
            window.nextId = 'lair'; window.nextRound = 2;""")
        self.start_next()
        self.finish()
        self.assertEqual(self.page.evaluate('latest.battle_round'), 2)
        self.assertEqual(self.page.evaluate('window.opens'), ['normal:lair','lair'])
        self.assertTrue(self.page.locator('#battleActionModal').evaluate('node => node.hidden'))

    def test_no_next_participant_leaves_modal_closed(self):
        self.page.evaluate('window.nextId = null')
        self.start_next()
        self.finish()
        self.assertTrue(self.page.locator('#battleActionModal').evaluate('node => node.hidden'))
        self.assertEqual(self.page.evaluate('window.opens'), [])
        self.assertIn('No active participant', self.page.locator('#message').inner_text())

    def test_uncertain_response_reconciles_without_retry_or_reopen(self):
        self.page.evaluate('window.failNext = true')
        self.start_next()
        self.finish()
        self.assertEqual(self.next_posts(), 1)
        self.assertEqual(self.page.evaluate('latest.monsters.find(x => x.in_turn).id'), 'b')
        self.assertTrue(self.page.locator('#battleActionModal').evaluate('node => node.hidden'))
        self.assertIn('uncertain', self.page.locator('#message').inner_text())

    def test_refresh_failure_keeps_closed_without_retry(self):
        self.page.evaluate('window.failRefresh = true')
        self.start_next()
        self.finish()
        self.assertEqual(self.next_posts(), 1)
        self.assertTrue(self.page.locator('#battleActionModal').evaluate('node => node.hidden'))
        self.assertIn('Refresh before continuing', self.page.locator('#message').inner_text())

    def test_scope_change_during_advance_does_not_reopen(self):
        self.page.evaluate('window.switchScope = true')
        self.start_next()
        self.finish()
        self.assertEqual(self.next_posts(), 1)
        self.assertEqual(self.page.evaluate('window.opens'), [])
        self.assertTrue(self.page.locator('#battleActionModal').evaluate('node => node.hidden'))

    def test_stale_actor_before_post_does_not_advance(self):
        self.page.evaluate("window.serverState.monsters.forEach(x => {x.in_turn = x.id === 'b';})")
        self.start_next()
        self.finish()
        self.assertEqual(self.next_posts(), 0)
        self.assertIn('Encounter or turn changed', self.page.locator('#message').inner_text())

    def test_main_next_keeps_modal_closed(self):
        self.page.evaluate("closeBattleActions(); window.operation = document.querySelector('#nextBattle').onclick(); void 0")
        self.finish()
        self.assertEqual(self.next_posts(), 1)
        self.assertEqual(self.page.evaluate('window.opens'), [])
        self.assertTrue(self.page.locator('#battleActionModal').evaluate('node => node.hidden'))

    def test_real_feedback_dependencies_and_scope_retirement(self):
        self.assertTrue(self.page.evaluate("Boolean(window.scryingAdminFeedback && window.ScryingFeedback && window.ScryingFeedbackView)"))
        self.page.evaluate("""() => {
            const feedback = window.scryingAdminFeedback;
            const ticket = feedback.begin({region:'global',operation:'fixture.next.dependencies',target:'fixture',label:'Fixture feedback'});
            feedback.publish(ticket,{severity:'error',text:'Fixture dependency check'});
        }""")
        self.assertIn('Fixture dependency check', self.page.locator('#message').inner_text())
        self.assertEqual(self.page.evaluate("JSON.parse(scryingAdminFeedback.snapshot()[0].scope)"), ['campaign','campaign','setup'])
        self.page.evaluate("window.serverState.active_setup.name='other'; load(true)")
        self.assertEqual(self.page.evaluate('scryingAdminFeedback.snapshot().length'), 0)
        self.assertEqual(self.page.evaluate('window.posts.length'), 0)
        self.assertEqual(self.errors, [])

if __name__ == '__main__':
    unittest.main()
