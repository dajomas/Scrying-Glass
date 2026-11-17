"""022.08 building blocks: limits, shared fetching, job scheduling and selection stores.

Pure in-process tests with fake clocks/transports; no network, FastAPI or browser.
"""
import threading
import time
import unittest

from test_statblock_encounters import snapshot
from python.scrying_glass_statblock_fetching import FetchFailure, SharedFetcher
from python.scrying_glass_statblock_jobs import Job, JobCapacity, JobScheduler
from python.scrying_glass_statblock_limits import StatblockLimits
from python.scrying_glass_statblock_model import content_digest
from python.scrying_glass_statblock_selections import Scope, SelectionError, SelectionStore


class Clock:
    def __init__(self, value=1000.0):
        self.value = value

    def __call__(self):
        return self.value


def prepared(label):
    value = snapshot(label)
    value['content_digest'] = content_digest(value)
    return value


def scope(session='s', monster='m'):
    return Scope(session, '1', '1', 'token', monster, 'Goblin', ())


class LimitTests(unittest.TestCase):
    def test_defaults_match_the_agreed_contract(self):
        limits = StatblockLimits()
        self.assertEqual((limits.preparation_seconds, limits.active_jobs, limits.queued_jobs, limits.selection_seconds,
                          limits.selection_references, limits.session_selection_references), (10, 2, 16, 600, 1000, 200))
        self.assertEqual(len(limits.__dataclass_fields__), 26)

    def test_configuration_is_validated(self):
        self.assertEqual(StatblockLimits.from_config({}).active_jobs, 2)
        self.assertEqual(StatblockLimits.from_config({'statblocks': {'limits': {'active_jobs': 3}}}).active_jobs, 3)
        for bad in ({'statblocks': {'limits': {'unknown': 1}}}, {'statblocks': {'limits': {'active_jobs': 0}}},
                    {'statblocks': {'limits': {'active_jobs': True}}}, {'statblocks': {'other': {}}},
                    {'statblocks': {'limits': []}}):
            with self.assertRaises(ValueError):
                StatblockLimits.from_config(bad)

    def test_preparation_limits_use_the_configured_values(self):
        limits = StatblockLimits(inheritance_steps=5, reference_steps=4, snapshot_bytes=4096, supporting_definitions=9)
        preparation = limits.preparation()
        self.assertEqual((preparation.resolution.inheritance_steps, preparation.collection.reference_steps,
                          preparation.model.snapshot_bytes, preparation.collection.supporting_definitions,
                          preparation.model.supporting_definitions), (5, 4, 4096, 9, 9))
        self.assertNotEqual(limits.fingerprint(), StatblockLimits().fingerprint())


class SharedFetcherTests(unittest.TestCase):
    def test_success_is_cached_and_failures_cool_down(self):
        clock = Clock()
        shared = SharedFetcher(StatblockLimits(failure_cooldown_seconds=30), clock=clock)
        calls = []
        def ok(deadline):
            calls.append(1)
            return b'data'
        self.assertEqual(shared.fetch('p', 'u', ok, deadline=clock() + 5), b'data')
        self.assertEqual(shared.fetch('p', 'u', ok, deadline=clock() + 5), b'data')
        self.assertEqual(len(calls), 1)
        class Down(Exception):
            code = 'provider_unavailable'
        def fail(deadline):
            raise Down()
        with self.assertRaises(FetchFailure) as caught:
            shared.fetch('p', 'v', fail, deadline=clock() + 5)
        self.assertEqual(caught.exception.code, 'provider_unavailable')
        with self.assertRaises(FetchFailure) as caught:
            shared.fetch('p', 'v', ok, deadline=clock() + 5)
        self.assertEqual((caught.exception.code, caught.exception.retry_at), ('cooldown', clock() + 30))
        clock.value += 31
        self.assertEqual(shared.fetch('p', 'v', ok, deadline=clock() + 5), b'data')
        clock.value += 3600
        shared.fetch('p', 'u', ok, deadline=clock() + 5)
        self.assertEqual(len(calls), 3)  # expired cache entry fetched again

    def test_oversized_responses_fail_and_are_not_cached(self):
        shared = SharedFetcher(StatblockLimits(response_bytes=3))
        with self.assertRaises(FetchFailure) as caught:
            shared.fetch('p', 'u', lambda d: b'four', deadline=time.monotonic() + 5)
        self.assertEqual(caught.exception.code, 'response_bytes_limit')
        self.assertEqual(shared.cache_stats()['entries'], 0)

    def test_cache_is_bounded_by_entries_and_bytes(self):
        shared = SharedFetcher(StatblockLimits(cache_entries=2, cache_bytes=10))
        for key in 'abc':
            shared.fetch('p', key, lambda d: b'1234', deadline=time.monotonic() + 5)
        self.assertEqual(shared.cache_stats(), {'entries': 2, 'bytes': 8})
        shared.fetch('p', 'big', lambda d: b'12345678901', deadline=time.monotonic() + 5)
        self.assertLessEqual(shared.cache_stats()['bytes'], 10)

    def test_identical_requests_are_shared_and_a_leader_deadline_does_not_fail_others(self):
        shared = SharedFetcher(StatblockLimits())
        release, started, calls = threading.Event(), threading.Event(), []
        def slow(deadline):
            calls.append(deadline)
            started.set()
            if len(calls) == 1:
                while time.monotonic() < deadline:
                    time.sleep(0.01)
                raise FetchFailure('deadline')
            release.wait(5)
            return b'shared'
        results = {}
        def leader():
            try:
                shared.fetch('p', 'u', slow, deadline=time.monotonic() + 0.2)
            except FetchFailure as exc:
                results['leader'] = exc.code
        def follower():
            results['follower'] = shared.fetch('p', 'u', slow, deadline=time.monotonic() + 5)
        first = threading.Thread(target=leader); first.start(); started.wait(5)
        second = threading.Thread(target=follower); second.start()
        first.join(5); release.set(); second.join(5)
        self.assertEqual(results, {'leader': 'deadline', 'follower': b'shared'})
        self.assertEqual(len(calls), 2)
        self.assertEqual(shared.fetch('p', 'u', slow, deadline=time.monotonic() + 1), b'shared')
        self.assertEqual(len(calls), 2)

    def test_provider_and_global_concurrency_are_bounded(self):
        shared = SharedFetcher(StatblockLimits(outbound_requests=3, provider_requests=1))
        active, peak, lock = {'p': 0, 'all': 0}, {'p': 0, 'all': 0}, threading.Lock()
        def work(provider):
            def fn(deadline):
                with lock:
                    active[provider] = active.get(provider, 0) + 1; active['all'] += 1
                    peak[provider] = max(peak.get(provider, 0), active[provider]); peak['all'] = max(peak['all'], active['all'])
                time.sleep(0.05)
                with lock:
                    active[provider] -= 1; active['all'] -= 1
                return b'x'
            return fn
        threads = [threading.Thread(target=shared.fetch, args=(provider, f'{provider}{i}', work(provider)),
                                    kwargs={'deadline': time.monotonic() + 5})
                   for i in range(3) for provider in ('p', 'q', 'r', 's')]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(10)
        self.assertEqual(peak['p'], 1)
        self.assertLessEqual(peak['all'], 3)

    def test_waiting_for_capacity_respects_the_deadline(self):
        shared = SharedFetcher(StatblockLimits(outbound_requests=1))
        hold = threading.Event()
        thread = threading.Thread(target=shared.fetch, args=('p', 'a', lambda d: hold.wait(5) and b'x'),
                                  kwargs={'deadline': time.monotonic() + 5})
        thread.start(); time.sleep(0.05)
        with self.assertRaises(FetchFailure) as caught:
            shared.fetch('q', 'b', lambda d: b'y', deadline=time.monotonic() + 0.1)
        self.assertEqual(caught.exception.code, 'deadline')
        hold.set(); thread.join(5)
        # The timed-out request is not cooled down.
        self.assertEqual(shared.fetch('q', 'b', lambda d: b'y', deadline=time.monotonic() + 1), b'y')


class SchedulerTests(unittest.TestCase):
    def test_queue_limit_fairness_and_queued_deadline(self):
        gate, order = threading.Event(), []
        scheduler = JobScheduler(active=1, queued=3)
        def work(name):
            def run(job):
                if name == 'block':
                    gate.wait(5)
                order.append(name)
                return name
            return run
        blocker = scheduler.submit(Job('bulk', work('block'), deadline=time.monotonic() + 5))
        time.sleep(0.05)
        jobs = [scheduler.submit(Job('bulk', work('bulk1'), deadline=time.monotonic() + 5)),
                scheduler.submit(Job('bulk', work('bulk2'), deadline=time.monotonic() + 5)),
                scheduler.submit(Job('single', work('single'), deadline=time.monotonic() + 5))]
        with self.assertRaises(JobCapacity):
            scheduler.submit(Job('other', work('rejected'), deadline=time.monotonic() + 5))
        gate.set()
        for job in [blocker] + jobs:
            self.assertTrue(job.done.wait(5))
        self.assertEqual(order, ['block', 'bulk1', 'single', 'bulk2'])
        self.assertEqual([job.state for job in jobs], ['completed'] * 3)
        expired = scheduler.submit(Job('x', work('late'), deadline=time.monotonic() - 1))
        self.assertTrue(expired.done.wait(5))
        self.assertEqual((expired.state, expired.error[0]), ('failed', 'deadline'))
        self.assertNotIn('late', order)

    def test_cancel_queued_and_running_jobs(self):
        gate = threading.Event()
        scheduler = JobScheduler(active=1, queued=4)
        def running(job):
            while not job.cancelled():
                time.sleep(0.01)
            return 'too late'
        first = scheduler.submit(Job('a', running, deadline=time.monotonic() + 5))
        queued = scheduler.submit(Job('a', lambda job: 'never', deadline=time.monotonic() + 5))
        time.sleep(0.05)
        self.assertTrue(scheduler.cancel(queued))
        self.assertEqual(queued.state, 'cancelled')
        self.assertTrue(scheduler.cancel(first))
        self.assertTrue(first.done.wait(5))
        self.assertEqual((first.state, first.result), ('cancelled', None))
        self.assertEqual(scheduler.counts(), {'running': 0, 'queued': 0})

    def test_on_finish_controls_the_stored_outcome(self):
        seen = []
        def on_finish(job, state, result, error):
            seen.append(state)
            return ('failed', None, ('capacity', 'full', None)) if result == 'reject' else (state, result, error)
        scheduler = JobScheduler(active=1, queued=2, on_finish=on_finish)
        job = scheduler.submit(Job('a', lambda job: 'reject', deadline=time.monotonic() + 5))
        self.assertTrue(job.done.wait(5))
        self.assertEqual((job.state, job.error[0], seen), ('failed', 'capacity', ['completed']))


class SelectionStoreTests(unittest.TestCase):
    def test_references_capacity_dedupe_expiry_and_release(self):
        clock = Clock()
        store = SelectionStore(StatblockLimits(session_selection_references=2, selection_references=3,
                                               prepared_snapshots=2, selection_seconds=600), clock=clock)
        store.reserve('s'); store.reserve('s')
        with self.assertRaises(SelectionError) as caught:
            store.reserve('s')
        self.assertEqual(caught.exception.code, 'session_selection_capacity')
        store.reserve('t')
        with self.assertRaises(SelectionError) as caught:
            store.reserve('u')
        self.assertEqual(caught.exception.code, 'selection_capacity')
        a = store.complete(scope('s', 'm'), 0, prepared('Same'), {})
        b = store.complete(scope('s', 'n'), 0, prepared('Same'), {})
        self.assertEqual(store.counts()['prepared_snapshots'], 1)
        self.assertEqual(store.snapshot(a)['source_label'], 'Same')
        with self.assertRaises(SelectionError):
            store.binding(a.id, 't')
        store.discard(a.id, 's')
        self.assertEqual(store.counts()['prepared_snapshots'], 1)
        clock.value += 601
        with self.assertRaises(SelectionError) as caught:
            store.binding(b.id, 's')
        self.assertEqual(caught.exception.code, 'selection_expired')
        self.assertEqual(store.counts()['prepared_snapshots'], 0)

    def test_prepared_capacity_rejects_without_evicting_and_releases_the_reservation(self):
        store = SelectionStore(StatblockLimits(prepared_snapshots=1))
        store.reserve('s'); store.complete(scope('s'), 0, prepared('One'), {})
        store.reserve('t')
        with self.assertRaises(SelectionError) as caught:
            store.complete(scope('t'), 0, prepared('Two'), {})
        self.assertEqual(caught.exception.code, 'prepared_capacity')
        self.assertEqual(store.counts()['bindings'], 1)
        self.assertEqual(store.counts()['reserved'], 0)

    def test_outcomes_share_the_global_budget_and_keep_the_selection_expiry(self):
        clock = Clock()
        store = SelectionStore(StatblockLimits(selection_references=2, selection_seconds=100), clock=clock)
        store.reserve('s'); binding = store.complete(scope(), 0, prepared('One'), {})
        clock.value += 40
        store.reserve_outcome('s', 'op', [binding.id])
        store.finish_apply('s', 'op', 'digest', [binding.id], {'ok': True})
        self.assertEqual(store.outcome('s', 'op').result, {'ok': True})
        self.assertEqual(store.counts()['bindings'], 0)
        store.reserve('s')
        with self.assertRaises(SelectionError):
            store.reserve('s')
        clock.value += 61
        self.assertIsNone(store.outcome('s', 'op'))

    def test_candidates_are_session_bound_and_revoked_with_the_session(self):
        store = SelectionStore(StatblockLimits())
        ident = store.add_candidate(scope(), 'Open5e', {'key': 'goblin'}, {'label': 'Goblin'})
        self.assertEqual(store.candidate(ident, 's').identity, {'key': 'goblin'})
        with self.assertRaises(SelectionError):
            store.candidate(ident, 'other')
        store.reserve('s'); store.complete(scope(), 0, prepared('x'), {})
        store.revoke_session('s')
        self.assertEqual(store.counts()['candidates'], 0)
        self.assertEqual(store.counts()['bindings'], 0)


if __name__ == '__main__':
    unittest.main()
