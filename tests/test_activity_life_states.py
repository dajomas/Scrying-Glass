"""Activity state labels must not report downed/stable characters as dead."""
import unittest
import test_encounter_features as fixtures
from python.scrying_glass_combatant import combatant_state

class CombatantStateTests(unittest.TestCase):
    def test_downed_label(self):
        self.assertEqual(combatant_state({'life_state': 'down', 'alive': False}), 'down')
    def test_stable_label(self):
        self.assertEqual(combatant_state({'life_state': 'stable', 'alive': False}), 'stable')
    def test_dead_label(self):
        self.assertEqual(combatant_state({'life_state': 'dead', 'alive': False}), 'dead')
    def test_standing_keeps_legacy_alive_label(self):
        self.assertEqual(combatant_state({'life_state': 'standing', 'alive': True}), 'alive')
    def test_legacy_records_preserved(self):
        self.assertEqual(combatant_state({'alive': True}), 'alive')
        self.assertEqual(combatant_state({'alive': False}), 'dead')
        self.assertEqual(combatant_state(None), 'unknown')

class ActivityLifeStateIntegrationTests(unittest.TestCase):
    setUp = fixtures.FeatureTests.setUp
    tearDown = fixtures.FeatureTests.tearDown
    call = fixtures.FeatureTests.call
    item = fixtures.FeatureTests.item

    def test_downing_event_actor_and_target_and_sqlite_reload(self):
        self.call('edit_features', 'c', {'hp_delta': -20})
        event = self.c.STATE['activity_log'][-1]
        self.assertEqual(event['active_combatant_state'], 'down')
        self.assertEqual(event['target_combatant_state'], 'down')
        self.c.load_state()
        self.assertEqual(self.c.STATE['activity_log'][-1]['target_combatant_state'], 'down')

    def test_stabilization_event(self):
        self.call('edit_features', 'c', {'hp_delta': -20})
        self.call('edit_features', 'c', {'death_successes': 3})
        event = self.c.STATE['activity_log'][-1]
        self.assertEqual(event['active_combatant_state'], 'stable')
        self.assertEqual(event['target_combatant_state'], 'stable')

    def test_permanent_death_event_remains_dead(self):
        self.call('edit_features', 'c', {'life_state': 'down'})
        self.call('edit_features', 'c', {'death_failures': 3})
        self.assertEqual(self.c.STATE['activity_log'][-1]['target_combatant_state'], 'dead')

if __name__ == '__main__':
    unittest.main()
