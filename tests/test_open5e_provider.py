"""Offline Open5e v2 provider fixtures (SG-TODO-017 Stage 2); no network access."""
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from python import scrying_glass_open5e as open5e
from python import scrying_glass_monster_selection as ms
from python.scrying_glass_monster_source_snapshot import capture_source_fields, validate_source_fields

BASE = "https://api.open5e.com/v2"


def document(key, name, system_key, system_name):
    return {"key": key, "display_name": name, "name": name, "type": "SOURCE",
            "publisher": {"name": "Pub " + key, "key": "pub"},
            "gamesystem": {"key": system_key, "name": system_name}}


SRD = document("srd-2014", "5e 2014 Rules", "5e-2014", "5th Edition 2014")
A5E = document("a5e-mm", "Monstrous Menagerie", "a5e", "Advanced 5th Edition")
GOBLINS = [
    {"key": "srd_goblin", "name": "Goblin", "document": SRD, "armor_class": 15,
     "hit_points": 7, "hit_dice": "2d6", "initiative_bonus": 2, "illustration": None},
    {"key": "a5e-mm_goblin", "name": "Goblin", "document": A5E, "armor_class": 13,
     "hit_points": 10, "hit_dice": "3d6", "initiative_bonus": 1,
     "illustration": {"file_url": "/static/img/goblin.png"}},
]
DOCUMENTS = {"count": 2, "next": None, "results": [
    dict(SRD, licenses=[{"name": "OPEN GAME LICENSE Version 1.0a", "key": "ogl-10a"}]),
    dict(A5E, licenses=[{"name": "Creative Commons Attribution 4.0", "key": "cc-by-40"}])]}


class Fixture:
    """Route URLs to fixture payloads and record requests."""
    def __init__(self, creatures, documents=DOCUMENTS):
        self.creatures, self.documents, self.urls = creatures, documents, []

    def __call__(self, url):
        self.urls.append(url)
        if "/documents/" in url:
            return copy.deepcopy(self.documents)
        if callable(self.creatures):
            return self.creatures(url)
        return copy.deepcopy(self.creatures)


def listing(items, count=None, next_url=None):
    return {"count": len(items) if count is None else count, "next": next_url, "results": items}


class Open5eProviderTests(unittest.TestCase):
    def run_candidates(self, payload, species="Goblin", display=None, documents=DOCUMENTS):
        fixture = Fixture(payload, documents)
        with patch.object(open5e, "load_json", fixture):
            return open5e.candidates(species, display or {}), fixture

    def test_exact_name_candidates_are_mapped_with_attribution(self):
        result, fixture = self.run_candidates(listing(copy.deepcopy(GOBLINS)))
        self.assertIn("name__iexact=Goblin", fixture.urls[0])
        self.assertIn("fields=key%2Cname%2Cdocument", fixture.urls[0])
        srd, a5e = result
        self.assertEqual((srd["provider"], srd["source"], srd["game_system"]),
                         ("Open5e", "5e 2014 Rules", "5th Edition 2014"))
        self.assertEqual((srd["ac"], srd["hp"], srd["hp_source"]), (15, "2d6", "dice"))
        self.assertEqual(srd["source_url"], BASE + "/creatures/srd_goblin/")
        self.assertTrue(srd["legacy"])
        self.assertFalse(a5e["legacy"])
        self.assertEqual(srd["attribution"],
                         "5e 2014 Rules by Pub srd-2014 (OPEN GAME LICENSE Version 1.0a) via Open5e")
        self.assertEqual((srd["initiative_bonus"], srd["initiative_bonus_status"]), (2, "available"))
        self.assertIsNone(srd["image_url"])
        self.assertEqual(a5e["image_url"], "https://api.open5e.com/static/img/goblin.png")

    def test_ignored_filter_results_are_validated_not_trusted(self):
        other = dict(GOBLINS[0], key="srd_aboleth", name="Aboleth")
        result, _ = self.run_candidates(listing([other, copy.deepcopy(GOBLINS[0])]))
        self.assertEqual([item["source_url"].rsplit("/", 2)[-2] for item in result], ["srd_goblin"])

    def test_zero_matches_is_success_without_catalog_request(self):
        result, fixture = self.run_candidates(listing([]))
        self.assertEqual(result, [])
        self.assertEqual(len(fixture.urls), 1)

    def test_incomplete_or_invalid_listings_raise(self):
        bad = [
            listing(copy.deepcopy(GOBLINS), count=3),
            listing([dict(GOBLINS[0], document=document("unknown", "X", "5e-2014", "5e"))]),
            listing([GOBLINS[0], GOBLINS[0]]),
            listing([dict(GOBLINS[0], key="../evil")]),
            listing([GOBLINS[0]], next_url="https://evil.example/v2/creatures/?page=2"),
            {"results": []},
            listing([None]),
            listing([GOBLINS[0]] * 33, count=33),
        ]
        for payload in bad:
            with self.subTest(payload=str(payload)[:80]), self.assertRaises(open5e.Open5eError):
                self.run_candidates(payload)

    def test_next_pages_are_followed_until_null(self):
        pages = {1: listing([copy.deepcopy(GOBLINS[0])], count=2, next_url=BASE + "/creatures/?page=2"),
                 2: listing([copy.deepcopy(GOBLINS[1])], count=2)}
        result, fixture = self.run_candidates(lambda url: pages[2 if "page=2" in url else 1])
        self.assertEqual(len(result), 2)
        self.assertTrue(any("page=2" in url for url in fixture.urls))

    def test_hit_points_prefer_matching_dice_otherwise_average(self):
        cases = [("20d10 + 40", 150, ("20d10+40", "dice")), ("18d10", 135, ("135", "average")),
                 (None, 165, ("165", "average")), ("2d6", -1, (None, None)), ("2d6", "7", (None, None))]
        for dice, hp, expected in cases:
            with self.subTest(dice=dice, hp=hp):
                self.assertEqual(open5e.hit_points({"hit_dice": dice, "hit_points": hp}), expected)

    def test_initiative_bonus_offer_states(self):
        self.assertEqual(open5e.initiative_offer({"initiative_bonus": None})["initiative_bonus_status"], "missing")
        for raw in ("2", 2.0, True, 2 ** 63):
            with self.subTest(raw=raw):
                self.assertEqual(open5e.initiative_offer({"initiative_bonus": raw})["initiative_bonus_status"], "invalid")
        self.assertEqual(open5e.initiative_offer({"initiative_bonus": -1})["initiative_bonus"], -1)

    def test_illustrations_stay_on_the_configured_https_host(self):
        for path in ("//evil.example/x.png", "https://evil.example/x.png", "", None, 5):
            with self.subTest(path=path):
                self.assertIsNone(open5e.image_url({"illustration": {"file_url": path}}, BASE))

    def test_base_url_requires_plain_https(self):
        for value in ("http://api.open5e.com/v2", "https://user:pw@api.open5e.com/v2",
                      "https://api.open5e.com/v2?x=1", "", None, 5):
            with self.subTest(value=value), self.assertRaises(open5e.Open5eError):
                open5e.base_url({"open5e_base_url": value})
        self.assertEqual(open5e.base_url({}), BASE)
        self.assertEqual(open5e.base_url({"open5e_base_url": BASE + "/"}), BASE)

    def test_source_identity_and_snapshot_round_trip(self):
        result, _ = self.run_candidates(listing(copy.deepcopy(GOBLINS)))
        fields = capture_source_fields(result[0])
        self.assertEqual(fields["monster_source_provider"], "Open5e")
        self.assertEqual(fields["monster_source_book"], "5e 2014 Rules")
        self.assertEqual(validate_source_fields(fields), fields)
        for url in ("https://api.open5e.com/v2/creatures/srd_goblin", "https://evil.example/v2/creatures/x/",
                    "https://api.open5e.com/v2/creatures/../x/"):
            with self.subTest(url=url):
                self.assertEqual(capture_source_fields(dict(result[0], source_url=url)), {})


class Open5eLookupIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.ctx = SimpleNamespace(CONFIG={"display": {"dndbeyond_image_lookup": False,
                                                       "fivetools_fallback": False,
                                                       "open5e_lookup": True}},
                                   dnd_monster_candidates=Mock(return_value=[]))

    def test_candidates_are_signed_with_bonus_offers_after_other_providers(self):
        self.ctx.CONFIG["display"]["fivetools_fallback"] = True
        first = {"provider": "5e.tools", "species": "Goblin", "name": "Goblin"}
        with patch.object(ms, "fivetools_candidates", return_value=[first]), \
                patch.object(open5e, "load_json", Fixture(listing(copy.deepcopy(GOBLINS)))):
            result = ms.lookup_candidates(self.ctx, "Goblin")
        self.assertEqual(result["status"], "ok")
        self.assertEqual([item["provider"] for item in result["candidates"]], ["5e.tools", "Open5e", "Open5e"])
        self.assertEqual([item["provider"] for item in result["providers"]], ["D&D Beyond", "5e.tools", "Open5e"])
        signed = result["candidates"][1]
        self.assertIn("selection_token", signed)
        self.assertIn("initiative_bonus_offer_token", signed)
        image, fields = ms.selected_snapshot(signed["selection_token"], "Goblin")
        self.assertEqual(fields["monster_source_url"], BASE + "/creatures/srd_goblin/")

    def test_open5e_failure_blocks_all_candidates(self):
        self.ctx.CONFIG["display"]["fivetools_fallback"] = True
        with patch.object(ms, "fivetools_candidates", return_value=[{"provider": "5e.tools", "species": "Goblin"}]), \
                patch.object(open5e, "load_json", side_effect=OSError("secret")):
            result = ms.lookup_candidates(self.ctx, "Goblin")
        self.assertEqual((result["status"], result["candidates"]), ("error", []))
        self.assertIn("Open5e", result["reason"])
        self.assertNotIn("secret", repr(result))

    def test_disabled_absent_or_refresh_lookup_never_contacts_open5e(self):
        for display, kwargs in (({"open5e_lookup": False}, {}), ({}, {}),
                                ({"open5e_lookup": True}, {"include_open5e": False})):
            with self.subTest(display=display, kwargs=kwargs):
                self.ctx.CONFIG["display"] = {"dndbeyond_image_lookup": False, "fivetools_fallback": False, **display}
                with patch.object(open5e, "load_json", side_effect=AssertionError("network")):
                    result = ms.lookup_candidates(self.ctx, "Goblin", **kwargs)
                self.assertEqual(result["status"], "ok")
                self.assertEqual(result["providers"][-1], {"provider": "Open5e", "status": "disabled"})

    def test_refresh_skips_retained_open5e_identity_when_disabled(self):
        from python.scrying_glass_monster_refresh_sources import _fetch_exact
        identity = {"monster_source_provider": "Open5e",
                    "monster_source_url": BASE + "/creatures/srd_goblin/"}
        self.ctx.CONFIG["display"] = {"open5e_lookup": False}
        with patch.object(open5e, "load_json", side_effect=AssertionError("network")):
            with self.assertRaisesRegex(ValueError, "Provider disabled"):
                _fetch_exact(self.ctx, {"monster_species": "Goblin"}, identity)

    def test_refresh_resolves_retained_open5e_identity_when_enabled(self):
        from python.scrying_glass_monster_refresh_sources import _fetch_exact
        self.ctx.CONFIG["display"] = {"open5e_lookup": True}
        candidate = {"provider": "Open5e", "name": "Goblin", "source": "SRD", "legacy": True,
                     "source_url": BASE + "/creatures/srd_goblin/", "ac": 15, "hp": "2d6"}
        other = dict(candidate, source="Other", source_url=BASE + "/creatures/other_goblin/")
        identity = {"monster_source_provider": "Open5e", "monster_source_url": candidate["source_url"],
                    "monster_source_name": "Goblin", "monster_source_book": "SRD", "monster_source_legacy": True}
        with patch.object(ms, "open5e_candidates", return_value=[other, candidate]) as lookup:
            self.assertIs(_fetch_exact(self.ctx, {"monster_species": "Goblin"}, identity), candidate)
        lookup.assert_called_once()
        with patch.object(ms, "open5e_candidates", return_value=[other]):
            with self.assertRaisesRegex(ValueError, "missing or ambiguous"):
                _fetch_exact(self.ctx, {"monster_species": "Goblin"}, identity)

    def test_dnd_beyond_and_fivetools_source_attribution(self):
        html = '<footer><p class="source monster-source">\n  Basic Rules (2014), <span>pg. 138</span>\n </p></footer>'
        self.assertEqual(ms.dnd_source_attribution(html), "Basic Rules (2014), pg. 138 via D&D Beyond")
        self.assertIsNone(ms.dnd_source_attribution("<p class='source'>Elsewhere</p>"))
        self.assertIsNone(ms.dnd_source_attribution('<p class="monster-source"> </p>'))
        self.assertEqual(ms.dnd_source_book(html), "Basic Rules (2014)")
        self.assertIsNone(ms.dnd_source_book('<p class="monster-source"> </p>'))
        self.assertEqual(ms.fivetools_source_attribution("MM", {"page": 166}), "MM, page 166 via 5e.tools")
        for page in (None, 0, "166", True, 1.5):
            self.assertIsNone(ms.fivetools_source_attribution("MM", {"page": page}))


class Open5eConfigTests(unittest.TestCase):
    def load(self, text):
        import tempfile
        from pathlib import Path
        from python.scrying_glass_init import load_config
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "config.yaml"
            path.write_text(text, encoding="utf-8")
            return load_config(path)

    def test_defaults_enable_open5e_and_validate_values(self):
        from python.scrying_glass_init import load_config
        self.assertIs(load_config(None)["display"]["open5e_lookup"], True)
        self.assertEqual(self.load("display: {}\n")["display"]["open5e_base_url"], BASE)
        self.assertIs(self.load("display:\n  open5e_lookup: false\n")["display"]["open5e_lookup"], False)
        for text in ("display:\n  open5e_lookup: 'yes'\n", "display:\n  open5e_base_url: http://x.test/v2\n"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                self.load(text)

    def test_example_config_documents_keys(self):
        from pathlib import Path
        text = (Path(__file__).resolve().parents[1] / "config.example.yaml").read_text(encoding="utf-8")
        self.assertIn("open5e_lookup: true", text)
        self.assertIn('open5e_base_url: "https://api.open5e.com/v2"', text)


if __name__ == "__main__":
    unittest.main()
