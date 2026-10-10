"""Focused battle-entry/timer and round-boundary regressions for 3d5b2d4.
Production battle classes are AST-extracted; real turn/lair helpers are imported.
Effect expiry, checkpoints and persistence are explicit fixtures, not integration
with the feature/storage services. SQLite integer binding is real.
"""
import ast
import asyncio
import copy
import sqlite3
import types
import unittest
from pathlib import Path
from python.scrying_glass_turn_rules import can_take_turn
from python.scrying_glass_lair_rules import participants,initiative_key,place_lair
ROOT=Path(__file__).resolve().parents[1]

def cls(path,name):
    tree=ast.parse((ROOT/path).read_text());node=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name==name)
    future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
    scope=dict(can_take_turn=can_take_turn,participants=participants,initiative_key=initiative_key,place_lair=place_lair)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future,node],type_ignores=[])),'production-extract','exec'),scope)
    return scope[name]
BattleService=cls('python/scrying_glass_service_battle.py','BattleService')
AdminBattleMixin=cls('python/scrying_glass_admin_battle.py','AdminBattleMixin')
class HTTPError(Exception):
    def __init__(self,status_code,detail):self.status_code=status_code;self.detail=detail;super().__init__(detail)

def combatant(ident,initiative):
    return dict(id=ident,name=ident,hp=10,alive=True,active=True,visible=False,in_turn=False,initiative=initiative,effects=[])

def effect(anchor='a',timing='start',turns=2):return dict(id='effect',anchor_id=anchor,timing=timing,turns=turns)

class BattleTests(unittest.TestCase):
    def setUp(self):
        self.a=combatant('a',15);self.b=combatant('b',10)
        self.events=[];self.snapshots=[];self.saved=[]
        self.state=dict(characters=[self.a,self.b],monsters=[],lairs=[],battle_order=[],battle_round=0,
                        turn_successors=[],turn_successors_before_wrap=[],activity_log=[])
        self.c=types.SimpleNamespace(STATE=self.state,HTTPException=HTTPError,
            entities=lambda:self.state['characters']+self.state['monsters'],active_campaign=lambda:'1',
            admin_initiative_key=initiative_key,save_active_campaign_characters=lambda:None,
            public_state=lambda:copy.deepcopy(self.state))
        self.c.entity=lambda ident:next((x for x in participants(self.c) if x['id']==ident),None)
        self.c.active_combatant=lambda:next((x for x in participants(self.c) if x.get('in_turn')),None)
        self.service=BattleService(self.c)
        for name in vars(BattleService):
            method=getattr(self.service,name,None)
            if not name.startswith('_') and callable(method):setattr(self.c,name,method)
        self.c.features=types.SimpleNamespace(expire=self.expire,store=types.SimpleNamespace(save_snapshot=self.snapshot))
        async def changed(**kwargs):self.saved.append(copy.deepcopy(self.state))
        self.c.combatants_changed=changed
        self.admin=AdminBattleMixin();self.admin.context=self.c
    def snapshot(self,*args):self.snapshots.append(copy.deepcopy(self.state))
    def expire(self,anchor,timing):
        self.events.append((anchor,timing))
        for target in self.c.entities():
            kept=[]
            for e in target['effects']:
                if e['anchor_id']==anchor and e['timing']==timing:
                    e['turns']-=1
                    if e['turns']==0:continue
                kept.append(e)
            target['effects']=kept
    def start(self,order=None):return asyncio.run(self.admin.battle_start(types.SimpleNamespace(order=order or ['a','b'])))
    def test_initial_start_event(self):
        self.start();self.assertEqual(self.events,[('a','start')])
    def test_initial_counter_decrements(self):
        self.b['effects']=[effect()];self.start();self.assertEqual(self.b['effects'][0]['turns'],1)
    def test_initial_one_turn_effect_expires(self):
        self.b['effects']=[effect(turns=1)];self.start();self.assertEqual(self.b['effects'],[])
    def test_other_anchor_untouched(self):
        self.b['effects']=[effect(anchor='b')];self.start();self.assertEqual(self.b['effects'][0]['turns'],2)
    def test_end_timing_untouched(self):
        self.b['effects']=[effect(timing='end')];self.start();self.assertEqual(self.b['effects'][0]['turns'],2)
    def test_manual_timing_untouched(self):
        self.b['effects']=[effect(timing='manual',turns=None)];self.start();self.assertIsNone(self.b['effects'][0]['turns'])
    def test_checkpoint_is_before_expiry(self):
        self.b['effects']=[effect()];self.start();self.assertEqual(self.snapshots[0]['characters'][1]['effects'][0]['turns'],2)
    def test_persisted_and_returned_state_include_expiry(self):
        self.b['effects']=[effect()];result=self.start()
        self.assertEqual(result['characters'][1]['effects'][0]['turns'],1)
        self.assertEqual(self.saved[-1]['characters'][1]['effects'][0]['turns'],1)
    def test_lair_first_start_event(self):
        self.state['lairs']=[dict(id='lair',kind='lair',active=True,visible=False,in_turn=False,initiative=20)]
        self.start();self.assertEqual(self.events,[('lair','start')])
    def test_explicit_order_controls_first_anchor(self):
        self.start(['b','a']);self.assertEqual(self.events,[('b','start')])
    def test_next_turn_end_then_start(self):
        self.start();self.events.clear();asyncio.run(self.admin.battle_next())
        self.assertEqual(self.events,[('a','end'),('b','start')]);self.assertEqual(self.state['battle_round'],1)
    def test_start_without_feature_service(self):
        del self.c.features;self.start();self.assertEqual(self.state['battle_round'],1)
    def test_invalid_start_does_not_emit_timer_event(self):
        with self.assertRaises(HTTPError):self.start(['a'])
        self.assertEqual(self.events,[])
    def wrap(self,round_number):
        self.c.begin_battle(['a','b']);self.a['in_turn']=False;self.b['in_turn']=True
        self.state['battle_round']=round_number
        return self.c.advance_turn()
    def test_regular_wrap(self):
        target=self.wrap(3);self.assertEqual(target['id'],'a');self.assertEqual(self.state['battle_round'],4)
    def test_last_valid_round_increment(self):
        self.wrap(2**63-2);self.assertEqual(self.state['battle_round'],2**63-1)
        with sqlite3.connect(':memory:') as db:db.execute('SELECT ?', (self.state['battle_round'],))
    def test_round_overflow_is_controlled(self):
        with self.assertRaises(HTTPError) as raised:self.wrap(2**63-1)
        self.assertEqual(raised.exception.status_code,409)
        self.assertEqual(self.state['battle_round'],2**63-1);self.assertTrue(self.b['in_turn'])
    def test_turn_change_without_wrap_at_maximum(self):
        self.c.begin_battle(['a','b']);self.state['battle_round']=2**63-1
        self.assertEqual(self.c.advance_turn()['id'],'b');self.assertEqual(self.state['battle_round'],2**63-1)
    def test_advance_never_produces_unbindable_round(self):
        try:self.wrap(2**63-1)
        except HTTPError:return
        with sqlite3.connect(':memory:') as db:db.execute('SELECT ?', (self.state['battle_round'],))

if __name__=='__main__':unittest.main()
