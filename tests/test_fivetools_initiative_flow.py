"""Secured ASGI/SQLite with mocked JSON transport; not live-provider/browser tests."""
import copy
import unittest
from urllib.parse import urlencode
from unittest.mock import patch
import test_source_bonus_offer_acceptance as creation
import test_monster_refresh_review as reviews
from test_fivetools_initiative import noble
from python import scrying_glass_monster_selection as selection
from python.scrying_glass_monster_refresh_review import install_monster_refresh
from python.scrying_glass_storage import SQLiteStorage


class FivetoolsInitiativeFlowTests(unittest.IsolatedAsyncioTestCase):
    request = creation.SourceBonusOfferAcceptanceTests.request
    form = creation.SourceBonusOfferAcceptanceTests.form
    snapshot = creation.SourceBonusOfferAcceptanceTests.snapshot
    json_request = reviews.MonsterRefreshReviewTests.json_request

    def setUp(self):
        creation.SourceBonusOfferAcceptanceTests.setUp(self)
        install_monster_refresh(self.context, self.app)
        self.context.CONFIG["display"].update(dndbeyond_image_lookup=False,
            fivetools_fallback=True, fivetools_sources=["XMM"])
        self.source = noble(ac=[16], hp={"average": 148})
        def load(url):
            if url.endswith("/index.json"):
                return {"XMM": "bestiary-xmm.json"}
            if url.endswith("/bestiary-xmm.json"):
                return {"monster": [copy.deepcopy(self.source)]}
            raise AssertionError(url)
        patcher = patch.object(selection.ft, "load_json", side_effect=load)
        patcher.start()
        self.addCleanup(patcher.stop)

    async def candidate(self):
        status, result = await self.request("GET", "/api/monsters/lookup",
            query=urlencode({"species": "Noble Prodigy"}))
        self.assertEqual((status, result["status"], len(result["candidates"])), (200, "ok", 1))
        return result["candidates"][0]

    async def create(self):
        fields = dict(self.form(await self.candidate()), name="Noble Prodigy", monster_species="Noble Prodigy")
        status, created = await self.request("POST", "/api/monsters", fields=fields)
        self.assertEqual(status, 200)
        return created[0]

    def reopen(self):
        self.context.STORAGE.close()
        self.context.STORAGE = SQLiteStorage(self.directory / "scrying-glass.sqlite3")
        self.context.load_state()
        return self.context.STATE["monsters"]

    async def preview(self, ident):
        before = self.snapshot()
        status, review = await self.json_request("/api/monsters/refresh/preview", {"ids": [ident]})
        self.assertEqual(status, 200)
        self.assertEqual(self.snapshot(), before)
        return review

    async def apply(self, review, ident):
        return await self.json_request("/api/monsters/refresh/apply",
            {"review_id": review["review_id"], "selected": {ident: ["initiative_bonus"]}})

    async def test_creation_signed_values_source_identity_and_storage_reopen(self):
        for value in (7, 0, -2):
            self.source["initiative"] = {"proficiency": 1} if value == 7 else {"initiative": value}
            candidate = await self.candidate()
            self.assertEqual(candidate["initiative_bonus"], value)
            self.assertIn("initiative_bonus_offer_token", candidate)
            created = await self.create()
            item = next(item for item in self.reopen() if item["id"] == created["id"])
            self.assertEqual((item["initiative_bonus"], item["initiative_bonus_origin"]), (value, "source"))
            self.assertEqual(item["monster_source_url"], "https://5e.tools/bestiary.html#noble%20prodigy_xmm")
            self.assertEqual(item["monster_source_book"], "XMM")
            self.assertIsNone(item["initiative_roll"])
            self.assertIsNone(item["initiative"])

    async def test_refresh_recalculation_missing_invalid_and_exact_edition(self):
        created = await self.create()
        ident = created["id"]
        item = self.context.STATE["monsters"][0]
        item.update(initiative_bonus=2, initiative_bonus_origin="manual", initiative_roll=16, initiative=18)
        await self.context.combatants_changed(monsters=True)
        self.context.hp_value_factory.reset_mock()
        before = copy.deepcopy(item)
        review = await self.preview(ident)
        fields = review["rows"][0]["fields"]
        self.assertEqual(fields["initiative_bonus"]["proposed"], 7)
        self.assertTrue(all(not field["checked"] for field in fields.values()))
        self.assertEqual((await self.apply(review, ident))[0], 200)
        restored = self.reopen()[0]
        self.assertEqual((restored["initiative_bonus"], restored["initiative_roll"], restored["initiative"]), (7, 16, 23))
        self.assertEqual(restored["initiative_bonus_origin"], "source")
        for key in ("hp", "max_hp", "ac", "monster_source_url"):
            self.assertEqual(restored[key], before[key])
        self.context.hp_value_factory.assert_not_called()
        for raw in (None, {"proficiency": "1"}):
            self.source.pop("initiative", None)
            if raw is not None:
                self.source["initiative"] = raw
            candidate = await self.candidate()
            self.assertIsNone(candidate["initiative_bonus"])
            self.assertNotIn("initiative_bonus_offer_token", candidate)
            before = self.snapshot()
            review = await self.preview(ident)
            self.assertFalse(review["rows"][0]["fields"]["initiative_bonus"]["enabled"])
            self.assertEqual((await self.apply(review, ident))[0], 422)
            self.assertEqual(self.snapshot(), before)
        self.source["source"] = "MM"
        self.assertEqual((await self.preview(ident))["rows"][0]["status"], "failed")


if __name__ == "__main__":
    unittest.main()
