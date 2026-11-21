"""Mutation reply/rollback privacy in small ASGI apps, not full-server acceptance."""
import copy
import json
import unittest
from unittest.mock import patch
from fastapi import Depends
import test_statblock_transport_privacy as transport
from python.scrying_glass_admin_display import AdminDisplayMixin
from python.scrying_glass_admin_monsters import AdminMonstersMixin
from python.scrying_glass_classes import DisplayBackgroundUpdate, MonsterUpdate
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_request_security import same_origin
from python.scrying_glass_service_battle import BattleService
from python.scrying_glass_service_features import FeaturesService
from python.scrying_glass_statblock_encounters import PrivateEncounterStorage


class Handlers(AdminDisplayMixin, AdminMonstersMixin):
    pass


class StatblockMutationPrivacyTests(unittest.IsolatedAsyncioTestCase):
    assert_private_absent = transport.StatblockTransportPrivacyTests.assert_private_absent
    websocket = transport.StatblockTransportPrivacyTests.websocket

    def setUp(self):
        transport.StatblockTransportPrivacyTests.setUp(self)
        battle = BattleService(self.c)
        for name in vars(BattleService):
            if not name.startswith('_') and callable(getattr(battle, name, None)):
                setattr(self.c, name, getattr(battle, name))
        self.c.features = FeaturesService(self.c)
        handlers = Handlers(); handlers.context = self.c

        async def update_display_background(payload: DisplayBackgroundUpdate):
            return await handlers.update_display_background(payload)

        async def update_monster(ident: str, update: MonsterUpdate):
            return await handlers.update_monster(ident, update)

        for path, handler in (('/api/display/background', update_display_background),
                              ('/api/monsters/{ident}', update_monster)):
            self.admin_app.add_api_route(path, transactional_handler(
                self.c, handler, role='admin', cookie_name='admin'), methods=['PATCH'],
                dependencies=[Depends(self.c.require('admin','admin')), Depends(same_origin)])

    def stored_private(self):
        row = self.c.STORAGE.connection.execute(
            'SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',
            (self.a, self.c.DEFAULT_SETUP_NAME)).fetchone()
        return PrivateEncounterStorage(self.c.STORAGE).load(row[0])['_statblocks']

    async def request(self, path, body, *, cookie='admin=dm', origin='http://fixture.test', failure=False):
        content = json.dumps(body).encode(); messages = []; delivered = False
        scope = dict(type='http', asgi={'version':'3.0','spec_version':'2.3'}, http_version='1.1',
            method='PATCH', scheme='http', path=path, raw_path=path.encode(), root_path='', query_string=b'',
            headers=[(b'host',b'fixture.test'), (b'cookie',cookie.encode()), (b'origin',origin.encode()),
                     (b'content-type',b'application/json'), (b'content-length',str(len(content)).encode())],
            client=('127.0.0.1',1234), server=('fixture.test',80))
        async def receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {'type':'http.request','body':content,'more_body':False}
            return {'type':'http.disconnect'}
        async def send(message): messages.append(message)
        raised = False
        try: await self.admin_app(scope, receive, send)
        except OSError:
            if not failure: raise
            raised = True
        self.assertEqual(raised, failure)
        status = next(m['status'] for m in messages if m['type']=='http.response.start')
        text = b''.join(m.get('body',b'') for m in messages if m['type']=='http.response.body').decode()
        try: result = json.loads(text)
        except ValueError: result = text
        self.assert_private_absent(result)
        return status, result

    async def test_full_state_mutation_reply_preserves_private_memory_and_storage(self):
        before = copy.deepcopy(self.c.STATE._statblocks)
        status, body = await self.request('/api/display/background', {'background':'#123456'})
        self.assertEqual(status, 200); self.assertEqual(body['display']['background'], '#123456')
        self.assertEqual(body['monsters'][0]['id'], 'live-secret')
        self.assertEqual(self.c.STATE._statblocks, before); self.assertEqual(self.stored_private(), before)

    async def test_monster_row_mutation_reply_preserves_statblock_metadata(self):
        before = copy.deepcopy(self.c.STATE._statblocks)
        status, body = await self.request('/api/monsters/live-secret', {'name':'Renamed visible monster'})
        self.assertEqual(status, 200); self.assertEqual(body['id'], 'live-secret')
        self.assertEqual(body['name'], 'Renamed visible monster')
        self.assertEqual(self.c.STATE._statblocks, before); self.assertEqual(self.stored_private(), before)

    async def test_mutation_and_broadcast_frames_remain_private(self):
        async def mutate():
            status, _ = await self.request('/api/monsters/live-secret', {'name':'Renamed on display'})
            self.assertEqual(status, 200)
        frames, _ = await self.websocket(self.a, [mutate, 'resync'])
        states = [f['state'] for f in frames if f['type']=='state']
        self.assertGreaterEqual(len(states), 3)
        self.assertEqual(states[-1]['monsters'][0]['name'], 'Renamed on display')
        self.assertNotIn('hp', states[-1]['monsters'][0])

    async def test_rejected_mutations_preserve_live_and_stored_private_content(self):
        before = copy.deepcopy(self.c.STATE); snapshots = copy.deepcopy(before._statblocks)
        for path, body, options, expected in (
            ('/api/display/background', {'background':'#123456'}, {'cookie':''}, 401),
            ('/api/display/background', {'background':'#123456'}, {'cookie':'admin=alice'}, 403),
            ('/api/display/background', {'background':'#123456'}, {'origin':'http://evil.test'}, 403),
            ('/api/display/background', {'background':''}, {}, 422),
            ('/api/display/background', {'background':'   '}, {}, 400),
            ('/api/monsters/missing', {'name':'No target'}, {}, 404),
        ):
            with self.subTest(path=path, expected=expected, options=options):
                self.assertEqual((await self.request(path, body, **options))[0], expected)
                self.assertEqual(self.c.STATE, before)
                self.assertEqual(self.c.STATE._statblocks, snapshots)
                self.assertEqual(self.stored_private(), snapshots)

    async def test_failed_persistence_rolls_back_memory_and_private_metadata(self):
        before = copy.deepcopy(self.c.STATE); snapshots = copy.deepcopy(before._statblocks)
        revision = self.c.features.store.revision()
        with patch.object(self.c.STORAGE, 'set_value', side_effect=OSError('injected persistence failure')):
            status, _ = await self.request('/api/display/background', {'background':'#987654'}, failure=True)
        self.assertEqual(status, 500); self.assertEqual(self.c.STATE, before)
        self.assertEqual(self.c.STATE._statblocks, snapshots); self.assertEqual(self.stored_private(), snapshots)
        self.assertEqual(self.c.features.store.revision(), revision)
        self.assertFalse(self.c.STORAGE.connection.in_transaction)


if __name__ == '__main__': unittest.main()
