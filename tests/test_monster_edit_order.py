"""Direct Edit/order integration using the existing handler fixture."""
import copy
import unittest
from types import SimpleNamespace
from fastapi import HTTPException


class MonsterEditOrderTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from test_monster_initiative_bonus_edit import MonsterBonusEditTests
        fixture = MonsterBonusEditTests("test_bonus_recalculates_retained_raw")
        fixture.setUp()
        self.handler = fixture.handler
        self.context = fixture.context
        self.monster = fixture.monster
        self.arguments = dict(fixture.args, initiative="14")
        self.monster.update(initiative=14, initiative_roll=2)
        self.context.STATE.update(battle_order=["c", "m"], battle_round=4)

    async def test_bonus_edit_reorders_and_keeps_turn_round_and_character(self):
        before = copy.deepcopy(self.context.STATE["characters"])
        result = await self.handler.edit_monster(**self.arguments, initiative_bonus="30")
        self.assertEqual(result["initiative"], 32)
        self.assertEqual(self.context.STATE["battle_order"], ["m", "c"])
        self.assertTrue(result["in_turn"])
        self.assertEqual(self.context.STATE["battle_round"], 4)
        self.assertEqual(self.context.STATE["characters"], before)
        self.context.combatants_changed.assert_awaited_once_with(monsters=True, characters=False)

    async def test_retained_legacy_total_does_not_reorder(self):
        self.monster["initiative_roll"] = None
        await self.handler.edit_monster(**self.arguments, initiative_bonus="30")
        self.assertEqual(self.monster["initiative"], 14)
        self.assertEqual(self.context.STATE["battle_order"], ["c", "m"])

    async def test_invalid_order_rejected_before_image_and_mutation(self):
        self.context.STATE["battle_order"] = ["missing", "m"]
        before = copy.deepcopy(self.context.STATE)
        with self.assertRaises(HTTPException) as error:
            await self.handler.edit_monster(**dict(self.arguments,
                image=SimpleNamespace(filename="new.png")), initiative_bonus="30")
        self.assertEqual(error.exception.status_code, 409)
        self.assertEqual(self.context.STATE, before)
        self.context.save_image.assert_not_called()
        self.context.combatants_changed.assert_not_awaited()
