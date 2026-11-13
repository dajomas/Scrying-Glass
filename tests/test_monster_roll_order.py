"""Pure automatic/shared roll planning; no framework or persistence fixtures."""
import copy
import unittest
from unittest.mock import Mock
from python.scrying_glass_monster_roll_order import plan_monster_rolls, RollOrderError


class MonsterRollOrderTests(unittest.TestCase):
    def setUp(self):
        self.a=dict(id="a", initiative=2, initiative_roll=None, initiative_bonus=12,
                    initiative_bonus_origin="manual", active=True, in_turn=True, hp=30)
        self.b=dict(id="b", initiative=30, initiative_roll=None, initiative_bonus=3,
                    initiative_bonus_origin="import", active=True, in_turn=False, hp=20)
        self.c=dict(id="c", initiative=8, initiative_roll=None, initiative_bonus=-2,
                    initiative_bonus_origin="source", active=False, in_turn=False, hp=10)
        self.state=dict(monsters=[self.a,self.b,self.c],
            characters=[dict(id="hero", initiative=21, in_turn=False)],
            lairs=[dict(id="lair",kind="lair",initiative=20)],
            battle_order=["b","hero","lair","a"], battle_round=4,
            turn_successors=["hero","a"],turn_successors_before_wrap=["hero"],
            activity_log=[dict(text="keep")])

    def test_automatic_uses_one_die_per_monster_and_final_totals(self):
        die=Mock(side_effect=[16,10,1])
        changes,order=plan_monster_rolls(self.state,self.state["monsters"],die)
        self.assertEqual([values["initiative"] for _,values in changes],[28,13,-1])
        self.assertEqual([values["initiative_roll"] for _,values in changes],[16,10,1])
        self.assertEqual(order,["a","hero","lair","b"])
        self.assertEqual(die.call_count,3)
        self.assertTrue(all(call.args==(1,20) for call in die.call_args_list))

    def test_shared_roll_is_one_die_plus_individual_bonus(self):
        die=Mock(return_value=16)
        changes,order=plan_monster_rolls(self.state,[self.a,self.b,self.c],die,shared=True)
        die.assert_called_once_with(1,20)
        self.assertEqual([values["initiative"] for _,values in changes],[28,19,14])
        self.assertEqual(order,["a","hero","lair","b"])

    def test_unselected_monsters_and_characters_are_not_changed(self):
        before=copy.deepcopy(self.state)
        changes,order=plan_monster_rolls(self.state,[self.a],Mock(return_value=16),shared=True)
        self.assertEqual([monster["id"] for monster,_ in changes],["a"])
        self.assertEqual(self.state,before)
        self.assertEqual(order,["b","a","hero","lair"])

    def test_no_order_is_started(self):
        self.state["battle_order"]=[]
        changes,order=plan_monster_rolls(self.state,[self.a],Mock(return_value=16))
        self.assertEqual(order,[])
        self.assertEqual(changes[0][1]["initiative"],28)

    def test_membership_and_all_unrelated_state_are_preserved(self):
        before=copy.deepcopy(self.state)
        changes,order=plan_monster_rolls(self.state,self.state["monsters"],Mock(return_value=16))
        self.assertEqual(set(order),set(before["battle_order"]))
        self.assertNotIn("c",order)
        self.assertEqual(self.state,before)
        self.assertTrue(self.a["in_turn"])
        self.assertEqual(self.state["battle_round"],4)
        self.assertEqual(self.state["turn_successors"],["hero","a"])

    def test_final_ties_retain_original_order_not_intermediate_sort_order(self):
        self.a.update(initiative=10,initiative_bonus=0)
        self.b.update(initiative=30,initiative_bonus=0)
        self.state["battle_order"]=["b","a","hero","lair"]
        _,order=plan_monster_rolls(self.state,[self.a,self.b],Mock(return_value=16),shared=True)
        self.assertEqual(order,["hero","lair","b","a"])

    def test_lair_loses_twenty_tie_to_creatures(self):
        self.a["initiative_bonus"]=4
        _,order=plan_monster_rolls(self.state,[self.a],Mock(return_value=16))
        self.assertEqual(order,["b","hero","a","lair"])

    def test_invalid_bonus_is_rejected_before_any_die(self):
        self.b["initiative_bonus"]=True
        before=copy.deepcopy(self.state)
        die=Mock(return_value=16)
        with self.assertRaises(ValueError):plan_monster_rolls(self.state,[self.a,self.b],die)
        die.assert_not_called()
        self.assertEqual(self.state,before)

    def test_late_overflow_has_no_partial_mutation(self):
        self.b["initiative_bonus"]=2**63-1
        before=copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            plan_monster_rolls(self.state,[self.a,self.b],Mock(side_effect=[16,1]))
        self.assertEqual(self.state,before)

    def test_unknown_order_member_is_rejected_without_mutation(self):
        self.state["battle_order"]=["missing","a"]
        before=copy.deepcopy(self.state)
        with self.assertRaises(RollOrderError):
            plan_monster_rolls(self.state,[self.a],Mock(return_value=16))
        self.assertEqual(self.state,before)

    def test_duplicate_or_detached_targets_are_rejected_before_dice(self):
        for targets in ([self.a,self.a],[dict(self.a)]):
            die=Mock(return_value=16)
            with self.assertRaises(ValueError):plan_monster_rolls(self.state,targets,die)
            die.assert_not_called()

    def test_only_outside_order_targets_leave_other_order_untouched(self):
        self.state["battle_order"]=["a","b","hero","lair"]
        _,order=plan_monster_rolls(self.state,[self.c],Mock(return_value=16))
        self.assertEqual(order,["a","b","hero","lair"])

    def test_empty_shared_selection_uses_no_die(self):
        die=Mock(return_value=16)
        changes,order=plan_monster_rolls(self.state,[],die,shared=True)
        self.assertEqual(changes,[])
        self.assertEqual(order,self.state["battle_order"])
        die.assert_not_called()

    def test_repeat_roll_replaces_raw_without_compounding(self):
        for _ in range(2):
            changes,order=plan_monster_rolls(self.state,[self.a],Mock(return_value=16))
            for monster,values in changes:monster.update(values)
            self.state["battle_order"]=order
        self.assertEqual((self.a["initiative_roll"],self.a["initiative"]),(16,28))

    def test_invalid_generated_die_cannot_clear_or_corrupt_initiative(self):
        for raw in (None,True,0,21,1.5):
            with self.subTest(raw=raw):
                before=copy.deepcopy(self.state)
                with self.assertRaises(ValueError):
                    plan_monster_rolls(self.state,[self.a],Mock(return_value=raw),shared=True)
                self.assertEqual(self.state,before)
