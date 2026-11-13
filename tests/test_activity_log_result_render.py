# SG-TODO-019. Loaded production Admin with intercepted HTTP, not live-server evidence.
# Entries are produced by the real battle handler and loggers, then rendered by the
# unchanged production renderActivityLog into the Activity log table.
import unittest
import test_activity_log_result_details as details
import test_admin_global_feedback_composition as composed

ROWS = """() => [...document.querySelectorAll('#activityLog tr')].filter(tr => tr.querySelector('td')).map(tr =>
  [...tr.querySelectorAll('td')].map(td => td.textContent.trim()))"""


class ActivityLogResultRenderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Real handlers use asyncio.run, so produce entries before Playwright owns the loop.
        cls.entries = cls.produced_entries()
        composed.GlobalFeedbackCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        composed.GlobalFeedbackCompositionTests.tearDownClass.__func__(cls)

    open_page = composed.GlobalFeedbackCompositionTests.open_page

    @staticmethod
    def produced_entries():
        producer = details.ProducerTests(methodName='test_battle_damage_and_heal_rows_name_each_target_with_result')
        producer.setUp()
        try:
            producer.add_second_goblin(); start = len(producer.log())
            producer.submit([dict(target_id='m', action='damage', amount=5),
                             dict(target_id='m2', action='damage', amount=2)])
            producer.update('characters', -6)
            return producer.log()[start:]
        finally:
            producer.tearDown()

    def test_multiple_affected_units_render_distinguishable_detail_lines(self):
        page, _ = self.open_page()
        page.evaluate('entries => renderActivityLog(entries)', self.entries)
        rows = page.evaluate(ROWS)
        # Newest first; columns: time, actor, actor state, target, target state, action, amount, details.
        self.assertEqual([(r[3], r[5], r[6], r[7]) for r in rows], [
            ('Cleric', 'damage', '6', 'Cleric: HP 20 → 14/20'),
            ('Goblin - 2', 'damage', '2', 'Goblin - 2: HP 12 → 10/12'),
            ('Goblin - 1', 'damage', '5', 'Goblin - 1: HP 12 → 7/12')])
        self.assertEqual(len({r[7] for r in rows}), 3)

    def test_details_are_rendered_as_text(self):
        page, _ = self.open_page()
        page.evaluate("renderActivityLog([{action:'damage',amount:1,target_combatant:'<b>X</b>',note:'<img src=x onerror=alert(1)>: HP 2 → 1/2'}])")
        self.assertEqual(page.locator('#activityLog tbody td.activity-log-details').inner_text(),
                         '<img src=x onerror=alert(1)>: HP 2 → 1/2')
        self.assertEqual(page.locator('#activityLog img').count(), 0)


if __name__ == '__main__': unittest.main()
