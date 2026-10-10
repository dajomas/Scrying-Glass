"""Account and origin regression tests for commit 4d1df12.

Executes exact production functions/classes extracted via AST to avoid framework
imports. Route decorators, request injection and serialization are not exercised.
Account operations use real in-memory SQLite, not a mocked database.
"""
import ast
import asyncio
import copy
import sqlite3
import types
import unittest
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
class HTTPError(Exception):
    def __init__(self,status_code,detail):
        self.status_code=status_code;self.detail=detail;super().__init__(detail)

def execute(nodes,scope):
    nodes=copy.deepcopy(nodes)
    for node in nodes:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):node.decorator_list=[]
    future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future,*nodes],type_ignores=[])),'production-extract','exec'),scope)
    return scope

auth_tree=ast.parse((ROOT/'python/scrying_glass_service_auth.py').read_text())
auth_scope=execute([next(n for n in auth_tree.body if isinstance(n,ast.ClassDef))],dict(HTTPException=HTTPError,ROLES={'superadmin','admin','client'}))
AuthService=auth_scope['AuthService']
security_tree=ast.parse((ROOT/'python/scrying_glass_request_security.py').read_text())
origin_scope=execute([next(n for n in security_tree.body if isinstance(n,ast.AsyncFunctionDef))],dict(HTTPException=HTTPError,urlsplit=urlsplit))
shared_origin=origin_scope['same_origin']
users_tree=ast.parse((ROOT/'python/scrying_glass_admin_users.py').read_text())
installer=next(n for n in users_tree.body if isinstance(n,ast.FunctionDef) and n.name=='install_user_routes')
user_functions=[n for n in installer.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]

def request(base='https://table.example/',origin='https://table.example',site='same-origin'):
    headers={'sec-fetch-site':site}
    if origin is not None:headers['origin']=origin
    return types.SimpleNamespace(base_url=base,headers=headers)

class OriginTests(unittest.TestCase):
    def check(self,req):asyncio.run(shared_origin(req))
    def test_root_origin_allowed(self):self.check(request())
    def test_subpath_origin_allowed(self):self.check(request(base='https://table.example/tracker/'))
    def test_cross_origin_rejected(self):
        with self.assertRaises(HTTPError) as exc:self.check(request(origin='https://evil.example'))
        self.assertEqual(exc.exception.status_code,403)
    def test_cross_site_rejected_without_origin(self):
        with self.assertRaises(HTTPError):self.check(request(origin=None,site='cross-site'))
    def test_no_origin_nonbrowser_preserved(self):self.check(request(origin=None,site='none'))
    def test_scheme_mismatch_rejected(self):
        with self.assertRaises(HTTPError):self.check(request(origin='http://table.example'))
    def test_port_preserved(self):self.check(request(base='https://table.example:8443/tracker/',origin='https://table.example:8443'))
    def test_wrong_port_rejected(self):
        with self.assertRaises(HTTPError):self.check(request(base='https://table.example:8443/tracker/'))
    def test_path_in_origin_not_accepted(self):
        with self.assertRaises(HTTPError):self.check(request(base='https://table.example/tracker/',origin='https://table.example/tracker'))

class AccountTests(unittest.TestCase):
    def setUp(self):
        self.db=sqlite3.connect(':memory:');self.db.row_factory=sqlite3.Row
        self.db.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, role TEXT, password_hash TEXT)")
        self.db.execute("INSERT INTO users VALUES(1,'owner','superadmin','hash')")
        self.context=types.SimpleNamespace(STORAGE=types.SimpleNamespace(connection=self.db,transaction=lambda:self.db))
        self.auth=AuthService(self.context)
        async def invalidate(username):pass
        self.auth.invalidate=invalidate
        chosen=[n for n in user_functions if n.name in {'fields','create','update','delete','validate_user_id','same_origin'}]
        self.scope=execute(chosen,dict(context=self.context,auth=self.auth,HTTPException=HTTPError,
            sqlite3=sqlite3,Body=lambda *args:None,password_hash=lambda value:value.encode('utf-8').hex(),same_origin=shared_origin))
    def tearDown(self):self.db.close()
    def call(self,name,*args):return asyncio.run(self.scope[name](*args))
    def assert422(self,fn):
        with self.assertRaises(HTTPError) as exc:fn()
        self.assertEqual(exc.exception.status_code,422)
    def test_username_surrogate_rejected(self):
        self.assert422(lambda:self.call('create',{'username':'\ud800','role':'client','password':'password1'}))
    def test_password_surrogate_rejected(self):
        self.assert422(lambda:self.call('create',{'username':'new','role':'client','password':'abcdefg\ud800'}))
    def test_invalid_username_lookup_is_nonmatch(self):
        self.assertIsNone(self.auth.user('\ud800'))
    def test_unicode_account_supported(self):
        result=self.call('create',{'username':'José🐉','role':'client','password':'abcdefgh🐉'})
        self.assertEqual(self.auth.user('José🐉')['username'],'José🐉')
        self.assertEqual(result['role'],'client')
    def test_regular_update(self):
        result=self.call('update',1,{'username':'renamed'})
        self.assertEqual(result['username'],'renamed')
    def test_last_superadmin_delete_rejected(self):
        with self.assertRaises(HTTPError) as exc:self.call('delete',1)
        self.assertEqual(exc.exception.status_code,409)
    def test_last_superadmin_demotion_rejected(self):
        with self.assertRaises(HTTPError) as exc:self.call('update',1,{'role':'client'})
        self.assertEqual(exc.exception.status_code,409)
    def test_duplicate_username_rejected(self):
        with self.assertRaises(HTTPError) as exc:self.call('create',{'username':'owner','role':'client','password':'password1'})
        self.assertEqual(exc.exception.status_code,409)
    def test_missing_in_range_user_is_404(self):
        with self.assertRaises(HTTPError) as exc:self.call('delete',2**63-1)
        self.assertEqual(exc.exception.status_code,404)
    def test_user_routes_accept_subpath_origin(self):
        asyncio.run(self.scope['same_origin'](request(base='https://table.example/tracker/')))
    def test_regular_delete(self):
        user=self.call('create',{'username':'new','role':'client','password':'password1'})
        self.call('delete',user['id']);self.assertIsNone(self.auth.user('new'))

def invalid_id_test(operation,value):
    def test(self):
        args=(value,{'username':'changed'}) if operation=='update' else (value,)
        self.assert422(lambda:self.call(operation,*args))
        self.assertEqual(self.db.execute('SELECT username FROM users WHERE id=1').fetchone()[0],'owner')
    return test
for operation in ('update','delete'):
    for label,value in (('overflow',2**63),('underflow',-(2**63)-1),('zero',0)):
        setattr(AccountTests,'test_'+operation+'_'+label,invalid_id_test(operation,value))

if __name__=='__main__':unittest.main()
