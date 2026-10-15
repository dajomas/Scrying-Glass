"""Route guard registration checks without requiring an installed FastAPI server."""
import asyncio
import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch
from test_sqlite_storage import HTTPError

class ViewerRouteTests(unittest.TestCase):
    def setUp(self):
        self.fake=types.ModuleType('fastapi');self.fake.Body=lambda value:value
        self.fake.Depends=lambda dependency:dependency;self.fake.Request=object;self.fake.HTTPException=HTTPError
        self.c=types.SimpleNamespace(STATE={},ADMIN_SESSION_COOKIE='admin-cookie')
        def require(role,cookie):
            async def guard(request):
                if request.role not in {'admin','superadmin'}:raise HTTPError(403,'Admin role required')
                return {'role':request.role}
            return guard
        self.c.require=require
        self.routes=[];self.events=[]
        self.app=types.SimpleNamespace(add_api_route=lambda path,handler,**kwargs:self.routes.append((path,handler,kwargs)),
            add_event_handler=lambda event,fn:self.events.append((event,fn)))
        self.patch=patch.dict(sys.modules,{'fastapi':self.fake});self.patch.start()
        self.module=importlib.import_module('python.scrying_glass_campaign_viewer_routes')
    def tearDown(self):self.patch.stop()
    def test_admin_routes_have_role_recheck_and_same_origin_write_guard(self):
        self.module.install_campaign_viewers(self.c,self.app,admin=True)
        self.assertEqual(len(self.routes),2)
        self.assertEqual([r[2]['methods'] for r in self.routes],[['GET'],['PUT']])
        self.assertEqual(len(self.routes[0][2]['dependencies']),1)
        self.assertEqual(self.routes[1][2]['dependencies'][1].__name__,'same_origin')
        self.assertEqual(self.events[0][0],'startup')
    def test_client_user_cannot_execute_admin_grant_handler(self):
        self.module.install_campaign_viewers(self.c,self.app,admin=True)
        request=types.SimpleNamespace(role='client')
        for path,handler,options in self.routes:
            kwargs={'campaign_id':'1','_operation_request':request}
            if options['methods']==['PUT']:kwargs['body']={'user_ids':[]}
            with self.assertRaises(HTTPError) as error:asyncio.run(handler(**kwargs))
            self.assertEqual(error.exception.status_code,403)
    def test_client_app_registers_startup_but_no_grant_routes(self):
        self.module.install_campaign_viewers(self.c,self.app)
        self.assertEqual(self.routes,[]);self.assertEqual(len(self.events),1)
    def test_write_guard_rejects_cross_origin(self):
        from python.scrying_glass_request_security import same_origin
        request=types.SimpleNamespace(headers={'origin':'http://evil.example'},base_url='http://localhost/')
        with self.assertRaises(HTTPError) as error:asyncio.run(same_origin(request))
        self.assertEqual(error.exception.status_code,403)

if __name__=='__main__':unittest.main()
