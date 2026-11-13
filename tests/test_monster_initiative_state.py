"""Full StateService monster initiative normalization regressions."""
import copy
import json
import unittest
import uuid
from types import SimpleNamespace
from python.scrying_glass_service_state import StateService
from python.scrying_glass_monster_initiative import (
    initiative_patch, legacy_total_patch, normalize_initiative,
)


class MonsterStateInitiativeTests(unittest.TestCase):
    def setUp(self):
        context = SimpleNamespace(uuid=uuid, normalize_display=lambda value: value or {})
        self.service = StateService(context)

    def normalize(self, monster):
        return self.service.normalize_state({"monsters": [dict(id="m", **monster)]})["monsters"][0]

    def test_legacy_total_is_preserved_with_default_zero(self):
        item = self.normalize({"initiative": 23})
        self.assertEqual((item["initiative"], item["original_initiative"]), (23, 23))
        self.assertEqual(item["initiative_bonus"], 0)
        self.assertEqual(item["initiative_bonus_origin"], "default")
        self.assertIsNone(item["initiative_roll"])

    def test_unset_initiative_stays_unset(self):
        item = self.normalize({})
        self.assertIsNone(item["initiative"])
        self.assertIsNone(item["initiative_roll"])

    def test_retained_raw_roll_uses_signed_bonus_once(self):
        for bonus in (-2, 0, 12):
            with self.subTest(bonus=bonus):
                item = self.normalize({"initiative": 16+bonus, "initiative_roll": 16,
                                       "initiative_bonus": bonus, "initiative_bonus_origin": "source"})
                self.assertEqual(item["initiative"], 16+bonus)
                self.assertEqual(item["initiative_roll"], 16)

    def test_repeat_json_reload_is_idempotent(self):
        raw = {"monsters": [{"id":"m", **initiative_patch({}, roll=16, bonus=12)}]}
        expected = self.service.normalize_state(raw)
        for _ in range(5):
            restored = self.service.normalize_state(json.loads(json.dumps(expected)))
            self.assertEqual(restored, expected)
            expected = restored

    def test_explicit_zero_origin_survives(self):
        item = self.normalize(initiative_patch({}, bonus=0, origin="manual"))
        self.assertEqual(item["initiative_bonus_origin"], "manual")

    def test_normalization_does_not_mutate_input(self):
        raw = {"monsters": [{"id":"m", "initiative":23}]}
        before = copy.deepcopy(raw)
        self.service.normalize_state(raw)
        self.assertEqual(raw, before)

    def test_character_fields_and_total_unchanged(self):
        result = self.service.normalize_state({"characters":[{"id":"c", "initiative":28}]})
        item = result["characters"][0]
        self.assertEqual(item["initiative"], 28)
        for field in ("initiative_roll", "initiative_bonus", "initiative_bonus_origin"):
            self.assertNotIn(field, item)

    def test_bad_monster_fields_reject_without_mutation(self):
        for field, value in (("initiative_bonus", True), ("initiative_bonus", "12"),
                             ("initiative_roll", 1.5), ("initiative_roll", False),
                             ("initiative_bonus_origin", "unknown")):
            with self.subTest(field=field, value=value):
                raw = {"monsters":[{"id":"m", field:value}]}
                before = copy.deepcopy(raw)
                with self.assertRaisesRegex(ValueError, r"monsters\[0\]"):
                    self.service.normalize_state(raw)
                self.assertEqual(raw, before)

    def test_legacy_negative_total_preserved(self):
        self.assertEqual(self.normalize({"initiative":-2})["initiative"], -2)

    def test_round_turn_and_selected_tie_order_are_retained(self):
        raw = {"monsters":[{"id":"a", "initiative":28, "active":True, "in_turn":True},
                            {"id":"b", "initiative":28, "active":True}],
               "battle_order":["b","a"], "battle_round":4,
               "turn_successors":["b"], "turn_successors_before_wrap":["b"]}
        result = self.service.normalize_state(raw)
        self.assertEqual(result["battle_order"], ["b","a"])
        self.assertEqual(result["battle_round"], 4)
        self.assertTrue(result["monsters"][0]["in_turn"])
        self.assertEqual(result["turn_successors"], ["b"])

    def test_lair_is_not_given_monster_bonus_fields(self):
        item = self.service.normalize_state({"lairs":[{"id":"l", "name":"Lair"}]})["lairs"][0]
        self.assertEqual(item["initiative"], 20)
        self.assertNotIn("initiative_bonus", item)

    def test_real_statistics_reduction_normalization_coexists(self):
        effect = dict(id="e", name="Reduction", notes="", public=False,
                      concentration=False, timing="manual", turns=None,
                      mechanical=dict(version=1, stat="max_hp", amount=5))
        source = dict(hp=20, max_hp=20, original_hp=20, base_max_hp=20,
                      active=True, in_turn=True, effects=[effect],
                      **initiative_patch({}, roll=16, bonus=12))
        before = copy.deepcopy(source)
        item = self.normalize(source)
        self.assertEqual((item["hp"], item["max_hp"]), (15,15))
        self.assertEqual((item["initiative_roll"], item["initiative"]), (16,28))
        self.assertTrue(item["in_turn"])
        self.assertEqual(source, before)

    def test_real_feature_validation_rejects_invalid_effects(self):
        source = dict(effects="invalid", initiative=23)
        before = copy.deepcopy(source)
        with self.assertRaisesRegex(ValueError, "effects"):
            self.normalize(source)
        self.assertEqual(source, before)


    def test_legacy_edit_survives_full_state_reload(self):
        item = self.normalize(initiative_patch({}, roll=16, bonus=12))
        item.update(legacy_total_patch(item, 22))
        restored = self.service.normalize_state({"monsters":[item]})["monsters"][0]
        self.assertEqual(restored["initiative"], 22)
        self.assertIsNone(restored["initiative_roll"])
        self.assertEqual(restored["initiative_bonus"], 12)

    def test_retained_roll_repairs_stale_derived_total(self):
        item = self.normalize(dict(initiative=99, initiative_roll=16,
                                   initiative_bonus=12, initiative_bonus_origin="manual"))
        self.assertEqual(item["initiative"], 28)
        self.assertEqual(item["initiative_roll"], 16)


class LegacyTotalBridgeTests(unittest.TestCase):
    def test_final_total_is_not_incremented(self):
        item = initiative_patch({}, roll=16, bonus=12)
        result = legacy_total_patch(item, 22)
        self.assertEqual(result["initiative"], 22)
        self.assertIsNone(result["initiative_roll"])
        self.assertEqual(result["initiative_bonus"], 12)
        self.assertEqual(normalize_initiative(result)["initiative"], 22)

    def test_clear_keeps_bonus(self):
        result = legacy_total_patch(initiative_patch({}, roll=16, bonus=-2), None)
        self.assertIsNone(result["initiative"])
        self.assertIsNone(result["initiative_roll"])
        self.assertEqual(result["initiative_bonus"], -2)

    def test_next_raw_roll_replaces_legacy(self):
        legacy = legacy_total_patch(initiative_patch({}, roll=16, bonus=12), 22)
        self.assertEqual(initiative_patch(legacy, roll=10)["initiative"], 22)
        self.assertEqual(initiative_patch(legacy, roll=16)["initiative"], 28)

    def test_repeated_bridge_updates_do_not_mutate_source(self):
        item = initiative_patch({}, roll=16, bonus=12)
        before = copy.deepcopy(item)
        for total in (22, 22, -2, 0):
            self.assertEqual(legacy_total_patch(item, total)["initiative"], total)
        self.assertEqual(item, before)

    def test_invalid_final_total_rejected(self):
        item = initiative_patch({}, roll=16, bonus=12)
        for total in (True, "22", 1.5):
            with self.assertRaises(ValueError):
                legacy_total_patch(item, total)
