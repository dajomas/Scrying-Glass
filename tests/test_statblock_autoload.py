"""022.12 automatic original-source loading through the statblock transport on native SQLite.

Recording listener sockets, a fake preparation runner and the real scheduler,
transactional save and broadcast; no network, FastAPI or browser.
"""
import asyncio
import json
import threading
import unittest

import test_statblock_import_service as service_tests
from python.scrying_glass_service_features import fingerprint
from python.scrying_glass_statblock_contract import PreparationFailure
from python.scrying_glass_statblock_transport import notify, sockets


class Socket:
    def __init__(self):
        self.frames = []

    async def send_text(self, text):
        self.frames.append(json.loads(text))

    async def close(self, code=1000, reason=''):
        self.closed = code


class AutoLoadTests(service_tests.ImportFixture, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        service_tests.ImportFixture.setUp(self)
        self.failure = None

    def runner(self):
        original = self.service.runner
        def run(provider, identity, job, file_bytes, config):
            if self.gate is not None:
                self.gate.wait(5)
            if self.failure:
                raise PreparationFailure(self.failure)
            return original(provider, identity, job, file_bytes, config)
        self.service.runner = run

    async def settle(self, predicate, seconds=5):
        for _ in range(int(seconds / 0.02)):
            if predicate():
                return True
            await asyncio.sleep(0.02)
        return False

    def tiles(self, socket):
        return {row['monster_id']: row for row in socket.frames[-1]['state']['tiles']}

    async def test_missing_original_statblock_loads_once_and_is_saved(self):
        self.runner()
        self.gate = threading.Event()
        socket = Socket(); sockets(self.c)[socket] = 'alice-token'
        await notify(self.c)
        self.assertEqual(self.tiles(socket)['m']['status'], 'loading')
        self.assertEqual(self.tiles(socket)['n']['status'], 'missing')  # no retained identity: never searched
        await notify(self.c)
        self.gate.set()
        self.assertTrue(await self.settle(lambda: 'm' in self.stored()))
        self.assertEqual(self.runs, [('5e.tools', {'root': 'https://5e.tools/data', 'name': 'Goblin', 'source': 'MM'})])
        self.assertTrue(await self.settle(lambda: self.tiles(socket)['m']['status'] == 'available'))
        self.assertEqual(self.tiles(socket)['m']['statblock_revision'], 1)
        await notify(self.c)
        self.assertEqual(len(self.runs), 1)

    async def test_undo_history_survives_automatic_loading(self):
        self.runner()
        await self.async_call_edit()
        top = self.f.store.latest_undo(self.c.active_campaign())
        self.assertIsNotNone(top)
        socket = Socket(); sockets(self.c)[socket] = 'alice-token'
        await notify(self.c)
        self.assertTrue(await self.settle(lambda: 'm' in self.stored()))
        after = self.f.store.latest_undo(self.c.active_campaign())
        self.assertEqual(after['id'], top['id'])
        self.assertEqual(after['after_digest'], fingerprint(self.c.STATE))

    async def async_call_edit(self):
        from python.scrying_glass_database_transactions import transactional_handler
        async def edit_features():
            return await self.f.edit_features('m', {'hp_delta': -1})
        await transactional_handler(self.c, edit_features)()

    async def test_failures_cool_down_or_stay_unavailable(self):
        self.runner()
        self.failure = 'provider_unavailable'
        socket = Socket(); sockets(self.c)[socket] = 'alice-token'
        await notify(self.c)
        self.assertTrue(await self.settle(lambda: self.tiles(socket)['m']['status'] == 'error'))
        self.assertIn('retry_at', self.tiles(socket)['m']['status_detail'])
        runs = len(self.runs)
        await notify(self.c)
        self.assertEqual(len(self.runs), runs)  # within the cooldown
        key = next(iter(self.service._auto))
        self.service._auto[key]['until'] = 0
        self.failure = 'not_found'
        await notify(self.c)
        self.assertTrue(await self.settle(lambda: self.tiles(socket)['m']['status'] == 'unavailable'))
        runs = len(self.runs)
        self.service._auto[key]['until'] = 0
        await notify(self.c)
        self.assertEqual(len(self.runs), runs)
        self.assertNotIn('m', self.stored())

    async def test_disabled_provider_no_viewer_and_changed_target_load_nothing(self):
        self.runner()
        await notify(self.c)  # nobody watching: no work
        self.assertEqual(self.runs, [])
        socket = Socket(); sockets(self.c)[socket] = 'alice-token'
        self.display['fivetools_fallback'] = False
        await notify(self.c)
        self.assertEqual(self.tiles(socket)['m']['status'], 'unavailable')
        self.assertEqual(self.tiles(socket)['m']['status_detail']['code'], 'provider_disabled')
        self.assertEqual(self.runs, [])
        self.display['fivetools_fallback'] = True
        self.gate = threading.Event()
        await notify(self.c)
        # The tracker source changes before the job completes: the stale result is discarded
        # and, with no retained identity left, nothing is loaded again.
        for key in ('monster_source_provider', 'monster_source_url', 'monster_source_name', 'monster_source_book'):
            self.item('m').pop(key)
        self.gate.set()
        self.assertTrue(await self.settle(lambda: not any(v['state'] == 'loading' for v in self.service._auto.values())))
        await asyncio.sleep(0.1)
        self.assertNotIn('m', self.stored())

    async def test_inactive_monsters_and_revoked_viewers_do_not_trigger_loads(self):
        self.runner()
        self.item('m')['active'] = False
        socket = Socket(); sockets(self.c)[socket] = 'alice-token'
        await notify(self.c)
        self.assertEqual(self.runs, [])
        self.item('m')['active'] = True
        sockets(self.c).clear()
        bob = Socket(); sockets(self.c)[bob] = 'bob-token'
        await notify(self.c)
        self.assertEqual(bob.frames[-1]['type'], 'revoked')
        self.assertEqual(sockets(self.c), {})
        await asyncio.sleep(0.1)
        self.assertEqual(self.runs, [])


if __name__ == '__main__':
    unittest.main()
