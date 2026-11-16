"""2C.1 clone kernel tests; public copy/move/Save As are not exercised here."""
import copy
import unittest
from unittest.mock import patch
import test_statblock_encounters as fixtures
from python.scrying_glass_statblock_cloning import clone_private_snapshots
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage


def reference_snapshot(label):
    value = fixtures.snapshot(label)
    value['prepared_at'] = '2000-01-01T00:00:00Z'
    value['definitions'] = [dict(local_id='spell',kind='spell',name='Fixture spell',source_key='fixture:spell',position=0)]
    value['nodes'] = [
        dict(local_id='root',parent_local_id=None,definition_id=None,position=0,kind='paragraph'),
        dict(local_id='ref',parent_local_id='root',definition_id=None,position=0,kind='reference',target_definition_local_id='spell'),
        dict(local_id='detail',parent_local_id=None,definition_id='spell',position=0,kind='paragraph'),
        dict(local_id='text',parent_local_id='detail',definition_id='spell',position=0,kind='text',text='Supporting rule.'),
    ]
    value['provenance'][0]['credits'] = [dict(position=0,attribution='Fixture terms',license_name='Fixture license')]
    return value


class PrivateCloneKernelTests(unittest.TestCase):
    setUp = fixtures.EncounterAdapterTests.setUp

    def target(self, name='copy', ids=('m',)):
        self.storage.save_setup(self.campaign, name, {'monsters':[{'id':ident,'hp':3} for ident in ids]})
        return self.storage.connection.execute(
            'SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?', (self.campaign,name)).fetchone()[0]

    def seed(self, label='Source'):
        value = self.api.load(self.encounter); value[PRIVATE_KEY]['m'] = reference_snapshot(label)
        return self.api.save(self.encounter, value)[PRIVATE_KEY]['m']

    def row(self, encounter):
        return self.storage.connection.execute('SELECT id FROM monsters WHERE encounter_id=?', (encounter,)).fetchone()[0]

    def test_clone_has_independent_graph_revision_time_and_source_immutability(self):
        self.seed(); original = self.seed('Latest'); target = self.target()
        source_head = self.storage._statblock_revision_head(self.row(self.encounter))
        result = clone_private_snapshots(self.storage, self.encounter, target)['m']
        self.assertGreater(original['revision'], 1); self.assertEqual(result['revision'], 1)
        self.assertNotEqual(result['prepared_at'], original['prepared_at'])
        for key in ('content_digest','definitions','nodes','facts','warnings','provenance'):
            self.assertEqual(result[key], original[key])
        self.assertNotEqual(self.row(self.encounter), self.row(target))
        self.assertEqual(self.api.load(self.encounter)[PRIVATE_KEY]['m'], original)
        self.assertEqual(self.storage._statblock_revision_head(self.row(self.encounter)), source_head)
        self.assertEqual(self.storage._statblock_revision_head(self.row(target)), 1)
        candidate = PrivateEncounterStorage(self.storage).load(target)
        candidate[PRIVATE_KEY]['m'] = reference_snapshot('Copy changed')
        self.api.save(target, candidate)
        self.assertEqual(self.api.load(self.encounter)[PRIVATE_KEY]['m'], original)
        self.assertEqual(list(self.storage.connection.execute('PRAGMA foreign_key_check')), [])

    def test_same_mismatched_and_owned_destinations_are_rejected(self):
        self.seed(); wrong = self.target('wrong', ('other',)); target = self.target()
        with self.assertRaises(ValueError): clone_private_snapshots(self.storage, self.encounter, self.encounter)
        with self.assertRaises(ValueError): clone_private_snapshots(self.storage, self.encounter, wrong)
        with self.storage.transaction(): self.storage._record_statblock_revision(self.row(target), 4)
        with self.assertRaises(ValueError): clone_private_snapshots(self.storage, self.encounter, target)
        self.assertEqual(self.api.load(target)[PRIVATE_KEY], {})
        occupied = self.target('occupied'); clone_private_snapshots(self.storage, self.encounter, occupied)
        before = self.api.load(occupied)
        with self.assertRaises(ValueError): clone_private_snapshots(self.storage, self.encounter, occupied)
        self.assertEqual(self.api.load(occupied), before)

    def test_counter_only_source_does_not_export_its_history(self):
        target = self.target()
        with self.storage.transaction(): self.storage._record_statblock_revision(self.row(self.encounter), 9)
        self.assertEqual(clone_private_snapshots(self.storage, self.encounter, target), {})
        self.assertEqual(self.storage._statblock_revision_head(self.row(target)), 0)
        value = self.api.load(target); value[PRIVATE_KEY]['m'] = reference_snapshot('First content')
        self.assertEqual(self.api.save(target, value)[PRIVATE_KEY]['m']['revision'], 1)
        self.assertEqual(self.storage._statblock_revision_head(self.row(self.encounter)), 9)

    def test_partial_graph_write_rolls_back_clone_and_outer_tracker_creation(self):
        self.seed(); value = self.api.load(self.encounter)
        value['monsters'].append({'id':'n','hp':5}); value[PRIVATE_KEY]['n'] = reference_snapshot('Other')
        self.api.save(self.encounter, value); before = copy.deepcopy(self.api.load(self.encounter))
        save = self.api.snapshots.__class__.save; calls = []
        def fail_second(writer, *args, **kwargs):
            calls.append(args[0])
            if len(calls) == 2: raise OSError('injected second graph failure')
            return save(writer, *args, **kwargs)
        with self.assertRaises(OSError):
            with self.storage.transaction():
                target = self.target('atomic', ('m','n'))
                with patch('python.scrying_glass_statblock_storage.StatblockStorage.save', new=fail_second):
                    clone_private_snapshots(self.storage, self.encounter, target)
        self.assertEqual(len(calls), 2)
        self.assertFalse(self.storage.setup_exists(self.campaign, 'atomic'))
        self.assertEqual(self.api.load(self.encounter), before)
        self.assertEqual(list(self.storage.connection.execute('PRAGMA foreign_key_check')), [])


if __name__ == '__main__': unittest.main()
