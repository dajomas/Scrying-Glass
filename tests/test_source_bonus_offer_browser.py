"""Native FormData with intercepted lookup; opaque tokens are not server proof."""
import unittest
import test_monster_candidate_browser as fixtures

class SourceBonusOfferBrowserTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.CandidateBrowserTests('test_single_and_zero')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.page = self.fixture.page

    def candidate(self, value=12, **changes):
        result = dict(found=True, name='Goblin', species='Goblin', provider='D&D Beyond',
            source='MM', legacy=False, ac=15, hp='10', selection_token='selected-A',
            initiative_bonus=value, initiative_bonus_status='available',
            initiative_bonus_offer_token='opaque-offer-A')
        result.update(changes)
        return result

    def start(self, **changes):
        self.fixture.start_candidates([self.candidate(**changes)])
        self.fixture.finish()

    def payload(self):
        return self.page.evaluate("Object.fromEntries(new FormData(document.querySelector('#monsterForm')))")

    def test_blank_fill_signed_positive_zero_negative_for_both_providers(self):
        for provider in ('D&D Beyond', '5e.tools'):
            for value in (12, 0, -2):
                with self.subTest(provider=provider, value=value):
                    self.page.locator('#monsterInitiativeBonus').fill('')
                    self.start(value=value, provider=provider)
                    payload = self.payload()
                    self.assertEqual(payload['initiative_bonus'], str(value))
                    self.assertEqual(payload['selection_token'], 'selected-A')
                    self.assertEqual(payload['initiative_bonus_offer_token'], 'opaque-offer-A')

    def test_existing_values_preserved_unchecked_and_replaced_checked(self):
        for provider in ('D&D Beyond', '5e.tools'):
            for checked in (False, True):
                with self.subTest(provider=provider, checked=checked):
                    self.page.locator('#monsterSpeciesLookupOverwrite').set_checked(checked)
                    self.page.locator('#monsterAc').fill('19')
                    self.page.locator('#monsterHpRangeStart').fill('99')
                    self.page.locator('#monsterInitiativeBonus').fill('0')
                    self.start(provider=provider)
                    self.assertEqual(self.page.locator('#monsterAc').input_value(), '15' if checked else '19')
                    self.assertEqual(self.page.locator('#monsterHpRangeStart').input_value(), '10' if checked else '99')
                    self.assertEqual(self.payload()['initiative_bonus'], '12' if checked else '0')
                    self.assertEqual('initiative_bonus_offer_token' in self.payload(), checked)

    def test_unsigned_copy_is_manual(self):
        self.start(initiative_bonus_offer_token=None)
        self.assertEqual(self.payload()['initiative_bonus'], '12')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())

    def test_unavailable_and_invalid_never_fill_or_overwrite(self):
        self.page.locator('#monsterSpeciesLookupOverwrite').check()
        for status, value in [('missing', None), ('invalid', None), ('ambiguous', None),
                              ('available', '12'), ('available', 1.5), ('available', True)]:
            for current in ('', '5'):
                with self.subTest(status=status, value=value, current=current):
                    self.page.locator('#monsterInitiativeBonus').fill(current)
                    self.start(value=value, initiative_bonus_status=status)
                    self.assertEqual(self.payload()['initiative_bonus'], current)
                    self.assertNotIn('initiative_bonus_offer_token', self.payload())

    def test_manual_edit_then_revert_does_not_restore_attribution(self):
        self.start()
        self.page.locator('#monsterInitiativeBonus').fill('9')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.page.locator('#monsterInitiativeBonus').fill('12')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.assertEqual(self.payload()['selection_token'], 'selected-A')

    def test_species_reset_and_new_lookup_clear_applied_offer(self):
        self.start()
        self.page.locator('#monsterSpecies').fill('Orc')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.page.locator('#monsterSpecies').fill('Goblin')
        self.page.locator('#monsterInitiativeBonus').fill('')
        self.start()
        self.page.evaluate("document.querySelector('#monsterForm').reset()")
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.start()
        self.start(selection_token='selected-B', initiative_bonus_offer_token='opaque-offer-B')
        self.assertEqual(self.payload()['selection_token'], 'selected-B')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())

    def test_programmatic_value_mismatch_not_submitted_as_source(self):
        self.start()
        self.page.evaluate("document.querySelector('#monsterInitiativeBonus').value='99'")
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.assertEqual(self.payload()['initiative_bonus'], '99')

    def test_edits_during_chooser_preserved_including_edit_then_revert(self):
        self.page.locator('#monsterSpeciesLookupOverwrite').check()
        for revert in (False, True):
            self.page.locator('#monsterInitiativeBonus').fill('4')
            self.fixture.start_candidates([self.candidate(), self.candidate(value=7, selection_token='B')])
            self.page.evaluate("document.querySelector('#monsterAc').value='20'; document.querySelector('#monsterHpRangeStart').value='88';")
            self.page.evaluate("const b=document.querySelector('#monsterInitiativeBonus'); b.value='9'; b.dispatchEvent(new Event('input', {bubbles:true}));")
            if revert:
                self.page.evaluate("const b=document.querySelector('#monsterInitiativeBonus'); b.value='4'; b.dispatchEvent(new Event('input', {bubbles:true}));")
            self.page.get_by_role('button', name='1. Goblin', exact=False).click()
            self.fixture.finish()
            self.assertEqual(self.payload()['initiative_bonus'], '4' if revert else '9')
            self.assertEqual(self.page.locator('#monsterAc').input_value(), '20')
            self.assertEqual(self.page.locator('#monsterHpRangeStart').input_value(), '88')
            self.assertNotIn('initiative_bonus_offer_token', self.payload())
            self.page.locator('#monsterAc').fill('')
            self.page.locator('#monsterHpRangeStart').fill('')

    def test_delayed_http_edits_are_preserved(self):
        self.page.locator('#monsterSpeciesLookupOverwrite').check()
        self.page.locator('#monsterInitiativeBonus').fill('4')
        self.page.evaluate("""
            window.realFetch = window.fetch;
            window.fetch = async function(url, options) {
                if (url.startsWith('/api/monsters/lookup?')) {
                    await new Promise(resolve => {window.releaseLookup = resolve;});
                }
                return realFetch(url, options);
            };
            void 0;
        """)
        self.fixture.result = {'status': 'ok', 'candidates': [self.candidate()]}
        self.fixture.launch_lookup()
        self.page.wait_for_function('() => typeof releaseLookup === "function"')
        self.page.locator('#monsterInitiativeBonus').fill('9')
        self.page.locator('#monsterInitiativeBonus').fill('4')
        self.page.evaluate('releaseLookup()')
        self.fixture.finish()
        self.assertEqual(self.payload()['initiative_bonus'], '4')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())

    def test_cancel_species_reset_and_overwrite_change_during_chooser(self):
        for action in ('cancel', 'species', 'reset', 'overwrite'):
            with self.subTest(action=action):
                self.page.locator('#monsterSpecies').fill('Goblin')
                self.page.locator('#monsterSpeciesLookupOverwrite').uncheck()
                self.page.locator('#monsterInitiativeBonus').fill('4')
                self.fixture.start_candidates([self.candidate(), self.candidate(value=7)])
                if action == 'cancel':
                    self.page.keyboard.press('Escape')
                elif action == 'species':
                    self.page.evaluate("const s=document.querySelector('#monsterSpecies'); s.value='Orc'; s.dispatchEvent(new Event('input', {bubbles:true}));")
                elif action == 'reset':
                    self.page.evaluate("document.querySelector('#monsterForm').reset()")
                else:
                    self.page.evaluate("""const box = document.querySelector('#monsterSpeciesLookupOverwrite');
                        box.checked = true; box.dispatchEvent(new Event('change', {bubbles:true}));""")
                self.fixture.finish()
                self.assertEqual(self.payload()['selection_token'], 'manual')
                self.assertNotIn('initiative_bonus_offer_token', self.payload())
                self.assertEqual(self.payload()['initiative_bonus'], '' if action == 'reset' else '4')

    def test_selected_version_owns_bonus_and_offer(self):
        self.fixture.start_candidates([self.candidate(), self.candidate(value=7, provider='5e.tools',
            source='XMM', selection_token='selected-B', initiative_bonus_offer_token='offer-B')])
        self.page.get_by_role('button', name='2. Goblin', exact=False).click()
        self.fixture.finish()
        self.assertEqual(self.payload()['initiative_bonus'], '7')
        self.assertEqual(self.payload()['selection_token'], 'selected-B')
        self.assertEqual(self.payload()['initiative_bonus_offer_token'], 'offer-B')

if __name__ == '__main__':
    unittest.main()
