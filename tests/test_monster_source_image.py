"""Direct handler tests for choosing a monster image from a looked-up source."""
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
from python.scrying_glass_classes import MonsterUpdate
from python.scrying_glass_monster_initiative_edit import InitiativeEditMonstersMixin
from python.scrying_glass_monster_selection import issue_token

IMAGE = "https://example.test/goblin.png"


def token(species="goblin", image=IMAGE):
    return issue_token({"species": species, "image_url": image})


class MonsterSourceImageTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.monsters = [dict(id=i, name=f"Goblin {i}", monster_species="goblin", ac=15, hp=7, max_hp=7,
            original_hp=7, color="#842029", active=False, alive=True, in_turn=False, initiative=None,
            initiative_roll=None, initiative_bonus=0, initiative_bonus_origin="default",
            original_initiative=None, effects=[], image_url="/media/old.png") for i in ("a", "b", "c")]
        state = dict(monsters=self.monsters, characters=[], battle_order=[], round=0)
        self.context = SimpleNamespace(STATE=state, MonsterUpdate=MonsterUpdate, HTTPException=HTTPException,
            save_image=Mock(return_value="/media/upload.png"), remember_turn_successors=Mock(),
            insert_into_battle_order=Mock(), clean_order=Mock(), combatants_changed=AsyncMock(),
            selected_entities=lambda kind, ids: [m for m in state[kind] if m["id"] in ids]
                if all(any(m["id"] == i for m in state[kind]) for i in ids)
                else (_ for _ in ()).throw(HTTPException(404, "Selected monster no longer exists")))
        self.handler = InitiativeEditMonstersMixin()
        self.handler.context = self.context

    async def edit(self, **changes):
        args = dict(ident="a", name="Goblin a", monster_species="goblin", ac=15, hp=7, max_hp=7,
                    original_hp=7, color="#842029", initiative="", ally="false", image=None)
        return await self.handler.edit_monster(**dict(args, **changes))

    async def test_edit_uses_the_signed_source_image(self):
        """Edit saves the image of the chosen source candidate."""
        result = await self.edit(image_selection_token=token(), image_species="goblin")
        self.assertEqual(result["image_url"], IMAGE)

    async def test_edit_upload_takes_precedence_over_source_image(self):
        """Edit prefers an uploaded file over a chosen source image."""
        upload = SimpleNamespace(filename="mine.png")
        result = await self.edit(image=upload, image_selection_token=token())
        self.assertEqual(result["image_url"], "/media/upload.png")

    async def test_edit_rejects_a_tampered_token(self):
        """Edit rejects a source image token with a bad signature."""
        with self.assertRaises(HTTPException) as caught:
            await self.edit(image_selection_token=token()[:-2] + "00", image_species="goblin")
        self.assertEqual(caught.exception.status_code, 422)
        self.assertEqual(self.monsters[0]["image_url"], "/media/old.png")

    async def test_edit_without_token_keeps_the_image(self):
        """Edit without upload or source choice keeps the current image."""
        result = await self.edit()
        self.assertEqual(result["image_url"], "/media/old.png")

    async def test_bulk_sets_the_image_on_all_selected_monsters(self):
        """Bulk action sets the chosen source image on every selected monster only."""
        result = await self.handler.set_monster_source_image(
            {"ids": ["a", "c"], "image_selection_token": token("Goblin"), "image_species": "Goblin"})
        self.assertEqual(result["count"], 2)
        self.assertEqual([m["image_url"] for m in self.monsters], [IMAGE, "/media/old.png", IMAGE])
        self.context.combatants_changed.assert_awaited_once_with(monsters=True, characters=False)

    async def test_bulk_rejects_species_mismatch_and_missing_image(self):
        """Bulk action rejects a token for another species or without an image."""
        for body in ({"ids": ["a"], "image_selection_token": token("orc"), "image_species": "goblin"},
                     {"ids": ["a"], "image_selection_token": token(image=None), "image_species": "goblin"},
                     {"ids": [], "image_selection_token": token(), "image_species": "goblin"}):
            with self.subTest(body=body), self.assertRaises(HTTPException) as caught:
                await self.handler.set_monster_source_image(body)
            self.assertEqual(caught.exception.status_code, 422)
        self.assertTrue(all(m["image_url"] == "/media/old.png" for m in self.monsters))
        self.context.combatants_changed.assert_not_awaited()

    async def test_bulk_rejects_unknown_monsters(self):
        """Bulk action fails without changes when a selected monster is gone."""
        with self.assertRaises(HTTPException) as caught:
            await self.handler.set_monster_source_image(
                {"ids": ["a", "zz"], "image_selection_token": token(), "image_species": "goblin"})
        self.assertEqual(caught.exception.status_code, 404)
        self.assertEqual(self.monsters[0]["image_url"], "/media/old.png")

    def test_route_is_registered_as_authenticated_post(self):
        """The bulk source-image route is an authenticated POST."""
        from python.scrying_glass_api_admin import ADMIN_ROUTES
        self.assertIn(("/api/monsters/source-image", "set_monster_source_image", "POST", True), ADMIN_ROUTES)


if __name__ == "__main__":
    unittest.main()
