"""Real SQLite feature tests; HTTP/browser integration is separate."""
import asyncio,copy,io,json,sqlite3,tempfile,time,types,unittest,zipfile
from pathlib import Path
from unittest.mock import patch
import importlib.util
from test_sqlite_storage import context,HTTPError
from python.scrying_glass_feature_rules import normalize_features,apply_hp,public_features
from python.scrying_glass_feature_storage import FeatureStorage
from python.scrying_glass_service_features import FeaturesService
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_combatant import combatant_state

class FeatureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.c=context(Path(self.tmp.name))
        self.c.import_legacy_storage();self.c.load_state()
        self.c.UPLOAD_DIR=Path(self.tmp.name)/'uploads';self.c.UPLOAD_DIR.mkdir()
        if importlib.util.find_spec('fastapi') is None:
            fake=types.ModuleType('fastapi');fake.HTTPException=HTTPError;fake.Request=fake.UploadFile=object
            with patch.dict('sys.modules',{'fastapi':fake}):
                from python.scrying_glass_service_battle import BattleService
        else:
            from python.scrying_glass_service_battle import BattleService
        battle=BattleService(self.c)
        for name in vars(BattleService):
            if not name.startswith('_') and callable(getattr(battle,name,None)):setattr(self.c,name,getattr(battle,name))
        self.c.combatant_state=combatant_state;self.c.features=FeaturesService(self.c);self.f=self.c.features
        self.c.STATE=self.c.normalize_state({'monsters':[{'id':'m','name':'Goblin','hp':12,'active':True,'visible':True}], 'characters':[{'id':'c','name':'Cleric','hp':20,'active':True,'visible':True,'in_turn':True}], 'battle_order':['c','m'],'battle_round':1,'active_setup':{'campaign_id':self.c.active_campaign(),'name':'default'}})
        self.c.save_active_campaign_characters();self.c.save_active_setup_monsters();self.c.save_state()
    def tearDown(self):self.c.STORAGE.close();self.tmp.cleanup()
    def call(self,name,*args):return asyncio.run(transactional_handler(self.c,getattr(self.f,name))(*args))
    def item(self,id='m'):return self.c.entity(id)
    def effect(self,**kw):return dict(name='Blessed',source_id='c',notes='private note',public=False,concentration=False,timing='manual',turns=None,anchor_id=None,**kw)
    def test_temp_absorbs(self):
        self.call('edit_features','m',{'temp_hp':7});self.call('edit_features','m',{'hp_delta':-10})
        self.assertEqual((self.item()['hp'],self.item()['temp_hp']),(9,0))
    def test_temp_bypass_and_healing(self):
        self.call('edit_features','m',{'temp_hp':7});self.call('edit_features','m',{'hp_delta':-5,'absorb_temp':False});self.call('edit_features','m',{'hp_delta':3})
        self.assertEqual((self.item()['hp'],self.item()['temp_hp']),(10,7))
    def test_temp_replaced(self):
        self.call('edit_features','m',{'temp_hp':8});self.call('edit_features','m',{'temp_hp':3});self.assertEqual(self.item()['temp_hp'],3)
    def test_zero_is_down_and_recovers(self):
        self.call('edit_features','m',{'hp_delta':-12});self.assertEqual(self.item()['life_state'],'down')
        self.call('edit_features','m',{'hp_delta':3});self.assertEqual(self.item()['life_state'],'standing')
    def test_dead_needs_explicit_recovery(self):
        self.call('edit_features','m',{'life_state':'dead'});self.call('edit_features','m',{'hp_delta':3});self.assertEqual(self.item()['life_state'],'dead')
        self.call('edit_features','m',{'life_state':'standing'});self.assertTrue(self.item()['alive'])
    def test_death_saves(self):
        self.call('edit_features','m',{'life_state':'down'});self.call('edit_features','m',{'death_successes':3});self.assertEqual(self.item()['life_state'],'stable')
        self.call('edit_features','m',{'death_failures':3});self.assertEqual(self.item()['life_state'],'dead')
    def test_stable_damaged(self):
        self.call('edit_features','m',{'life_state':'stable'});self.call('edit_features','m',{'hp_delta':-1});self.assertEqual(self.item()['life_state'],'down')
    def test_invalid_edits_atomic(self):
        before=copy.deepcopy(self.c.STATE);revision=self.f.store.revision()
        for body in ({'temp_hp':-1},{'temp_hp':True},{'life_state':[]},{'death_successes':4},{'unknown':1}):
            with self.assertRaises(HTTPError):self.call('edit_features','m',body)
            self.assertEqual(self.c.STATE,before);self.assertEqual(self.f.store.revision(),revision)
    def test_effect_roundtrip_private(self):
        e=self.call('add_effect','m',self.effect());self.call('add_effect','m',{**self.effect(),'name':'Poisoned','public':True})
        loaded=self.c.STORAGE.load_setup(self.c.active_campaign(),'default')['monsters'][0]
        self.assertEqual(loaded['effects'],self.item()['effects'])
        payload=self.c.display_state()['monsters'][0];self.assertEqual(payload['effects'],[{'name':'Poisoned'}]);self.assertNotIn('private note',json.dumps(payload))
        self.call('remove_effect','m',e['id']);self.assertEqual(len(self.item()['effects']),1)
    def test_effect_anchor_boundary(self):
        self.call('add_effect','m',{**self.effect(),'timing':'end','anchor_id':'c','turns':2})
        self.f.expire('m','end');self.f.expire('c','start');self.assertEqual(self.item()['effects'][0]['turns'],2)
        self.f.expire('c','end');self.assertEqual(self.item()['effects'][0]['turns'],1)
        self.f.expire('c','end');self.assertEqual(self.item()['effects'],[])
    def test_concentration_linked_removal(self):
        self.call('add_effect','m',{**self.effect(),'concentration':True});self.call('add_effect','m',{**self.effect(),'name':'Prone'})
        self.call('end_concentration','c');self.assertEqual([e['name'] for e in self.item()['effects']],['Prone']);self.assertFalse(self.item('c')['concentrating'])
    def test_downed_source_drops_effects(self):
        self.call('add_effect','m',{**self.effect(),'concentration':True});self.call('edit_features','c',{'hp_delta':-20});self.assertEqual(self.item()['effects'],[])
    def test_invalid_effects_atomic(self):
        before=copy.deepcopy(self.c.STATE)
        for values in ({'public':'yes'},{'timing':'end','turns':1},{'source_id':'missing'},{'name':''}):
            with self.assertRaises(HTTPError):self.call('add_effect','m',{**self.effect(),**values})
            self.assertEqual(self.c.STATE,before)
    def test_undo_multiple_retains_audit(self):
        self.call('edit_features','m',{'temp_hp':7});self.call('edit_features','m',{'hp_delta':-10});count=len(self.c.STATE['activity_log'])
        self.call('undo',{'id':self.f.summary()['undo']['id']});self.assertEqual((self.item()['hp'],self.item()['temp_hp']),(12,7));self.assertEqual(len(self.c.STATE['activity_log']),count+1)
        self.call('undo',{'id':self.f.summary()['undo']['id']});self.assertEqual(self.item()['temp_hp'],0)
    def test_undo_roster_persisted(self):
        self.call('edit_features','c',{'hp_delta':-3});self.call('undo',{'id':self.f.summary()['undo']['id']});self.assertEqual(self.c.STORAGE.load_characters(self.c.active_campaign())[0]['hp'],20)
    def test_stale_undo(self):
        self.call('edit_features','m',{'temp_hp':5});old=self.f.summary()['undo']['id'];self.call('edit_features','m',{'temp_hp':4})
        with self.assertRaises(HTTPError):self.call('undo',{'id':old})
    def test_structural_change_clears_undo(self):
        self.call('edit_features','m',{'temp_hp':2})
        async def structural_edit():self.item()['name']='Changed'
        asyncio.run(transactional_handler(self.c,structural_edit)());self.assertIsNone(self.f.summary()['undo'])
    def test_failed_transaction_rollback(self):
        before=copy.deepcopy(self.c.STATE)
        async def edit_features():
            self.item()['hp']=1;self.c.save_active_setup_monsters();raise RuntimeError('failure')
        with self.assertRaises(RuntimeError):asyncio.run(transactional_handler(self.c,edit_features)())
        self.assertEqual(self.c.STATE,before);self.assertIsNone(self.f.summary()['undo']);self.assertEqual(self.c.STORAGE.load_setup(self.c.active_campaign(),'default')['monsters'][0]['hp'],12)
    def test_checkpoint_complete_restore(self):
        id=self.call('save_checkpoint',{'name':'Before'})['id'];self.call('edit_features','c',{'hp_delta':-5});self.call('add_effect','m',self.effect())
        preview=self.f.preview_checkpoint(id);self.call('restore_checkpoint',id,{'confirm':True,'revision':preview['revision']})
        self.assertEqual(self.item('c')['hp'],20);self.assertEqual(self.item()['effects'],[]);self.assertTrue(self.item('c')['in_turn']);self.assertIsNotNone(self.f.summary()['undo'])
    def test_checkpoint_confirmation(self):
        id=self.call('save_checkpoint',{'name':'Before'})['id'];rev=self.f.preview_checkpoint(id)['revision'];self.call('edit_features','m',{'temp_hp':1})
        with self.assertRaises(HTTPError):self.call('restore_checkpoint',id,{'confirm':True,'revision':rev})
    def test_checkpoint_campaign_scope(self):
        id=self.call('save_checkpoint',{'name':'Before'})['id'];other=self.c.STORAGE.create_campaign('Other','','now');self.c.STORAGE.set_value('active_campaign',other)
        with self.assertRaises(HTTPError):self.f.preview_checkpoint(id)
    def test_snapshot_limit_and_cascade(self):
        for i in range(35):self.call('edit_features','m',{'temp_hp':i+1})
        self.assertEqual(len(self.f.store.list(self.c.active_campaign(),'undo')),30);self.f.store.clear_undo()
        self.assertEqual(self.c.STORAGE.connection.execute('SELECT count(*) FROM snapshot_characters').fetchone()[0],0);self.assertFalse(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')))
    def test_revision_and_ack_status(self):
        rev=self.f.store.revision();self.call('edit_features','m',{'temp_hp':2});self.assertEqual(self.f.store.revision(),rev+1)
        ws=object();self.c.SOCKETS.add(ws);self.f.displays[ws]={'username':'table','revision':rev,'seen':time.time()};self.assertEqual(self.f.summary()['displays'][0]['status'],'behind')
        self.f.displays[ws]['revision']=rev+1;self.assertEqual(self.f.summary()['displays'][0]['status'],'live');self.f.displays[ws]['seen']-=40;self.assertEqual(self.f.summary()['displays'][0]['status'],'stale')
        self.c.SOCKETS.clear();self.assertEqual(self.f.summary()['displays'],[])
    def test_bundle_import_media_and_no_overwrite(self):
        self.item()['image_url']='/media/goblin.png';(self.c.UPLOAD_DIR/'goblin.png').write_bytes(b'image fixture');self.c.save_active_setup_monsters()
        raw=self.f.export_bundle();active=self.c.active_campaign();result=self.call('import_bundle',raw);self.assertEqual(self.c.active_campaign(),active);self.assertNotEqual(result['campaign_id'],active)
        imported=self.c.STORAGE.load_setup(result['campaign_id'],'default')['monsters'][0];self.assertNotEqual(imported['image_url'],'/media/goblin.png');self.assertEqual((self.c.UPLOAD_DIR/imported['image_url'].split('/')[-1]).read_bytes(),b'image fixture')
    def test_bundle_traversal_rejected(self):
        before=self.c.read_campaigns();out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as archive:archive.writestr('../evil.png',b'x');archive.writestr('campaign.json','{}')
        with self.assertRaises(HTTPError):self.call('import_bundle',out.getvalue())
        self.assertEqual(self.c.read_campaigns(),before);self.assertEqual(list(self.c.UPLOAD_DIR.iterdir()),[])
    def test_bundle_missing_media(self):
        self.item()['image_url']='/media/missing.png'
        with self.assertRaises(HTTPError):self.f.export_bundle()
    def test_restart_preserves_undo(self):
        self.call('add_effect','m',self.effect());self.call('edit_features','c',{'temp_hp':8});self.c.STORAGE.close();self.c.STORAGE=self.c.STORAGE.__class__(Path(self.tmp.name)/'scrying-glass.sqlite3');self.c.load_state()
        self.assertEqual(self.item('c')['temp_hp'],8);self.assertEqual(self.item()['effects'][0]['name'],'Blessed');self.call('undo',{'id':self.f.summary()['undo']['id']});self.assertEqual(self.item('c')['temp_hp'],0)
    def test_v4_upgrade_backup_preserves_accounts(self):
        path=Path(self.tmp.name)/'v4.sqlite3';db=self.c.STORAGE.__class__(path);db.connection.execute("INSERT INTO users(username,role,password_hash) VALUES ('dm','admin','hash')")
        for table in ('characters_effects','monsters_effects','snapshot_characters_effects','snapshot_characters_attributes','snapshot_characters','encounter_snapshots','feature_state'):db.connection.execute('DROP TABLE '+table)
        db.connection.execute('DROP TRIGGER IF EXISTS cleanup_snapshot');db.connection.execute('PRAGMA user_version=4');db.close();db=self.c.STORAGE.__class__(path)
        self.assertEqual(db.connection.execute('SELECT username FROM users').fetchone()[0],'dm');self.assertTrue(db.migration_backup.is_file())
        with sqlite3.connect(db.migration_backup) as backup:self.assertEqual(backup.execute('PRAGMA user_version').fetchone()[0],4)
        db.close()

if __name__=='__main__':unittest.main()
