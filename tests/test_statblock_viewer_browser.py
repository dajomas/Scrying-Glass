"""022.10-022.12 statblock viewer in Chromium: tiles, safe rendering, references, keyboard, live updates.

The real page shell, CSS and scripts with an intercepted read API and WebSocket
(Playwright routing); no server, network or account. Real-server e2e is in
e2e/test_statblock_viewer.py.
"""
import copy
import json
import time
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'http://statblocks.test'


def fixture_snapshot():
    from test_fivetools_preparation import Fetcher
    from python.scrying_glass_fivetools_preparation import prepare_statblock
    value = prepare_statblock('Grave Wight Elder', 'TST', fetch=Fetcher(), deadline=time.monotonic() + 20).snapshot
    value['revision'] = 1
    return value


def hostile_snapshot():
    """Not model-valid on purpose: the renderer must stay safe even if storage were bypassed."""
    nodes = [
        dict(local_id='s', parent_local_id=None, definition_id=None, position=0, kind='section',
             label='<img src=x onerror="window.pwned=1">Traits'),
        dict(local_id='p', parent_local_id='s', definition_id=None, position=0, kind='paragraph'),
        dict(local_id='t', parent_local_id='p', definition_id=None, position=0, kind='text',
             text='<script>window.pwned=2</script><b>bold?</b>'),
        dict(local_id='l1', parent_local_id='p', definition_id=None, position=1, kind='link',
             url='javascript:window.pwned=3', text='js link'),
        dict(local_id='l2', parent_local_id='p', definition_id=None, position=2, kind='link',
             url='http://insecure.test/', text='http link'),
        dict(local_id='l3', parent_local_id='p', definition_id=None, position=3, kind='link',
             url='https://user:pw@evil.test/', text='credential link'),
        dict(local_id='l4', parent_local_id='p', definition_id=None, position=4, kind='link',
             url='https://ok.test/page', text='good link'),
        dict(local_id='x', parent_local_id='p', definition_id=None, position=5, kind='weird', text='unknown kind'),
    ]
    return dict(model_version=1, source_label='Hostile', subtitle='<i>subtitle</i>', completeness='partial',
                revision=4, provenance=[dict(position=0, role='selected', provider='file', entity_id='x',
                adapter_version='1', source_url='javascript:alert(1)',
                credits=[dict(position=0, attribution='<b>credit</b>', license_name='L',
                              license_url='http://bad.test/')])],
                facts=[dict(position=0, key='speed', label='Speed', display_text='<u>30 ft.</u>')],
                definitions=[], nodes=nodes,
                warnings=[dict(position=0, code='reference_unavailable', message='<em>missing</em>')])


def tile(ident, name, species='Grave Wight Elder', revision=1, **extra):
    value = dict(monster_id=ident, name=name, species=species, color='#336699', ac=14, hp=30, max_hp=45,
                 initiative_bonus=2, statblock_revision=revision, status='available' if revision else 'missing',
                 warnings=0)
    value.update(extra)
    return value


class ViewerBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from web_html.statblock_html import STATBLOCK_HTML
        cls.html = STATBLOCK_HTML
        cls.snapshot = fixture_snapshot()

    def setUp(self):
        self.playwright = sync_playwright().start()
        self.addCleanup(self.playwright.stop)
        try:
            self.browser = self.playwright.chromium.launch(headless=True)
        except Exception:
            self.browser = self.playwright.chromium.launch(headless=True, executable_path='/usr/bin/google-chrome',
                                                           args=['--no-sandbox'])
        self.addCleanup(self.browser.close)
        self.page = self.browser.new_page(viewport={'width': 1000, 'height': 900})
        self.page.set_default_timeout(5000)
        self.errors, self.fetches, self.sockets = [], [], []
        self.statblocks = {'a': self.snapshot, 'b': self.snapshot, 'c': self.snapshot, 'd': self.snapshot,
                           'e': self.snapshot, 'h': hostile_snapshot()}
        self.status = {}
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.route(ORIGIN + '/', lambda route: route.fulfill(content_type='text/html', body=self.html))
        self.page.route(ORIGIN + '/static/**', self.static)
        self.page.route(ORIGIN + '/api/statblocks/monsters/**', self.monster)
        self.page.route_web_socket(ORIGIN.replace('http', 'ws') + '/ws', lambda ws: self.sockets.append(ws))
        self.page.goto(ORIGIN + '/')
        self.page.wait_for_function('window.ScryingStatblockViewer !== undefined')
        for _ in range(100):
            if self.sockets:
                break
            self.page.wait_for_timeout(20)
        self.state = dict(campaign_id='1', encounter_token='enc', projection_revision=1, monsters=[],
                          tiles=[tile('a', 'Wight A'), tile('b', 'Wight B'), tile('c', 'Thrall', 'Grave Thrall', 0),
                                 tile('d', 'Wight D'), tile('e', 'Wight E')])
        self.send()

    def static(self, route):
        path = ROOT / 'static' / route.request.url.split('/static/')[1].split('?')[0]
        route.fulfill(path=str(path)) if path.is_file() else route.fulfill(status=404, body='')

    def monster(self, route):
        ident = route.request.url.split('/monsters/')[1].split('?')[0]
        self.fetches.append(route.request.url)
        if ident in self.status:
            route.fulfill(status=self.status[ident], json={'code': 'x', 'message': 'Access ended for the test.', 'items': []})
            return
        snapshot = copy.deepcopy(self.statblocks[ident])
        known = route.request.url.split('known_revision=')[1] if 'known_revision=' in route.request.url else None
        body = {'monster_id': ident, 'encounter_token': self.state['encounter_token'],
                'statblock_revision': snapshot['revision'], 'status': snapshot['completeness'], 'live': {}}
        if known is not None and int(known) == snapshot['revision']:
            body['unchanged'] = True
        else:
            body['statblock'] = snapshot
        route.fulfill(json=body)

    def send(self, message=None):
        self.sockets[-1].send(json.dumps(message or {'type': 'state', 'state': self.state}))
        self.page.wait_for_timeout(50)

    def toggle(self, name):
        return self.page.get_by_role('button', name=name)

    def expanded(self):
        return self.page.locator('.sb-tile.sb-expanded').all_inner_texts()

    def wait_statblock(self):
        self.page.locator('.sb-expanded .sb-statblock').wait_for()

    def test_tiles_follow_membership_order_with_colour_and_states(self):
        names = self.page.locator('.sb-toggle .sb-name').all_inner_texts()
        self.assertEqual(names, ['Wight A', 'Wight B', 'Thrall', 'Wight D', 'Wight E'])
        self.assertEqual(self.page.locator('#status').inner_text(), '5 monsters in battle.')
        colour = self.page.locator('.sb-tile').first.evaluate("e => getComputedStyle(e).borderLeftColor")
        self.assertEqual(colour, 'rgb(51, 102, 153)')
        self.assertEqual(self.page.locator('.sb-tile[data-id="c"] .sb-badge').inner_text(), 'No statblock')
        self.state['tiles'] = []
        self.send()
        self.assertEqual(self.page.locator('#status').inner_text(), 'No monsters in battle.')
        self.assertEqual(self.errors, [])

    def test_one_expanded_tile_and_collapse_paths(self):
        self.toggle('Wight A').click()
        self.wait_statblock()
        self.assertEqual(self.toggle('Wight A').get_attribute('aria-expanded'), 'true')
        self.page.locator('.sb-expanded .sb-statblock p').first.click()  # text clicks never collapse
        self.page.locator('.sb-expanded .sb-statblock').dblclick()
        self.assertEqual(len(self.expanded()), 1)
        self.toggle('Wight B').click()
        self.wait_statblock()
        self.assertEqual(self.page.locator('.sb-tile.sb-expanded').get_attribute('data-id'), 'b')
        self.assertEqual(self.page.locator('.sb-tile.sb-expanded').count(), 1)
        self.toggle('Wight B').click()
        self.assertEqual(self.page.locator('.sb-tile.sb-expanded').count(), 0)
        self.toggle('Wight D').focus()
        self.page.keyboard.press('Enter')
        self.wait_statblock()
        self.page.locator('.sb-expanded summary').first.focus()
        self.page.keyboard.press('Escape')
        self.assertEqual(self.page.locator('.sb-tile.sb-expanded').count(), 0)
        self.assertEqual(self.page.evaluate('document.activeElement.closest(".sb-tile").dataset.id'), 'd')
        self.toggle('Thrall').click()
        self.assertIn('No statblock is saved', self.page.locator('.sb-expanded .sb-panel').inner_text())
        self.assertEqual(self.errors, [])

    def test_sg_values_override_and_species_placeholders_follow_live_species(self):
        self.toggle('Wight A').click()
        self.wait_statblock()
        block = self.page.locator('.sb-expanded .sb-statblock')
        self.assertEqual(block.locator('[data-live="name"]').inner_text(), 'Wight A')
        self.assertEqual(block.locator('[data-live="ac"]').inner_text(), '14')
        self.assertEqual(block.locator('[data-live="hp"]').inner_text(), '30 / 45')
        self.assertEqual(block.locator('[data-live="initiative_bonus"]').inner_text(), '+2')
        facts = block.locator('.sb-facts').first.inner_text()
        self.assertNotIn('Armor Class', facts)
        self.assertEqual(block.locator('.sb-species-name').all_inner_texts(), ['Grave Wight Elder'])
        before = len(self.fetches)
        self.state['tiles'][0].update(species='Frost Wight', hp=12, name='Renamed')
        self.send()
        self.assertEqual(block.locator('.sb-species-name').all_inner_texts(), ['Frost Wight'])
        self.assertEqual(block.locator('[data-live="hp"]').inner_text(), '12 / 45')
        self.assertEqual(self.toggle('Renamed').count(), 1)
        self.assertEqual(len(self.fetches), before)  # live values never refetch content
        self.statblocks['a'] = dict(copy.deepcopy(self.snapshot), revision=2, source_label='Changed')
        self.state['tiles'][0]['statblock_revision'] = 2
        self.send(); self.send()
        self.page.wait_for_timeout(100)
        self.assertEqual(len(self.fetches), before + 1)
        self.assertIn('known_revision=1', self.fetches[-1])

    def test_statblock_layout_follows_the_published_statblocks(self):
        self.toggle('Wight A').click()
        self.wait_statblock()
        block = self.page.locator('.sb-expanded .sb-statblock')
        core = block.locator('.sb-live').inner_text()
        for label in ('Armor Class', 'Hit Points', 'Initiative', 'Speed'):
            self.assertIn(label, core)
        rows = block.locator('.sb-abilities tbody tr')
        self.assertEqual(rows.count(), 6)
        self.assertEqual(rows.first.locator('th, td').all_inner_texts(), ['STR', '15', '+2', '+2'])
        self.assertEqual(block.locator('.sb-abilities thead').first.inner_text().split(), ['MOD', 'SAVE'])
        properties = block.locator('.sb-facts').first.inner_text()
        self.assertNotIn('Speed', properties)
        self.assertNotIn('Strength', properties)
        # Wide statblocks: the sections sit in a second column beside the statistics.
        stats = block.locator('.sb-stats').bounding_box()
        sections = block.locator('.sb-sections').bounding_box()
        self.assertGreater(sections['x'], stats['x'] + stats['width'] - 1)
        self.assertLess(abs(sections['y'] - stats['y']), 2)
        self.page.set_viewport_size({'width': 600, 'height': 900})
        stats = block.locator('.sb-stats').bounding_box()
        sections = block.locator('.sb-sections').bounding_box()
        self.assertGreaterEqual(sections['y'], stats['y'] + stats['height'] - 1)

    def test_saving_throws_fill_the_save_column(self):
        snapshot = copy.deepcopy(self.snapshot)
        snapshot['facts'] = [row for row in snapshot['facts'] if row['key'] != 'saving_throws']
        snapshot['facts'].append(dict(position=len(snapshot['facts']), key='saving_throws', label='Saving Throws',
                                      display_text='Con +6, Wis +4'))
        self.statblocks['a'] = snapshot
        self.toggle('Wight A').click()
        self.wait_statblock()
        block = self.page.locator('.sb-expanded .sb-statblock')
        saves = dict(zip(block.locator('.sb-abilities tbody th').all_inner_texts(),
                         block.locator('.sb-abilities tbody td.sb-save').all_inner_texts()))
        self.assertEqual((saves['CON'], saves['WIS'], saves['STR']), ('+6', '+4', '+2'))
        self.assertNotIn('Saving Throws', block.locator('.sb-facts').first.inner_text())

    def test_references_open_existing_definitions_without_nesting(self):
        self.toggle('Wight A').click()
        self.wait_statblock()
        block = self.page.locator('.sb-expanded .sb-statblock')
        details = block.locator('.sb-ref-details')
        self.assertEqual(details.count(), len(self.snapshot['definitions']))
        self.assertTrue(all(not d for d in details.evaluate_all('ds => ds.map(d => d.open)')))
        refs = block.locator(':scope > :not(.sb-references) button.sb-ref')
        refs.first.click()
        self.assertEqual(details.evaluate_all('ds => ds.filter(d => d.open).length'), 1)
        block.locator('.sb-ref-details summary').nth(2).click()
        self.assertEqual(details.evaluate_all('ds => ds.filter(d => d.open).length'), 2)
        holder = block.locator('.sb-ref-details:has(button.sb-ref)').first
        if not holder.evaluate('d => d.open'):
            holder.locator('summary').click()
        target = holder.locator('button.sb-ref').first.get_attribute('data-ref')
        holder.locator('button.sb-ref').first.click()  # navigates to the existing definition, never a copy
        self.assertTrue(block.locator('#' + target).evaluate('d => d.open'))
        self.assertEqual(self.page.evaluate('document.activeElement.parentElement.id'), target)
        self.assertEqual(details.count(), len(self.snapshot['definitions']))
        self.assertEqual(block.locator('.sb-ref-details .sb-ref-details').count(), 0)
        self.assertEqual(len(self.expanded()), 1)
        self.assertGreater(block.locator('.sb-credits a').count(), 0)

    def test_hostile_content_stays_text(self):
        self.state['tiles'].append(tile('h', '<img src=x onerror="window.pwned=9">', revision=4))
        self.send()
        self.page.locator('.sb-tile[data-id="h"] .sb-toggle').click()
        self.wait_statblock()
        block = self.page.locator('.sb-expanded .sb-statblock')
        self.assertIsNone(self.page.evaluate('window.pwned'))
        self.assertEqual(self.page.locator('.sb-expanded img, .sb-expanded script, .sb-tile img').count(), 0)
        self.assertIn('<script>window.pwned=2</script><b>bold?</b>', block.inner_text())
        hrefs = block.locator('a').evaluate_all('as => as.map(a => a.getAttribute("href"))')
        self.assertEqual(hrefs, ['https://ok.test/page'])
        self.assertEqual(block.locator('a').first.get_attribute('rel'), 'noopener noreferrer nofollow')
        self.assertIn('Partial statblock', block.inner_text())
        self.assertIn('<u>30 ft.</u>', block.inner_text())
        self.assertIn('unknown kind', block.inner_text())

    def test_grid_arrow_keys_roving_focus_and_removed_tiles(self):
        self.page.set_viewport_size({'width': 900, 'height': 900})  # three columns of 15rem tiles
        columns = self.page.evaluate("getComputedStyle(document.querySelector('#tiles')).gridTemplateColumns.split(' ').length")
        self.assertEqual(columns, 3)
        self.assertEqual(self.page.locator('.sb-toggle[tabindex="0"]').count(), 1)
        self.toggle('Wight A').focus()
        def at():
            return self.page.evaluate('document.activeElement.closest(".sb-tile").dataset.id')
        for key, expected in (('ArrowRight', 'b'), ('ArrowDown', 'e'), ('ArrowLeft', 'd'), ('ArrowUp', 'a'),
                              ('End', 'e'), ('ArrowDown', 'e'), ('Home', 'a'), ('ArrowLeft', 'a')):
            self.page.keyboard.press(key)
            self.assertEqual(at(), expected, key)
        self.toggle('Thrall').focus()
        self.page.keyboard.press('ArrowDown')  # incomplete next row: nearest tile below
        self.assertEqual(at(), 'e')
        self.assertEqual(self.page.locator('.sb-toggle[tabindex="0"]').count(), 1)
        self.state['tiles'] = [t for t in self.state['tiles'] if t['monster_id'] != 'e']
        self.send()
        self.assertEqual(at(), 'd')  # focus stays in the grid on a neighbour
        self.page.set_viewport_size({'width': 420, 'height': 900})
        self.page.keyboard.press('ArrowUp')
        self.assertEqual(at(), 'c')  # one column: up is the previous tile

    def test_revocation_campaign_change_and_access_errors_clear_content(self):
        self.toggle('Wight A').click()
        self.wait_statblock()
        self.send({'type': 'revoked', 'code': 'campaign_forbidden', 'message': 'This campaign is not assigned to you.'})
        self.assertEqual(self.page.locator('.sb-tile').count(), 0)
        self.assertEqual(self.page.locator('#status').inner_text(), 'This campaign is not assigned to you.')
        self.send()
        self.toggle('Wight A').click()
        self.wait_statblock()
        other = dict(self.state, campaign_id='2', tiles=[tile('z', 'Other campaign monster')])
        self.send({'type': 'state', 'state': other})
        self.assertEqual(self.page.locator('.sb-toggle .sb-name').all_inner_texts(), ['Other campaign monster'])
        self.assertEqual(self.page.locator('.sb-statblock').count(), 0)
        self.send()
        self.status['b'] = 403
        self.toggle('Wight B').click()
        self.page.wait_for_function("document.querySelectorAll('.sb-tile').length === 0")
        self.assertIn('Access ended', self.page.locator('#status').inner_text())

    def test_stale_responses_are_ignored(self):
        gate = []
        def slow(route):
            gate.append(route)
        self.page.unroute(ORIGIN + '/api/statblocks/monsters/**')
        self.page.route(ORIGIN + '/api/statblocks/monsters/**', slow)
        self.toggle('Wight A').click()
        self.page.wait_for_function('true')
        for _ in range(50):
            if gate:
                break
            self.page.wait_for_timeout(20)
        self.toggle('Wight A').click()  # collapsed before the response
        self.page.unroute(ORIGIN + '/api/statblocks/monsters/**')
        self.page.route(ORIGIN + '/api/statblocks/monsters/**', self.monster)
        self.monster(gate[0])
        self.page.wait_for_timeout(100)
        self.assertEqual(self.page.locator('.sb-statblock').count(), 0)
        self.assertEqual(self.errors, [])


if __name__ == '__main__':
    unittest.main()
