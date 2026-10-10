"""Single-row lair damage logging using real HP and activity-log functions."""
import ast
import asyncio
import copy
import uuid
import unittest
from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from python.scrying_glass_feature_rules import apply_hp,validate_effects,normalize_features
from python.scrying_glass_turn_rules import permanently_dead

class HTTPError(Exception):
    def __init__(self,status_code,detail):self.status_code=status_code;self.detail=detail

def load_class(filename,class_name,scope):
    tree=ast.parse((Path(__file__).resolve().parents[1]/'python'/filename).read_text())
    cls=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==class_name)
    future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),filename,'exec'),scope)
    return scope[class_name]

class LoggingTests(unittest.TestCase):
    def setUp(self):
        self.c=SimpleNamespace(HTTPException=HTTPError,uuid=uuid,datetime=datetime,timezone=timezone)
        self.target=normalize_features({'id':'c','name':'Hero','hp':24,'max_hp':24,'active':True,'visible':True})
        self.lair={'id':'l','name':'Lair','kind':'lair','active':True,'in_turn':True,'initiative':20}
        self.c.STATE={'lairs':[self.lair],'characters':[self.target],'monsters':[],'activity_log':[]}
        self.c.entities=lambda:self.c.STATE['characters']+self.c.STATE['monsters']
        self.c.entity=lambda ident:next((x for x in [self.lair]+self.c.entities() if x['id']==ident),None)
        self.c.combatant_state=lambda item:item.get('life_state','unknown')
        self.c.remember_turn_successors=lambda:None;self.c.clean_order=lambda:None
        async def persist(**kwargs):pass
        self.c.combatants_changed=persist
        def feature_log(action,target=None,amount=None,note=''):
            self.c.STATE['activity_log'].append({'action':action,'amount':amount,'note':note,'target_combatant_id':target['id'] if target else None})
        self.c.features=SimpleNamespace(store=SimpleNamespace(revision=lambda:3),log=feature_log)
        activity=load_class('scrying_glass_service_activity.py','ActivityService',{})(self.c)
        self.c.log_battle_action=activity.log_battle_action
        scope={'copy':copy,'uuid':uuid,'apply_hp':apply_hp,'validate_effects':validate_effects,'permanently_dead':permanently_dead}
        self.service=load_class('scrying_glass_service_lairs.py','LairService',scope)(self.c)
    def apply(self,rows,name='Tremor'):
        return asyncio.run(self.service.apply_lair_action('l',{'revision':3,'name':name,'targets':rows}))
    def damage_rows(self):return [x for x in self.c.STATE['activity_log'] if x['action']=='damage']
    def test_twelve_damage_is_logged_and_applied_once(self):
        self.apply([{'id':'c','damage':12}]);self.assertEqual(self.target['hp'],12)
        self.assertEqual(len(self.c.STATE['activity_log']),1)
        self.assertEqual(self.damage_rows()[0]['amount'],12);self.assertEqual(self.damage_rows()[0]['note'],'Tremor')
        self.assertEqual(self.damage_rows()[0]['active_combatant_id'],'l')
        self.assertFalse(any(x['action']=='lair-action' for x in self.c.STATE['activity_log']))
    def test_multi_target_one_damage_row_each(self):
        monster=normalize_features({'id':'m','name':'Goblin','monster_species':'Goblin','hp':20,'max_hp':20,'active':True})
        self.c.STATE['monsters'].append(monster)
        self.apply([{'id':'c','damage':12},{'id':'m','damage':6}])
        self.assertEqual([(x['target_combatant_id'],x['amount']) for x in self.damage_rows()],[('c',12),('m',6)])
        self.assertEqual((self.target['hp'],monster['hp']),(12,14))
    def test_condition_has_separate_non_damage_row(self):
        self.apply([{'id':'c','damage':12,'effects':[{'name':'Prone'}]}])
        self.assertEqual(len(self.damage_rows()),1)
        effect=next(x for x in self.c.STATE['activity_log'] if x['action']=='effect-added')
        self.assertIsNone(effect['amount']);self.assertEqual(effect['note'],'Tremor: Prone')
    def test_condition_only_no_damage_row(self):
        self.apply([{'id':'c','effects':[{'name':'Prone'}]}]);self.assertEqual(self.damage_rows(),[]);self.assertEqual(self.target['hp'],24)
    def test_concentration_reminder_not_duplicate_damage(self):
        self.target['concentrating']=True;self.apply([{'id':'c','damage':12}])
        self.assertEqual(len(self.damage_rows()),1)
        reminder=next(x for x in self.c.STATE['activity_log'] if x['action']=='concentration-reminder')
        self.assertIsNone(reminder['amount'])
    def test_temporary_hp_still_absorbs_damage_once(self):
        self.target['temp_hp']=5;self.apply([{'id':'c','damage':12}])
        self.assertEqual((self.target['hp'],self.target['temp_hp']),(17,0));self.assertEqual(len(self.damage_rows()),1)
    def test_invalid_batch_leaves_hp_and_log_unchanged(self):
        before=copy.deepcopy(self.c.STATE)
        with self.assertRaises(HTTPError):self.apply([{'id':'c','damage':12},{'id':'missing','damage':12}])
        self.assertEqual(self.c.STATE,before)
    def test_previous_log_entries_are_not_rewritten(self):
        self.c.STATE['activity_log'].append({'action':'lair-action','amount':12,'note':'Historical'})
        self.apply([{'id':'c','damage':12}]);self.assertEqual(self.c.STATE['activity_log'][0]['note'],'Historical')
        self.assertEqual(len(self.damage_rows()),1)

if __name__=='__main__':unittest.main()
