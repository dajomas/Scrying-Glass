"""04c.3a component semantics and checked JSON equality; no provider fixtures."""
import json
import unittest
from types import SimpleNamespace
from python.scrying_glass_fivetools_modifications import apply_modifications, ModificationError
from python.scrying_glass_fivetools_resolution_bounds import json_equal

def op(items, prop='a'):
    return SimpleNamespace(property=prop, mode='appendIfNotExistsArr',
        payload_json=json.dumps({'mode': 'appendIfNotExistsArr', 'items': items}, ensure_ascii=False).encode())

def apply(record, *ops, **limits):
    return apply_modifications(record, ops, check=lambda: None, **limits)

def equal(a, b, check=lambda: None):
    def fail(code):
        raise ValueError(code)
    return json_equal(a, b, check, fail)

class AppendIfAbsentTests(unittest.TestCase):
    def error(self, code, record, *ops, **limits):
        with self.assertRaises(ModificationError) as caught:
            apply(record, *ops, **limits)
        self.assertEqual(caught.exception.diagnostic.code, code)
        return caught.exception.diagnostic
    def test_compares_with_original_array_not_accepted_candidates(self):
        self.assertEqual(apply({'a': [1]}, op([1, 2, 2]))['a'], [1, 2, 2])
        self.assertEqual(apply({'a': [1, 1]}, op([1, 2]))['a'], [1, 1, 2])
    def test_deep_objects_ignore_key_order_arrays_preserve_order(self):
        old = [{'x': 1, 'y': [2, 3]}]
        out = apply({'a': old}, op([{'y': [2, 3], 'x': 1}, {'y': [3, 2], 'x': 1}]))
        self.assertEqual(len(out['a']), 2); self.assertEqual(out['a'][0], old[0])
        self.assertEqual(out['a'][1]['y'], [3, 2])
    def test_boolean_string_and_number_domains_are_distinct(self):
        self.assertEqual(apply({'a': [1]}, op([True, '1', 1.0]))['a'], [1, True, '1'])
        self.assertFalse(equal(True, 1)); self.assertTrue(equal(1, 1.0))
        self.assertFalse(equal(None, [])); self.assertFalse(equal({}, []))
    def test_object_is_signed_zero(self):
        self.assertFalse(equal(-0.0, 0)); self.assertTrue(equal(-0.0, -0.0))
        self.assertEqual(len(apply({'a': [-0.0]}, op([0]))['a']), 2)
    def test_missing_falsey_and_empty_targets(self):
        self.assertEqual(apply({}, op(['x', 'x'])), {'a': ['x', 'x']})
        for old in (None, False, 0, '', []):
            self.assertEqual(apply({'a': old}, op([1, 1]))['a'], [1, 1])
        self.error('unsupported_modification_target', {'a': 'truthy'}, op([1]))
    def test_scalar_null_and_object_items(self):
        for item in (None, False, 0, 'x', {'name': 'x'}):
            self.assertEqual(apply({'a': []}, op(item))['a'], [item])
            self.assertEqual(apply({'a': [item]}, op(item))['a'], [item])
    def test_later_instruction_sees_earlier_output(self):
        self.assertEqual(apply({'a': []}, op([1, 1]), op([1, 2, 2]))['a'], [1, 1, 2, 2])
    def test_nested_paths_wildcards_and_isolation(self):
        self.assertEqual(apply({'x': {'a': [1]}}, op([1, 2], 'x.a'))['x']['a'], [1, 2])
        payload = [{'x': []}]; instruction = op(payload, '*')
        out = apply({}, instruction); out['action'][0]['x'].append(1)
        self.assertEqual(out['trait'][0]['x'], [])
        self.assertEqual(payload, [{'x': []}]); self.assertEqual(apply({}, instruction)['action'], [{'x': []}])
    def test_utf8_equality_overflow_and_duplicate_payload_allowance(self):
        record = {'a': ['é'*30]}; instruction = op(['😀'*30])
        wanted = {'a': ['é'*30, '😀'*30]}
        cap = len(json.dumps(wanted, ensure_ascii=False, separators=(',', ':')).encode())
        self.assertEqual(apply(record, instruction, intermediate_creature_bytes=cap), wanted)
        self.error('intermediate_creature_bytes_limit', record, instruction, intermediate_creature_bytes=cap-1)
        small = {'a': ['é']}; exact = len(json.dumps(small, ensure_ascii=False, separators=(',', ':')).encode())
        self.assertEqual(apply(small, op(['é']*100), intermediate_creature_bytes=exact), small)
        self.assertEqual(record, {'a': ['é'*30]})
    def test_noop_budget_and_malformed_payload_are_explicit(self):
        self.assertEqual(apply({'a': [1]}, op([1]), modification_operations=1), {'a': [1]})
        self.error('modification_operations_limit', {'a': [1]}, op([1]), op([1]), modification_operations=1)
        missing = op([]); missing.payload_json = b'{"mode":"appendIfNotExistsArr"}'
        self.error('malformed_modification_payload', {}, missing)
        self.error('unsupported_substitution_value', {}, op(['<$name$>']))
        self.assertEqual(apply({'name': 'Ogre', 'a': ['Ogre']}, op(['<$name$>', 'x'])), {'name': 'Ogre', 'a': ['Ogre', 'x']})
    def test_unsupported_numbers_and_shadowing_fail_instead_of_approximating(self):
        d = self.error('unsupported_comparison_number', {'a': []}, op([2**53]))
        self.assertEqual((d.property, d.operation_index, d.mode), ('a', 0, 'appendIfNotExistsArr'))
        self.error('unsupported_comparison_key', {'a': []}, op([{'hasOwnProperty': 1}]))
        with self.assertRaisesRegex(ValueError, 'malformed_record'):
            equal(float('inf'), float('inf'))
    def test_comparison_checks_cancellation(self):
        probes = [0]
        def check():
            probes[0] += 1
            if probes[0] == 10:
                raise RuntimeError('cancelled')
        with self.assertRaisesRegex(RuntimeError, 'cancelled'):
            equal(list(range(100)), list(range(100)), check)
        self.assertEqual(probes[0], 10)

if __name__ == '__main__':
    unittest.main()
