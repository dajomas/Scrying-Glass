"""Direct raw-roll mutation checks; not authenticated HTTP/storage acceptance."""
import copy
import unittest
from fastapi import HTTPException
from python.scrying_glass_monster_raw_roll import apply_raw_roll


class RawRollHandlerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from test_monster_initiative_bonus_edit import MonsterBonusEditTests
        fixture=MonsterBonusEditTests("test_bonus_recalculates_retained_raw")
        fixture.setUp()
        self.context=fixture.context
        self.monster=fixture.monster
        self.context.STATE["battle_round"]=4

    async def test_roll_recalculates_and_reorders_without_turn_or_character_changes(self):
        characters=copy.deepcopy(self.context.STATE["characters"])
        result=await apply_raw_roll(self.context,"m",{"initiative_roll":0})
        self.assertEqual((result["initiative_roll"],result["initiative"]),(0,12))
        self.assertEqual(self.context.STATE["battle_order"],["c","m"])
        self.assertTrue(result["in_turn"])
        self.assertEqual(self.context.STATE["battle_round"],4)
        self.assertEqual(self.context.STATE["characters"],characters)
        self.context.combatants_changed.assert_awaited_once_with(monsters=True,characters=False)

    async def test_active_clear_is_rejected_without_mutation(self):
        before=copy.deepcopy(self.context.STATE)
        with self.assertRaises(HTTPException) as error:
            await apply_raw_roll(self.context,"m",{"initiative_roll":None})
        self.assertEqual(error.exception.status_code,400)
        self.assertEqual(self.context.STATE,before)
        self.context.combatants_changed.assert_not_awaited()

    async def test_inactive_clear_is_explicit_and_does_not_start_battle(self):
        self.monster["active"]=False
        self.context.STATE["battle_order"]=[]
        result=await apply_raw_roll(self.context,"m",{"initiative_roll":None})
        self.assertIsNone(result["initiative"])
        self.assertIsNone(result["initiative_roll"])
        self.assertEqual(result["initiative_bonus"],12)
        self.assertEqual(self.context.STATE["battle_order"],[])

    async def test_invalid_input_and_order_are_atomic(self):
        for body in ({"initiative_roll":True},{"initiative_roll":16,"initiative":28}):
            before=copy.deepcopy(self.context.STATE)
            with self.assertRaises(HTTPException) as error:
                await apply_raw_roll(self.context,"m",body)
            self.assertEqual(error.exception.status_code,422)
            self.assertEqual(self.context.STATE,before)
        self.context.STATE["battle_order"]=["missing","m"]
        before=copy.deepcopy(self.context.STATE)
        with self.assertRaises(HTTPException) as error:
            await apply_raw_roll(self.context,"m",{"initiative_roll":10})
        self.assertEqual(error.exception.status_code,409)
        self.assertEqual(self.context.STATE,before)
        self.context.combatants_changed.assert_not_awaited()

    async def test_missing_monster_keeps_not_found_response(self):
        with self.assertRaises(HTTPException) as error:
            await apply_raw_roll(self.context,"missing",{"initiative_roll":16})
        self.assertEqual(error.exception.status_code,404)
