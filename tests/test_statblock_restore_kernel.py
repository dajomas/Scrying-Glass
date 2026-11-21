"""Trusted recovery kernel: replacement, explicit absence and SQL clear guards."""
import copy
import sqlite3
import unittest
from unittest.mock import patch
import test_statblock_stage2_contracts as contracts
from python import scrying_glass_statblock_revisions as revisions
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_loading import PrivateEncounterState
from python.scrying_glass_statblock_restore import restore_bindings, restore_encounter, _clear_survivors


class RestoreKernelTests(unittest.TestCase):
    setUp = contracts.StatblockStage2ContractTests.setUp
    tearDown = contracts.StatblockStage2ContractTests.tearDown
    encounter = contracts.StatblockStage2ContractTests.encounter
    seed = contracts.StatblockStage2ContractTests.seed
    stored = contracts.StatblockStage2ContractTests.stored
    assert_content = contracts.StatblockStage2ContractTests.assert_content

    def bindings(self, state):
        return restore_bindings(self.c.STORAGE, self.encounter(), [m['id'] for m in state['monsters']])

    def restore(self, state, bindings=None):
        return restore_encounter(self.c.STORAGE, self.encounter(), state,
            expected_bindings=self.bindings(state) if bindings is None else bindings)

    def test_historical_replacement_uses_new_destination_revision_and_tracker_values(self):
        original = self.seed(); image = copy.deepcopy(self.c.STATE)
        replacement = self.seed('Replacement'); image['monsters'][0]['hp'] = 5
        result = self.restore(image)
        self.assert_content(result[PRIVATE_KEY]['m'], original)
        self.assertEqual(result[PRIVATE_KEY]['m']['revision'], replacement['revision'] + 1)
        self.assertEqual(result['monsters'][0]['hp'], 5)
        self.assertEqual(image._statblocks['m'], original)

    def test_identical_content_keeps_current_metadata(self):
        expected = self.seed(); image = copy.deepcopy(self.c.STATE)
        image._statblocks['m']['revision'] += 100
        result = self.restore(image)
        self.assertEqual(result[PRIVATE_KEY]['m'], expected)

    def test_trusted_clear_advances_head_and_ordinary_omission_still_fails(self):
        original = self.seed(); api = PrivateEncounterStorage(self.c.STORAGE)
        ordinary = api.load(self.encounter()); ordinary[PRIVATE_KEY] = {}
        with self.assertRaisesRegex(ValueError, 'Omitted'): api.save(self.encounter(), ordinary)
        image = PrivateEncounterState(copy.deepcopy(dict(self.c.STATE)), {})
        image['monsters'][0]['hp'] = 5
        result = self.restore(image)
        self.assertEqual(result[PRIVATE_KEY], {}); self.assertEqual(result['monsters'][0]['hp'], 5)
        head = self.bindings(image)['m'][1]
        self.assertEqual(head, original['revision'] + 1)
        self.restore(image)
        self.assertEqual(self.bindings(image)['m'][1], head)
        self.assertGreater(self.seed('Readded')['revision'], head)

    def test_stale_revision_rejects_before_tracker_writes(self):
        self.seed(); image = copy.deepcopy(self.c.STATE); bindings = self.bindings(image)
        latest = self.seed('Latest')
        with patch.object(self.c.STORAGE, '_save_encounter', side_effect=AssertionError('must not write')):
            with self.assertRaisesRegex(ValueError, 'Stale'): self.restore(image, bindings)
        self.assertEqual(self.stored()['m'], latest)

    def test_another_encounters_equal_combatant_id_is_not_a_valid_binding(self):
        self.seed(); image = copy.deepcopy(self.c.STATE); campaign = self.c.active_campaign()
        self.c.STORAGE.save_setup(campaign, 'other', {'monsters':[{'id':'m','hp':9}]})
        other = self.encounter(campaign, 'other')
        foreign = restore_bindings(self.c.STORAGE, other)
        with self.assertRaisesRegex(ValueError, 'Stale'): self.restore(image, foreign)
        self.assertEqual(self.c.STORAGE.load_setup(campaign, 'other')['monsters'][0]['hp'], 9)

    def test_failed_content_write_rolls_back_tracker_and_reference_content(self):
        self.seed(); image = copy.deepcopy(self.c.STATE); self.seed('Current')
        image['monsters'][0]['hp'] = 1
        api = PrivateEncounterStorage(self.c.STORAGE); before = api.load(self.encounter())
        bindings = self.bindings(image)
        with patch('python.scrying_glass_statblock_storage.StatblockStorage.save', side_effect=OSError('injected')):
            with self.assertRaises(OSError): self.restore(image, bindings)
        self.assertEqual(api.load(self.encounter()), before)
        self.assertFalse(self.c.STORAGE.connection.in_transaction)

    def test_removed_monster_cascades_without_a_surviving_clear(self):
        self.seed(); image = PrivateEncounterState(copy.deepcopy(dict(self.c.STATE)), {})
        image['monsters'] = []
        result = self.restore(image)
        self.assertEqual(result['monsters'], []); self.assertEqual(result[PRIVATE_KEY], {})

    def test_raw_dictionary_is_not_an_authoritative_restore_image(self):
        self.seed()
        with self.assertRaises(ValueError): self.restore(dict(self.c.STATE))

    def test_invalid_graph_is_rejected_before_restoration_transaction(self):
        self.seed(); image = copy.deepcopy(self.c.STATE); bindings = self.bindings(image)
        image._statblocks['m']['model_version'] = 99
        with patch.object(self.c.STORAGE, 'transaction', side_effect=AssertionError('must validate first')):
            with self.assertRaises(ValueError): self.restore(image, bindings)

    def test_absence_bindings_detect_clear_readd_clear_cycle(self):
        self.seed(); image = PrivateEncounterState(copy.deepcopy(dict(self.c.STATE)), {})
        self.restore(image); absent = self.bindings(image)
        self.seed('Again'); self.restore(image)
        with patch.object(self.c.STORAGE, '_save_encounter', side_effect=AssertionError('must not write')):
            with self.assertRaisesRegex(ValueError, 'Stale'): self.restore(image, absent)
        self.assertGreater(self.bindings(image)['m'][1], absent['m'][1])

    def test_clearing_without_durable_allocation_fails_before_tracker_writes(self):
        original = self.seed(); image = PrivateEncounterState(copy.deepcopy(dict(self.c.STATE)), {})
        with patch.object(self.c.STORAGE, '_next_statblock_revision', None), patch.object(self.c.STORAGE, '_save_encounter', side_effect=AssertionError('must not write')):
            with self.assertRaisesRegex(ValueError, 'durable'): self.restore(image)
        self.assertEqual(self.stored()['m'], original)

    def test_failed_mixed_clear_and_replace_restores_cleared_graph_and_counter(self):
        self.seed(); api = PrivateEncounterStorage(self.c.STORAGE); state = api.load(self.encounter())
        state['monsters'].append({'id':'n','hp':7})
        state[PRIVATE_KEY]['n'] = contracts.reference_snapshot('Other')
        before = api.save(self.encounter(), state); self.c.load_state()
        image = PrivateEncounterState(copy.deepcopy(dict(self.c.STATE)), {'n':contracts.reference_snapshot('Changed')})
        bindings = self.bindings(image)
        with patch('python.scrying_glass_statblock_storage.StatblockStorage.save', side_effect=OSError('after clear')):
            with self.assertRaises(OSError): self.restore(image, bindings)
        self.assertEqual(api.load(self.encounter()), before)
        self.assertEqual(self.bindings(image), bindings)


class ClearSqlTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:', isolation_level=None); self.db.row_factory = sqlite3.Row
        self.addCleanup(self.db.close); self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript("""
            CREATE TABLE monsters(id INTEGER PRIMARY KEY,encounter_id INTEGER,combatant_id TEXT);
            INSERT INTO monsters VALUES(1,10,'m'),(2,20,'m'),(3,10,'n');
            CREATE TABLE monster_statblocks(monster_id INTEGER UNIQUE REFERENCES monsters(id) ON DELETE CASCADE,revision INTEGER);
            INSERT INTO monster_statblocks VALUES(1,1),(2,4),(3,2);
            CREATE TABLE children(parent INTEGER REFERENCES monster_statblocks(monster_id) ON DELETE CASCADE);
            INSERT INTO children VALUES(1),(2),(3);
            CREATE TABLE monsters_attributes(parent_id INTEGER REFERENCES monsters(id) ON DELETE CASCADE,field_name TEXT,
              value_kind TEXT CHECK(value_kind IN ('null','text','integer','real','boolean','present')),
              text_value TEXT,integer_value INTEGER,real_value REAL,UNIQUE(parent_id,field_name));
        """)
        self.storage = revisions.StatblockRevisionMixin(); self.storage.connection = self.db

    def clear(self, bindings=None, ids=('m',), encounter=10):
        self.db.execute('SAVEPOINT clear_test')
        try:
            _clear_survivors(self.storage, encounter, ids, {}, {'m':(1,1)} if bindings is None else bindings)
            self.db.execute('RELEASE clear_test')
        except BaseException:
            self.db.execute('ROLLBACK TO clear_test'); self.db.execute('RELEASE clear_test'); raise

    def test_clear_advances_counter_cascades_and_keeps_other_encounter(self):
        self.clear()
        self.assertIsNone(self.db.execute('SELECT * FROM monster_statblocks WHERE monster_id=1').fetchone())
        self.assertEqual(revisions.revision_head(self.db, 1), 2)
        self.assertEqual(revisions.next_revision(self.db, 1), 3)
        self.assertEqual([r[0] for r in self.db.execute('SELECT parent FROM children ORDER BY parent')], [2,3])
        self.assertEqual(revisions.revision_head(self.db, 2), 4)
        self.clear({'m':(1,2)})
        self.assertEqual(revisions.revision_head(self.db, 1), 2)
        self.assertEqual(list(self.db.execute('PRAGMA foreign_key_check')), [])

    def test_wrong_scope_or_head_is_rejected(self):
        with self.assertRaises(ValueError): self.clear(encounter=20)
        with self.assertRaises(ValueError): self.clear({'m':(1,0)})
        with self.assertRaises(ValueError): self.clear({'n':(1,1)}, ids=('n',))
        self.assertEqual(revisions.revision_head(self.db, 1), 1)

    def test_missing_counter_protocol_is_rejected(self):
        self.storage._record_statblock_revision = None
        with self.assertRaises(ValueError): self.clear()
        self.assertIsNotNone(self.db.execute('SELECT * FROM monster_statblocks WHERE monster_id=1').fetchone())

    def test_overflow_preflights_all_clears_before_writing(self):
        revisions.record_revision(self.db, 3, revisions.MAX_REVISION)
        with self.assertRaises(ValueError): self.clear({'m':(1,1),'n':(3,revisions.MAX_REVISION)}, ids=('m','n'))
        self.assertEqual(revisions.revision_head(self.db, 1), 1)
        self.assertEqual(self.db.execute('SELECT count(*) FROM children').fetchone()[0], 3)

    def test_delete_failure_rolls_back_recorded_counter(self):
        self.db.execute("CREATE TRIGGER deny_clear BEFORE DELETE ON monster_statblocks BEGIN SELECT RAISE(ABORT,'injected'); END")
        with self.assertRaises(sqlite3.IntegrityError): self.clear()
        self.assertEqual(revisions.revision_head(self.db, 1), 1)
        self.assertEqual(self.db.execute('SELECT count(*) FROM children').fetchone()[0], 3)

    def test_invalid_allocator_and_corrupt_marker_fail_closed(self):
        allocate = self.storage._next_statblock_revision
        self.storage._next_statblock_revision = lambda owner: True
        with self.assertRaises(ValueError): self.clear()
        self.storage._next_statblock_revision = allocate
        revisions.record_revision(self.db, 1, 1)
        self.db.execute('UPDATE monsters_attributes SET text_value=NULL WHERE parent_id=1')
        with self.assertRaises(ValueError): self.clear()
        self.assertIsNotNone(self.db.execute('SELECT * FROM monster_statblocks WHERE monster_id=1').fetchone())


if __name__ == '__main__': unittest.main()
