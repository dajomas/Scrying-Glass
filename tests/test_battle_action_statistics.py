"""SG-TODO-015: full Admin/assets with intercepted HTTP, not live-server evidence."""
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TARGET = '#battleActionRows .battle-action-row:first-child [data-action-target]'
SOURCE = '#battleActionRows .battle-reaction-row [data-action-source]'
REACTION_TARGET = '#battleActionRows .battle-reaction-row [data-action-target]'


class ActionStatisticsSourceTests(unittest.TestCase):
    def test_assets_order_sizes_and_read_only_contract(self):
        end = (ROOT / 'templates/admin/190_document_end.html').read_text(encoding='utf-8')
        self.assertEqual(end.count('/static/battle-action-statistics.js?v=1'), 1)
        self.assertEqual(end.count('/static/battle-action-statistics.css?v=1'), 1)
        self.assertLess(end.index('/static/admin-workflow-navigation.js'), end.index('/static/battle-action-statistics.js'))
        source = (ROOT / 'static/battle-action-statistics.js').read_text(encoding='utf-8')
        for forbidden in ('fetch(', 'innerHTML', 'cloneNode', '.value =', '.disabled =', 'setInterval', 'localStorage'):
            self.assertNotIn(forbidden, source)
        for name in ('battle-action-statistics.js', 'battle-action-statistics.css'):
            self.assertLessEqual((ROOT / 'static' / name).stat().st_size, 20000)


class ActionStatisticsBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import test_monster_button_layout as rows
        cls.rows = rows.MonsterButtonLayoutTests
        cls.rows.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        cls.rows.tearDownClass.__func__(cls)

    def open_page(self, width=1440):
        page, errors, mutations = self.rows.open_page(self, width)
        page.wait_for_function("document.body.dataset.actionStats === 'ready'")
        page.evaluate("""() => {
            const m=latest.monsters[0], c=latest.characters[0];
            Object.assign(m,{active:true,alive:true,in_turn:true,ac:14,hp:9,max_hp:20});
            Object.assign(c,{active:true,alive:true,in_turn:false,hp:0,max_hp:12});
            delete c.ac;
            window.statsMonster=m.id; window.statsCharacter=c.id;
            openBattleActions(m.id);
        }""")
        page.wait_for_function("document.querySelectorAll('#battleActionRows .sg-action-stats').length === 1")
        return page, errors, mutations

    def assert_summary(self, page, selector, expected):
        page.wait_for_function("""([selector,text]) => {
            const n=document.querySelector(selector)?.nextElementSibling;
            return n?.classList.contains('sg-action-stats') && n.textContent===text && n.hidden===(text==='');
        }""", arg=[selector, expected])

    def pick(self, page, selector, variable, expected):
        page.locator(selector).select_option(page.evaluate(variable))
        self.assert_summary(page, selector, expected)

    def test_selection_zero_independent_reaction_and_reduction_rows(self):
        page, errors, mutations = self.open_page()
        self.assert_summary(page, TARGET, '')
        self.pick(page, TARGET, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
        self.pick(page, TARGET, 'statsCharacter', 'HP 0 · HP MAX 12')
        page.locator('#addBattleReaction').click()
        self.assert_summary(page, SOURCE, '')
        self.pick(page, SOURCE, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
        self.pick(page, REACTION_TARGET, 'statsCharacter', 'HP 0 · HP MAX 12')
        page.locator(TARGET).evaluate("n => {n.value='';n.dispatchEvent(new Event('change',{bubbles:true}));}")
        self.assert_summary(page, TARGET, '')
        self.assert_summary(page, SOURCE, 'AC 14 · HP 9 · HP MAX 20')
        self.assertEqual(page.get_by_role('combobox', name='Reaction source', exact=True).count(), 1)
        page.locator('#addStatisticsReduction').click()
        reduction = '#battleActionRows .statistics-reduction-row [data-action-target]'
        self.pick(page, reduction, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])

    def test_missing_invalid_zero_deleted_and_idempotence(self):
        page, errors, mutations = self.open_page()
        self.pick(page, TARGET, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
        page.evaluate("const m=latest.monsters[0];m.ac=null;m.hp=0;delete m.max_hp;scryingLairsRender(latest);")
        self.assert_summary(page, TARGET, 'HP 0')
        page.evaluate("Object.assign(latest.monsters[0],{ac:'14',hp:false,max_hp:NaN});scryingLairsRender(latest);")
        self.assert_summary(page, TARGET, '')
        page.evaluate("Object.assign(latest.monsters[0],{ac:0,hp:0,max_hp:0});scryingLairsRender(latest);")
        self.assert_summary(page, TARGET, 'AC 0 · HP 0 · HP MAX 0')
        page.add_script_tag(content=(ROOT / 'static/battle-action-statistics.js').read_text(encoding='utf-8'))
        self.assertEqual(page.locator('#battleActionRows .sg-action-stats').count(), 1)
        page.evaluate('scryingLairsRender({...latest,monsters:[]})')
        self.assert_summary(page, TARGET, '')
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])

    def test_apply_refresh_keeps_locked_draft_and_reopen_clears_summary(self):
        page, errors, mutations = self.open_page()
        self.pick(page, TARGET, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
        page.locator('#battleActionRows [data-action-amount]').fill('3')
        state = page.evaluate('latest')
        state['monsters'][0]['hp'] = 6
        posts = []
        def apply(route):
            posts.append(route.request.post_data_json)
            route.fulfill(json={'applied':1})
        page.route('**/api/battle/actions', apply)
        page.route('**/api/state', lambda route: route.fulfill(json=state))
        with page.expect_response(lambda r: r.url.endswith('/api/battle/actions')):
            page.locator('#battleActionForm button[type=submit]').click()
        page.wait_for_function("document.querySelector('#battleActionRows .battle-action-row').dataset.applied==='true' && !battleActionsApplying")
        self.assert_summary(page, TARGET, 'AC 14 · HP 6 · HP MAX 20')
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]['actor_id'], page.evaluate('statsMonster'))
        self.assertEqual(posts[0]['actions'][0]['amount'], 3)
        self.assertTrue(page.locator(TARGET).is_disabled())
        self.assertEqual(page.locator(TARGET).input_value(), page.evaluate('statsMonster'))
        self.assertEqual(page.locator('#battleActionRows [data-action-amount]').input_value(), '3')
        state['monsters'][0]['hp'] = 4
        page.evaluate('() => load(true)')
        self.assert_summary(page, TARGET, 'AC 14 · HP 4 · HP MAX 20')
        self.assertTrue(page.locator(TARGET).is_disabled())
        self.assertEqual(page.locator('#battleActionRows .sg-action-stats input').count(), 0)
        page.locator('#closeBattleActions').click()
        page.evaluate('openBattleActions(statsMonster)')
        self.assert_summary(page, TARGET, '')
        self.assertEqual(page.locator(TARGET).input_value(), '')
        self.assertEqual(len(posts), 1)
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])

    def test_scope_boundary_and_row_removal(self):
        page, errors, mutations = self.open_page()
        self.pick(page, TARGET, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
        page.evaluate("latest.active_setup={name:'other'};latest.monsters[0].hp=55;scryingLairsRender(latest);")
        self.assert_summary(page, TARGET, '')
        self.assertEqual(page.locator(TARGET).input_value(), page.evaluate('statsMonster'))
        page.locator('#closeBattleActions').click()
        page.evaluate('openBattleActions(statsMonster)')
        self.pick(page, TARGET, 'statsMonster', 'AC 14 · HP 55 · HP MAX 20')
        page.locator('#battleActionRows [data-remove-action-row]').click()
        self.assertEqual(page.locator('#battleActionRows .sg-action-stats').count(), 0)
        self.assertEqual(errors, [])
        self.assertEqual(mutations, [])

    def test_desktop_narrow_placement_accessibility_and_screenshots(self):
        directory = Path(os.environ.get('SG_VISUAL_ARTIFACTS', str(Path(tempfile.gettempdir()) / 'sg-admin-foundations')))
        directory.mkdir(parents=True, exist_ok=True)
        for width in (1440, 375):
            with self.subTest(width=width):
                page, errors, mutations = self.open_page(width)
                self.pick(page, TARGET, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
                page.locator('#addBattleReaction').click()
                self.pick(page, SOURCE, 'statsCharacter', 'HP 0 · HP MAX 12')
                self.pick(page, REACTION_TARGET, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
                for selector in (TARGET, SOURCE, REACTION_TARGET):
                    field = page.locator(selector)
                    self.assertTrue(field.evaluate("""n => {
                        const s=n.nextElementSibling,b=n.getBoundingClientRect(),r=s.getBoundingClientRect(),p=n.parentElement.getBoundingClientRect();
                        return r.top>=b.bottom-1 && r.left>=p.left-1 && r.right<=p.right+1 && r.height>0;
                    }"""))
                    ident = field.evaluate('n => n.nextElementSibling.id')
                    self.assertIn(ident, field.get_attribute('aria-describedby').split())
                    self.assertEqual(page.locator('#'+ident).get_attribute('role'), 'status')
                page.screenshot(path=str(directory / f'015-{width}-summaries.png'))
                self.assertEqual(errors, [])
                self.assertEqual(mutations, [])
                page.close()


if __name__ == '__main__':
    unittest.main()
