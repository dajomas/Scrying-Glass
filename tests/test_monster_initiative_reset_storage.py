"""Reset/setup integration and isolated SQLite entity-record persistence."""
import copy
import sqlite3
import tempfile
import unittest
from pathlib import Path
from python.scrying_glass_combatant import reset_entity, reset_imported_monster, setup_snapshot
from python.scrying_glass_monster_initiative import (
    initiative_patch, normalize_initiative, reset_initiative_patch,
)
from python.scrying_glass_storage_fields import ENTITY_FIELDS, TEXT_FIELDS
from python.scrying_glass_storage_records import StorageRecordsMixin


def monster(**changes):
    item = dict(id="m", name="Dragon", monster_species="dragon", hp=4,
                max_hp=20, original_hp=20, initiative=28, original_initiative=None,
                initiative_roll=16, initiative_bonus=12,
                initiative_bonus_origin="manual", active=True, visible=True, in_turn=True)
    item.update(changes)
    return item


class InitiativeResetTests(unittest.TestCase):
    def test_reset_clears_roll_and_preserves_bonus(self):
        item = monster()
        reset_entity(item)
        self.assertIsNone(item["initiative"])
        self.assertIsNone(item["initiative_roll"])
        self.assertEqual(item["initiative_bonus"], 12)
        self.assertEqual(item["initiative_bonus_origin"], "manual")
        self.assertEqual(item["hp"], 20)
        self.assertFalse(item["active"] or item["in_turn"] or item["visible"])
        self.assertIsNone(normalize_initiative(item)["initiative"])

    def test_original_total_becomes_legacy_not_new_roll(self):
        item = monster(original_initiative=23)
        reset_entity(item)
        self.assertEqual(item["initiative"], 23)
        self.assertIsNone(item["initiative_roll"])
        self.assertEqual(normalize_initiative(item)["initiative"], 23)
        self.assertEqual(initiative_patch(item, bonus=10)["initiative"], 23)
        self.assertEqual(initiative_patch(item, roll=16)["initiative"], 28)

    def test_reset_is_idempotent(self):
        item = monster(original_initiative=-2)
        reset_entity(item)
        expected = copy.deepcopy(item)
        reset_entity(item)
        self.assertEqual(item, expected)

    def test_legacy_representation_is_unchanged(self):
        item = monster(original_initiative=19)
        for key in ("initiative_roll", "initiative_bonus", "initiative_bonus_origin"):
            item.pop(key)
        reset_entity(item)
        self.assertEqual(item["initiative"], 19)
        self.assertNotIn("initiative_roll", item)
        self.assertNotIn("initiative_bonus", item)

    def test_character_reset_keeps_announced_total_semantics(self):
        item = dict(hp=4, max_hp=20, initiative=28, original_initiative=23)
        reset_entity(item)
        self.assertEqual((item["hp"], item["initiative"]), (20, 23))
        self.assertNotIn("initiative_roll", item)
        self.assertNotIn("initiative_bonus", item)

    def test_import_preserves_hp_and_source(self):
        source = monster(original_initiative=23, source_provider="5e.tools", source_key="dragon_XMM")
        before = copy.deepcopy(source)
        result = reset_imported_monster(source)
        self.assertNotEqual(result["id"], source["id"])
        self.assertEqual((result["hp"], result["max_hp"]), (4, 20))
        self.assertEqual(result["source_key"], "dragon_XMM")
        self.assertEqual(result["initiative"], 23)
        self.assertIsNone(result["initiative_roll"])
        self.assertEqual(result["initiative_bonus"], 12)
        self.assertFalse(result["active"] or result["visible"] or result["in_turn"])
        self.assertEqual(source, before)

    def test_import_is_a_deep_copy(self):
        source = monster(effects=[{"id": "effect", "notes": "kept"}])
        result = reset_imported_monster(source)
        result["effects"][0]["notes"] = "changed"
        self.assertEqual(source["effects"][0]["notes"], "kept")

    def test_snapshot_preserves_current_relationship(self):
        item = monster()
        state = dict(monsters=[item], characters=[{"id": "c"}], battle_order=["c", "m"])
        result = setup_snapshot(state)
        self.assertEqual(result["monsters"][0]["initiative_roll"], 16)
        self.assertEqual(result["monsters"][0]["initiative"], 28)
        self.assertEqual(result["battle_order"], ["m"])
        self.assertEqual(result["characters"], [])
        result["monsters"][0]["initiative_bonus"] = 99
        self.assertEqual(item["initiative_bonus"], 12)

    def test_invalid_original_rejected_before_reset_mutation(self):
        for value in (True, "23", 1.5):
            with self.subTest(value=value):
                item = monster(original_initiative=value)
                before = copy.deepcopy(item)
                with self.assertRaises(ValueError):
                    reset_entity(item)
                self.assertEqual(item, before)

    def test_signed_and_explicit_zero_bonus_retained(self):
        for bonus in (-2, 0, 12):
            with self.subTest(bonus=bonus):
                item = monster(initiative_bonus=bonus, initiative_bonus_origin="source")
                result = reset_initiative_patch(item)
                self.assertEqual(result["initiative_bonus"], bonus)
                self.assertEqual(result["initiative_bonus_origin"], "source")
                self.assertIsNone(result["initiative_roll"])


class EntityRecordsFixture(StorageRecordsMixin):
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.connection.row_factory = sqlite3.Row
        columns = ",".join(f"{field} {'TEXT' if field in TEXT_FIELDS else 'INTEGER'}" for field in ENTITY_FIELDS)
        self.connection.execute(f"CREATE TABLE IF NOT EXISTS monsters (id INTEGER PRIMARY KEY, encounter_id INTEGER, combatant_id TEXT, position INTEGER, {columns}, UNIQUE(encounter_id, combatant_id))")
        self.connection.execute("CREATE TABLE IF NOT EXISTS monsters_attributes (parent_id INTEGER, field_name TEXT, value_kind TEXT, text_value TEXT, integer_value INTEGER, real_value REAL, UNIQUE(parent_id, field_name))")

    def roundtrip(self, item):
        self._save_entities("monsters", "encounter_id", 1, [item])
        self.connection.commit()
        return self._load_entities("monsters", "encounter_id", 1)[0]


class InitiativeRecordTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "records.sqlite3"
        self.store = EntityRecordsFixture(self.path)
        self.addCleanup(self.store.connection.close)

    def test_roundtrip_preserves_signed_roll_bonus_and_origin(self):
        for bonus in (-2, 0, 12):
            item = monster(initiative_bonus=bonus, initiative=16+bonus)
            self.assertEqual(self.store.roundtrip(item), item)

    def test_reopen_preserves_without_compounding(self):
        item = monster()
        self.store.roundtrip(item)
        reopened = EntityRecordsFixture(self.path)
        self.addCleanup(reopened.connection.close)
        restored = reopened._load_entities("monsters", "encounter_id", 1)[0]
        for _ in range(3):
            restored.update(normalize_initiative(restored))
            restored = reopened.roundtrip(restored)
        self.assertEqual((restored["initiative_roll"], restored["initiative"]), (16, 28))

    def test_reset_save_reload_does_not_resurrect_old_roll(self):
        item = self.store.roundtrip(monster(original_initiative=23))
        reset_entity(item)
        restored = self.store.roundtrip(item)
        self.assertIsNone(restored["initiative_roll"])
        self.assertEqual(normalize_initiative(restored)["initiative"], 23)

    def test_legacy_and_default_zero_remain_distinct(self):
        legacy = {"id": "m", "initiative": 23}
        self.assertEqual(self.store.roundtrip(legacy), legacy)
        default = dict(legacy, **normalize_initiative(legacy))
        restored = self.store.roundtrip(default)
        self.assertEqual(restored["initiative_bonus_origin"], "default")
        self.assertEqual(restored["initiative_bonus"], 0)
        self.assertIsNone(restored["initiative_roll"])

    def test_setup_import_roundtrip_preserves_bonus_not_live_roll(self):
        result = reset_imported_monster(monster())
        restored = self.store.roundtrip(result)
        self.assertEqual(restored["initiative_bonus"], 12)
        self.assertIsNone(restored["initiative_roll"])
        self.assertIsNone(restored["initiative"])

    def test_source_identity_scalars_roundtrip(self):
        item = monster(source_provider="5e.tools", source_key="dragon_XMM")
        self.assertEqual(self.store.roundtrip(item), item)
