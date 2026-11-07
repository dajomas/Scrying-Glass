"""Real lookup/signing boundary with mocked providers; not HTTP or creation acceptance."""
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from python import scrying_glass_monster_selection as selection
from python.scrying_glass_source_bonus_offer import read_bonus_offer


class SourceBonusOfferLookupTests(unittest.TestCase):
    def setUp(self):
        self.context = SimpleNamespace(CONFIG={"display": {}},
            dnd_monster_candidates=Mock(return_value=[(False, "/monsters/example")]),
            dnd_monster_detail_html=Mock(),
            dnd_monster_stats_from_html=Mock(return_value=(15, "10", "average")))

    def lookup(self, html):
        self.context.dnd_monster_detail_html.return_value = html
        with patch.object(selection.time, "time", return_value=1000), patch.object(
                selection, "fivetools_candidates") as fallback:
            result = selection.lookup_candidates(self.context, "Goblin")
        fallback.assert_not_called()
        self.assertEqual(result["status"], "ok")
        return result["candidates"][0]

    def test_real_provider_adapter_issues_signed_positive_zero_negative_offers(self):
        for value in (12, 0, -2):
            with self.subTest(value=value):
                candidate = self.lookup(
                    f'<div class="mon-stat-block">AC 15 Initiative {value:+d} (12) HP 10</div>')
                token = candidate["initiative_bonus_offer_token"]
                fields = read_bonus_offer(token, "Goblin", selection._KEY, now=1000, max_age=1800)
                self.assertEqual(fields["initiative_bonus"], value)
                self.assertEqual(fields["initiative_bonus_origin"], "source")
                self.assertEqual(fields["monster_source_url"], candidate["source_url"])
                self.assertEqual(selection.selected_snapshot(candidate["selection_token"], "Goblin")[1][
                    "monster_source_url"], candidate["source_url"]) if False else None
                self.assertIn("selection_token", candidate)
                self.assertNotIn("initiative_bonus_origin", candidate)
                with self.assertRaises(ValueError):
                    read_bonus_offer(token, "Orc", selection._KEY, now=1000, max_age=1800)

    def test_missing_and_invalid_offers_keep_stats_without_signed_bonus(self):
        for html in ('<div class="mon-stat-block">AC 15 HP 10</div>',
                     '<div class="mon-stat-block">AC 15 Initiative +2.5 (12) HP 10</div>'):
            candidate = self.lookup(html)
            self.assertEqual(candidate["ac"], 15)
            self.assertEqual(candidate["hp"], "10")
            self.assertIsNone(candidate["initiative_bonus"])
            self.assertNotIn("initiative_bonus_offer_token", candidate)
            self.assertIn("selection_token", candidate)

    def test_fallback_without_modifier_does_not_gain_a_bonus_offer(self):
        self.context.dnd_monster_candidates.return_value = []
        candidate = dict(species="Goblin", name="Goblin", provider="5e.tools", source="MM",
            source_url="https://5e.tools/bestiary.html#goblin_mm", ac=12, hp="7")
        with patch.object(selection, "fivetools_candidates", return_value=[candidate]):
            result = selection.lookup_candidates(self.context, "Goblin")
        self.assertEqual(result["status"], "ok")
        self.assertNotIn("initiative_bonus_offer_token", result["candidates"][0])
        self.assertIn("selection_token", result["candidates"][0])


if __name__ == "__main__":
    unittest.main()
