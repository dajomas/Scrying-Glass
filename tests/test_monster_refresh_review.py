"""Secured ASGI refresh review/apply with real SQLite; provider resolution is mocked."""
import asyncio
import copy
import json
import unittest
from unittest.mock import patch
import test_source_bonus_offer_acceptance as creation
from python import scrying_glass_monster_refresh_review as refresh
from python.scrying_glass_monster_refresh_sources import proposed_fields


class MonsterRefreshReviewTests(unittest.IsolatedAsyncioTestCase):
    request = creation.SourceBonusOfferAcceptanceTests.request
    lookup = creation.SourceBonusOfferAcceptanceTests.lookup
    form = creation.SourceBonusOfferAcceptanceTests.form
    snapshot = creation.SourceBonusOfferAcceptanceTests.snapshot

    def setUp(self):
        creation.SourceBonusOfferAcceptanceTests.setUp(self)
        refresh.install_monster_refresh(self.context, self.app)

    async def json_request(self, path, body, *, session='owner-session', origin='http://fixture.test'):
        data = json.dumps(body).encode()
        headers = [(b'host', b'fixture.test'), (b'content-type', b'application/json')]
        if session is not None:
            headers.append((b'cookie', ('admin-test='+session).encode()))
        headers.append((b'origin', origin.encode()))
        scope = dict(type='http', asgi={'version': '3.0'}, http_version='1.1', method='POST',
            scheme='http', path=path, raw_path=path.encode(), query_string=b'', root_path='',
            headers=headers, client=('127.0.0.1', 1234), server=('fixture.test', 80))
        messages = []
        sent = False
        async def receive():
            nonlocal sent
            if not sent:
                sent = True
                return dict(type='http.request', body=data, more_body=False)
            return dict(type='http.disconnect')
        async def send(message):
            messages.append(message)
        await asyncio.wait_for(self.app(scope, receive, send), 10)
        return (next(item['status'] for item in messages if item['type'] == 'http.response.start'),
                json.loads(b''.join(item.get('body', b'') for item in messages if item['type'] == 'http.response.body')))

    async def seed(self, *, roll=None, total=19):
        candidate = await self.lookup()
        status, created = await self.request('POST', '/api/monsters', fields=self.form(candidate))
        self.assertEqual(status, 200)
        ident = created[0]['id']
        item = self.context.STATE['monsters'][0]
        item.update(initiative_roll=roll, initiative=total)
        await self.context.combatants_changed(monsters=True)
        self.context.hp_value_factory.reset_mock()
        return ident

    async def preview(self, ident):
        def resolve(context, roster, ids, **kwargs):
            return [dict(id=key, status='resolved', source_fields={
                name: value for name, value in next(item for item in roster if item['id'] == key).items()
                if name.startswith('monster_source_')}, fields=proposed_fields(
                    next(item for item in roster if item['id'] == key),
                    dict(ac=20, hp='10', hp_source='average', initiative_bonus=3,
                         initiative_bonus_status='available'))) for key in ids]
        before = self.snapshot()
        with patch.object(refresh, 'resolve_selected_sources', side_effect=resolve):
            status, review = await self.json_request('/api/monsters/refresh/preview', {'ids': [ident]})
        self.assertEqual(status, 200)
        self.assertEqual(self.snapshot(), before)
        self.context.hp_value_factory.assert_not_called()
        return review

    async def apply(self, review, selected, **kwargs):
        return await self.json_request('/api/monsters/refresh/apply',
            dict(review_id=review['review_id'], selected=selected), **kwargs)

    async def test_bonus_apply_preserves_legacy_total_and_is_single_use(self):
        ident = await self.seed()
        review = await self.preview(ident)
        status, _ = await self.apply(review, {ident: ['initiative_bonus']})
        self.assertEqual(status, 200)
        item = self.context.STATE['monsters'][0]
        self.assertEqual((item['initiative_bonus'], item['initiative_bonus_origin'], item['initiative']), (3, 'source', 19))
        self.assertEqual((await self.apply(review, {ident: ['initiative_bonus']}))[0], 410)

    async def test_retained_raw_recalculates_and_hp_is_generated_once_only_on_apply(self):
        ident = await self.seed(roll=16, total=28)
        review = await self.preview(ident)
        status, _ = await self.apply(review, {ident: ['initiative_bonus', 'hp', 'max_hp']})
        self.assertEqual(status, 200)
        self.context.hp_value_factory.assert_called_once_with('10', '')
        item = self.context.STATE['monsters'][0]
        self.assertEqual((item['initiative'], item['hp'], item['max_hp']), (19, 10, 10))
        self.context.load_state()
        self.assertEqual(self.context.STATE['monsters'][0]['initiative_bonus_origin'], 'source')

    async def test_stale_changed_deleted_and_expired_reviews_are_rejected(self):
        ident = await self.seed()
        review = await self.preview(ident)
        self.context.STATE['monsters'][0]['hp'] = 9
        self.assertEqual((await self.apply(review, {ident: ['ac']}))[0], 409)
        self.context.STATE['monsters'].clear()
        self.assertEqual((await self.apply(review, {ident: ['ac']}))[0], 409)
        self.context._monster_refresh_reviews[review['review_id']]['expires'] = 0
        self.assertEqual((await self.apply(review, {ident: ['ac']}))[0], 410)

    async def test_anonymous_client_cross_origin_and_other_user_are_rejected(self):
        ident = await self.seed()
        review = await self.preview(ident)
        before = self.snapshot()
        for options, code in (({'session': None}, 401), ({'session': 'viewer-session'}, 403),
                              ({'origin': 'http://evil.test'}, 403)):
            self.assertEqual((await self.apply(review, {ident: ['ac']}, **options))[0], code)
        # Permit the second admin campaign access to reach the user-bound review guard.
        with self.context.STORAGE.transaction():
            self.context.STORAGE.connection.execute("UPDATE users SET role='superadmin' WHERE username='outsider'")
        self.context.SESSIONS['outsider-session']['role'] = 'superadmin'
        self.assertEqual((await self.apply(review, {ident: ['ac']}, session='outsider-session'))[0], 403)
        self.assertEqual(self.context.STATE, before[0])

    async def test_unknown_rows_fields_and_client_values_are_rejected(self):
        ident = await self.seed()
        review = await self.preview(ident)
        for selected in ({'other': ['ac']}, {ident: ['unknown']}, {ident: {'ac': 99}}, {ident: ['ac', 'ac']}):
            self.assertEqual((await self.apply(review, selected))[0], 422)
        status, _ = await self.json_request('/api/monsters/refresh/apply',
            dict(review_id=review['review_id'], selected={ident: ['ac']}, ac=99))
        self.assertEqual(status, 422)
        self.context.hp_value_factory.assert_not_called()

    async def test_unavailable_field_cannot_overwrite_assigned_bonus(self):
        ident = await self.seed()
        review = await self.preview(ident)
        stored = self.context._monster_refresh_reviews[review['review_id']]
        stored['rows'][0]['fields']['initiative_bonus'].update(enabled=False, status='missing', proposed=None)
        self.assertEqual((await self.apply(review, {ident: ['initiative_bonus']}))[0], 422)
        self.assertEqual(self.context.STATE['monsters'][0]['initiative_bonus'], 12)

    async def test_persistence_failure_rolls_back_and_consumed_token_cannot_replay(self):
        ident = await self.seed()
        review = await self.preview(ident)
        before = self.snapshot()
        real = self.context.combatants_changed
        async def fail(**kwargs):
            await real(**kwargs)
            raise RuntimeError('fixture persistence failure')
        with patch.object(self.context, 'combatants_changed', side_effect=fail):
            with self.assertRaisesRegex(RuntimeError, 'fixture persistence failure'):
                await self.apply(review, {ident: ['ac']})
        self.assertEqual(self.snapshot(), before)
        self.assertEqual((await self.apply(review, {ident: ['ac']}))[0], 410)

    async def test_preview_update_cannot_expand_original_selection(self):
        ident = await self.seed()
        review = await self.preview(ident)
        status, _ = await self.json_request('/api/monsters/refresh/preview',
            dict(review_id=review['review_id'], ids=[ident, 'other']))
        self.assertEqual(status, 422)


if __name__ == '__main__':
    unittest.main()
