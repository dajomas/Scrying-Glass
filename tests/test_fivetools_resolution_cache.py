"""04b.1 logical cache-content accounting; real resolver, synthetic datasets."""
import json
import unittest
from dataclasses import replace
from python.scrying_glass_fivetools_resolution import (
    Identity, Limits, Provenance, Result, Resolver, ResolutionError,
    _cache_entry_bytes,
)

def wire(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()

class Loader:
    def __init__(self, rows):
        self.rows = {k: (wire(v),) for k, v in rows.items()}
        self.calls = []
    def load(self, identity):
        self.calls.append(identity)
        return self.rows.get(identity, ())

class CacheAccountingTests(unittest.TestCase):
    def setUp(self):
        self.a = Identity('root', 'monster', 'MM', 'A')
        self.b = replace(self.a, name='B')
        self.c = replace(self.a, name='C')
        self.rows = {i: {'name': i.name, 'source': i.source} for i in (self.a, self.b, self.c)}
    def resolver(self, rows=None, **limits):
        return Resolver(Loader(self.rows if rows is None else rows), limits=Limits(**limits), clock=lambda: 0)
    def get(self, resolver, identity=None, **kwargs):
        return resolver.resolve(identity or self.a, deadline=10, **kwargs)
    def ledger(self, resolver):
        self.assertEqual(resolver._cache_bytes, sum(_cache_entry_bytes(k, v) for k, v in resolver._cache.items()))
        self.assertLessEqual(resolver._cache_bytes, resolver.limits.cache_bytes)
        self.assertLessEqual(len(resolver._cache), resolver.limits.cache_entries)
        self.assertEqual(set(resolver._cache), set(resolver._cache_times))
    def size(self, identity):
        resolver = self.resolver(); self.get(resolver, identity)
        return _cache_entry_bytes(identity, resolver._cache[identity])
    def test_exact_metadata_wire_definition(self):
        selected = replace(self.a, name='é', discriminator='v', edition='2024')
        result = Result(b'{}', (Provenance(self.b, 'base', (selected, self.b)),), 2, 3)
        key = ['root', 'monster', 'MM', 'é', 'v', '2024']
        base = ['root', 'monster', 'MM', 'B', None, None]
        expected = wire({'key': key, 'provenance': [[base, 'base', [key, base]]], 'depth': 2, 'operations': 3})
        self.assertEqual(_cache_entry_bytes(selected, result), 2 + len(expected))
        self.assertGreater(len(expected), len(expected.decode()))
    def test_every_identity_component_and_work_are_charged(self):
        result = Result(b'{}', (), 1, 1)
        initial = _cache_entry_bytes(self.a, result)
        for field in ('dataset', 'kind', 'source', 'name'):
            self.assertEqual(_cache_entry_bytes(replace(self.a, **{field: getattr(self.a, field)+'é'}), result), initial+2)
        self.assertGreater(_cache_entry_bytes(replace(self.a, discriminator='variant', edition='2024'), result), initial)
        self.assertEqual(_cache_entry_bytes(self.a, replace(result, inheritance_depth=10, modification_operations=10)), initial+2)
    def test_repeated_provenance_occurrences_are_not_free(self):
        p = Provenance(self.b, 'base', (self.a, self.b))
        empty = Result(b'{}', (), 0, 0)
        once = replace(empty, provenance=(p,)); twice = replace(empty, provenance=(p, p))
        self.assertGreater(_cache_entry_bytes(self.a, twice), _cache_entry_bytes(self.a, once))
        self.assertGreater(_cache_entry_bytes(self.a, once), _cache_entry_bytes(self.a, empty))
    def test_cache_byte_equality_and_one_beyond(self):
        size = self.size(self.a)
        for cap, retained in ((size-1, False), (size, True), (size+1, True)):
            with self.subTest(cap=cap):
                resolver = self.resolver(cache_bytes=cap)
                first = self.get(resolver); second = self.get(resolver)
                self.assertEqual(first.record_json, second.record_json)
                self.assertEqual(self.a in resolver._cache, retained)
                self.assertEqual(len(resolver.loader.calls), 1 if retained else 2)
                self.ledger(resolver)
    def test_record_only_fit_does_not_admit_metadata(self):
        resolver = self.resolver(cache_bytes=len(wire(self.rows[self.a])))
        self.assertEqual(self.get(resolver).record(), self.rows[self.a])
        self.assertEqual(resolver._cache_bytes, 0); self.assertFalse(resolver._cache)
    def test_long_dataset_key_is_bounded_even_for_small_records(self):
        identity = replace(self.a, dataset='é'*1000)
        resolver = self.resolver({identity: self.rows[self.a]}, cache_bytes=1024)
        self.get(resolver, identity); self.get(resolver, identity)
        self.assertFalse(resolver._cache); self.assertEqual(len(resolver.loader.calls), 2)
        self.ledger(resolver)
    def test_base_and_repeated_template_paths_are_counted(self):
        template = Identity('root', 'monsterTemplate', 'MM', 'T')
        rows = {self.a: dict(self.rows[self.a], _copy={'name': 'B', 'source': 'MM', '_templates': [{'name': 'T', 'source': 'MM'}]*2}), self.b: self.rows[self.b], template: {'name': 'T', 'source': 'MM', 'apply': {}}}
        resolver = self.resolver(rows); result = self.get(resolver)
        cached = resolver._cache[self.a]
        self.assertEqual([p.role for p in cached.provenance], ['base', 'template', 'template'])
        self.assertGreater(_cache_entry_bytes(self.a, cached), _cache_entry_bytes(self.a, replace(cached, provenance=())))
        self.assertEqual(result.provenance[0].role, 'selected')
        self.assertNotEqual(result.provenance, cached.provenance)
        self.ledger(resolver)
        cap = _cache_entry_bytes(self.a, cached)
        tight = self.resolver(rows, cache_bytes=cap)
        self.assertEqual(self.get(tight).record_json, result.record_json)
        self.assertEqual(list(tight._cache), [self.a]); self.ledger(tight)
    def test_byte_eviction_respects_lru_hits(self):
        cap = self.size(self.a)+self.size(self.b)
        resolver = self.resolver(cache_bytes=cap)
        for identity in (self.a, self.b, self.a, self.c):
            self.get(resolver, identity); self.ledger(resolver)
        self.assertEqual(list(resolver._cache), [self.a, self.c])
        self.assertEqual(resolver.loader.calls, [self.a, self.b, self.c])
    def test_entry_eviction_uses_same_ledger(self):
        resolver = self.resolver(cache_entries=1)
        for identity in (self.a, self.b, self.a):
            self.get(resolver, identity); self.ledger(resolver)
            self.assertEqual(list(resolver._cache), [identity])
    def test_ttl_equality_releases_full_charge(self):
        now = [0]; resolver = self.resolver(cache_seconds=1)
        resolver.clock = lambda: now[0]
        self.get(resolver); before = resolver._cache_bytes
        now[0] = 1; self.get(resolver)
        self.assertEqual(len(resolver.loader.calls), 2)
        self.assertEqual(resolver._cache_bytes, before); self.ledger(resolver)
    def test_failure_and_cancellation_do_not_publish_pending_content(self):
        rows = dict(self.rows); rows[self.a] = dict(self.rows[self.a], _copy={'name': 'B', 'source': 'MM', '_mod': {'trait': 'remove'}})
        resolver = self.resolver(rows); self.get(resolver, self.c)
        before = resolver._cache_bytes
        with self.assertRaises(ResolutionError) as raised:
            self.get(resolver)
        self.assertEqual(raised.exception.diagnostic.code, 'modification_execution_pending_04c')
        with self.assertRaises(ResolutionError) as raised:
            self.get(resolver, cancelled=lambda: True)
        self.assertEqual(raised.exception.diagnostic.code, 'cancelled')
        self.assertEqual(list(resolver._cache), [self.c]); self.assertEqual(resolver._cache_bytes, before)
        self.ledger(resolver)
    def test_returned_mutation_does_not_change_cached_bytes(self):
        resolver = self.resolver({self.a: dict(self.rows[self.a], trait=['original'])})
        first = self.get(resolver); before = resolver._cache_bytes
        first.record()['trait'].append('changed')
        second = self.get(resolver)
        self.assertEqual(second.record()['trait'], ['original'])
        self.assertEqual(second.provenance, first.provenance)
        self.assertEqual(resolver._cache_bytes, before); self.ledger(resolver)

if __name__ == '__main__':
    unittest.main()
