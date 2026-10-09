"""Focused server WebSocket tests with fake transport, real asyncio locks."""
import ast,asyncio,json,time,types,unittest
from pathlib import Path
from unittest.mock import patch

class Disconnect(Exception):
    code=1000;reason='test disconnect'

class Socket:
    def __init__(self,events):
        self.events=list(events);self.sent=[];self.closes=[];self.accepted=False
        self.headers={'host':'testserver','origin':'http://testserver'};self.url=types.SimpleNamespace(scheme='ws');self.cookies={'client':'token'}
    async def accept(self):self.accepted=True
    async def send_text(self,text):self.sent.append(json.loads(text))
    async def close(self,code=1000,reason=''):self.closes.append((code,reason))
    async def receive_text(self):
        if not self.events:raise Disconnect()
        event=self.events.pop(0)
        if callable(event):event=event()
        if isinstance(event,Exception):raise event
        return event

class DisplayConnectionTests(unittest.TestCase):
    def run_socket(self,events,mutate=None):
        feature=types.SimpleNamespace(store=types.SimpleNamespace(revision=lambda:7),displays={})
        c=types.SimpleNamespace(features=feature,SOCKETS=set(),CLIENT_SESSION_COOKIE='client',json=json,display_state=lambda:{'campaign':{'id':'1','name':'Campaign'},'monsters':[]},auth_session=lambda token:{'username':'table','role':'client'} if token=='token' else None)
        socket=Socket(events)
        if mutate:mutate(c,socket)
        tree=ast.parse((Path(__file__).resolve().parents[1]/'python/scrying_glass_api_client.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef));fn=next(n for n in cls.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='ws')
        future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0);scope={'operation_lock':lambda ctx:asyncio.Lock()}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[future,fn],type_ignores=[])),'ws','exec'),scope)
        fake=types.ModuleType('fastapi');fake.WebSocketDisconnect=Disconnect
        with patch.dict('sys.modules',{'fastapi':fake}):asyncio.run(scope['ws'](types.SimpleNamespace(context=c),socket))
        self.assertFalse(c.SOCKETS);self.assertFalse(feature.displays)
        return socket
    def test_initial_snapshot(self):self.assertEqual(self.run_socket([]).sent[0]['type'],'state')
    def test_ack_does_not_trigger_heartbeat(self):self.assertEqual(len(self.run_socket(['{"type":"ack","revision":7}']).sent),1)
    def test_pong_does_not_trigger_heartbeat_loop(self):self.assertEqual(len(self.run_socket(['{"type":"pong","revision":7}']).sent),1)
    def test_idle_sends_heartbeat_without_disconnect(self):
        socket=self.run_socket([TimeoutError(),TimeoutError()]);self.assertEqual([m['type'] for m in socket.sent],['state','heartbeat','heartbeat']);self.assertFalse(any(code==1008 for code,_ in socket.closes))
    def test_ping_receives_one_heartbeat(self):self.assertEqual([m['type'] for m in self.run_socket(['{"type":"ping"}']).sent],['state','heartbeat'])
    def test_resync_receives_snapshot(self):self.assertEqual([m['type'] for m in self.run_socket(['{"type":"resync"}']).sent],['state','state'])
    def test_invalid_json_ignored(self):self.assertEqual(len(self.run_socket(['not-json']).sent),1)
    def test_oversized_message_rejected(self):self.assertTrue(any(code==1008 for code,_ in self.run_socket(['x'*1025]).closes))
    def test_origin_rejected(self):
        socket=self.run_socket([],lambda c,s:s.headers.update(origin='http://other'));self.assertFalse(socket.accepted);self.assertEqual(socket.closes[0][0],1008)
    def test_missing_session_rejected(self):
        socket=self.run_socket([],lambda c,s:s.cookies.clear());self.assertFalse(socket.accepted);self.assertIn('Sign in',socket.closes[0][1])
    def test_session_revoked_during_idle(self):
        def mutate(c,s):
            def revoke():c.auth_session=lambda token:None;return TimeoutError()
            s.events=[revoke]
        socket=self.run_socket([],mutate);self.assertTrue(any(code==1008 for code,_ in socket.closes));self.assertEqual(len(socket.sent),1)

if __name__=='__main__':unittest.main()
