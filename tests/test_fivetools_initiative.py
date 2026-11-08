"""Explicit 5e.tools initiative formats; fixtures contain only minimal stat fields."""
import copy
import unittest
from python.scrying_glass_fivetools_initiative import fivetools_initiative_offer as offer


def noble(**changes):
    result = dict(name="Noble Prodigy", source="XMM", dex=16, cr="10",
                  initiative={"proficiency": 1})
    result.update(changes)
    return result


class FivetoolsInitiativeTests(unittest.TestCase):
    def test_noble_prodigy_explicit_proficiency_is_seven(self):
        result = offer(noble())
        self.assertEqual((result["initiative_bonus"], result["initiative_bonus_status"]), (7, "available"))
        self.assertIn("proficiency=1", result["initiative_bonus_evidence"])

    def test_explicit_zero_proficiency_and_expertise(self):
        for multiplier, expected in ((0, 3), (1, 7), (2, 11)):
            with self.subTest(multiplier=multiplier):
                self.assertEqual(offer(noble(initiative={"proficiency": multiplier}))["initiative_bonus"], expected)

    def test_signed_numeric_and_object_totals_override_abilities(self):
        for value in (-2, 0, 12, -(2**63), 2**63-1):
            for raw in (value, {"initiative": value}, {"initiative": value, "proficiency": 2}):
                result = offer(noble(initiative=raw, dex=None, cr=None))
                self.assertEqual((result["initiative_bonus"], result["initiative_bonus_status"]), (value, "available"))

    def test_challenge_rating_bands_fractional_and_object_forms(self):
        for cr, pb in (("0", 2), ("1/8", 2), ("1/4", 2), ("1/2", 2),
                       (1, 2), (4, 2), (5, 3), (8, 3), (9, 4), (12, 4),
                       (13, 5), (16, 5), (17, 6), (20, 6), (21, 7), (24, 7),
                       (25, 8), (28, 8), (29, 9), (30, 9)):
            for raw in (cr, {"cr": cr, "xpLair": 999}):
                with self.subTest(cr=raw):
                    self.assertEqual(offer(noble(cr=raw))["initiative_bonus"], 3+pb)

    def test_missing_initiative_never_uses_dexterity(self):
        item = noble()
        del item["initiative"]
        result = offer(item)
        self.assertEqual(result["initiative_bonus_status"], "missing")
        self.assertIsNone(result["initiative_bonus"])

    def test_unresolved_copies_are_not_resolved_by_guessing(self):
        self.assertEqual(offer(noble(_copy={"name": "Other", "source": "MM"}))["initiative_bonus_status"], "missing")

    def test_advantage_changes_no_roll_bonus(self):
        for mode in ("adv", "dis"):
            self.assertEqual(offer(noble(initiative={"proficiency": 1, "advantageMode": mode}))["initiative_bonus"], 7)

    def test_malformed_or_unknown_explicit_formats_are_unavailable(self):
        for raw in (None, True, False, 7.0, "+7", [], {}, {"proficiency": True},
                    {"proficiency": "1"}, {"proficiency": 0.5}, {"proficiency": -1},
                    {"proficiency": 3}, {"initiative": False}, {"initiative": "+7"},
                    {"bonus": 7}, {"proficiency": 1, "advantageMode": "bad"},
                    {"advantageMode": "adv"}, 2**63, -(2**63)-1):
            with self.subTest(raw=raw):
                result = offer(noble(initiative=raw))
                self.assertEqual(result["initiative_bonus_status"], "invalid")
                self.assertIsNone(result["initiative_bonus"])

    def test_invalid_dexterity_or_cr_cannot_create_source_zero(self):
        for dex in (None, True, "16", 16.0, {"special": "varies"}, -1, 2**63):
            self.assertEqual(offer(noble(dex=dex))["initiative_bonus_status"], "invalid")
        for cr in (None, True, 10.0, "Unknown", "31", 31, -1, {}, {"cr": True}, "10 "):
            self.assertEqual(offer(noble(cr=cr))["initiative_bonus_status"], "invalid")
        self.assertEqual(offer(noble(dex=10, cr=None, initiative={"proficiency": 0}))["initiative_bonus"], 0)

    def test_input_is_not_mutated(self):
        item = noble()
        before = copy.deepcopy(item)
        offer(item)
        self.assertEqual(item, before)


if __name__ == "__main__":
    unittest.main()
