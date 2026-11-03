"""Viewer/ownership composition unit tests; no startup-event helpers."""
import asyncio
from contextlib import AsyncExitStack, ExitStack
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
        self.patches = ExitStack()
        self.addCleanup(self.patches.close)
        self.fake = types.ModuleType('fastapi')
        self.fake.Body = lambda value: value
        self.fake.Depends = lambda dependency: dependency
        self.fake.Request = object
        self.fake.HTTPException = HTTPError
        self.fake.APIRouter = lambda *, lifespan: types.SimpleNamespace(lifespan_context=lifespan)
        self.service = types.SimpleNamespace(initialize=Mock())
        service_module = types.ModuleType('python.scrying_glass_campaign_viewers')
        service_module.viewers = lambda context: self.service
        self.patches.enter_context(patch.dict(sys.modules, {
            'fastapi': self.fake,
            'python.scrying_glass_campaign_viewers': service_module,
        }))
        self.module = importlib.import_module('python.scrying_glass_campaign_viewer_routes')
        self.owner_module = importlib.import_module('python.scrying_glass_campaign_ownership_routes')
        # Import caching must not substitute real FastAPI objects for these doubles.
        for module in (self.module, self.owner_module):
            for name in ('APIRouter', 'Body', 'Depends'):
                self.patches.enter_context(patch.object(module, name, getattr(self.fake, name)))
        self.patches.enter_context(patch.object(self.module, 'viewers', lambda context: self.service))
        self.owner_service = types.SimpleNamespace(initialize=Mock())
        self.patches.enter_context(patch.object(self.owner_module, 'ownership', lambda context: self.owner_service))
        self.required = []
        self.c = types.SimpleNamespace(STATE={}, ADMIN_SESSION_COOKIE='admin-cookie')
        def require(role, cookie):
            self.required.append((role, cookie))
            async def guard(request):
                allowed = {'admin', 'superadmin'} if role == 'admin' else {'superadmin'}
                if request.role not in allowed:
                    raise HTTPError(403, 'Required role: ' + role)
                return {'role': request.role}
            return guard
        self.c.require = require
        self.routes = []
        self.routers = []
        self.app = types.SimpleNamespace(
            add_api_route=lambda path, handler, **kwargs: self.routes.append((path, handler, kwargs)),
            include_router=lambda router: self.routers.append(router),
        )
    def test_registration_works_without_add_event_handler_or_on_event(self):
        self.assertFalse(hasattr(self.app, 'add_event_handler'))
        self.assertFalse(hasattr(self.app, 'on_event'))
        self.module.install_campaign_viewers(self.c, self.app, admin=True)
        # One viewer initializer and one ownership initializer, not duplicates.
        self.assertEqual(len(self.routers), 2)
        self.service.initialize.assert_not_called()

    def test_admin_routes_keep_authorization_and_same_origin_guards(self):
        self.module.install_campaign_viewers(self.c, self.app, admin=True)
        keys = [(path, tuple(options['methods'])) for path, handler, options in self.routes]
        self.assertEqual(keys, [
            ('/api/campaign-ownership', ('GET',)),
            ('/api/campaign-ownership/{campaign_id}', ('PUT',)),
            ('/api/campaigns/{campaign_id}/viewers', ('GET',)),
            ('/api/campaigns/{campaign_id}/viewers', ('PUT',)),
        ])
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(self.required, [('superadmin', 'admin-cookie'), ('admin', 'admin-cookie')])
        for path, handler, options in self.routes:
            expected = 1 if options['methods'] == ['GET'] else 2
            self.assertEqual(len(options['dependencies']), expected)
            if expected == 2:
                self.assertEqual(options['dependencies'][1].__name__, 'same_origin')
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
        # One viewer initializer and one ownership initializer, not duplicates.
        self.assertEqual(len(self.routers), 2)

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

    def test_both_lifespans_initialize_their_own_service_once(self):
        self.module.install_campaign_viewers(self.c, self.app)
        self.service.initialize.assert_not_called()
        self.owner_service.initialize.assert_not_called()
        async def run():
            async with AsyncExitStack() as stack:
                for router in self.routers:
                    await stack.enter_async_context(router.lifespan_context(self.app))
                self.service.initialize.assert_called_once_with()
                self.owner_service.initialize.assert_called_once_with()
                from python.scrying_glass_database_transactions import operation_lock
                self.assertFalse(operation_lock(self.c).locked())
        asyncio.run(run())
        self.service.initialize.assert_called_once_with()
        self.owner_service.initialize.assert_called_once_with()

    def test_regular_admin_cannot_execute_ownership_handlers(self):
        self.module.install_campaign_viewers(self.c, self.app, admin=True)
        owners = [row for row in self.routes if row[0].startswith('/api/campaign-ownership')]
        self.assertEqual(len(owners), 2)
        for path, handler, options in owners:
            kwargs = {'_operation_request': types.SimpleNamespace(role='admin')}
            if options['methods'] == ['PUT']:
                kwargs.update(campaign_id='1', body={'owner_user_id': None})
            with self.assertRaises(HTTPError) as error:
                asyncio.run(handler(**kwargs))
            self.assertEqual(error.exception.status_code, 403)

    def test_ownership_initialization_failure_aborts_composed_startup(self):
        self.owner_service.initialize.side_effect = RuntimeError('Unable to initialize ownership')
        self.module.install_campaign_viewers(self.c, self.app)
        async def run():
            async with AsyncExitStack() as stack:
                for router in self.routers:
                    await stack.enter_async_context(router.lifespan_context(self.app))
                self.fail('Application must not start after ownership initialization failed')
        with self.assertRaisesRegex(RuntimeError, 'Unable to initialize ownership'):
            asyncio.run(run())
        self.service.initialize.assert_called_once_with()
        self.owner_service.initialize.assert_called_once_with()

if __name__ == '__main__':
    unittest.main()
