"""Real SQLite ACLs, player-safe snapshots and scoped live-update checks."""
import asyncio
import ast
import copy
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
from test_sqlite_storage import context, HTTPError
from python.scrying_glass_campaign_viewers import viewers
from python.scrying_glass_database_transactions import operation_lock
from python.scrying_glass_storage import SQLiteStorage

class Socket:
    def __init__(self, token, campaign=None):
        self.cookies={'client':token};self.query_params={} if campaign is None else {'campaign_id':campaign}
        self.frames=[];self.closed=[];self.accepted=False
        self.headers={'host':'localhost','origin':'http://localhost'};self.url=types.SimpleNamespace(scheme='ws')
    async def send_text(self,text): self.frames.append(json.loads(text))
    async def close(self,**kwargs): self.closed.append(kwargs)
    async def accept(self): self.accepted=True

class CampaignViewerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.directory=Path(self.tmp.name)
        self.c=context(self.directory);self.c.import_legacy_storage();self.a=self.c.active_campaign()
        self.b=self.c.STORAGE.create_campaign('Second campaign','','now')
        self.c.create_default_setup(self.b);self.c.save_campaign_characters(self.b,[])
        self.c.STATE=self.c.normalize_state({'monsters':[{'id':'live-secret','name':'Live secret','active':True,
            'visible':True,'hp':9,'ac':15,'initiative':12,'show_hp':False,'show_ac':False,
            'effects':[{'id':'hidden','name':'Private effect','public':False,'concentration':False,
                        'timing':'manual','turns':None,'notes':'','source_id':None,'anchor_id':None}]}]})
        self.c.set_active_setup(self.a,self.c.DEFAULT_SETUP_NAME)
        saved=self.c.normalize_state({'monsters':[{'id':'saved-only','name':'Saved monster','active':True,
            'visible':True,'hp':7,'ac':17,'initiative':4,'show_hp':False,'show_ac':False}]})
        self.c.STORAGE.save_setup(self.b,'encounter',self.c.setup_snapshot(saved));self.c.remember_setup(self.b,'encounter')
        self.ids={}
        for name,role in [('alice','client'),('bob','client'),('dm','admin'),('root','superadmin')]:
            self.ids[name]=str(self.c.STORAGE.connection.execute('INSERT INTO users(username,role,password_hash) VALUES (?,?,?)',(name,role,'hash')).lastrowid)
        self.c.SESSIONS={name:{'username':name,'role':role} for name,role in [('alice','client'),('bob','client'),('dm','admin'),('root','superadmin')]}
        self.c.CLIENT_SESSION_COOKIE='client'
        def user(name):
            row=self.c.STORAGE.connection.execute('SELECT id,username,role FROM users WHERE username=?',(name,)).fetchone()
            return dict(row) if row else None
        self.c.user=user
        def session(token):
            value=self.c.SESSIONS.get(token);actual=user(value['username']) if value else None
            return value if actual and actual['role']==value['role'] else None
        self.c.auth_session=session
        self.c.features=types.SimpleNamespace(store=types.SimpleNamespace(revision=lambda:7),displays={})
        self.acl=viewers(self.c);self.acl.initialize()
    def tearDown(self): self.c.STORAGE.close();self.tmp.cleanup()
    def grant(self,campaign,*names): return self.acl.replace(campaign,{'user_ids':[self.ids[name] for name in names]})
    def test_new_acl_is_deny_by_default_and_backed_up(self):
        self.assertEqual(self.acl.choices(self.c.SESSIONS['alice']),[])
        self.assertTrue(self.c.STORAGE.migration_backup.is_file());self.assertEqual(self.acl.state('alice')['monsters'],[])
    def test_many_users_and_many_campaigns(self):
        self.grant(self.a,'alice','bob');self.grant(self.b,'alice')
        self.assertEqual({r['id'] for r in self.acl.choices(self.c.SESSIONS['alice'])},{self.a,self.b})
        self.assertEqual([r['id'] for r in self.acl.choices(self.c.SESSIONS['bob'])],[self.a])
    def test_single_campaign_auto_selects(self):
        self.grant(self.a,'alice');state=self.acl.state('alice')
        self.assertEqual(state['campaign']['id'],self.a);self.assertFalse(state['viewer_selection_required'])
    def test_multiple_campaigns_require_selection_before_data(self):
        self.grant(self.a,'alice');self.grant(self.b,'alice');state=self.acl.state('alice')
        self.assertTrue(state['viewer_selection_required']);self.assertEqual(state['monsters'],[])
        self.assertNotIn('Live secret',json.dumps(state))
    def test_unauthorized_http_selection_is_forbidden(self):
        self.grant(self.b,'alice')
        with self.assertRaises(HTTPError) as error:self.acl.state('alice',self.a)
        self.assertEqual(error.exception.status_code,403)
    def test_saved_campaign_projection_never_changes_live_state_or_exposes_hidden_fields(self):
        self.grant(self.b,'alice');before=copy.deepcopy(self.c.STATE);state=self.acl.state('alice',self.b)
        self.assertEqual(state['campaign']['id'],self.b);self.assertEqual([m['id'] for m in state['monsters']],['saved-only'])
        self.assertNotIn('hp',state['monsters'][0]);self.assertNotIn('ac',state['monsters'][0])
        self.assertEqual(state['viewer_source'],'saved');self.assertEqual(self.c.STATE,before);self.assertEqual(self.c.active_campaign(),self.a)
    def test_live_campaign_uses_existing_player_filter(self):
        self.grant(self.a,'alice');state=self.acl.state('alice',self.a)
        self.assertNotIn('hp',state['monsters'][0]);self.assertNotIn('Private effect',json.dumps(state))
    def test_nonclient_grants_rejected_atomically(self):
        self.grant(self.a,'alice')
        with self.assertRaises(HTTPError):self.grant(self.a,'bob','dm')
        self.assertEqual([r['username'] for r in self.acl.grants(self.a)['users'] if r['granted']],['alice'])
    def test_admin_and_superadmin_implicitly_see_all_campaigns(self):
        for name in ('dm','root'):self.assertEqual({r['id'] for r in self.acl.choices(self.c.SESSIONS[name])},{self.a,self.b})
    def test_grants_persist_across_restart(self):
        self.grant(self.a,'alice');path=self.c.STORAGE.path;self.c.STORAGE.close();self.c.STORAGE=SQLiteStorage(path);self.acl.initialize()
        self.assertEqual([r['id'] for r in self.acl.choices(self.c.SESSIONS['alice'])],[self.a])
    def test_role_change_removes_grants(self):
        self.grant(self.a,'alice');self.c.STORAGE.connection.execute("UPDATE users SET role='admin' WHERE username='alice'")
        self.c.STORAGE.connection.execute("UPDATE users SET role='client' WHERE username='alice'")
        self.assertEqual(self.acl.choices(self.c.SESSIONS['alice']),[])
    def test_user_deletion_cascades_grants(self):
        self.grant(self.a,'alice');self.c.STORAGE.connection.execute("DELETE FROM users WHERE username='alice'")
        self.assertEqual(self.c.STORAGE.connection.execute('SELECT count(*) FROM campaign_viewers').fetchone()[0],0)
    def test_invalid_ids_and_unknown_users_do_not_change_grants(self):
        self.grant(self.a,'alice')
        for value in ('no','0','-1','9'*40,'999999'):
            with self.assertRaises(HTTPError):self.acl.replace(self.a,{'user_ids':[value]})
        self.assertTrue(any(u['granted'] for u in self.acl.grants(self.a)['users']))
    def test_broadcast_is_scoped_per_viewer_and_revocation_clears_data(self):
        self.grant(self.a,'alice');self.grant(self.b,'bob');first=Socket('alice',self.a);second=Socket('bob',self.b)
        self.c.SOCKETS.update([first,second]);asyncio.run(self.c.broadcast())
        self.assertEqual(first.frames[-1]['state']['campaign']['id'],self.a);self.assertEqual(second.frames[-1]['state']['campaign']['id'],self.b)
        self.assertNotIn('Live secret',json.dumps(second.frames));self.grant(self.a);asyncio.run(self.c.broadcast())
        self.assertEqual(first.frames[-1]['state']['monsters'],[]);self.assertIsNone(first.frames[-1]['state']['campaign'])
    def test_revoked_selection_offers_only_remaining_campaigns(self):
        self.grant(self.a,'alice');self.grant(self.b,'alice');self.grant(self.a);state=self.acl.state('alice',self.a,forgiving=True)
        self.assertTrue(state['viewer_selection_required']);self.assertEqual([c['id'] for c in state['viewer_campaigns']],[self.b])
        self.assertEqual(state['monsters'],[])
    def test_logged_out_socket_gets_only_empty_auth_required_state(self):
        self.grant(self.a,'alice');self.c.SESSIONS.pop('alice');state=self.acl.socket_state(Socket('alice',self.a))
        self.assertTrue(state['viewer_auth_required']);self.assertEqual(state['monsters'],[])
    def client_class(self):
        tree=ast.parse((Path(__file__).resolve().parents[1]/'python/scrying_glass_api_client.py').read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef))
        module=ast.Module(body=[ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0),cls],type_ignores=[])
        namespace={'Form':lambda *args,**kwargs:None,'operation_lock':operation_lock,
                   '__package__':'python','__name__':'python.scrying_glass_api_client'}
        exec(compile(ast.fix_missing_locations(module),'ClientAPI','exec'),namespace)
        return namespace['ClientAPI']
    def test_http_state_handler_uses_cookie_and_campaign_query(self):
        cls=self.client_class();client=cls.__new__(cls);client.context=self.c
        request=types.SimpleNamespace(cookies={'client':'alice'},query_params={'campaign_id':self.b});self.grant(self.b,'alice')
        self.assertEqual(client.client_get_state(request)['campaign']['id'],self.b)
    def test_websocket_initial_and_resync_never_fall_back_to_global_state(self):
        self.grant(self.b,'alice');ws=Socket('alice',self.b)
        class Disconnect(Exception):
            code=1000
            reason='test complete'
        messages=iter(['resync'])
        async def receive():
            try:return json.dumps({'type':next(messages)})
            except StopIteration:raise Disconnect()
        ws.receive_text=receive;cls=self.client_class();client=cls.__new__(cls);client.context=self.c
        fake=types.ModuleType('fastapi');fake.WebSocketDisconnect=Disconnect
        with patch.dict(sys.modules,{'fastapi':fake}):asyncio.run(client.ws(ws))
        states=[frame['state'] for frame in ws.frames if frame['type']=='state'];self.assertEqual(len(states),2)
        self.assertTrue(all(frame['campaign']['id']==self.b for frame in states));self.assertNotIn('Live secret',json.dumps(ws.frames))

if __name__=='__main__':unittest.main()
