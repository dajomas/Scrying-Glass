"""Candidate/source-review asset wiring; not full Stage 2 acceptance."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CandidateReviewFeedbackAssetTests(unittest.TestCase):
    def test_cache_versions_and_single_inclusions(self):
        end = (ROOT / 'templates/admin/190_document_end.html').read_text(encoding='utf-8')
        versions = {'monster-candidate-selection': 5, 'monster-refresh-review': 2}
        for name, version in versions.items():
            with self.subTest(asset=name):
                prefix = '/static/' + name + '.js'
                self.assertEqual(end.count(prefix + '?v=' + str(version)), 1)
                self.assertEqual(end.count(prefix), 1)
                for obsolete in range(1, version):
                    self.assertNotIn(prefix + '?v=' + str(obsolete), end)

    def test_existing_dependency_order_is_retained(self):
        end = (ROOT / 'templates/admin/190_document_end.html').read_text(encoding='utf-8')
        self.assertLess(end.index('/static/admin.js'), end.index('/static/monster-candidate-selection.js'))
        self.assertLess(end.index('/static/monster-refresh-selection.js'), end.index('/static/monster-refresh-review.js'))

    def test_review_asset_is_bounded_and_has_no_untyped_pane_calls(self):
        data = (ROOT / 'static/monster-refresh-review.js').read_bytes()
        self.assertLessEqual(len(data), 20000)
        self.assertNotIn('paneNotification(', data.decode('utf-8'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
