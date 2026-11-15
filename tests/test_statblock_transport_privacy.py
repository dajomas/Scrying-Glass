"""In-process ASGI privacy checks, not full-app startup or live-server acceptance."""
import asyncio
import copy
import inspect
import json
import unittest
from types import SimpleNamespace
from urllib.parse import urlencode
from fastapi import FastAPI, HTTPException, Request, WebSocket
import test_campaign_viewers as fixtures
from test_statblock_encounters import snapshot
from python.scrying_glass_api_client import ClientAPI
from python.scrying_glass_admin_pages import AdminPagesMixin
from python.scrying_glass_database_transactions import serialized_handler
from python.scrying_glass_service_auth import AuthService
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage


class StatblockTransportPrivacyTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        fixture = fixtures.CampaignViewerTests('test_live_campaign_uses_existing_player_filter')
        self.addCleanup(fixture.tearDown)
        fixture.setUp()
        self.c, self.acl, self.a, self.b = fixture.c, fixture.acl, fixture.a, fixture.b
        self.c.HTTPException = HTTPException
        self.c.ADMIN_SESSION_COOKIE = 'admin'
        auth = AuthService(self.c)
        self.c.user, self.c.auth_session, self.c.require = auth.user, auth.session, auth.require
        self.acl.replace(self.a, {'user_ids':[fixture.ids['alice']]})
        self.acl.replace(self.b, {'user_ids':[fixture.ids['alice']]})
        self.markers = ('PRIVATE_LIVE_STATBLOCK', 'PRIVATE_SAVED_STATBLOCK')
        db = self.c.STORAGE
        db.save_setup(self.a, self.c.DEFAULT_SETUP_NAME, self.c.setup_snapshot(self.c.STATE))
        for campaign, name, marker in ((self.a, self.c.DEFAULT_SETUP_NAME, self.markers[0]),
                                       (self.b, 'encounter', self.markers[1])):
            encounter = db.connection.execute(
                'SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?', (campaign, name)).fetchone()[0]
            api = PrivateEncounterStorage(db); state = api.load(encounter)
            monster = state['monsters'][0]['id']; value = snapshot(marker)
            value['facts'] = [dict(position=0, key='rules', label='Private rules', display_text=marker)]
            value['provenance'][0]['entity_id'] = marker
            state[PRIVATE_KEY][monster] = value
            saved = api.save(encounter, state)
            self.assertEqual(saved[PRIVATE_KEY][monster]['source_label'], marker)
        self.c.STATE = self.c.load_setup_state(self.c.DEFAULT_SETUP_NAME, self.a)
        self.c.set_active_setup(self.a, self.c.DEFAULT_SETUP_NAME)
        self.assertEqual(self.c.STATE._statblocks['live-secret']['source_label'], self.markers[0])
        self.client = ClientAPI.__new__(ClientAPI); self.client.context = self.c
        admin = AdminPagesMixin(); admin.context = self.c
        self.admin_app, self.client_app = FastAPI(), FastAPI()
        self.admin_app.add_api_route('/api/state', serialized_handler(
            self.c, admin.admin_get_state, role='admin', cookie_name='admin'), methods=['GET'])

        def client_state(request: Request):
            return self.client.client_get_state(request)
        client_state.__name__ = 'client_get_state'
        self.client_app.add_api_route('/api/state', serialized_handler(
            self.c, client_state, role='client', cookie_name='client'), methods=['GET'])

        async def socket(websocket: WebSocket):
            await self.client.ws(websocket)
        self.client_app.add_api_websocket_route('/ws', socket)

    def assert_private_absent(self, value):
        encoded = json.dumps(value)
        for marker in self.markers:
            self.assertNotIn(marker, encoded)
        def walk(item):
            if isinstance(item, dict):
                self.assertNotIn(PRIVATE_KEY, item)
                self.assertFalse({'content_digest','prepared_at','provenance','definitions'} & set(item))
                for child in item.values(): walk(child)
            elif isinstance(item, list):
                for child in item: walk(child)
        walk(value)

    async def http(self, app, cookie='', campaign=None):
        messages = []
        scope = dict(type='http', asgi={'version':'3.0','spec_version':'2.3'}, http_version='1.1',
            method='GET', scheme='http', path='/api/state', raw_path=b'/api/state', root_path='',
            query_string=urlencode({'campaign_id':campaign} if campaign else {}).encode(),
            headers=[(b'host',b'fixture.test'),(b'cookie',cookie.encode())],
            client=('127.0.0.1',1234), server=('fixture.test',80))
        async def receive(): return {'type':'http.request','body':b'','more_body':False}
        async def send(message): messages.append(message)
        await app(scope, receive, send)
        status = next(m['status'] for m in messages if m['type']=='http.response.start')
        body = b''.join(m.get('body',b'') for m in messages if m['type']=='http.response.body')
        result = json.loads(body); self.assert_private_absent(result)
        return status, result

    async def websocket(self, campaign, events=(), token='alice', origin='http://fixture.test'):
        incoming = iter([None, *events]); sent = []
        scope = dict(type='websocket', asgi={'version':'3.0','spec_version':'2.3'}, http_version='1.1',
            scheme='ws', path='/ws', raw_path=b'/ws', root_path='', subprotocols=[],
            query_string=urlencode({'campaign_id':campaign}).encode(),
            headers=[(b'host',b'fixture.test'),(b'origin',origin.encode()),(b'cookie',('client='+token).encode())],
            client=('127.0.0.1',1234), server=('fixture.test',80))
        async def receive():
            while True:
                try: event = next(incoming)
                except StopIteration: return {'type':'websocket.disconnect','code':1000,'reason':'fixture complete'}
                if callable(event):
                    result = event()
                    if inspect.isawaitable(result): await result
                    continue
                if event is None: return {'type':'websocket.connect'}
                return {'type':'websocket.receive','text':json.dumps({'type':event})}
        async def send(message): sent.append(message)
        await asyncio.wait_for(self.client_app(scope, receive, send), timeout=5)
        frames = [json.loads(m['text']) for m in sent if m['type']=='websocket.send']
        self.assert_private_absent(frames)
        return frames, sent

    async def test_admin_http_state_uses_real_serializer_without_private_metadata(self):
        status, body = await self.http(self.admin_app, 'admin=dm')
        self.assertEqual(status, 200)
        self.assertEqual(body['monsters'][0]['id'], 'live-secret')
        self.assertTrue(self.c.STATE._statblocks)

    async def test_client_http_live_and_saved_campaigns_are_scoped_and_private(self):
        before = copy.deepcopy(self.c.STATE._statblocks)
        for campaign, ident in ((self.a,'live-secret'), (self.b,'saved-only')):
            status, body = await self.http(self.client_app, 'client=alice', campaign)
            self.assertEqual(status, 200); self.assertEqual(body['monsters'][0]['id'], ident)
            self.assertNotIn('hp', body['monsters'][0])
        self.assertEqual(self.c.STATE._statblocks, before)

    async def test_http_auth_and_grant_errors_do_not_expose_private_content(self):
        self.assertEqual((await self.http(self.admin_app))[0], 401)
        self.assertEqual((await self.http(self.admin_app, 'admin=alice'))[0], 403)
        self.assertEqual((await self.http(self.client_app, campaign=self.a))[0], 401)
        self.acl.replace(self.b, {'user_ids':[]})
        self.assertEqual((await self.http(self.client_app, 'client=alice', self.b))[0], 403)

    async def test_websocket_initial_resync_and_heartbeat_are_private(self):
        for campaign, ident in ((self.a,'live-secret'), (self.b,'saved-only')):
            frames, _ = await self.websocket(campaign, ['resync','ping'])
            states = [f['state'] for f in frames if f['type']=='state']
            self.assertEqual(len(states), 2)
            self.assertTrue(all(s['monsters'][0]['id']==ident for s in states))
            self.assertEqual(len([f for f in frames if f['type']=='heartbeat']), 1)
        self.assertEqual(self.c.SOCKETS, set()); self.assertEqual(self.c.features.displays, {})

    async def test_broadcast_and_revoked_resync_clear_data_without_private_content(self):
        def revoke(): self.acl.replace(self.a, {'user_ids':[]})
        frames, _ = await self.websocket(self.a, [self.c.broadcast, revoke, self.c.broadcast, 'resync'])
        states = [f['state'] for f in frames if f['type']=='state']
        self.assertEqual(len(states), 4)
        self.assertEqual(states[0]['monsters'][0]['id'], 'live-secret')
        self.assertEqual(states[1]['monsters'][0]['id'], 'live-secret')
        self.assertTrue(all(s['monsters']==[] and s['campaign'] is None for s in states[2:]))

    async def test_unauthorized_websocket_selection_never_uses_active_state(self):
        self.acl.replace(self.b, {'user_ids':[]})
        frames, _ = await self.websocket(self.b, ['resync'])
        states = [f['state'] for f in frames if f['type']=='state']
        self.assertEqual(len(states), 2)
        self.assertTrue(all(s['monsters']==[] and s['campaign'] is None for s in states))

    async def test_websocket_unauthenticated_and_cross_origin_send_no_state(self):
        for kwargs in ({'token':'missing'}, {'origin':'http://evil.test'}):
            frames, sent = await self.websocket(self.a, **kwargs)
            self.assertEqual(frames, [])
            self.assertTrue(any(m['type']=='websocket.close' and m['code']==1008 for m in sent))


if __name__ == '__main__': unittest.main()
