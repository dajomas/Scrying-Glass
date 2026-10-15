"""Real FastAPI lifespan composition checks; skipped if FastAPI is absent."""
import asyncio
import importlib
import types
import unittest
from contextlib import asynccontextmanager
from unittest.mock import patch
try:
    from fastapi import FastAPI, Request
except ImportError:
    FastAPI = None

@unittest.skipIf(FastAPI is None, 'FastAPI is not installed in this test environment')
class FastAPILifespanIntegrationTests(unittest.TestCase):
    def context(self):
        async def guard(request: Request):
            return {'role': 'admin'}
        return types.SimpleNamespace(STATE={}, ADMIN_SESSION_COOKIE='admin-cookie', require=lambda role, cookie: guard)

    def test_existing_lifespan_and_state_are_preserved(self):
        from python import scrying_glass_campaign_viewer_routes as routes
        importlib.reload(routes)
        events = []
        @asynccontextmanager
        async def existing(app):
            events.append('existing-start')
            yield {'existing': 'retained'}
            events.append('existing-stop')
        app = FastAPI(lifespan=existing)
        service = types.SimpleNamespace(initialize=lambda: events.append('acl-start'))
        async def run():
            with patch.object(routes, 'viewers', return_value=service):
                routes.install_campaign_viewers(self.context(), app, admin=True)
                self.assertEqual(events, [])
                async with app.router.lifespan_context(app) as state:
                    self.assertIn('acl-start', events)
                    self.assertIn('existing-start', events)
                    self.assertEqual(state['existing'], 'retained')
                    self.assertNotIn('existing-stop', events)
        asyncio.run(run())
        self.assertEqual(events.count('acl-start'), 1)
        self.assertIn('existing-stop', events)

    def test_client_lifespan_initializes_without_admin_endpoints(self):
        from python import scrying_glass_campaign_viewer_routes as routes
        importlib.reload(routes)
        app = FastAPI()
        initialized = []
        service = types.SimpleNamespace(initialize=lambda: initialized.append(True))
        async def run():
            with patch.object(routes, 'viewers', return_value=service):
                routes.install_campaign_viewers(self.context(), app)
                async with app.router.lifespan_context(app):
                    self.assertEqual(initialized, [True])
        asyncio.run(run())
        self.assertFalse(any('/viewers' in getattr(route, 'path', '') for route in app.routes))

if __name__ == '__main__':
    unittest.main()
