"""Lair regression tests against real SQLite and transaction wrappers."""
import ast
import asyncio
import copy
import importlib
import sqlite3
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import test_encounter_features as feature_tests
from test_sqlite_storage import HTTPError
from python.scrying_glass_service_lairs import LairService
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_lair_rules import normalize_lairs
from python.scrying_glass_storage import SQLiteStorage

class LairTests(unittest.TestCase):
    def setUp(self):
        feature_tests.FeatureTests.setUp(self)
        from datetime import datetime, timezone
        self.c.datetime=datetime;self.c.timezone=timezone
        self.service=LairService(self.c)
        path=Path(__file__).resolve().parents[1]/'python/scrying_glass_service_activity.py'
        tree=ast.parse(path.read_text());cls=next(x for x in tree.body if isinstance(x,ast.ClassDef))
        scope={};future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),'activity','exec'),scope)
        self.c.log_battle_action=scope['ActivityService'](self.c).log_battle_action
        self.c.STATE['characters'][0]['initiative']=20
        self.c.STATE['monsters'][0]['initiative']=19
        self.lair=self.call('create_lair',{'name':'Volcano','notes':'Private DM notes'})
        self.ident=self.lair['id']
    tearDown=feature_tests.FeatureTests.tearDown
    def call(self,name,*args):
        owner=self.service if hasattr(self.service,name) else self.f
        return asyncio.run(transactional_handler(self.c,getattr(owner,name))(*args))
    def actor(self):
        self.c.begin_battle(['c','m']);self.c.set_turn(self.c.entity(self.ident),True)
    def action(self,rows,**kwargs):
        return self.call('apply_lair_action',self.ident,{'name':'Tremor','revision':self.f.store.revision(),'targets':rows,**kwargs})
    def test_no_combat_stats(self):
        self.assertFalse(set(self.lair)&{'hp','max_hp','ac','alive','life_state','effects'})
        self.assertNotIn(self.ident,[x['id'] for x in self.c.entities()])
        self.assertEqual(self.lair['initiative'],20)
    def test_single_lair(self):
        with self.assertRaises(HTTPError):self.call('create_lair',{'name':'Second'})
    def test_fixed_initiative_api(self):
        with self.assertRaises(HTTPError):self.call('update_lair',self.ident,{'initiative':21})
    def test_load_enforces_twenty(self):
        self.assertEqual(normalize_lairs([{**self.lair,'initiative':3}])[0]['initiative'],20)
    def test_bad_stats_rejected(self):
        with self.assertRaises(ValueError):normalize_lairs([{**self.lair,'hp':10}])
    def test_start_loses_ties(self):
        self.c.begin_battle(['m',self.ident,'c'])
        self.assertEqual(self.c.STATE['battle_order'],['c',self.ident,'m'])
    def test_creature_tie_choices_preserved(self):
        other=copy.deepcopy(self.c.entity('c'));other.update(id='d',name='Other')
        self.c.STATE['characters'].append(other)
        self.c.begin_battle(['d','c','m'])
        self.assertEqual(self.c.STATE['battle_order'],['d','c',self.ident,'m'])
    def test_next_and_round_wrap(self):
        self.c.begin_battle(['c','m'])
        self.assertEqual(self.c.advance_turn()['id'],self.ident)
        self.assertEqual(self.c.advance_turn()['id'],'m')
        self.assertEqual(self.c.advance_turn()['id'],'c')
        self.assertEqual(self.c.STATE['battle_round'],2)
    def test_new_twenty_before_lair(self):
        self.c.begin_battle(['c','m'])
        other=copy.deepcopy(self.c.entity('m'));other.update(id='n',initiative=20,in_turn=False)
        self.c.STATE['monsters'].append(other);self.c.insert_into_battle_order(other)
        self.assertEqual(self.c.STATE['battle_order'],['c','n',self.ident,'m'])
    def test_missing_lair_reinserted(self):
        self.c.begin_battle(['c','m']);self.c.STATE['battle_order'].remove(self.ident)
        self.assertEqual(self.c.advance_turn()['id'],self.ident)
    def test_initiative_edit_reorders_stably(self):
        self.c.begin_battle(['c','m']);self.c.entity('m')['initiative']=20;self.c.clean_order()
        self.assertEqual(self.c.STATE['battle_order'],['c','m',self.ident])
        self.assertTrue(self.c.entity('c')['in_turn'])
    def test_disabled_current_successor(self):
        self.actor();self.call('update_lair',self.ident,{'active':False})
        self.assertEqual(self.c.advance_turn()['id'],'m')
        self.assertNotIn(self.ident,self.c.STATE['battle_order'])
    def test_deleted_current_successor(self):
        self.actor();self.call('delete_lair',self.ident)
        self.assertEqual(self.c.advance_turn()['id'],'m')
    def test_enable_midbattle(self):
        self.call('update_lair',self.ident,{'active':False});self.c.begin_battle(['c','m'])
        self.call('update_lair',self.ident,{'active':True})
        self.assertEqual(self.c.STATE['battle_order'],['c',self.ident,'m'])
    def test_mixed_targets_damage_conditions(self):
        self.actor();self.c.entity('m')['ally']=True
        self.action([{'id':'c','damage':4,'effects':[{'name':'Prone','public':True}]},
            {'id':'m','damage':6,'effects':[{'name':'Frightened'}]}])
        self.assertEqual(self.c.entity('c')['hp'],16);self.assertEqual(self.c.entity('m')['hp'],6)
        self.assertEqual(self.c.entity('c')['effects'][0]['source_id'],self.ident)
        self.assertEqual(self.c.entity('m')['effects'][0]['name'],'Frightened')
    def test_temporary_hp(self):
        self.actor();self.c.entity('c')['temp_hp']=3;self.action([{'id':'c','damage':5}])
        self.assertEqual((self.c.entity('c')['hp'],self.c.entity('c')['temp_hp']),(18,0))
    def test_zero_hp_death_saves(self):
        self.actor();self.c.entity('c').update(hp=0,life_state='down',alive=False)
        self.action([{'id':'c','damage':1}]);self.assertEqual(self.c.entity('c')['death_failures'],1)
        self.assertIn('c',self.c.STATE['battle_order'])
    def test_monster_death_removed(self):
        self.actor();self.action([{'id':'m','damage':12}]);self.assertEqual(self.c.entity('m')['life_state'],'dead')
        self.assertNotIn('m',self.c.STATE['battle_order'])
    def test_instant_death(self):
        self.actor();self.action([{'id':'c','damage':40}]);self.assertEqual(self.c.entity('c')['life_state'],'dead')
    def test_condition_only(self):
        self.actor();self.action([{'id':'c','effects':[{'name':'Prone'}]}]);self.assertEqual(self.c.entity('c')['hp'],20)
    def test_not_current_rejected(self):
        before=copy.deepcopy(self.c.STATE)
        with self.assertRaises(HTTPError):self.action([{'id':'c','damage':1}])
        self.assertEqual(self.c.STATE,before)
    def test_stale_revision_rejected(self):
        self.actor()
        with self.assertRaises(HTTPError):self.action([{'id':'c','damage':1}],revision=-1)
    def test_batch_validation_atomic(self):
        self.actor();before=copy.deepcopy(self.c.STATE);revision=self.f.store.revision()
        with self.assertRaises(HTTPError):self.action([{'id':'c','damage':1},{'id':'missing','damage':2}])
        self.assertEqual(self.c.STATE,before);self.assertEqual(self.f.store.revision(),revision)
    def test_invalid_rows_atomic(self):
        self.actor();before=copy.deepcopy(self.c.STATE)
        rows=[{'id':self.ident,'damage':1},{'id':'c','damage':True},{'id':'c','damage':-1},
            {'id':'c','damage':1.5},{'id':'c','damage':0},{'id':'c','effects':[{'name':''}]},
            {'id':'c','effects':[{'name':'Prone','public':'yes'}]}]
        for row in rows:
            with self.assertRaises(HTTPError):self.action([row])
            self.assertEqual(self.c.STATE,before)
    def test_duplicate_target_rejected(self):
        self.actor()
        with self.assertRaises(HTTPError):self.action([{'id':'c','damage':1},{'id':'c','damage':1}])
    def test_hp_feature_target_rejected(self):
        for method,args in [('edit_features',(self.ident,{'hp_delta':-1})),('add_effect',(self.ident,{'name':'Prone'})),('end_concentration',(self.ident,))]:
            with self.assertRaises(HTTPError):self.call(method,*args)
    def test_reset_endpoint_rejected(self):
        tree=ast.parse((Path(__file__).resolve().parents[1]/'python/scrying_glass_admin_combatants.py').read_text())
        cls=next(x for x in tree.body if isinstance(x,ast.ClassDef))
        scope={};future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),'reset','exec'),scope)
        handler=scope['AdminCombatantsMixin']();handler.context=self.c
        before=copy.deepcopy(self.c.STATE)
        with self.assertRaises(HTTPError):asyncio.run(handler.reset_one_combatant(self.ident))
        self.assertEqual(self.c.STATE,before)
    def test_expiry_next_lair_turn(self):
        self.actor();self.action([{'id':'c','effects':[{'name':'Prone','timing':'start','anchor_id':self.ident,'turns':1}]}])
        self.f.expire('c','start');self.assertEqual(len(self.c.entity('c')['effects']),1)
        self.f.expire(self.ident,'start');self.assertEqual(self.c.entity('c')['effects'],[])
    def test_delete_anchor_becomes_manual(self):
        self.actor();self.action([{'id':'c','effects':[{'name':'Prone','timing':'start','anchor_id':self.ident,'turns':1}]}])
        self.call('delete_lair',self.ident);effect=self.c.entity('c')['effects'][0]
        self.assertEqual((effect['timing'],effect['turns'],effect['source_id']),('manual',None,None))
    def test_player_safe_display(self):
        self.actor();self.action([{'id':'c','effects':[{'name':'Private'},{'name':'Public','public':True}]}])
        display=self.c.display_state();self.assertEqual(display['lairs'][0]['id'],self.ident)
        self.assertNotIn('Private DM notes',str(display));self.assertNotIn('Private',str(display))
        self.assertEqual(display['characters'][0]['effects'],[{'name':'Public'}])
        self.assertNotIn('hp',display['lairs'][0])
    def test_hidden_lair(self):
        self.call('update_lair',self.ident,{'visible':False});display=self.c.display_state()
        self.assertEqual(display['lairs'],[]);self.assertNotIn(self.ident,display['display_order'])
    def test_restart_during_lair_turn(self):
        self.actor();self.c.save_active_campaign_characters();self.c.save_active_setup_monsters();self.c.save_state()
        path=self.c.STORAGE.path;self.c.STORAGE.close();self.c.STORAGE=SQLiteStorage(path);self.c.load_state()
        self.assertEqual(self.c.active_combatant()['id'],self.ident)
        self.assertEqual(self.c.STATE['battle_order'],['c',self.ident,'m'])
    def test_setup_load_clears_turn(self):
        self.actor();self.c.save_active_setup_monsters()
        state=self.c.load_setup_state('default',self.c.active_campaign())
        self.assertFalse(state['lairs'][0]['in_turn']);self.assertEqual(state['battle_round'],0)
    def test_undo_complete_action(self):
        self.actor();self.action([{'id':'c','damage':4,'effects':[{'name':'Prone'}]}])
        self.call('undo',{'id':self.f.summary()['undo']['id']})
        self.assertEqual(self.c.entity('c')['hp'],20);self.assertEqual(self.c.entity('c')['effects'],[])
        self.assertTrue(self.c.entity(self.ident)['in_turn'])
    def test_undo_lair_delete(self):
        self.actor();self.call('delete_lair',self.ident)
        self.call('undo',{'id':self.f.summary()['undo']['id']});self.assertEqual(self.c.active_combatant()['id'],self.ident)
    def test_bundle_roundtrip(self):
        self.actor();self.c.save_active_setup_monsters();raw=self.f.export_bundle();result=self.call('import_bundle',raw)
        imported=self.c.STORAGE.load_setup(result['campaign_id'],'default')
        self.assertEqual(imported['lairs'][0]['name'],'Volcano')
    def test_schema_v5_upgrade_and_backup(self):
        path=Path(self.tmp.name)/'upgrade.sqlite3';db=SQLiteStorage(path)
        db.connection.execute('DROP TABLE lairs');db.connection.execute('PRAGMA user_version=5');db.close()
        db=SQLiteStorage(path)
        try:
            self.assertEqual(db.connection.execute('PRAGMA user_version').fetchone()[0],6)
            self.assertTrue(db.migration_backup.is_file())
            with sqlite3.connect(db.migration_backup) as backup:self.assertEqual(backup.execute('PRAGMA user_version').fetchone()[0],5)
            self.assertEqual(list(db.connection.execute('PRAGMA foreign_key_check')),[])
        finally:db.close()
    def test_route_registration_guards(self):
        import sys
        captured=[]
        fake=types.ModuleType('fastapi')
        fake.Body=lambda value:value
        fake.Depends=lambda dependency:dependency
        fake.Request=object;fake.HTTPException=HTTPError
        context=types.SimpleNamespace(STATE={},ADMIN_SESSION_COOKIE='admin-cookie',require=lambda role,cookie:('guard',role,cookie))
        app=types.SimpleNamespace(add_api_route=lambda path,handler,**kwargs:captured.append((path,handler,kwargs)))
        with patch.dict(sys.modules,{'fastapi':fake}):
            from python.scrying_glass_api_lairs import install_lair_routes
            install_lair_routes(context,app)
        self.assertEqual(len(captured),4)
        self.assertEqual([row[2]['methods'] for row in captured],[['POST'],['PATCH'],['DELETE'],['POST']])
        for path,handler,options in captured:
            self.assertEqual(options['dependencies'][0],('guard','admin','admin-cookie'))
            self.assertEqual(options['dependencies'][1].__name__,'same_origin')
            self.assertIn('_operation_request',__import__('inspect').signature(handler).parameters)
    def test_ordinary_battle_action_rejects_lair_target(self):
        from python.scrying_glass_feature_rules import apply_hp
        from python.scrying_glass_turn_rules import permanently_dead,can_take_turn
        tree=ast.parse((Path(__file__).resolve().parents[1]/'python/scrying_glass_admin_battle.py').read_text())
        cls=next(x for x in tree.body if isinstance(x,ast.ClassDef))
        scope={'apply_hp':apply_hp,'permanently_dead':permanently_dead,'can_take_turn':can_take_turn}
        future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),'battle-admin','exec'),scope)
        handler=scope['AdminBattleMixin']();handler.context=self.c
        self.c.begin_battle(['c','m'])
        payload=types.SimpleNamespace(actor_id='c',actions=[types.SimpleNamespace(target_id=self.ident,action='damage',amount=1)])
        before=copy.deepcopy(self.c.STATE)
        with self.assertRaises(HTTPError):asyncio.run(handler.apply_battle_actions(payload))
        self.assertEqual(self.c.STATE,before)
    def test_condition_target_end_expiry(self):
        self.actor();self.action([{'id':'c','effects':[{'name':'Prone','timing':'end','anchor_id':'c','turns':1}]}])
        self.f.expire(self.ident,'end');self.assertEqual(len(self.c.entity('c')['effects']),1)
        self.f.expire('c','end');self.assertEqual(self.c.entity('c')['effects'],[])
    def test_dead_or_inactive_targets_rejected(self):
        self.actor()
        for fields in ({'active':False},{'life_state':'dead','hp':0,'alive':False}):
            self.c.entity('m').update(fields)
            with self.assertRaises(HTTPError):self.action([{'id':'m','damage':1}])

    def test_record_id_stable(self):
        ident=self.c.STORAGE.connection.execute('SELECT id FROM lairs WHERE name=?',('Volcano',)).fetchone()[0]
        self.call('update_lair',self.ident,{'notes':'Edited'})
        self.assertEqual(self.c.STORAGE.connection.execute('SELECT id FROM lairs WHERE name=?',('Volcano',)).fetchone()[0],ident)

if __name__=='__main__':unittest.main()
