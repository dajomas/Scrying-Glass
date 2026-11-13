"""Direct active handler checks; not authenticated HTTP or persistence tests."""
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from python.scrying_glass_classes import BulkCombatantAction
from python.scrying_glass_admin_monsters import AdminMonstersMixin
from python.scrying_glass_service_battle import BattleService


class MonsterRollOrderHandlerTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        from test_monster_initiative_bonus_edit import MonsterBonusEditTests
        fixture=MonsterBonusEditTests("test_bonus_recalculates_retained_raw")
        fixture.setUp()
        self.handler=fixture.handler
        self.context=fixture.context
        self.a=fixture.monster
        self.b=dict(self.a,id="n",initiative=19,initiative_roll=16,
                    initiative_bonus=3,initiative_bonus_origin="import",in_turn=False)
        self.context.STATE["monsters"].append(self.b)
        self.context.STATE.update(battle_order=["n","c","m"],battle_round=4,
                                  turn_successors=["c"],turn_successors_before_wrap=["c"])
        self.context.random=SimpleNamespace(randint=Mock(return_value=16))
        self.context.unique_ids=lambda ids:list(dict.fromkeys(ids))
        self.context.selected_entities=BattleService(self.context).selected_entities

    async def test_automatic_reorders_preserving_turn_round_and_unrelated_fields(self):
        before=copy.deepcopy(self.context.STATE)
        result=await self.handler.roll_monster_initiative()
        self.assertEqual(result,{"count":2})
        self.assertEqual(self.context.random.randint.call_count,2)
        self.assertEqual(self.context.STATE["battle_order"],["m","c","n"])
        self.assertTrue(self.a["in_turn"])
        self.assertEqual(self.context.STATE["battle_round"],4)
        self.assertEqual(self.context.STATE["characters"],before["characters"])
        self.assertEqual(self.context.STATE["turn_successors"],before["turn_successors"])
        self.assertEqual(self.a["hp"],before["monsters"][0]["hp"])
        self.context.remember_turn_successors.assert_not_called()
        self.context.combatants_changed.assert_awaited_once_with(monsters=True,characters=False)

    async def test_shared_one_roll_deduplicates_and_only_changes_selection(self):
        before=copy.deepcopy(self.b)
        body=BulkCombatantAction(action="roll-shared-initiative",ids=["m","m"])
        result=await self.handler.bulk_monsters(body)
        self.assertEqual(result,{"count":1})
        self.context.random.randint.assert_called_once_with(1,20)
        self.assertEqual(self.b,before)
        self.assertEqual((self.a["initiative_roll"],self.a["initiative"]),(16,28))
        self.assertEqual(self.context.STATE["battle_order"],["m","c","n"])

    async def test_missing_selection_rejected_before_dice(self):
        before=copy.deepcopy(self.context.STATE)
        with self.assertRaises(HTTPException) as error:
            await self.handler.bulk_monsters(BulkCombatantAction(action="roll-shared-initiative",ids=["missing"]))
        self.assertEqual(error.exception.status_code,404)
        self.context.random.randint.assert_not_called()
        self.context.combatants_changed.assert_not_awaited()
        self.assertEqual(self.context.STATE,before)

    async def test_invalid_bonus_rejected_before_dice_or_mutation(self):
        self.b["initiative_bonus"]=True
        before=copy.deepcopy(self.context.STATE)
        with self.assertRaises(HTTPException) as error:
            await self.handler.roll_monster_initiative()
        self.assertEqual(error.exception.status_code,422)
        self.context.random.randint.assert_not_called()
        self.context.combatants_changed.assert_not_awaited()
        self.assertEqual(self.context.STATE,before)

    async def test_invalid_order_is_conflict_without_partial_mutation(self):
        self.context.STATE["battle_order"]=["m","missing"]
        before=copy.deepcopy(self.context.STATE)
        with self.assertRaises(HTTPException) as error:
            await self.handler.roll_monster_initiative()
        self.assertEqual(error.exception.status_code,409)
        self.assertEqual(self.context.STATE,before)
        self.context.combatants_changed.assert_not_awaited()

    async def test_other_bulk_actions_delegate_without_rolling(self):
        body=BulkCombatantAction(action="show-ac",ids=["m"])
        with patch.object(AdminMonstersMixin,"bulk_monsters",new_callable=AsyncMock,
                          return_value={"count":1}) as original:
            result=await self.handler.bulk_monsters(body)
        original.assert_awaited_once_with(body)
        self.assertEqual(result,{"count":1})
        self.context.random.randint.assert_not_called()
