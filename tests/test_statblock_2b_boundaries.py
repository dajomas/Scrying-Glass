"""2B recovery authorization, native exhaustion and production notification gates.

Sessions are seeded, not logged in. ASGI apps use the actual feature installer;
recording sockets observe production sends, not real WebSocket/network delivery.
"""
import asyncio
import copy
import json
import unittest
from unittest.mock import patch
import test_statblock_stage2_contracts as contracts
from python.scrying_glass_campaign_ownership import actor, ownership
from python.scrying_glass_campaign_viewers import viewers
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_service_features import fingerprint
from python.scrying_glass_service_notifications import NotificationsService
from python.scrying_glass_statblock_detaching import detach_loaded_setup
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_loading import PrivateEncounterState
from python.scrying_glass_statblock_restore import restore_bindings


class BoundaryFixture:
    encounter = contracts.StatblockStage2ContractTests.encounter
    stored = contracts.StatblockStage2ContractTests.stored
    seed = contracts.StatblockStage2ContractTests.seed
    assert_content = contracts.StatblockStage2ContractTests.assert_content
    secret = 'PRIVATE_2B_BOUNDARY_GRAPH'

    def setUp(self):
        contracts.StatblockStage2ContractTests.setUp(self)
        from fastapi import HTTPException
        from python.scrying_glass_service_auth import AuthService
        self.c.HTTPException = HTTPException
        self.seed(self.secret); self.initial = copy.deepcopy(self.c.STATE)
        self.c.ADMIN_SESSION_COOKIE = 'admin'; self.c.CLIENT_SESSION_COOKIE = 'client'
        self.c.SESSIONS = {}; self.ids = {}; db = self.c.STORAGE
        for name, role in (('alice','admin'), ('bob','admin'), ('viewer','client'), ('root','superadmin')):
            self.ids[name] = str(db.connection.execute(
                'INSERT INTO users(username,role,password_hash) VALUES (?,?,?)',
                (name,role,'unused-seeded-session')).lastrowid)
            self.c.SESSIONS[name+'-token'] = {'username':name,'role':role}
        auth = AuthService(self.c)
        self.c.user, self.c.require, self.c.auth_session = auth.user, auth.require, auth.session
        self.owner = ownership(self.c); self.owner.initialize()
        self.owner.reassign(self.c.active_campaign(), {'owner_user_id':self.ids['alice']})
        self.other = db.create_campaign('Other recovery owner', '', 'now')
        db.save_characters(self.other, [])
        self.owner.reassign(self.other, {'owner_user_id':self.ids['bob']})
        acl = viewers(self.c); acl.initialize()
        acl.replace(self.c.active_campaign(), {'user_ids':[self.ids['viewer']]})
        self.sends = []; fixture = self
        class RecordingSocket:
            cookies = {'client':'viewer-token'}
            query_params = {'campaign_id':fixture.c.active_campaign()}
            async def send_text(self, text):
                fixture.sends.append(dict(frame=json.loads(text),
                    in_transaction=fixture.c.STORAGE.connection.in_transaction,
                    revision=fixture.f.store.revision(),
                    metadata=copy.deepcopy(fixture.c.STATE._statblocks),
                    stored=copy.deepcopy(fixture.current_private())))
            async def close(self, **kwargs):
                raise AssertionError('Recording socket must not be dropped')
        self.socket = RecordingSocket(); self.c.SOCKETS.add(self.socket)
        self.assertIs(self.c.broadcast.__func__, NotificationsService.broadcast)

    def tearDown(self):
        self.c.SOCKETS.clear()
        contracts.StatblockStage2ContractTests.tearDown(self)

    def dump(self):
        return list(self.c.STORAGE.connection.iterdump())

    def current_encounter(self):
        reference = self.c.active_setup_reference()
        if reference:
            return self.encounter(reference['campaign_id'], reference['name'])
        return self.c.STORAGE.connection.execute(
            'SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()[0]

    def current_private(self):
        return PrivateEncounterStorage(self.c.STORAGE).load(self.current_encounter())[PRIVATE_KEY]

    def assert_private_response(self, value):
        text = json.dumps(value)
        for marker in (self.secret, 'Retain this supporting rule.', PRIVATE_KEY, 'content_digest', 'prepared_at'):
            self.assertNotIn(marker, text)

    def assert_unchanged(self, dump, state):
        self.assertEqual(self.dump(), dump)
        self.assertEqual(dict(self.c.STATE), dict(state))
        self.assertEqual(self.c.STATE._statblocks, state._statblocks)
        self.assertEqual(self.sends, [])
        self.assertFalse(self.c.STORAGE.connection.in_transaction)
        self.assertIsNone(actor(self.c))
        self.assertFalse(getattr(self.c, '_database_broadcast_pending', False))
        self.assertFalse(getattr(self.c, '_defer_database_broadcast', False))


class RecoveryRouteBoundaryTests(BoundaryFixture, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        BoundaryFixture.setUp(self)
        from fastapi import FastAPI
        from python.scrying_glass_api_features import install_feature_routes
        campaign = self.c.active_campaign()
        self.checkpoint = self.f.store.save_snapshot(campaign, self.initial, 'checkpoint', 'Private before')
        api = PrivateEncounterStorage(self.c.STORAGE); state = api.load(self.encounter())
        state['monsters'][0]['hp'] = 9
        state[PRIVATE_KEY]['m'] = contracts.reference_snapshot(self.secret+' changed')
        api.save(self.encounter(), state); self.c.load_state()
        self.current = copy.deepcopy(self.current_private()['m'])
        self.undo_id = self.f.store.save_snapshot(campaign, self.initial, 'undo', 'Private undo', fingerprint(self.c.STATE))
        foreign = PrivateEncounterState({'monsters':[], 'characters':[], 'active_setup':None}, {})
        self.foreign_checkpoint = self.f.store.save_snapshot(self.other, foreign, 'checkpoint', 'Foreign')
        self.foreign_undo = self.f.store.save_snapshot(self.other, foreign, 'undo', 'Foreign undo')
        self.app = FastAPI(); install_feature_routes(self.c, self.app)

    async def request(self, path, body, *, token='alice-token', origin='http://fixture.test'):
        content = json.dumps(body).encode(); messages = []; sent = False
        headers = [(b'host',b'fixture.test'),(b'content-type',b'application/json'),
                   (b'content-length',str(len(content)).encode()),(b'origin',origin.encode())]
        if token is not None: headers.append((b'cookie',('admin='+token).encode()))
        scope = dict(type='http', asgi={'version':'3.0','spec_version':'2.3'}, http_version='1.1',
            method='POST', scheme='http', path=path, raw_path=path.encode(), root_path='',
            query_string=b'', headers=headers, client=('127.0.0.1',1234), server=('fixture.test',80))
        async def receive():
            nonlocal sent
            if not sent:
                sent = True; return {'type':'http.request','body':content,'more_body':False}
            return {'type':'http.disconnect'}
        async def send(message): messages.append(message)
        await self.app(scope, receive, send)
        status = next(message['status'] for message in messages if message['type']=='http.response.start')
        value = json.loads(b''.join(message.get('body',b'') for message in messages if message['type']=='http.response.body'))
        self.assert_private_response(value)
        return status, value

    def restore_path(self, ident=None):
        return '/api/checkpoints/'+str(self.checkpoint if ident is None else ident)+'/restore'

    def confirmation(self):
        return {'confirm':True, 'revision':self.f.store.revision()}

    def assert_restored(self):
        saved = self.current_private()['m']
        self.assert_content(saved, self.initial._statblocks['m'])
        self.assertGreater(saved['revision'], self.current['revision'])
        self.assertEqual(self.c.STATE['monsters'][0]['hp'], 12)
        self.assertEqual(self.c.STATE._statblocks, self.current_private())
        self.assertEqual(len(self.sends), 1); self.assertFalse(self.sends[0]['in_transaction'])
        self.assert_private_response(self.sends[0]['frame'])
        self.assertIsNone(actor(self.c))
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, self.current_private())

    async def test_owned_checkpoint_restore_uses_real_auth_and_private_kernel(self):
        status, value = await self.request(self.restore_path(), self.confirmation())
        self.assertEqual((status,value), (200, {'restored':self.checkpoint}))
        self.assert_restored()

    async def test_owned_undo_uses_real_auth_and_advances_private_revision(self):
        status, value = await self.request('/api/battle/undo', {'id':self.undo_id})
        self.assertEqual(status, 200); self.assertIn('undone', value)
        self.assert_restored()
        self.assertIsNone(self.f.store.row(self.undo_id, self.c.active_campaign(), 'undo'))

    async def test_existing_superadmin_recovery_permission_is_retained(self):
        status, _ = await self.request(self.restore_path(), self.confirmation(), token='root-token')
        self.assertEqual(status, 200); self.assert_restored()

    async def test_checkpoint_denials_are_atomic_and_private(self):
        valid = self.confirmation()
        cases = [(self.restore_path(),valid,{'token':None},401),
                 (self.restore_path(),valid,{'token':'viewer-token'},403),
                 (self.restore_path(),valid,{'token':'bob-token'},403),
                 (self.restore_path(),valid,{'origin':'http://evil.test'},403),
                 (self.restore_path(),{'revision':valid['revision']},{},409),
                 (self.restore_path(),{'confirm':False,'revision':valid['revision']},{},409),
                 (self.restore_path(),{'confirm':True,'revision':valid['revision']-1},{},409),
                 (self.restore_path(self.foreign_checkpoint),valid,{},404),
                 (self.restore_path(self.undo_id),valid,{},404)]
        for path, body, options, expected in cases:
            with self.subTest(path=path, options=options, body=body):
                dump = self.dump(); state = copy.deepcopy(self.c.STATE)
                status, _ = await self.request(path, body, **options)
                self.assertEqual(status, expected); self.assert_unchanged(dump, state)

    async def test_undo_denials_are_atomic_and_private(self):
        cases = [({'id':self.undo_id},{'token':None},401),
                 ({'id':self.undo_id},{'token':'viewer-token'},403),
                 ({'id':self.undo_id},{'token':'bob-token'},403),
                 ({'id':self.undo_id},{'origin':'http://evil.test'},403),
                 ({'id':self.foreign_undo},{},409), ({'id':True},{},409)]
        for body, options, expected in cases:
            with self.subTest(body=body, options=options):
                dump = self.dump(); state = copy.deepcopy(self.c.STATE)
                status, _ = await self.request('/api/battle/undo', body, **options)
                self.assertEqual(status, expected); self.assert_unchanged(dump, state)

    async def test_stale_undo_fingerprint_cannot_replace_private_content(self):
        with self.c.STORAGE.transaction():
            self.c.STORAGE.connection.execute('UPDATE encounter_snapshots SET after_digest=? WHERE id=?', ('0'*64,self.undo_id))
        dump = self.dump(); state = copy.deepcopy(self.c.STATE)
        status, _ = await self.request('/api/battle/undo', {'id':self.undo_id})
        self.assertEqual(status, 409); self.assert_unchanged(dump, state)


class NativeClearExhaustionTests(BoundaryFixture, unittest.TestCase):
    def exercise(self, runtime):
        db = self.c.STORAGE; api = PrivateEncounterStorage(db); state = api.load(self.encounter())
        for ident in ('n','r'):
            item = copy.deepcopy(state['monsters'][0]); item['id'] = ident; state['monsters'].append(item)
            state[PRIVATE_KEY][ident] = contracts.reference_snapshot(self.secret+' '+ident)
        api.save(self.encounter(), state); self.c.load_state()
        saved_setup = copy.deepcopy(self.stored())
        if runtime:
            async def detach(): detach_loaded_setup(self.c)
            asyncio.run(transactional_handler(self.c, detach)())
        image = PrivateEncounterState(copy.deepcopy(dict(self.c.STATE)),
                                      {'r':contracts.reference_snapshot(self.secret+' replacement')})
        for item in image['monsters']: item['hp'] = 1
        checkpoint = self.f.store.save_snapshot(self.c.active_campaign(), image, 'checkpoint', 'Clear and replace')
        owner = self.current_encounter(); bindings = restore_bindings(db, owner)
        with db.transaction(): db._record_statblock_revision(bindings['n'][0], 2**63-1)
        bindings = restore_bindings(db, owner)
        self.assertLess(bindings['m'][1], 2**63-1); self.assertEqual(bindings['n'][1], 2**63-1)
        self.sends.clear()
        dump = self.dump(); before = copy.deepcopy(self.c.STATE)
        with (
            patch.object(db, '_save_encounter', wraps=db._save_encounter) as tracker,
            patch.object(db, '_record_statblock_revision', wraps=db._record_statblock_revision) as counters,
        ):
            with self.assertRaises(self.c.HTTPException) as raised:
                asyncio.run(transactional_handler(self.c, self.f.restore_checkpoint)(checkpoint,
                    {'confirm':True,'revision':self.f.store.revision()}))
            self.assertEqual(raised.exception.status_code, 409)
            tracker.assert_not_called(); counters.assert_not_called()
        self.assert_unchanged(dump, before)
        self.assertEqual(restore_bindings(db, owner), bindings)
        self.assertEqual(self.stored(), saved_setup)
        self.assertEqual(list(db.connection.execute('PRAGMA foreign_key_check')), [])

    def test_saved_setup_mixed_clear_exhaustion_preflights_all_writes(self):
        self.exercise(False)

    def test_unsaved_runtime_mixed_clear_exhaustion_preserves_saved_setup(self):
        self.exercise(True)


class NotificationBoundaryTests(BoundaryFixture, unittest.TestCase):
    def change(self):
        async def edit_monster():
            self.c.STATE['monsters'][0]['hp'] = 9
            value = self.c.STATE._statblocks['m']
            value.pop('content_digest', None); value['source_label'] = self.secret+' changed'
            await self.c.combatants_changed(monsters=True, characters=False)
            self.assertTrue(self.c._database_broadcast_pending)
            self.assertEqual(self.sends, [])
        return asyncio.run(transactional_handler(self.c, edit_monster)())

    def test_handler_and_private_flush_coalesce_through_real_broadcast(self):
        before = copy.deepcopy(self.current_private()['m']); revision = self.f.store.revision()
        with patch.object(self.c, 'broadcast', wraps=self.c.broadcast) as broadcast:
            self.change()
            self.assertEqual(broadcast.await_count, 2)
        self.assertEqual(len(self.sends), 1); sent = self.sends[0]
        self.assertFalse(sent['in_transaction']); self.assertEqual(sent['revision'], revision+1)
        self.assertEqual(sent['frame']['revision'], revision+1)
        self.assertEqual(sent['frame']['state']['monsters'][0]['id'], 'm')
        self.assertNotIn('hp', sent['frame']['state']['monsters'][0])
        self.assertEqual(sent['metadata'], sent['stored']); self.assertEqual(sent['stored'], self.current_private())
        self.assertEqual(sent['metadata']['m']['revision'], before['revision']+1)
        self.assertEqual(sent['metadata']['m']['source_label'], self.secret+' changed')
        self.assertEqual(self.c.STATE['monsters'][0]['hp'], 9)
        self.assertEqual(self.f.store.latest_undo(self.c.active_campaign())['after_digest'], fingerprint(self.c.STATE))
        self.assert_private_response(sent['frame'])
        self.assertFalse(self.c._database_broadcast_pending); self.assertFalse(self.c._defer_database_broadcast)

    def test_late_history_failure_sends_nothing_and_restores_all_state(self):
        dump = self.dump(); before = copy.deepcopy(self.c.STATE); after = self.f.after_transaction
        def fail(*args):
            after(*args)
            self.assertNotEqual(self.current_private(), before._statblocks)
            raise OSError('after private flush and real history')
        with patch.object(self.f, 'after_transaction', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'real history'): self.change()
        self.assert_unchanged(dump, before)

    def test_true_noop_after_private_edit_adds_no_write_or_frame(self):
        self.change(); self.sends.clear(); dump = self.dump(); before = copy.deepcopy(self.c.STATE)
        async def no_op(): return {'ok':True}
        result = asyncio.run(transactional_handler(self.c, no_op)())
        self.assertEqual(result, {'ok':True}); self.assert_unchanged(dump, before)


if __name__ == '__main__': unittest.main()
