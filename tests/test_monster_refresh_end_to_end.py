"""Assembled Chromium UI forwarded to real secured ASGI refresh routes and SQLite.

Transport is intercepted, sessions pre-seeded, and provider/HP operations mocked.
No live external provider, password login, TCP server or new OS process is tested.
"""
import asyncio
import copy
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from unittest.mock import Mock
from playwright.async_api import async_playwright
from web_html.admin_html import ADMIN_HTML
import test_source_bonus_offer_acceptance as creation
from python.scrying_glass_monster_refresh_review import install_monster_refresh
from python.scrying_glass_service_battle import BattleService
from python.scrying_glass_service_features import FeaturesService
from python.scrying_glass_combatant import combatant_state
from python.scrying_glass_monster_source_snapshot import FIELDS
from python.scrying_glass_statistics import reduce_stat
from python.scrying_glass_storage import SQLiteStorage

ROOT = Path(__file__).resolve().parents[1]


class MonsterRefreshEndToEndTests(unittest.IsolatedAsyncioTestCase):
    request = creation.SourceBonusOfferAcceptanceTests.request
    lookup = creation.SourceBonusOfferAcceptanceTests.lookup
    form = creation.SourceBonusOfferAcceptanceTests.form
    snapshot = creation.SourceBonusOfferAcceptanceTests.snapshot

    async def asyncSetUp(self):
        creation.SourceBonusOfferAcceptanceTests.setUp(self)
        c = self.context
        battle = BattleService(c)
        for name in vars(BattleService):
            if not name.startswith('_') and callable(getattr(battle, name, None)):
                setattr(c, name, getattr(battle, name))
        c.combatant_state = combatant_state
        c.features = FeaturesService(c)
        install_monster_refresh(c, self.app)
        self.ids = []
        for name, bonus in (('Alpha', 2), ('Beta', 3)):
            candidate = await self.lookup(bonus)
            status, result = await self.request('POST', '/api/monsters',
                fields=dict(self.form(candidate), name=name))
            self.assertEqual(status, 200)
            self.ids.append(result[0]['id'])
        for item, bonus in zip(c.STATE['monsters'], (2, 3)):
            item.update(initiative_bonus=bonus, initiative_roll=16, initiative=16+bonus,
                        active=True, visible=True, in_turn=False)
        character = c.normalize_state({'characters': [dict(id='hero', name='Hero', hp=20,
            max_hp=20, initiative=19, active=True, visible=True, in_turn=True)]})['characters'][0]
        c.STATE['characters'] = [character]
        c.STATE['battle_order'] = ['hero', self.ids[1], self.ids[0]]
        c.STATE['battle_round'] = 4
        c.save_active_campaign_characters()
        await c.combatants_changed(monsters=True)
        c.dnd_monster_candidates = Mock(return_value=[(False, '/monsters/example')])
        c.dnd_monster_detail_html = Mock(return_value=
            '<div class="mon-stat-block">AC 18 Initiative +12 (22) HP 13</div>')
        c.dnd_monster_stats_from_html = Mock(return_value=(18, '2d8+2', 'dice'))
        self.hp_roll = Mock(return_value=13)
        c.hp_value_factory = Mock(return_value=self.hp_roll)
        self.calls = []
        self.errors = []
        runtime = await async_playwright().start()
        self.addAsyncCleanup(runtime.stop)
        self.browser = await runtime.chromium.launch(headless=True)
        self.addAsyncCleanup(self.browser.close)

    async def dispatch(self, request):
        parts = urlsplit(request.url)
        body = (request.post_data or '').encode()
        headers = await request.all_headers()
        scope = dict(type='http', asgi={'version': '3.0'}, http_version='1.1',
            method=request.method, scheme='http', path=parts.path, raw_path=parts.path.encode(),
            query_string=parts.query.encode(), root_path='',
            headers=[(key.encode(), value.encode()) for key, value in headers.items()],
            client=('127.0.0.1', 1234), server=('fixture.test', 80))
        messages = []
        sent = False
        async def receive():
            nonlocal sent
            if not sent:
                sent = True
                return dict(type='http.request', body=body, more_body=False)
            return dict(type='http.disconnect')
        async def send(message):
            messages.append(message)
        await asyncio.wait_for(self.app(scope, receive, send), 10)
        status = next(item['status'] for item in messages if item['type'] == 'http.response.start')
        response = b''.join(item.get('body', b'') for item in messages if item['type'] == 'http.response.body')
        return status, response

    async def open_page(self, width=1440):
        page = await self.browser.new_page(viewport={'width': width, 'height': 1000})
        self.addAsyncCleanup(page.close)
        page.set_default_timeout(5000)
        await page.context.add_cookies([dict(name='admin-test', value='owner-session', url='http://fixture.test/')])
        page.on('pageerror', lambda error: self.errors.append(str(error)))
        async def route(request):
            path = urlsplit(request.request.url).path
            if path == '/':
                await request.fulfill(content_type='text/html', body=ADMIN_HTML)
            elif path.startswith('/static/'):
                target = ROOT/path.lstrip('/')
                if target.is_file():
                    await request.fulfill(content_type='text/javascript' if target.suffix == '.js' else 'text/css',
                                          body=target.read_bytes())
                else:
                    await request.fulfill(status=404)
            elif path.startswith('/api/monsters/refresh/'):
                payload = request.request.post_data_json
                status, response = await self.dispatch(request.request)
                self.calls.append((path, payload, status))
                await request.fulfill(status=status, content_type='application/json', body=response)
            elif path.startswith('/api/'):
                self.assertEqual(request.request.method, 'GET', 'Unexpected browser mutation: '+path)
                c = self.context
                campaign = c.active_campaign()
                data = {
                    '/api/state': c.public_state(), '/api/features': c.features.summary(),
                    '/api/campaigns': dict(active=campaign, campaigns=[dict(id=campaign,
                        name='Default', description='', setups=['default'], last_setup='default')], moved=[]),
                    '/api/setups': dict(campaign=campaign, names=['default']),
                    '/api/me': dict(username='owner', role='admin'),
                }.get(path, {})
                await request.fulfill(json=data)
            else:
                await request.fulfill(status=404)
        await page.route('**/*', route)
        await page.goto('http://fixture.test/', wait_until='load')
        await page.wait_for_function("document.querySelectorAll('#monsters input[data-select-id]').length === 2")
        toggle = page.locator('#toggleMonsterDisplayPane')
        if await toggle.get_attribute('aria-expanded') == 'false':
            await toggle.click()
        await page.locator('#monsterBulkAction').wait_for(state='visible')
        self.assertEqual(self.errors, [])
        return page

    async def review(self, page, indexes=(0,)):
        for index in indexes:
            ident = self.ids[index]
            await page.locator(f'#monsters input[data-select-id="{ident}"]').check()
        # Drive the real bulk-select change handler, including its action reset.
        await page.locator('#monsterBulkAction').select_option('refresh-source-review')
        await page.get_by_role('dialog', name='Refresh selected monsters from source', exact=True).wait_for()
        await page.wait_for_function("document.querySelector('.sg-refresh-review').getAttribute('aria-busy') === 'false'")
        self.context.hp_value_factory.assert_not_called()
        self.hp_roll.assert_not_called()

    async def apply(self, page):
        await page.get_by_role('button', name='Apply selected changes', exact=True).click()
        await page.wait_for_function("!document.querySelector('.sg-refresh-review')")
        await page.wait_for_function("document.querySelectorAll('#monsters input[data-select-id]').length === 2")

    async def test_desktop_and_narrow_apply_preserve_turn_ties_unselected_and_restart(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                self.context.hp_value_factory.reset_mock()
                self.hp_roll.reset_mock()
                before = copy.deepcopy(self.context.STATE)
                page = await self.open_page(width)
                await self.review(page)
                self.assertEqual(self.context.STATE, before)
                for label in ('Initiative bonus', 'Max HP', 'Current HP'):
                    control = page.get_by_role('checkbox', name=label+' for Alpha', exact=True)
                    self.assertFalse(await control.is_checked())
                    await control.focus()
                    await page.keyboard.press('Space')
                self.assertEqual(self.context.STATE, before)
                await self.apply(page)
                state = self.context.STATE
                self.assertEqual(state['battle_order'], [self.ids[0], 'hero', self.ids[1]])
                self.assertEqual(state['battle_round'], 4)
                self.assertEqual(state['characters'], before['characters'])
                self.assertEqual(state['monsters'][1], before['monsters'][1])
                first = state['monsters'][0]
                self.assertEqual((first['initiative'], first['initiative_roll'], first['initiative_bonus']), (28, 16, 12))
                self.assertEqual((first['hp'], first['max_hp']), (13, 13))
                self.assertFalse(first['in_turn'])
                self.context.hp_value_factory.assert_called_once_with('2d8+2', '')
                self.hp_roll.assert_called_once_with()
                self.context.STORAGE.close()
                self.context.STORAGE = SQLiteStorage(self.directory/'scrying-glass.sqlite3')
                self.context.load_state()
                self.assertEqual(self.context.STATE['battle_order'], [self.ids[0], 'hero', self.ids[1]])
                self.assertEqual(self.context.STATE['monsters'][0]['initiative'], 28)
                self.assertEqual(self.context.STATE['monsters'][0]['initiative_bonus_origin'], 'source')
                self.assertTrue(self.context.STATE['characters'][0]['in_turn'])
                await page.close()
        self.assertEqual(self.errors, [])

    async def test_real_candidate_resolution_keeps_other_checks_and_unchecked_hp(self):
        self.context.dnd_monster_candidates.return_value = [
            (False, '/monsters/example'), (True, '/monsters/legacy-example')]
        for item in self.context.STATE['monsters']:
            for field in FIELDS:
                item.pop(field, None)
        await self.context.combatants_changed(monsters=True)
        before = copy.deepcopy(self.context.STATE)
        page = await self.open_page()
        await self.review(page, (0, 1))
        for name in ('Alpha', 'Beta'):
            chooser = page.get_by_label('Source candidate for '+name, exact=True)
            self.assertEqual(await chooser.locator('option').count(), 3)
            self.assertFalse(await page.get_by_role('checkbox', name='Current HP for '+name, exact=True).is_checked())
            await chooser.select_option('0')
            await page.get_by_role('button', name='Use candidate for '+name, exact=True).click()
            await page.wait_for_function("document.querySelector('.sg-refresh-review').getAttribute('aria-busy') === 'false'")
            self.assertEqual(self.context.STATE, before)
            if name == 'Alpha':
                await page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).check()
        self.assertTrue(await page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).is_checked())
        await self.apply(page)
        self.assertEqual(self.context.STATE['monsters'][0]['ac'], 18)
        self.assertEqual(self.context.STATE['monsters'][0]['hp'], before['monsters'][0]['hp'])
        self.assertEqual(self.context.STATE['monsters'][1], before['monsters'][1])
        self.context.hp_value_factory.assert_not_called()
        self.assertEqual(self.errors, [])

    async def test_real_sole_candidate_auto_resolution_requires_explicit_apply(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                for item in self.context.STATE['monsters']:
                    for field in FIELDS:
                        item.pop(field, None)
                await self.context.combatants_changed(monsters=True)
                before = self.snapshot()
                calls_before = len(self.calls)
                page = await self.open_page(width)
                await self.review(page, (0, 1))
                dialog = page.locator('.sg-refresh-review')
                self.assertEqual(await dialog.locator('select').count(), 0)
                self.assertEqual(await dialog.locator('input:checked').count(), 0)
                self.assertTrue(await page.get_by_role('button', name='Apply selected changes', exact=True).is_disabled())
                self.assertEqual(self.snapshot(), before)
                self.assertEqual(len(self.calls), calls_before + 1)
                self.assertEqual(self.calls[-1][0], '/api/monsters/refresh/preview')
                await page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).check()
                self.assertEqual(self.snapshot(), before)
                await self.apply(page)
                self.assertEqual(self.calls[-1][1]['selected'], {self.ids[0]: ['ac']})
                first = self.context.STATE['monsters'][0]
                self.assertEqual(first['ac'], 18)
                self.assertEqual(first['monster_source_url'], 'https://www.dndbeyond.com/monsters/example')
                self.assertIs(first['monster_source_legacy'], False)
                self.assertEqual(first['hp'], before[0]['monsters'][0]['hp'])
                self.assertEqual(self.context.STATE['monsters'][1], before[0]['monsters'][1])
                self.context.hp_value_factory.assert_not_called()
                self.hp_roll.assert_not_called()
                await page.close()
        self.assertEqual(self.errors, [])

    async def test_real_stale_review_is_rejected_without_apply_or_hp_generation(self):
        page = await self.open_page()
        await self.review(page)
        await page.get_by_role('checkbox', name='Armor Class for Alpha', exact=True).check()
        self.context.STATE['monsters'][0]['hp'] = 9
        before = copy.deepcopy(self.context.STATE)
        await page.get_by_role('button', name='Apply selected changes', exact=True).click()
        await page.get_by_role('status').filter(has_text='Encounter or source configuration changed').wait_for()
        self.assertEqual(self.context.STATE, before)
        self.assertEqual(self.calls[-1][2], 409)
        self.context.hp_value_factory.assert_not_called()
        self.assertTrue(await page.get_by_role('button', name='Apply selected changes', exact=True).is_disabled())
        self.assertEqual(self.errors, [])

    async def test_active_max_hp_reduction_conflict_is_atomic(self):
        item = self.context.STATE['monsters'][0]
        reduce_stat(item, 'max_hp', 2)
        await self.context.combatants_changed(monsters=True)
        before = self.snapshot()
        page = await self.open_page(375)
        await self.review(page)
        await page.get_by_role('checkbox', name='Max HP for Alpha', exact=True).check()
        await page.get_by_role('button', name='Apply selected changes', exact=True).click()
        await page.get_by_role('status').filter(has_text='Active Max HP reductions').wait_for()
        self.assertEqual(self.calls[-1][2], 409)
        self.assertEqual(self.snapshot(), before)
        self.assertTrue(await page.get_by_role('button', name='Apply selected changes', exact=True).is_disabled())
        self.assertEqual(self.errors, [])


if __name__ == '__main__':
    unittest.main()
