"""Ownership migration, request isolation and authorization using real SQLite."""
import asyncio
import copy
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from test_sqlite_storage import context, HTTPError, Handlers
from python.scrying_glass_campaign_ownership import ownership, actor
from python.scrying_glass_database_transactions import serialized_handler, transactional_handler
from python.scrying_glass_campaign_viewers import viewers
from python.scrying_glass_storage import SQLiteStorage

class OwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.c=context(Path(self.temp.name));self.c.import_legacy_storage()
        self.a=self.c.active_campaign();self.b=self.c.STORAGE.create_campaign('Other campaign','','now')
        self.c.create_default_setup(self.b);self.c.save_campaign_characters(self.b,[])
        self.ids={}
        for name,role in [('alice','admin'),('bob','admin'),('root','superadmin'),('viewer','client')]:
            self.ids[name]=str(self.c.STORAGE.connection.execute('INSERT INTO users(username,role,password_hash) VALUES (?,?,?)',(name,role,'hash')).lastrowid)
        def user(name):
            row=self.c.STORAGE.connection.execute('SELECT id,username,role FROM users WHERE username=?',(name,)).fetchone()
            return dict(row) if row else None
        self.c.user=user;self.c.ADMIN_SESSION_COOKIE='admin';self.c.CLIENT_SESSION_COOKIE='client'
        def session(token):
            value=user(token)
            return {'username':value['username'],'role':value['role']} if value else None
        self.c.auth_session=session
        def require(role,cookie):
            async def check(request):
                value=session(request.cookies.get(cookie,''))
                if not value:raise HTTPError(401,'Sign in required')
                if role=='superadmin' and value['role']!='superadmin':raise HTTPError(403,'Superadmin role required')
                if role=='admin' and value['role'] not in {'admin','superadmin'}:raise HTTPError(403,'Admin role required')
                return value
            return check
        self.c.require=require
        self.owner=ownership(self.c);self.owner.initialize();viewers(self.c).initialize()
        self.c.STATE=self.c.normalize_state({'monsters':[{'id':'private','name':'Private monster','initiative':10,'active':True}]})
        self.c.set_active_setup(self.a,self.c.DEFAULT_SETUP_NAME)
        fake=types.ModuleType('fastapi');fake.Request=object;fake.Form=lambda *args,**kwargs:None
        self.fake_patch=patch.dict(sys.modules,{'fastapi':fake});self.fake_patch.start()
    def tearDown(self):self.fake_patch.stop();self.c.STORAGE.close();self.temp.cleanup()
    def request(self,name,path):return types.SimpleNamespace(cookies={'admin':name},url=types.SimpleNamespace(path=path))
    def call(self,name,path,handler,*args,write=False,role='admin',**kwargs):
        wrapper=transactional_handler if write else serialized_handler
        return asyncio.run(wrapper(self.c,handler,role=role,cookie_name='admin')(*args,_operation_request=self.request(name,path),**kwargs))
    def grant(self,campaign,name):self.owner.reassign(campaign,{'owner_user_id':self.ids[name] if name else None})
    def test_multiple_admins_leave_all_campaigns_unassigned(self):
        self.assertIsNone(self.owner.owner(self.a));self.assertIsNone(self.owner.owner(self.b))
    def test_unassigned_admin_can_login_to_html(self):
        from python.scrying_glass_admin_pages import AdminPagesMixin
        self.c.HTMLResponse=lambda text:('html',text);self.c.ADMIN_HTML='Admin page'
        self.c.RedirectResponse=lambda url,status:('redirect',url)
        handler=AdminPagesMixin();handler.context=self.c
        response=asyncio.run(handler.admin_home(self.request('alice','/')))
        self.assertEqual(response,('html','Admin page'))
    def test_unassigned_admin_gets_empty_campaign_list_and_no_global_state(self):
        async def get_campaigns():return self.c.campaigns_payload()
        async def admin_get_state():return self.c.public_state()
        data=self.call('alice','/api/campaigns',get_campaigns)
        self.assertEqual(data['campaigns'],[]);self.assertIsNone(data['active'])
        state=self.call('alice','/api/state',admin_get_state)
        self.assertEqual(state['monsters'],[]);self.assertIsNone(state['active_campaign_id'])
        self.assertNotIn('Private monster',str(state))
    def test_admin_lists_only_owned_campaigns(self):
        self.grant(self.a,'alice');self.grant(self.b,'bob')
        async def get_campaigns():return self.c.campaigns_payload()
        self.assertEqual([x['id'] for x in self.call('alice','/api/campaigns',get_campaigns)['campaigns']],[self.a])
        self.assertEqual([x['id'] for x in self.call('root','/api/campaigns',get_campaigns)['campaigns']],[self.a,self.b])
    def test_owned_state_is_visible_but_other_owner_receives_blank(self):
        self.grant(self.a,'alice');self.grant(self.b,'bob')
        async def admin_get_state():return self.c.public_state()
        self.assertEqual(len(self.call('alice','/api/state',admin_get_state)['monsters']),1)
        self.assertEqual(self.call('bob','/api/state',admin_get_state)['monsters'],[])
    def test_nonowner_global_mutation_is_rejected_before_handler(self):
        self.grant(self.a,'alice');before=copy.deepcopy(self.c.STATE);called=[]
        async def mutate():called.append(True);self.c.STATE['monsters']=[]
        with self.assertRaises(HTTPError) as error:self.call('bob','/api/battle/next',mutate,write=True)
        self.assertEqual(error.exception.status_code,403);self.assertEqual(called,[]);self.assertEqual(self.c.STATE,before)
    def test_cross_campaign_target_is_rejected(self):
        self.grant(self.a,'alice');self.grant(self.b,'bob')
        async def update_campaign(campaign_id):return campaign_id
        with self.assertRaises(HTTPError):self.call('alice',f'/api/campaigns/{self.b}',update_campaign,self.b)
    def test_transfer_checks_both_source_and_destination(self):
        self.grant(self.a,'alice');self.grant(self.b,'bob')
        async def add_setup_to_campaign(campaign_id,payload):return True
        payload=types.SimpleNamespace(model_dump=lambda **kwargs:{'from_campaign':self.b})
        with self.assertRaises(HTTPError):self.call('alice',f'/api/campaigns/{self.a}/setups',add_setup_to_campaign,self.a,payload)
    def test_import_into_someone_elses_active_campaign_is_rejected(self):
        self.grant(self.b,'bob')
        async def import_setup(payload):return True
        payload=types.SimpleNamespace(model_dump=lambda **kwargs:{'campaign':self.b})
        with self.assertRaises(HTTPError):self.call('bob','/api/setups/import',import_setup,payload,write=True)
    def test_regular_admin_cannot_reassign(self):
        async def reassign_campaign_owner(campaign_id,body):return self.owner.reassign(campaign_id,body)
        with self.assertRaises(HTTPError):self.call('alice','/api/campaign-ownership/1',reassign_campaign_owner,self.a,{'owner_user_id':self.ids['alice']},write=True,role='superadmin')
        self.assertIsNone(self.owner.owner(self.a))
    def test_superadmin_reassigns_without_changing_client_grants(self):
        self.grant(self.a,'alice');viewers(self.c).replace(self.a,{'user_ids':[self.ids['viewer']]})
        async def reassign_campaign_owner(campaign_id,body):return self.owner.reassign(campaign_id,body)
        self.call('root',f'/api/campaign-ownership/{self.a}',reassign_campaign_owner,self.a,{'owner_user_id':self.ids['bob']},write=True,role='superadmin')
        self.assertEqual(self.owner.owner(self.a),self.ids['bob'])
        self.assertTrue(viewers(self.c).grants(self.a)['users'][0]['granted'])
    def test_create_campaign_is_automatically_owned_and_visible(self):
        payload=types.SimpleNamespace(name='New owned campaign',description='',activate=True)
        result=self.call('alice','/api/campaigns',Handlers(self.c).create_campaign,payload,write=True)
        ident=result['created_campaign_id'];self.assertEqual(self.owner.owner(ident),self.ids['alice'])
        self.assertIn(ident,[x['id'] for x in result['campaigns']]);self.assertEqual(self.c.active_campaign(),ident)
    def test_imported_new_campaign_is_owned_by_importing_admin(self):
        async def import_bundle():
            return {'campaign_id':self.c.STORAGE.create_campaign('Imported','','now')}
        result=self.call('alice','/api/campaign-bundle',import_bundle,write=True)
        self.assertEqual(self.owner.owner(result['campaign_id']),self.ids['alice'])
    def test_reassignment_is_effective_on_next_request(self):
        self.grant(self.a,'alice')
        async def mutate():return True
        self.assertTrue(self.call('alice','/api/battle/next',mutate))
        self.grant(self.a,'bob')
        with self.assertRaises(HTTPError):self.call('alice','/api/battle/next',mutate)
    def test_owner_role_change_and_deletion_clear_owner(self):
        self.grant(self.a,'alice');self.c.STORAGE.connection.execute("UPDATE users SET role='client' WHERE username='alice'")
        self.assertIsNone(self.owner.owner(self.a))
        self.grant(self.b,'bob');self.c.STORAGE.connection.execute("DELETE FROM users WHERE username='bob'")
        self.assertIsNone(self.owner.owner(self.b))
    def test_migration_never_reruns_after_assignment_or_restart(self):
        self.grant(self.a,'bob');path=self.c.STORAGE.path;self.c.STORAGE.close();self.c.STORAGE=SQLiteStorage(path)
        self.owner.initialize();self.assertEqual(self.owner.owner(self.a),self.ids['bob']);self.assertIsNone(self.owner.owner(self.b))
    def test_invalid_owner_is_rejected_without_changing_assignment(self):
        self.grant(self.a,'alice')
        for invalid in [self.ids['viewer'],self.ids['root'],'99999',True,'-1','9'*30]:
            with self.assertRaises(HTTPError):self.owner.reassign(self.a,{'owner_user_id':invalid})
        self.assertEqual(self.owner.owner(self.a),self.ids['alice'])
    def test_admin_viewer_choices_follow_ownership(self):
        self.grant(self.a,'alice');self.grant(self.b,'bob')
        self.assertEqual([x['id'] for x in viewers(self.c).choices({'username':'alice','role':'admin'})],[self.a])
        self.assertEqual(len(viewers(self.c).choices({'username':'root','role':'superadmin'})),2)
    def test_viewer_projection_does_not_inherit_requesting_admin_ownership(self):
        self.grant(self.a,'alice');self.grant(self.b,'bob');viewers(self.c).replace(self.b,{'user_ids':[self.ids['viewer']]})
        async def get_viewers(campaign_id):return viewers(self.c).state('viewer',self.b)
        state=self.call('alice',f'/api/campaigns/{self.a}/viewers',get_viewers,self.a)
        self.assertEqual(state['campaign']['id'],self.b);self.assertIsNone(actor(self.c))
    def test_viewer_grants_cannot_be_read_for_another_owner(self):
        self.grant(self.a,'alice');self.grant(self.b,'bob')
        async def get_viewers(campaign_id):return viewers(self.c).grants(campaign_id)
        with self.assertRaises(HTTPError):self.call('alice',f'/api/campaigns/{self.b}/viewers',get_viewers,self.b)
    def test_no_other_owned_replacement_deletion_is_rejected_safely(self):
        self.grant(self.a,'alice');self.grant(self.b,'bob')
        with self.assertRaises(HTTPError) as error:self.call('alice',f'/api/campaigns/{self.a}',Handlers(self.c).delete_campaign,self.a,delete_setups=True,write=True)
        self.assertEqual(error.exception.status_code,409);self.assertTrue(self.c.STORAGE.campaign_exists(self.a))
    def test_request_actor_is_cleared_after_exception(self):
        self.grant(self.a,'alice')
        async def mutate():raise RuntimeError('deliberate')
        with self.assertRaises(RuntimeError):self.call('alice','/api/battle/next',mutate)
        self.assertIsNone(actor(self.c))

class MigrationMatrixTests(unittest.TestCase):
    def test_approved_zero_one_and_multiple_admin_migration_matrix(self):
        for admin_count in (0,1,2):
            for campaigns in (1,2):
                with self.subTest(admin_count=admin_count,campaigns=campaigns),tempfile.TemporaryDirectory() as directory:
                    c=context(Path(directory));c.import_legacy_storage()
                    if campaigns==2:c.STORAGE.create_campaign('Second','','now')
                    db=c.STORAGE.connection
                    db.execute("INSERT INTO users(username,role,password_hash) VALUES ('root','superadmin','hash')")
                    ids=[]
                    for i in range(admin_count):ids.append(str(db.execute("INSERT INTO users(username,role,password_hash) VALUES (?,'admin','hash')",(f'admin{i}',)).lastrowid))
                    try:
                        service=ownership(c);service.initialize()
                        for row in db.execute('SELECT id FROM campaigns'):
                            self.assertEqual(service.owner(str(row[0])),ids[0] if admin_count==1 else None)
                        self.assertTrue(c.STORAGE.migration_backup.is_file())
                    finally:c.STORAGE.close()

if __name__=='__main__':unittest.main()
