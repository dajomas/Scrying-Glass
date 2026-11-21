"""2C.2c.3 native transfer/history and selected real-ASGI regressions.

Native/ASGI methods are prepared, not executed at delivery. HTTP sessions are
seeded in memory; login/password, listeners, browsers and WebSockets are not tested.
"""
import asyncio
import copy
import json
import unittest
from unittest.mock import patch
import test_statblock_private_transaction_saves as fixtures
from python.scrying_glass_admin_campaigns import AdminCampaignsMixin
from python.scrying_glass_classes import CampaignSetupAdd
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_campaign_ownership import actor, ownership


class TransferFixture:
    setUp = fixtures.PrivateTransactionSaveTests.setUp
    tearDown = fixtures.PrivateTransactionSaveTests.tearDown
    call = fixtures.PrivateTransactionSaveTests.call
    encounter = fixtures.PrivateTransactionSaveTests.encounter
    seed = fixtures.PrivateTransactionSaveTests.seed
    stored = fixtures.PrivateTransactionSaveTests.stored
    secret = 'SG_PRIVATE_TRANSFER_CONTENT'

    def transfer(self, target, mode):
        handler = AdminCampaignsMixin(); handler.context = self.c
        payload = CampaignSetupAdd(from_campaign=self.c.active_campaign(),setup='default',mode=mode)
        return asyncio.run(transactional_handler(self.c,handler.add_setup_to_campaign)(target,payload))

    def dump(self):
        return '\n'.join(self.c.STORAGE.connection.iterdump())

    def history(self):
        self.seed(self.secret)
        self.call('edit_features','m',{'temp_hp':1})
        checkpoint = self.call('save_checkpoint',{'name':'Before transfer'})['id']
        self.assertIsNotNone(self.f.summary()['undo'])
        return checkpoint

    def emitter(self):
        seen = []
        async def broadcast():
            if getattr(self.c,'_defer_database_broadcast',False):
                self.c._database_broadcast_pending = True
                return
            seen.append((self.c.STORAGE.connection.in_transaction,self.f.store.revision(),copy.deepcopy(self.c.STATE._statblocks)))
        self.c.broadcast = broadcast
        return seen

    def assert_private(self, value):
        text = json.dumps(value)
        self.assertNotIn(self.secret,text)
        self.assertNotIn('Retain this supporting rule.',text)
        self.assertNotIn('_statblocks',text)


class TransferBoundaryTests(TransferFixture, unittest.TestCase):
    def test_copy_clears_boundary_undo_but_preserves_checkpoint_revision_and_live_state(self):
        checkpoint = self.history(); source = self.c.active_campaign()
        target = self.c.STORAGE.create_campaign('Other','','now')
        before = copy.deepcopy(self.c.STATE); content = self.stored(); revision = self.f.store.revision()
        seen = self.emitter(); result = self.transfer(target,'copy')
        self.assertIsNone(self.f.summary()['undo']); self.assertEqual(self.f.store.revision(),revision)
        self.assertEqual(seen,[]); self.assertEqual(dict(self.c.STATE),dict(before))
        self.assertEqual(self.c.STATE._statblocks,before._statblocks); self.assertEqual(self.stored(),content)
        self.assertEqual(self.f.store.load(checkpoint,source,'checkpoint')._statblocks,content)
        self.assertEqual(self.stored(target,result['setup'])['m']['content_digest'],content['m']['content_digest'])
        self.assert_private(result); self.assert_private(self.c.public_state()); self.assert_private(self.c.display_state())

    def test_loaded_move_emits_once_after_commit_with_saved_metadata_and_final_revision(self):
        checkpoint = self.history(); source = self.c.active_campaign(); content = self.stored()
        target = self.c.STORAGE.create_campaign('Other','','now'); revision = self.f.store.revision()
        seen = self.emitter(); result = self.transfer(target,'move')
        runtime = self.c.STORAGE.connection.execute('SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()[0]
        saved = PrivateEncounterStorage(self.c.STORAGE).load(runtime)[PRIVATE_KEY]
        self.assertEqual(seen,[(False,revision+1,saved)])
        self.assertEqual(self.f.store.revision(),revision+1); self.assertIsNone(self.f.summary()['undo'])
        self.assertEqual(self.c.STATE._statblocks,saved); self.assertIsNone(self.c.active_setup_reference())
        self.assertEqual(self.stored(target,result['setup']),content)
        self.assertEqual(self.f.store.load(checkpoint,source,'checkpoint')._statblocks,content)
        self.assert_private(result); self.assert_private(self.c.public_state()); self.assert_private(self.c.display_state())
        self.assert_private(self.c.STATE)

    def test_failure_after_real_history_processing_rolls_back_copy_and_loaded_move(self):
        self.history(); target = self.c.STORAGE.create_campaign('Other','','now')
        for mode in ('copy','move'):
            with self.subTest(mode=mode):
                before = self.dump(); state = copy.deepcopy(self.c.STATE); revision = self.f.store.revision()
                seen = self.emitter(); after = self.f.after_transaction; observed = []
                def fail_after_history(*args):
                    after(*args); observed.append((self.f.store.revision(),self.f.summary()['undo']))
                    raise OSError('injected after boundary history processing')
                with patch.object(self.f,'after_transaction',side_effect=fail_after_history):
                    with self.assertRaises(OSError): self.transfer(target,mode)
                self.assertEqual(observed,[(revision+(mode=='move'),None)])
                self.assertEqual(self.dump(),before); self.assertEqual(dict(self.c.STATE),dict(state))
                self.assertEqual(self.c.STATE._statblocks,state._statblocks); self.assertEqual(seen,[])
                self.assertFalse(self.c.STORAGE.connection.in_transaction)
                self.assertFalse(self.c._database_broadcast_pending); self.assertFalse(self.c._defer_database_broadcast)

    def test_pre_move_checkpoint_cannot_recreate_or_overwrite_missing_source_setup(self):
        checkpoint = self.history(); target = self.c.STORAGE.create_campaign('Other','','now')
        result = self.transfer(target,'move'); content = self.stored(target,result['setup'])
        before = self.dump(); state = copy.deepcopy(self.c.STATE); seen = self.emitter()
        with self.assertRaises(self.c.HTTPException) as error:
            self.call('restore_checkpoint',checkpoint,{'confirm':True,'revision':self.f.store.revision()})
        self.assertEqual(error.exception.status_code,409)
        self.assertEqual(self.dump(),before); self.assertEqual(self.stored(target,result['setup']),content)
        self.assertEqual(dict(self.c.STATE),dict(state)); self.assertEqual(self.c.STATE._statblocks,state._statblocks)
        self.assertEqual(seen,[])


class TransferHTTPTests(TransferFixture, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        TransferFixture.setUp(self)
        from fastapi import FastAPI, HTTPException
        from python.scrying_glass_service_auth import AuthService
        from python import scrying_glass_api_admin as api
        self.seed(self.secret); self.c.HTTPException = HTTPException
        self.target = self.c.STORAGE.create_campaign('Other','','now')
        self.ids = {}; self.c.SESSIONS = {}; self.c.ADMIN_SESSION_COOKIE = 'admin'
        for name, role in (('alice','admin'),('bob','admin'),('viewer','client'),('root','superadmin')):
            self.ids[name] = str(self.c.STORAGE.connection.execute(
                'INSERT INTO users(username,role,password_hash) VALUES (?,?,?)',(name,role,'unused-session-fixture')).lastrowid)
            self.c.SESSIONS[name+'-token'] = {'username':name,'role':role}
        auth = AuthService(self.c)
        self.c.user = auth.user; self.c.require = auth.require; self.c.auth_session = auth.session
        self.owner = ownership(self.c); self.owner.initialize()
        self.grant(self.c.active_campaign(),'alice'); self.grant(self.target,'alice')
        self.c.CampaignSetupAdd = CampaignSetupAdd
        self.app = FastAPI(); admin = api.AdminAPI.__new__(api.AdminAPI)
        admin.context = self.c; admin.app = self.app
        routes = tuple(row for row in api.ADMIN_ROUTES if row[1]=='add_setup_to_campaign')
        self.assertEqual(len(routes),1)
        with patch.object(api,'ADMIN_ROUTES',routes): admin.register_routes()

    def grant(self, campaign, name):
        self.owner.reassign(campaign,{'owner_user_id':self.ids[name]})

    async def request(self, *, token='alice-token', mode='copy', origin='http://fixture.test'):
        path = '/api/campaigns/' + self.target + '/setups'
        body = json.dumps({'from_campaign':self.c.active_campaign(),'setup':'default','mode':mode}).encode()
        headers = [(b'host',b'fixture.test'),(b'content-type',b'application/json'),(b'content-length',str(len(body)).encode()),(b'origin',origin.encode())]
        if token is not None: headers.append((b'cookie',('admin='+token).encode()))
        scope = dict(type='http',asgi={'version':'3.0','spec_version':'2.3'},http_version='1.1',method='POST',scheme='http',path=path,raw_path=path.encode(),query_string=b'',root_path='',headers=headers,client=('127.0.0.1',1234),server=('fixture.test',80))
        sent = False; messages = []
        async def receive():
            nonlocal sent
            if not sent:
                sent = True; return {'type':'http.request','body':body,'more_body':False}
            return {'type':'http.disconnect'}
        async def send(message): messages.append(message)
        await self.app(scope,receive,send)
        status = next(message['status'] for message in messages if message['type']=='http.response.start')
        response = json.loads(b''.join(message.get('body',b'') for message in messages if message['type']=='http.response.body'))
        return status,response

    async def test_real_session_role_origin_source_and_target_denials_do_not_transfer(self):
        cases = ((None,'alice','copy','http://fixture.test',401),
                 ('viewer-token','alice','copy','http://fixture.test',403),
                 ('alice-token','bob','copy','http://fixture.test',403),
                 ('bob-token','bob','move','http://fixture.test',403),
                 ('alice-token','alice','copy','http://evil.test',403),
                 ('alice-token','alice','invalid','http://fixture.test',422))
        for token, target_owner, mode, origin, expected in cases:
            with self.subTest(token=token,mode=mode,origin=origin):
                self.grant(self.target,target_owner); before = self.dump(); state = copy.deepcopy(self.c.STATE)
                with patch.object(self.c.STORAGE,'transfer_setup',wraps=self.c.STORAGE.transfer_setup) as transfer:
                    status,response = await self.request(token=token,mode=mode,origin=origin)
                    self.assertEqual(status,expected); transfer.assert_not_called()
                self.assertEqual(self.dump(),before); self.assertEqual(dict(self.c.STATE),dict(state))
                self.assertEqual(self.c.STATE._statblocks,state._statblocks); self.assertIsNone(actor(self.c))
                self.assert_private(response)

    async def test_owned_copy_then_loaded_move_and_superadmin_copy_keep_private_responses(self):
        original = self.stored(); source = self.c.active_campaign()
        for token, mode in (('alice-token','copy'),('root-token','copy'),('alice-token','move')):
            with self.subTest(token=token,mode=mode):
                status,response = await self.request(token=token,mode=mode)
                self.assertEqual(status,200); self.assert_private(response); self.assertIsNone(actor(self.c))
                self.assertEqual(self.stored(self.target,response['setup'])['m']['content_digest'],original['m']['content_digest'])
                self.assertEqual(self.c.active_campaign(),source)
                self.assert_private(self.c.public_state()); self.assert_private(self.c.display_state())
        self.assertIsNone(self.c.active_setup_reference())
        self.assertFalse(self.c.STORAGE.setup_exists(source,'default'))
        self.c.STORAGE._check_foreign_keys()


if __name__ == '__main__': unittest.main()
