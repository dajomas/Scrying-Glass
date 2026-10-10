"""Lair-button backend tests using real rules/services and mocked persistence."""
import ast
import asyncio
import copy
import unittest
from pathlib import Path
from types import SimpleNamespace
from python.scrying_glass_lair_rules import participants,initiative_key,place_lair,normalize_lairs
from python.scrying_glass_turn_rules import can_take_turn
from python.scrying_glass_service_lairs import LairService

class HTTPError(Exception):
    def __init__(self,status_code,detail):self.status_code=status_code;self.detail=detail

class LairButtonTests(unittest.TestCase):
    def setUp(self):
        self.c=SimpleNamespace(HTTPException=HTTPError)
        self.c.STATE={'characters':[{'id':'c','name':'Hero','hp':20,'active':True,'alive':True,'in_turn':True,'initiative':21}],
            'monsters':[{'id':'m','name':'Monster','monster_species':'Goblin','hp':10,'active':True,'alive':True,'in_turn':False,'initiative':19}],
            'lairs':normalize_lairs([{'id':'l','name':'Lair'}]),'battle_order':['c','l','m'],'battle_round':1,
            'turn_successors':[],'turn_successors_before_wrap':[]}
        self.c.entities=lambda:self.c.STATE['characters']+self.c.STATE['monsters']
        self.c.entity=lambda ident:next((x for x in participants(self.c) if x['id']==ident),None)
        self.c.active_combatant=lambda:next((x for x in participants(self.c) if x.get('in_turn')),None)
        self.c.admin_initiative_key=initiative_key
        self.logs=[];self.c.features=SimpleNamespace(log=lambda *args,**kwargs:self.logs.append((args,kwargs)))
        self.persisted=0
        async def persist(**kwargs):self.persisted+=1
        self.c.combatants_changed=persist
        tree=ast.parse((Path(__file__).resolve().parents[1]/'python/scrying_glass_service_battle.py').read_text())
        cls=next(x for x in tree.body if isinstance(x,ast.ClassDef))
        future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
        scope={'can_take_turn':can_take_turn,'participants':participants,'initiative_key':initiative_key,'place_lair':place_lair}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),'battle-service','exec'),scope)
        service=scope['BattleService'](self.c)
        for name in vars(scope['BattleService']):
            if not name.startswith('_') and callable(getattr(service,name,None)):setattr(self.c,name,getattr(service,name))
        self.service=LairService(self.c)
    def update(self,body):return asyncio.run(self.service.update_lair('l',body))
    def test_turn_assigns_exclusively_and_reveals(self):
        self.c.entity('l')['visible']=False;self.update({'in_turn':True})
        self.assertEqual([x['id'] for x in participants(self.c) if x.get('in_turn')],['l'])
        self.assertTrue(self.c.entity('l')['visible']);self.assertEqual(self.persisted,1)
    def test_turn_toggle_off_preserves_next(self):
        self.update({'in_turn':True});self.update({'in_turn':False})
        self.assertIsNone(self.c.active_combatant());self.assertEqual(self.c.advance_turn()['id'],'m')
    def test_turn_inactive_rejected_before_mutation(self):
        self.update({'active':False});before=copy.deepcopy(self.c.STATE)
        with self.assertRaises(HTTPError):self.update({'in_turn':True})
        self.assertEqual(self.c.STATE,before)
    def test_join_and_turn_together(self):
        self.update({'active':False});self.update({'active':True,'in_turn':True})
        self.assertEqual(self.c.active_combatant()['id'],'l');self.assertIn('l',self.c.STATE['battle_order'])
    def test_leave_current_clears_turn_and_preserves_successor(self):
        self.update({'in_turn':True});self.update({'active':False})
        self.assertFalse(self.c.entity('l')['in_turn']);self.assertNotIn('l',self.c.STATE['battle_order'])
        self.assertEqual(self.c.advance_turn()['id'],'m')
    def test_visible_toggles_without_changing_actor(self):
        self.update({'visible':False});self.assertFalse(self.c.entity('l')['visible']);self.assertEqual(self.c.active_combatant()['id'],'c')
        self.update({'visible':True});self.assertTrue(self.c.entity('l')['visible'])
    def test_invalid_turn_types_atomic(self):
        for value in (None,'true',1,[],{}):
            before=copy.deepcopy(self.c.STATE)
            with self.assertRaises(HTTPError):self.update({'in_turn':value})
            self.assertEqual(self.c.STATE,before)
    def test_turn_does_not_change_initiative_or_round(self):
        self.update({'in_turn':True});self.assertEqual(self.c.entity('l')['initiative'],20);self.assertEqual(self.c.STATE['battle_round'],1)
    def test_join_inserts_at_twenty(self):
        self.update({'active':False});self.update({'active':True});self.assertEqual(self.c.STATE['battle_order'],['c','l','m'])
    def test_fixed_initiative_still_rejected(self):
        with self.assertRaises(HTTPError):self.update({'initiative':25})

if __name__=='__main__':unittest.main()
