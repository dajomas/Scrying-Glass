"""Rollback-safe logical review scope, plus secured ASGI retry regressions."""
import copy
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from fastapi import HTTPException
import test_monster_refresh_review as fixture
from python import scrying_glass_monster_refresh_review as refresh


class RefreshScopeRetryTests(unittest.IsolatedAsyncioTestCase):
    request = fixture.MonsterRefreshReviewTests.request
    lookup = fixture.MonsterRefreshReviewTests.lookup
    form = fixture.MonsterRefreshReviewTests.form
    snapshot = fixture.MonsterRefreshReviewTests.snapshot
    json_request = fixture.MonsterRefreshReviewTests.json_request
    seed = fixture.MonsterRefreshReviewTests.seed
    preview = fixture.MonsterRefreshReviewTests.preview
    apply = fixture.MonsterRefreshReviewTests.apply

    def setUp(self):
        fixture.MonsterRefreshReviewTests.setUp(self)

    async def test_invalid_requests_can_be_corrected_without_false_staleness(self):
        ident = await self.seed()
        review = await self.preview(ident)
        before = self.snapshot()
        original_state = self.context.STATE
        for selected in ({'other': ['ac']}, {ident: ['unknown']},
                         {ident: {'ac': 99}}, {ident: ['ac', 'ac']}):
            status, _ = await self.apply(review, selected)
            self.assertEqual(status, 422)
            self.assertEqual(self.snapshot(), before)
            self.assertIn(review['review_id'], self.context._monster_refresh_reviews)
        self.assertIsNot(self.context.STATE, original_state)
        status, _ = await self.apply(review, {ident: ['ac']})
        self.assertEqual(status, 200)
        self.assertEqual(self.context.STATE['monsters'][0]['ac'], 20)
        self.assertEqual((await self.apply(review, {ident: ['ac']}))[0], 410)

    async def test_real_state_change_after_validation_rollback_remains_stale(self):
        ident = await self.seed()
        review = await self.preview(ident)
        self.assertEqual((await self.apply(review, {ident: ['unknown']}))[0], 422)
        self.context.STATE['monsters'][0]['hp'] = 9
        before = self.snapshot()
        self.assertEqual((await self.apply(review, {ident: ['ac']}))[0], 409)
        self.assertEqual(self.snapshot(), before)

    async def test_source_configuration_change_after_rollback_remains_stale(self):
        ident = await self.seed()
        review = await self.preview(ident)
        self.assertEqual((await self.apply(review, {ident: ['unknown']}))[0], 422)
        self.context.CONFIG['display']['dndbeyond_image_lookup'] = False
        self.assertEqual((await self.apply(review, {ident: ['ac']}))[0], 409)
        self.context.hp_value_factory.assert_not_called()


class RefreshRevisionScopeTests(unittest.TestCase):
    def test_revision_change_rejects_equal_state_but_equal_copy_is_allowed(self):
        revision = Mock(return_value=7)
        context = SimpleNamespace(STATE={'active_setup': {'campaign_id': '1', 'name': 'default'}},
            CONFIG={'display': {}}, features=SimpleNamespace(store=SimpleNamespace(revision=revision)),
            active_campaign=lambda: '1', HTTPException=HTTPException)
        user = dict(id=1, username='owner', role='admin')
        with patch.object(refresh, 'actor', return_value=user):
            scope = refresh._scope(context)
            context._monster_refresh_reviews = {'token': dict(scope=scope,
                state=copy.deepcopy(context.STATE), display={}, expires=time.monotonic()+600)}
            context.STATE = copy.deepcopy(context.STATE)
            self.assertIs(refresh._review(context, 'token'), context._monster_refresh_reviews['token'])
            revision.return_value = 8
            with self.assertRaises(HTTPException) as caught:
                refresh._review(context, 'token')
            self.assertEqual(caught.exception.status_code, 409)


if __name__ == '__main__':
    unittest.main()
