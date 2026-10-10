"""Isolated health/effect regressions; no HTTP or server integration tests.
FastAPI's exception is stubbed only when FastAPI is not installed.
"""
import copy
import importlib
import sys
import types
import unittest
from unittest.mock import patch
try:
    import fastapi
except ImportError:
    class HTTPException(Exception):
        def __init__(self, status_code, detail):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)
    with patch.dict(sys.modules, {'fastapi': types.SimpleNamespace(HTTPException=HTTPException)}):
        hp = importlib.import_module('python.scrying_glass_hp')
else:
    HTTPException = fastapi.HTTPException
    hp = importlib.import_module('python.scrying_glass_hp')
from python.scrying_glass_feature_rules import normalize_features, apply_hp, validate_effects
from python.scrying_glass_health_limits import MAX_STORED_HP, HpStorageRangeError

def combatant(**values):
    item = dict(hp=10, max_hp=20, original_hp=10, active=True, alive=True,
                life_state='standing', temp_hp=5, death_successes=0, death_failures=0)
    item.update(values)
    return item

def effect(**values):
    item = dict(id='e', name='Effect', notes='', source_id=None, anchor_id=None,
                public=False, concentration=False, timing='manual', turns=None)
    item.update(values)
    return item

class HealthRegressionTests(unittest.TestCase):
    def test_integer_zero_start(self):
        self.assertEqual(hp.hp_value_factory(0, None)(), 0)
    def test_integer_zero_end(self):
        with self.assertRaises(HTTPException): hp.hp_value_factory('1', 0)
    def test_integer_zero_end_with_dice(self):
        with self.assertRaises(HTTPException): hp.hp_value_factory('1d6', 0)
    def test_string_zero(self):
        self.assertEqual(hp.hp_value_factory('0', '0')(), 0)
    def test_empty_start(self):
        for value in (None, ''):
            with self.subTest(value=value), self.assertRaises(HTTPException): hp.hp_value_factory(value, None)
    def test_dice(self):
        self.assertEqual(hp.parse_hp_dice_expression('3d8+9'), (3, 8, 9))
    def test_sqlite_boundary(self):
        item = combatant(hp=MAX_STORED_HP, max_hp=MAX_STORED_HP, original_hp=MAX_STORED_HP)
        normalize_features(item)
        self.assertEqual(item['hp'], MAX_STORED_HP)
    def test_historical_negatives(self):
        item = combatant(hp=-1, max_hp=-2, original_hp=-3, life_state='down')
        normalize_features(item)
        self.assertEqual((item['hp'], item['max_hp'], item['original_hp']), (0, 0, 0))
    def test_missing_original_hp(self):
        item = combatant(); del item['original_hp']
        normalize_features(item)
        self.assertNotIn('original_hp', item)
    def test_valid_absorption(self):
        for absorb, expected in ((True, (9, 0)), (False, (4, 5))):
            item = combatant(); apply_hp(item, -6, absorb=absorb)
            self.assertEqual((item['hp'], item['temp_hp']), expected)
    def test_critical_zero_hp(self):
        item = combatant(hp=0, life_state='down', temp_hp=0)
        apply_hp(item, -1, critical=True)
        self.assertEqual(item['death_failures'], 2)
    def test_healing_overflow(self):
        with self.assertRaises(HpStorageRangeError): apply_hp(combatant(hp=MAX_STORED_HP), 1)
    def test_valid_unicode(self):
        validate_effects([effect(name='Bénédiction 🐉', notes='Café')])
    def test_duplicate_effects(self):
        with self.assertRaises(ValueError): validate_effects([effect(), effect()])
    def test_invalid_effect_flag(self):
        with self.assertRaises(ValueError): validate_effects([effect(public=1)])

def overflow_test(field):
    def test(self):
        item = combatant(**{field: MAX_STORED_HP + 1}); before = copy.deepcopy(item)
        with self.assertRaises(HpStorageRangeError): normalize_features(item)
        self.assertEqual(item, before)
    return test
for field in ('hp', 'max_hp', 'original_hp'):
    setattr(HealthRegressionTests, 'test_overflow_' + field, overflow_test(field))

def original_type_test(value):
    def test(self):
        item = combatant(original_hp=value); before = copy.deepcopy(item)
        with self.assertRaises(ValueError): normalize_features(item)
        self.assertEqual(item, before)
    return test
for label, value in (('bool', True), ('float', 1.5), ('string', '12'), ('null', None)):
    setattr(HealthRegressionTests, 'test_original_hp_' + label, original_type_test(value))

def absorption_test(value):
    def test(self):
        item = combatant(); before = copy.deepcopy(item)
        with self.assertRaises(ValueError): apply_hp(item, -1, absorb=value)
        self.assertEqual(item, before)
    return test
for label, value in (('string', 'false'), ('integer', 1), ('null', None)):
    setattr(HealthRegressionTests, 'test_absorb_' + label, absorption_test(value))

def surrogate_test(field):
    def test(self):
        with self.assertRaises(ValueError): validate_effects([effect(**{field: '\ud800'})])
    return test
for field in ('id', 'name', 'notes', 'source_id', 'anchor_id'):
    setattr(HealthRegressionTests, 'test_surrogate_' + field, surrogate_test(field))

if __name__ == '__main__': unittest.main()
