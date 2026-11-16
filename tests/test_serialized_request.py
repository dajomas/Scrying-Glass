"""Request forwarding through real ASGI and production client route registration."""
import asyncio
import inspect
import json
import unittest
from types import SimpleNamespace
from fastapi import FastAPI, HTTPException, Request, WebSocket
import test_campaign_viewers as fixtures
from python.scrying_glass_api_client import ClientAPI
from python.scrying_glass_campaign_ownership import actor
from python.scrying_glass_database_transactions import operation_lock, serialized_handler
from python.scrying_glass_service_auth import AuthService


class SerializedRequestTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.allowed = True
        self.auth_requests = []
        self.handler_requests = []
        self.c = SimpleNamespace(require=self.require)

    def require(self, role, cookie_name):
        self.assertEqual((role, cookie_name), ('client', 'client'))
        async def authorize(request: Request):
            self.assertTrue(operation_lock(self.c).locked())
            self.auth_requests.append(request)
            if not self.allowed or request.cookies.get('client') != 'alice':
                raise HTTPException(401, 'Sign in required')
            return {'username': 'alice', 'role': 'client'}
        return authorize

    def wrap(self, handler):
        wrapped = serialized_handler(self.c, handler, role='client', cookie_name='client')
        parameters = list(inspect.signature(wrapped).parameters.values())
        requests = [parameter for parameter in parameters if parameter.annotation is Request]
        self.assertEqual(len(requests), 1)
        return wrapped

    def app(self, handler):
        app = FastAPI()
        app.add_api_route('/api/state', self.wrap(handler), methods=['GET'])
        return app

    async def response(self, app, cookie='client=alice', query=b'value=12'):
        messages = []
        scope = dict(type='http', asgi={'version':'3.0','spec_version':'2.3'}, http_version='1.1',
            method='GET', scheme='http', path='/api/state', raw_path=b'/api/state', root_path='',
            query_string=query, headers=[(b'host',b'fixture.test'),(b'cookie',cookie.encode())],
            client=('127.0.0.1',1234), server=('fixture.test',80))
        async def receive(): return {'type':'http.request','body':b'','more_body':False}
        async def send(message): messages.append(message)
        await app(scope, receive, send)
        status = next(message['status'] for message in messages if message['type']=='http.response.start')
        body = b''.join(message.get('body',b'') for message in messages if message['type']=='http.response.body')
        return status, json.loads(body)

    async def test_sync_existing_request_reaches_auth_and_handler(self):
        def endpoint(incoming: Request, value: int=7):
            self.handler_requests.append(incoming)
            self.assertTrue(operation_lock(self.c).locked())
            return {'value':value}
        status, body = await self.response(self.app(endpoint))
        self.assertEqual((status, body), (200, {'value':12}))
        self.assertIs(self.handler_requests[0], self.auth_requests[0])
        self.assertIsNone(actor(self.c))

    async def test_async_keyword_only_request_is_preserved(self):
        async def endpoint(*, request: Request, value: int=7):
            self.handler_requests.append(request)
            await asyncio.sleep(0)
            return {'value':value}
        status, body = await self.response(self.app(endpoint))
        self.assertEqual((status, body), (200, {'value':12}))
        self.assertIs(self.handler_requests[0], self.auth_requests[0])

    async def test_requestless_handler_keeps_internal_request_injection(self):
        def endpoint(value: int=7): return {'value':value}
        wrapped = self.wrap(endpoint)
        self.assertIn('_operation_request', inspect.signature(wrapped).parameters)
        app = FastAPI(); app.add_api_route('/api/state', wrapped, methods=['GET'])
        self.assertEqual(await self.response(app), (200, {'value':12}))
        self.assertEqual(len(self.auth_requests), 1)

    async def test_direct_positional_request_is_authenticated(self):
        def endpoint(incoming: Request): return {'same':incoming is request}
        request = Request({'type':'http','headers':[(b'cookie',b'client=alice')]})
        self.assertEqual(await self.wrap(endpoint)(request), {'same':True})
        self.assertIs(self.auth_requests[0], request)

    async def test_revocation_while_waiting_is_checked_after_lock(self):
        def endpoint(request: Request): self.handler_requests.append(request)
        request = Request({'type':'http','headers':[(b'cookie',b'client=alice')]})
        wrapped = self.wrap(endpoint); lock = operation_lock(self.c)
        await lock.acquire()
        task = asyncio.create_task(wrapped(request=request))
        try:
            await asyncio.sleep(0)
            self.assertEqual(self.auth_requests, [])
            self.allowed = False
        finally:
            lock.release()
        with self.assertRaises(HTTPException) as raised: await task
        self.assertEqual(raised.exception.status_code, 401)
        self.assertEqual(self.handler_requests, [])
        self.assertIsNone(actor(self.c))
        self.assertFalse(lock.locked())

    async def test_missing_or_bad_session_cannot_reach_handler(self):
        def endpoint(request: Request): self.handler_requests.append(request); return {}
        app = self.app(endpoint)
        for cookie in ('', 'client=missing'):
            with self.subTest(cookie=cookie):
                self.assertEqual((await self.response(app, cookie=cookie))[0], 401)
        self.assertEqual(self.handler_requests, [])
        self.assertIsNone(actor(self.c))

    async def test_actual_client_route_registration_preserves_campaign_selection(self):
        fixture = fixtures.CampaignViewerTests('test_live_campaign_uses_existing_player_filter')
        fixture.setUp(); self.addCleanup(fixture.tearDown)
        c = fixture.c
        c.HTTPException, c.FastAPIRequest, c.WebSocket = HTTPException, Request, WebSocket
        auth = AuthService(c)
        c.user, c.auth_session, c.require = auth.user, auth.session, auth.require
        fixture.grant(fixture.a, 'alice'); fixture.grant(fixture.b, 'alice')
        client = ClientAPI.__new__(ClientAPI); client.context = c; client.app = FastAPI()
        client.register_routes()
        for campaign, ident in ((fixture.a,'live-secret'), (fixture.b,'saved-only')):
            status, body = await self.response(client.app, query=('campaign_id='+campaign).encode())
            self.assertEqual(status, 200)
            self.assertEqual(body['campaign']['id'], campaign)
            self.assertEqual(body['monsters'][0]['id'], ident)
            self.assertNotIn('hp', body['monsters'][0])
        self.assertEqual((await self.response(client.app, cookie=''))[0], 401)
        fixture.grant(fixture.b)
        self.assertEqual((await self.response(client.app, query=('campaign_id='+fixture.b).encode()))[0], 403)
        self.assertIsNone(actor(c))


if __name__ == '__main__': unittest.main()
