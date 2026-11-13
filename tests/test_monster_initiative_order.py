"""Pure order-proposal checks; no route, persistence or turn advancement."""
import copy
import unittest
from python.scrying_glass_monster_initiative_order import order_for_monster_change


class MonsterInitiativeOrderTests(unittest.TestCase):
    def setUp(self):
        self.state = dict(monsters=[dict(id="m", initiative=14, in_turn=True),
                                   dict(id="n", initiative=18, in_turn=False)],
                          characters=[dict(id="c", initiative=21, in_turn=False)],
                          lairs=[dict(id="l", kind="lair", initiative=20)],
                          battle_order=["c", "l", "n", "m"], battle_round=4,
                          turn_successors=["c", "n"], activity_log=[dict(text="keep")])

    def proposal(self, total):
        return order_for_monster_change(self.state, "m", dict(self.state["monsters"][0], initiative=total))

    def test_increase_and_decrease(self):
        self.assertEqual(self.proposal(28), ["m", "c", "l", "n"])
        self.assertEqual(self.proposal(-2), ["c", "l", "n", "m"])

    def test_existing_tie_order_is_stable(self):
        self.assertEqual(self.proposal(21), ["c", "m", "l", "n"])
        self.state["battle_order"] = ["m", "c", "l", "n"]
        self.assertEqual(self.proposal(21), ["m", "c", "l", "n"])

    def test_creature_precedes_lair_on_twenty(self):
        self.assertEqual(self.proposal(20), ["c", "m", "l", "n"])

    def test_state_turn_round_and_other_fields_are_untouched(self):
        before=copy.deepcopy(self.state)
        result=self.proposal(28)
        self.assertEqual(self.state, before)
        self.assertIsNot(result, self.state["battle_order"])
        self.assertTrue(self.state["monsters"][0]["in_turn"])
        self.assertEqual(self.state["battle_round"], 4)

    def test_no_active_order_is_not_started(self):
        self.state["battle_order"]=[]
        self.assertEqual(self.proposal(28), [])

    def test_monster_outside_order_does_not_reorder_others(self):
        self.state["battle_order"]=["n", "c", "l"]
        self.assertEqual(self.proposal(28), ["n", "c", "l"])

    def test_membership_is_not_expanded_or_filtered(self):
        self.state["monsters"][1]["active"]=False
        result=self.proposal(28)
        self.assertEqual(set(result), set(self.state["battle_order"]))

    def test_unknown_and_duplicate_ids_are_rejected_without_mutation(self):
        for order in (["c", "missing", "m"], ["c", "m", "m"]):
            with self.subTest(order=order):
                self.state["battle_order"]=order
                before=copy.deepcopy(self.state)
                with self.assertRaises(ValueError): self.proposal(28)
                self.assertEqual(self.state, before)

    def test_ambiguous_entity_ids_are_rejected(self):
        self.state["characters"].append(dict(id="m", initiative=1))
        with self.assertRaises(ValueError): self.proposal(28)

    def test_candidate_identity_is_checked(self):
        with self.assertRaises(ValueError):
            order_for_monster_change(self.state, "m", dict(id="wrong", initiative=28))

    def test_unset_totals_sort_after_numeric(self):
        self.assertEqual(self.proposal(None), ["c", "l", "n", "m"])
