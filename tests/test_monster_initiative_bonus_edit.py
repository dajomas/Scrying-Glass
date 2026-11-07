"""Direct edit-handler tests; not authenticated HTTP or storage acceptance."""
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
from python.scrying_glass_classes import MonsterUpdate
from python.scrying_glass_monster_initiative_edit import InitiativeEditMonstersMixin


class MonsterBonusEditTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.monster = dict(id="m", name="Dragon", monster_species="dragon", ac=18,
            hp=20, max_hp=20, original_hp=20, color="#842029", active=True,
            alive=True, in_turn=True, initiative=28, initiative_roll=16,
            initiative_bonus=12, initiative_bonus_origin="source",
            original_initiative=None, effects=[])
        self.context = SimpleNamespace(STATE=dict(monsters=[self.monster],
            characters=[dict(id="c", initiative=21)], battle_order=["m", "c"], round=4),
            MonsterUpdate=MonsterUpdate, HTTPException=HTTPException,
            save_image=Mock(return_value="/media/new.png"),
            remember_turn_successors=Mock(), insert_into_battle_order=Mock(),
            clean_order=Mock(), combatants_changed=AsyncMock())
        self.handler = InitiativeEditMonstersMixin()
        self.handler.context = self.context
        self.args = dict(ident="m", name="Dragon", monster_species="dragon", ac=18,
            hp=20, max_hp=20, original_hp=20, color="#842029", initiative="28",
            ally="false", image=None)

    async def edit(self, **changes):
        return await self.handler.edit_monster(**dict(self.args, **changes))

    async def test_bonus_recalculates_retained_raw(self):
        result = await self.edit(initiative_bonus="10")
        self.assertEqual((result["initiative"], result["initiative_roll"]), (26, 16))
        self.assertEqual(result["initiative_bonus_origin"], "manual")
        self.assertIsNone(result["original_initiative"])
        self.context.combatants_changed.assert_awaited_once_with(monsters=True, characters=False)
        self.context.insert_into_battle_order.assert_called_once_with(self.monster)

    async def test_omitted_bonus_keeps_source_assignment(self):
        await self.edit()
        self.assertEqual((self.monster["initiative"], self.monster["initiative_bonus_origin"]), (28, "source"))

    async def test_blank_bonus_keeps_source_assignment(self):
        await self.edit(initiative_bonus="  ")
        self.assertEqual((self.monster["initiative_bonus"], self.monster["initiative_bonus_origin"]), (12, "source"))

    async def test_explicit_zero_is_manual(self):
        await self.edit(initiative_bonus="0")
        self.assertEqual((self.monster["initiative"], self.monster["initiative_bonus_origin"]), (16, "manual"))

    async def test_negative_bonus(self):
        await self.edit(initiative_bonus="-2")
        self.assertEqual(self.monster["initiative"], 14)

    async def test_legacy_total_is_not_reinterpreted(self):
        self.monster["initiative_roll"] = None
        await self.edit(initiative_bonus="10")
        self.assertEqual(self.monster["initiative"], 28)
        self.assertIsNone(self.monster["initiative_roll"])

    async def test_unset_total_remains_unset(self):
        self.monster.update(initiative=None, initiative_roll=None)
        await self.edit(initiative="", initiative_bonus="12")
        self.assertIsNone(self.monster["initiative"])

    async def test_legacy_total_change_detaches_raw_before_bonus(self):
        await self.edit(initiative="22", initiative_bonus="10")
        self.assertEqual(self.monster["initiative"], 22)
        self.assertIsNone(self.monster["initiative_roll"])

    async def test_unchanged_derived_total_outside_legacy_input_bound(self):
        self.monster.update(initiative=112, initiative_bonus=96)
        await self.edit(initiative="112", initiative_bonus="+100")
        self.assertEqual(self.monster["initiative"], 116)

    async def test_repeated_edit_does_not_compound(self):
        await self.edit(initiative_bonus="10")
        await self.edit(initiative="26", initiative_bonus="10")
        self.assertEqual(self.monster["initiative"], 26)

    async def test_invalid_bonus_has_no_side_effects(self):
        for value in ("12 bonus", "1.5", "9223372036854775808"):
            with self.subTest(value=value):
                before = copy.deepcopy(self.context.STATE)
                with self.assertRaises(HTTPException) as error:
                    await self.edit(initiative_bonus=value, image=SimpleNamespace(filename="new.png"))
                self.assertEqual(error.exception.status_code, 422)
                self.assertEqual(self.context.STATE, before)
        self.context.save_image.assert_not_called()
        self.context.remember_turn_successors.assert_not_called()
        self.context.combatants_changed.assert_not_awaited()

    async def test_invalid_health_has_no_side_effects(self):
        before = copy.deepcopy(self.context.STATE)
        with self.assertRaises(HTTPException):
            await self.edit(hp=-1, initiative_bonus="10")
        self.assertEqual(self.context.STATE, before)
        self.context.combatants_changed.assert_not_awaited()

    async def test_missing_monster(self):
        with self.assertRaises(HTTPException) as error:
            await self.edit(ident="missing", initiative_bonus="10")
        self.assertEqual(error.exception.status_code, 404)

    async def test_character_round_turn_and_unrelated_fields_retained(self):
        before = copy.deepcopy(self.context.STATE)
        await self.edit(initiative_bonus="10")
        self.assertEqual(self.context.STATE["characters"], before["characters"])
        self.assertEqual(self.context.STATE["round"], 4)
        self.assertTrue(self.monster["in_turn"])
        self.assertEqual(self.monster["hp"], 20)
        self.context.clean_order.assert_called_once()
