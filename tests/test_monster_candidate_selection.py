"""Offline public-provider selection and signed image snapshot regressions."""
import time
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock, patch
from python import scrying_glass_monster_selection as ms
from python import scrying_glass_source_bonus_offer as offers

class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.ctx = SimpleNamespace(CONFIG={"display": {}},
            dnd_monster_candidates=Mock(return_value=[]),
            dnd_monster_detail_html=Mock(return_value='<img class="monster-image" src="https://example.org/chosen.png">'),
            dnd_monster_stats_from_html=Mock(return_value=(12, "2d6", "dice")))

    def test_count_table(self):
        for primary, secondary in [(1, 0), (2, 0), (0, 1), (0, 2), (0, 0), (1, 1), (2, 2)]:
            with self.subTest(primary=primary, secondary=secondary):
                self.ctx.dnd_monster_candidates.return_value = [(False, f"/monsters/{i}") for i in range(primary)]
                fallback = [dict(species="Goblin", provider="5e.tools") for _ in range(secondary)]
                with patch.object(ms, "fivetools_candidates", return_value=fallback) as ft:
                    result = ms.lookup_candidates(self.ctx, "Goblin")
                self.assertEqual(result["status"], "ok")
                self.assertEqual(len(result["candidates"]), primary + secondary)
                self.assertEqual(ft.call_count, 1)
                for candidate in result["candidates"]:
                    self.assertIn("selection_token", candidate)

    def test_unusable_duplicates_and_image(self):
        self.ctx.dnd_monster_candidates.return_value = [(False, "/monsters/empty"), (False, "/monsters/ok"), (False, "/monsters/ok")]
        self.ctx.dnd_monster_stats_from_html.side_effect = [(None, None, None), (12, "2d6", "dice")]
        with patch.object(ms, "fivetools_candidates", return_value=[]) as ft:
            result = ms.lookup_candidates(self.ctx, "Goblin")
        self.assertEqual(len(result["candidates"]), 1)
        self.assertEqual(result["candidates"][0]["image_url"], "https://example.org/chosen.png")
        ft.assert_called_once_with("Goblin", self.ctx.CONFIG["display"])

    def test_errors_block_combined_results_without_leaking_details(self):
        self.ctx.dnd_monster_candidates.side_effect = OSError("secret")
        with patch.object(ms, "fivetools_candidates", return_value=[]) as ft:
            result = ms.lookup_candidates(self.ctx, "Goblin")
        self.assertEqual(result["status"], "error")
        self.assertNotIn("secret", result["reason"])
        ft.assert_called_once_with("Goblin", self.ctx.CONFIG["display"])

    def test_incomplete_search_is_error(self):
        self.ctx.dnd_monster_candidates.return_value = [(False, "/monsters/ok"), (False, "/monsters/broken")]
        self.ctx.dnd_monster_detail_html.side_effect = ['html', OSError('secret')]
        with patch.object(ms, "fivetools_candidates", return_value=[]) as ft:
            self.assertEqual(ms.lookup_candidates(self.ctx, "Goblin")["status"], "error")
        ft.assert_called_once_with("Goblin", self.ctx.CONFIG["display"])

    def test_disabled_and_invalid_link(self):
        self.ctx.CONFIG["display"].update(dndbeyond_image_lookup=False, fivetools_fallback=False)
        self.assertEqual(ms.lookup_candidates(self.ctx, "Goblin")["candidates"], [])
        self.ctx.dnd_monster_candidates.assert_not_called()
        self.ctx.CONFIG["display"]["dndbeyond_image_lookup"] = True
        self.ctx.dnd_monster_candidates.return_value = [(False, 'https://evil.invalid/monsters/x')]
        self.assertEqual(ms.lookup_candidates(self.ctx, "Goblin")["status"], 'error')
        self.ctx.dnd_monster_detail_html.assert_not_called()

    def test_tokens(self):
        token = ms.issue_token({"species": "Goblin", "image_url": "https://example.org/chosen.png"})
        self.assertEqual(ms.selected_image(token, "Goblin"), "https://example.org/chosen.png")
        for value, species in [(token + "x", "Goblin"), (token, "Orc")]:
            with self.assertRaises(ValueError):
                ms.selected_image(value, species)
        with patch.object(ms.time, "time", return_value=time.time() + ms.TOKEN_AGE + 5):
            with self.assertRaises(ValueError):
                ms.selected_image(token, "Goblin")
        self.assertIsNone(ms.selected_image("manual", "Goblin"))
        self.assertIsNone(ms.selected_image(ms.issue_token({"species": "Goblin"}), "Goblin"))

    def test_fivetools_sources_and_deduplication(self):
        def load(url):
            if url.endswith('index.json'):
                return {'MM': 'mm.json', 'XMM': 'xmm.json'}
            source = 'XMM' if url.endswith('xmm.json') else 'MM'
            monster = {'name': 'Goblin', 'source': source, 'ac': [12], 'hp': {'average': 7}}
            return {'monster': [monster, monster, {'name': 'Goblin', '_copy': {}}]}
        with patch.object(ms.ft, 'load_json', side_effect=load):
            results = ms.fivetools_candidates('Goblin', {'fivetools_sources': ['MM', 'XMM', 'MM']})
        self.assertEqual([c['source'] for c in results], ['MM', 'XMM'])
        with patch.object(ms.ft, 'load_json', side_effect=OSError('secret')):
            with self.assertRaises(ms.ProviderError):
                ms.fivetools_candidates('Goblin', {})

    def test_secondary_failure_returns_no_candidates_and_never_signs(self):
        self.ctx.dnd_monster_candidates.return_value = [(False, "/monsters/old")]
        with patch.object(ms, "fivetools_candidates", side_effect=ms.ProviderError("secret")), \
                patch.object(ms, "issue_token") as sign, \
                patch.object(offers, "issue_bonus_offer") as bonus:
            result = ms.lookup_candidates(self.ctx, "Goblin")
        self.assertEqual((result["status"], result["candidates"]), ("error", []))
        self.assertNotIn("secret", result["reason"])
        sign.assert_not_called()
        bonus.assert_not_called()

    def test_both_versions_retain_separate_signed_source_identity(self):
        self.ctx.dnd_monster_candidates.return_value = [(True, "/monsters/old")]
        newer = dict(name="Goblin", species="Goblin", provider="5e.tools", source="XMM",
            legacy=False, source_url="https://5e.tools/bestiary.html#goblin_xmm",
            ac=16, hp="10", initiative_bonus=7, initiative_bonus_status="available")
        with patch.object(ms, "fivetools_candidates", return_value=[newer]):
            result = ms.lookup_candidates(self.ctx, "Goblin")
        old, new = result["candidates"]
        self.assertEqual((old["ac"], new["ac"]), (12, 16))
        for item in (old, new):
            _, identity = ms.selected_snapshot(item["selection_token"], "Goblin")
            self.assertEqual(identity["monster_source_url"], item["source_url"])
            self.assertEqual(identity["monster_source_provider"], item["provider"])
        offered = offers.read_bonus_offer(new["initiative_bonus_offer_token"], "Goblin",
            ms._KEY, now=time.time(), max_age=ms.TOKEN_AGE)
        self.assertEqual((offered["initiative_bonus"], offered["monster_source_book"]), (7, "XMM"))
        self.assertNotIn("selection_token", newer)

    def test_missing_configured_book_blocks_partial_candidates(self):
        self.ctx.CONFIG["display"].update(dndbeyond_image_lookup=False, fivetools_sources=["MM", "XMM"])
        def load(url):
            if url.endswith("index.json"):
                return {"MM": "mm.json"}
            return {"monster": [dict(name="Goblin", source="MM", ac=[12], hp={"average": 7})]}
        with patch.object(ms.ft, "load_json", side_effect=load), patch.object(ms, "issue_token") as sign:
            result = ms.lookup_candidates(self.ctx, "Goblin")
        self.assertEqual((result["status"], result["candidates"]), ("error", []))
        sign.assert_not_called()

    def test_unconfigured_entry_source_is_not_offered(self):
        data = dict(monster=[dict(name="Goblin", source="XMM", ac=[12], hp={"average": 7})])
        with patch.object(ms.ft, "load_json", side_effect=[{"MM": "mm.json"}, data]):
            result = ms.fivetools_candidates("Goblin", {"fivetools_sources": ["MM"]})
        self.assertEqual(result, [])

class CreationTests(unittest.IsolatedAsyncioTestCase):
    async def test_selection_and_manual_never_relookup(self):
        for image in [None, 'https://example.org/chosen.png']:
            context = SimpleNamespace(STATE={'monsters': []}, hp_value_factory=lambda *a: lambda: 7,
                make_monster=lambda fields, color, upload, url: {**fields, 'image_url': url},
                combatants_changed=AsyncMock(), dnd_image=Mock(side_effect=AssertionError('relookup')),
                HTTPException=lambda code, detail: ValueError(detail))
            handler = ms.CandidateMonstersMixin()
            handler.context = context
            token = ms.issue_token({'species': 'Goblin', 'image_url': image})
            for selection in [token, 'manual']:
                result = await handler.create_monster(name='Goblin', monster_species='Goblin', ac=12,
                    hprangestart='7', hprangeend='', color='#842029', quantity=1, image=None,
                    selection_token=selection)
                self.assertEqual(result[0]['image_url'], image if selection == token else None)
            context.dnd_image.assert_not_called()
            with self.assertRaises(ValueError):
                await handler.create_monster(name='Goblin', monster_species='Goblin', ac=12,
                    hprangestart='7', hprangeend='', color='#842029', quantity=1, image=None,
                    selection_token='invalid')
            self.assertEqual(len(context.STATE['monsters']), 2)

if __name__ == '__main__':
    unittest.main()
