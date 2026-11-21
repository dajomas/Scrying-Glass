"""04b.2 resource boundaries on the actual interpreter; no live providers."""
import json
import math
import unittest
from dataclasses import fields, replace
from unittest.mock import patch
from python import scrying_glass_fivetools_resolution as core
from python.scrying_glass_fivetools_resolution_bounds import measure_json

def wire(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode()

class Loader:
    def __init__(self, rows):
        self.rows = {k: (wire(v),) for k, v in rows.items()}
        self.calls = []
    def load(self, identity):
        self.calls.append(identity)
        return self.rows.get(identity, ())

class ResourceTests(unittest.TestCase):
    def setUp(self):
        self.a = core.Identity('root', 'monster', 'MM', 'A')
        self.b = replace(self.a, name='B'); self.c = replace(self.a, name='C')
    def row(self, identity, **values):
        return dict(name=identity.name, source=identity.source, **values)
    def resolver(self, rows, **limits):
        return core.Resolver(Loader(rows), limits=core.Limits(**limits), clock=lambda: 0)
    def get(self, resolver, selected=None, **kwargs):
        return resolver.resolve(selected or self.a, deadline=10, **kwargs)
    def error(self, code, fn):
        with self.assertRaises(core.ResolutionError) as caught:
            fn()
        self.assertEqual(caught.exception.diagnostic.code, code)
        self.assertEqual(caught.exception.diagnostic.selected, self.a)
    def measure(self, value, cap):
        def fail(code):
            raise ValueError(code)
        return measure_json(value, cap, lambda: None, fail)
    def test_exact_preflight_unicode_escaping_numbers_and_nesting(self):
        values = [None, True, False, 0, -123, 1.2e30, -0.0, [], {}, {'é': ['\x00\b\f\n\r\t"\\😀', {'x': 1}]}]
        values += [chr(i) for i in range(128)]
        for value in values:
            size = len(wire(value))
            with self.subTest(value=value):
                self.assertEqual(self.measure(value, size), size)
                with self.assertRaisesRegex(ValueError, 'intermediate_creature_bytes_limit'):
                    self.measure(value, size-1)
    def test_invalid_json_values_fail_safely(self):
        for value in (float('nan'), float('inf'), '\ud800', {1: 'x'}, set()):
            with self.subTest(value=repr(value)), self.assertRaisesRegex(ValueError, 'malformed_record'):
                self.measure(value, 1000)
    def test_every_limit_rejects_boolean_zero_negative_fraction_and_overflow(self):
        for field in fields(core.Limits):
            for bad in (True, False, 0, -1, 0.5, None, 2**63):
                with self.subTest(field=field.name, bad=bad), self.assertRaises(ValueError):
                    core.Limits(**{field.name: bad})
        for bad in (False, 0, {}, [], 'x'):
            with self.assertRaisesRegex(ValueError, 'invalid_limits'):
                core.Resolver(Loader({}), limits=bad)
    def test_deadline_and_callback_validation(self):
        resolver = self.resolver({self.a: self.row(self.a)})
        for deadline in (True, None, math.nan, math.inf):
            with self.assertRaisesRegex(ValueError, 'invalid_deadline'):
                resolver.resolve(self.a, deadline=deadline)
        for clock in (lambda: math.nan, lambda: True, lambda: 'bad'):
            resolver.clock = clock
            self.error('invalid_clock', lambda: self.get(resolver))
        resolver.clock = lambda: 0
        with self.assertRaisesRegex(ValueError, 'invalid_callback'):
            self.get(resolver, cancelled=False)
        resolver.clock = lambda: 10
        self.error('deadline', lambda: self.get(resolver))
        self.assertFalse(resolver._cache)
    def test_input_overflow_is_rejected_before_json_output_allocation(self):
        resolver = self.resolver({self.a: self.row(self.a, text='x'*1000)}, intermediate_creature_bytes=100)
        with patch.object(core.json.JSONEncoder, 'iterencode', side_effect=AssertionError('serialized before preflight')):
            self.error('intermediate_creature_bytes_limit', lambda: self.get(resolver))
        self.assertFalse(resolver._cache)
    def test_root_union_growth_rejected_without_mutating_inputs(self):
        a = self.row(self.a, own='a'*100, _copy={'name': 'B', 'source': 'MM'})
        b = self.row(self.b, inherited='b'*200)
        resolver = self.resolver({self.a: a, self.b: b}, intermediate_creature_bytes=max(len(wire(a)), len(wire(b))))
        self.error('intermediate_creature_bytes_limit', lambda: self.get(resolver))
        self.assertNotIn('inherited', a); self.assertFalse(resolver._cache)
    def test_template_metadata_and_root_expansion_are_bounded(self):
        t = core.Identity('root', 'monsterTemplate', 'MM', 'T')
        a = self.row(self.a, _copy={'name': 'B', 'source': 'MM', '_templates': [{'name': 'T', 'source': 'MM'}]})
        rows = {self.a: a, self.b: self.row(self.b, inherited='b'*200), t: self.row(t, apply={'_root': {'extra': 't'*400}})}
        cap = max(len(wire(row)) for row in rows.values())
        resolver = self.resolver(rows, intermediate_creature_bytes=cap)
        self.error('intermediate_creature_bytes_limit', lambda: self.get(resolver))
        self.assertFalse(resolver._cache)
        resolver = self.resolver({self.a: a, self.b: self.row(self.b)}, intermediate_creature_bytes=len(wire(a)))
        self.error('intermediate_creature_bytes_limit', lambda: self.get(resolver))
    def test_instruction_limit_precedes_compilation_and_counts_lists(self):
        for count, expected in ((2, 'modification_execution_pending_04c'), (3, 'modification_operations_limit')):
            rows = {self.a: self.row(self.a, _copy={'name': 'B', 'source': 'MM', '_mod': {'trait': ['remove']*count}}), self.b: self.row(self.b)}
            resolver = self.resolver(rows, modification_operations=2)
            if count == 3:
                with patch.object(core, 'compile_modifications', side_effect=AssertionError('compiled over budget')):
                    self.error(expected, lambda: self.get(resolver))
            else:
                self.error(expected, lambda: self.get(resolver))
            self.assertFalse(resolver._cache)
    def test_changed_limits_invalidate_cached_raw_input_and_capacity(self):
        row = self.row(self.a); resolver = self.resolver({self.a: row})
        resolver.loader.rows[self.a] = (b' '*100 + wire(row),)
        self.get(resolver)
        resolver.limits = replace(resolver.limits, response_bytes=len(wire(row)))
        self.error('response_bytes_limit', lambda: self.get(resolver))
        self.assertFalse(resolver._cache); self.assertEqual(resolver._cache_bytes, 0)
        self.assertEqual(len(resolver.loader.calls), 2)
        resolver = self.resolver({self.a: row}); self.get(resolver)
        resolver.limits = replace(resolver.limits, cache_bytes=1)
        self.assertEqual(self.get(resolver).record(), row); self.assertFalse(resolver._cache)
    def test_cancel_during_cache_publication_is_atomic(self):
        resolver = self.resolver({self.a: self.row(self.a)})
        original = core._cache_entry_bytes; calls = [0]
        def charge(*args):
            calls[0] += 1
            return original(*args)
        with patch.object(core, '_cache_entry_bytes', side_effect=charge):
            self.error('cancelled', lambda: self.get(resolver, cancelled=lambda: calls[0] >= 2))
        self.assertEqual(calls[0], 2); self.assertFalse(resolver._cache)
        self.assertEqual(resolver._cache_bytes, 0); self.assertFalse(resolver._cache_times)
    def test_compilation_checks_cancellation_between_instructions(self):
        probes = [0]
        def check():
            probes[0] += 1
            if probes[0] == 3:
                raise RuntimeError('cancel')
        with self.assertRaisesRegex(RuntimeError, 'cancel'):
            core.compile_modifications({'trait': ['remove']*10}, check=check)
        self.assertEqual(probes[0], 3)

if __name__ == '__main__':
    unittest.main()
