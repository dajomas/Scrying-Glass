"""022.09 statblock listener application through FastAPI: sign-in, page, reads and WebSocket.

Raw ASGI calls with seeded accounts on native SQLite; no network or browser.
"""
import asyncio
import json
import unittest
from urllib.parse import urlencode

import test_statblock_import_service as service_tests
from python.scrying_glass_service_auth import AuthService

COOKIE = 'scrying_glass_statblock_session'


class ListenerHTTPTests(service_tests.ImportFixture, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        service_tests.ImportFixture.setUp(self)
        import secrets
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse, RedirectResponse
        from python.scrying_glass_init import login, password_hash, password_ok
        from python.scrying_glass_statblock_viewer_app import install_statblock_viewer
        c = self.c
        auth = AuthService(c)
        c.HTTPException, c.HTMLResponse, c.RedirectResponse = HTTPException, HTMLResponse, RedirectResponse
        c.login, c.password_ok, c.secrets = login, password_ok, secrets
        c.user, c.require, c.auth_session = auth.user, auth.require, auth.session
        c.STATBLOCK_SESSION_COOKIE, c.LEGACY_SESSION_COOKIES = COOKIE, ()
        for name in ('alice', 'root', 'viewer'):
            c.STORAGE.connection.execute('UPDATE users SET password_hash=? WHERE username=?',
                                         (password_hash('correct-horse'), name))
        self.app = FastAPI()
        install_statblock_viewer(c, self.app)

    async def request(self, path, *, method='GET', raw=b'', cookie=None, content_type='application/json',
                      origin='http://fixture.test'):
        headers = [(b'host', b'fixture.test'), (b'content-type', content_type.encode()),
                   (b'content-length', str(len(raw)).encode()), (b'origin', origin.encode())]
        if cookie is not None:
            headers.append((b'cookie', cookie.encode()))
        scope = dict(type='http', asgi={'version': '3.0', 'spec_version': '2.3'}, http_version='1.1', method=method,
                     scheme='http', path=path, raw_path=path.encode(), root_path='', query_string=b'',
                     headers=headers, client=('127.0.0.1', 1234), server=('fixture.test', 80))
        sent, messages = False, []
        async def receive():
            nonlocal sent
            if not sent:
                sent = True
                return {'type': 'http.request', 'body': raw, 'more_body': False}
            return {'type': 'http.disconnect'}
        async def send(message):
            messages.append(message)
        await self.app(scope, receive, send)
        start = next(m for m in messages if m['type'] == 'http.response.start')
        body = b''.join(m.get('body', b'') for m in messages if m['type'] == 'http.response.body')
        return start['status'], body, start['headers']

    async def socket(self, cookie, origin='http://fixture.test'):
        """Connect, collect frames until the first one (or a close), then disconnect."""
        incoming = asyncio.Queue()
        await incoming.put({'type': 'websocket.connect'})
        sent = []
        first = asyncio.Event()
        async def receive():
            return await incoming.get()
        async def send(message):
            sent.append(message)
            if message['type'] in ('websocket.send', 'websocket.close'):
                first.set()
        headers = [(b'host', b'fixture.test'), (b'origin', origin.encode()), (b'cookie', cookie.encode())]
        scope = dict(type='websocket', asgi={'version': '3.0'}, scheme='ws', path='/ws', raw_path=b'/ws',
                     root_path='', query_string=b'', headers=headers, client=('127.0.0.1', 1234),
                     server=('fixture.test', 80), subprotocols=[])
        task = asyncio.create_task(self.app(scope, receive, send))
        await asyncio.wait_for(first.wait(), 5)
        await incoming.put({'type': 'websocket.disconnect', 'code': 1000})
        await asyncio.wait_for(task, 5)
        return sent

    def session_cookie(self, headers):
        for key, value in headers:
            if key == b'set-cookie' and value.startswith(COOKIE.encode() + b'='):
                return value.split(b';')[0].decode()
        return None

    async def login(self, username):
        return await self.request('/login', method='POST', raw=urlencode(
            {'username': username, 'password': 'correct-horse'}).encode(),
            content_type='application/x-www-form-urlencoded')

    async def test_only_regular_admins_can_sign_in(self):
        status, _, headers = await self.login('alice')
        self.assertEqual(status, 303)
        self.assertIsNotNone(self.session_cookie(headers))
        for name in ('root', 'viewer'):
            status, body, headers = await self.login(name)
            self.assertEqual(status, 200)
            self.assertIsNone(self.session_cookie(headers))
            self.assertIn(b'regular admin', body)

    async def test_page_and_reads_need_the_listener_session(self):
        status, _, headers = await self.request('/', cookie='admin=alice-token')
        self.assertEqual(status, 303)
        status, body, headers = await self.request('/', cookie=COOKIE + '=alice-token')
        self.assertEqual(status, 200)
        self.assertIn(b'Statblocks', body)
        self.assertIn((b'cache-control', b'no-store'), headers)
        self.assertEqual((await self.request('/', cookie=COOKIE + '=bob-token'))[0], 403)
        status, body, _ = await self.request('/api/statblocks/state', cookie=COOKIE + '=alice-token')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['encounter_token'], self.token())
        self.assertEqual((await self.request('/api/statblocks/state', cookie='admin=alice-token'))[0], 401)
        status, body, _ = await self.request('/api/statblocks/state', cookie=COOKIE + '=root-token')
        self.assertEqual((status, json.loads(body)['code']), (403, 'regular_admin_required'))
        for path in ('/api/statblocks/apply', '/api/statblocks/discover', '/api/statblocks/prepare'):
            self.assertIn((await self.request(path, method='POST', raw=b'{}', cookie=COOKIE + '=alice-token'))[0],
                          (404, 405))

    async def test_websocket_sends_an_authorized_projection_or_refuses(self):
        sent = await self.socket(COOKIE + '=alice-token')
        self.assertEqual(sent[0]['type'], 'websocket.accept')
        frame = json.loads(sent[1]['text'])
        self.assertEqual((frame['type'], frame['state']['campaign_id']), ('state', self.c.active_campaign()))
        for cookie, origin in ((COOKIE + '=root-token', 'http://fixture.test'), ('admin=alice-token', 'http://fixture.test'),
                               (COOKIE + '=alice-token', 'http://evil.test')):
            sent = await self.socket(cookie, origin)
            self.assertEqual([m['type'] for m in sent], ['websocket.close'])
            self.assertEqual(sent[0]['code'], 1008)

    async def test_logout_ends_the_session(self):
        status, _, _ = await self.request('/logout', method='POST', cookie=COOKIE + '=alice-token')
        self.assertEqual(status, 303)
        self.assertNotIn('alice-token', self.c.SESSIONS)
        self.assertEqual((await self.request('/', cookie=COOKIE + '=alice-token'))[0], 303)


if __name__ == '__main__':
    unittest.main()
