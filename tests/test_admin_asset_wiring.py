"""Template asset wiring and the 20,000-byte limit for static files and template fragments.

Pages get a fresh cache-busting token per render (python/scrying_glass_asset_cache.py),
so manual ?v=N suffixes are not pinned here.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 20000
ASSEMBLED = {ROOT / 'static/admin.js'}  # assembled from static/admin/*.js by the test runner


def local_assets(text):
    found = re.findall(r'<script[^>]*\ssrc="(/static/[^"]+)"', text)
    found += re.findall(r'<link[^>]*rel="stylesheet"[^>]*href="(/static/[^"]+)"', text)
    return [value.split('?', 1)[0] for value in found]


class AdminAssetWiringTests(unittest.TestCase):
    def test_local_assets_exist_and_are_included_once(self):
        pages = {'admin': ''.join(p.read_text(encoding='utf-8') for p in sorted((ROOT / 'templates/admin').glob('*.html'))),
                 'users': (ROOT / 'templates/users.html').read_text(encoding='utf-8')}
        for page, text in pages.items():
            assets = local_assets(text)
            with self.subTest(page=page):
                self.assertTrue(assets)
                self.assertEqual(len(assets), len(set(assets)), 'Duplicate asset include')
                for asset in assets:
                    self.assertTrue((ROOT / asset.lstrip('/')).is_file(), asset)

    def test_existing_dependency_order_is_retained(self):
        end = (ROOT / 'templates/admin/190_document_end.html').read_text(encoding='utf-8')
        self.assertLess(end.index('/static/admin.js'), end.index('/static/monster-candidate-selection.js'))
        self.assertLess(end.index('/static/monster-refresh-selection.js'), end.index('/static/monster-refresh-review.js'))

    def test_static_files_and_template_fragments_are_bounded(self):
        files = [p for p in (ROOT / 'static').rglob('*') if p.is_file() and p not in ASSEMBLED]
        files += list((ROOT / 'templates').rglob('*.html'))
        self.assertTrue(files)
        for path in files:
            with self.subTest(path=str(path.relative_to(ROOT))):
                self.assertLessEqual(path.stat().st_size, LIMIT)

    def test_review_asset_has_no_untyped_pane_calls(self):
        self.assertNotIn('paneNotification(', (ROOT / 'static/monster-refresh-review.js').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
