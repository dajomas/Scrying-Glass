"""Direct creation/constructor checks; not authenticated HTTP or storage tests."""
import unittest
from types import SimpleNamespace
from fastapi import HTTPException
from python import scrying_glass_monster_selection as selection
from python.scrying_glass_monster_source_snapshot import PROVIDER, URL, NAME, BOOK, LEGACY


class SelectedSourceCreationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from test_manual_monster_bonus_creation import ManualBonusCreationTests
        fixture=ManualBonusCreationTests("test_explicit_manual_bonus_and_unset_roll_total")
        fixture.setUp()
        self.handler=fixture.handler
        self.context=fixture.context
        self.arguments=fixture.arguments
        self.candidate=dict(species="dragon",name="Dragon",provider="5e.tools",
            source="XMM",legacy=False,source_url="https://5e.tools/bestiary.html#dragon_xmm",
            image_url="https://example.test/dragon.png")

    async def create(self, **changes):
        return await self.handler.create_monster(**dict(self.arguments,**changes))

    async def test_valid_source_is_retained_without_changing_bonus_provenance(self):
        result=await self.create(selection_token=selection.issue_token(self.candidate))
        self.assertEqual(result[0][PROVIDER],"5e.tools")
        self.assertEqual(result[0][URL],self.candidate["source_url"])
        self.assertEqual((result[0][NAME],result[0][BOOK],result[0][LEGACY]),("Dragon","XMM",False))
        self.assertEqual(result[0]["initiative_bonus_origin"],"default")
        self.assertIsNone(result[0]["initiative_roll"])
        self.context.dnd_image.assert_not_called()

    async def test_quantity_copies_keep_identity_and_unique_ids(self):
        result=await self.create(quantity=2,selection_token=selection.issue_token(self.candidate))
        self.assertEqual(len({item["id"] for item in result}),2)
        self.assertTrue(all(item[URL]==self.candidate["source_url"] for item in result))

    async def test_uploaded_image_preserves_valid_selected_identity(self):
        result=await self.create(image=SimpleNamespace(filename="dragon.png"),
            selection_token=selection.issue_token(self.candidate))
        self.assertEqual(result[0]["image_url"],"/media/new.png")
        self.assertEqual(result[0][URL],self.candidate["source_url"])
        self.context.dnd_image.assert_not_called()

    async def test_invalid_token_cannot_supply_identity_when_upload_wins(self):
        result=await self.create(image=SimpleNamespace(filename="dragon.png"),selection_token="invalid")
        self.assertEqual(result[0]["image_url"],"/media/new.png")
        self.assertNotIn(PROVIDER,result[0])
        self.assertNotIn(URL,result[0])

    async def test_manual_selection_does_not_invent_identity(self):
        result=await self.create(selection_token="manual")
        self.assertNotIn(PROVIDER,result[0])
        self.assertNotIn(URL,result[0])

    async def test_mismatched_species_is_rejected_without_append(self):
        candidate=dict(self.candidate,species="different")
        with self.assertRaises(HTTPException) as error:
            await self.create(selection_token=selection.issue_token(candidate))
        self.assertEqual(error.exception.status_code,422)
        self.assertEqual(self.context.STATE["monsters"],[])
        self.context.combatants_changed.assert_not_awaited()
