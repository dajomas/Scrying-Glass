"""SG-TODO-015 control alignment using full Admin/intercepted HTTP assets."""
import unittest
import test_battle_action_statistics as stats


class ActionAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stats.ActionStatisticsBrowserTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        stats.ActionStatisticsBrowserTests.tearDownClass.__func__(cls)

    open_page = stats.ActionStatisticsBrowserTests.open_page
    assert_summary = stats.ActionStatisticsBrowserTests.assert_summary
    pick = stats.ActionStatisticsBrowserTests.pick

    def assert_aligned(self, row):
        result = row.evaluate("""row => {
            const visible = n => n.getClientRects().length > 0;
            const rect = n => n.getBoundingClientRect();
            const labels = [...row.children].filter(n => n.tagName === 'LABEL' && visible(n));
            const controls = labels.map(n => n.querySelector('select,input:not([type=hidden])'));
            controls.push(row.querySelector('[data-remove-action-row]'));
            const boxes = controls.filter(n => n && visible(n)).map(rect);
            const critical = row.querySelector(':scope > .critical-option');
            return {
                tops: boxes.map(b => b.top), heights: boxes.map(b => b.height),
                labels: labels.map(n => rect(n).top),
                critical: !critical || !visible(critical) ||
                    Math.abs(rect(critical).top + rect(critical).height/2 - boxes[0].top - boxes[0].height/2) <= 1,
                summaries: [...row.querySelectorAll('.sg-action-stats')].filter(visible).every(n => {
                    const b=rect(n), s=rect(n.previousElementSibling), p=rect(n.parentElement);
                    return b.top >= s.bottom-1 && b.left >= p.left-1 && b.right <= p.right+1;
                })
            };
        }""")
        self.assertLessEqual(max(result['tops'])-min(result['tops']), 1, result)
        self.assertLessEqual(max(result['heights'])-min(result['heights']), 1, result)
        self.assertLessEqual(max(result['labels'])-min(result['labels']), 1, result)
        self.assertTrue(result['critical'], result)
        self.assertTrue(result['summaries'], result)

    def test_desktop_empty_selected_wrapped_and_hidden_fields(self):
        page, errors, mutations = self.open_page()
        try:
            ordinary = page.locator('#battleActionRows .battle-action-row').first
            self.assert_aligned(ordinary)
            self.pick(page, stats.TARGET, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
            self.assert_aligned(ordinary)
            page.locator('#addBattleReaction').click()
            self.pick(page, stats.SOURCE, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
            self.pick(page, stats.REACTION_TARGET, 'statsCharacter', 'HP 0 · HP MAX 12')
            self.assert_aligned(page.locator('.battle-reaction-row'))
            page.locator('#addStatisticsReduction').click()
            reduction = page.locator('.statistics-reduction-row')
            self.pick(page, '.statistics-reduction-row [data-action-target]', 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
            self.assert_aligned(reduction)
            page.evaluate("latest.monsters[0].max_hp=123456789012345; scryingLairsRender(latest)")
            ordinary.evaluate("n => n.style.width='32rem'")
            self.assert_aligned(ordinary)
            ordinary.locator('[data-action-kind]').select_option('heal')
            self.assert_aligned(ordinary)
            ordinary.locator('[data-action-kind]').select_option('buff')
            self.assert_aligned(ordinary)
            self.assertEqual(errors, [])
            self.assertEqual(mutations, [])
        finally:
            page.close()

    def test_mobile_summaries_stay_with_their_selectors(self):
        page, errors, mutations = self.open_page(375)
        try:
            self.pick(page, stats.TARGET, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
            page.locator('#addBattleReaction').click()
            self.pick(page, stats.SOURCE, 'statsMonster', 'AC 14 · HP 9 · HP MAX 20')
            self.pick(page, stats.REACTION_TARGET, 'statsCharacter', 'HP 0 · HP MAX 12')
            for row in page.locator('#battleActionRows .battle-action-row').all():
                self.assertTrue(row.evaluate("""row => {
                    const labels=[...row.children].filter(n => n.tagName==='LABEL' && n.getClientRects().length);
                    return labels.every((n,i) => {
                        const b=n.getBoundingClientRect(), next=labels[i+1]?.getBoundingClientRect();
                        return !next || b.bottom<=next.top+1;
                    }) && [...row.querySelectorAll('.sg-action-stats')].every(n => {
                        const b=n.getBoundingClientRect(), s=n.previousElementSibling.getBoundingClientRect();
                        return b.top>=s.bottom-1 && Math.abs(b.left-s.left)<=1 && b.right<=s.right+1;
                    });
                }"""))
            self.assertEqual(errors, [])
            self.assertEqual(mutations, [])
        finally:
            page.close()


if __name__ == '__main__':
    unittest.main()
