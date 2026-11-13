# SG-TODO-009.7 Deliverable 2. Loaded Admin with intercepted HTTP, not live-server evidence.
# Background-poll connection warning (persistent, deduplicated, recovery resolves only its own
# identity) and near-field validation association (aria-invalid, aria-describedby, adjacent hint,
# re-association after re-render, clearing on resolution/dismissal).
import unittest
import test_admin_global_feedback_composition as composed

FIELD = """sel => { const n = document.querySelector(sel); if (!n) return null;
  const ids = (n.getAttribute('aria-describedby') || '').split(/\\s+/).filter(Boolean);
  const hints = ids.map(id => document.getElementById(id)).filter(Boolean);
  return {invalid: n.getAttribute('aria-invalid'), hints: hints.map(h => h.textContent),
          adjacent: hints.map(h => n.nextElementSibling === h), live: hints.map(h => h.closest('[aria-live]') !== null)}; }"""


class AdminDeliverable2CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        composed.GlobalFeedbackCompositionTests.setUpClass.__func__(cls)

    @classmethod
    def tearDownClass(cls):
        composed.GlobalFeedbackCompositionTests.tearDownClass.__func__(cls)

    open_page = composed.GlobalFeedbackCompositionTests.open_page
    records = composed.GlobalFeedbackCompositionTests.records

    def field(self, page, selector):
        return page.evaluate(FIELD, selector)

    def test_raw_roll_validation_is_associated_with_the_monster_input(self):
        page, h = self.open_page()
        selector = 'input[data-mi="m"]'
        self.assertEqual(self.field(page, selector), {'invalid': None, 'hints': [], 'adjacent': [], 'live': []})
        page.eval_on_selector(selector, "n => { n.value = '1.5'; n.dispatchEvent(new Event('change', {bubbles: true})); }")
        record = self.records(page, 'monster.raw-roll.validation')[0]
        self.assertEqual(record['field'], selector)
        name = page.evaluate("latest.monsters.find(x => x.id === 'm').name")
        self.assertTrue(record['text'].startswith(name + ': '))
        state = self.field(page, selector)
        self.assertEqual(state, {'invalid': 'true', 'hints': [record['text']], 'adjacent': [True], 'live': [False]})
        # A roster re-render replaces the input; the persistent record re-associates the new node.
        page.evaluate('() => load(true)')
        page.wait_for_function("document.querySelector('input[data-mi=\"m\"]').getAttribute('aria-invalid') === 'true'")
        self.assertEqual(self.field(page, selector)['hints'], [record['text']])
        self.assertEqual(page.locator('.sg-field-error').count(), 1)
        # Matching valid input resolves the validation and restores the control.
        h['replies']['/api/monsters/m'] = (422, {'detail': 'Fixture rejection'})
        page.eval_on_selector(selector, "n => { n.value = ''; n.dispatchEvent(new Event('change', {bubbles: true})); }")
        page.wait_for_function("!scryingAdminFeedback.snapshot().some(r => r.operation === 'monster.raw-roll.validation')")
        self.assertEqual(self.field(page, selector), {'invalid': None, 'hints': [], 'adjacent': [], 'live': []})
        self.assertEqual(page.locator('.sg-field-error').count(), 0)

    def test_blocked_join_is_associated_and_dismissal_restores_the_input(self):
        page, _ = self.open_page()
        page.evaluate("() => { const m = latest.monsters.find(x => x.id === 'm'); m.initiative = null; m.active = false; }")
        page.evaluate("() => document.querySelector('button[data-ma=\"m\"]').click()")
        record = self.records(page, 'roster.join')[0]
        self.assertEqual(record['field'], 'input[data-mi="m"]')
        self.assertEqual(self.field(page, 'input[data-mi="m"]')['invalid'], 'true')
        page.locator('#message').get_by_role('button', name='Dismiss Join battle error message').click()
        self.assertEqual(self.records(page, 'roster.join'), [])
        self.assertEqual(self.field(page, 'input[data-mi="m"]')['invalid'], None)

    def test_setup_name_validation_marks_the_name_field_and_keeps_prior_attributes(self):
        page, _ = self.open_page()
        page.eval_on_selector('#setupName', "n => { n.value = ''; n.setAttribute('aria-describedby', 'setupSelect'); }")
        page.evaluate("() => document.querySelector('#newSetup').onclick()")
        state = self.field(page, '#setupName')
        self.assertEqual(state['invalid'], 'true')
        self.assertEqual(state['hints'][1:], ['Enter a unique battle setup name before creating it.'])
        page.eval_on_selector('#setupName', "n => { n.value = 'Fresh setup'; }")
        page.evaluate("() => document.querySelector('#newSetup').onclick()")
        page.wait_for_function("!scryingAdminFeedback.snapshot().some(r => r.operation === 'setup.new.validation')")
        self.assertIsNone(page.get_attribute('#setupName', 'aria-invalid'))
        self.assertEqual(page.get_attribute('#setupName', 'aria-describedby'), 'setupSelect')

    def test_poll_connection_loss_is_one_persistent_warning_and_recovery_keeps_other_errors(self):
        page, _ = self.open_page()
        page.evaluate("""() => { const f = scryingAdminFeedback;
            f.publish(f.begin({region: 'global', operation: 'battle.next', target: 'battle', label: 'Next'}),
                      {severity: 'error', text: 'Unrelated error'}); }""")
        page.route('**/api/features', lambda r: r.abort())
        page.wait_for_function("scryingAdminFeedback.snapshot().some(r => r.operation === 'connection.poll')", timeout=8000)
        first = self.records(page, 'connection.poll')
        self.assertEqual([(r['severity'], r['lane'], r['region']) for r in first], [('warning', 'page', 'global')])
        self.assertIn('Warning: Connection to the server was lost', page.locator('#message').text_content())
        self.assertEqual(page.get_attribute('#message', 'aria-live'), 'polite')
        # Two more failing polls: same record, one row, no new announcement node.
        page.wait_for_timeout(6500)
        again = self.records(page, 'connection.poll')
        self.assertEqual([r['id'] for r in again], [first[0]['id']])
        self.assertEqual(page.locator('#message .sg-feedback-record[data-severity="warning"]').count(), 1)
        self.assertEqual(page.locator('#featureNotice').text_content(), '')
        page.unroute('**/api/features')
        page.wait_for_function("scryingAdminFeedback.snapshot().some(r => r.operation === 'connection.poll' && r.severity === 'success')", timeout=8000)
        self.assertEqual(self.records(page, 'connection.poll')[0]['text'], 'Connection to the server restored.')
        self.assertEqual(self.records(page, 'battle.next')[0]['text'], 'Unrelated error')
        self.assertEqual(page.locator('#message .sg-feedback-record[data-severity="warning"]').count(), 0)


if __name__ == '__main__':
    unittest.main()
