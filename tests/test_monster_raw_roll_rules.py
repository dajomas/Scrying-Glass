"""Raw-roll arithmetic and validation without framework substitutes."""
import copy
import unittest
from python.scrying_glass_monster_raw_roll import raw_roll_patch, MAX_INTEGER, MIN_INTEGER


class RawRollRulesTests(unittest.TestCase):
    def setUp(self):
        self.monster = dict(initiative=28, initiative_roll=16,
            initiative_bonus=12, initiative_bonus_origin="manual")

    def test_replacement_and_repeat_never_compound(self):
        for raw,total in ((16,28),(10,22),(16,28),(16,28)):
            self.monster.update(raw_roll_patch(self.monster, {"initiative_roll":raw}))
            self.assertEqual(self.monster["initiative"], total)

    def test_negative_and_zero_bonus(self):
        for bonus,total in ((-2,14),(0,16)):
            self.monster["initiative_bonus"]=bonus
            self.assertEqual(raw_roll_patch(self.monster,{"initiative_roll":16})["initiative"],total)

    def test_legacy_total_establishes_calculation_only_on_explicit_roll(self):
        self.monster.update(initiative_roll=None,initiative=99)
        self.assertEqual(raw_roll_patch(self.monster,{"initiative_roll":16})["initiative"],28)
        self.assertEqual(self.monster["initiative"],99)

    def test_clear_unsets_raw_and_total_but_preserves_bonus_origin(self):
        values=raw_roll_patch(self.monster,{"initiative_roll":None})
        self.assertIsNone(values["initiative"])
        self.assertIsNone(values["initiative_roll"])
        self.assertEqual((values["initiative_bonus"],values["initiative_bonus_origin"]),(12,"manual"))

    def test_missing_bonus_defaults_without_inventing_old_raw(self):
        values=raw_roll_patch(dict(initiative=25),{"initiative_roll":16})
        self.assertEqual((values["initiative"],values["initiative_bonus_origin"]),(16,"default"))

    def test_no_new_gameplay_bounds(self):
        self.assertEqual(raw_roll_patch(self.monster,{"initiative_roll":-50})["initiative"],-38)
        self.assertEqual(raw_roll_patch(self.monster,{"initiative_roll":500})["initiative"],512)

    def test_malformed_or_extra_fields_rejected_without_mutation(self):
        for body in ({},[],None,{"initiative":16},{"initiative_roll":True},
                     {"initiative_roll":16.0},{"initiative_roll":"16"},
                     {"initiative_roll":16,"initiative_bonus":99}):
            with self.subTest(body=body):
                before=copy.deepcopy(self.monster)
                with self.assertRaises(ValueError):raw_roll_patch(self.monster,body)
                self.assertEqual(self.monster,before)

    def test_storage_boundaries_and_total_overflow(self):
        for raw in (MIN_INTEGER-1,MAX_INTEGER+1,MAX_INTEGER):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):raw_roll_patch(self.monster,{"initiative_roll":raw})
        self.monster["initiative_bonus"]=0
        self.assertEqual(raw_roll_patch(self.monster,{"initiative_roll":MAX_INTEGER})["initiative"],MAX_INTEGER)

    def test_shared_existing_raw_is_not_added_twice(self):
        self.monster.update(initiative_roll=16,initiative=28)
        values=raw_roll_patch(self.monster,{"initiative_roll":16})
        self.assertEqual(values["initiative"],28)
