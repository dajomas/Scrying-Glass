"""2B.8 protected save/refresh tests with the production facade and recovery fixture.

These are not authenticated HTTP/browser or complete 2B.9 history tests.
"""
import asyncio
import copy
import unittest
from unittest.mock import patch
import test_statblock_stage2_contracts as contracts
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_restore import restore_bindings


class PrivateTransactionSaveTests(unittest.TestCase):
    setUp = contracts.StatblockStage2ContractTests.setUp
    tearDown = contracts.StatblockStage2ContractTests.tearDown
    call = contracts.StatblockStage2ContractTests.call
    encounter = contracts.StatblockStage2ContractTests.encounter
    seed = contracts.StatblockStage2ContractTests.seed
    stored = contracts.StatblockStage2ContractTests.stored

    def replace(self, label, hp=None):
        async def private_replace():
            value = self.c.STATE._statblocks['m']
            if value['source_label'] != label:
                value.pop('content_digest', None)
                value['source_label'] = label
            if hp is not None: self.c.STATE['monsters'][0]['hp'] = hp
        asyncio.run(transactional_handler(self.c, private_replace)())

    def runtime(self):
        setup = self.seed(); self.c.clear_active_setup(); self.c.save_state()
        db = self.c.STORAGE
        encounter = db.connection.execute('SELECT runtime_encounter_id FROM application_state WHERE id=1').fetchone()[0]
        api = PrivateEncounterStorage(db); state = api.load(encounter)
        state[PRIVATE_KEY]['m'] = contracts.reference_snapshot('Runtime')
        api.save(encounter, state, runtime=True); self.c.load_state()
        return setup, encounter

    def test_setup_private_only_replace_refreshes_and_reloads(self):
        original = self.seed(); before = copy.deepcopy(dict(self.c.STATE))
        self.replace('Changed'); saved = self.stored()['m']
        self.assertEqual(dict(self.c.STATE), before)
        self.assertEqual(saved['source_label'], 'Changed')
        self.assertEqual(saved['revision'], original['revision'] + 1)
        self.assertEqual(saved['nodes'], original['nodes'])
        self.assertEqual(saved['definitions'], original['definitions'])
        self.assertEqual(self.c.STATE._statblocks, self.stored())
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, self.stored())

    def test_unchanged_and_tracker_only_changes_keep_metadata(self):
        original = self.seed(); self.replace(original['source_label'])
        self.call('edit_features', 'm', {'temp_hp':7})
        self.assertEqual(self.stored()['m'], original)
        self.assertEqual(self.c.STATE._statblocks, self.stored())

    def test_runtime_private_replace_does_not_touch_saved_setup(self):
        setup, encounter = self.runtime(); api = PrivateEncounterStorage(self.c.STORAGE)
        original = api.load(encounter)[PRIVATE_KEY]['m']
        self.replace('Runtime changed'); saved = api.load(encounter)[PRIVATE_KEY]['m']
        self.assertEqual(saved['revision'], original['revision'] + 1)
        self.assertEqual(saved['source_label'], 'Runtime changed')
        self.assertEqual(self.stored()['m'], setup)
        self.assertEqual(self.c.STATE._statblocks, {'m':saved})
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, {'m':saved})

    def test_stale_metadata_and_ordinary_omission_fail_without_clearing(self):
        self.seed(); stale = copy.deepcopy(self.c.STATE); current = self.seed('Current')
        async def stale_change():
            self.c.STATE = stale
            self.c.STATE._statblocks['m'].pop('content_digest', None)
            self.c.STATE._statblocks['m']['source_label'] = 'Stale change'
        with self.assertRaisesRegex(ValueError, 'Stale'):
            asyncio.run(transactional_handler(self.c, stale_change)())
        async def omit(): self.c.STATE._statblocks = {}
        with self.assertRaisesRegex(ValueError, 'Omitted'):
            asyncio.run(transactional_handler(self.c, omit)())
        self.assertEqual(self.stored()['m'], current)
        self.assertEqual(self.c.STATE._statblocks, self.stored())

    def test_failed_final_refresh_rolls_back_tracker_graph_counter_and_memory(self):
        self.seed(); before = copy.deepcopy(self.c.STATE); stored = self.stored()
        db = self.c.STORAGE; encounter = self.encounter(); bindings = restore_bindings(db, encounter)
        stamp = db.connection.execute('SELECT updated_at FROM battle_setups WHERE encounter_id=?', (encounter,)).fetchone()[0]
        load = PrivateEncounterStorage.load
        def fail_changed(api, owner):
            value = load(api, owner)
            if owner == encounter and value[PRIVATE_KEY].get('m', {}).get('source_label') == 'Changed':
                raise OSError('injected final refresh failure')
            return value
        with patch.object(PrivateEncounterStorage, 'load', fail_changed):
            with self.assertRaises(OSError): self.replace('Changed', hp=1)
        self.assertEqual(self.c.STATE, before); self.assertEqual(self.c.STATE._statblocks, before._statblocks)
        self.assertEqual(self.stored(), stored); self.assertEqual(restore_bindings(db, encounter), bindings)
        self.assertEqual(db.connection.execute('SELECT updated_at FROM battle_setups WHERE encounter_id=?', (encounter,)).fetchone()[0], stamp)
        self.assertFalse(db.connection.in_transaction)

    def test_rebuild_then_private_replace_advances_once(self):
        original = self.seed(); db = self.c.STORAGE; encounter = self.encounter()
        before = restore_bindings(db, encounter)['m']; save = db._save_entities
        def rebuild(table, owner_name, owner, items):
            if table == 'monsters':
                db.connection.execute('DELETE FROM monsters WHERE encounter_id=?', (owner,))
            return save(table, owner_name, owner, items)
        with patch.object(db, '_save_entities', side_effect=rebuild): self.replace('Changed')
        after = restore_bindings(db, encounter)['m']
        self.assertNotEqual(before[0], after[0]); self.assertEqual(after[1], original['revision'] + 1)
        self.assertEqual(self.c.STATE._statblocks, self.stored())


if __name__ == '__main__': unittest.main()
