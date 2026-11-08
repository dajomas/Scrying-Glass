"""Offline access-gate fixtures and production selection-function integration.

No account, network, FastAPI server or live-provider verification is performed.
"""
import ast
import io
import logging
from html.parser import HTMLParser
from pathlib import Path
from types import SimpleNamespace
from urllib.error import HTTPError
from urllib.parse import urljoin
from unittest.mock import Mock, patch
import unittest
from python import scrying_glass_dndbeyond as dnd

ROOT = Path(__file__).resolve().parents[1]
LOCKED = b'<main>You do not have access to this content. Purchase this content to view.</main>'
STATS = b'''<span class="mon-stat-block__attribute-label">Armor Class</span>
<span class="mon-stat-block__attribute-data-value">12</span>
<span class="mon-stat-block__attribute-label">Hit Points</span>
<span class="mon-stat-block__attribute-data-value">7</span>
<span class="mon-stat-block__attribute-label">Speed</span>'''

class Response(io.BytesIO):
    def __init__(self, body, url='https://www.dndbeyond.com/monsters/claw'):
        super().__init__(body)
        self.url = url

    def geturl(self):
        return self.url


def error(code, body=LOCKED):
    return HTTPError('https://www.dndbeyond.com/monsters/claw', code, 'fixture', {}, io.BytesIO(body))


class LockedPageTests(unittest.TestCase):
    def test_visible_gate_text(self):
        for body in [LOCKED.decode(), '<main>You need to purchase this monster.</main>',
                     '<main>This content is locked.</main>']:
            self.assertTrue(dnd.dnd_monster_content_locked(body))
        for body in [STATS.decode(), '<nav>You do not have access to this content</nav><main>Goblin</main>',
                     '<script>"This content is locked"</script>',
                     '<main>Verify you are human. This content is locked.</main>',
                     '<main>403 Forbidden</main>', '<a href="/marketplace">Buy books</a>']:
            self.assertFalse(dnd.dnd_monster_content_locked(body))

    def test_locked_success_and_confirmed_http_denials(self):
        with patch.object(dnd, 'urlopen', return_value=Response(LOCKED)):
            self.assertEqual(dnd.dnd_monster_detail_html('/monsters/claw'), '')
        for code in [401, 403]:
            with patch.object(dnd, 'urlopen', side_effect=error(code)):
                self.assertEqual(dnd.dnd_monster_detail_html('/monsters/claw'), '')

    def test_generic_denials_and_server_errors_still_raise(self):
        for code in [401, 403, 429, 500]:
            body = b'Forbidden: checking your browser' if code in [401, 403] else LOCKED
            with patch.object(dnd, 'urlopen', side_effect=error(code, body)):
                with self.assertRaises(HTTPError):
                    dnd.dnd_monster_detail_html('/monsters/claw')
        with patch.object(dnd, 'urlopen', side_effect=TimeoutError('fixture')):
            with self.assertRaises(TimeoutError):
                dnd.dnd_monster_detail_html('/monsters/claw')

    def test_gate_redirects_and_untrusted_redirects(self):
        for path in ['/marketplace', '/marketplace/monsters/claw', '/login', '/sign-in?returnUrl=x']:
            with patch.object(dnd, 'urlopen', return_value=Response(b'', 'https://www.dndbeyond.com' + path)):
                self.assertEqual(dnd.dnd_monster_detail_html('/monsters/claw'), '')
        for url in ['https://evil.invalid/login', 'http://www.dndbeyond.com/login',
                    'https://www.dndbeyond.com/unknown', 'https://www.dndbeyond.com/marketplace-fake']:
            with patch.object(dnd, 'urlopen', return_value=Response(LOCKED, url)):
                with self.assertRaises(ValueError):
                    dnd.dnd_monster_detail_html('/monsters/claw')

    def test_oversized_denial_is_not_classified(self):
        with patch.object(dnd, 'urlopen', side_effect=error(403, LOCKED + b' ' * 128001)):
            with self.assertRaises(HTTPError):
                dnd.dnd_monster_detail_html('/monsters/claw')

    def test_accessible_stats_unchanged(self):
        with patch.object(dnd, 'urlopen', return_value=Response(STATS)):
            html = dnd.dnd_monster_detail_html('/monsters/claw')
        self.assertEqual(dnd.dnd_monster_stats_from_html(html), (12, '7', 'average'))


class SelectionIntegrationTests(unittest.TestCase):
    def setUp(self):
        # Extract production selection functions to avoid requiring FastAPI.
        source = ROOT / 'python/scrying_glass_monster_selection.py'
        tree = ast.parse(source.read_text(encoding='utf-8'))
        names = {'ProviderError', 'dnd_candidates', 'lookup_candidates', 'MonsterImage'}
        subset = ast.Module(body=[n for n in tree.body if getattr(n, 'name', None) in names], type_ignores=[])
        self.fallback = Mock(return_value=[{'found': True, 'species': 'Crawling Claw', 'provider': '5e.tools'}])
        self.sign = Mock(return_value='fixture-token')
        self.ns = dict(HTTPError=HTTPError, urlsplit=dnd.urlsplit, MAX_CANDIDATES=32,
                       LOG=logging.getLogger(__name__), HTMLParser=HTMLParser, urljoin=urljoin,
                       ft=SimpleNamespace(https_url=lambda value: value.startswith('https://')),
                       _KEY=b'locked-page-fixture-only-key', time=SimpleNamespace(time=lambda: 1000),
                       issue_token=self.sign, fivetools_candidates=self.fallback)
        self.ns.update(__name__='python.scrying_glass_monster_selection', __package__='python')
        exec(compile(subset, str(source), 'exec'), self.ns)
        self.ctx = SimpleNamespace(CONFIG={'display': {}},
            dnd_monster_candidates=Mock(return_value=[(True, '/monsters/old-claw'), (False, '/monsters/new-claw')]),
            dnd_monster_detail_html=dnd.dnd_monster_detail_html,
            dnd_monster_stats_from_html=dnd.dnd_monster_stats_from_html)

    def lookup(self):
        return self.ns['lookup_candidates'](self.ctx, 'Crawling Claw')

    def test_all_locked_keeps_fivetools_results(self):
        with patch.object(dnd, 'urlopen', side_effect=[Response(LOCKED), error(403)]):
            result = self.lookup()
        self.assertEqual(result['status'], 'ok')
        self.assertEqual(len(result['candidates']), 1)
        self.assertEqual(result['candidates'][0]['provider'], '5e.tools')
        self.fallback.assert_called_once_with('Crawling Claw', self.ctx.CONFIG['display'])
        self.sign.assert_called_once()

    def test_locked_then_usable_keeps_both_providers(self):
        with patch.object(dnd, 'urlopen', side_effect=[Response(LOCKED), Response(STATS)]):
            result = self.lookup()
        self.assertEqual(result['status'], 'ok')
        self.assertEqual([item['provider'] for item in result['candidates']], ['D&D Beyond', '5e.tools'])
        self.assertEqual((result['candidates'][0]['ac'], result['candidates'][0]['hp']), (12, '7'))
        self.fallback.assert_called_once_with('Crawling Claw', self.ctx.CONFIG['display'])
        self.assertEqual(self.sign.call_count, 2)

    def test_unclassified_failure_and_search_failure_block_all_results(self):
        with patch.object(dnd, 'urlopen', side_effect=error(403, b'Generic forbidden')):
            result = self.lookup()
        self.assertEqual((result['status'], result['candidates']), ('error', []))
        self.fallback.assert_called_once_with('Crawling Claw', self.ctx.CONFIG['display'])
        self.sign.assert_not_called()
        self.fallback.reset_mock()
        self.ctx.dnd_monster_candidates.side_effect = TimeoutError('fixture')
        result = self.lookup()
        self.assertEqual((result['status'], result['candidates']), ('error', []))
        self.fallback.assert_called_once_with('Crawling Claw', self.ctx.CONFIG['display'])
        self.sign.assert_not_called()

    def test_secondary_failure_blocks_accessible_primary_without_signing(self):
        self.fallback.side_effect = TimeoutError('private endpoint')
        with patch.object(dnd, 'urlopen', side_effect=[Response(LOCKED), Response(STATS)]):
            result = self.lookup()
        self.assertEqual((result['status'], result['candidates']), ('error', []))
        self.assertNotIn('private endpoint', result['reason'])
        self.fallback.assert_called_once_with('Crawling Claw', self.ctx.CONFIG['display'])
        self.sign.assert_not_called()

if __name__ == '__main__':
    unittest.main()
