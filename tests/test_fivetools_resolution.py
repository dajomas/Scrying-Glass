"""Native graph tests using synthetic exact-source datasets, not live providers."""
import json
import time
import unittest
from dataclasses import replace
from python.scrying_glass_fivetools_resolution import Identity, Limits, Resolver, ResolutionError, DatasetLoader, MODES, compile_modifications

def wire(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode()

class Loader:
    def __init__(self, rows):
        self.rows = {k: tuple(wire(v) for v in values) for k, values in rows.items()}
        self.calls = []
    def load(self, identity):
        self.calls.append(identity)
        return self.rows.get(identity, ())

class ResolutionTests(unittest.TestCase):
    def setUp(self):
        self.a = Identity('root', 'monster', 'XMM', 'A')
        self.b = Identity('root', 'monster', 'MM', 'B')
        self.c = Identity('root', 'monster', 'MM', 'C')
        self.t = Identity('root', 'monsterTemplate', 'PHB', 'T')
    def rows(self, meta=None, **overrides):
        a = {'name': 'A', 'source': 'XMM', '_copy': dict(name='B', source='MM', **(meta or {}))}
        a.update(overrides)
        return {self.a: [a], self.b: [{'name': 'B', 'source': 'MM', 'str': 8, 'dex': 9, 'trait': ['base'], 'page': 3, 'environment': ['forest']}], self.t: [{'name': 'T', 'source': 'PHB', 'apply': {'_root': {'str': 18, 'trait': ['template'], 'dex': 14}}}]}
    def resolve(self, rows, limits=None, selected=None):
        return Resolver(Loader(rows), limits=limits).resolve(selected or self.a, deadline=time.monotonic()+10)
    def code(self, expected, fn):
        with self.assertRaises(ResolutionError) as raised:
            fn()
        self.assertEqual(raised.exception.diagnostic.code, expected)
        return raised.exception.diagnostic
    def test_plain_and_independent_snapshots(self):
        row = {'name': 'A', 'source': 'XMM', 'trait': ['original']}
        loader = Loader({self.a: [row]}); resolver = Resolver(loader)
        first = resolver.resolve(self.a, deadline=time.monotonic()+10)
        first.record()['trait'].append('changed'); row['trait'].append('input changed')
        second = resolver.resolve(self.a, deadline=time.monotonic()+10)
        self.assertEqual(second.record()['trait'], ['original'])
        self.assertEqual(first.record_json, second.record_json)
        self.assertEqual(len(loader.calls), 1)
        self.assertEqual(second.provenance[0].role, 'selected')
    def test_multilevel_cross_bestiary_and_provenance(self):
        rows = self.rows(); rows[self.b][0]['_copy'] = {'name': 'C', 'source': 'MM'}
        rows[self.c] = [{'name': 'C', 'source': 'MM', 'str': 18, 'wis': 10}]
        out = self.resolve(rows)
        self.assertEqual(out.inheritance_depth, 2)
        self.assertEqual((out.record()['name'], out.record()['str'], out.record()['wis']), ('A', 8, 10))
        self.assertEqual([p.identity for p in out.provenance], [self.a, self.b, self.c])
        self.assertEqual(out.provenance[-1].chain, (self.a, self.b, self.c))
    def test_null_override_preserve_and_unchanged_input(self):
        rows = self.rows({'_preserve': {'page': True}}, trait=None, absent=None)
        out = self.resolve(rows)
        self.assertNotIn('trait', out.record()); self.assertIsNone(out.record()['absent'])
        self.assertEqual(out.record()['page'], 3); self.assertNotIn('environment', out.record())
        self.assertIn('_copy', rows[self.a][0]); self.assertEqual(out.modification_operations, 1)
    def test_wildcard_preservation(self):
        self.assertEqual(self.resolve(self.rows({'_preserve': {'*': True}})).record()['environment'], ['forest'])
    def test_template_roots_and_selected_null_priority(self):
        out = self.resolve(self.rows({'_templates': [{'name': 'T', 'source': 'PHB'}]}, str=15, trait=None))
        self.assertEqual((out.record()['str'], out.record()['dex']), (15, 14))
        self.assertNotIn('trait', out.record()); self.assertEqual(out.provenance[-1].role, 'template')
    def test_recursive_template_copy(self):
        rows = self.rows({'_templates': [{'name': 'T', 'source': 'PHB'}]})
        t2 = replace(self.t, name='T2')
        rows[self.t] = [{'name': 'T', 'source': 'PHB', '_copy': {'name': 'T2', 'source': 'PHB'}}]
        rows[t2] = [{'name': 'T2', 'source': 'PHB', 'apply': {'_root': {'dex': 14}}}]
        out = self.resolve(rows)
        self.assertEqual(out.record()['dex'], 14); self.assertIn(t2, [p.identity for p in out.provenance])
    def test_repeated_template_is_not_cycle(self):
        out = self.resolve(self.rows({'_templates': [{'name': 'T', 'source': 'PHB'}]*2}))
        self.assertEqual(out.record()['dex'], 14)
        self.assertEqual(sum(p.role == 'template' for p in out.provenance), 2)
    def test_cycle_reports_full_active_path(self):
        rows = self.rows(); rows[self.b][0]['_copy'] = {'name': 'A', 'source': 'XMM'}
        self.assertEqual(self.code('inheritance_cycle', lambda: self.resolve(rows)).chain, (self.a, self.b, self.a))
    def test_missing_duplicate_and_wrong_edition(self):
        self.code('missing_dependency', lambda: self.resolve({}))
        self.code('ambiguous_dependency', lambda: self.resolve({self.a: [{'name': 'A', 'source': 'XMM'}]*2}))
        wrong = replace(self.a, source='MM')
        self.code('missing_dependency', lambda: self.resolve({wrong: [{'name': 'A', 'source': 'MM'}]}))
        self.code('identity_mismatch', lambda: self.resolve({self.a: [{'name': 'A', 'source': 'MM'}]}))
    def test_discriminator_dataset_and_edition_are_exact(self):
        exact = replace(self.a, discriminator='one', edition='2024')
        rows = {exact: [{'name': 'A', 'source': 'XMM', 'discriminator': 'one', 'edition': '2024'}]}
        self.assertEqual(self.resolve(rows, selected=exact).record()['discriminator'], 'one')
        self.code('missing_dependency', lambda: self.resolve(rows, selected=replace(exact, dataset='other')))
    def test_malformed_identity_and_duplicate_json(self):
        rows = self.rows(); rows[self.a][0]['_copy'] = {'name': 'B'}
        self.code('malformed_identity', lambda: self.resolve(rows))
        loader = Loader({}); loader.rows[self.a] = (b'{"name":"A","name":"A","source":"XMM"}',)
        self.code('malformed_record', lambda: Resolver(loader).resolve(self.a, deadline=time.monotonic()+10))
    def test_depth_equality_and_beyond_even_cached(self):
        rows = self.rows(); rows[self.b][0]['_copy'] = {'name': 'C', 'source': 'MM'}
        rows[self.c] = [{'name': 'C', 'source': 'MM'}]
        resolver = Resolver(Loader(rows), limits=Limits(inheritance_steps=1))
        resolver.resolve(self.b, deadline=time.monotonic()+10)
        self.code('inheritance_steps_limit', lambda: resolver.resolve(self.a, deadline=time.monotonic()+10))
        self.assertEqual(self.resolve(rows, Limits(inheritance_steps=2)).inheritance_depth, 2)
    def test_cached_operations_are_charged(self):
        rows = self.rows(dex=None); rows[self.b][0].update(str=None, _copy={'name': 'C', 'source': 'MM'})
        rows[self.c] = [{'name': 'C', 'source': 'MM', 'str': 8, 'dex': 9}]
        resolver = Resolver(Loader(rows), limits=Limits(modification_operations=1))
        self.assertEqual(resolver.resolve(self.b, deadline=time.monotonic()+10).modification_operations, 1)
        self.code('modification_operations_limit', lambda: resolver.resolve(self.a, deadline=time.monotonic()+10))
    def test_compact_unicode_bytes_boundary_and_whitespace(self):
        obj = {'name': 'A', 'source': 'XMM', 'trait': ['é']}; size = len(wire(obj))
        loader = Loader({self.a: [obj]}); loader.rows[self.a] = (b'  '+wire(obj)+b'  ',)
        self.assertEqual(Resolver(loader, limits=Limits(intermediate_creature_bytes=size)).resolve(self.a, deadline=time.monotonic()+10).record(), obj)
        self.code('intermediate_creature_bytes_limit', lambda: self.resolve({self.a: [obj]}, Limits(intermediate_creature_bytes=size-1)))
    def test_failed_and_cancelled_work_is_not_cached(self):
        resolver = Resolver(Loader(self.rows())); count = [0]
        def cancelled():
            count[0] += 1
            return count[0] > 20
        self.code('cancelled', lambda: resolver.resolve(self.a, deadline=time.monotonic()+10, cancelled=cancelled))
        self.assertEqual(len(resolver._cache), 0)
        self.code('deadline', lambda: resolver.resolve(self.a, deadline=0))
        self.assertEqual(len(resolver._cache), 0)
    def test_sibling_cache_isolation_and_cache_eviction(self):
        rows = self.rows(); rows[self.c] = [{'name': 'C', 'source': 'MM', 'trait': ['base']}]
        rows[self.a][0]['_copy'] = rows[self.b][0]['_copy'] = {'name': 'C', 'source': 'MM'}
        resolver = Resolver(Loader(rows), limits=Limits(cache_entries=1))
        a = resolver.resolve(self.a, deadline=time.monotonic()+10); a.record()['trait'].append('mutated')
        self.assertEqual(resolver.resolve(self.b, deadline=time.monotonic()+10).record()['trait'], ['base'])
        self.assertLessEqual(len(resolver._cache), 1); self.assertLessEqual(resolver._cache_bytes, resolver.limits.cache_bytes)
    def test_instruction_order_modes_and_fail_closed(self):
        self.assertEqual(len(MODES), 28)
        items = compile_modifications({'*': {'mode': 'scalarAddHit', 'scalar': 1}, 'trait': ['remove', {'mode': 'appendArr', 'items': []}], '_': {'mode': 'addAllSaves', 'saves': 1}, 'action': 'remove'})
        self.assertEqual([i.property for i in items], ['trait', 'trait', 'action', '_', '*'])
        for mode, code in [('appendArr', 'modification_execution_pending_04c'), ('unknown', 'unknown_modification_mode')]:
            d = self.code(code, lambda: self.resolve(self.rows({'_mod': {'trait': {'mode': mode, 'items': []}}})))
            self.assertEqual((d.selected, d.property, d.operation_index, d.mode), (self.a, 'trait', 0, mode))
    def test_limit_and_identity_validation(self):
        for value in [True, 0, -1, 1.5]:
            with self.assertRaises(ValueError):
                Limits(inheritance_steps=value)
        with self.assertRaises(ValueError):
            Identity('root', 'monster', '', 'A')
    def test_dataset_loader_immutable_exact_duplicates(self):
        payload = wire({'name': 'A', 'source': 'XMM'}); records = [(self.a, payload)]*2
        loader = DatasetLoader('root', records); records.clear()
        self.assertEqual(loader.load(self.a), (payload, payload))
        self.assertEqual(loader.load(replace(self.a, dataset='other')), ())
        with self.assertRaises(ValueError):
            DatasetLoader('other', [(self.a, payload)])
    def test_cache_expiry_and_response_byte_boundary(self):
        obj = {'name': 'A', 'source': 'XMM'}; loader = Loader({self.a: [obj]}); clock = [0]
        resolver = Resolver(loader, clock=lambda: clock[0], limits=Limits(cache_seconds=1, response_bytes=len(wire(obj))))
        resolver.resolve(self.a, deadline=10); resolver.resolve(self.a, deadline=10)
        self.assertEqual(len(loader.calls), 1); clock[0] = 1; resolver.resolve(self.a, deadline=10)
        self.assertEqual(len(loader.calls), 2)
        self.code('response_bytes_limit', lambda: self.resolve({self.a: [obj]}, Limits(response_bytes=len(wire(obj))-1)))
    def test_template_cycle_and_malformed_preserve(self):
        rows = self.rows({'_templates': [{'name': 'T', 'source': 'PHB'}]})
        rows[self.t] = [{'name': 'T', 'source': 'PHB', '_copy': {'name': 'T', 'source': 'PHB'}}]
        self.code('inheritance_cycle', lambda: self.resolve(rows))
        self.code('malformed_copy_metadata', lambda: self.resolve(self.rows({'_preserve': {'page': False}})))
    def test_template_output_property_order_matches_runtime(self):
        out = self.resolve(self.rows({'_templates': [{'name': 'T', 'source': 'PHB'}]}))
        self.assertEqual(list(out.record()), ['name', 'source', '_copy_templates', 'str', 'dex', 'trait', '_isCopy'])

if __name__ == '__main__':
    unittest.main()
