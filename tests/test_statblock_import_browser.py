"""022.13/022.14 Admin statblock import UI in Chromium with intercepted statblock APIs.

Real scripts (statblocks-render, monster-statblock-common/edit/bulk, feedback) on a
minimal Admin fixture page; the fake server below mimics the 022.08 routes. Not an
authenticated server test (see test_statblock_import_http.py and e2e).
"""
import copy
import json
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright
from feedback_browser_fixture import install_feedback

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = dict(model_version=1, source_label='Goblin', subtitle='Small Humanoid', completeness='available',
                provenance=[dict(position=0, role='selected', provider='5e.tools', entity_id='monster|Goblin|MM',
                                 adapter_version='1', credits=[])],
                facts=[dict(position=0, key='speed', label='Speed', display_text='30 ft.')], definitions=[],
                nodes=[dict(local_id='p', parent_local_id=None, definition_id=None, position=0, kind='paragraph'),
                       dict(local_id='t', parent_local_id='p', definition_id=None, position=0, kind='text',
                            text='Nimble Escape.')],
                warnings=[], content_digest='0' * 64)
MONSTERS = [dict(id='a', name='Goblin 1', monster_species='Goblin', ac=15, hp=7, max_hp=7, original_hp=7,
                 color='#842029', initiative=None, ally=False, initiative_bonus=2),
            dict(id='b', name='Goblin 2', monster_species='Goblin', ac=15, hp=7, max_hp=7, original_hp=7,
                 color='#842029', initiative=None, ally=False, initiative_bonus=2),
            dict(id='c', name='Nameless', monster_species='', ac=10, hp=3, max_hp=3, original_hp=3,
                 color='#842029', initiative=None, ally=False, initiative_bonus=0)]


class FakeServer:
    def __init__(self, page):
        self.page, self.calls, self.jobs, self.applies, self.deleted = page, [], {}, [], []
        self.revisions = {'a': 0, 'b': 3, 'c': 0}
        self.collected, self.decisions = [], []
        self.shown = []
        self.fail_prepare, self.fail_apply = set(), None
        self.pending_polls = 1
        page.route('**/api/statblocks/**', self.handle)

    def handle(self, route):
        request, url = route.request, route.request.url
        path = url.split('/api/statblocks/')[1].split('?')[0]
        self.calls.append((request.method, path))
        if path == 'state':
            route.fulfill(json={'campaign_id': '1', 'encounter_token': 'enc', 'projection_revision': 1, 'tiles': [],
                                'monsters': [{'monster_id': k, 'statblock_revision': v,
                                              'status': 'available' if v else 'missing', 'warnings': 0}
                                             for k, v in self.revisions.items()]})
        elif path == 'collected':
            route.fulfill(json={'campaign_id': '1', 'encounter_token': 'enc', 'items': self.collected})
        elif path.startswith('collected/'):
            ident = path.split('/')[1]
            body = json.loads(request.post_data)
            self.decisions.append((ident, body))
            if body['expected_statblock_revision'] == 99:
                route.fulfill(status=409, json={'code': 'stale_revision', 'message': 'The statblock changed meanwhile.',
                                                'items': []})
                return
            self.collected = [item for item in self.collected if item['collected_id'] != ident]
            route.fulfill(json={'collected_id': ident, 'decision': body['decision']})
        elif path.startswith('monsters/'):
            ident = path.split('/')[1]
            body = {'monster_id': ident, 'encounter_token': 'enc', 'live': {}, 'statblock_revision': self.revisions[ident],
                    'status': 'available' if self.revisions[ident] else 'missing'}
            if self.revisions[ident]:
                body.update(statblock=copy.deepcopy(SNAPSHOT), source={'provider': '5e.tools', 'source_code': 'MM'})
            self.shown.append(ident)
            route.fulfill(json=body)
        elif path == 'discover':
            body = json.loads(request.post_data)
            self.discovered = body
            rows = []
            for ident in body['monster_ids']:
                saved = {m['id']: m['monster_species'] for m in MONSTERS}.get(ident, 'Goblin')
                species = body.get('species') or saved
                candidates = [] if not species else [
                    {'candidate_id': f'{ident}-orig', 'provider': '5e.tools', 'label': species, 'source': 'MM', 'original': True},
                    {'candidate_id': f'{ident}-o5e', 'provider': 'Open5e', 'label': species, 'document': 'SRD 5.1'}]
                rows.append({'monster_id': ident, 'species': species, 'status': 'ok' if species else 'no_species',
                             'statblock_revision': self.revisions[ident], 'candidates': candidates,
                             'providers': [{'provider': 'D&D Beyond', 'status': 'error', 'code': 'provider_unavailable'}]})
            route.fulfill(json={'campaign_id': '1', 'encounter_token': 'enc', 'complete': False, 'monsters': rows})
        elif path == 'prepare':
            if 'multipart' in (request.headers.get('content-type') or ''):
                body = {'monster_id': 'a' if b'name="monster_id"\r\n\r\na' in request.post_data_buffer else 'b',
                        'candidate_id': 'file'}
            else:
                body = json.loads(request.post_data)
            job = 'job-%d' % (len(self.jobs) + 1)
            failed = body['candidate_id'] in self.fail_prepare
            self.jobs[job] = dict(body, polls=0, failed=failed)
            route.fulfill(status=202, json={'job_id': job, 'status': 'queued', 'monster_id': body['monster_id']})
        elif path.startswith('jobs/'):
            job = self.jobs[path.split('/')[1]]
            ident = path.split('/')[1]
            if request.method == 'DELETE':
                self.deleted.append(ident)
                route.fulfill(json={'job_id': ident, 'status': 'cancelled'})
                return
            job['polls'] += 1
            if job['polls'] <= self.pending_polls:
                route.fulfill(json={'job_id': ident, 'status': 'running'})
            elif job['failed']:
                route.fulfill(json={'job_id': ident, 'status': 'failed', 'error': {'code': 'not_found',
                                                                                    'message': 'The source record was not found.'}})
            else:
                preview = copy.deepcopy(SNAPSHOT)
                route.fulfill(json={'job_id': ident, 'status': 'completed', 'selection_id': 'sel-' + ident,
                                    'expires_at': '2026-11-17T17:00:00Z', 'monster_id': job['monster_id'],
                                    'source': {'provider': '5e.tools', 'source_code': 'MM'}, 'source_label': 'Goblin',
                                    'completeness': 'available', 'warnings': [], 'preview': preview})
        elif path == 'apply':
            body = json.loads(request.post_data)
            self.applies.append(body)
            if self.fail_apply and len(self.applies) == self.fail_apply:
                route.fulfill(status=409, json={'code': 'apply_rejected', 'message': 'No statblocks were changed.',
                                                'items': [{'monster_id': body['items'][0]['monster_id'],
                                                           'code': 'stale_revision', 'message': 'The statblock changed.'}]})
                return
            route.fulfill(json={'operation_id': body['operation_id'], 'applied': [
                {'monster_id': item['monster_id'], 'statblock_revision': item['expected_statblock_revision'] + 1}
                for item in body['items']]})
        else:
            route.fulfill(status=404, json={'code': 'x', 'message': 'unknown', 'items': []})


class ImportBrowserTests(unittest.TestCase):
    def setUp(self):
        runtime = sync_playwright().start()
        self.addCleanup(runtime.stop)
        try:
            browser = runtime.chromium.launch(headless=True)
        except Exception:
            browser = runtime.chromium.launch(headless=True, executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        self.addCleanup(browser.close)
        self.page = browser.new_page(viewport={'width': 1280, 'height': 900})
        self.page.set_default_timeout(8000)
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.route('http://fixture.test/', lambda route: route.fulfill(content_type='text/html', body=(
            '<select id="monsterBulkAction"><option value="">Actions</option><option value="remove">Remove</option></select>'
            '<div id="editModal" hidden><form id="editForm" class="edit-form"></form></div>')))
        self.server = FakeServer(self.page)
        self.page.goto('http://fixture.test/')
        install_feedback(self.page)
        self.page.add_script_tag(content="""
            let latest = {monsters: %s};
            let editing = null, chosen = [];
            const editModal = document.querySelector('#editModal');
            function selectedIds() {return chosen;}
            async function runBulkAction() {window.legacyBulk = true;}
            async function load() {window.reloaded = (window.reloaded || 0) + 1;}
            function closeEdit() {editModal.hidden = true; editing = null; document.querySelector('#editForm').innerHTML = '';}
            function openEdit(kind, id) {
                editing = {kind, id};
                const m = latest.monsters.find(x => x.id === id);
                document.querySelector('#editForm').innerHTML =
                    `<label>Name <input name="name" value="${m.name}"></label>` +
                    `<label>Monster species <input name="monster_species" value="${m.monster_species}"></label>` +
                    `<label>AC <input name="ac" type="number" value="${m.ac}"></label>` +
                    `<label>HP <input name="hp" type="number" value="${m.hp}"></label>` +
                    `<label>Max HP <input name="max_hp" type="number" value="${m.max_hp}"></label>` +
                    `<label>Initiative <input name="initiative" type="number" value=""></label>` +
                    `<label>Ally <select name="ally"><option value="false">No</option><option value="true">Yes</option></select></label>` +
                    '<div class="actions"><button>Save monster</button><button type="button" id="cancelEdit">Cancel</button></div>';
                editModal.hidden = false;
            }
        """ % json.dumps(MONSTERS))
        for name in ('glass-theme.css', 'statblocks.css', 'monster-statblock-import.css'):
            self.page.add_style_tag(content=(ROOT / 'static' / name).read_text())
        for name in ('statblocks-render.js', 'monster-statblock-common.js', 'monster-statblock-edit.js',
                     'monster-statblock-bulk.js', 'monster-statblock-collected.js'):
            self.page.add_script_tag(content=(ROOT / 'static' / name).read_text())

    def form_data(self):
        return self.page.evaluate("Object.fromEntries(new FormData(document.querySelector('#editForm')))")

    # -- Edit Monster ---------------------------------------------------------------
    def open_edit(self, ident='a'):
        self.page.evaluate(f"openEdit('monsters', '{ident}')")
        self.page.locator('.monster-statblock-status').filter(has_text='Current:').wait_for()

    def test_edit_find_preview_and_stage_for_save(self):
        self.open_edit()
        self.assertIn('No statblock', self.page.locator('.monster-statblock-status').inner_text())
        self.page.fill('input[name="monster_species"]', 'Goblin boss')  # searched with the edited species
        self.page.get_by_role('button', name='Find statblock').click()
        dialog = self.page.get_by_role('dialog', name='Choose a statblock for Goblin boss')
        self.assertIn('D&D Beyond: not searched', dialog.inner_text())
        self.assertEqual(self.server.discovered['species'], 'Goblin boss')
        dialog.get_by_role('button', name='Goblin boss · 5e.tools · MM — original source').click()
        review = self.page.get_by_role('dialog', name='Statblock: Goblin boss · 5e.tools · MM — original source')
        review.get_by_role('button', name='Use this statblock').wait_for()
        self.assertIn('Nimble Escape.', review.inner_text())
        self.assertEqual(review.locator('[data-live="name"]').inner_text(), 'Goblin 1')
        self.assertEqual(review.locator('.sb-subtitle').inner_text(), 'Goblin boss — Small Humanoid')
        review.get_by_role('button', name='Use this statblock').click()
        data = self.form_data()
        self.assertEqual((data['statblock_selection_id'], data['statblock_expected_revision']), ('sel-job-1', '0'))
        self.assertTrue(data['statblock_operation_id'])
        self.assertEqual(json.loads(data['expected_values']), {'monster_species': 'Goblin'})
        self.assertIn('Save monster to apply', self.page.locator('.monster-statblock-status').inner_text())
        self.assertNotIn('Statblock: ', [d for d in self.page.locator('dialog').all_inner_texts()])
        self.page.get_by_role('button', name='Keep current statblock').click()
        self.assertEqual(self.form_data()['statblock_selection_id'], '')
        self.page.wait_for_timeout(300)
        self.assertIn('job-1', self.server.deleted)
        self.assertEqual(self.errors, [])

    def test_show_statblock_shows_the_staged_or_saved_statblock_with_form_values(self):
        self.open_edit('a')
        show = self.page.get_by_role('button', name='Show statblock')
        self.assertTrue(show.is_disabled())  # nothing saved, nothing staged
        self.page.get_by_role('button', name='Find statblock').click()
        self.page.get_by_role('dialog', name='Choose a statblock for Goblin').get_by_role(
            'button', name='Goblin · 5e.tools · MM — original source').click()
        self.page.get_by_role('button', name='Use this statblock').click()
        self.page.fill('input[name="name"]', 'Goblin chief')
        show.click()
        dialog = self.page.get_by_role('dialog', name='Statblock: Goblin chief')
        self.assertIn('not saved until you save the monster', dialog.inner_text())
        self.assertEqual(dialog.locator('[data-live="name"]').inner_text(), 'Goblin chief')
        dialog.get_by_role('button', name='Close').click()
        self.assertEqual(self.page.locator('dialog').count(), 0)
        self.assertEqual(self.server.shown, [])  # the staged preview needs no request
        self.page.get_by_role('button', name='Keep current statblock').click()
        self.assertTrue(show.is_disabled())
        self.page.evaluate('closeEdit()')
        self.open_edit('b')
        show.click()
        dialog = self.page.get_by_role('dialog', name='Statblock: Goblin 2')
        self.assertIn('Saved statblock (revision 3)', dialog.inner_text())
        self.assertIn('Nimble Escape.', dialog.inner_text())
        self.assertEqual(self.server.shown, ['b'])
        self.page.keyboard.press('Escape')
        self.assertEqual(self.page.locator('dialog').count(), 0)
        self.assertEqual(self.errors, [])

    def collected(self, ident, name, reasons, revision, current=None):
        return {'collected_id': ident, 'monster_id': ident, 'name': name, 'species': 'Goblin', 'reasons': reasons,
                'statblock_revision': revision, 'current_source_label': current, 'provider': '5e.tools',
                'source_label': 'Goblin', 'completeness': 'available', 'preview': copy.deepcopy(SNAPSHOT),
                'live': {'name': name, 'species': 'Goblin', 'ac': 15, 'hp': 7, 'max_hp': 7, 'initiative_bonus': 2},
                'expires_at': '2026-11-20T21:00:00Z'}

    def test_collected_statblocks_are_replaced_or_kept_only_on_confirmation(self):
        self.server.collected = [self.collected('c1', 'Goblin 1', ['has_statblock'], 2, 'Chosen in Edit'),
                                 self.collected('c2', 'Goblin 2', ['changed'], 0)]
        self.page.evaluate('window.scryingCollectedStatblocks.check()')
        dialog = self.page.get_by_role('dialog', name='Replace statblocks?')
        first = dialog.get_by_role('region', name='Goblin 1')
        self.assertIn('already has a different statblock', first.inner_text())
        self.assertIn('Chosen in Edit (revision 2)', first.inner_text())
        self.assertIn('species or source was edited', dialog.get_by_role('region', name='Goblin 2').inner_text())
        first.get_by_text('Show the collected statblock').click()
        self.assertEqual(first.locator('[data-live="name"]').inner_text(), 'Goblin 1')
        first.get_by_role('button', name='Replace').click()
        self.page.wait_for_function('window.reloaded >= 1')
        self.assertEqual(self.server.decisions[0], ('c1', {'decision': 'replace', 'expected_statblock_revision': 2}))
        dialog.get_by_role('region', name='Goblin 2').get_by_role('button', name='Keep current').click()
        self.page.locator('dialog.monster-statblock-collected').wait_for(state='detached')
        self.assertEqual(self.server.decisions[1], ('c2', {'decision': 'keep', 'expected_statblock_revision': 0}))
        self.assertEqual(self.errors, [])

    def test_decide_later_and_a_changed_statblock(self):
        self.server.collected = [self.collected('c1', 'Goblin 1', ['has_statblock'], 99, 'Chosen in Edit')]
        self.page.evaluate('window.scryingCollectedStatblocks.check()')
        dialog = self.page.get_by_role('dialog', name='Replace statblocks?')
        dialog.get_by_role('button', name='Replace').click()  # the statblock changed since the question
        self.page.locator('dialog.monster-statblock-collected').wait_for(state='detached')
        self.server.collected = [self.collected('c3', 'Goblin 3', ['changed'], 0)]
        self.page.evaluate('window.scryingCollectedStatblocks.check()')
        dialog.get_by_role('button', name='Decide later').click()
        self.assertEqual(self.page.locator('dialog').count(), 0)
        self.page.evaluate('window.scryingCollectedStatblocks.check()')
        self.page.wait_for_timeout(300)
        self.assertEqual(self.page.locator('dialog').count(), 0)  # not asked again until the next add or reload
        self.assertEqual([ident for ident, _ in self.server.decisions], ['c1'])
        self.assertEqual(self.errors, [])

    def test_edit_statblock_controls_are_bottom_aligned(self):
        self.open_edit('b')
        bottoms = self.page.evaluate("""[...document.querySelectorAll('.monster-statblock-actions > :not([hidden])')]
            .map(e => Math.round((e.matches('label') ? e.querySelector('input') : e).getBoundingClientRect().bottom))""")
        self.assertEqual(len(bottoms), 3)
        self.assertEqual(len(set(bottoms)), 1, bottoms)

    def test_edit_cancel_paths_discard_unconfirmed_and_staged_choices(self):
        self.open_edit('b')
        self.page.get_by_role('button', name='Find statblock').click()
        dialog = self.page.get_by_role('dialog', name='Choose a statblock for Goblin')
        dialog.get_by_role('button', name='Cancel').click()
        self.assertEqual(self.form_data()['statblock_selection_id'], '')
        self.server.pending_polls = 1000
        self.page.get_by_role('button', name='Find statblock').click()
        self.page.get_by_role('dialog', name='Choose a statblock for Goblin').get_by_role(
            'button', name='Goblin · Open5e · SRD 5.1').click()
        preparing = self.page.get_by_role('dialog', name='Statblock: Goblin · Open5e · SRD 5.1')
        preparing.get_by_text('Preparing the statblock').wait_for()
        preparing.get_by_role('button', name='Cancel').click()
        self.page.wait_for_function("document.querySelectorAll('dialog').length === 0")
        self.page.wait_for_timeout(500)
        self.assertIn('job-1', self.server.deleted)
        self.assertEqual(self.form_data()['statblock_selection_id'], '')
        self.server.pending_polls = 1
        self.page.get_by_role('button', name='Find statblock').click()
        self.page.get_by_role('dialog', name='Choose a statblock for Goblin').get_by_role(
            'button', name='Goblin · 5e.tools · MM — original source').click()
        self.page.get_by_role('button', name='Use this statblock').click()
        self.assertEqual(self.form_data()['statblock_expected_revision'], '3')
        self.page.evaluate('closeEdit()')
        self.page.wait_for_timeout(300)
        self.assertIn('job-2', self.server.deleted)
        self.assertEqual(self.errors, [])

    def test_edit_failures_and_file_upload(self):
        self.open_edit()
        self.server.fail_prepare.add('a-o5e')
        self.page.get_by_role('button', name='Find statblock').click()
        self.page.get_by_role('dialog', name='Choose a statblock for Goblin').get_by_role(
            'button', name='Goblin · Open5e · SRD 5.1').click()
        failed = self.page.get_by_role('dialog', name='Statblock: Goblin · Open5e · SRD 5.1')
        failed.get_by_text('The source record was not found.').wait_for()
        failed.get_by_role('button', name='Close').click()
        self.assertEqual(self.form_data()['statblock_selection_id'], '')
        self.page.set_input_files('.monster-statblock-upload input', files=[
            {'name': 'goblin.monster', 'mimeType': 'application/json', 'buffer': b'{"name":"Goblin"}'}])
        self.page.get_by_role('dialog', name='Statblock: goblin.monster').get_by_role('button', name='Use this statblock').click()
        self.assertTrue(self.form_data()['statblock_selection_id'].startswith('sel-'))
        self.assertNotIn('', [key for key in self.form_data() if key == ''])
        self.assertEqual(self.errors, [])

    # -- Bulk --------------------------------------------------------------------------
    def start_bulk(self, ids):
        self.page.evaluate(f"chosen = {json.dumps(ids)}; setTimeout(() => runBulkAction('monsters', 'load-statblocks')); void 0")
        dialog = self.page.locator('dialog.monster-statblock-bulk')
        dialog.wait_for()
        self.page.wait_for_function("document.querySelector('dialog.monster-statblock-bulk').getAttribute('aria-busy') === 'false'")
        return dialog

    def row(self, ident):
        return self.page.locator(f'.monster-statblock-row[data-monster-id="{ident}"]')

    def test_bulk_independent_rows_keep_current_and_atomic_apply(self):
        self.assertEqual(self.page.locator('#monsterBulkAction option[value="load-statblocks"]').inner_text(), 'Load statblocks')
        dialog = self.start_bulk(['a', 'b', 'c'])
        self.assertEqual(self.server.calls.count(('POST', 'discover')), 1)
        self.assertIn('No species to search for.', self.row('c').inner_text())
        self.assertIn('D&D Beyond: not searched', self.row('a').inner_text())
        self.assertTrue(dialog.get_by_role('button', name='Apply statblocks').is_disabled())
        self.row('a').get_by_label('Statblock for Goblin 1').select_option(label='Goblin · 5e.tools · MM — original source')
        self.row('b').get_by_label('Statblock for Goblin 2').select_option(label='Goblin · Open5e · SRD 5.1')
        dialog.get_by_role('button', name='Apply statblocks (2)').wait_for()
        self.row('a').locator('summary').click()
        self.row('a').get_by_text('Nimble Escape.').wait_for()
        self.row('b').get_by_label('Statblock for Goblin 2').select_option(label='Keep current')
        self.page.wait_for_timeout(300)
        self.assertEqual(self.server.deleted, ['job-2'])  # the released Goblin 2 preparation
        dialog.get_by_role('button', name='Apply statblocks (1)').click()
        self.page.wait_for_function("!document.querySelector('dialog.monster-statblock-bulk')")
        self.assertEqual(len(self.server.applies), 1)
        self.assertEqual(self.server.applies[0]['items'],
                         [{'monster_id': 'a', 'expected_statblock_revision': 0, 'selection_id': 'sel-job-1'}])
        self.assertEqual(self.page.evaluate('window.reloaded'), 1)
        self.assertEqual(self.errors, [])

    def test_bulk_failures_retry_and_rejected_batches_are_reported(self):
        self.server.fail_prepare.add('b-o5e')
        self.server.fail_apply = 1
        dialog = self.start_bulk(['a', 'b'])
        self.row('a').get_by_label('Statblock for Goblin 1').select_option(label='Goblin · Open5e · SRD 5.1')
        self.row('b').get_by_label('Statblock for Goblin 2').select_option(label='Goblin · Open5e · SRD 5.1')
        self.row('b').get_by_text('Failed: The source record was not found.').wait_for()
        self.server.fail_prepare.clear()
        self.row('b').get_by_role('button', name='Retry').click()
        dialog.get_by_role('button', name='Apply statblocks (2)').wait_for()
        dialog.get_by_role('button', name='Apply statblocks (2)').click()
        self.row('a').get_by_text('Not saved: The statblock changed.').wait_for()
        self.assertIn('not saved', dialog.locator('[role=status]').first.inner_text())
        first = self.server.applies[0]['operation_id']
        self.row('a').get_by_role('button', name='Retry').click()
        self.row('b').get_by_role('button', name='Retry').click()
        dialog.get_by_role('button', name='Apply statblocks (2)').click()
        self.page.wait_for_function("!document.querySelector('dialog.monster-statblock-bulk')")
        self.assertNotEqual(self.server.applies[1]['operation_id'], first)
        self.assertEqual(self.errors, [])

    def test_bulk_row_monster_file(self):
        dialog = self.start_bulk(['a', 'c'])
        self.row('c').locator('select').select_option('file')
        # Dismissing the file picker fires a bubbling 'cancel' that must not close the dialog.
        self.row('c').locator('input[type=file]').dispatch_event('cancel')
        self.assertTrue(dialog.is_visible())
        self.row('c').locator('input[type=file]').set_input_files(files=[
            {'name': 'thing.monster', 'mimeType': 'application/json', 'buffer': b'{"name":"Thing"}'}])
        dialog.get_by_role('button', name='Apply statblocks (1)').click()
        self.page.wait_for_function("!document.querySelector('dialog.monster-statblock-bulk')")
        self.assertEqual([item['monster_id'] for item in self.server.applies[0]['items']], ['c'])  # 'a' kept current
        self.assertEqual(self.errors, [])

    def test_bulk_batches_of_fifty_and_cancel(self):
        many = [dict(MONSTERS[0], id=f'm{i}', name=f'Goblin {i}') for i in range(55)]
        self.page.evaluate(f"latest.monsters = {json.dumps(many)}")
        self.server.revisions.update({m['id']: 0 for m in many})
        dialog = self.start_bulk([m['id'] for m in many])
        bodies = [c for c in self.server.calls if c == ('POST', 'discover')]
        self.assertEqual(len(bodies), 2)  # 50 + 5 targets
        for ident in ('m0', 'm54'):
            self.row(ident).locator('select').select_option(label='Goblin · Open5e · SRD 5.1')
        self.page.wait_for_timeout(50)
        dialog.get_by_role('button', name='Cancel').click()
        self.page.wait_for_function("!document.querySelector('dialog.monster-statblock-bulk')")
        self.assertEqual(self.server.applies, [])
        self.assertEqual(self.errors, [])


if __name__ == '__main__':
    unittest.main()
