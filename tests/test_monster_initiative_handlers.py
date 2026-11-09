"""Direct handler regressions; HTTP/authentication remain separate coverage."""
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from fastapi import HTTPException
from python.scrying_glass_admin_monsters import AdminMonstersMixin
from python.scrying_glass_classes import MonsterUpdate
from python.scrying_glass_monster_initiative import initiative_patch, normalize_initiative


def monster(ident="m", bonus=12):
    return dict(id=ident, name="Monster", monster_species="dragon", color="#842029",
                ac=18, hp=20, max_hp=20, original_hp=20, active=True, alive=True,
                visible=True, in_turn=False, **initiative_patch({}, roll=16, bonus=bonus))


class CompatibilityHandlerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.item = monster()
        self.context = SimpleNamespace(
            STATE={"monsters":[self.item], "characters":[], "battle_order":["m"], "battle_round":3},
            random=SimpleNamespace(randint=Mock(return_value=10)),
            combatants_changed=AsyncMock(), HTTPException=HTTPException, MonsterUpdate=MonsterUpdate,
            remember_turn_successors=Mock(), insert_into_battle_order=Mock(),
            clean_order=Mock(), set_turn=Mock(), log_hp_change=Mock(),
        )
        self.handler = AdminMonstersMixin()
        self.handler.context = self.context

    async def test_patch_changed_total_detaches_roll(self):
        result = await self.handler.update_monster("m", MonsterUpdate(initiative=22))
        self.assertEqual(result["initiative"], 22)
        self.assertIsNone(result["initiative_roll"])
        self.assertEqual(result["initiative_bonus"], 12)
        self.assertEqual(normalize_initiative(result)["initiative"], 22)
        self.context.combatants_changed.assert_awaited_once()

    async def test_patch_same_total_keeps_roll(self):
        result = await self.handler.update_monster("m", MonsterUpdate(initiative=28))
        self.assertEqual(result["initiative_roll"], 16)
        self.assertEqual(result["initiative"], 28)

    async def test_patch_clear_preserves_bonus(self):
        result = await self.handler.update_monster("m", MonsterUpdate(initiative=None))
        self.assertIsNone(result["initiative"])
        self.assertIsNone(result["initiative_roll"])
        self.assertEqual(result["initiative_bonus"], 12)

    async def test_unrelated_patch_keeps_relationship(self):
        result = await self.handler.update_monster("m", MonsterUpdate(name="Renamed"))
        self.assertEqual((result["initiative_roll"], result["initiative"]), (16, 28))

    async def test_form_edit_changed_total_detaches_roll(self):
        result = await self.handler.edit_monster(
            "m", name="Monster", monster_species="dragon", ac=18, hp=20,
            max_hp=20, original_hp=20, color="#842029", initiative="22",
            ally="false", image=None,
        )
        self.assertEqual(result["initiative"], 22)
        self.assertIsNone(result["initiative_roll"])
        self.assertEqual(result["initiative_bonus"], 12)

    async def test_individual_roll_replaces_raw_and_adds_bonus(self):
        result = await self.handler.roll_monster_initiative()
        self.assertEqual(result["count"], 1)
        self.assertEqual((self.item["initiative_roll"], self.item["initiative"]), (10, 22))
        self.context.random.randint.assert_called_once_with(1, 20)

    async def test_shared_roll_uses_individual_bonuses_and_selection(self):
        other, untouched = monster("b", -2), monster("c", 3)
        self.context.STATE["monsters"].extend([other, untouched])
        before = copy.deepcopy(untouched)
        self.context.selected_entities = Mock(return_value=[self.item, other])
        result = await self.handler.bulk_monsters(SimpleNamespace(action="roll-shared-initiative", ids=["m","b"]))
        self.assertEqual(result["count"], 2)
        self.assertEqual((self.item["initiative"], other["initiative"]), (22, 8))
        self.assertEqual((self.item["initiative_roll"], other["initiative_roll"]), (10, 10))
        self.assertEqual(untouched, before)
        self.context.random.randint.assert_called_once_with(1, 20)
