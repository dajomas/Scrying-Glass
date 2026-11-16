"""2C.3c selected-route Save As authorization using real seeded sessions.

No password login/full server or real-network WebSocket coverage is claimed.
"""
import asyncio
import copy
import unittest
from unittest.mock import patch
import test_statblock_2b_boundaries as boundaries
from python.scrying_glass_campaign_ownership import actor
from python.scrying_glass_classes import CampaignSetupAdd, SetupName
from python.scrying_glass_database_transactions import operation_lock
from python.scrying_glass_service_auth import AuthService
from python.scrying_glass_service_features import fingerprint
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_restore import restore_bindings


class SetupSavingHTTPTests(boundaries.BoundaryFixture, unittest.IsolatedAsyncioTestCase):
    request = boundaries.RecoveryRouteBoundaryTests.request
    secret = 'PRIVATE_2C_SAVE_AS_AUTH'

    def setUp(self):
        boundaries.BoundaryFixture.setUp(self)
        from fastapi import FastAPI
        from python import scrying_glass_api_admin as api
        self.source = self.c.active_campaign()
        self.inactive = self.c.STORAGE.create_campaign('Owned inactive campaign', '', 'now')
        self.owner.reassign(self.inactive, {'owner_user_id':self.ids['alice']})
        self.c.SetupName = SetupName; self.c.CampaignSetupAdd = CampaignSetupAdd
        self.app = FastAPI(); admin = api.AdminAPI.__new__(api.AdminAPI)
        admin.context = self.c; admin.app = self.app
        routes = tuple(row for row in api.ADMIN_ROUTES if row[1] in {'save_setup','add_setup_to_campaign'})
        self.assertEqual(len(routes), 2)
        with patch.object(api, 'ADMIN_ROUTES', routes): admin.register_routes()
        self.f.store.save_snapshot(self.source, self.c.STATE, 'checkpoint', 'Private checkpoint')
        self.f.store.save_snapshot(self.source, self.c.STATE, 'undo', 'Private undo', fingerprint(self.c.STATE))

    def body(self, name='http-save-as'):
        return {'name':name, 'campaign':self.source}

    def assert_private_frames(self):
        for sent in self.sends: self.assert_private_response(sent['frame'])
        self.assert_private_response(self.c.public_state())
        self.assert_private_response(self.c.display_state())
        self.assertIsNone(actor(self.c))

    async def test_owner_save_as_carries_live_private_edits_without_changing_source(self):
        original = copy.deepcopy(self.stored()); source_bindings = restore_bindings(self.c.STORAGE, self.encounter())
        self.c.STATE['monsters'][0]['hp'] = 7
        value = self.c.STATE._statblocks['m']; value.pop('content_digest', None)
        value['source_label'] = self.secret+' live edit'
        status, response = await self.request('/api/setups/save', self.body())
        self.assertEqual((status,response), (200, {'name':'http-save-as','campaign':self.source}))
        saved = self.stored(name='http-save-as')
        self.assertEqual(saved['m']['source_label'], self.secret+' live edit')
        self.assertEqual(saved['m']['revision'], 1)
        self.assertNotEqual(saved['m']['prepared_at'], original['m']['prepared_at'])
        self.assertEqual(self.stored(), original)
        self.assertEqual(restore_bindings(self.c.STORAGE, self.encounter()), source_bindings)
        self.assertNotEqual(restore_bindings(self.c.STORAGE, self.encounter(name='http-save-as'))['m'][0], source_bindings['m'][0])
        self.assertEqual(self.c.STATE._statblocks, saved)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, saved)
        self.assertEqual(self.c.STATE['monsters'][0]['hp'], 7); self.assert_private_frames()

    async def test_existing_superadmin_save_permission_is_not_restricted_to_owner(self):
        self.owner.reassign(self.source, {'owner_user_id':self.ids['bob']})
        original = copy.deepcopy(self.stored())
        status, response = await self.request('/api/setups/save', self.body('root-save-as'), token='root-token')
        self.assertEqual((status,response), (200, {'name':'root-save-as','campaign':self.source}))
        self.assertEqual(self.stored(), original)
        self.assertEqual(self.stored(name='root-save-as')['m']['content_digest'], original['m']['content_digest'])
        self.assert_private_frames()

    async def test_save_denials_leave_sql_private_counters_history_and_live_state_unchanged(self):
        cases = [(self.body(), {'token':None}, 401),
                 (self.body(), {'token':'viewer-token'}, 403),
                 (self.body(), {'token':'bob-token'}, 403),
                 (self.body(), {'origin':'http://evil.test'}, 403),
                 ({'name':'foreign', 'campaign':self.other}, {}, 403),
                 ({'name':'inactive', 'campaign':self.inactive}, {}, 409),
                 ({'name':'', 'campaign':self.source}, {}, 422)]
        for body, options, expected in cases:
            with self.subTest(body=body, options=options):
                before = self.dump(); state = copy.deepcopy(self.c.STATE)
                with patch.object(self.c.STORAGE, 'save_setup', wraps=self.c.STORAGE.save_setup) as save:
                    status, _ = await self.request('/api/setups/save', body, **options)
                    self.assertEqual(status, expected); save.assert_not_called()
                self.assert_unchanged(before, state)

    async def test_waiting_save_rechecks_live_ownership_role_and_session(self):
        real_session = AuthService.session
        for change, expected in (('ownership',403), ('role',401), ('session',401)):
            with self.subTest(change=change):
                with self.c.STORAGE.transaction():
                    self.c.STORAGE.connection.execute("UPDATE users SET role='admin' WHERE username='alice'")
                    self.owner.reassign(self.source, {'owner_user_id':self.ids['alice']})
                self.c.SESSIONS['alice-token'] = {'username':'alice','role':'admin'}
                checked = asyncio.Event(); task = None
                def observe_session(auth, token):
                    result = real_session(auth, token)
                    if auth.context is self.c and token == 'alice-token' and result: checked.set()
                    return result
                try:
                    with patch.object(AuthService, 'session', new=observe_session):
                        async with operation_lock(self.c):
                            task = asyncio.create_task(self.request('/api/setups/save', self.body('revoked-save')))
                            await asyncio.wait_for(checked.wait(), timeout=5)
                            with self.c.STORAGE.transaction():
                                if change == 'ownership':
                                    self.owner.reassign(self.source, {'owner_user_id':self.ids['bob']})
                                elif change == 'role':
                                    self.c.STORAGE.connection.execute("UPDATE users SET role='client' WHERE username='alice'")
                                else:
                                    self.c.SESSIONS.pop('alice-token')
                            before = self.dump(); state = copy.deepcopy(self.c.STATE)
                        status, _ = await asyncio.wait_for(task, timeout=5)
                        self.assertEqual(status, expected); self.assert_unchanged(before, state)
                finally:
                    if task is not None:
                        if not task.done(): task.cancel()
                        await asyncio.gather(task, return_exceptions=True)

    async def test_authenticated_save_copy_move_runtime_save_sequence_preserves_saved_owners(self):
        self.owner.reassign(self.other, {'owner_user_id':self.ids['alice']})
        original = copy.deepcopy(self.stored()); original_owner = self.encounter()
        status, _ = await self.request('/api/setups/save', self.body('http-first'))
        self.assertEqual(status, 200)
        first_owner = self.encounter(name='http-first'); first = copy.deepcopy(self.stored(name='http-first'))
        first_bindings = restore_bindings(self.c.STORAGE, first_owner)
        path = '/api/campaigns/'+self.other+'/setups'
        body = {'from_campaign':self.source, 'setup':'http-first', 'mode':'copy'}
        status, copied = await self.request(path, body); self.assertEqual(status, 200)
        copy_owner = self.encounter(self.other, copied['setup']); copied_private = copy.deepcopy(self.stored(self.other, copied['setup']))
        body['mode'] = 'move'
        status, moved = await self.request(path, body); self.assertEqual(status, 200)
        self.assertNotEqual(moved['setup'], copied['setup'])
        self.assertEqual(self.encounter(self.other, moved['setup']), first_owner)
        self.assertFalse(self.c.STORAGE.setup_exists(self.source, 'http-first'))
        self.assertIsNone(self.c.active_setup_reference())
        runtime = self.current_encounter()
        self.assertNotIn(runtime, (original_owner, first_owner, copy_owner))
        runtime_private = PrivateEncounterStorage(self.c.STORAGE).load(runtime)[PRIVATE_KEY]
        self.assertEqual(runtime_private['m']['content_digest'], first['m']['content_digest'])
        self.assertEqual(runtime_private['m']['revision'], 1)
        status, _ = await self.request('/api/setups/save', self.body('http-final'))
        self.assertEqual(status, 200)
        final_owner = self.encounter(name='http-final'); final = self.stored(name='http-final')
        self.assertNotIn(final_owner, (original_owner, first_owner, copy_owner, runtime))
        self.assertEqual(final['m']['revision'], 1)
        self.assertEqual(final['m']['content_digest'], first['m']['content_digest'])
        self.assertEqual(self.stored(), original)
        self.assertEqual(self.stored(self.other, moved['setup']), first)
        self.assertEqual(restore_bindings(self.c.STORAGE, first_owner), first_bindings)
        self.assertEqual(self.stored(self.other, copied['setup']), copied_private)
        self.assertEqual(self.c.active_campaign(), self.source)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, final)
        self.assertEqual(self.c.active_setup_reference()['name'], 'http-final')
        self.assert_private_frames()
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])


if __name__ == '__main__': unittest.main()
