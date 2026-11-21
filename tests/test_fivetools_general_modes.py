"""022.04c.3c-04c.5 general copy modes; expectations checked against the pinned runtime."""
import json
import unittest
from types import SimpleNamespace

from python.scrying_glass_fivetools_modifications import apply_modifications, ModificationError


def op(selector, mode, **payload):
    data = {'mode': mode, **payload}
    return SimpleNamespace(property=selector, mode=mode, payload_json=json.dumps(data).encode())


def apply(record, *ops, **kwargs):
    return apply_modifications(record, ops, check=lambda: None, **kwargs)


ACTIONS = [{'name': 'Multiattack', 'entries': ['The ogre attacks twice.']},
           {'name': 'Club', 'entries': ['{@atk mw} {@hit 6} the ogre hits. {@dc 13|special}']}, 'plain']


class GeneralModeTests(unittest.TestCase):
    def error(self, code, record, *ops, **kwargs):
        with self.assertRaises(ModificationError) as caught:
            apply(record, *ops, **kwargs)
        self.assertEqual(caught.exception.diagnostic.code, code)
        return caught.exception.diagnostic

    def test_replace_text_skips_tags_and_honours_props(self):
        out = apply({'action': ACTIONS}, op('action', 'replaceTxt', **{'replace': 'the ogre', 'with': 'Grok', 'flags': 'i'}))
        self.assertEqual(out['action'][0]['entries'], ['Grok attacks twice.'])
        out = apply({'action': ACTIONS}, op('action', 'replaceTxt', **{'replace': 'hit', 'with': 'X'}))
        self.assertEqual(out['action'][1]['entries'][0], '{@atk mw} {@hit 6} the ogre Xs. {@dc 13|special}')
        out = apply({'action': ACTIONS}, op('action', 'replaceTxt', **{'replace': 'hit', 'with': 'X', 'tagInsensitive': True}))
        self.assertIn('{@X 6}', out['action'][1]['entries'][0])
        out = apply({'action': ACTIONS}, op('action', 'replaceTxt', **{'replace': 'plain', 'with': 'P', 'props': ['entries']}))
        self.assertEqual(out['action'][2], 'plain')
        out = apply({'action': ACTIONS}, op('action', 'replaceTxt', **{'replace': 'plain', 'with': 'P'}))
        self.assertEqual(out['action'][2], 'P')
        self.assertEqual(apply({'action': ACTIONS}, op('action', 'replaceTxt', **{'replace': 'a', 'with': 'b', 'props': []})), {'action': ACTIONS})

    def test_replace_text_targets_and_growth(self):
        self.assertEqual(apply({}, op('missing', 'replaceTxt', **{'replace': 'a', 'with': 'b'})), {})
        self.error('malformed_modification_path', {}, op('_', 'replaceTxt', **{'replace': 'a', 'with': 'b'}))
        self.error('unsupported_modification_target', {'x': {'a': 'b'}}, op('x', 'replaceTxt', **{'replace': 'a', 'with': 'b'}))
        self.error('malformed_modification_payload', {'x': ['a']}, op('x', 'replaceTxt', replace='a'))
        self.error('intermediate_creature_bytes_limit', {'x': ['a' * 50]},
                   op('x', 'replaceTxt', **{'replace': 'a', 'with': 'aaaa'}), intermediate_creature_bytes=150)

    def test_replace_name(self):
        out = apply({'action': ACTIONS}, op('action', 'replaceName', **{'replace': 'club', 'with': 'Maul', 'flags': 'i'}))
        self.assertEqual([a.get('name') if type(a) is dict else a for a in out['action']], ['Multiattack', 'Maul', 'plain'])

    def test_replace_array_selectors(self):
        def names(out):
            return [a.get('name') if type(a) is dict else a for a in out['action']]
        new = {'name': 'Rock', 'entries': ['r']}
        self.assertEqual(names(apply({'action': ACTIONS}, op('action', 'replaceArr', replace='Club', items=new))), ['Multiattack', 'Rock', 'plain'])
        self.assertEqual(names(apply({'action': ACTIONS}, op('action', 'replaceArr', replace='plain', items=[new, 'x']))), ['Multiattack', 'Club', 'Rock', 'x'])
        self.assertEqual(names(apply({'action': ACTIONS}, op('action', 'replaceArr', replace={'regex': '^m', 'flags': 'i'}, items=new))), ['Rock', 'Club', 'plain'])
        self.assertEqual(names(apply({'action': ACTIONS}, op('action', 'replaceArr', replace={'index': -2}, items=new))), ['Multiattack', 'Rock', 'plain'])
        self.assertEqual(names(apply({'action': ACTIONS}, op('action', 'replaceArr', replace={'index': 1.7}, items=[]))), ['Multiattack', 'plain'])
        self.error('missing_modification_item', {'action': ACTIONS}, op('action', 'replaceArr', replace={'index': -1}, items=new))
        self.error('missing_modification_item', {'action': ACTIONS}, op('action', 'replaceArr', replace='Nope', items=new))
        self.error('missing_modification_target', {}, op('action', 'replaceArr', replace='Nope', items=new))
        self.error('malformed_modification_payload', {'action': ACTIONS}, op('action', 'replaceArr', items=new))
        out = apply({'action': ACTIONS}, op('action', 'replaceOrAppendArr', replace='Nope', items=new))
        self.assertEqual(names(out), ['Multiattack', 'Club', 'plain', 'Rock'])
        self.assertEqual(apply({}, op('action', 'replaceOrAppendArr', replace='Nope', items=new))['action'], [new])

    def test_remove_and_rename(self):
        def names(out):
            return [a.get('name') if type(a) is dict else a for a in out['action']]
        self.assertEqual(names(apply({'action': ACTIONS}, op('action', 'removeArr', names=['Club', 'Multiattack']))), ['plain'])
        self.error('missing_modification_item', {'action': ACTIONS}, op('action', 'removeArr', names='Nope'))
        self.assertEqual(names(apply({'action': ACTIONS}, op('action', 'removeArr', names='Nope', force=True))), ['Multiattack', 'Club', 'plain'])
        self.assertEqual(names(apply({'action': ACTIONS}, op('action', 'removeArr', items='plain'))), ['Multiattack', 'Club'])
        self.error('missing_modification_item', {'action': ACTIONS}, op('action', 'removeArr', items={'name': 'Club'}))
        self.error('malformed_modification_payload', {'action': ACTIONS}, op('action', 'removeArr'))
        self.error('missing_modification_target', {}, op('action', 'removeArr', names='Club'))
        out = apply({'action': ACTIONS}, op('action', 'renameArr', renames=[{'rename': 'Club', 'with': 'C'}, {'rename': 'C', 'with': 'D'}]))
        self.assertEqual(names(out), ['Multiattack', 'D', 'plain'])
        self.error('missing_modification_item', {'action': ACTIONS}, op('action', 'renameArr', renames={'rename': 'Nope', 'with': 'x'}))

    def test_scalar_properties_keep_string_signs(self):
        record = {'m': {'a': 1, 'b': '+2', 'c': '-5', '10': 4}}
        out = apply(record, op('m', 'scalarAddProp', prop='*', scalar=-3))
        self.assertEqual(out['m'], {'a': -2, 'b': '-1', 'c': '-8', '10': 1})
        out = apply(record, op('m', 'scalarMultProp', prop='b', scalar=1.5, floor=True))
        self.assertEqual(out['m']['b'], '+3')
        self.assertEqual(apply(record, op('m', 'scalarMultProp', prop='a', scalar=0.5))['m']['a'], 0.5)
        self.error('nonfinite_numeric_result', record, op('m', 'scalarAddProp', prop='zz', scalar=1))
        self.assertEqual(apply({}, op('m', 'scalarAddProp', prop='a', scalar=1)), {})
        self.error('malformed_modification_payload', record, op('m', 'scalarAddProp', prop='a', scalar='1'))

    def test_calculate_property_uses_restricted_evaluation(self):
        record = {'cr': '13', 'dex': 14, 'm': {}}
        out = apply(record, op('m', 'calculateProp', prop='x', formula='2 * <$prof_bonus$> + <$dex_mod$>'))
        self.assertEqual(out['m']['x'], 12)
        self.assertEqual(apply({'cr': '1'}, op('n', 'calculateProp', prop='x', formula='10 / 4'))['n'], {'x': 2.5})
        self.error('unknown_formula_variable', record, op('m', 'calculateProp', prop='x', formula='<$wis_mod$>'))
        self.error('nonfinite_numeric_result', record, op('m', 'calculateProp', prop='x', formula='1/0'))

    def test_hit_and_dc_tags(self):
        out = apply({'action': ACTIONS}, op('*', 'scalarAddHit', scalar=2), op('action', 'scalarAddDc', scalar=-3))
        self.assertEqual(out['action'][1]['entries'][0], '{@atk mw} {@hit 8} the ogre hits. {@dc 10}')
        self.assertEqual(apply({}, op('action', 'scalarAddHit', scalar=1)), {})

    def test_reversed_compositions_change_the_result(self):
        first = apply({'action': ['the ogre']}, op('action', 'replaceTxt', **{'replace': 'ogre', 'with': 'troll'}),
                      op('action', 'appendArr', items='the ogre'))
        second = apply({'action': ['the ogre']}, op('action', 'appendArr', items='the ogre'),
                       op('action', 'replaceTxt', **{'replace': 'ogre', 'with': 'troll'}))
        self.assertEqual(first['action'], ['the troll', 'the ogre'])
        self.assertEqual(second['action'], ['the troll', 'the troll'])


if __name__ == '__main__':
    unittest.main()
