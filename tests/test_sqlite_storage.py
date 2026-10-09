"""Real SQLite migration, relational storage, stability and domain regression tests."""
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
from python.scrying_glass_combatant import setup_snapshot,reset_imported_monster,admin_initiative_key
from contextlib import closing

class HTTPError(Exception):
    def __init__(self,status_code,detail):
        self.status_code,self.detail=status_code,detail
        super().__init__(detail)

def slug(value):
    value=re.sub('[^a-z0-9]+','-',value.strip().lower()).strip('-')
    if not value:raise HTTPError(400,'Invalid slug')
    return value[:80]

def context(directory):
    c=SimpleNamespace(DATA_DIR=directory,STORAGE=SQLiteStorage(directory/'scrying-glass.sqlite3'),CONFIG={'display':{'background':'#080b14','entry_direction':'left','exit_direction':'right','monster_width_percent':20}},STATE={},DEFAULT_SETUP_NAME='default',DEFAULT_CAMPAIGN_SLUG='default',DEFAULT_CAMPAIGN_NAME='Default',DEFAULT_VIEW_BACKGROUND='#080b14',HTTPException=HTTPError,json=json,uuid=uuid,copy=copy,setup_slug=slug,now_iso=lambda:'2026-10-09T00:00:00+00:00',setup_snapshot=setup_snapshot,reset_imported_monster=reset_imported_monster,admin_initiative_key=admin_initiative_key,LOCK=asyncio.Lock(),SOCKETS=set())
    for cls in (StateService,CampaignsService,PersistenceService,MigrationsService,NotificationsService):
        service=cls(c)
        for name in vars(cls):
            if not name.startswith('_') and callable(getattr(service,name,None)):setattr(c,name,getattr(service,name))
    return c
class Handlers(AdminCampaignsMixin,AdminSetupsMixin):
    def __init__(self,c):self.context=c

def old_database(path,version=1,*,bad=False,unsupported=False):
    conn=sqlite3.connect(path)
    if version==1:
        conn.execute('CREATE TABLE campaigns(slug TEXT PRIMARY KEY,metadata_json TEXT NOT NULL)');owner='campaign_slug'
    else:
        conn.execute("CREATE TABLE campaigns(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT NOT NULL,description TEXT NOT NULL,created TEXT NOT NULL,metadata_json TEXT NOT NULL)");owner='campaign_id'
    conn.execute(f'CREATE TABLE campaign_characters({owner} PRIMARY KEY REFERENCES campaigns({"slug" if version==1 else "id"}),characters_json TEXT NOT NULL)')
    conn.execute(f'CREATE TABLE battle_setups({owner} REFERENCES campaigns({"slug" if version==1 else "id"}),name TEXT NOT NULL,snapshot_json TEXT NOT NULL,updated_at REAL NOT NULL,PRIMARY KEY({owner},name))')
    conn.execute('CREATE TABLE application_state(key TEXT PRIMARY KEY,value_json TEXT NOT NULL)')
    meta={'name':'Campaign','description':'keep','created':'before','last_setup':'fight','last_setup_at':'yesterday'}
    ident='old-campaign' if version==1 else 42
    if version==1:conn.execute('INSERT INTO campaigns VALUES (?,?)',(ident,json.dumps(meta)))
    else:conn.execute('INSERT INTO campaigns(id,name,description,created,metadata_json) VALUES (?,?,?,?,?)',(ident,meta['name'],meta['description'],meta['created'],json.dumps({'last_setup':'fight','last_setup_at':'yesterday'})))
    entity={'id':'m','hp':8,'name':'Goblin','active':True,'alive':True,'in_turn':True,'image_url':None}
    log={'id':'event','timestamp':'now','active_combatant_id':'m','target_combatant_id':'c','action':'damage','amount':2}
    snap={'monsters':[entity],'characters':[],'battle_order':['m'],'activity_log':[log],'display':{'background':'#123456','battle_order_font_size':24},'battle_round':4}
    if unsupported:snap['unknown_nested']={'x':[1]}
    conn.execute('INSERT INTO battle_setups VALUES (?,?,?,?)',(ident,'fight','{' if bad else json.dumps(snap),1234.5))
    conn.execute('INSERT INTO campaign_characters VALUES (?,?)',(ident,json.dumps([{'id':'c','hp':12,'name':'Hero','active':True,'alive':True}])))
    ref={'campaign' if version==1 else 'campaign_id':str(ident),'name':'fight'}
    state={**snap,'monsters':[],'active_setup':ref,'active_turn_id':'m','battle_order':['m','c'],'turn_successors':['c'],'turn_successors_before_wrap':['c']}
    for key,value in [('active_campaign',str(ident)),('runtime_state',state),('legacy_import_complete',{'at':'old','counts':{'campaigns':1,'characters':1,'setups':1}})]:conn.execute('INSERT INTO application_state VALUES (?,?)',(key,json.dumps(value)))
    conn.execute(f'PRAGMA user_version={version}');conn.commit();conn.close()
    return snap,state

class DomainTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.directory=Path(self.temp.name);self.c=context(self.directory);self.handlers=Handlers(self.c)
    def tearDown(self):self.c.STORAGE.close();self.temp.cleanup()
    def initialize(self):self.c.import_legacy_storage();return self.c.active_campaign()
    def call(self,handler_name,**kwargs):return asyncio.run(transactional_handler(self.c,getattr(self.handlers,handler_name))(**kwargs))
    def payload(self,**kwargs):return SimpleNamespace(**kwargs)
    def create(self,name='Second',activate=False):return self.call('create_campaign',payload=self.payload(name=name,description='',activate=activate))['created_campaign_id']
    def test_fresh_schema_and_repeat_import(self):
        ident=self.initialize();self.assertTrue(ident.isdecimal());self.assertEqual(self.c.list_setups(),['default']);self.assertEqual(self.c.import_legacy_storage()['campaigns'],0)
    def test_no_json_columns_and_all_lists_have_record_ids(self):
        self.initialize();sql=self.c.STORAGE.connection
        tables=[r[0] for r in sql.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        for name in tables:
            columns=[r[1] for r in sql.execute(f'PRAGMA table_info({name})')]
            self.assertIn('id',columns);self.assertFalse(any('json' in col.lower() for col in columns))
        self.assertNotIn('campaign_characters',tables)
    def test_rename_only_changes_campaign_row(self):
        self.initialize();ident=self.create(activate=True);sql=self.c.STORAGE.connection
        tables=['battle_setups','characters','encounters','application_state','ordered_combatants']
        before={t:[tuple(r) for r in sql.execute(f'SELECT * FROM {t}')] for t in tables}
        self.call('update_campaign',campaign_id=ident,payload=self.payload(name='Renamed',description=None))
        self.assertEqual(before,{t:[tuple(r) for r in sql.execute(f'SELECT * FROM {t}')] for t in tables})
        self.assertEqual(self.c.active_campaign(),ident)
    def test_save_restart_round_turn_font_lists(self):
        ident=self.initialize()
        self.c.STATE=self.c.normalize_state({'monsters':[{'id':'m','hp':8,'active':True,'in_turn':True}],'characters':[{'id':'c','hp':12,'active':True}],'battle_round':5,'battle_order':['m','c'],'turn_successors':['c'],'turn_successors_before_wrap':['c'],'display':{'battle_order_font_size':24},'activity_log':[{'id':'event','action':'damage','amount':2}]})
        self.call('save_setup',payload=self.payload(name='Fight',campaign=None))
        self.c.STORAGE.close();self.c=context(self.directory);self.handlers=Handlers(self.c);self.c.load_state()
        self.assertEqual(self.c.STATE['battle_round'],5);self.assertTrue(self.c.STATE['monsters'][0]['in_turn']);self.assertEqual(self.c.STATE['display']['battle_order_font_size'],24)
        self.assertEqual(self.c.STATE['battle_order'],['m','c']);self.assertEqual(self.c.STATE['turn_successors_before_wrap'],['c']);self.assertEqual(self.c.STATE['activity_log'][0]['id'],'event')
        self.assertEqual(self.c.STATE['active_setup'],{'campaign_id':ident,'name':'fight'})
    def test_entity_and_list_record_ids_survive_updates(self):
        ident=self.initialize();self.c.STATE=self.c.normalize_state({'monsters':[{'id':'m','hp':8},{'id':'n','hp':9}],'battle_order':['m','n'],'activity_log':[{'id':'event','amount':2}]})
        self.call('save_setup',payload=self.payload(name='Fight',campaign=None));sql=self.c.STORAGE.connection
        before=[tuple(r) for r in sql.execute('SELECT id,combatant_id FROM monsters ORDER BY id')]
        order=[tuple(r) for r in sql.execute('SELECT id,combatant_id FROM ordered_combatants ORDER BY id')]
        logs=[tuple(r) for r in sql.execute('SELECT id,event_id FROM activity_log_entries ORDER BY id')]
        self.c.STATE['monsters'][0]['hp']=3;self.c.STATE['battle_order']=['n','m']
        asyncio.run(self.c.combatants_changed(monsters=True))
        self.assertEqual(before,[tuple(r) for r in sql.execute('SELECT id,combatant_id FROM monsters ORDER BY id')])
        self.assertEqual(order,[tuple(r) for r in sql.execute('SELECT id,combatant_id FROM ordered_combatants ORDER BY id')])
        self.assertEqual(logs,[tuple(r) for r in sql.execute('SELECT id,event_id FROM activity_log_entries ORDER BY id')])
    def test_roster_record_ids_survive_hp_change(self):
        ident=self.initialize();db=self.c.STORAGE;db.save_characters(ident,[{'id':'c','hp':8}]);record=db.connection.execute('SELECT id FROM characters').fetchone()[0]
        db.save_characters(ident,[{'id':'c','hp':3}]);self.assertEqual(db.connection.execute('SELECT id FROM characters').fetchone()[0],record)
    def test_scalar_extension_is_typed_not_json(self):
        ident=self.initialize();db=self.c.STORAGE;db.save_characters(ident,[{'id':'c','hp':8,'note':'hello','score':2.5,'flag':True}]);item=db.load_characters(ident)[0]
        self.assertEqual(item['score'],2.5);self.assertIs(item['flag'],True)
        self.assertEqual(db.connection.execute("SELECT value_kind FROM characters_attributes WHERE field_name='note'").fetchone()[0],'text')
    def test_unknown_nested_value_aborts_without_data_loss(self):
        ident=self.initialize();db=self.c.STORAGE;db.save_characters(ident,[{'id':'c','hp':8}])
        with self.assertRaises(ValueError):db.save_characters(ident,[{'id':'c','hp':3,'nested':{'x':[1]}}])
        self.assertEqual(db.load_characters(ident)[0]['hp'],8)
    def test_list_duplicates_and_order_round_trip(self):
        ident=self.initialize();self.c.STORAGE.save_setup(ident,'duplicates',{'battle_order':['a','a','b'],'turn_successors':['b','a']})
        self.assertEqual(self.c.STORAGE.load_setup(ident,'duplicates')['battle_order'],['a','a','b'])
    def test_absent_and_null_fields_preserved(self):
        ident=self.initialize();items=[{'id':'a','hp':8},{'id':'b','hp':9,'initiative':None}];self.c.STORAGE.save_characters(ident,items)
        self.assertEqual(self.c.STORAGE.load_characters(ident),items)
    def test_move_preserves_setup_id_copy_gets_new_id(self):
        source=self.initialize();target=self.create();db=self.c.STORAGE
        original=db.connection.execute('SELECT id FROM battle_setups WHERE campaign_id=?',(source,)).fetchone()[0]
        copy_name=db.transfer_setup(source,target,'default','copy');copy_id=db.connection.execute('SELECT id FROM battle_setups WHERE campaign_id=? AND name=?',(target,copy_name)).fetchone()[0]
        moved=db.transfer_setup(source,target,'default','move');move_id=db.connection.execute('SELECT id FROM battle_setups WHERE campaign_id=? AND name=?',(target,moved)).fetchone()[0]
        self.assertEqual(original,move_id);self.assertNotEqual(original,copy_id)
    def test_setup_rename_active_and_last_reference(self):
        ident=self.initialize();self.call('load_setup',payload=self.payload(name='default',campaign=None));self.call('rename_setup',payload=self.payload(name='default',new_name='renamed',campaign=None))
        self.c.load_state();self.assertEqual(self.c.STATE['active_setup']['name'],'renamed');self.assertEqual(self.c.read_campaigns()['campaigns'][ident]['last_setup'],'renamed')
    def test_delete_active_campaign_and_cascades(self):
        first=self.initialize();second=self.create(activate=True);self.call('delete_campaign',campaign_id=second,move_to=first)
        self.assertEqual(self.c.active_campaign(),first);self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')),[])
    def test_delete_last_setup_recreates_default(self):
        self.initialize();result=self.call('delete_setup',name='default',campaign=None);self.assertTrue(result['created_default'])
    def test_transaction_memory_rollback(self):
        self.initialize();before=copy.deepcopy(self.c.STATE)
        async def broken():self.c.STATE['battle_round']=99;self.c.STORAGE.update_campaign(self.c.active_campaign(),name='Broken');raise ValueError()
        with self.assertRaises(ValueError):asyncio.run(transactional_handler(self.c,broken)())
        self.assertEqual(self.c.STATE,before);self.assertNotEqual(self.c.read_campaigns()['campaigns'][self.c.active_campaign()]['name'],'Broken')
    def test_unsaved_encounter_restart(self):
        self.initialize();self.c.STATE=self.c.normalize_state({'monsters':[{'id':'m','hp':5}],'characters':[{'id':'c','hp':8}]});asyncio.run(self.c.combatants_changed(monsters=True,characters=True));self.c.STATE={};self.c.load_state()
        self.assertEqual(self.c.STATE['monsters'][0]['hp'],5);self.assertEqual(self.c.STATE['characters'][0]['hp'],8)
    def test_original_json_import_and_source_immutability(self):
        (self.directory/'setups'/'old').mkdir(parents=True);p=self.directory/'setups'/'old'/'fight.json'
        p.write_text(json.dumps({'monsters':[{'id':'m','hp':8,'active':True,'in_turn':True}],'characters':[{'id':'c','hp':9}]}))
        (self.directory/'campaigns.json').write_text(json.dumps({'active':'old','campaigns':{'old':{'name':'Old','last_setup':'fight'}}}))
        (self.directory/'state.json').write_text(json.dumps({'active_setup':{'campaign':'old','name':'fight'},'active_turn_id':'m','monsters':[],'battle_round':4}))
        before=p.read_bytes();self.initialize();self.assertEqual(p.read_bytes(),before);self.assertEqual(self.c.STATE['battle_round'],4);self.assertTrue(self.c.STATE['monsters'][0]['in_turn'])
    def test_import_invalid_json_rolls_back(self):
        (self.directory/'setups').mkdir();(self.directory/'setups'/'bad.json').write_text('{')
        with self.assertRaises(RuntimeError):self.initialize()
        self.assertEqual(self.c.read_campaigns()['campaigns'],{})

    def test_cancelled_mutation_rolls_back(self):
        ident=self.initialize()
        async def cancelled():self.c.STORAGE.update_campaign(ident,name='Wrong');raise asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):asyncio.run(transactional_handler(self.c,cancelled)())
        self.assertEqual(self.c.read_campaigns()['campaigns'][ident]['name'],'Default')
    def test_serialized_mutations(self):
        self.initialize();events=[]
        async def first():events.append('a');await asyncio.sleep(.005);events.append('b')
        async def second():events.append('c')
        async def run():await asyncio.gather(transactional_handler(self.c,first)(),transactional_handler(self.c,second)())
        asyncio.run(run());self.assertEqual(events,['a','b','c'])
    def test_shared_campaign_roster_across_setups(self):
        ident=self.initialize();self.c.STATE=self.c.normalize_state({'characters':[{'id':'c','hp':10}]});self.call('save_setup',payload=self.payload(name='one',campaign=None))
        self.c.STATE['characters'][0]['hp']=3;self.call('save_setup',payload=self.payload(name='two',campaign=None));self.call('load_setup',payload=self.payload(name='one',campaign=None))
        self.assertEqual(self.c.STATE['characters'][0]['hp'],3)
    def test_unicode_name_and_duplicate_guard(self):
        self.initialize();ident=self.create('龍の旅',activate=True)
        self.call('update_campaign',campaign_id=ident,payload=self.payload(name='Étoiles',description=None));self.assertEqual(self.c.active_campaign(),ident)
        with self.assertRaises(HTTPError):self.create('étoiles')
    def test_nested_transaction_failure_rolls_back(self):
        ident=self.initialize()
        with self.assertRaises(ValueError):
            with self.c.STORAGE.transaction():
                with self.c.STORAGE.transaction():self.c.STORAGE.update_campaign(ident,name='Wrong')
                raise ValueError()
        self.assertEqual(self.c.read_campaigns()['campaigns'][ident]['name'],'Default')
    def test_removed_list_entries_deleted_remaining_ids_stable(self):
        ident=self.initialize();db=self.c.STORAGE;db.save_setup(ident,'fight',{'battle_order':['a','b','c']})
        sql=db.connection;before={r['combatant_id']:r['id'] for r in sql.execute('SELECT * FROM ordered_combatants')}
        db.save_setup(ident,'fight',{'battle_order':['c','a']})
        after={r['combatant_id']:r['id'] for r in sql.execute('SELECT * FROM ordered_combatants')}
        self.assertEqual(after,{'a':before['a'],'c':before['c']})
    def test_last_campaign_guard(self):
        ident=self.initialize()
        with self.assertRaises(HTTPError):self.call('delete_campaign',campaign_id=ident,delete_setups=True)
    def test_broadcast_after_commit(self):
        self.initialize();events=[]
        async def broadcaster():
            if getattr(self.c,'_defer_database_broadcast',False):self.c._database_broadcast_pending=True
            else:events.append(self.c.STORAGE.connection.in_transaction)
        self.c.broadcast=broadcaster;asyncio.run(transactional_handler(self.c,self.c.changed)());self.assertEqual(events,[False])

class MigrationTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.directory=Path(self.temp.name);self.path=self.directory/'scrying-glass.sqlite3'
    def tearDown(self):self.temp.cleanup()
    def check_upgrade(self,version):
        snap,state=old_database(self.path,version);c=context(self.directory)
        try:
            db=c.STORAGE;ident=db.get_value('active_campaign');self.assertEqual(db.connection.execute('PRAGMA user_version').fetchone()[0],4)
            if version==2:self.assertEqual(ident,'42')
            self.assertEqual(db.load_characters(ident)[0]['id'],'c');self.assertEqual(db.load_setup(ident,'fight')['monsters'],snap['monsters'])
            self.assertEqual(db.connection.execute('SELECT updated_at FROM battle_setups').fetchone()[0],1234.5)
            c.load_state();self.assertEqual(c.STATE['battle_round'],4);self.assertTrue(c.STATE['monsters'][0]['in_turn']);self.assertEqual(c.STATE['display']['battle_order_font_size'],24);self.assertEqual(c.STATE['activity_log'][0]['id'],'event')
            self.assertEqual(c.STATE['turn_successors_before_wrap'],['c']);self.assertEqual(db.read_campaigns()['campaigns'][ident]['last_setup'],'fight')
            self.assertTrue(db.migration_backup.is_file())
            with closing(sqlite3.connect(db.migration_backup)) as backup, backup:self.assertEqual(backup.execute('PRAGMA user_version').fetchone()[0],version)
            self.assertEqual(list(db.connection.execute('PRAGMA foreign_key_check')),[])
            for table in ('campaigns','battle_setups','characters','encounters','application_state'):
                self.assertFalse(any('json' in r[1] for r in db.connection.execute(f'PRAGMA table_info({table})')))
        finally:c.STORAGE.close()
        db=SQLiteStorage(self.path)
        try:self.assertIsNone(db.migration_backup);self.assertEqual(db.get_value('active_campaign'),ident)
        finally:db.close()

    def test_v1_slug_database_upgrade(self):self.check_upgrade(1)
    def test_v2_id_database_upgrade_preserves_ids(self):self.check_upgrade(2)
    def test_corrupt_json_rolls_back_schema(self):
        old_database(self.path,bad=True)
        with self.assertRaises(ValueError):SQLiteStorage(self.path)
        with closing(sqlite3.connect(self.path)) as c, c:self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],1);self.assertIn('slug',[r[1] for r in c.execute('PRAGMA table_info(campaigns)')])
    def test_unknown_nested_data_rolls_back_schema(self):
        old_database(self.path,unsupported=True)
        with self.assertRaises(ValueError):SQLiteStorage(self.path)
        with sqlite3.connect(self.path) as c:self.assertEqual(c.execute('PRAGMA user_version').fetchone()[0],1)
    def test_future_schema_rejected(self):
        with closing(sqlite3.connect(self.path)) as c, c:c.execute('PRAGMA user_version=99')
        with self.assertRaises(RuntimeError):SQLiteStorage(self.path)
    def test_unversioned_existing_table_rejected(self):
        with closing(sqlite3.connect(self.path)) as c, c:c.execute('CREATE TABLE example(x)')
        with self.assertRaises(RuntimeError):SQLiteStorage(self.path)
    def test_upgrade_v3_preserves_data_and_creates_backup(self):
        self.storage.close()
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("DROP TABLE users")
            db.execute("DROP TABLE account_migration")
            db.execute("PRAGMA user_version=3")
        from python.scrying_glass_storage import SQLiteStorage
        self.storage = SQLiteStorage(self.path)
        self.context.STORAGE = self.storage
        self.assertEqual(self.auth.db.execute("PRAGMA user_version").fetchone()[0], 4)
        self.assertTrue(self.storage.migration_backup.is_file())
        self.assertEqual(self.auth.db.execute("SELECT COUNT(*) FROM application_state").fetchone()[0], 1)
        self.assertIsNone(self.auth.db.execute("SELECT 1 FROM account_migration").fetchone())

    def test_backup_filename_not_overwritten(self):
        old_database(self.path);old=self.path.with_name(self.path.name+'.before-normalization.bak');old.write_bytes(b'keep')
        db=SQLiteStorage(self.path)
        try:self.assertNotEqual(db.migration_backup,old);self.assertEqual(old.read_bytes(),b'keep')
        finally:db.close()

if __name__=='__main__':unittest.main()
