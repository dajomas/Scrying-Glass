"""Framework-independent initiative bonus input checks."""
import unittest
from python.scrying_glass_initiative_input import creation_bonus_fields


class BonusInputTests(unittest.TestCase):
    def test_missing_and_blank_default(self):
        for result in (creation_bonus_fields(), creation_bonus_fields(""), creation_bonus_fields("   ")):
            self.assertEqual(result, dict(initiative_bonus=0, initiative_bonus_origin="default"))

    def test_signed_numbers_and_text(self):
        for value, expected in ((12,12),(-2,-2),(0,0),("+12",12),(" -2 ",-2),("00012",12)):
            with self.subTest(value=value):
                result = creation_bonus_fields(value)
                self.assertEqual(result["initiative_bonus"], expected)
                self.assertEqual(result["initiative_bonus_origin"], "manual")

    def test_explicit_zero_not_defaulted(self):
        self.assertEqual(creation_bonus_fields("0")["initiative_bonus_origin"], "manual")
        self.assertEqual(creation_bonus_fields(0, origin="import")["initiative_bonus_origin"], "import")

    def test_invalid_types_and_text(self):
        for value in (None, True, False, 12.0, 1.5, [], {}, "1.0", "1e2", "12 bonus", "--2", "1_000", "１２"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    creation_bonus_fields(value)

    def test_storage_bounds(self):
        for value in (-(2**63), 2**63-1):
            self.assertEqual(creation_bonus_fields(value)["initiative_bonus"], value)
        for value in (-(2**63)-1, 2**63, "9"*10000):
            with self.assertRaises(ValueError):
                creation_bonus_fields(value)

    def test_long_leading_zeros_do_not_hit_int_conversion_limit(self):
        self.assertEqual(creation_bonus_fields("+"+"0"*10000+"12")["initiative_bonus"], 12)

    def test_origins_validated(self):
        for origin in ("unknown", None, []):
            with self.assertRaises(ValueError):
                creation_bonus_fields(0, origin=origin)
        with self.assertRaises(ValueError):
            creation_bonus_fields(1, origin="default")
