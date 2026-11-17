"""04c.1 native executor tests; compiler-shaped records, no graph integration."""
import json
import unittest
from types import SimpleNamespace
from python.scrying_glass_fivetools_modifications import (
    apply_modifications, ModificationError, ENTRY_PROPS,
)

def op(selector, mode, **payload):
    data = {'mode': mode, **payload}
    return SimpleNamespace(property=selector, mode=mode,
        payload_json=json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode())

def apply(record, *ops, **kwargs):
    return apply_modifications(record, ops, check=lambda: None, **kwargs)

def wire(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()

class ModificationTests(unittest.TestCase):
    def error(self, code, record, *ops, **kwargs):
        with self.assertRaises(ModificationError) as caught:
            apply(record, *ops, **kwargs)
        self.assertEqual(caught.exception.diagnostic.code, code)
        return caught.exception.diagnostic
    def test_append_string_and_javascript_falsey_values(self):
        for original in ('base', '', None, False, 0):
            out = apply({'label': original}, op('label', 'appendStr', str='next', joiner=' / '))
            self.assertEqual(out['label'], 'base / next' if original == 'base' else 'next')
        self.assertEqual(apply({}, op('label', 'appendStr', str='new'))['label'], 'new')
        self.error('unsupported_modification_target', {'label': []}, op('label', 'appendStr', str='x'))
    def test_dotted_paths_arrays_and_falsey_parent_creation(self):
        self.assertEqual(apply({'entries': [{'name': 'A'}]}, op('entries.0.name', 'appendStr', str='B'))['entries'][0]['name'], 'AB')
        for value in (None, False, 0, ''):
            self.assertEqual(apply({'a': value}, op('_', 'setProp', prop='a.b', value=3)), {'a': {'b': 3}})
        self.error('unsupported_modification_path', {'a': []}, op('a.1', 'setProp', value='x'))
    def test_set_prop_deepcopy_and_overwrite(self):
        record = {'nested': {'old': 1}}; instruction = op('nested', 'setProp', prop='child', value={'x': [1]})
        out = apply(record, instruction)
        self.assertEqual(record, {'nested': {'old': 1}})
        out['nested']['child']['x'].append(2)
        self.assertEqual(apply(record, instruction)['nested']['child']['x'], [1])
        self.assertEqual(apply({'x': 'old'}, op('x', 'setProp', value=None)), {'x': None})
    def test_prefix_suffix_nonstrings_and_missing_are_noops(self):
        instruction = op('_', 'prefixSuffixStringProp', prop='x', prefix='[', suffix=']')
        self.assertEqual(apply({'x': 'A'}, instruction), {'x': '[A]'})
        self.assertEqual(apply({'x': ''}, instruction), {'x': '[]'})
        for record in ({}, {'x': None}, {'x': 3}, {'x': []}):
            self.assertEqual(apply(record, instruction), record)
        self.assertEqual(apply({}, op('_', 'setProp', value=3)), {})
    def test_selected_template_groups_merge_before_tail_groups(self):
        ops = (op('_', 'setProp', prop='label', value='root'),
            op('label', 'appendStr', str='selected'),
            op('label', 'appendStr', str='template'),
            op('_', 'prefixSuffixStringProp', prop='label', suffix='!'))
        self.assertEqual(apply({'label': 'base'}, *ops)['label'], 'root!')
        a = op('label', 'appendStr', str='a'); b = op('label', 'prefixSuffixStringProp', prefix='[' , suffix=']')
        self.assertEqual(apply({'label': 'x'}, a, b)['label'], '[xa]')
        self.assertEqual(apply({'label': 'x'}, b, a)['label'], '[x]a')
    def test_first_seen_ordinary_group_order_and_root_precedes_wildcard(self):
        out = apply({}, op('b', 'setProp', value={}), op('a', 'setProp', value=1), op('b', 'setProp', prop='x', value=3))
        self.assertEqual(list(out), ['b', 'a']); self.assertEqual(out, {'b': {'x': 3}, 'a': 1})
        out = apply({}, op('*', 'appendStr', str='!'), op('_', 'setProp', prop='action', value='first'))
        self.assertEqual(out['action'], 'first!'); self.assertEqual(list(out), list(ENTRY_PROPS))
    def test_wildcard_payloads_are_independent(self):
        out = apply({}, op('*', 'setProp', value={'x': []}))
        self.assertEqual(list(out), list(ENTRY_PROPS))
        out['action']['x'].append(1)
        self.assertEqual(out['trait']['x'], [])
        self.assertEqual(apply({'trait': [{'name': 'A'}]}, op('*', 'prefixSuffixStringProp', prop='0.name', suffix='!'))['trait'][0]['name'], 'A!')
    def test_mode_failures_unknown_modes_and_atomic_failure(self):
        record = {'x': 'base'}
        for mode, code in (('replaceArr', 'malformed_modification_payload'),
                           ('removeArr', 'unsupported_modification_target'),
                           ('unknown', 'unknown_modification_mode')):
            d = self.error(code, record,
                op('x', 'appendStr', str='a'), op('x', mode))
            self.assertEqual((d.property, d.operation_index, d.mode), ('x', 1, mode))
            self.assertEqual(record, {'x': 'base'})
    def test_paths_payloads_and_dynamic_variables_fail_explicitly(self):
        for key in ('__proto__.x', 'a.constructor.x', 'x..y', 'a.prototype'):
            self.error('unsafe_modification_path', {}, op('_', 'setProp', prop=key, value=1))
        self.error('malformed_modification_path', {}, op('_', 'appendStr', str='x'))
        self.error('malformed_modification_payload', {}, op('x', 'setProp'))
        self.error('malformed_modification_payload', {}, op('x', 'appendStr', str=3))
        self.error('unsupported_substitution_value', {}, op('x', 'setProp', value={'text': '<$name$>'}))
        self.assertEqual(apply({'name': 'Ogre'}, op('x', 'setProp', value={'text': '<$name$>'}))['x'], {'text': 'Ogre'})
        d = self.error('malformed_modification_payload', {}, op('a/b~c', 'appendStr', str=3))
        self.assertEqual(d.source_path, '$/_copy/_mod/a~1b~0c')
    def test_byte_equality_one_over_and_expansion_before_join(self):
        record = {'x': 'é'}; instruction = op('x', 'appendStr', str='😀'*100)
        expected = {'x': 'é'+'😀'*100}; size = len(wire(expected))
        self.assertEqual(apply(record, instruction, intermediate_creature_bytes=size), expected)
        self.error('intermediate_creature_bytes_limit', record, instruction, intermediate_creature_bytes=size-1)
        self.assertEqual(record, {'x': 'é'})
        self.error('intermediate_creature_bytes_limit', {}, op('*', 'setProp', value='x'*100), intermediate_creature_bytes=400)
    def test_operation_budget_counts_noops_and_wildcard_once(self):
        ops = (op('missing', 'prefixSuffixStringProp', suffix='!'),)*2
        self.assertEqual(apply({}, *ops, modification_operations=2), {})
        self.error('modification_operations_limit', {}, *ops, modification_operations=1)
        self.assertEqual(len(apply({}, op('*', 'setProp', value='x'), modification_operations=1)), 13)
    def test_invalid_limits_cancellation_and_record_isolation(self):
        for value in (False, 0, -1, 0.5, 2**63):
            with self.assertRaises(ValueError):
                apply({}, intermediate_creature_bytes=value)
        record = {'x': ['unchanged']}; probes = [0]
        def check():
            probes[0] += 1
            if probes[0] == 12:
                raise RuntimeError('cancelled')
        with self.assertRaisesRegex(RuntimeError, 'cancelled'):
            apply_modifications(record, (op('x', 'setProp', value=[]),), check=check)
        self.assertEqual(record, {'x': ['unchanged']})
        out = apply(record); out['x'].append('new')
        self.assertEqual(record, {'x': ['unchanged']})

if __name__ == '__main__':
    unittest.main()
