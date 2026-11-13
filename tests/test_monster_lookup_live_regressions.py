"""Offline regressions for the observed marketplace redirect; no live HTTP."""
import io
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from python import scrying_glass_dndbeyond as dnd
from python import scrying_glass_monster_selection as selection

MARKETPLACE = 'https://marketplace.dndbeyond.com/category/monster-manual'
STATS = b'''<span class="mon-stat-block__attribute-label">Armor Class</span>
<span class="mon-stat-block__attribute-data-value">12</span>
<span class="mon-stat-block__attribute-label">Hit Points</span>
<span class="mon-stat-block__attribute-data-value">7</span>
<span class="mon-stat-block__attribute-label">Speed</span>'''

class Response(io.BytesIO):
    def __init__(self, url, body=b''):
        super().__init__(body)
        self.url = url

    def geturl(self):
        return self.url

class MarketplaceRegressionTests(unittest.TestCase):
    def context(self):
        return SimpleNamespace(CONFIG={'display': {}},
            dnd_monster_candidates=Mock(return_value=[(True, '/monsters/old-claw'), (False, '/monsters/new-claw')]),
            dnd_monster_detail_html=dnd.dnd_monster_detail_html,
            dnd_monster_stats_from_html=dnd.dnd_monster_stats_from_html)

    def test_observed_marketplace_redirect_is_unavailable(self):
        with patch.object(dnd, 'urlopen', return_value=Response(MARKETPLACE)) as fetch:
            self.assertEqual(dnd.dnd_monster_detail_html('/monsters/claw'), '')
        fetch.assert_called_once()

    def test_two_marketplace_redirects_search_fivetools_once(self):
        fallback = [{'found': True, 'species': 'Crawling Claw', 'provider': '5e.tools',
                     'image_url': None, 'ac': 12, 'hp': '2d4+2'}]
        with patch.object(dnd, 'urlopen', side_effect=[Response(MARKETPLACE), Response(MARKETPLACE)]) as fetch:
            with patch.object(selection, 'fivetools_candidates', return_value=fallback) as ft:
                result = selection.lookup_candidates(self.context(), 'Crawling Claw')
        self.assertEqual(fetch.call_count, 2)
        ft.assert_called_once_with('Crawling Claw', {})
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(result['candidates'][0]['provider'], '5e.tools')
        self.assertIn('selection_token', result['candidates'][0])

    def test_one_usable_primary_candidate_keeps_fivetools_version(self):
        newer = [dict(found=True, species='Crawling Claw', name='Crawling Claw',
            provider='5e.tools', source='XMM', legacy=False, ac=15, hp='10',
            source_url='https://5e.tools/bestiary.html#crawling%20claw_xmm')]
        with patch.object(dnd, 'urlopen', side_effect=[Response(MARKETPLACE),
                Response('https://www.dndbeyond.com/monsters/new-claw', STATS)]):
            with patch.object(selection, 'fivetools_candidates', return_value=newer) as ft:
                result = selection.lookup_candidates(self.context(), 'Crawling Claw')
        ft.assert_called_once_with('Crawling Claw', {})
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['candidates']), 2)
        self.assertEqual(result['candidates'][0]['provider'], 'D&D Beyond')
        self.assertEqual(result['candidates'][0]['ac'], 12)
        self.assertEqual((result['candidates'][1]['provider'], result['candidates'][1]['ac']), ('5e.tools', 15))

    def test_marketplace_exception_does_not_trust_other_destinations(self):
        for url in ['http://marketplace.dndbeyond.com/category/monster-manual',
                    'https://marketplace.dndbeyond.com.evil.invalid/category/monster-manual',
                    'https://user:secret@marketplace.dndbeyond.com/category/monster-manual',
                    'https://marketplace.dndbeyond.com/not-a-category']:
            with self.subTest(url=url):
                with patch.object(dnd, 'urlopen', return_value=Response(url)):
                    with self.assertRaises(ValueError):
                        dnd.dnd_monster_detail_html('/monsters/claw')

if __name__ == '__main__':
    unittest.main()
