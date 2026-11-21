"""2C.3c production notification behavior for protected setup operations.

Real seeded-session ASGI routes and broadcast/deferral; recording sockets are not
real-network WebSockets. Unchanged explicit Save still requests its legacy refresh.
"""
import copy
import unittest
from unittest.mock import patch
import test_statblock_2b_boundaries as boundaries
import test_statblock_setup_saving_http as saving_http
from python.scrying_glass_campaign_ownership import actor
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_service_features import fingerprint
from python.scrying_glass_service_notifications import NotificationsService


class SetupNotificationTests(boundaries.BoundaryFixture, unittest.IsolatedAsyncioTestCase):
    setUp = saving_http.SetupSavingHTTPTests.setUp
    request = saving_http.SetupSavingHTTPTests.request
    body = saving_http.SetupSavingHTTPTests.body
    secret = 'PRIVATE_2C_NOTIFICATION'

    async def post(self, path, body, *, frames=1, revision_delta=None):
        self.assertIs(self.c.broadcast.__func__, NotificationsService.broadcast)
        before = self.f.store.revision(); self.sends.clear()
        with patch.object(self.c, 'broadcast', wraps=self.c.broadcast) as broadcast:
            status, response = await self.request(path, body)
            self.assertEqual(status, 200)
            self.assertEqual(broadcast.await_count, 2 if frames else 0)
        self.assertEqual(len(self.sends), frames)
        self.assertEqual(self.f.store.revision(), before+(frames if revision_delta is None else revision_delta))
        if frames:
            sent = self.sends[0]
            self.assertFalse(sent['in_transaction'])
            self.assertEqual(sent['revision'], self.f.store.revision())
            self.assertEqual(sent['frame']['revision'], sent['revision'])
            self.assertEqual(sent['metadata'], sent['stored'])
            self.assertEqual(sent['metadata'], self.c.STATE._statblocks)
            self.assertEqual(sent['stored'], self.current_private())
            self.assert_private_response(sent['frame'])
        self.assertIn(self.socket, self.c.SOCKETS)
        self.assertFalse(self.c._database_broadcast_pending); self.assertFalse(self.c._defer_database_broadcast)
        self.assertIsNone(actor(self.c))
        return response

    async def test_authenticated_sequence_emits_only_final_committed_metadata_once_per_changed_step(self):
        self.owner.reassign(self.other, {'owner_user_id':self.ids['alice']})
        original = copy.deepcopy(self.stored())
        await self.post('/api/setups/save', self.body('notify-first'))
        first_owner = self.encounter(name='notify-first'); first = copy.deepcopy(self.stored(name='notify-first'))
        self.assertEqual(self.sends[0]['metadata'], first)
        path = '/api/campaigns/'+self.other+'/setups'
        body = {'from_campaign':self.source, 'setup':'notify-first', 'mode':'copy'}
        state = copy.deepcopy(self.c.STATE)
        copied = await self.post(path, body, frames=0)
        self.assertEqual(dict(self.c.STATE), dict(state)); self.assertEqual(self.c.STATE._statblocks, state._statblocks)
        copied_private = copy.deepcopy(self.stored(self.other, copied['setup']))
        body['mode'] = 'move'
        moved = await self.post(path, body)
        self.assertNotEqual(moved['setup'], copied['setup'])
        self.assertEqual(self.encounter(self.other, moved['setup']), first_owner)
        self.assertIsNone(self.c.active_setup_reference())
        self.assertEqual(self.sends[0]['metadata']['m']['revision'], 1)
        self.assertEqual(self.sends[0]['metadata']['m']['content_digest'], first['m']['content_digest'])
        self.assertIsNone(self.f.store.latest_undo(self.source))
        await self.post('/api/setups/save', self.body('notify-final'))
        self.assertEqual(self.sends[0]['metadata'], self.stored(name='notify-final'))
        self.assertEqual(self.c.active_setup_reference()['name'], 'notify-final')
        self.assertEqual(self.stored(), original)
        self.assertEqual(self.stored(self.other, moved['setup']), first)
        self.assertEqual(self.stored(self.other, copied['setup']), copied_private)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, self.stored(name='notify-final'))
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])

    async def test_unchanged_explicit_save_has_no_extra_frame_or_revision_and_true_noop_is_silent(self):
        metadata = copy.deepcopy(self.current_private()); revision = self.f.store.revision()
        undo = self.f.store.latest_undo(self.source)['id']
        await self.post('/api/setups/save', self.body('default'), revision_delta=0)
        self.assertEqual(self.current_private(), metadata)
        self.assertEqual(self.f.store.latest_undo(self.source)['id'], undo)
        before = self.dump(); state = copy.deepcopy(self.c.STATE); self.sends.clear()
        async def no_op(): return {'ok':True}
        with patch.object(self.c, 'broadcast', wraps=self.c.broadcast) as broadcast:
            result = await transactional_handler(self.c, no_op)()
            broadcast.assert_not_awaited()
        self.assertEqual(result, {'ok':True}); self.assert_unchanged(before, state)
        self.assertEqual(self.f.store.revision(), revision)

    async def test_late_history_failures_emit_nothing_for_save_as_copy_and_loaded_move(self):
        self.owner.reassign(self.other, {'owner_user_id':self.ids['alice']})
        await self.post('/api/setups/save', self.body('notify-source'))
        self.f.store.save_snapshot(self.source, self.c.STATE, 'checkpoint', 'Retained private checkpoint')
        self.f.store.save_snapshot(self.source, self.c.STATE, 'undo', 'Retained undo', fingerprint(self.c.STATE))
        path = '/api/campaigns/'+self.other+'/setups'
        cases = [('save', '/api/setups/save', self.body('notify-failed'), 1),
                 ('copy', path, {'from_campaign':self.source,'setup':'notify-source','mode':'copy'}, 0),
                 ('move', path, {'from_campaign':self.source,'setup':'notify-source','mode':'move'}, 1)]
        after = self.f.after_transaction
        for name, route, body, revision_delta in cases:
            with self.subTest(operation=name):
                self.sends.clear(); before = self.dump(); state = copy.deepcopy(self.c.STATE)
                revision = self.f.store.revision(); observed = []
                def fail_after_history(*args):
                    after(*args)
                    observed.append((self.c.STORAGE.connection.in_transaction,
                        self.f.store.revision(), self.f.store.latest_undo(self.source)))
                    self.assertEqual(self.sends, [])
                    raise OSError('injected after notification history')
                with patch.object(self.f, 'after_transaction', side_effect=fail_after_history):
                    with self.assertRaisesRegex(OSError, 'notification history'):
                        await self.request(route, body)
                self.assertEqual(observed, [(True, revision+revision_delta, None)])
                self.assert_unchanged(before, state)
                self.assertEqual(self.f.store.revision(), revision)
                self.assertIn(self.socket, self.c.SOCKETS)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, self.stored(name='notify-source'))
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])


if __name__ == '__main__': unittest.main()
