"""Increment 2A recovery capture/read tests; restore/apply and copies are separate."""
import copy
import json
import unittest
from unittest.mock import patch
import test_statblock_stage2_contracts as contracts
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_loading import PrivateEncounterState


class RecoveryCaptureTests(unittest.TestCase):
    setUp = contracts.StatblockStage2ContractTests.setUp
    tearDown = contracts.StatblockStage2ContractTests.tearDown
    encounter = contracts.StatblockStage2ContractTests.encounter
    stored = contracts.StatblockStage2ContractTests.stored
    seed = contracts.StatblockStage2ContractTests.seed

    def capture(self, kind='checkpoint', state=None):
        return self.f.store.save_snapshot(self.c.active_campaign(), self.c.STATE if state is None else state,
                                          kind, 'Recovery fixture')

    def counts(self):
        return {table:self.c.STORAGE.connection.execute('SELECT count(*) FROM '+table).fetchone()[0]
            for table in ('encounters','monsters','encounter_snapshots','snapshot_characters',
                          'monster_statblocks','statblock_definitions','statblock_nodes','statblock_provenance')}

    def test_checkpoint_and_undo_roundtrip_full_historical_metadata(self):
        self.seed('First'); expected = self.seed('Second')
        self.assertGreater(expected['revision'], 1)
        for kind in ('checkpoint','undo'):
            ident = self.capture(kind)
            loaded = self.f.store.load(ident, self.c.active_campaign(), kind)
            self.assertIsInstance(loaded, PrivateEncounterState)
            self.assertEqual(loaded._statblocks, {'m':expected})
            self.assertNotIn(PRIVATE_KEY, loaded)
            self.assertNotIn('source_label', json.dumps(loaded))
            self.assertEqual(loaded['characters'], self.c.STATE['characters'])
            self.assertEqual(loaded['active_setup'], self.c.STATE['active_setup'])
        self.assertEqual(self.stored(), {'m':expected})

    def test_capture_without_content_is_explicit_empty_and_does_not_guess_source(self):
        self.seed()
        ident = self.capture(state=dict(self.c.STATE))
        loaded = self.f.store.load(ident, self.c.active_campaign(), 'checkpoint')
        self.assertIsInstance(loaded, PrivateEncounterState)
        self.assertEqual(loaded._statblocks, {})
        self.assertNotIn(PRIVATE_KEY, loaded)
        self.assertTrue(self.stored())

    def test_captured_records_are_independent_from_source(self):
        expected = self.seed(); ident = self.capture()
        encounter = self.f.store.row(ident, self.c.active_campaign(), 'checkpoint')['encounter_id']
        sql = self.c.STORAGE.connection
        headers = list(sql.execute(
            'SELECT s.id,s.monster_id FROM monster_statblocks s JOIN monsters m ON m.id=s.monster_id '
            'WHERE m.encounter_id IN (?,?)', (self.encounter(), encounter)))
        self.assertEqual(len(headers), 2)
        self.assertEqual(len({r['id'] for r in headers}), 2)
        self.assertEqual(len({r['monster_id'] for r in headers}), 2)
        api = PrivateEncounterStorage(self.c.STORAGE); state = api.load(encounter)
        state[PRIVATE_KEY]['m'] = contracts.reference_snapshot('Captured copy changed')
        api.save(encounter, state)
        self.assertEqual(self.stored(), {'m':expected})
        self.assertEqual(self.f.store.load(ident, self.c.active_campaign(), 'checkpoint')._statblocks['m']['source_label'],
                         'Captured copy changed')

    def test_invalid_private_graph_is_rejected_before_transaction_or_allocation(self):
        self.seed(); candidate = copy.deepcopy(self.c.STATE)
        candidate._statblocks['m']['model_version'] = 99
        before = self.counts()
        with patch.object(self.c.STORAGE, 'transaction', side_effect=AssertionError('must validate first')):
            with self.assertRaises(ValueError): self.capture(state=candidate)
        self.assertEqual(self.counts(), before)

    def test_serialized_private_field_is_not_a_trusted_capture_channel(self):
        self.seed(); candidate = dict(self.c.STATE)
        candidate[PRIVATE_KEY] = copy.deepcopy(self.c.STATE._statblocks)
        before = self.counts()
        with self.assertRaises(ValueError): self.capture(state=candidate)
        self.assertEqual(self.counts(), before)

    def test_late_character_write_failure_rolls_back_direct_capture(self):
        expected = self.seed(); before = self.counts()
        original = self.c.STORAGE._save_entities
        def fail(table, owner_name, owner, items):
            if table == 'snapshot_characters': raise OSError('injected character failure')
            return original(table, owner_name, owner, items)
        with patch.object(self.c.STORAGE, '_save_entities', side_effect=fail):
            with self.assertRaises(OSError): self.capture()
        self.assertEqual(self.counts(), before)
        self.assertEqual(self.stored(), {'m':expected})
        self.assertFalse(self.c.STORAGE.connection.in_transaction)

    def test_nested_capture_failure_keeps_unrelated_outer_transaction(self):
        self.seed(); before = self.counts(); db = self.c.STORAGE
        from python.scrying_glass_statblock_recovery import write_capture
        def fail(storage, encounter, prepared):
            write_capture(storage, encounter, prepared)
            raise OSError('injected after private rows')
        with db.transaction():
            db.update_campaign(self.c.active_campaign(), description='Outer change retained')
            with patch('python.scrying_glass_statblock_recovery.write_capture', side_effect=fail):
                with self.assertRaises(OSError): self.capture()
            self.assertTrue(db.connection.in_transaction)
            self.assertEqual(self.counts(), before)
        self.assertEqual(db.read_campaigns()['campaigns'][self.c.active_campaign()]['description'], 'Outer change retained')

    def test_wrong_campaign_kind_and_invalid_ids_reject_before_private_read(self):
        self.seed(); ident = self.capture(); campaign = self.c.active_campaign()
        other = self.c.STORAGE.create_campaign('Other scope', '', 'now')
        cases = [(ident,other,'checkpoint'), (ident,campaign,'undo'), (True,campaign,'checkpoint'),
                 (0,campaign,'checkpoint'), (2**80,campaign,'checkpoint')]
        with patch('python.scrying_glass_statblock_recovery.read_capture', side_effect=AssertionError('must scope first')):
            for args in cases:
                with self.subTest(args=args):
                    with self.assertRaises(ValueError): self.f.store.load(*args)

    def test_pruning_and_delete_cascade_preserve_only_live_source_content(self):
        expected = self.seed()
        for kind, count, limit in (('checkpoint',52,50), ('undo',32,30)):
            for _ in range(count): self.capture(kind)
            self.assertEqual(len(self.f.store.list(self.c.active_campaign(), kind)), limit)
        self.assertEqual(self.c.STORAGE.connection.execute('SELECT count(*) FROM monster_statblocks').fetchone()[0], 81)
        self.f.store.clear_undo()
        for row in self.f.store.list(self.c.active_campaign(), 'checkpoint'):
            self.f.store.delete(row['id'], self.c.active_campaign(), 'checkpoint')
        self.assertEqual(self.c.STORAGE.connection.execute('SELECT count(*) FROM monster_statblocks').fetchone()[0], 1)
        self.assertEqual(self.stored(), {'m':expected})
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])

    def test_stored_content_above_preparation_defaults_survives_capture(self):
        expected = self.seed('x' * 70000); ident = self.capture()
        loaded = self.f.store.load(ident, self.c.active_campaign(), 'checkpoint')
        self.assertEqual(loaded._statblocks, {'m':expected})


if __name__ == '__main__': unittest.main()
