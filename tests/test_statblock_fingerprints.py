"""Increment 2B.1 private fingerprints/comparisons, not restore or private saves."""
import copy
import hashlib
import json
import unittest
import test_statblock_stage2_contracts as contracts
from python.scrying_glass_feature_rules import normalize_features
from python.scrying_glass_service_features import fingerprint
from python.scrying_glass_statblock_changes import private_signature, state_changed
from python.scrying_glass_statblock_loading import PrivateEncounterState


class PrivateFingerprintTests(unittest.TestCase):
    setUp = contracts.StatblockStage2ContractTests.setUp
    tearDown = contracts.StatblockStage2ContractTests.tearDown
    encounter = contracts.StatblockStage2ContractTests.encounter
    seed = contracts.StatblockStage2ContractTests.seed

    def test_no_private_content_retains_legacy_hash(self):
        payload = copy.deepcopy(self.c.STATE)
        payload.pop('activity_log', None); payload.pop('active_turn_id', None)
        for item in payload.get('monsters', []) + payload.get('characters', []): normalize_features(item)
        expected = hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        self.assertEqual(fingerprint(self.c.STATE), expected)
        self.assertEqual(fingerprint(PrivateEncounterState(self.c.STATE, {})), expected)

    def test_private_only_replacement_changes_fingerprint_and_comparison(self):
        self.seed(); before = copy.deepcopy(self.c.STATE)
        self.seed('Replacement'); after = self.c.STATE
        self.assertEqual(dict(before), dict(after))
        self.assertNotEqual(fingerprint(before), fingerprint(after))
        self.assertTrue(state_changed(before, after))

    def test_revision_and_prepared_time_changes_are_detected(self):
        self.seed(); before = copy.deepcopy(self.c.STATE)
        changed = copy.deepcopy(before); changed._statblocks['m']['revision'] += 1
        self.assertNotEqual(fingerprint(before), fingerprint(changed))
        changed = copy.deepcopy(before)
        changed._statblocks['m']['prepared_at'] = ('2000-01-01T00:00:00Z' if
            before._statblocks['m']['prepared_at'] != '2000-01-01T00:00:00Z' else '2001-01-01T00:00:00Z')
        self.assertTrue(state_changed(before, changed))
        self.assertNotEqual(fingerprint(before), fingerprint(changed))

    def test_equivalent_local_ids_and_array_order_remain_canonical(self):
        self.seed(); before = copy.deepcopy(self.c.STATE); changed = copy.deepcopy(before)
        value = changed._statblocks['m']
        dm = {row['local_id']:'custom-'+row['local_id'] for row in value['definitions']}
        nm = {row['local_id']:'custom-'+row['local_id'] for row in value['nodes']}
        for row in value['definitions']: row['local_id'] = dm[row['local_id']]
        for group in ('nodes','facts','warnings','provenance'):
            for row in value[group]:
                if row.get('definition_id') is not None: row['definition_id'] = dm[row['definition_id']]
                if group == 'nodes':
                    row['local_id'] = nm[row['local_id']]
                    if row['parent_local_id'] is not None: row['parent_local_id'] = nm[row['parent_local_id']]
                    if row.get('target_definition_local_id') is not None:
                        row['target_definition_local_id'] = dm[row['target_definition_local_id']]
        value['nodes'].reverse(); value['definitions'].reverse()
        self.assertEqual(fingerprint(before), fingerprint(changed))
        self.assertFalse(state_changed(before, changed))

    def test_activity_log_is_ignored_by_recovery_hash_not_full_state_comparison(self):
        self.seed(); changed = copy.deepcopy(self.c.STATE)
        changed['activity_log'].append({'id':'extra','action':'fixture'})
        changed['active_turn_id'] = 'm'
        self.assertEqual(fingerprint(self.c.STATE), fingerprint(changed))
        self.assertTrue(state_changed(self.c.STATE, changed))

    def test_signature_is_independent_and_does_not_enter_json_fields(self):
        self.seed(); before = copy.deepcopy(self.c.STATE._statblocks)
        value = private_signature(self.c.STATE); value['m']['source_label'] = 'Changed'
        self.assertEqual(self.c.STATE._statblocks, before)
        self.assertNotIn('_statblocks', self.c.STATE)
        self.assertNotIn('source_label', json.dumps(self.c.STATE))

    def test_invalid_private_content_is_rejected_not_silently_ignored(self):
        self.seed(); changed = copy.deepcopy(self.c.STATE)
        changed._statblocks['m']['model_version'] = 99
        with self.assertRaises(ValueError): fingerprint(changed)
        raw = dict(self.c.STATE); raw['_statblocks'] = self.c.STATE._statblocks
        with self.assertRaises(ValueError): fingerprint(raw)

    def test_reconcile_prunes_removed_monster_metadata_before_fingerprinting(self):
        self.seed(); before = copy.deepcopy(self.c.STATE)
        self.c.STATE['monsters'] = []; self.f.reconcile()
        self.assertEqual(self.c.STATE._statblocks, {})
        self.assertTrue(before._statblocks)
        self.assertNotEqual(fingerprint(before), fingerprint(self.c.STATE))

    def test_reconcile_does_not_silently_discard_invalid_map_type(self):
        self.seed(); self.c.STATE._statblocks = []
        with self.assertRaises(ValueError): self.f.reconcile()


if __name__ == '__main__': unittest.main()
