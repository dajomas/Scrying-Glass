"""A.3 secured ASGI/SQLite and intercepted-Chromium regressions, not live-provider acceptance."""
import copy
import unittest
from unittest.mock import patch
import test_combined_monster_lookup_application as combined
import test_monster_refresh_review_browser as browser_fixture
from python import scrying_glass_monster_refresh_review as refresh
from python import scrying_glass_monster_refresh_sources as sources
from python import scrying_glass_monster_selection as selection
from python.scrying_glass_monster_source_snapshot import FIELDS


class SoleRefreshApplicationTests(unittest.IsolatedAsyncioTestCase):
    request = combined.CombinedLookupApplicationTests.request
    form = combined.CombinedLookupApplicationTests.form
    snapshot = combined.CombinedLookupApplicationTests.snapshot
    json_request = combined.CombinedLookupApplicationTests.json_request
    lookup_combined = combined.CombinedLookupApplicationTests.lookup_combined
    create_from = combined.CombinedLookupApplicationTests.create_from
    reopen = combined.CombinedLookupApplicationTests.reopen
    setUp = combined.CombinedLookupApplicationTests.setUp

    async def identityless(self, count=1):
        candidates = await self.lookup_combined()
        ids = [(await self.create_from(candidates[0]))['id'] for _ in range(count)]
        for item in self.context.STATE['monsters']:
            for field in FIELDS:
                item.pop(field, None)
        await self.context.combatants_changed(monsters=True)
        self.context.hp_value_factory.reset_mock()
        return ids, candidates

    async def test_sole_candidate_review_is_read_only_and_only_explicit_apply_generates_hp(self):
        ids, _ = await self.identityless()
        ident = ids[0]
        c = self.context
        c.CONFIG['display']['dndbeyond_image_lookup'] = False
        before = self.snapshot()
        status, review = await self.json_request('/api/monsters/refresh/preview', {'ids': ids})
        self.assertEqual(status, 200)
        row = review['rows'][0]
        self.assertEqual(row['status'], 'resolved')
        self.assertEqual(row['source_fields']['monster_source_book'], 'XMM')
        self.assertNotIn('candidates', row)
        self.assertTrue(all(not field['checked'] for field in row['fields'].values()))
        self.assertEqual(self.snapshot(), before)
        c.hp_value_factory.assert_not_called()
        status, _ = await self.json_request('/api/monsters/refresh/apply',
            {'review_id': review['review_id'], 'selected': {ident: []}})
        self.assertEqual(status, 422)
        self.assertEqual(self.snapshot(), before)
        c.hp_value_factory.assert_not_called()
        status, _ = await self.json_request('/api/monsters/refresh/apply',
            {'review_id': review['review_id'], 'selected': {ident: ['hp', 'max_hp', 'initiative_bonus']}})
        self.assertEqual(status, 200)
        c.hp_value_factory.assert_called_once_with('10', '')
        restored = self.reopen()[0]
        self.assertEqual((restored['hp'], restored['max_hp'], restored['initiative_bonus']), (10, 10, 7))
        self.assertEqual(restored['monster_source_book'], 'XMM')
        self.assertEqual(restored['ac'], before[0]['monsters'][0]['ac'])
        self.assertEqual((await self.json_request('/api/monsters/refresh/apply',
            {'review_id': review['review_id'], 'selected': {ident: ['ac']}}))[0], 410)

    async def test_continuation_keeps_automatic_and_explicit_rows_without_refetch(self):
        ids, candidates = await self.identityless(3)
        first, second, third = ids
        before = self.snapshot()
        results = [{'status': 'ok', 'candidates': candidates[1:]},
                   {'status': 'ok', 'candidates': candidates},
                   {'status': 'ok', 'candidates': candidates}]
        with patch.object(selection, 'lookup_candidates', side_effect=results):
            status, review = await self.json_request('/api/monsters/refresh/preview', {'ids': ids})
        self.assertEqual(status, 200)
        self.assertEqual([row['status'] for row in review['rows']],
                         ['resolved', 'selection_required', 'selection_required'])
        with patch.object(selection, 'lookup_candidates', side_effect=AssertionError('No repeated lookup')):
            status, next_review = await self.json_request('/api/monsters/refresh/preview',
                {'review_id': review['review_id'], 'choices': {second: candidates[0]['selection_token']}})
        self.assertEqual(status, 200)
        self.assertEqual(next_review['rows'][0], review['rows'][0])
        self.source['ac'] = [99]
        with patch.object(sources, '_fetch_exact', wraps=sources._fetch_exact) as fetch:
            status, last = await self.json_request('/api/monsters/refresh/preview',
                {'review_id': next_review['review_id'], 'choices': {third: candidates[1]['selection_token']}})
        self.assertEqual(status, 200)
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(last['rows'][:2], next_review['rows'][:2])
        self.assertEqual(self.snapshot(), before)
        self.context.hp_value_factory.assert_not_called()
        status, _ = await self.json_request('/api/monsters/refresh/apply',
            {'review_id': last['review_id'], 'selected': {first: ['ac'], second: ['initiative_bonus']}})
        self.assertEqual(status, 200)
        by_id = {item['id']: item for item in self.context.STATE['monsters']}
        self.assertEqual(by_id[first]['ac'], 16)
        self.assertEqual(by_id[second]['initiative_bonus'], 2)
        self.assertEqual(by_id[third], before[0]['monsters'][2])

    async def test_stale_auto_response_expiry_configuration_and_scope_are_guarded(self):
        ids, _ = await self.identityless()
        self.context.CONFIG['display']['dndbeyond_image_lookup'] = False
        real = refresh.resolve_selected_sources
        def changed(*args, **kwargs):
            rows = real(*args, **kwargs)
            self.context.STATE['monsters'][0]['ac'] += 1
            return rows
        with patch.object(refresh, 'resolve_selected_sources', side_effect=changed):
            status, _ = await self.json_request('/api/monsters/refresh/preview', {'ids': ids})
        self.assertEqual(status, 409)
        self.assertFalse(getattr(self.context, '_monster_refresh_reviews', {}))
        status, review = await self.json_request('/api/monsters/refresh/preview', {'ids': ids})
        self.assertEqual(status, 200)
        for body in ({'ids': [[]]}, {'ids': ids + ids},
                     {'review_id': review['review_id'], 'choices': {'other': 'bad'}}):
            self.assertEqual((await self.json_request('/api/monsters/refresh/preview', body))[0], 422)
        self.context.CONFIG['display']['fivetools_fallback'] = False
        self.assertEqual((await self.json_request('/api/monsters/refresh/apply',
            {'review_id': review['review_id'], 'selected': {ids[0]: ['ac']}}))[0], 409)
        self.context.CONFIG['display']['fivetools_fallback'] = True
        self.context._monster_refresh_reviews[review['review_id']]['expires'] = 0
        self.assertEqual((await self.json_request('/api/monsters/refresh/preview',
            {'review_id': review['review_id'], 'choices': {}}))[0], 410)
        self.context.hp_value_factory.assert_not_called()


class SoleRefreshBrowserTests(unittest.TestCase):
    setUp = browser_fixture.RefreshReviewBrowserTests.setUp
    open = browser_fixture.RefreshReviewBrowserTests.open

    def test_automatic_row_has_no_chooser_and_selects_no_fields_at_both_widths(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                self.page.set_viewport_size({'width': width, 'height': 900})
                before = self.page.evaluate('JSON.stringify(latest)')
                self.open()
                self.assertEqual(self.page.locator('dialog select').count(), 0)
                self.assertEqual(self.page.locator('dialog input:checked').count(), 0)
                self.assertTrue(self.page.get_by_role('button', name='Apply selected changes', exact=True).is_disabled())
                self.assertEqual(self.page.evaluate('JSON.stringify(latest)'), before)
                self.page.get_by_role('button', name='Cancel', exact=True).click()
        self.assertFalse(any(url.endswith('/apply') for url, _ in self.calls))
        self.assertEqual(self.errors, [])

    def test_multiple_choice_keeps_individual_choices_on_automatic_row(self):
        self.review['rows'][1]['status'] = 'selection_required'
        self.review['rows'][1]['candidates'] = [
            dict(name='Goblin', provider='5e.tools', source=book, selection_token=book)
            for book in ('MM', 'XMM')]
        self.open()
        self.page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).check()
        self.page.get_by_role('checkbox', name='Initiative bonus for Alpha', exact=True).check()
        self.page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).uncheck()
        self.page.get_by_label('Source candidate for Beta', exact=True).select_option('1')
        self.page.get_by_role('button', name='Use candidate for Beta', exact=True).click()
        self.page.wait_for_function("document.querySelector('dialog').getAttribute('aria-busy') === 'false'")
        self.assertTrue(self.page.get_by_role('checkbox', name='Initiative bonus for Alpha', exact=True).is_checked())
        self.assertFalse(self.page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).is_checked())
        self.assertFalse(self.page.get_by_role('checkbox', name='Current HP for Alpha', exact=True).is_checked())
        self.assertFalse(any(url.endswith('/apply') for url, _ in self.calls))
        self.page.get_by_role('button', name='Apply selected changes', exact=True).click()
        self.page.wait_for_function('window.reloaded === true')
        self.assertEqual(self.calls[-1][1], {'review_id': 'review-B', 'selected': {'a': ['initiative_bonus']}})
        self.assertEqual(self.errors, [])


if __name__ == '__main__':
    unittest.main()
