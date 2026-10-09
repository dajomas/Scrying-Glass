"""Regression checks for numeric initiative versus unset initiative."""
import tempfile
import unittest
from pathlib import Path
from python.scrying_glass_combatant import admin_initiative_key
from test_sqlite_storage import context

class InitiativeOrderingTests(unittest.TestCase):
    def test_unset_after_very_negative_integer(self):
        items = [{"id": "unset", "name": "A", "initiative": None},
                 {"id": "numeric", "name": "Z", "initiative": -1000}]
        self.assertEqual([x["id"] for x in sorted(items, key=admin_initiative_key)],
                         ["numeric", "unset"])

    def test_unset_does_not_tie_with_minus_999(self):
        items = [{"id": "unset", "name": "A", "initiative": None},
                 {"id": "numeric", "name": "Z", "initiative": -999}]
        self.assertEqual([x["id"] for x in sorted(items, key=admin_initiative_key)],
                         ["numeric", "unset"])

    def test_numeric_order_and_name_ties_preserved(self):
        items = [{"name": "Z", "initiative": 5}, {"name": "B", "initiative": -2},
                 {"name": "a", "initiative": 5}]
        self.assertEqual([x["name"] for x in sorted(items, key=admin_initiative_key)],
                         ["a", "Z", "B"])

    def test_boolean_is_not_numeric(self):
        items = [{"name": "A", "initiative": True}, {"name": "Z", "initiative": -1000}]
        self.assertEqual(sorted(items, key=admin_initiative_key)[0]["name"], "Z")

    def test_sqlite_restart_preserves_sortable_numeric_initiative(self):
        with tempfile.TemporaryDirectory() as directory:
            c = context(Path(directory))
            try:
                c.import_legacy_storage()
                c.STATE = c.normalize_state({"monsters": [
                    {"id": "unset", "name": "A", "initiative": None, "active": True},
                    {"id": "numeric", "name": "Z", "initiative": -1000, "active": True}]})
                c.save_state()
                c.load_state()
                ordered = sorted(c.STATE["monsters"], key=admin_initiative_key)
                self.assertEqual([item["id"] for item in ordered], ["numeric", "unset"])
            finally:
                c.STORAGE.close()

if __name__ == "__main__":
    unittest.main()
