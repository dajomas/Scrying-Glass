"""Route/lifespan unit tests; the app double has no startup-event helpers."""
import asyncio
import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch

class HTTPError(Exception):
    def __init__(self, status_code, detail):
        self.status_code, self.detail = status_code, detail
        super().__init__(detail)

class ViewerRouteTests(unittest.TestCase):
    def setUp(self):
        self.fake = types.ModuleType('fastapi')
        self.fake.Body = lambda value: value
        self.fake.Depends = lambda dependency: dependency
        self.fake.Request = object
        self.fake.HTTPException = HTTPError
        self.fake.APIRouter = lambda *, lifespan: types.SimpleNamespace(lifespan_context=lifespan)
        self.service = types.SimpleNamespace(initialize=Mock())
        service_module = types.ModuleType('python.scrying_glass_campaign_viewers')
        service_module.viewers = lambda context: self.service
        self.module_patch = patch.dict(sys.modules, {
            'fastapi': self.fake,
            'python.scrying_glass_campaign_viewers': service_module,
        })
        self.module_patch.start()
        self.module = importlib.import_module('python.scrying_glass_campaign_viewer_routes')
        self.service_patch = patch.object(self.module, 'viewers', lambda context: self.service)
        self.service_patch.start()
        self.c = types.SimpleNamespace(STATE={}, ADMIN_SESSION_COOKIE='admin-cookie')
        def require(role, cookie):
            async def guard(request):
                if request.role not in {'admin', 'superadmin'}:
                    raise HTTPError(403, 'Admin role required')
                return {'role': request.role}
            return guard
        self.c.require = require
        self.routes = []
        self.routers = []
        self.app = types.SimpleNamespace(
            add_api_route=lambda path, handler, **kwargs: self.routes.append((path, handler, kwargs)),
            include_router=lambda router: self.routers.append(router),
        )
    def tearDown(self):
        self.service_patch.stop()
        self.module_patch.stop()

    def test_registration_works_without_add_event_handler_or_on_event(self):
        self.assertFalse(hasattr(self.app, 'add_event_handler'))
        self.assertFalse(hasattr(self.app, 'on_event'))
        self.module.install_campaign_viewers(self.c, self.app, admin=True)
        self.assertEqual(len(self.routers), 1)
        self.service.initialize.assert_not_called()

    def test_admin_routes_keep_authorization_and_same_origin_guards(self):
        self.module.install_campaign_viewers(self.c, self.app, admin=True)
        self.assertEqual([row[2]['methods'] for row in self.routes], [['GET'], ['PUT']])
        self.assertEqual(len(self.routes[0][2]['dependencies']), 1)
        self.assertEqual(self.routes[1][2]['dependencies'][1].__name__, 'same_origin')

    def test_client_cannot_execute_admin_grant_handler(self):
        self.module.install_campaign_viewers(self.c, self.app, admin=True)
        for path, handler, options in self.routes:
            kwargs = {'campaign_id': '1', '_operation_request': types.SimpleNamespace(role='client')}
            if options['methods'] == ['PUT']:
                kwargs['body'] = {'user_ids': []}
            with self.assertRaises(HTTPError) as error:
                asyncio.run(handler(**kwargs))
            self.assertEqual(error.exception.status_code, 403)

    def test_client_app_includes_lifespan_but_no_grant_routes(self):
        self.module.install_campaign_viewers(self.c, self.app)
        self.assertEqual(self.routes, [])
        self.assertEqual(len(self.routers), 1)

    def test_lifespan_initializes_only_on_entry_before_requests(self):
        self.module.install_campaign_viewers(self.c, self.app)
        self.service.initialize.assert_not_called()
        async def run():
            async with self.routers[0].lifespan_context(self.app):
                self.service.initialize.assert_called_once_with()
                from python.scrying_glass_database_transactions import operation_lock
                self.assertFalse(operation_lock(self.c).locked())
        asyncio.run(run())
        self.service.initialize.assert_called_once_with()

    def test_initialization_failure_aborts_startup_without_yielding(self):
        self.service.initialize.side_effect = RuntimeError('Unable to initialize ACL')
        self.module.install_campaign_viewers(self.c, self.app)
        async def run():
            async with self.routers[0].lifespan_context(self.app):
                self.fail('Application must not start after ACL initialization failed')
        with self.assertRaisesRegex(RuntimeError, 'Unable to initialize ACL'):
            asyncio.run(run())

    def test_write_guard_rejects_cross_origin(self):
        from python.scrying_glass_request_security import same_origin
        request = types.SimpleNamespace(headers={'origin': 'http://evil.example'}, base_url='http://localhost/')
        with self.assertRaises(Exception) as error:
            asyncio.run(same_origin(request))
        self.assertEqual(error.exception.status_code, 403)

if __name__ == '__main__':
    unittest.main()
