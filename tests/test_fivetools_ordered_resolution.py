"""Native ordered graph/compiler/executor checks; isolated worker is 04c.2c."""
import json
import unittest
from python.scrying_glass_fivetools_resolution import Identity, Limits, DatasetLoader, Resolver, ResolutionError, COPY_ENTRY_PROPS
from python.scrying_glass_fivetools_ordered_resolution import OrderedResolver
from python.scrying_glass_fivetools_modifications import ENTRY_PROPS

def mod(mode, **values):
    return dict(mode=mode, **values)

class OrderedGraphTests(unittest.TestCase):
    def setUp(self):
        self.a, self.b, self.c = [Identity('root', 'monster', 'MM', n) for n in 'ABC']
        self.t = Identity('root', 'monsterTemplate', 'MM', 'T')
    def make(self, ops=None, *, base=None, template=None, repeats=1, **limits):
        def row(i, **values):
            return dict(name=i.name, source=i.source, **values)
        meta = dict(name='B', source='MM', _mod=ops or {})
        if template is not None:
            meta['_templates'] = [dict(name='T', source='MM')]*repeats
        rows = {self.a: row(self.a, _copy=meta), self.b: row(self.b, label='base', trait=['base'])}
        if base is not None:
            rows[self.b] = row(self.b, _copy=dict(name='C', source='MM', _mod=base))
            rows[self.c] = row(self.c, label='root', trait=['root'])
        if template is not None:
            rows[self.t] = row(self.t, apply={'_mod': template})
        loader = DatasetLoader('root', [(i, json.dumps(r).encode()) for i, r in rows.items()])
        return OrderedResolver(loader, limits=Limits(**limits), clock=lambda: 0)
    def get(self, r, identity=None, **values):
        return r.resolve(identity or self.a, deadline=10, **values)
    def error(self, code, r):
        with self.assertRaises(ResolutionError) as caught:
            self.get(r)
        d = caught.exception.diagnostic
        self.assertEqual(d.code, code); self.assertEqual(d.selected, self.a)
        return d
    def test_legacy_entry_is_unchanged(self):
        r = self.make(); legacy = Resolver(r.loader, clock=lambda: 0)
        self.assertEqual(self.get(r), self.get(legacy))
        r = self.make({'trait': 'remove'})
        self.assertNotIn('trait', self.get(r).record())
        self.error('modification_execution_pending_04c', Resolver(r.loader, clock=lambda: 0))
    def test_six_modes_and_exact_instruction_budget(self):
        ops = {'label': [mod('appendStr', str='!'), mod('prefixSuffixStringProp', prefix='[', suffix=']')], 'trait': ['remove', mod('appendArr', items=['end']), mod('prependArr', items=['start'])], '_': mod('setProp', prop='extra.value', value=3)}
        result = self.get(self.make(ops, modification_operations=6)); out = result.record()
        self.assertEqual((out['label'], out['trait'], out['extra']), ('[base!]', ['start', 'end'], {'value': 3}))
        self.assertEqual(result.modification_operations, 6); self.assertNotIn('_copy', out); self.assertTrue(out['_isCopy'])
    def test_recursive_base_modifications_precede_selected(self):
        r = self.make({'trait': mod('appendArr', items=['selected'])}, base={'trait': mod('appendArr', items=['base'])})
        result = self.get(r)
        self.assertEqual(result.record()['trait'], ['root', 'base', 'selected'])
        self.assertEqual((result.inheritance_depth, result.modification_operations), (2, 2))
        self.assertEqual([p.identity for p in result.provenance], [self.a, self.b, self.c])
    def test_repeated_template_groups_merge_before_tail(self):
        r = self.make({'_': mod('setProp', prop='label', value='tail'), 'trait': mod('appendArr', items=['selected'])}, template={'label': mod('appendStr', str='template'), 'trait': mod('appendArr', items=['template'])}, repeats=2, modification_operations=6)
        result = self.get(r)
        self.assertEqual(result.record()['label'], 'tail')
        self.assertEqual(result.record()['trait'], ['base', 'selected', 'template', 'template'])
        self.assertEqual(result.modification_operations, 6)
        self.assertEqual(sum(p.role == 'template' for p in result.provenance), 2)
    def test_cached_work_is_not_double_charged_or_free(self):
        ops, base = {'trait': mod('appendArr', items=['s'])}, {'trait': mod('appendArr', items=['b'])}
        r = self.make(ops, base=base, modification_operations=2); self.get(r, self.b)
        first = self.get(r); self.assertEqual(self.get(r), first); self.assertEqual(first.modification_operations, 2)
        tight = self.make(ops, base=base, modification_operations=1); self.get(tight, self.b)
        self.error('modification_operations_limit', tight); self.assertNotIn(self.a, tight._cache)
    def test_template_error_has_origin_and_merged_index(self):
        r = self.make({'trait': mod('appendArr', items=['s'])}, template={'trait': mod('appendArr')})
        d = self.error('malformed_modification_payload', r)
        self.assertEqual((d.chain, d.property, d.operation_index, d.mode), ((self.a, self.t), 'trait', 1, 'appendArr'))
        self.assertEqual(d.source_path, '$/apply/_mod/trait'); self.assertFalse(r._cache)
    def test_base_unsupported_mode_preserves_active_chain(self):
        d = self.error('modification_execution_pending_04c', self.make(base={'trait': mod('removeArr', names=['x'])}))
        self.assertEqual((d.chain, d.mode), ((self.a, self.b), 'removeArr'))
    def test_dynamic_and_wildcard_contract(self):
        self.assertEqual(ENTRY_PROPS, COPY_ENTRY_PROPS)
        r = self.make({'_': mod('setProp', prop='extra', value='<$name$>')})
        self.error('dynamic_substitution_pending_04d', r); self.assertFalse(r._cache)
        result = self.get(self.make({'*': 'remove'}, modification_operations=1))
        self.assertNotIn('trait', result.record()); self.assertEqual(result.modification_operations, 1)
    def test_cached_result_base_and_cancellation_isolation(self):
        r = self.make({'trait': mod('appendArr', items=[{'name': 'new'}])})
        self.get(r).record()['trait'].append('mutated')
        self.assertEqual(self.get(r).record()['trait'], ['base', {'name': 'new'}])
        self.assertEqual(self.get(r, self.b).record()['trait'], ['base'])
        with self.assertRaises(ResolutionError) as caught:
            self.get(r, cancelled=lambda: True)
        self.assertEqual(caught.exception.diagnostic.code, 'cancelled')
    def test_growth_failure_never_publishes(self):
        r = self.make({'trait': mod('appendArr', items=['x'*400])}, base={'trait': mod('appendArr', items=['b'*300])}, intermediate_creature_bytes=1000)
        self.error('intermediate_creature_bytes_limit', r); self.assertFalse(r._cache)

if __name__ == '__main__':
    unittest.main()
