"""04c.2a executor remove/array semantics; graph and worker are later stages."""
import json
import unittest
from types import SimpleNamespace
from python.scrying_glass_fivetools_modifications import apply_modifications, ModificationError, ENTRY_PROPS

def op(prop, mode, **payload):
    value = 'remove' if mode == 'remove' else {'mode': mode, **payload}
    return SimpleNamespace(property=prop, mode=mode, payload_json=json.dumps(value, ensure_ascii=False).encode())

def apply(record, *ops, **limits):
    return apply_modifications(record, ops, check=lambda: None, **limits)

class ArrayRemovalTests(unittest.TestCase):
    def error(self, code, fn):
        with self.assertRaises(ModificationError) as caught:
            fn()
        self.assertEqual(caught.exception.diagnostic.code, code)
        return caught.exception.diagnostic
    def test_nested_removal_missing_and_no_parent_pruning(self):
        record = {'a': {'b': 1}, 'c': 2}
        self.assertEqual(apply(record, op('a.b', 'remove')), {'a': {}, 'c': 2})
        self.assertEqual(record, {'a': {'b': 1}, 'c': 2})
        self.assertEqual(apply(record, op('missing.x', 'remove')), record)
        self.assertEqual(apply({'a': None}, op('a.b', 'remove')), {'a': None})
    def test_removal_inside_array_not_splicing_or_fabricating_holes(self):
        self.assertEqual(apply({'a': [{'x': 1}]}, op('a.0.x', 'remove')), {'a': [{}]})
        self.error('unsupported_modification_path', lambda: apply({'a': [1, 2]}, op('a.0', 'remove')))
    def test_unscoped_and_wildcard_remove(self):
        self.assertEqual(apply({'null': 'literal', 'a': 1}, op('_', 'remove')), {'a': 1})
        record = {p: ['x'] for p in ENTRY_PROPS}; record['keep'] = 1
        self.assertEqual(apply(record, op('*', 'remove')), {'keep': 1})
    def test_append_prepend_scalar_object_and_null_items(self):
        for mode in ('appendArr', 'prependArr'):
            for item in ('x', 0, False, None, {'name': 'x'}):
                with self.subTest(mode=mode, item=item):
                    wanted = ['old', item] if mode == 'appendArr' else [item, 'old']
                    self.assertEqual(apply({'a': ['old']}, op('a', mode, items=item)), {'a': wanted})
    def test_falsey_targets_and_empty_arrays(self):
        for mode in ('appendArr', 'prependArr'):
            for value in (None, False, 0, '', []):
                self.assertEqual(apply({'a': value}, op('a', mode, items=['x']))['a'], ['x'])
            self.assertEqual(apply({}, op('a', mode, items=[])), {'a': []})
            self.error('unsupported_modification_target', lambda: apply({'a': 'truthy'}, op('a', mode, items=['x'])))
    def test_order_sensitive_lists_and_remove_then_recreate(self):
        self.assertEqual(apply({'a': [0]}, op('a', 'appendArr', items=[1, 2]), op('a', 'prependArr', items=[-1])), {'a': [-1, 0, 1, 2]})
        self.assertEqual(apply({'a': ['old']}, op('a', 'remove'), op('a', 'appendArr', items=['new'])), {'a': ['new']})
        self.assertEqual(apply({'a': ['old']}, op('a', 'appendArr', items=['new']), op('a', 'remove')), {})
    def test_wildcard_items_and_input_payload_isolation(self):
        payload = {'x': []}; instruction = op('*', 'appendArr', items=payload)
        first = apply({}, instruction); first['action'][0]['x'].append(1)
        self.assertEqual(first['trait'][0]['x'], [])
        self.assertEqual(payload, {'x': []})
        self.assertEqual(apply({}, instruction)['action'], [{'x': []}])
    def test_byte_equality_and_overflow_are_atomic(self):
        record = {'a': ['é'*100]}; instruction = op('a', 'appendArr', items=['😀'*100])
        wanted = {'a': ['é'*100, '😀'*100]}
        size = len(json.dumps(wanted, ensure_ascii=False, separators=(',', ':')).encode())
        self.assertEqual(apply(record, instruction, intermediate_creature_bytes=size), wanted)
        self.error('intermediate_creature_bytes_limit', lambda: apply(record, instruction, intermediate_creature_bytes=size-1))
        self.assertEqual(record, {'a': ['é'*100]})
        self.error('modification_operations_limit', lambda: apply({}, op('a', 'remove'), op('b', 'remove'), modification_operations=1))
    def test_malformed_remove_and_missing_array_items_are_explicit(self):
        wrong = op('a', 'appendArr'); wrong.mode = 'remove'
        self.error('malformed_modification_payload', lambda: apply({}, wrong))
        self.error('malformed_modification_payload', lambda: apply({}, op('a', 'appendArr')))
        self.error('unsafe_modification_path', lambda: apply({}, op('a.__proto__', 'remove')))

if __name__ == '__main__':
    unittest.main()
