"""022.15 Add Monster statblock preview from a signed lookup selection (no monster yet).

The ImportFixture of test_statblock_import_service (fake runner, real scheduler);
the signed-selection check is replaced by a fixture map (the real one needs
FastAPI). No network or browser; the button is covered in test_statblock_import_browser.
"""
import time
import unittest

import test_statblock_import_service as service_tests
from python.scrying_glass_statblock_collecting import collect_after_add
from python.scrying_glass_statblock_contract import PreparationFailure

GOBLIN = {'monster_source_provider': '5e.tools', 'monster_source_url': 'https://5e.tools/bestiary.html#goblin_mm',
          'monster_source_name': 'Goblin', 'monster_source_book': 'MM'}


class PreviewTests(service_tests.ImportFixture, unittest.TestCase):
    def setUp(self):
        service_tests.ImportFixture.setUp(self)
        self.selections = {'sel-goblin': ('Goblin', GOBLIN), 'sel-manual': ('Goblin', {})}
        def read(token, species):
            if token not in self.selections or self.selections[token][0] != species:
                raise ValueError('expired')
            return self.selections[token][1]
        self.service._read_selection = read
        self.failure = None
        original = self.service.runner
        def run(provider, identity, job, file_bytes, config):
            if self.gate is not None:
                self.gate.wait(5)
            if self.failure:
                raise PreparationFailure(self.failure)
            return original(provider, identity, job, file_bytes, config)
        self.service.runner = run

    def begin(self, token='sel-goblin', species='Goblin'):
        return self.service.preview_begin(self.principal(), {'selection_token': token, 'species': species})

    def follow(self, job):
        for _ in range(250):
            job = self.service.job_status(self.principal(), job['job_id'])
            if job['status'] not in ('queued', 'running'):
                return job
            time.sleep(0.02)
        self.fail('preview did not finish')

    def test_preview_of_the_selected_source_without_saving(self):
        job = self.follow(self.begin())
        self.assertEqual((job['status'], job['monster_id'], job['provider']), ('completed', None, '5e.tools'))
        self.assertEqual(job['preview']['source_label'], '5e.tools Goblin')
        self.assertEqual(job['source_label'], '5e.tools Goblin')
        self.assertNotIn('selection_id', job)
        self.assertEqual(self.runs, [('5e.tools', {'root': 'https://5e.tools/data', 'name': 'Goblin', 'source': 'MM'})])
        self.assertEqual(self.stored(), {})  # nothing saved
        # Cancelling a finished preview is harmless.
        self.assertEqual(self.service.job_cancel(self.principal(), job['job_id'])['status'], 'completed')

    def test_the_add_reuses_the_previewed_preparation(self):
        self.follow(self.begin())
        monster = next(m for m in self.c.STATE['monsters'] if m['id'] == 'm')
        import asyncio
        async def add():
            job = collect_after_add(self.c, [monster])
            for _ in range(250):
                if job.finished() and job.info.get('future') and job.info['future'].done():
                    return job.info['future'].result()
                await asyncio.sleep(0.02)
        self.assertEqual(asyncio.run(add()), 1)
        self.assertEqual(len(self.runs), 1)  # the cached conversion, not a second preparation

    def test_unavailable_and_rejected_previews(self):
        self.failure = 'statblock_unavailable'
        job = self.follow(self.begin())
        self.assertEqual((job['status'], job['error']['code']), ('failed', 'statblock_unavailable'))
        self.assert_error(422, 'no_source', self.begin, 'sel-manual')
        self.assert_error(410, 'selection_expired', self.begin, 'sel-goblin', 'Hobgoblin')
        self.assert_error(410, 'selection_expired', self.begin, 'forged')
        for body in ({}, {'selection_token': 'sel-goblin'}, {'selection_token': 1, 'species': 'Goblin'},
                     {'selection_token': 'sel-goblin', 'species': ' '},
                     {'selection_token': 'sel-goblin', 'species': 'Goblin', 'monster_id': 'm'}):
            with self.subTest(body=body):
                self.assert_error(422, 'invalid_request', self.service.preview_begin, self.principal(), body)
        self.display.update(fivetools_fallback=False)
        self.assert_error(409, 'provider_disabled', self.begin)

    def test_a_new_preview_cancels_the_previous_one_and_jobs_are_private(self):
        import threading
        self.gate = threading.Event()
        first = self.begin()
        second = self.begin()
        self.gate.set()
        self.assertEqual(self.follow(first)['status'], 'cancelled')
        self.assertEqual(self.follow(second)['status'], 'completed')
        self.c.SESSIONS['alice-other-token'] = {'username': 'alice', 'role': 'admin'}  # another browser session
        self.assert_error(404, 'job_not_found', self.service.job_status, self.principal('alice-other-token'),
                          second['job_id'])


if __name__ == '__main__':
    unittest.main()
