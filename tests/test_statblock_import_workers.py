"""022.08 preparation through the real isolated workers, shared fetcher and native SQLite.

.monster files, captured Open5e/D&D Beyond goblin responses and the Stage A synthetic
5e.tools dataset; no network. Skips when prlimit enforcement or captured evidence is absent.
"""
import copy
import glob
import hashlib
import json
import unittest
from pathlib import Path

from test_statblock_import_service import ROOT, ImportFixture, Transport
from python.scrying_glass_statblock_limits import StatblockLimits
from python.scrying_glass_statblock_service import StatblockService


class IsolatedFileWorkerTests(ImportFixture, unittest.TestCase):
    """The default runner for .monster files: real prlimit-bounded child process."""

    def setUp(self):
        super().setUp()
        self.service.scheduler.stop()
        self.c.statblocks = self.service = StatblockService(self.c, limits=StatblockLimits(), transport=self.transport,
                                                            display=lambda: self.display)

    def test_monster_file_prepares_in_the_worker_and_applies(self):
        files = sorted(glob.glob(str(ROOT / 'monsters_examples' / 'tetra-cube' / '*.monster')))
        if not files:
            self.skipTest('monsters_examples/tetra-cube is not present')
        raw = Path(files[0]).read_bytes()
        result = self.prepare(file_bytes=raw, filename='spider.monster')
        if result['status'] == 'failed' and result['error']['code'] == 'worker_enforcement_unavailable':
            self.skipTest('prlimit enforcement unavailable')
        self.assertEqual(result['status'], 'completed', result.get('error'))
        self.assertEqual(result['source']['provider'], 'file')
        self.assertEqual(result['source']['entity_id'], 'file|sha256:' + hashlib.sha256(raw).hexdigest())
        self.apply([{'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': result['selection_id']}])
        self.assertEqual(self.stored()['m']['provenance'][0]['file_name'], 'spider.monster')
        self.assert_error(413, 'file_too_large', self.prepare, file_bytes=b'x' * (5 * 1024 * 1024 + 1))
        bad = self.prepare(file_bytes=b'not json', filename='bad.monster')
        self.assertEqual((bad['status'], bad['error']['code']), ('failed', 'malformed_file'))


class CapturedProviderWorkerTests(ImportFixture, unittest.TestCase):
    """Open5e and D&D Beyond through the real worker, shared fetcher and captured responses."""

    def setUp(self):
        super().setUp()
        directory = ROOT / 'monsters_examples' / 'goblin'
        if not (directory / 'manifest.json').is_file():
            self.skipTest('captured monsters_examples evidence not present')
        manifest = json.loads((directory / 'manifest.json').read_text())
        responses = {row['url']: (directory / row['file']).read_bytes() for row in manifest['requests']
                     if row.get('status') == 200 and row.get('file')}
        for path in (ROOT / 'monsters_examples' / 'open5e-documents').glob('*.json'):
            responses[f'https://api.open5e.com/v2/documents/{path.stem}/?format=json'] = path.read_bytes()
        self.service.scheduler.stop()
        self.transport = Transport(responses)
        self.display.update(dndbeyond_image_lookup=True, fivetools_fallback=False)
        self.c.statblocks = self.service = StatblockService(self.c, limits=StatblockLimits(), transport=self.transport,
                                                            display=lambda: self.display)

    def test_open5e_and_dndbeyond_candidates_prepare_in_the_worker(self):
        discovered = self.discover(('n',))['monsters'][0]
        providers = {row['provider']: row['status'] for row in discovered['providers']}
        self.assertEqual(providers, {'D&D Beyond': 'complete', '5e.tools': 'disabled', 'Open5e': 'complete'})
        open5e = next(row for row in discovered['candidates'] if row['provider'] == 'Open5e')
        dndbeyond = next(row for row in discovered['candidates'] if row['provider'] == 'D&D Beyond')
        first = self.prepare('n', candidate=open5e['candidate_id'])
        if first['status'] == 'failed' and first['error']['code'] == 'worker_enforcement_unavailable':
            self.skipTest('prlimit enforcement unavailable')
        self.assertEqual(first['status'], 'completed', first.get('error'))
        self.assertEqual(first['source']['provider'], 'Open5e')
        self.assertTrue(first['source']['credits'])
        second = self.prepare('m', candidate=self.candidate('m', 'D&D Beyond'))
        self.assertEqual(second['status'], 'completed', second.get('error'))
        self.assertEqual(second['source']['provider'], 'D&D Beyond')
        self.apply([{'monster_id': 'n', 'expected_statblock_revision': 0, 'selection_id': first['selection_id']},
                    {'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': second['selection_id']}])
        stored = self.stored()
        self.assertEqual({key: value['provenance'][0]['provider'] for key, value in stored.items()},
                         {'n': 'Open5e', 'm': 'D&D Beyond'})
        self.assertIsNotNone(dndbeyond)
        # A second preparation of the same identity reuses the conversion and the fetched responses.
        calls = len(self.transport.calls)
        self.assertEqual(self.prepare('n', candidate=open5e['candidate_id'], revision=1)['status'], 'completed')
        self.assertEqual(len(self.transport.calls), calls)

    def test_plain_state_attaches_stored_private_content_before_writing(self):
        first = self.prepare('n', candidate=self.candidate('n', 'Open5e'))
        if first['status'] == 'failed' and first['error']['code'] == 'worker_enforcement_unavailable':
            self.skipTest('prlimit enforcement unavailable')
        self.apply([{'monster_id': 'n', 'expected_statblock_revision': 0, 'selection_id': first['selection_id']}])
        private = copy.deepcopy(self.c.STATE._statblocks)
        self.c.STATE = dict(self.c.STATE)  # trusted plain state without attached metadata
        self.assertEqual(self.service.revision('n'), 0)
        second = self.prepare('m', candidate=self.candidate('m', 'Open5e'))
        self.apply([{'monster_id': 'm', 'expected_statblock_revision': 0, 'selection_id': second['selection_id']}], 'op-2')
        stored = self.stored()
        self.assertEqual(stored['n']['content_digest'], private['n']['content_digest'])
        self.assertEqual(stored['m']['revision'], 1)


class IsolatedFivetoolsWorkerTests(ImportFixture, unittest.TestCase):
    """The default 5e.tools runner: discovery and the Stage A worker over the shared fetcher."""

    def setUp(self):
        super().setUp()
        from test_fivetools_preparation import dataset
        self.service.scheduler.stop()
        self.transport = Transport({'https://5e.tools/data/' + path: data for path, data in dataset().items()})
        self.display.update(fivetools_sources=['TST'], open5e_lookup=False)
        self.item('n')['monster_species'] = 'Grave Wight'
        self.c.statblocks = self.service = StatblockService(self.c, limits=StatblockLimits(), transport=self.transport,
                                                            display=lambda: self.display)

    def test_fivetools_candidate_prepares_in_the_worker(self):
        discovered = self.discover(('n',))['monsters'][0]
        self.assertEqual([(row['label'], row['source']) for row in discovered['candidates']], [('Grave Wight', 'TST')])
        result = self.prepare('n', candidate=discovered['candidates'][0]['candidate_id'])
        if result['status'] == 'failed' and result['error']['code'] == 'worker_enforcement_unavailable':
            self.skipTest('prlimit enforcement unavailable')
        self.assertEqual(result['status'], 'completed', result.get('error'))
        self.assertEqual((result['source']['provider'], result['source_label']), ('5e.tools', 'Grave Wight'))
        # Every dataset request went through the shared fetcher and its allowlist.
        self.assertTrue(all(url.startswith('https://5e.tools/data/') for url in self.transport.calls))
        self.apply([{'monster_id': 'n', 'expected_statblock_revision': 0, 'selection_id': result['selection_id']}])
        self.assertEqual(self.stored()['n']['provenance'][0]['provider'], '5e.tools')

    def test_fivetools_failures_are_explicit(self):
        discovered = self.discover(('n',))['monsters'][0]
        self.transport.responses.pop('https://5e.tools/data/bestiary/bestiary-tst.json')
        self.service.shared = type(self.service.shared)(self.service.limits)
        result = self.prepare('n', candidate=discovered['candidates'][0]['candidate_id'])
        if result['status'] == 'failed' and result['error']['code'] == 'worker_enforcement_unavailable':
            self.skipTest('prlimit enforcement unavailable')
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(self.service.store.counts()['bindings'], 0)


if __name__ == '__main__':
    unittest.main()
