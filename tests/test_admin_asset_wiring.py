"""Template asset wiring for the Admin and users pages.

Pages get a fresh cache-busting token per render (python/scrying_glass_asset_cache.py),
so manual ?v=N suffixes are not pinned here.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


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

    # Typed refresh-review feedback is checked by behaviour in
    # test_monster_refresh_review_browser.py; a text ban on paneNotification( was removed
    # (SG-TODO-023, handover 740: all three untyped variants fail those tests).


if __name__ == '__main__':
    unittest.main()
