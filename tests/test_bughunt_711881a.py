"""Focused WebSocket and snapshot-ID regressions for 711881a.
Production methods are AST-extracted to avoid framework imports. WebSocket
transport/auth are fixtures; snapshot queries use real in-memory SQLite.
"""
import ast
import asyncio
import copy
import json
import sqlite3
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT=Path(__file__).resolve().parents[1]
def execute(nodes,scope):
    future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future,*copy.deepcopy(nodes)],type_ignores=[])),'production-extract','exec'),scope)
    return scope
client_tree=ast.parse((ROOT/'python/scrying_glass_api_client.py').read_text())
client_class=next(n for n in client_tree.body if isinstance(n,ast.ClassDef))
ws_node=next(n for n in client_class.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='ws')
ws_handler=execute([ws_node],{'__name__':'regression_ws','operation_lock':lambda context:context.operation_lock})['ws']
storage_tree=ast.parse((ROOT/'python/scrying_glass_feature_storage.py').read_text())
FeatureStorage=execute([next(n for n in storage_tree.body if isinstance(n,ast.ClassDef))],{})['FeatureStorage']

class Disconnect(Exception):
    def __init__(self):self.code=1000;self.reason='test complete'

class Socket:
    def __init__(self,context,messages):
        self.context=context;self.messages=iter(messages);self.sent=[];self.closed=[];self.last_data=None
        self.headers={'origin':'https://table.example','host':'table.example'}
        self.url=types.SimpleNamespace(scheme='wss');self.cookies={'client':'token'}
    async def accept(self):pass
    async def send_text(self,text):self.sent.append(json.loads(text))
    async def close(self,code=1000,reason=''):self.closed.append((code,reason))
    async def receive_text(self):
        try:return next(self.messages)
        except StopIteration:
            self.last_data=copy.deepcopy(self.context.features.displays.get(self));raise Disconnect()

class WebSocketTests(unittest.IsolatedAsyncioTestCase):
    async def run_socket(self,messages,authorized=True):
        context=types.SimpleNamespace(CLIENT_SESSION_COOKIE='client',SOCKETS=set(),json=json,
            operation_lock=asyncio.Lock(),display_state=lambda:{'characters':[]},
            auth_session=lambda token:dict(username='table',role='client') if authorized and token=='token' else None,
            features=types.SimpleNamespace(store=types.SimpleNamespace(revision=lambda:5),displays={}))
        websocket=Socket(context,messages);logger=Mock()
        with patch.dict('sys.modules',{'fastapi':types.SimpleNamespace(WebSocketDisconnect=Disconnect)}),patch('logging.getLogger',return_value=logger):
            await ws_handler(types.SimpleNamespace(context=context),websocket)
        self.assertEqual(context.SOCKETS,set());self.assertEqual(context.features.displays,{})
        return websocket,logger
    async def test_ping(self):
        ws,logger=await self.run_socket([json.dumps({'type':'ping'})])
        self.assertEqual([m['type'] for m in ws.sent],['state','heartbeat'])
        logger.exception.assert_not_called()
    async def test_resync(self):
        ws,logger=await self.run_socket([json.dumps({'type':'resync'})])
        self.assertEqual([m['type'] for m in ws.sent],['state','state'])
        logger.exception.assert_not_called()
    async def test_ack_is_receive_only(self):
        ws,logger=await self.run_socket([json.dumps({'type':'ack','revision':5})])
        self.assertEqual(len(ws.sent),1);self.assertEqual(ws.last_data['revision'],5)
        logger.exception.assert_not_called()
    async def test_ack_cannot_move_backwards(self):
        ws,_=await self.run_socket([json.dumps({'type':'ack','revision':5}),json.dumps({'type':'ack','revision':2})])
        self.assertEqual(ws.last_data['revision'],5)
    async def test_boolean_ack_revision_is_ignored(self):
        ws,_=await self.run_socket([json.dumps({'type':'ack','revision':True})])
        self.assertIsNone(ws.last_data['revision'])
    async def test_invalid_json_is_ignored(self):
        ws,logger=await self.run_socket(['not json',json.dumps({'type':'ping'})])
        self.assertEqual(len(ws.sent),2);logger.exception.assert_not_called()
    async def test_nonobject_message_is_ignored(self):
        ws,logger=await self.run_socket(['[]',json.dumps({'type':'ping'})])
        self.assertEqual(len(ws.sent),2);logger.exception.assert_not_called()
    async def test_oversized_message_closes_with_policy_code(self):
        ws,_=await self.run_socket(['x'*1025])
        self.assertEqual(ws.closed[0][0],1008)
    async def test_unauthorized_connection_is_rejected(self):
        ws,_=await self.run_socket([],authorized=False)
        self.assertEqual(ws.sent,[]);self.assertEqual(ws.closed[0][0],1008)

def malformed_type_test(value):
    async def test(self):
        ws,logger=await self.run_socket([json.dumps({'type':value}),json.dumps({'type':'ping'})])
        self.assertEqual([m['type'] for m in ws.sent],['state','heartbeat'])
        logger.exception.assert_not_called()
    return test
for label,value in (('list',[]),('object',{}),('null',None),('bool',True),('integer',3)):
    setattr(WebSocketTests,'test_malformed_type_'+label,malformed_type_test(value))

class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');self.db.row_factory=sqlite3.Row
        self.db.execute('CREATE TABLE encounter_snapshots(id INTEGER PRIMARY KEY, campaign_id INTEGER, kind TEXT)')
        self.db.execute("INSERT INTO encounter_snapshots VALUES(1,1,'checkpoint')")
        self.store=FeatureStorage(types.SimpleNamespace(connection=self.db))
    def tearDown(self):self.db.close()
    def test_existing_row(self):self.assertEqual(self.store.row(1,1,'checkpoint')['id'],1)
    def test_other_campaign_cannot_read(self):self.assertIsNone(self.store.row(1,2,'checkpoint'))
    def test_other_kind_cannot_read(self):self.assertIsNone(self.store.row(1,1,'undo'))
    def test_existing_delete(self):
        self.store.delete(1,1,'checkpoint');self.assertIsNone(self.store.row(1,1,'checkpoint'))
    def test_scoped_delete(self):
        self.store.delete(1,2,'checkpoint');self.assertIsNotNone(self.store.row(1,1,'checkpoint'))
    def test_maximum_in_range_is_missing(self):self.assertIsNone(self.store.row(2**63-1,1,'checkpoint'))

def invalid_row_test(value):
    def test(self):self.assertIsNone(self.store.row(value,1,'checkpoint'))
    return test

def invalid_delete_test(value):
    def test(self):
        self.store.delete(value,1,'checkpoint');self.assertIsNotNone(self.store.row(1,1,'checkpoint'))
    return test
for label,value in (('overflow',2**63),('underflow',-(2**63)-1),('bool',True),('float',1.0)):
    setattr(SnapshotTests,'test_row_'+label,invalid_row_test(value))
    setattr(SnapshotTests,'test_delete_'+label,invalid_delete_test(value))

def invalid_load_test(value):
    def test(self):
        with self.assertRaisesRegex(ValueError,'Snapshot not found'):self.store.load(value,1,'checkpoint')
    return test
for label,value in (('overflow',2**63),('underflow',-(2**63)-1)):
    setattr(SnapshotTests,'test_load_'+label,invalid_load_test(value))

if __name__=='__main__':unittest.main()
