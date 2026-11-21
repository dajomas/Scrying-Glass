"""022.15 statblock collection when monsters are added, on native SQLite.

Fake preparation runner and the real scheduler and transactional save (the
ImportFixture of test_statblock_import_service); no network, FastAPI or browser.
The Add Monster/Import handlers' calls are covered in test_monster_bonus_import.
"""
import asyncio
import copy
import hashlib
import threading
import unittest

import test_statblock_import_service as service_tests
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_statblock_collecting import collect_after_add
from python.scrying_glass_statblock_contract import PreparationFailure, StatblockAPIError

GOBLIN_MM = {'root': 'https://5e.tools/data', 'name': 'Goblin', 'source': 'MM'}
FILE = b'{"name": "Owlbear", "type": "monstrosity", "ac": 13, "hp": 59}'


class CollectionTests(service_tests.ImportFixture, unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        service_tests.ImportFixture.setUp(self)
        self.failure = None
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

    def add(self, template, *idents):
        """Like Add Monster: copies of a monster (with its source fields) appended and saved."""
        source = next(m for m in self.c.STATE['monsters'] if m['id'] == template)
        created = []
        for ident in idents:
            monster = copy.deepcopy(source)
            monster.update(id=ident, name=f'Goblin {ident}')
            created.append(monster)
        self.c.STATE['monsters'].extend(created)
        self.c.save_active_setup_monsters(); self.c.save_state(); self.c.load_state()
        return created

    def monster(self, ident):
        return next(m for m in self.c.STATE['monsters'] if m['id'] == ident)

    async def finished(self, job):
        """Wait until the job's save (if any) has run; -> number of monsters saved."""
        self.assertTrue(await self.settle(lambda: job.finished()))
        future = job.info.get('future')
        if future is None:
            return 0
        self.assertTrue(await self.settle(future.done))
        return future.result()

    async def test_add_from_a_source_collects_one_statblock_for_every_copy(self):
        created = self.add('m', 'x1', 'x2')
        job = collect_after_add(self.c, created)
        self.assertIsNotNone(job)
        self.assertEqual(await self.finished(job), 2)
        stored = self.stored()
        self.assertEqual(stored['x1']['source_label'], '5e.tools Goblin')
        self.assertEqual(stored['x1']['content_digest'], stored['x2']['content_digest'])
        self.assertEqual(self.runs, [('5e.tools', GOBLIN_MM)])  # the same source, prepared once
        self.assertNotIn('m', stored)  # only the added monsters

    async def test_import_uses_the_file_as_the_statblock(self):
        created = self.add('n', 'f1')
        job = collect_after_add(self.c, created, file_bytes=FILE, filename='owlbear.monster')
        self.assertEqual(await self.finished(job), 1)
        self.assertIn('f1', self.stored())
        self.assertEqual(self.runs, [('file', {'sha256': hashlib.sha256(FILE).hexdigest(),
                                                'filename': 'owlbear.monster'})])

    async def test_nothing_is_collected_without_a_source_or_a_usable_provider(self):
        created = self.add('n', 'y1')  # manual add: no selected source
        self.assertIsNone(collect_after_add(self.c, created))
        self.display.update(fivetools_fallback=False)
        self.assertIsNone(collect_after_add(self.c, self.add('m', 'y2')))
        self.assertIsNone(collect_after_add(self.c, created, file_bytes=b''))
        self.assertEqual(self.runs, [])
        self.assertEqual(self.stored(), {})

    async def test_an_unavailable_statblock_leaves_the_monsters_without_one(self):
        self.failure = 'statblock_unavailable'
        created = self.add('m', 'z1')
        job = collect_after_add(self.c, created)
        self.assertEqual(await self.finished(job), 0)
        self.assertEqual(self.stored(), {})
        self.assertEqual(self.monster('z1')['name'], 'Goblin z1')  # the add itself is untouched

    async def decide(self, collected_id, decision, revision):
        principal = self.service.authorize('alice-token')
        async def decide_collected_statblock():
            return self.service.collected_decide(principal, collected_id,
                                                 {'decision': decision, 'expected_statblock_revision': revision})
        return await transactional_handler(self.c, decide_collected_statblock)()

    def held(self):
        return {row['monster_id']: row for row in self.service.collected_list(self.service.authorize('alice-token'))['items']}

    async def test_changed_monsters_wait_for_confirmation_and_removed_ones_are_skipped(self):
        self.gate = threading.Event()
        created = self.add('m', 'c1', 'c2', 'c3')
        job = collect_after_add(self.c, created)
        self.monster('c1')['monster_species'] = 'Hobgoblin'  # edited while the statblock was collected
        self.c.STATE['monsters'] = [m for m in self.c.STATE['monsters'] if m['id'] != 'c2']  # removed
        self.c.save_active_setup_monsters(); self.c.save_state(); self.c.load_state()
        self.gate.set()
        self.assertEqual(await self.finished(job), 1)
        self.assertEqual(sorted(self.stored()), ['c3'])
        held = self.held()
        self.assertEqual(sorted(held), ['c1'])
        self.assertEqual((held['c1']['reasons'], held['c1']['statblock_revision']), (['changed'], 0))
        self.assertEqual(held['c1']['live']['species'], 'Hobgoblin')
        self.assertEqual(held['c1']['preview']['source_label'], '5e.tools Goblin')
        await self.decide(held['c1']['collected_id'], 'replace', 0)
        self.assertEqual(sorted(self.stored()), ['c1', 'c3'])
        self.assertEqual(self.held(), {})
        again = collect_after_add(self.c, [self.monster('c3')])
        self.assertEqual(await self.finished(again), 0)
        self.assertEqual(self.held(), {})  # the identical statblock is already saved: no question

    async def test_a_different_statblock_is_replaced_only_after_confirmation(self):
        self.gate = threading.Event()
        created = self.add('m', 'd1', 'd2')
        job = collect_after_add(self.c, created)
        async def choose_in_edit():  # meanwhile a statblock is chosen in Edit Monster
            for ident in ('d1', 'd2'):
                self.service._ensure_private()[ident] = service_tests.prepared('Chosen in Edit')
        await transactional_handler(self.c, choose_in_edit)()
        self.gate.set()
        self.assertEqual(await self.finished(job), 0)
        held = self.held()
        self.assertEqual(held['d1']['reasons'], ['has_statblock'])
        self.assertEqual(held['d1']['current_source_label'], 'Chosen in Edit')
        revision = held['d1']['statblock_revision']
        self.assertGreater(revision, 0)
        with self.assertRaises(StatblockAPIError) as caught:  # the statblock changed after the question
            await self.decide(held['d1']['collected_id'], 'replace', revision + 1)
        self.assertEqual(caught.exception.code, 'stale_revision')
        await self.decide(held['d1']['collected_id'], 'replace', revision)
        await self.decide(held['d2']['collected_id'], 'keep', held['d2']['statblock_revision'])
        stored = self.stored()
        self.assertEqual((stored['d1']['source_label'], stored['d2']['source_label']),
                         ('5e.tools Goblin', 'Chosen in Edit'))
        self.assertEqual(self.held(), {})
        with self.assertRaises(StatblockAPIError) as caught:
            await self.decide(held['d2']['collected_id'], 'replace', held['d2']['statblock_revision'])
        self.assertEqual(caught.exception.code, 'collected_expired')

    async def test_held_statblocks_expire_and_requests_are_validated(self):
        self.gate = threading.Event()
        job = collect_after_add(self.c, self.add('m', 'e1'))
        self.monster('e1')['monster_species'] = 'Hobgoblin'
        self.c.save_active_setup_monsters(); self.c.save_state(); self.c.load_state()
        self.gate.set()
        await self.finished(job)
        held = self.held()['e1']
        for body in ({}, {'decision': 'maybe', 'expected_statblock_revision': 0},
                     {'decision': 'replace', 'expected_statblock_revision': -1},
                     {'decision': 'replace', 'expected_statblock_revision': 0, 'x': 1}):
            with self.subTest(body=body), self.assertRaises(StatblockAPIError) as caught:
                self.service.collected_decide(self.service.authorize('alice-token'), held['collected_id'], body)
            self.assertEqual(caught.exception.code, 'invalid_request')
        for entry in self.service._collected().values():
            entry['expires'] = 0
        self.assertEqual(self.held(), {})

    async def test_a_context_without_the_service_and_any_failure_never_fail_the_add(self):
        created = self.add('m', 'w1')
        statblocks, self.c.statblocks = self.c.statblocks, None
        try:
            self.assertIsNone(collect_after_add(self.c, created))
        finally:
            self.c.statblocks = statblocks
        broken = type('Broken', (), {'collect_new_monsters': lambda *a, **k: 1 / 0})()
        self.c.statblocks = broken
        try:
            self.assertIsNone(collect_after_add(self.c, created))
        finally:
            self.c.statblocks = statblocks


if __name__ == '__main__':
    unittest.main()
