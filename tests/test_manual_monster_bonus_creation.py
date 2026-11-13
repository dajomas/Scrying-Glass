"""Direct active creation-handler checks; not authenticated HTTP tests."""
import copy
import unittest
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
from python.scrying_glass_monster_selection import CandidateMonstersMixin, issue_token
from python.scrying_glass_service_images import ImagesService


class ManualBonusCreationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.context = SimpleNamespace(uuid=uuid, HTTPException=HTTPException,
            STATE=dict(monsters=[], characters=[], battle_order=[]),
            hp_value_factory=Mock(return_value=Mock(return_value=20)),
            dnd_image=Mock(return_value=None), save_image=Mock(return_value="/media/new.png"),
            combatants_changed=AsyncMock())
        self.images = ImagesService(self.context)
        self.context.make_monster = Mock(wraps=self.images.make_monster)
        self.handler = CandidateMonstersMixin()
        self.handler.context = self.context
        self.arguments = dict(name="Dragon", monster_species="dragon", ac=18,
            hprangestart="20", hprangeend="", color="#842029", quantity=1,
            image=None, selection_token="manual")

    async def test_explicit_manual_bonus_and_unset_roll_total(self):
        result = await self.handler.create_monster(**self.arguments, initiative_bonus="+12")
        self.assertEqual((result[0]["initiative_bonus"],result[0]["initiative_bonus_origin"]),(12,"manual"))
        self.assertIsNone(result[0]["initiative_roll"])
        self.assertIsNone(result[0]["initiative"])
        self.assertIsNone(result[0]["original_initiative"])
        self.context.dnd_image.assert_not_called()
        self.context.combatants_changed.assert_awaited_once_with(monsters=True, characters=False)

    async def test_omitted_bonus_direct_call_default(self):
        result = await self.handler.create_monster(**self.arguments)
        self.assertEqual((result[0]["initiative_bonus"],result[0]["initiative_bonus_origin"]),(0,"default"))
        self.assertIsNone(result[0]["initiative_roll"])

    async def test_explicit_zero_and_blank_have_distinct_origins(self):
        zero = await self.handler.create_monster(**self.arguments, initiative_bonus="0")
        blank = await self.handler.create_monster(**self.arguments, initiative_bonus="")
        self.assertEqual(zero[0]["initiative_bonus_origin"],"manual")
        self.assertEqual(blank[0]["initiative_bonus_origin"],"default")

    async def test_invalid_bonus_before_side_effects(self):
        arguments = dict(self.arguments,image=SimpleNamespace(filename="new.png"))
        with self.assertRaises(HTTPException) as error:
            await self.handler.create_monster(**arguments,initiative_bonus="12 bonus")
        self.assertEqual(error.exception.status_code,422)
        self.context.hp_value_factory.assert_not_called()
        self.context.dnd_image.assert_not_called()
        self.context.save_image.assert_not_called()
        self.context.make_monster.assert_not_called()
        self.context.combatants_changed.assert_not_awaited()
        self.assertEqual(self.context.STATE["monsters"],[])

    async def test_quantity_keeps_negative_bonus_and_unique_ids(self):
        result = await self.handler.create_monster(**dict(self.arguments,quantity=3),initiative_bonus="-2")
        self.assertEqual(len(result),3)
        self.assertEqual(len({item["id"] for item in result}),3)
        self.assertTrue(all(item["initiative_bonus"] == -2 and item["initiative_bonus_origin"] == "manual" for item in result))
        self.assertTrue(all(item["initiative_roll"] is None and item["initiative"] is None for item in result))

    async def test_scope_change_during_lookup_still_rejected(self):
        old_state = self.context.STATE
        def change_scope(species):
            self.context.STATE = dict(monsters=[],characters=[],battle_order=[])
            return None
        self.context.dnd_image.side_effect = change_scope
        with self.assertRaises(HTTPException) as error:
            await self.handler.create_monster(**dict(self.arguments,selection_token=""),initiative_bonus="12")
        self.assertEqual(error.exception.status_code,409)
        self.assertEqual(old_state["monsters"],[])
        self.assertEqual(self.context.STATE["monsters"],[])
        self.context.make_monster.assert_not_called()
        self.context.combatants_changed.assert_not_awaited()

    async def test_selected_image_snapshot_is_retained(self):
        token = issue_token(dict(species="dragon",image_url="https://example.test/dragon.png"))
        result = await self.handler.create_monster(**dict(self.arguments,selection_token=token),initiative_bonus="12")
        self.assertEqual(result[0]["image_url"],"https://example.test/dragon.png")
        self.assertEqual(result[0]["initiative_bonus"],12)
        self.context.dnd_image.assert_not_called()

    async def test_uploaded_image_precedence_is_unchanged(self):
        arguments = dict(self.arguments,image=SimpleNamespace(filename="new.png"),selection_token="invalid-token")
        result = await self.handler.create_monster(**arguments,initiative_bonus="12")
        self.assertEqual(result[0]["image_url"],"/media/new.png")
        self.assertEqual(result[0]["initiative_bonus"],12)
        self.context.save_image.assert_called_once()
        self.context.dnd_image.assert_not_called()
