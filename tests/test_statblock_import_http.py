"""022.08 statblock API routes through FastAPI: authentication, same-origin, envelopes, Edit save.

Seeded sessions, native SQLite and fake provider runners; raw ASGI calls, no network/browser.
"""
import asyncio
import json
import unittest
import uuid

import test_statblock_import_service as service_tests
from python.scrying_glass_service_auth import AuthService


class StatblockHTTPTests(service_tests.ImportFixture, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        service_tests.ImportFixture.setUp(self)
        from fastapi import FastAPI, HTTPException
        from python.scrying_glass_statblock_routes import install_statblock_routes
        auth = AuthService(self.c)
        self.c.HTTPException = HTTPException
        self.c.user, self.c.require, self.c.auth_session = auth.user, auth.require, auth.session
        self.app = FastAPI()
        install_statblock_routes(self.c, self.app)

    async def request(self, path, *, method='GET', body=None, raw=None, content_type='application/json',
                      token='alice-token', origin='http://fixture.test', query=b''):
        content = raw if raw is not None else (json.dumps(body).encode() if body is not None else b'')
        headers = [(b'host', b'fixture.test'), (b'content-type', content_type.encode()),
                   (b'content-length', str(len(content)).encode())]
        if origin is not None:
            headers.append((b'origin', origin.encode()))
        if token is not None:
            headers.append((b'cookie', ('admin=' + token).encode()))
        scope = dict(type='http', asgi={'version': '3.0', 'spec_version': '2.3'}, http_version='1.1', method=method,
                     scheme='http', path=path, raw_path=path.encode(), root_path='', query_string=query,
                     headers=headers, client=('127.0.0.1', 1234), server=('fixture.test', 80))
        sent, messages = False, []
        async def receive():
            nonlocal sent
            if not sent:
                sent = True
                return {'type': 'http.request', 'body': content, 'more_body': False}
            return {'type': 'http.disconnect'}
        async def send(message):
            messages.append(message)
        await self.app(scope, receive, send)
        start = next(m for m in messages if m['type'] == 'http.response.start')
        output = b''.join(m.get('body', b'') for m in messages if m['type'] == 'http.response.body')
        return start['status'], json.loads(output) if output else None, dict(start['headers'])

    async def poll(self, job_id):
        for _ in range(500):
            status, value, _ = await self.request('/api/statblocks/jobs/' + job_id)
            self.assertEqual(status, 200)
            if value['status'] not in ('queued', 'running'):
                return value
            await asyncio.sleep(0.01)
        raise AssertionError('job did not finish')

    async def test_reads_require_a_regular_admin_and_are_not_cached(self):
        status, value, headers = await self.request('/api/statblocks/state')
        self.assertEqual(status, 200)
        self.assertEqual(value['encounter_token'], self.token())
        status, value, headers = await self.request('/api/statblocks/state', token='root-token')
        self.assertEqual((status, value['code']), (403, 'regular_admin_required'))
        self.assertEqual(headers.get(b'cache-control'), b'no-store')
        self.assertEqual((await self.request('/api/statblocks/state', token=None))[0], 401)
        self.assertEqual((await self.request('/api/statblocks/state', token='viewer-token'))[0], 403)
        self.assertEqual((await self.request('/api/statblocks/state', token='bob-token'))[0], 403)
        status, value, _ = await self.request('/api/statblocks/monsters/missing')
        self.assertEqual((status, value['code']), (404, 'monster_not_found'))

    async def test_discover_prepare_poll_and_apply(self):
        campaign = self.c.active_campaign()
        status, found, _ = await self.request('/api/statblocks/discover', method='POST', body={
            'campaign_id': campaign, 'encounter_token': self.token(), 'monster_ids': ['m']})
        self.assertEqual(status, 200, found)
        candidate = found['monsters'][0]['candidates'][0]['candidate_id']
        status, job, _ = await self.request('/api/statblocks/prepare', method='POST', body={
            'campaign_id': campaign, 'encounter_token': self.token(), 'monster_id': 'm',
            'expected_statblock_revision': 0, 'candidate_id': candidate})
        self.assertEqual(status, 202, job)
        done = await self.poll(job['job_id'])
        self.assertEqual(done['status'], 'completed')
        body = {'operation_id': uuid.uuid4().hex, 'campaign_id': campaign, 'encounter_token': self.token(),
                'items': [{'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': done['selection_id']}]}
        status, applied, _ = await self.request('/api/statblocks/apply', method='POST', body=body)
        self.assertEqual((status, applied['applied'][0]['statblock_revision']), (200, 1))
        self.assertEqual(self.stored()['m']['revision'], 1)
        self.assertEqual((await self.request('/api/statblocks/apply', method='POST', body=body))[1], applied)
        status, read, _ = await self.request('/api/statblocks/monsters/m', query=b'known_revision=1')
        self.assertEqual((status, read.get('unchanged')), (200, True))

    async def test_writes_are_same_origin_bounded_and_enveloped(self):
        campaign = self.c.active_campaign()
        body = {'campaign_id': campaign, 'encounter_token': self.token(), 'monster_ids': ['m']}
        self.assertEqual((await self.request('/api/statblocks/discover', method='POST', body=body,
                                             origin='http://evil.test'))[0], 403)
        status, value, _ = await self.request('/api/statblocks/apply', method='POST', raw=b'{' * 10)
        self.assertEqual((status, value['code']), (422, 'invalid_request'))
        status, value, _ = await self.request('/api/statblocks/apply', method='POST', raw=b' ' * (1024 * 1024 + 1))
        self.assertEqual((status, value['code']), (413, 'body_too_large'))
        status, value, _ = await self.request('/api/statblocks/discover', method='POST',
                                              body=dict(body, encounter_token='stale'))
        self.assertEqual((status, value['code'], value['items']), (409, 'encounter_changed', []))
        status, value, _ = await self.request('/api/statblocks/apply', method='POST', body={
            'operation_id': 'x', 'campaign_id': campaign, 'encounter_token': self.token(),
            'items': [{'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': 'forged'}]})
        self.assertEqual((status, value['code'], value['items'][0]['code']), (410, 'apply_rejected', 'selection_expired'))
        status, value, _ = await self.request('/api/statblocks/discover', method='POST', body=body, token='root-token')
        self.assertEqual((status, value['code']), (403, 'regular_admin_required'))

    async def test_multipart_monster_file_preparation(self):
        boundary = 'sg-statblock-boundary'
        fields = {'campaign_id': self.c.active_campaign(), 'encounter_token': self.token(), 'monster_id': 'm',
                  'expected_statblock_revision': '0'}
        parts = b''.join(('--' + boundary + '\r\nContent-Disposition: form-data; name="' + key + '"\r\n\r\n'
                          + value + '\r\n').encode() for key, value in fields.items())
        parts += ('--' + boundary + '\r\nContent-Disposition: form-data; name="file"; filename="g.monster"\r\n'
                  'Content-Type: application/octet-stream\r\n\r\n').encode() + b'{"name":"Goblin"}\r\n'
        parts += ('--' + boundary + '--\r\n').encode()
        status, job, _ = await self.request('/api/statblocks/prepare', method='POST', raw=parts,
                                            content_type='multipart/form-data; boundary=' + boundary)
        self.assertEqual(status, 202, job)
        done = await self.poll(job['job_id'])
        self.assertEqual(done['status'], 'completed')
        self.assertEqual(self.runs[-1][0], 'file')
        status, cancelled, _ = await self.request('/api/statblocks/jobs/' + job['job_id'], method='DELETE')
        self.assertEqual((status, cancelled['status']), (200, 'cancelled'))
        self.assertEqual(self.service.store.counts()['bindings'], 0)

    async def test_edit_monster_route_saves_a_staged_statblock(self):
        from types import SimpleNamespace
        from unittest.mock import AsyncMock
        from python import scrying_glass_api_admin as api
        from python.scrying_glass_classes import MonsterUpdate
        from unittest.mock import patch
        self.c.MonsterUpdate = MonsterUpdate
        self.c.combatants_changed = AsyncMock()
        admin = api.AdminAPI.__new__(api.AdminAPI); admin.context = self.c; admin.app = self.app
        routes = tuple(row for row in api.ADMIN_ROUTES if row[1] == 'edit_monster')
        with patch.object(api, 'ADMIN_ROUTES', routes):
            admin.register_routes()
        result = self.prepare(candidate=self.candidate())
        monster = self.item('m')
        fields = {'name': monster['name'], 'monster_species': 'Goblin', 'ac': str(monster.get('ac') or 10),
                  'hp': str(monster['hp']), 'max_hp': str(monster.get('max_hp') or monster['hp']),
                  'original_hp': str(monster.get('original_hp') or monster['hp']), 'color': '#842029',
                  'initiative': '', 'ally': 'false', 'statblock_selection_id': result['selection_id'],
                  'statblock_operation_id': 'edit-op', 'statblock_expected_revision': '0',
                  'expected_values': json.dumps({'hp': monster['hp']})}
        from urllib.parse import urlencode
        raw = urlencode(fields).encode()
        status, value, _ = await self.request('/api/monsters/m/edit', method='POST', raw=raw,
                                              content_type='application/x-www-form-urlencoded')
        self.assertEqual(status, 200, value)
        self.assertEqual(self.stored()['m']['revision'], 1)
        stale = dict(fields, statblock_selection_id='', statblock_operation_id='', statblock_expected_revision='',
                     expected_values=json.dumps({'hp': monster['hp'] + 1}), name='Renamed')
        status, value, _ = await self.request('/api/monsters/m/edit', method='POST', raw=urlencode(stale).encode(),
                                              content_type='application/x-www-form-urlencoded')
        self.assertEqual((status, value['code']), (409, 'edit_conflict'))
        self.assertNotEqual(self.item('m')['name'], 'Renamed')


if __name__ == '__main__':
    unittest.main()
