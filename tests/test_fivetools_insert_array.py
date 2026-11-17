"""04c.3b insertion regressions; no live provider dependencies."""
import json
import unittest
from types import SimpleNamespace
from python.scrying_glass_fivetools_modifications import apply_modifications, ModificationError, ENTRY_PROPS
from python.scrying_glass_fivetools_modifications import insert_position

MISSING = object()
def op(items=MISSING, index=MISSING, prop='a', mode='insertArr'):
    payload = {'mode': mode}
    if items is not MISSING:
        payload['items'] = items
    if index is not MISSING:
        payload['index'] = index
    return SimpleNamespace(property=prop, mode=mode, payload_json=json.dumps(payload, ensure_ascii=False).encode())
def apply(record, *ops, **limits):
    return apply_modifications(record, ops, check=lambda: None, **limits)

class InsertArrayTests(unittest.TestCase):
    def error(self, code, record, *ops, **limits):
        with self.assertRaises(ModificationError) as caught:
            apply(record, *ops, **limits)
        self.assertEqual(caught.exception.diagnostic.code, code)
        return caught.exception.diagnostic
    def test_positions(self):
        for i, expected in [(0, ['x',0,1,2]), (1,[0,'x',1,2]), (3,[0,1,2,'x']), (100,[0,1,2,'x']), (-2,[0,'x',1,2]), (-100,['x',0,1,2])]:
            with self.subTest(index=i):
                self.assertEqual(apply({'a':[0,1,2]},op('x',i))['a'],expected)
    def test_sentinel_aliases(self):
        for i in (-1,-1.9,-4294967297,4294967295,4294967295.5):
            self.assertEqual(apply({'a':[0,1,2]},op('x',i))['a'],[0,1,2,'x'])
    def test_fractional_and_default(self):
        for i in (1.9,-2.9):
            self.assertEqual(apply({'a':[0,1,2]},op('x',i))['a'],[0,'x',1,2])
        for i in (MISSING,None,-0.0,-0.9):
            self.assertEqual(apply({'a':[1]},op('x',i))['a'],['x',1])
    def test_targets(self):
        self.assertEqual(apply({'a':[]},op('x',-1)),{'a':['x']})
        for record in ({},{'a':None},{'a':False},{'a':0},{'a':''}):
            self.error('missing_modification_target',record,op('x',0))
        self.error('unsupported_modification_target',{'a':'truthy'},op('x',0))
    def test_item_shapes(self):
        for item in ('x',0,False,None,{'name':'x'}):
            self.assertEqual(apply({'a':[1]},op(item,0))['a'],[item,1])
        self.assertEqual(apply({'a':[1]},op([['nested'],'x','x'],0))['a'],[['nested'],'x','x',1])
    def test_paths(self):
        self.assertEqual(apply({'x':[{'a':[1]}]},op('x',0,'x.0.a'))['x'][0]['a'],['x',1])
        self.error('unsafe_modification_path',{},op('x',0,'a.__proto__'))
    def test_order(self):
        self.assertEqual(apply({'a':[1]},op('first',0),op('second',0))['a'],['second','first',1])
        self.assertEqual(apply({'a':[1]},op([2],mode='appendArr'),op([3],-1))['a'],[1,2,3])
    def test_wildcard_isolation(self):
        record={p:[] for p in ENTRY_PROPS}; items=[{'x':[]}]
        out=apply(record,op(items,0,'*')); out['action'][0]['x'].append(1)
        self.assertEqual(out['trait'],[{'x':[]}]); self.assertEqual(items,[{'x':[]}])
        self.assertEqual(record['action'],[])
        self.error('missing_modification_target',{'action':[]},op(items,0,'*'))
    def test_utf8_boundary(self):
        record={'a':['é'*30]}; wanted={'a':['😀'*30,'é'*30]}
        cap=len(json.dumps(wanted,ensure_ascii=False,separators=(',',':')).encode())
        self.assertEqual(apply(record,op(['😀'*30],0),intermediate_creature_bytes=cap),wanted)
        self.error('intermediate_creature_bytes_limit',record,op(['😀'*30],0),intermediate_creature_bytes=cap-1)
        self.assertEqual(record,{'a':['é'*30]})
    def test_invalid_indices(self):
        for i in (True,False,'1',[],{}):
            d=self.error('malformed_modification_index',{'a':[1]},op('x',i))
            self.assertEqual((d.property,d.operation_index,d.mode),('a',0,'insertArr'))
        self.error('unsupported_modification_index',{'a':[1]},op('x',2**53))
        overflow=op('x',0); overflow.payload_json=overflow.payload_json.replace(b'"index": 0',b'"index": 1e400')
        self.error('malformed_modification_index',{'a':[1]},overflow)
        self.error('malformed_modification_payload',{'a':[1]},op('x',float('inf')))
    def test_payload_and_budget(self):
        self.error('malformed_modification_payload',{'a':[]},op(index=0))
        self.error('dynamic_substitution_pending_04d',{'a':[]},op(['<$name$>'],0))
        self.assertEqual(apply({'a':[]},op([],0),modification_operations=1),{'a':[]})
        self.error('modification_operations_limit',{'a':[]},op([],0),op([],0),modification_operations=1)
    def test_cancellation(self):
        def stop():
            raise RuntimeError('cancelled')
        with self.assertRaisesRegex(RuntimeError,'cancelled'):
            insert_position(0,3,stop,lambda code:None)
        with self.assertRaisesRegex(RuntimeError,'cancelled'):
            apply_modifications({'a':[1]},(op('x',0),),check=stop)

if __name__ == '__main__':
    unittest.main()
