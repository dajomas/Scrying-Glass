"""2C.2b native move-preservation regressions; not protected-service coverage."""
import unittest
from unittest.mock import patch
import test_statblock_encounters as fixtures
from test_statblock_clone_kernel import reference_snapshot
from python.scrying_glass_identity_rules import ParticipantIdentityConflict
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_revisions import MAX_REVISION, REVISION_FIELD
from python.scrying_glass_statblock_storage import FIELDS, StatblockStorage


class SetupPrivateMoveTests(unittest.TestCase):
    setUp = fixtures.EncounterAdapterTests.setUp

    def binding(self, campaign, name):
        return dict(self.storage.connection.execute(
            'SELECT * FROM battle_setups WHERE campaign_id=? AND name=?', (campaign,name)).fetchone())

    def monster(self, encounter):
        return self.storage.connection.execute('SELECT id FROM monsters WHERE encounter_id=?', (encounter,)).fetchone()[0]

    def seed(self, label):
        state = self.api.load(self.encounter); state[PRIVATE_KEY]['m'] = reference_snapshot(label)
        return self.api.save(self.encounter, state)[PRIVATE_KEY]

    def private_rows(self):
        tables = ['monster_statblocks', *('statblock_' + name for name in sorted(FIELDS))]
        result = {table:[tuple(row) for row in self.storage.connection.execute(
            'SELECT * FROM ' + table + ' ORDER BY id')] for table in tables}
        result['counters'] = [tuple(row) for row in self.storage.connection.execute(
            'SELECT * FROM monsters_attributes WHERE field_name=? ORDER BY id', (REVISION_FIELD,))]
        return result

    def dump(self):
        return '\n'.join(self.storage.connection.iterdump())

    def test_same_and_cross_campaign_moves_retain_ownership_and_metadata(self):
        self.seed('First'); metadata = self.seed('Latest')
        target = self.storage.create_campaign('Other', '', 'now')
        self.storage.save_setup(target, 'one-2', {'monsters':[{'id':'existing','hp':1}]})
        occupied = self.binding(target, 'one-2')
        state = self.api.load(occupied['encounter_id'])
        state[PRIVATE_KEY]['existing'] = reference_snapshot('Existing target')
        self.api.save(occupied['encounter_id'], state)
        self.storage.set_value('runtime_state', {'monsters':[], 'active_setup':{'campaign_id':self.campaign,'name':'one'}})
        with self.storage.transaction():
            self.storage.connection.execute('UPDATE campaigns SET last_setup_id=? WHERE id=?', (occupied['id'],target))
        before = self.private_rows(); owner = self.encounter; monster = self.monster(owner)
        source, name = self.campaign, 'one'
        with patch('python.scrying_glass_statblock_cloning.clone_private_snapshots', side_effect=AssertionError('move cloned')) as clone, patch.object(StatblockStorage, 'save', side_effect=AssertionError('move rewrote snapshot')) as save:
            for destination in (self.campaign, target):
                with self.subTest(destination=destination):
                    binding = self.binding(source, name)
                    result = self.storage.transfer_setup(source, destination, name, 'move')
                    moved = self.binding(destination, result)
                    self.assertEqual((moved['id'],moved['encounter_id'],moved['updated_at']), (binding['id'],owner,binding['updated_at']))
                    self.assertEqual(self.monster(owner), monster)
                    self.assertFalse(self.storage.setup_exists(source, name))
                    self.assertEqual(self.api.load(owner)[PRIVATE_KEY], metadata)
                    self.assertEqual(self.private_rows(), before)
                    self.assertIsNone(self.storage.load_setup(destination, result).get('active_setup'))
                    self.assertEqual(self.storage.get_value('runtime_state')['active_setup'], {'campaign_id':destination,'name':result})
                    source, name = destination, result
            clone.assert_not_called(); save.assert_not_called()
        self.assertEqual(name, 'one-2-2')
        self.assertEqual(self.binding(target, 'one-2'), occupied)
        self.assertEqual(self.storage.connection.execute('SELECT last_setup_id FROM campaigns WHERE id=?', (target,)).fetchone()[0], occupied['id'])
        self.storage._check_foreign_keys()

    def test_counter_only_moves_survive_reopen_even_at_revision_limit(self):
        target = self.storage.create_campaign('Other', '', 'now')
        for index, (destination, head) in enumerate(((self.campaign,9),(target,MAX_REVISION))):
            with self.subTest(head=head):
                name = 'cleared-' + str(index)
                self.storage.save_setup(self.campaign, name, {'monsters':[{'id':'m','hp':2}]})
                binding = self.binding(self.campaign, name); owner = binding['encounter_id']; monster = self.monster(owner)
                with self.storage.transaction(): self.storage._record_statblock_revision(monster, head)
                before = self.private_rows()
                with patch('python.scrying_glass_statblock_cloning.clone_private_snapshots', side_effect=AssertionError('move cloned')), patch.object(StatblockStorage, 'save', side_effect=AssertionError('move allocated snapshot')):
                    result = self.storage.transfer_setup(self.campaign, destination, name, 'move')
                self.storage.close(); self.storage = self.storage.__class__(self.path)
                self.api = PrivateEncounterStorage(self.storage)
                moved = self.binding(destination, result)
                self.assertEqual((moved['id'],moved['encounter_id']), (binding['id'],owner))
                self.assertEqual(self.monster(owner), monster)
                self.assertEqual(self.api.load(owner)[PRIVATE_KEY], {})
                self.assertEqual(self.storage._statblock_revision_head(monster), head)
                self.assertEqual(self.private_rows(), before)
                self.assertFalse(self.storage.setup_exists(self.campaign, name))

    def test_late_failure_restores_bindings_graphs_counters_and_last_setup(self):
        self.seed('First'); self.seed('Latest')
        target = self.storage.create_campaign('Other', '', 'now')
        self.storage.save_setup(self.campaign, 'cleared', {'monsters':[{'id':'m','hp':2}]})
        cleared = self.binding(self.campaign, 'cleared')
        with self.storage.transaction(): self.storage._record_statblock_revision(self.monster(cleared['encounter_id']), 9)
        for name in ('one', 'cleared'):
            with self.subTest(name=name):
                self.storage.save_setup(target, name, {'monsters':[{'id':'existing','hp':1}]})
                binding = self.binding(self.campaign, name)
                with self.storage.transaction():
                    self.storage.connection.execute('UPDATE campaigns SET last_setup_id=? WHERE id=?', (binding['id'],self.campaign))
                before = self.dump(); save = self.storage.save_setup; observed = []
                def fail_after_save(*args, **kwargs):
                    save(*args, **kwargs)
                    moved = self.binding(target, name + '-2')
                    observed.append(moved['id'])
                    raise OSError('injected after moved encounter save')
                with patch.object(self.storage, 'save_setup', side_effect=fail_after_save):
                    with self.assertRaises(OSError): self.storage.transfer_setup(self.campaign, target, name, 'move')
                self.assertEqual(observed, [binding['id']])
                self.assertEqual(self.dump(), before)
                self.assertFalse(self.storage.connection.in_transaction)

    def test_source_scope_and_destination_roster_rejections_do_not_write(self):
        self.seed('Source'); target = self.storage.create_campaign('Other', '', 'now')
        self.storage.save_characters(target, [{'id':'m','hp':4}]); before = self.dump()
        cases = ((self.campaign,'missing',FileNotFoundError), (target,'one',FileNotFoundError), (self.campaign,'one',ParticipantIdentityConflict))
        for source, name, error in cases:
            with self.subTest(source=source, name=name):
                with self.assertRaises(error): self.storage.transfer_setup(source, target, name, 'move')
                self.assertEqual(self.dump(), before)


if __name__ == '__main__': unittest.main()
