"""Offline SG-TODO-016 source/monster catalog fixtures; no network access."""
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch
from fastapi import FastAPI, HTTPException, Request
from fastapi.testclient import TestClient
from python import scrying_glass_fivetools as ft
from python import scrying_glass_open5e as open5e
from python import scrying_glass_monster_selection as ms
from python import scrying_glass_provider_settings as settings
from python import scrying_glass_source_catalog as catalog
from test_open5e_provider import DOCUMENTS, GOBLINS, SRD, A5E, Fixture, listing

DISPLAY = {"fivetools_sources": ["MM", "XMM"], "open5e_lookup": True}
BESTIARY = {
    "index.json": {"MM": "bestiary-mm.json", "XMM": "bestiary-xmm.json"},
    "bestiary-mm.json": {"monster": [
        {"name": "Goblin", "source": "MM", "ac": [15], "hp": {"average": 7, "formula": "2d6"}},
        {"name": "aboleth", "source": "MM", "ac": [17], "hp": {"average": 135, "formula": "18d10+36"}},
        {"name": "Copy only", "source": "MM", "_copy": {"name": "Goblin"}},
        {"name": "Elsewhere", "source": "XMM", "ac": [10], "hp": {"average": 1}}]},
    "bestiary-xmm.json": {"monster": []},
}


def fivetools(url):
    return copy.deepcopy(BESTIARY[url.rsplit("/", 1)[1]])


class CatalogFunctionTests(unittest.TestCase):
    def setUp(self):
        patcher = patch.object(ft, "load_json", side_effect=fivetools)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_sources_list_configured_books_then_open5e_documents_without_dnd_beyond(self):
        with patch.object(open5e, "load_json", Fixture(listing([]))):
            result = catalog.sources(DISPLAY)
        self.assertEqual([(item["provider"], item["source"]) for item in result["sources"]],
                         [("5e.tools", "MM"), ("5e.tools", "XMM"), ("Open5e", "srd-2014"), ("Open5e", "a5e-mm")])
        self.assertEqual(result["sources"][2]["label"], "5e 2014 Rules")
        self.assertTrue(result["sources"][2]["legacy"])
        self.assertFalse(result["sources"][3]["legacy"])
        self.assertEqual(result["unavailable"], [])

    def test_disabled_providers_are_not_offered_and_open5e_failure_is_reported(self):
        self.assertEqual(catalog.sources(dict(DISPLAY, fivetools_fallback=False, open5e_lookup=False))["sources"], [])
        with patch.object(open5e, "load_json", side_effect=open5e.Open5eError("down")):
            result = catalog.sources(DISPLAY)
        self.assertEqual([item["provider"] for item in result["sources"]], ["5e.tools", "5e.tools"])
        self.assertEqual(result["unavailable"], ["Open5e"])
        with self.assertRaisesRegex(LookupError, "Provider disabled"):
            catalog.monsters(dict(DISPLAY, open5e_lookup=False), "Open5e", "srd-2014")

    def test_fivetools_source_lists_usable_monsters_sorted_and_signs_a_pick(self):
        result = catalog.monsters(DISPLAY, "5e.tools", "MM")
        self.assertEqual(result, {"status": "ok", "complete": True,
                                  "monsters": [{"id": "aboleth", "name": "aboleth"}, {"id": "Goblin", "name": "Goblin"}]})
        self.assertEqual(catalog.monsters(DISPLAY, "5e.tools", "XMM")["monsters"], [])
        with self.assertRaises(ValueError):
            catalog.monsters(DISPLAY, "5e.tools", "PHB")
        candidate = catalog.monster(DISPLAY, "5e.tools", "MM", "Goblin")["candidate"]
        self.assertEqual((candidate["name"], candidate["species"], candidate["source"], candidate["ac"]),
                         ("Goblin", "Goblin", "MM", 15))
        image, fields = ms.selected_snapshot(candidate["selection_token"], "Goblin")
        self.assertEqual(fields["monster_source_book"], "MM")
        with self.assertRaises(KeyError):
            catalog.monster(DISPLAY, "5e.tools", "MM", "Copy only")

    def test_open5e_document_list_is_validated_complete_and_sorted(self):
        items = [{"key": "srd_zombie", "name": "Zombie", "document": SRD},
                 {"key": "srd_goblin", "name": "Goblin", "document": SRD}]
        fixture = Fixture(listing(items))
        with patch.object(open5e, "load_json", fixture):
            result = catalog.monsters(DISPLAY, "Open5e", "srd-2014")
        self.assertIn("document__key=srd-2014", fixture.urls[-1])
        self.assertEqual([item["name"] for item in result["monsters"]], ["Goblin", "Zombie"])
        for bad, message in ((listing(items + [{"key": "x", "name": "X", "document": A5E}]), "another document"),
                             (listing(items, count=3), "Incomplete"),
                             (listing([items[0], items[0]]), "duplicate")):
            with self.subTest(message=message), patch.object(open5e, "load_json", Fixture(bad)):
                with self.assertRaisesRegex(open5e.Open5eError, message):
                    catalog.monsters(DISPLAY, "Open5e", "srd-2014")
        with patch.object(open5e, "load_json", Fixture(listing([]))):
            with self.assertRaisesRegex(open5e.Open5eError, "Unknown Open5e document"):
                catalog.monsters(DISPLAY, "Open5e", "tob")

    def test_open5e_pick_is_a_signed_candidate_from_the_chosen_document(self):
        with patch.object(open5e, "load_json", Fixture(copy.deepcopy(GOBLINS[0]))):
            candidate = catalog.monster(DISPLAY, "Open5e", "srd-2014", "srd_goblin")["candidate"]
        self.assertEqual((candidate["species"], candidate["source"], candidate["ac"], candidate["hp"]),
                         ("Goblin", "5e 2014 Rules", 15, "2d6"))
        self.assertIn("initiative_bonus_offer_token", candidate)
        ms.selected_snapshot(candidate["selection_token"], "Goblin")
        with patch.object(open5e, "load_json", Fixture(copy.deepcopy(GOBLINS[1]))):
            with self.assertRaisesRegex(open5e.Open5eError, "not in the chosen document"):
                catalog.monster(DISPLAY, "Open5e", "srd-2014", "a5e-mm_goblin")
        with self.assertRaisesRegex(open5e.Open5eError, "Invalid Open5e creature key"):
            catalog.monster(DISPLAY, "Open5e", "srd-2014", "../documents")


class CatalogRouteTests(unittest.TestCase):
    def setUp(self):
        def require(role, cookie):
            async def guard(request: Request):
                if request.cookies.get(cookie) != "alice":
                    raise HTTPException(401, "Sign in required")
            return guard
        context = SimpleNamespace(ADMIN_SESSION_COOKIE="admin", require=require)
        patcher = patch.object(settings, "effective_display", return_value=dict(DISPLAY, open5e_lookup=False))
        patcher.start()
        self.addCleanup(patcher.stop)
        ft_patch = patch.object(ft, "load_json", side_effect=fivetools)
        ft_patch.start()
        self.addCleanup(ft_patch.stop)
        app = FastAPI()
        catalog.install_source_catalog_routes(context, app)
        self.client = TestClient(app)

    def get(self, url, user="alice"):
        self.client.cookies.set("admin", user)
        return self.client.get(url)

    def test_routes_require_admin_and_validate_input(self):
        self.assertEqual(self.get("/api/monsters/catalog/sources", user="nobody").status_code, 401)
        self.assertEqual(len(self.get("/api/monsters/catalog/sources").json()["sources"]), 2)
        self.assertEqual(self.get("/api/monsters/catalog/monsters?provider=D%26D%20Beyond&source=MM").status_code, 400)
        self.assertEqual(self.get("/api/monsters/catalog/monsters?provider=Open5e&source=srd-2014").status_code, 409)
        self.assertEqual(self.get("/api/monsters/catalog/monster?provider=5e.tools&source=MM&id=Nope").status_code, 404)
        failed = self.get("/api/monsters/catalog/monsters?provider=5e.tools&source=PHB").json()
        self.assertEqual(failed["status"], "error")
        picked = self.get("/api/monsters/catalog/monster?provider=5e.tools&source=MM&id=Goblin").json()
        self.assertEqual(picked["candidate"]["name"], "Goblin")


if __name__ == "__main__":
    unittest.main()
