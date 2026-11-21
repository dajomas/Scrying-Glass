"""3B bundle boundaries: native SQLite, actual ASGI installers and seeded sessions.
Recording sockets exercise production notifications, not network/browser delivery.
"""
import asyncio
import copy
import io
import json
import struct
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest.mock import patch
import test_statblock_2b_boundaries as boundaries
import test_statblock_setup_importing as graphs
from python import scrying_glass_campaign_bundle as bundles
from python.scrying_glass_campaign_ownership import actor
from python.scrying_glass_campaign_viewers import viewers
from python.scrying_glass_database_transactions import operation_lock, transactional_handler
from python.scrying_glass_feature_storage import FeatureStorage
from python.scrying_glass_service_auth import AuthService
from python.scrying_glass_service_features import fingerprint
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_loading import load_setup_private
from python.scrying_glass_statblock_model import canonical_bytes
from python.scrying_glass_statblock_restore import restore_bindings

import test_statblock_3b_boundaries as fixtures

BundleFixture=fixtures.BundleFixture
unpack=fixtures.unpack


class BundleHTTPBoundaryTests(BundleFixture,unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        BundleFixture.setUp(self)
        from fastapi import FastAPI
        from python.scrying_glass_api_features import install_feature_routes
        from python import scrying_glass_api_admin as api
        self.app=FastAPI(); install_feature_routes(self.c,self.app)
        admin=api.AdminAPI.__new__(api.AdminAPI); admin.context=self.c; admin.app=self.app
        routes=tuple(row for row in api.ADMIN_ROUTES if row[1]=='activate_campaign')
        self.assertEqual(len(routes),1)
        with patch.object(api,'ADMIN_ROUTES',routes): admin.register_routes()

    async def request(self,path='/api/campaign-bundle',*,method='GET',raw=None,body=None,
                      token='alice-token',origin='http://fixture.test',missing_file=False):
        content=b''; content_type='application/json'
        if raw is not None:
            boundary='sg-3b-multipart-boundary'; field='other' if missing_file else 'file'
            content=(('--'+boundary+'\r\nContent-Disposition: form-data; name="'+field+'"; filename="campaign.zip"\r\nContent-Type: application/zip\r\n\r\n').encode()
                     +raw+('\r\n--'+boundary+'--\r\n').encode())
            content_type='multipart/form-data; boundary='+boundary
        elif body is not None: content=json.dumps(body).encode()
        headers=[(b'host',b'fixture.test'),(b'origin',origin.encode()),
                 (b'content-type',content_type.encode()),(b'content-length',str(len(content)).encode())]
        if token is not None: headers.append((b'cookie',('admin='+token).encode()))
        scope=dict(type='http',asgi={'version':'3.0','spec_version':'2.3'},http_version='1.1',
                   method=method,scheme='http',path=path,raw_path=path.encode(),root_path='',
                   query_string=b'',headers=headers,client=('127.0.0.1',1234),server=('fixture.test',80))
        messages=[]; sent=False
        async def receive():
            nonlocal sent
            if not sent:
                sent=True; return {'type':'http.request','body':content,'more_body':False}
            return {'type':'http.disconnect'}
        async def send(message): messages.append(message)
        await self.app(scope,receive,send)
        start=next(item for item in messages if item['type']=='http.response.start')
        output=b''.join(item.get('body',b'') for item in messages if item['type']=='http.response.body')
        response_headers=dict(start['headers'])
        if response_headers.get(b'content-type',b'').startswith(b'application/zip'):
            value=output
        else:
            value=json.loads(output); self.assert_private_response(value)
        return start['status'],value,response_headers

    async def test_owner_export_import_assigns_owner_without_live_history_or_notifications(self):
        before=self.capture(); revision=self.f.store.revision()
        status,raw,headers=await self.request()
        self.assertEqual(status,200); self.assertEqual(headers[b'cache-control'],b'no-store')
        self.assertIn(self.secret,json.dumps(unpack(raw)))
        self.unchanged(before)
        with patch.object(self.c,'broadcast',wraps=self.c.broadcast) as broadcast:
            status,result,_=await self.request(method='POST',raw=raw)
            self.assertEqual(status,200); broadcast.assert_not_awaited()
        self.imported(result); self.assertEqual(self.owner.owner(result['campaign_id']),self.ids['alice'])
        self.assertEqual(self.c.active_campaign(),self.original_campaign)
        self.assertEqual(self.c.STATE._statblocks,self.original); self.assertEqual(self.f.store.revision(),revision)
        self.assertEqual(self.f.store.latest_undo(self.original_campaign)['id'],self.undo)
        self.assertIsNotNone(self.f.store.row(self.checkpoint,self.original_campaign,'checkpoint'))
        self.assertEqual(self.sends,[]); self.assertIsNone(actor(self.c))

    async def test_import_existing_admin_policy_and_superadmin_permissions_are_preserved(self):
        before=self.capture()
        status,_,_=await self.request(token='bob-token'); self.assertEqual(status,403); self.unchanged(before)
        status,result,_=await self.request(method='POST',raw=self.raw,token='bob-token')
        self.assertEqual(status,200); self.imported(result)
        self.assertEqual(self.owner.owner(result['campaign_id']),self.ids['bob'])
        self.owner.reassign(self.original_campaign,{'owner_user_id':self.ids['bob']})
        status,raw,_=await self.request(token='root-token'); self.assertEqual(status,200)
        status,result,_=await self.request(method='POST',raw=raw,token='root-token')
        self.assertEqual(status,200); self.imported(result); self.assertIsNone(self.owner.owner(result['campaign_id']))
        self.assertEqual(self.sends,[]); self.assertIsNone(actor(self.c))

    async def test_auth_origin_multipart_and_corrupt_archive_denials_are_atomic(self):
        cases=[({'token':None},401),({'token':'viewer-token'},403),
               ({'method':'POST','raw':self.raw,'token':None},401),
               ({'method':'POST','raw':self.raw,'token':'viewer-token'},403),
               ({'method':'POST','raw':self.raw,'origin':'http://evil.test'},403),
               ({'method':'POST','raw':self.raw,'missing_file':True},422),
               ({'method':'POST','raw':b'not a ZIP'},422)]
        for options,expected in cases:
            with self.subTest(options={k:v for k,v in options.items() if k!='raw'}):
                before=self.capture(); status,_,_=await self.request(**options)
                self.assertEqual(status,expected); self.unchanged(before)

    async def test_actual_upload_reader_rejects_over_25_mib_without_writes(self):
        before=self.capture()
        status,_,_=await self.request(method='POST',raw=b'x'*(25*1024*1024+1))
        self.assertEqual(status,413); self.unchanged(before)

    async def test_waiting_requests_recheck_export_owner_and_import_role_session(self):
        original_session=AuthService.session
        for change,method,expected in (('owner','GET',403),('role','POST',401),('session','POST',401)):
            with self.subTest(change=change):
                with self.c.STORAGE.transaction():
                    self.c.STORAGE.connection.execute("UPDATE users SET role='admin' WHERE username='alice'")
                    self.owner.reassign(self.original_campaign,{'owner_user_id':self.ids['alice']})
                self.c.SESSIONS['alice-token']={'username':'alice','role':'admin'}
                checked=asyncio.Event(); task=None
                def observe(auth,token):
                    value=original_session(auth,token)
                    if auth.context is self.c and token=='alice-token' and value: checked.set()
                    return value
                try:
                    with patch.object(AuthService,'session',new=observe):
                        async with operation_lock(self.c):
                            task=asyncio.create_task(self.request(method=method,raw=self.raw if method=='POST' else None))
                            await asyncio.wait_for(checked.wait(),5)
                            with self.c.STORAGE.transaction():
                                if change=='owner': self.owner.reassign(self.original_campaign,{'owner_user_id':self.ids['bob']})
                                elif change=='role': self.c.STORAGE.connection.execute("UPDATE users SET role='client' WHERE username='alice'")
                                else: self.c.SESSIONS.pop('alice-token')
                            before=self.capture()
                        status,_,_=await asyncio.wait_for(task,5)
                        self.assertEqual(status,expected); self.unchanged(before)
                finally:
                    if task is not None:
                        if not task.done(): task.cancel()
                        await asyncio.gather(task,return_exceptions=True)

    async def test_checkpoint_ownership_history_and_media_failures_rollback_without_emission(self):
        self.c.STATE['monsters'][0]['image_url']='/media/before.png'
        (self.c.UPLOAD_DIR/'before.png').write_bytes(b'fixture')
        raw=self.f.export_bundle(); snapshot=FeatureStorage.save_snapshot
        assign=self.owner.assign_created; after=self.f.after_transaction; write=Path.write_bytes
        def fail_snapshot(store,*args,**kwargs):
            snapshot(store,*args,**kwargs); raise OSError('after checkpoint')
        def fail_assign(*args): assign(*args); raise OSError('after ownership')
        def fail_history(*args): after(*args); raise OSError('after history')
        def fail_media(path,data): write(path,data[:1]); raise OSError('during media')
        cases=[(FeatureStorage,'save_snapshot',fail_snapshot,422),
               (self.owner,'assign_created',fail_assign,None),
               (self.f,'after_transaction',fail_history,None),(Path,'write_bytes',fail_media,422)]
        for target,attribute,replacement,expected in cases:
            with self.subTest(stage=attribute):
                before=self.capture()
                with patch.object(target,attribute,new=replacement):
                    if expected is None:
                        with self.assertRaises(OSError): await self.request(method='POST',raw=raw)
                    else:
                        status,_,_=await self.request(method='POST',raw=raw); self.assertEqual(status,expected)
                self.unchanged(before)
                self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')),[])

    async def test_import_activate_private_edit_restore_undo_and_reexport_coalesce_final_frames(self):
        status,raw,_=await self.request(); self.assertEqual(status,200)
        status,result,_=await self.request(method='POST',raw=raw); self.assertEqual(status,200)
        destination=result['campaign_id']; original=copy.deepcopy(self.original)
        viewers(self.c).replace(destination,{'user_ids':[self.ids['viewer']]})
        self.socket.query_params={'campaign_id':destination}
        status,_,_=await self.request('/api/campaigns/'+destination+'/activate',method='POST')
        self.assertEqual(status,200); self.assertEqual(self.c.active_campaign(),destination)
        self.sends.clear()
        async def edit_monster():
            value=self.c.STATE._statblocks['m']; value.pop('content_digest',None); value['source_label']=self.secret+' edited'
            await self.c.combatants_changed(monsters=True,characters=False)
        await transactional_handler(self.c,edit_monster)()
        edited=copy.deepcopy(self.current_private()['m']); self.assertEqual(len(self.sends),1)
        self.sends.clear()
        status,_,_=await self.request('/api/checkpoints/'+str(result['checkpoint_id'])+'/restore',method='POST',
                                    body={'confirm':True,'revision':self.f.store.revision()})
        self.assertEqual(status,200); restored=copy.deepcopy(self.current_private()['m'])
        self.assert_content(restored,original['m']); self.assertGreater(restored['revision'],edited['revision'])
        self.assertEqual(len(self.sends),1); sent=self.sends[0]
        self.assertFalse(sent['in_transaction']); self.assertEqual(sent['metadata'],sent['stored'])
        self.assertEqual(sent['stored'],self.current_private()); self.assert_private_response(sent['frame'])
        self.sends.clear(); undo=self.f.store.latest_undo(destination)
        status,_,_=await self.request('/api/battle/undo',method='POST',body={'id':undo['id']})
        self.assertEqual(status,200); self.assertEqual(len(self.sends),1)
        final=self.current_private()['m']; self.assert_content(final,edited)
        self.assertGreater(final['revision'],restored['revision'])
        self.assertFalse(self.sends[0]['in_transaction']); self.assert_private_response(self.sends[0]['frame'])
        self.assertEqual(self.stored(self.original_campaign),original)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks,self.current_private())
        status,raw,_=await self.request(); self.assertEqual(status,200)
        self.assertEqual(unpack(raw)['statblocks']['encounter']['m']['content_digest'],final['content_digest'])
        self.assertIsNone(actor(self.c)); self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')),[])


if __name__=='__main__': unittest.main()
