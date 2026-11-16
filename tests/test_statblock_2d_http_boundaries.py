"""2D import-route authorization and production notification/history boundaries.

Real selected AdminAPI installer, seeded sessions and recording sockets; not password
login, full application startup, provider fetches or real-network WebSockets.
"""
import asyncio
import copy
import json
import unittest
from unittest.mock import patch
import test_statblock_2b_boundaries as boundaries
import test_statblock_setup_importing as imports
import test_statblock_stage2_contracts as contracts
from python import scrying_glass_statblock_importing as importing
from python.scrying_glass_campaign_ownership import actor
from python.scrying_glass_classes import SetupImport
from python.scrying_glass_database_transactions import operation_lock, transactional_handler
from python.scrying_glass_service_auth import AuthService
from python.scrying_glass_service_features import fingerprint
from python.scrying_glass_service_notifications import NotificationsService
from python.scrying_glass_statblock_detaching import detach_loaded_setup
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_restore import restore_bindings


class SetupImportHTTPBoundaryTests(boundaries.BoundaryFixture, unittest.IsolatedAsyncioTestCase):
    request = boundaries.RecoveryRouteBoundaryTests.request
    assert_content = contracts.StatblockStage2ContractTests.assert_content
    secret = 'PRIVATE_2D_HTTP_IMPORT'

    def setUp(self):
        boundaries.BoundaryFixture.setUp(self)
        from fastapi import FastAPI
        from python import scrying_glass_api_admin as api
        self.destination = self.c.active_campaign(); db = self.c.STORAGE
        adapter = PrivateEncounterStorage(db); state = adapter.load(self.encounter())
        state[PRIVATE_KEY]['m'] = imports.graph(self.secret)
        adapter.save(self.encounter(), state); self.c.load_state()
        db.save_setup(self.other, 'import-source', self.c.setup_snapshot(self.c.STATE))
        owner = self.encounter(self.other, 'import-source'); state = adapter.load(owner)
        state[PRIVATE_KEY]['m'] = imports.graph(self.secret+' remote')
        adapter.save(owner, state)
        self.checkpoint_metadata = copy.deepcopy(self.c.STATE._statblocks)
        self.checkpoint_id = self.f.store.save_snapshot(self.destination, self.c.STATE, 'checkpoint', 'Before import')
        self.undo_id = self.f.store.save_snapshot(self.destination, self.c.STATE, 'undo', 'Before import', fingerprint(self.c.STATE))
        self.c.SetupImport = SetupImport
        self.app = FastAPI(); admin = api.AdminAPI.__new__(api.AdminAPI)
        admin.context = self.c; admin.app = self.app
        routes = tuple(row for row in api.ADMIN_ROUTES if row[1] == 'import_setup')
        self.assertEqual(len(routes), 1)
        with patch.object(api, 'ADMIN_ROUTES', routes): admin.register_routes()
        self.assertIs(self.c.broadcast.__func__, NotificationsService.broadcast)

    def body(self, *, remote=True, life_filter='all'):
        return {'name':'import-source' if remote else 'default',
                'campaign':self.other if remote else self.destination,
                'kind':'monsters', 'life_filter':life_filter}

    def grant_both(self):
        for campaign in (self.destination, self.other):
            self.owner.reassign(campaign, {'owner_user_id':self.ids['alice']})

    def assert_private_response(self, value):
        boundaries.BoundaryFixture.assert_private_response(self, value)
        text = json.dumps(value)
        for marker in ('Private fixture credit', 'Private import warning'):
            self.assertNotIn(marker, text)

    def assert_checkpoint(self):
        image = self.f.store.load(self.checkpoint_id, self.destination, 'checkpoint')
        self.assertEqual(image._statblocks, self.checkpoint_metadata)

    def remote_image(self):
        owner = self.encounter(self.other, 'import-source')
        return (PrivateEncounterStorage(self.c.STORAGE).load(owner), restore_bindings(self.c.STORAGE, owner))

    async def test_owned_same_cross_and_runtime_imports_preserve_originals_and_clone_independently(self):
        self.grant_both()
        for mode in ('same', 'cross', 'runtime', 'superadmin'):
            with self.subTest(mode=mode):
                saved_setup = None
                if mode == 'runtime':
                    async def detach(): detach_loaded_setup(self.c)
                    await transactional_handler(self.c, detach)()
                if self.c.active_setup_reference() is None:
                    saved_setup = copy.deepcopy(self.stored())
                if mode == 'superadmin':
                    for campaign in (self.destination, self.other):
                        self.owner.reassign(campaign, {'owner_user_id':self.ids['bob']})
                remote = mode != 'same'; body = self.body(remote=remote)
                source_owner = self.encounter(body['campaign'], body['name'])
                source_image = PrivateEncounterStorage(self.c.STORAGE).load(source_owner)
                source_bindings = restore_bindings(self.c.STORAGE, source_owner)
                owner = self.current_encounter(); existing = copy.deepcopy(self.current_private())
                bindings = restore_bindings(self.c.STORAGE, owner)
                ids = {item['id'] for item in self.c.STATE['monsters']}
                self.sends.clear()
                token = 'root-token' if mode == 'superadmin' else 'alice-token'
                status, response = await self.request('/api/setups/import', body, token=token)
                self.assertEqual(status, 200); self.assertEqual(response['monsters'], 1)
                clones = [item for item in self.c.STATE['monsters'] if item['id'] not in ids]
                self.assertEqual(len(clones), 1); ident = clones[0]['id']; saved = self.current_private()
                self.assertEqual(set(saved), set(existing) | {ident})
                self.assert_content(saved[ident], source_image[PRIVATE_KEY]['m'])
                self.assertEqual(saved[ident]['revision'], 1)
                self.assertNotEqual(saved[ident]['prepared_at'], source_image[PRIVATE_KEY]['m']['prepared_at'])
                after = restore_bindings(self.c.STORAGE, owner)
                self.assertNotEqual(after[ident][0], source_bindings['m'][0])
                self.assertFalse(clones[0]['active']); self.assertFalse(clones[0]['in_turn'])
                for old in existing:
                    self.assertEqual(saved[old], existing[old]); self.assertEqual(after[old], bindings[old])
                if remote:
                    self.assertEqual(PrivateEncounterStorage(self.c.STORAGE).load(source_owner), source_image)
                    self.assertEqual(restore_bindings(self.c.STORAGE, source_owner), source_bindings)
                if saved_setup is not None:
                    self.assertIsNone(self.c.active_setup_reference()); self.assertEqual(self.stored(), saved_setup)
                self.assertEqual(self.c.STATE._statblocks, saved)
                self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, saved)
                for sent in self.sends: self.assert_private_response(sent['frame'])
                self.assertIsNone(actor(self.c)); self.assert_checkpoint()
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])

    async def test_import_auth_origin_scope_and_model_denials_are_atomic_and_private(self):
        local = self.body(remote=False)
        cases = [(local, {'token':None}, 401), (local, {'token':'viewer-token'}, 403),
                 (self.body(), {}, 403), (self.body(), {'token':'bob-token'}, 403),
                 (local, {'origin':'http://evil.test'}, 403),
                 ({**local,'life_filter':'invalid'}, {}, 422),
                 ({**local,'kind':'characters'}, {}, 422),
                 ({**local,'name':'missing'}, {}, 404)]
        for body, options, expected in cases:
            with self.subTest(body=body, options=options):
                before = self.dump(); state = copy.deepcopy(self.c.STATE)
                with patch.object(importing, 'prepare_setup_import', wraps=importing.prepare_setup_import) as prepare:
                    status, _ = await self.request('/api/setups/import', body, **options)
                    self.assertEqual(status, expected); prepare.assert_not_called()
                self.assert_unchanged(before, state)

    async def test_waiting_import_rechecks_source_destination_role_and_session(self):
        real_session = AuthService.session
        for change, expected in (('source',403), ('destination',403), ('role',401), ('session',401)):
            with self.subTest(change=change):
                with self.c.STORAGE.transaction():
                    self.c.STORAGE.connection.execute("UPDATE users SET role='admin' WHERE username='alice'")
                    self.grant_both()
                self.c.SESSIONS['alice-token'] = {'username':'alice','role':'admin'}
                checked = asyncio.Event(); task = None
                def observe_session(auth, token):
                    result = real_session(auth, token)
                    if auth.context is self.c and token == 'alice-token' and result: checked.set()
                    return result
                try:
                    with patch.object(AuthService, 'session', new=observe_session):
                        async with operation_lock(self.c):
                            task = asyncio.create_task(self.request('/api/setups/import', self.body()))
                            await asyncio.wait_for(checked.wait(), timeout=5)
                            with self.c.STORAGE.transaction():
                                if change in {'source','destination'}:
                                    campaign = self.other if change == 'source' else self.destination
                                    self.owner.reassign(campaign, {'owner_user_id':self.ids['bob']})
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

    async def test_real_broadcast_observes_final_clone_revision_history_and_private_metadata_once(self):
        self.grant_both(); source = self.remote_image(); revision = self.f.store.revision()
        existing = copy.deepcopy(self.current_private()); self.sends.clear()
        self.assertIsNotNone(self.f.summary()['undo'])
        with patch.object(self.c, 'broadcast', wraps=self.c.broadcast) as broadcast:
            status, _ = await self.request('/api/setups/import', self.body())
            self.assertEqual(status, 200); self.assertEqual(broadcast.await_count, 2)
        self.assertEqual(len(self.sends), 1); sent = self.sends[0]
        self.assertFalse(sent['in_transaction']); self.assertEqual(sent['revision'], revision+1)
        self.assertEqual(sent['frame']['revision'], revision+1)
        self.assertEqual(sent['metadata'], sent['stored']); self.assertEqual(sent['stored'], self.current_private())
        self.assertEqual(self.c.STATE._statblocks, sent['stored'])
        ident = next(key for key in sent['stored'] if key not in existing)
        self.assertEqual(sent['stored'][ident]['revision'], 1)
        self.assertEqual(sent['stored']['m'], existing['m'])
        self.assertIsNone(self.f.store.latest_undo(self.destination)); self.assert_checkpoint()
        self.assertEqual(self.remote_image(), source); self.assert_private_response(sent['frame'])
        self.assertFalse(self.c._database_broadcast_pending); self.assertFalse(self.c._defer_database_broadcast)
        self.assertIsNone(actor(self.c)); self.assertIn(self.socket, self.c.SOCKETS)

    async def test_real_import_late_history_failure_restores_everything_without_emission(self):
        self.grant_both(); before = self.dump(); state = copy.deepcopy(self.c.STATE)
        revision = self.f.store.revision(); after = self.f.after_transaction; observed = []
        def fail_after_history(*args):
            after(*args)
            self.assertEqual(self.c.STATE._statblocks, self.current_private())
            self.assertEqual(len(self.c.STATE._statblocks), len(state._statblocks)+1)
            self.assertEqual(self.sends, [])
            observed.append((self.c.STORAGE.connection.in_transaction,
                self.f.store.revision(), self.f.store.latest_undo(self.destination)))
            raise OSError('after real import history')
        with patch.object(self.f, 'after_transaction', side_effect=fail_after_history):
            with self.assertRaisesRegex(OSError, 'real import history'):
                await self.request('/api/setups/import', self.body())
        self.assertEqual(observed, [(True,revision+1,None)])
        self.assert_unchanged(before, state); self.assert_checkpoint()
        self.assertEqual(self.f.store.revision(), revision)
        self.assertIn(self.socket, self.c.SOCKETS)
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])

    async def test_empty_life_filter_keeps_history_graphs_and_revision_with_only_existing_refresh(self):
        metadata = copy.deepcopy(self.current_private()); revision = self.f.store.revision()
        ids = [item['id'] for item in self.c.STATE['monsters']]; self.sends.clear()
        with patch.object(self.c, 'broadcast', wraps=self.c.broadcast) as broadcast:
            status, response = await self.request('/api/setups/import', self.body(remote=False, life_filter='dead'))
            self.assertEqual(status, 200); self.assertEqual(response['monsters'], 0)
            self.assertEqual(broadcast.await_count, 2)
        self.assertEqual(len(self.sends), 1); sent = self.sends[0]
        self.assertFalse(sent['in_transaction']); self.assertEqual(sent['revision'], revision)
        self.assertEqual(sent['frame']['revision'], revision); self.assert_private_response(sent['frame'])
        self.assertEqual(sent['metadata'], metadata); self.assertEqual(sent['stored'], metadata)
        self.assertEqual(self.current_private(), metadata); self.assertEqual(self.c.STATE._statblocks, metadata)
        self.assertEqual([item['id'] for item in self.c.STATE['monsters']], ids)
        self.assertEqual(self.f.store.revision(), revision)
        self.assertEqual(self.f.store.latest_undo(self.destination)['id'], self.undo_id)
        self.assert_checkpoint(); self.assertIsNone(actor(self.c))
        self.assertFalse(self.c._database_broadcast_pending); self.assertFalse(self.c._defer_database_broadcast)


if __name__ == '__main__': unittest.main()
