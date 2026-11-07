"""Native FormData with intercepted lookup; tokens are opaque fixtures, not server proof."""
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

    def payload(self):
        return self.page.evaluate("Object.fromEntries(new FormData(document.querySelector('#monsterForm')))")

    def test_explicit_copy_submits_signed_positive_zero_negative_offers(self):
        for value in (12, 0, -2):
            with self.subTest(value=value):
                self.start(value=value)
                self.assertNotIn('initiative_bonus_offer_token', self.payload())
                self.assertIn('server validation', self.fixture.review().inner_text())
                self.fixture.finish(review_action='apply')
                payload = self.payload()
                self.assertEqual(payload['initiative_bonus'], str(value))
                self.assertEqual(payload['selection_token'], 'selected-A')
                self.assertEqual(payload['initiative_bonus_offer_token'], 'opaque-offer-A')
        self.assertEqual(self.fixture.errors, [])

    def test_keep_cancel_and_unsigned_copy_never_submit_offer(self):
        for action in ('keep', 'cancel'):
            self.start()
            self.fixture.finish(review_action=action)
            self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.start(initiative_bonus_offer_token=None)
        self.assertIn('editable manual value', self.fixture.review().inner_text())
        self.fixture.finish(review_action='apply')
        self.assertEqual(self.payload()['initiative_bonus'], '12')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.assertEqual(self.fixture.errors, [])

    def test_manual_edit_then_revert_does_not_restore_source_attribution(self):
        self.start()
        self.fixture.finish(review_action='apply')
        self.page.locator('#monsterInitiativeBonus').fill('9')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.page.locator('#monsterInitiativeBonus').fill('12')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.assertEqual(self.payload()['selection_token'], 'selected-A')

    def test_species_reset_and_new_lookup_clear_applied_offer(self):
        self.start()
        self.fixture.finish(review_action='apply')
        self.page.locator('#monsterSpecies').fill('Orc')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.page.locator('#monsterSpecies').fill('Goblin')
        self.start()
        self.fixture.finish(review_action='apply')
        self.page.evaluate("document.querySelector('#monsterForm').reset()")
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.start()
        self.fixture.finish(review_action='apply')
        self.start(selection_token='selected-B', initiative_bonus_offer_token='opaque-offer-B')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.fixture.finish(review_action='keep')
        self.assertEqual(self.payload()['selection_token'], 'selected-B')
        self.assertNotIn('initiative_bonus_offer_token', self.payload())

    def test_programmatic_value_mismatch_is_not_submitted_as_source(self):
        self.start()
        self.fixture.finish(review_action='apply')
        self.page.evaluate("document.querySelector('#monsterInitiativeBonus').value='99'")
        self.assertNotIn('initiative_bonus_offer_token', self.payload())
        self.assertEqual(self.payload()['initiative_bonus'], '99')


if __name__ == '__main__':
    unittest.main()
