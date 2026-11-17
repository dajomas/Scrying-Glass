"""022.08 discovery, preparation and atomic apply against real SQLite storage.

Seeded sessions (not logged in), fake provider transports and, except where a
test uses the real isolated .monster worker, fake preparation runners. HTTP
routing and the browser are covered elsewhere (test_statblock_import_http.py).
"""
import asyncio
import copy
import json
import threading
import time
import unittest
from pathlib import Path

import test_encounter_features as fixtures
from test_statblock_encounters import snapshot
from python.scrying_glass_campaign_ownership import ownership
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_fetching import FetchFailure
from python.scrying_glass_statblock_limits import StatblockLimits
from python.scrying_glass_statblock_model import content_digest
from python.scrying_glass_statblock_service import StatblockAPIError, StatblockService
from python.scrying_glass_statblock_sources import SourceError

ROOT = Path(__file__).resolve().parent.parent
DISPLAY = {'dndbeyond_image_lookup': False, 'fivetools_fallback': True, 'fivetools_sources': ['MM', 'XMM'],
           'fivetools_data_base_url': 'https://5e.tools/data/bestiary', 'open5e_lookup': True,
           'open5e_base_url': 'https://api.open5e.com/v2'}
INDEX = json.dumps({'MM': 'bestiary-mm.json', 'XMM': 'bestiary-xmm.json'}).encode()


def prepared(label, provider='5e.tools'):
    value = snapshot(label)
    value['provenance'][0]['provider'] = provider
    value['content_digest'] = content_digest(value)
    return value


class Transport:
    """(provider, url, deadline, root=None) -> bytes from a dictionary of URLs."""

    def __init__(self, responses):
        self.responses, self.calls = dict(responses), []

    def __call__(self, provider, url, deadline, root=None):
        self.calls.append(url)
        value = self.responses.get(url)
        if isinstance(value, Exception):
            raise value
        if value is None:
            raise SourceError('not_found')
        return value


class ImportFixture:
    item = fixtures.FeatureTests.item

    def setUp(self):
        fixtures.FeatureTests.setUp(self)
        c, db = self.c, self.c.STORAGE.connection
        c.ADMIN_SESSION_COOKIE, c.CLIENT_SESSION_COOKIE, c.SESSIONS = 'admin', 'client', {}
        self.ids = {}
        for name, role in (('alice', 'admin'), ('bob', 'admin'), ('root', 'superadmin'), ('viewer', 'client')):
            self.ids[name] = str(db.execute('INSERT INTO users(username,role,password_hash) VALUES (?,?,?)',
                                            (name, role, 'unused')).lastrowid)
            c.SESSIONS[name + '-token'] = {'username': name, 'role': role}
        def user(username):
            row = db.execute('SELECT id,username,role FROM users WHERE username=?', (username,)).fetchone()
            return dict(id=row['id'], username=row['username'], role=row['role']) if row else None
        def auth_session(token):
            session = c.SESSIONS.get(token)
            if not session:
                return None
            found = user(session['username'])
            if not found or found['role'] != session['role']:
                c.SESSIONS.pop(token, None)
                return None
            return session
        c.user, c.auth_session = user, auth_session
        owners = ownership(c); owners.initialize()
        owners.reassign(c.active_campaign(), {'owner_user_id': self.ids['alice']})
        self.other = c.STORAGE.create_campaign('Bob campaign', '', 'now'); c.STORAGE.save_characters(self.other, [])
        owners.reassign(self.other, {'owner_user_id': self.ids['bob']})
        monster = self.item('m')
        monster.update(monster_species='Goblin', monster_source_provider='5e.tools',
                       monster_source_url='https://5e.tools/bestiary.html#goblin_mm', monster_source_name='Goblin',
                       monster_source_book='MM')
        second = copy.deepcopy(monster)
        second.update(id='n', name='Goblin 2')
        for key in ('monster_source_provider', 'monster_source_url', 'monster_source_name', 'monster_source_book'):
            second.pop(key)
        c.STATE['monsters'].append(second)
        c.save_active_setup_monsters(); c.save_state(); c.load_state()
        self.display = dict(DISPLAY)
        self.transport = Transport({
            'https://5e.tools/data/bestiary/index.json': INDEX,
            'https://5e.tools/data/bestiary/bestiary-mm.json': json.dumps({'monster': [
                {'name': 'Goblin', 'source': 'MM'}, {'name': 'Hobgoblin', 'source': 'MM'}]}).encode(),
            'https://5e.tools/data/bestiary/bestiary-xmm.json': json.dumps({'monster': [
                {'name': 'Goblin', 'source': 'XMM', '_versions': [{}]}]}).encode(),
            'https://api.open5e.com/v2/creatures/?name__iexact=Goblin&limit=100&format=json': json.dumps(
                {'results': [{'key': 'srd_goblin', 'name': 'Goblin', 'document': {'name': 'SRD'}}], 'next': None}).encode(),
        })
        self.runs = []
        self.gate = None
        self.service = self.make_service()

    def make_service(self, **limits):
        def runner(provider, identity, job, file_bytes, config):
            self.runs.append((provider, dict(identity)))
            if self.gate is not None:
                self.gate.wait(5)
            label = identity.get('name') or identity.get('key') or identity.get('path') or 'File'
            return prepared(f'{provider} {label}', provider), {'snapshot_bytes': 1}
        self.c.statblocks = StatblockService(self.c, limits=StatblockLimits(**limits), transport=self.transport,
                                             runner=runner, display=lambda: self.display)
        return self.c.statblocks

    def tearDown(self):
        self.service.scheduler.stop()
        fixtures.FeatureTests.tearDown(self)

    def principal(self, token='alice-token', campaign=None):
        return self.service.authorize(token, campaign)

    def token(self):
        return self.service.encounter_token(self.c.active_campaign())

    def discover(self, ids=('m',), token='alice-token'):
        principal = self.principal(token)
        plan = self.service.discover_begin(principal, {'campaign_id': principal.campaign,
                                                       'encounter_token': self.token(), 'monster_ids': list(ids)})
        return self.service.discover_finish(self.principal(token), plan, self.service.discover_run(plan))

    def candidate(self, monster='m', provider='5e.tools', original=None, token='alice-token'):
        for row in self.discover((monster,), token)['monsters'][0]['candidates']:
            if row['provider'] == provider and (original is None or row.get('original', False) == original):
                return row['candidate_id']
        raise AssertionError('candidate not found')

    def prepare(self, monster='m', candidate=None, token='alice-token', revision=None, **extra):
        principal = self.principal(token)
        body = {'campaign_id': principal.campaign, 'encounter_token': self.token(), 'monster_id': monster,
                'expected_statblock_revision': self.service.revision(monster) if revision is None else revision}
        if candidate is not None:
            body['candidate_id'] = candidate
        body.update(extra.pop('body', {}))
        job = self.service.prepare(principal, body, **extra)
        return self.wait(job['job_id'], token)

    def wait(self, job_id, token='alice-token'):
        for _ in range(500):
            status = self.service.job_status(self.principal(token), job_id)
            if status['status'] not in ('queued', 'running'):
                return status
            time.sleep(0.01)
        raise AssertionError('job did not finish')

    def apply(self, items, operation='op-1', token='alice-token', encounter=None):
        principal = self.principal(token)
        body = {'operation_id': operation, 'campaign_id': principal.campaign,
                'encounter_token': self.token() if encounter is None else encounter, 'items': items}
        async def apply_statblocks():
            return self.service.apply(self.principal(token), body)
        return asyncio.run(transactional_handler(self.c, apply_statblocks)())

    def stored(self):
        reference = self.c.active_setup_reference()
        row = self.c.STORAGE.connection.execute('SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',
                                                (reference['campaign_id'], reference['name'])).fetchone()
        return PrivateEncounterStorage(self.c.STORAGE).load(row[0])[PRIVATE_KEY]

    def assert_error(self, status, code, call, *args, **kwargs):
        with self.assertRaises(StatblockAPIError) as caught:
            call(*args, **kwargs)
        self.assertEqual((caught.exception.status, caught.exception.code), (status, code), caught.exception.envelope())
        return caught.exception


class AuthorizationTests(ImportFixture, unittest.TestCase):
    def test_only_a_regular_admin_assigned_to_the_active_campaign_is_accepted(self):
        self.assertEqual(self.principal().campaign, self.c.active_campaign())
        self.assert_error(401, 'unauthenticated', self.service.authorize, 'missing-token')
        self.assert_error(401, 'unauthenticated', self.service.authorize, '')
        self.assert_error(403, 'regular_admin_required', self.service.authorize, 'root-token')
        self.assert_error(403, 'regular_admin_required', self.service.authorize, 'viewer-token')
        self.assert_error(403, 'campaign_forbidden', self.service.authorize, 'bob-token')
        self.assert_error(403, 'campaign_forbidden', self.service.authorize, 'alice-token', self.other)

    def test_role_change_and_logout_revoke_held_references(self):
        candidate = self.candidate()
        result = self.prepare(candidate=candidate)
        self.assertEqual(result['status'], 'completed')
        self.service.revoke_session('alice-token')
        self.c.SESSIONS.pop('alice-token')
        self.c.SESSIONS['alice-token'] = {'username': 'alice', 'role': 'admin'}
        item = {'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': result['selection_id']}
        error = self.assert_error(410, 'apply_rejected', self.apply, [item])
        self.assertEqual(error.items[0]['code'], 'selection_expired')
        self.c.STORAGE.connection.execute("UPDATE users SET role='client' WHERE username='alice'")
        self.assert_error(401, 'unauthenticated', self.service.authorize, 'alice-token')


class DiscoveryTests(ImportFixture, unittest.TestCase):
    def test_original_identity_comes_first_and_providers_report_completeness(self):
        result = self.discover(('m', 'n'))
        self.assertTrue(result['complete'])
        first, second = result['monsters']
        labels = [(row['provider'], row.get('source'), row.get('original', False)) for row in first['candidates']]
        self.assertEqual(labels, [('5e.tools', 'MM', True), ('5e.tools', 'XMM', False), ('Open5e', None, False)])
        self.assertEqual([row['provider'] for row in second['candidates']], ['5e.tools', '5e.tools', 'Open5e'])
        providers = {row['provider']: row for row in first['providers']}
        self.assertEqual(providers['D&D Beyond']['status'], 'disabled')
        self.assertEqual(providers['5e.tools']['omitted_versions'], 1)
        # One lookup per species and provider, shared through the cache across monsters.
        self.assertEqual(self.transport.calls.count('https://5e.tools/data/bestiary/index.json'), 1)
        self.discover(('m',))
        self.assertEqual(self.transport.calls.count('https://5e.tools/data/bestiary/index.json'), 1)
        self.assertNotIn('Hobgoblin', json.dumps(result))

    def test_failures_are_not_zero_match_results(self):
        self.transport.responses['https://5e.tools/data/bestiary/bestiary-xmm.json'] = SourceError('provider_unavailable')
        self.transport.responses['https://api.open5e.com/v2/creatures/?name__iexact=Goblin&limit=100&format=json'] = \
            SourceError('provider_error')
        result = self.discover(('n',))
        self.assertFalse(result['complete'])
        providers = {row['provider']: row for row in result['monsters'][0]['providers']}
        self.assertEqual((providers['5e.tools']['status'], providers['5e.tools']['code']), ('partial', 'provider_unavailable'))
        self.assertEqual((providers['Open5e']['status'], providers['Open5e']['code']), ('error', 'provider_error'))
        again = {row['provider']: row for row in self.discover(('n',))['monsters'][0]['providers']}
        self.assertEqual(again['Open5e']['status'], 'cooldown')
        self.assertIn('retry_at', again['Open5e'])

    def test_disabled_providers_are_not_contacted(self):
        self.display.update(fivetools_fallback=False, open5e_lookup=False)
        result = self.discover(('m',))
        self.assertEqual(self.transport.calls, [])
        candidate = result['monsters'][0]['candidates'][0]
        self.assertTrue(candidate['original'] and candidate['disabled'])
        self.assert_error(409, 'provider_disabled', self.prepare, candidate=candidate['candidate_id'])

    def test_requests_are_validated(self):
        principal = self.principal()
        for body, status, code in (
            ({'campaign_id': principal.campaign, 'encounter_token': 'stale', 'monster_ids': ['m']}, 409, 'encounter_changed'),
            ({'campaign_id': principal.campaign, 'encounter_token': self.token(), 'monster_ids': []}, 422, 'invalid_request'),
            ({'campaign_id': principal.campaign, 'encounter_token': self.token(), 'monster_ids': ['m', 'm']}, 422, 'invalid_request'),
            ({'campaign_id': principal.campaign, 'encounter_token': self.token(), 'monster_ids': ['x']}, 404, 'monster_not_found'),
            ({'campaign_id': principal.campaign, 'encounter_token': self.token(), 'monster_ids': [f'm{i}' for i in range(51)]},
             413, 'too_many_targets'),
            ({'campaign_id': principal.campaign, 'encounter_token': self.token(), 'monster_ids': ['m'], 'url': 'x'},
             422, 'invalid_request'),
        ):
            self.assert_error(status, code, self.service.discover_begin, principal, body)

    def test_a_target_changed_during_discovery_gets_no_candidates(self):
        principal = self.principal()
        plan = self.service.discover_begin(principal, {'campaign_id': principal.campaign,
                                                       'encounter_token': self.token(), 'monster_ids': ['m']})
        results = self.service.discover_run(plan)
        self.item('m')['monster_species'] = 'Bugbear'
        result = self.service.discover_finish(self.principal(), plan, results)
        self.assertEqual((result['complete'], result['monsters'][0]['status']), (False, 'target_changed'))


class PrepareApplyTests(ImportFixture, unittest.TestCase):
    def test_prepare_then_apply_saves_one_new_revision_atomically_and_replays(self):
        result = self.prepare(candidate=self.candidate(original=False))
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(self.runs, [('5e.tools', {'root': 'https://5e.tools/data', 'name': 'Goblin', 'source': 'XMM'})])
        self.assertEqual((result['source_label'], result['completeness']), ('5e.tools Goblin', 'available'))
        self.assertIn('preview', result)
        before = copy.deepcopy(dict(self.c.STATE))
        item = {'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': result['selection_id']}
        applied = self.apply([item])
        self.assertEqual(applied['applied'], [{'monster_id': 'm', 'statblock_revision': 1}])
        self.assertEqual(self.stored()['m']['source_label'], '5e.tools Goblin')
        self.assertEqual(self.c.STATE._statblocks['m']['revision'], 1)
        # Six SG fields and tracker source identity are untouched.
        self.assertEqual(dict(self.c.STATE)['monsters'], before['monsters'])
        # Identical retry returns the recorded outcome; different content under the same ID conflicts.
        self.assertEqual(self.apply([item]), applied)
        self.assert_error(409, 'operation_conflict', self.apply, [dict(item, expected_statblock_revision=1)])
        # The selection was consumed.
        error = self.assert_error(410, 'apply_rejected', self.apply, [dict(item, expected_statblock_revision=1)], 'op-2')
        self.assertEqual(error.items[0]['code'], 'selection_expired')
        self.assertEqual(self.service.store.counts()['bindings'], 0)
        # Apply is recorded for undo like other tracked encounter changes.
        undo = self.f.store.latest_undo(self.c.active_campaign())
        self.assertEqual(undo['name'], 'Apply statblocks')

    def test_one_invalid_row_rejects_the_whole_batch(self):
        good = self.prepare(candidate=self.candidate())
        other = self.prepare('n', candidate=self.candidate('n'))
        self.item('n')['monster_species'] = 'Bugbear'
        error = self.assert_error(409, 'apply_rejected', self.apply, [
            {'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': good['selection_id']},
            {'monster_id': 'n', 'expected_statblock_revision': 0, 'selection_id': other['selection_id']}])
        self.assertEqual([row['code'] for row in error.items], ['target_changed'])
        self.assertEqual(self.stored(), {})
        self.assertEqual(self.service.store.counts()['bindings'], 2)

    def test_tampered_stale_and_cross_target_references_are_rejected(self):
        mine = self.prepare(candidate=self.candidate())
        self.assert_error(409, 'candidate_mismatch', self.prepare, 'n', candidate=self.candidate('m'))
        self.assert_error(410, 'candidate_expired', self.prepare, candidate='forged-candidate')
        self.assert_error(409, 'stale_revision', self.prepare, candidate=self.candidate(), revision=3)
        rows = [
            ({'monster_id': 'n', 'expected_statblock_revision': 0, 'selection_id': mine['selection_id']}, 'selection_mismatch'),
            ({'monster_id': 'm', 'expected_statblock_revision': 1, 'selection_id': mine['selection_id']}, 'stale_revision'),
            ({'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': 'forged'}, 'selection_expired'),
        ]
        for index, (item, code) in enumerate(rows):
            error = self.assert_error(error_status(code), 'apply_rejected', self.apply, [item], f'op-{index}')
            self.assertEqual(error.items[0]['code'], code)
        self.assert_error(422, 'duplicate_target', self.apply, [rows[0][0], dict(rows[0][0], selection_id='other')])
        self.assert_error(409, 'encounter_changed', self.apply, [rows[1][0]], 'op-x', encounter='stale')
        self.assertEqual(self.stored(), {})

    def test_concurrent_saved_change_and_provider_switch_invalidate_preparations(self):
        first = self.prepare(candidate=self.candidate())
        second = self.prepare(candidate=self.candidate(original=False))
        self.apply([{'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': first['selection_id']}])
        error = self.assert_error(409, 'apply_rejected', self.apply,
                                  [{'monster_id': 'm', 'expected_statblock_revision': 0,
                                    'selection_id': second['selection_id']}], 'op-2')
        self.assertEqual(error.items[0]['code'], 'stale_revision')
        third = self.prepare(candidate=self.candidate())
        self.display['fivetools_fallback'] = False
        error = self.assert_error(409, 'apply_rejected', self.apply,
                                  [{'monster_id': 'm', 'expected_statblock_revision': 1,
                                    'selection_id': third['selection_id']}], 'op-3')
        self.assertEqual(error.items[0]['code'], 'provider_disabled')
        self.assertEqual(self.stored()['m']['revision'], 1)

    def test_selections_expire_and_are_private_to_the_session(self):
        self.c.SESSIONS['alice-2'] = {'username': 'alice', 'role': 'admin'}
        result = self.prepare(candidate=self.candidate())
        item = {'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': result['selection_id']}
        error = self.assert_error(403, 'apply_rejected', self.apply, [item], token='alice-2')
        self.assertEqual(error.items[0]['code'], 'selection_forbidden')
        self.assert_error(404, 'job_not_found', self.service.job_status, self.principal('alice-2'), result['job_id'])
        clock = [time.monotonic() + 601]
        self.service.store.clock = lambda: clock[0]
        error = self.assert_error(410, 'apply_rejected', self.apply, [item])
        self.assertEqual(error.items[0]['code'], 'selection_expired')

    def test_capacity_is_rejected_explicitly(self):
        self.service.scheduler.stop()
        self.service = self.make_service(session_selection_references=1)
        self.prepare(candidate=self.candidate())
        self.assert_error(429, 'session_selection_capacity', self.prepare, candidate=self.candidate())
        self.service.scheduler.stop()
        self.service = self.make_service(active_jobs=1, queued_jobs=1)
        self.gate = threading.Event()
        principal = self.principal()
        body = {'campaign_id': principal.campaign, 'encounter_token': self.token(), 'monster_id': 'm',
                'expected_statblock_revision': 0}
        running = self.service.prepare(principal, dict(body, candidate_id=self.candidate()))
        for _ in range(100):
            if self.runs:
                break
            time.sleep(0.01)
        self.service.prepare(principal, dict(body, candidate_id=self.candidate()))
        self.assert_error(429, 'queue_full', self.service.prepare, principal, dict(body, candidate_id=self.candidate()))
        cancelled = self.service.job_cancel(principal, running['job_id'])
        self.gate.set()
        self.assertEqual(self.wait(running['job_id'])['status'], 'cancelled')
        self.assertIn(cancelled['status'], ('running', 'cancelled'))

    def test_deadline_and_runner_failures_are_reported_without_a_selection(self):
        def runner(provider, identity, job, file_bytes, config):
            raise FetchFailure('provider_unavailable')
        self.service.runner = runner
        result = self.prepare(candidate=self.candidate())
        self.assertEqual((result['status'], result['error']['code']), ('failed', 'provider_unavailable'))
        from python.scrying_glass_statblock_service import PreparationFailure
        def failing(provider, identity, job, file_bytes, config):
            raise PreparationFailure('cooldown', time.monotonic() + 30)
        self.service.runner = failing
        result = self.prepare(candidate=self.candidate())
        self.assertEqual((result['status'], result['error']['code']), ('failed', 'cooldown'))
        self.assertIn('retry_at', result['error'])
        self.assertEqual(self.service.store.counts()['reserved'], 0)

    def test_conversion_cache_reuses_an_identical_preparation(self):
        self.prepare(candidate=self.candidate())
        self.prepare(candidate=self.candidate())
        self.assertEqual(len(self.runs), 1)
        self.service.limits = StatblockLimits(snapshot_bytes=1048576)
        self.prepare(candidate=self.candidate())
        self.assertEqual(len(self.runs), 2)

    def test_reads_expose_live_values_and_revisions(self):
        state = self.service.state_projection(self.principal())
        self.assertEqual(state['encounter_token'], self.token())
        self.assertEqual([row['monster_id'] for row in state['monsters']], ['m', 'n'])
        self.assertEqual(state['monsters'][0]['status'], 'missing')
        result = self.prepare(candidate=self.candidate())
        self.apply([{'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': result['selection_id']}])
        read = self.service.monster_projection(self.principal(), 'm')
        self.assertEqual((read['statblock_revision'], read['status'], read['live']['species']), (1, 'available', 'Goblin'))
        self.assertEqual(read['source']['provider'], '5e.tools')
        self.assertTrue(self.service.monster_projection(self.principal(), 'm', 1)['unchanged'])
        tiles = self.service.state_projection(self.principal())['tiles']
        self.assertEqual(tiles[0]['statblock_revision'], 1)

    def test_edit_staging_saves_the_statblock_with_the_ordinary_edit(self):
        result = self.prepare(candidate=self.candidate())
        fields = {'selection_id': result['selection_id'], 'operation_id': 'edit-1', 'expected_revision': '0',
                  'expected_values': json.dumps({'hp': self.item('m')['hp']})}
        async def edit_monster():
            monster = self.item('m')
            plan = self.service.stage_edit('alice-token', monster, fields)
            monster['monster_species'] = 'Goblin boss'  # intentional species edit in the same save
            plan.install(monster)
            return monster
        saved = asyncio.run(transactional_handler(self.c, edit_monster)())
        self.assertEqual(saved['monster_species'], 'Goblin boss')
        self.assertEqual(self.stored()['m']['revision'], 1)
        replay = self.service.stage_edit('alice-token', self.item('m'), fields)
        self.assertEqual(replay['replay']['statblock_revision'], 1)
        stale = dict(fields, operation_id='edit-2', expected_values=json.dumps({'hp': 999}))
        error = self.assert_error(409, 'edit_conflict', self.service.stage_edit, 'alice-token', self.item('m'), stale)
        self.assertIn('hp', error.items[0]['message'])
        self.assertIsNone(self.service.stage_edit('root-token', self.item('m'), {'selection_id': '', 'expected_values': ''}))
        self.assert_error(403, 'regular_admin_required', self.service.stage_edit, 'root-token', self.item('m'),
                          dict(fields, operation_id='edit-3'))

    def test_failed_transaction_keeps_the_selection_and_old_content(self):
        result = self.prepare(candidate=self.candidate())
        item = {'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': result['selection_id']}
        principal = self.principal()
        body = {'operation_id': 'op-fail', 'campaign_id': principal.campaign, 'encounter_token': self.token(),
                'items': [item]}
        async def apply_statblocks():
            self.service.apply(principal, body)
            raise RuntimeError('later failure in the same transaction')
        with self.assertRaises(RuntimeError):
            asyncio.run(transactional_handler(self.c, apply_statblocks)())
        self.assertEqual(self.stored(), {})
        self.assertEqual(self.service.store.counts()['bindings'], 1)
        self.assertIsNone(self.service.store.outcome(principal.session, 'op-fail'))
        self.assertEqual(self.apply([item], 'op-fail')['applied'][0]['statblock_revision'], 1)


def error_status(code):
    return {'selection_expired': 410, 'selection_forbidden': 403}.get(code, 409)


if __name__ == '__main__':
    unittest.main()
