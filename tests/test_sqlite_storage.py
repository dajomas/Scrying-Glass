"""Run with python -m unittest discover -s tests -v; no web dependencies needed."""
import asyncio
import copy
import json
import re
import sqlite3
import tempfile
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from python.scrying_glass_storage import SQLiteStorage
from python.scrying_glass_service_state import StateService
from python.scrying_glass_service_campaigns import CampaignsService
from python.scrying_glass_service_persistence import PersistenceService
from python.scrying_glass_service_migrations import MigrationsService
from python.scrying_glass_service_notifications import NotificationsService
from python.scrying_glass_admin_campaigns import AdminCampaignsMixin
from python.scrying_glass_admin_setups import AdminSetupsMixin
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_combatant import setup_snapshot, reset_imported_monster, admin_initiative_key

class HTTPError(Exception):
    def __init__(self, status_code, detail):
        self.status_code, self.detail = status_code, detail
        super().__init__(detail)

def slug(value):
    result=re.sub('[^a-z0-9]+','-',value.strip().lower()).strip('-')
    if not result: raise HTTPError(400,'Invalid slug')
    return result[:80]

def context(directory):
    c=SimpleNamespace(DATA_DIR=directory, STORAGE=SQLiteStorage(directory/'scrying-glass.sqlite3'), CONFIG={'display':{'background':'#080b14','entry_direction':'left','exit_direction':'right','monster_width_percent':20}}, STATE={}, DEFAULT_SETUP_NAME='default', DEFAULT_CAMPAIGN_SLUG='default', DEFAULT_CAMPAIGN_NAME='Default', DEFAULT_VIEW_BACKGROUND='#080b14', HTTPException=HTTPError, json=json, uuid=uuid, copy=copy, setup_slug=slug, campaign_slug=slug, now_iso=lambda:'2026-10-09T00:00:00+00:00', setup_snapshot=setup_snapshot, reset_imported_monster=reset_imported_monster, admin_initiative_key=admin_initiative_key, LOCK=asyncio.Lock(), SOCKETS=set())
    for cls in (StateService,CampaignsService,PersistenceService,MigrationsService,NotificationsService):
        service=cls(c)
        for name in vars(cls):
            if not name.startswith('_') and callable(getattr(service,name,None)):
                setattr(c,name,getattr(service,name))
    return c

class Handlers(AdminCampaignsMixin,AdminSetupsMixin):
    def __init__(self,c): self.context=c

class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.directory=Path(self.temp.name)
        self.c=context(self.directory)
        self.handlers=Handlers(self.c)
    def tearDown(self):
        self.c.STORAGE.close()
        self.temp.cleanup()
    def initialize(self): self.c.import_legacy_storage()
    def call(self,handler_name,**kwargs):
        return asyncio.run(transactional_handler(self.c,getattr(self.handlers,handler_name))(**kwargs))
    def payload(self,**kwargs): return SimpleNamespace(**kwargs)
    def test_fresh_database_and_idempotent_import(self):
        self.initialize()
        self.assertEqual(self.c.list_setups(),['default'])
        self.assertEqual(self.c.import_legacy_storage()['campaigns'],0)
        self.assertFalse((self.directory/'state.json').exists())
    def test_transaction_rollback(self):
        self.initialize()
        with self.assertRaises(ValueError):
            with self.c.STORAGE.transaction():
                self.c.STORAGE.set_value('example',1)
                raise ValueError('failure')
        self.assertIsNone(self.c.STORAGE.get_value('example'))
    def test_nested_transaction_rollback(self):
        with self.assertRaises(ValueError):
            with self.c.STORAGE.transaction():
                with self.c.STORAGE.transaction():
                    self.c.STORAGE.set_value('example',1)
                raise ValueError()
        self.assertIsNone(self.c.STORAGE.get_value('example'))
    def test_campaign_create_rename_and_fk_cascade(self):
        self.initialize()
        self.call('create_campaign',payload=self.payload(name='Second',description='test',activate=True))
        self.call('update_campaign',slug='second',payload=self.payload(name='Renamed',description=None))
        self.assertEqual(self.c.active_campaign(),'renamed')
        self.assertEqual(self.c.STATE['active_setup']['campaign'],'renamed')
        self.assertEqual(self.c.STORAGE.list_setups('renamed'),['default'])
        self.assertEqual(self.c.STORAGE.load_characters('renamed'),[])
        self.c.load_state()
        self.assertEqual(self.c.STATE['active_setup']['campaign'],'renamed')
    def test_setup_save_rename_restart_delete(self):
        self.initialize()
        self.c.STATE=self.c.normalize_state({'monsters':[{'id':'m','hp':8,'active':True,'in_turn':True}], 'battle_round':3,'battle_order':['m'],'turn_successors':['m'],'turn_successors_before_wrap':['m'],'display':{'battle_order_font_size':22}})
        self.call('save_setup',payload=self.payload(name='Encounter',campaign=None))
        self.call('rename_setup',payload=self.payload(name='encounter',new_name='Renamed',campaign=None))
        self.c.STATE={}
        self.c.load_state()
        self.assertEqual(self.c.STATE['battle_round'],3)
        self.assertEqual(self.c.STATE['display']['battle_order_font_size'],22)
        self.assertTrue(self.c.STATE['monsters'][0]['in_turn'])
        self.assertEqual(self.c.STATE['turn_successors_before_wrap'],['m'])
        loaded=self.c.load_setup_state('renamed','default')
        self.assertEqual(loaded['battle_round'],0)
        self.assertFalse(loaded['monsters'][0]['in_turn'])
        result=self.call('delete_setup',name='renamed',campaign=None)
        self.assertEqual(result['opened_setup'],'default')
    def test_delete_last_setup_creates_default(self):
        self.initialize()
        result=self.call('delete_setup',name='default',campaign=None)
        self.assertTrue(result['created_default'])
    def test_copy_and_move_loaded_setup(self):
        self.initialize()
        self.call('load_setup',payload=self.payload(name='default',campaign=None))
        self.call('create_campaign',payload=self.payload(name='Second',description='',activate=False))
        result=self.call('add_setup_to_campaign',slug='second',payload=self.payload(from_campaign='default',setup='default',mode='copy'))
        self.assertEqual(result['setup'],'default-2')
        result=self.call('add_setup_to_campaign',slug='second',payload=self.payload(from_campaign='default',setup='default',mode='move'))
        self.assertEqual(result['setup'],'default-3')
        self.assertIsNone(self.c.STATE['active_setup'])
        self.assertFalse(self.c.STORAGE.setup_exists('default','default'))
    def test_campaign_delete_and_last_campaign_guard(self):
        self.initialize()
        self.call('create_campaign',payload=self.payload(name='Second',description='',activate=True))
        self.call('delete_campaign',slug='second',move_to='default')
        self.assertEqual(self.c.active_campaign(),'default')
        self.assertEqual(self.c.list_setups(),['default','default-2'])
        with self.assertRaises(HTTPError): self.call('delete_campaign',slug='default',delete_setups=True)
    def test_handler_rollback_restores_state_and_database(self):
        self.initialize()
        original=copy.deepcopy(self.c.STATE)
        async def broken():
            self.c.STATE['battle_round']=99
            self.c.STORAGE.set_value('broken',True)
            raise ValueError('failed')
        with self.assertRaises(ValueError): asyncio.run(transactional_handler(self.c,broken)())
        self.assertEqual(self.c.STATE,original)
        self.assertIsNone(self.c.STORAGE.get_value('broken'))
    def test_broadcast_after_commit(self):
        self.initialize()
        events=[]
        async def broadcast(): events.append(self.c.STORAGE.connection.in_transaction)
        async def handler():
            await self.c.changed()
        original=self.c.broadcast
        async def deferred():
            if getattr(self.c,'_defer_database_broadcast',False):
                self.c._database_broadcast_pending=True
            else: await broadcast()
        self.c.broadcast=deferred
        asyncio.run(transactional_handler(self.c,handler)())
        self.assertEqual(events,[False])
        self.c.broadcast=original
    def test_unsaved_encounter_and_campaign_roster_restart(self):
        self.initialize()
        self.c.STATE=self.c.normalize_state({'monsters':[{'id':'m','hp':5}], 'characters':[{'id':'c','hp':12}]})
        asyncio.run(self.c.combatants_changed(monsters=True,characters=True))
        self.c.STATE={}
        self.c.load_state()
        self.assertEqual(self.c.STATE['monsters'][0]['hp'],5)
        self.assertEqual(self.c.STATE['characters'][0]['hp'],12)
        self.assertEqual(self.c.STORAGE.get_value('runtime_state')['characters'],[])
    def test_legacy_import_preserves_files_and_mtime(self):
        (self.directory/'setups'/'old').mkdir(parents=True)
        setup=self.directory/'setups'/'old'/'encounter.json'
        setup.write_text(json.dumps({'monsters':[{'id':'m','hp':10,'active':True,'in_turn':True}], 'characters':[{'id':'c','hp':12}]}))
        registry=self.directory/'campaigns.json'
        registry.write_text(json.dumps({'active':'old','campaigns':{'old':{'last_setup':'encounter'}}}))
        state=self.directory/'state.json'
        state.write_text(json.dumps({'active_setup':{'campaign':'old','name':'encounter'},'monsters':[],'active_turn_id':'m','battle_round':4}))
        before={p:p.read_bytes() for p in (setup,registry,state)}
        self.initialize()
        self.assertEqual(self.c.STATE['battle_round'],4)
        self.assertTrue(self.c.STATE['monsters'][0]['in_turn'])
        self.assertEqual(self.c.STATE['characters'][0]['id'],'c')
        stored=self.c.STORAGE.connection.execute('SELECT updated_at FROM battle_setups WHERE name=?',('encounter',)).fetchone()[0]
        self.assertEqual(stored,setup.stat().st_mtime)
        self.assertEqual(before,{p:p.read_bytes() for p in before})
    def test_corrupt_import_rolls_back_and_can_retry(self):
        (self.directory/'setups').mkdir()
        path=self.directory/'setups'/'broken.json';path.write_text('{')
        with self.assertRaises(RuntimeError): self.initialize()
        self.assertEqual(self.c.STORAGE.read_campaigns()['campaigns'],{})
        self.assertIsNone(self.c.STORAGE.get_value('legacy_import_complete'))
        path.write_text('{}');self.initialize()
        self.assertIn('broken',self.c.list_setups())
    def test_missing_runtime_reference_aborts_import(self):
        (self.directory/'state.json').write_text(json.dumps({'active_setup':{'campaign':'default','name':'missing'}}))
        with self.assertRaises(RuntimeError): self.initialize()
        self.assertEqual(self.c.STORAGE.read_campaigns()['campaigns'],{})
    def test_schema_version_guard(self):
        p=self.directory/'future.sqlite3'
        conn=sqlite3.connect(p);conn.execute('PRAGMA user_version=99');conn.close()
        with self.assertRaises(RuntimeError): SQLiteStorage(p)

    def test_database_reopen_restores_round_and_turn(self):
        self.initialize()
        self.c.STATE=self.c.normalize_state({'monsters':[{'id':'m','hp':7,'active':True,'in_turn':True}],'battle_round':6})
        self.call('save_setup',payload=self.payload(name='Fight',campaign=None))
        self.c.STORAGE.close()
        self.c=context(self.directory);self.handlers=Handlers(self.c)
        self.c.load_state()
        self.assertEqual(self.c.STATE['battle_round'],6)
        self.assertTrue(self.c.STATE['monsters'][0]['in_turn'])
    def test_roster_is_shared_between_setups(self):
        self.initialize()
        self.c.STATE=self.c.normalize_state({'characters':[{'id':'c','hp':10}]})
        self.call('save_setup',payload=self.payload(name='One',campaign=None))
        self.c.STATE['characters'][0]['hp']=4
        self.call('save_setup',payload=self.payload(name='Two',campaign=None))
        self.call('load_setup',payload=self.payload(name='one',campaign=None))
        self.assertEqual(self.c.STATE['characters'][0]['hp'],4)
    def test_delete_rolls_back_when_next_setup_invalid(self):
        self.initialize()
        self.call('save_setup',payload=self.payload(name='a',campaign=None))
        self.c.STORAGE.save_setup('default','b',{'monsters':'invalid'})
        with self.assertRaises(HTTPError): self.call('delete_setup',name='a',campaign=None)
        self.assertTrue(self.c.STORAGE.setup_exists('default','a'))
        self.assertEqual(self.c.STATE['active_setup']['name'],'a')
    def test_conflicting_rename_rolls_back(self):
        self.initialize()
        self.call('save_setup',payload=self.payload(name='fight',campaign=None))
        with self.assertRaises(HTTPError):
            self.call('rename_setup',payload=self.payload(name='fight',new_name='default',campaign=None))
        self.assertTrue(self.c.STORAGE.setup_exists('default','fight'))
    def test_loose_setup_collision_and_explicit_roster(self):
        (self.directory/'setups'/'default').mkdir(parents=True)
        (self.directory/'characters').mkdir()
        (self.directory/'setups'/'default'/'fight.json').write_text(json.dumps({'characters':[{'id':'legacy','hp':5}]}))
        (self.directory/'setups'/'fight.json').write_text('{}')
        (self.directory/'characters'/'default.json').write_text(json.dumps({'characters':[{'id':'roster','hp':8}]}))
        self.initialize()
        self.assertEqual(self.c.list_setups(),['fight','fight-2'])
        self.assertEqual(self.c.STATE['characters'][0]['id'],'roster')
    def test_last_setup_wins_over_mtime(self):
        self.initialize()
        self.c.STORAGE.save_setup('default','older',{},1)
        self.c.STORAGE.save_setup('default','newer',{},2)
        data=self.c.read_campaigns();data['campaigns']['default']['last_setup']='older';self.c.write_campaigns(data)
        self.assertEqual(self.c.pick_campaign_setup('default'),'older')
        data['campaigns']['default']['last_setup']='missing';self.c.write_campaigns(data)
        self.c.STORAGE.delete_setup('default','default')
        self.assertEqual(self.c.pick_campaign_setup('default'),'newer')
    def test_cancelled_handler_rolls_back(self):
        self.initialize()
        original=copy.deepcopy(self.c.STATE)
        async def cancelled():
            self.c.STORAGE.set_value('cancelled',True)
            self.c.STATE['battle_round']=7
            raise asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError): asyncio.run(transactional_handler(self.c,cancelled)())
        self.assertIsNone(self.c.STORAGE.get_value('cancelled'))
        self.assertEqual(self.c.STATE,original)
    def test_foreign_keys_enforced(self):
        with self.assertRaises(sqlite3.IntegrityError): self.c.STORAGE.save_characters('missing',[])

    def test_legacy_turn_without_marker(self):
        (self.directory/'setups'/'default').mkdir(parents=True)
        (self.directory/'setups'/'default'/'fight.json').write_text(json.dumps({'monsters':[{'id':'m','hp':8,'active':True,'in_turn':True}]}))
        (self.directory/'state.json').write_text(json.dumps({'active_setup':{'campaign':'default','name':'fight'},'monsters':[]}))
        self.initialize()
        self.assertTrue(self.c.STATE['monsters'][0]['in_turn'])
    def test_mutating_requests_are_serialized(self):
        self.initialize()
        events=[]
        async def first():
            events.append('first-start')
            await asyncio.sleep(0.01)
            self.c.STORAGE.set_value('first',1)
            events.append('first-end')
        async def second():
            events.append('second-start')
            self.assertEqual(self.c.STORAGE.get_value('first'),1)
        async def run():
            await asyncio.gather(transactional_handler(self.c,first)(),transactional_handler(self.c,second)())
        asyncio.run(run())
        self.assertEqual(events,['first-start','first-end','second-start'])

if __name__=='__main__': unittest.main()
