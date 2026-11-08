"""Production route/auth/transaction/persistence composition with real SQLite.

Sessions are pre-seeded, not obtained via login. HP/image/provider operations are
mocked. Storage reopen is tested, not a new OS process or browser-to-server flow.
"""
import asyncio
import copy
import json
import tempfile
import time
import unittest
from pathlib import Path
from urllib.parse import urlencode
from unittest.mock import Mock, patch
from fastapi import FastAPI, HTTPException, UploadFile
from python import scrying_glass_api_admin as api
from python import scrying_glass_monster_selection as selection
from python.scrying_glass_campaign_ownership import ownership
from python.scrying_glass_service_auth import AuthService
from python.scrying_glass_service_images import ImagesService
from python.scrying_glass_source_bonus_offer import issue_bonus_offer
import test_sqlite_storage as storage_fixture


class SourceBonusOfferAcceptanceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.context = storage_fixture.context(self.directory)
        self.addCleanup(lambda: self.context.STORAGE.close())
        c = self.context
        c.CONFIG = copy.deepcopy(c.CONFIG)
        c.CONFIG['display'].update(dndbeyond_image_lookup=True, fivetools_fallback=False)
        c.import_legacy_storage()
        c.HTTPException = HTTPException
        c.UploadFile = UploadFile
        c.ADMIN_SESSION_COOKIE = 'admin-test'
        c.SESSIONS = {}
        with c.STORAGE.transaction():
            for name, role in (('owner', 'admin'), ('outsider', 'admin'), ('viewer', 'client')):
                c.STORAGE.connection.execute(
                    'INSERT INTO users(username,role,password_hash) VALUES (?,?,?)',
                    (name, role, 'fixture-unused-no-password-login'))
                c.SESSIONS[name+'-session'] = dict(username=name, role=role)
        auth = AuthService(c)
        c.require, c.user = auth.require, auth.user
        ownership(c).initialize()
        with c.STORAGE.transaction():
            ownership(c).reassign(c.active_campaign(), {'owner_user_id': str(c.user('owner')['id'])})
        images = ImagesService(c)
        c.make_monster = Mock(wraps=images.make_monster)
        c.hp_value_factory = Mock(return_value=lambda: 10)
        c.dnd_image = Mock(return_value=None)
        c.save_image = Mock(return_value='/media/fixture.png')
        self.app = FastAPI()
        instance = object.__new__(api.AdminAPI)
        instance.context, instance.app = c, self.app
        routes = tuple(row for row in api.ADMIN_ROUTES if row[0] in {
            '/api/monsters/lookup', '/api/monsters'})
        with patch.object(api, 'ADMIN_ROUTES', routes):
            instance.register_routes()
        self.candidate = dict(found=True, species='Goblin', name='Goblin', provider='D&D Beyond',
            source_url='https://www.dndbeyond.com/monsters/example', legacy=False,
            image_url=None, ac=15, hp='10', initiative_bonus=12,
            initiative_bonus_status='available')

    async def request(self, method, path, *, fields=None, query='', session='owner-session',
                      origin='http://fixture.test'):
        body = urlencode(fields or {}).encode()
        headers = [(b'host', b'fixture.test')]
        if session is not None:
            headers.append((b'cookie', ('admin-test='+session).encode()))
        if origin is not None:
            headers.append((b'origin', origin.encode()))
        if method == 'POST':
            headers.extend([(b'content-type', b'application/x-www-form-urlencoded'),
                            (b'content-length', str(len(body)).encode())])
        scope = dict(type='http', asgi={'version': '3.0', 'spec_version': '2.3'},
            http_version='1.1', method=method, scheme='http', path=path,
            raw_path=path.encode(), query_string=query.encode(), root_path='', headers=headers,
            client=('127.0.0.1', 1234), server=('fixture.test', 80))
        sent = False
        messages = []
        async def receive():
            nonlocal sent
            if not sent:
                sent = True
                return {'type': 'http.request', 'body': body, 'more_body': False}
            return {'type': 'http.disconnect'}
        async def send(message):
            messages.append(message)
        await asyncio.wait_for(self.app(scope, receive, send), timeout=10)
        status = next(item['status'] for item in messages if item['type'] == 'http.response.start')
        body = b''.join(item.get('body', b'') for item in messages if item['type'] == 'http.response.body')
        return status, json.loads(body)

    async def lookup(self, value=12):
        with patch.object(selection, 'dnd_candidates', return_value=[dict(
                self.candidate, initiative_bonus=value)]):
            status, result = await self.request('GET', '/api/monsters/lookup', query='species=Goblin')
        self.assertEqual(status, 200)
        self.assertEqual(result['status'], 'ok')
        return result['candidates'][0]

    def form(self, candidate):
        return dict(name='Goblin', monster_species='Goblin', ac='15', hprangestart='10',
            hprangeend='', color='#842029', quantity='1',
            initiative_bonus=str(candidate['initiative_bonus']),
            selection_token=candidate['selection_token'],
            initiative_bonus_offer_token=candidate['initiative_bonus_offer_token'])

    def snapshot(self):
        return (copy.deepcopy(self.context.STATE),
                '\n'.join(self.context.STORAGE.connection.iterdump()))

    def assert_not_constructed(self):
        self.context.hp_value_factory.assert_not_called()
        self.context.make_monster.assert_not_called()
        self.context.save_image.assert_not_called()
        self.context.dnd_image.assert_not_called()

    async def test_owned_creation_persists_signed_values_across_storage_reopen(self):
        expected = {}
        for value in (12, 0, -2):
            candidate = await self.lookup(value)
            status, created = await self.request('POST', '/api/monsters', fields=self.form(candidate))
            self.assertEqual(status, 200)
            item = created[0]
            expected[item['id']] = value
            self.assertEqual(item['initiative_bonus_origin'], 'source')
            self.assertEqual(item['monster_source_url'], self.candidate['source_url'])
            self.assertIsNone(item['initiative_roll'])
            self.assertIsNone(item['initiative'])
        self.context.STORAGE.close()
        self.context = storage_fixture.context(self.directory)
        self.context.HTTPException = HTTPException
        for _ in range(3):
            self.context.load_state()
            restored = self.context.STATE['monsters']
            self.assertEqual({item['id']: item['initiative_bonus'] for item in restored}, expected)
            for item in restored:
                self.assertEqual(item['initiative_bonus_origin'], 'source')
                self.assertEqual(item['monster_source_url'], self.candidate['source_url'])
                self.assertIsNone(item['initiative_roll'])
                self.assertIsNone(item['initiative'])

    async def test_missing_client_and_unassigned_admin_cannot_create(self):
        candidate = await self.lookup()
        before = self.snapshot()
        for session, expected in ((None, 401), ('viewer-session', 403), ('outsider-session', 403)):
            with self.subTest(session=session):
                status, _ = await self.request('POST', '/api/monsters',
                    fields=self.form(candidate), session=session)
                self.assertEqual(status, expected)
                self.assertEqual(self.snapshot(), before)
        self.assert_not_constructed()

    async def test_cross_origin_owner_request_is_rejected(self):
        candidate = await self.lookup()
        before = self.snapshot()
        status, _ = await self.request('POST', '/api/monsters', fields=self.form(candidate),
                                       origin='http://evil.test')
        self.assertEqual(status, 403)
        self.assertEqual(self.snapshot(), before)
        self.assert_not_constructed()

    async def test_database_role_change_invalidates_existing_session(self):
        candidate = await self.lookup()
        with self.context.STORAGE.transaction():
            self.context.STORAGE.connection.execute("UPDATE users SET role='client' WHERE username='owner'")
        before = self.snapshot()
        status, _ = await self.request('POST', '/api/monsters', fields=self.form(candidate))
        self.assertEqual(status, 401)
        self.assertNotIn('owner-session', self.context.SESSIONS)
        self.assertEqual(self.snapshot(), before)
        self.assert_not_constructed()

    async def test_invalid_offer_rolls_back_without_constructing_or_persisting(self):
        candidate = await self.lookup()
        before = self.snapshot()
        expired = issue_bonus_offer(self.candidate, selection._KEY, now=time.time()-3600)
        for changes in ({'initiative_bonus_offer_token': candidate['initiative_bonus_offer_token']+'x'},
                        {'initiative_bonus': '99'}):
            fields = dict(self.form(candidate), **changes)
            status, _ = await self.request('POST', '/api/monsters', fields=fields)
            self.assertEqual(status, 422)
            self.assertEqual(self.snapshot(), before)
        self.assert_not_constructed()

    async def test_failure_after_real_persistence_rolls_back_memory_and_database(self):
        candidate = await self.lookup()
        before = self.snapshot()
        real_changed = self.context.combatants_changed
        async def fail_after_save(**kwargs):
            await real_changed(**kwargs)
            raise RuntimeError('fixture failure after persistence')
        with patch.object(self.context, 'combatants_changed', side_effect=fail_after_save):
            with self.assertRaisesRegex(RuntimeError, 'fixture failure after persistence'):
                await self.request('POST', '/api/monsters', fields=self.form(candidate))
        self.assertEqual(self.snapshot(), before)
        self.assertFalse(self.context.STORAGE.connection.in_transaction)
        self.assertFalse(self.context._defer_database_broadcast)


if __name__ == '__main__':
    unittest.main()
