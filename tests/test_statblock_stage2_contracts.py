"""Stage 2 preservation contracts; intentionally not expected-failure/skip tests.

Several paths are not implemented yet. Assertions describe required behavior;
AST parsing is not execution, and a green result is not claimed for this stage.
"""
import asyncio
import copy
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import test_encounter_features as fixtures
from test_statblock_encounters import snapshot
from python.scrying_glass_admin_setups import AdminSetupsMixin
from python.scrying_glass_combatant import reset_entity
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_service_features import fingerprint
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage


def private_map(state):
    return getattr(state, '_statblocks', state.get(PRIVATE_KEY, {}))


def reference_snapshot(label):
    value = snapshot(label)
    value['definitions'] = [dict(local_id='spell', kind='spell', name='Fixture spell',
        source_key='fixture:spell', position=0)]
    value['nodes'] = [
        dict(local_id='root', parent_local_id=None, definition_id=None, position=0, kind='paragraph'),
        dict(local_id='ref', parent_local_id='root', definition_id=None, position=0,
             kind='reference', target_definition_local_id='spell'),
        dict(local_id='details', parent_local_id=None, definition_id='spell', position=0, kind='paragraph'),
        dict(local_id='text', parent_local_id='details', definition_id='spell', position=0,
             kind='text', text='Retain this supporting rule.'),
    ]
    return value


class StatblockStage2ContractTests(unittest.TestCase):
    setUp = fixtures.FeatureTests.setUp
    tearDown = fixtures.FeatureTests.tearDown
    call = fixtures.FeatureTests.call
    item = fixtures.FeatureTests.item

    def encounter(self, campaign=None, name='default'):
        row = self.c.STORAGE.connection.execute(
            'SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',
            (campaign or self.c.active_campaign(), name)).fetchone()
        self.assertIsNotNone(row)
        return row[0]

    def stored(self, campaign=None, name='default'):
        return PrivateEncounterStorage(self.c.STORAGE).load(self.encounter(campaign, name))[PRIVATE_KEY]

    def seed(self, label='Original'):
        api = PrivateEncounterStorage(self.c.STORAGE); encounter = self.encounter()
        state = api.load(encounter); state[PRIVATE_KEY]['m'] = reference_snapshot(label)
        saved = api.save(encounter, state)[PRIVATE_KEY]['m']
        self.c.load_state()
        self.assertEqual(private_map(self.c.STATE)['m'], saved)
        return saved

    def assert_content(self, actual, expected):
        for key in ('content_digest', 'source_label', 'definitions', 'nodes', 'facts', 'warnings', 'provenance'):
            self.assertEqual(actual[key], expected[key], key)

    def test_reset_preserves_content_and_metadata_after_save_reload(self):
        before = self.seed()
        reset_entity(self.item())
        self.c.save_active_setup_monsters(); self.c.save_state(); self.c.load_state()
        self.assertEqual(private_map(self.c.STATE)['m'], before)
        self.assertEqual(self.stored()['m'], before)
        self.assertFalse(self.item()['active'])

    def test_checkpoint_capture_retains_private_content_and_references(self):
        before = self.seed()
        ident = self.call('save_checkpoint', {'name':'With private content'})['id']
        loaded = self.f.store.load(ident, self.c.active_campaign(), 'checkpoint')
        self.assertIn('m', private_map(loaded))
        self.assert_content(private_map(loaded)['m'], before)

    def test_checkpoint_restore_replaces_current_content_at_new_revision(self):
        before = self.seed()
        ident = self.call('save_checkpoint', {'name':'Original content'})['id']
        replacement = self.seed('Replacement')
        self.call('restore_checkpoint', ident, {'confirm':True, 'revision':self.f.store.revision()})
        self.assertIn('m', private_map(self.c.STATE))
        self.assert_content(private_map(self.c.STATE)['m'], before)
        restored = self.stored()['m']; self.assert_content(restored, before)
        self.assertGreater(restored['revision'], replacement['revision'])

    def test_restore_checkpoint_without_content_explicitly_clears_newer_content(self):
        ident = self.call('save_checkpoint', {'name':'No statblock yet'})['id']
        self.seed('Added later')
        self.call('restore_checkpoint', ident, {'confirm':True, 'revision':self.f.store.revision()})
        self.assertEqual(private_map(self.c.STATE), {})
        self.assertEqual(self.stored(), {})

    def test_setup_copy_has_independent_content_ownership(self):
        before = self.seed(); campaign = self.c.active_campaign()
        name = self.c.STORAGE.transfer_setup(campaign, campaign, 'default', 'copy')
        copied = self.stored(campaign, name)
        self.assertIn('m', copied); self.assert_content(copied['m'], before)
        self.assertEqual(copied['m']['revision'], 1)
        source_row = self.c.STORAGE.connection.execute(
            'SELECT id FROM monsters WHERE encounter_id=? AND combatant_id=?', (self.encounter(), 'm')).fetchone()[0]
        copied_row = self.c.STORAGE.connection.execute(
            'SELECT id FROM monsters WHERE encounter_id=? AND combatant_id=?', (self.encounter(campaign,name), 'm')).fetchone()[0]
        self.assertNotEqual(source_row, copied_row)
        api = PrivateEncounterStorage(self.c.STORAGE); value = api.load(self.encounter(campaign,name))
        value[PRIVATE_KEY]['m'] = reference_snapshot('Copy changed')
        api.save(self.encounter(campaign,name), value)
        self.assertEqual(self.stored()['m'], before)

    def test_setup_move_preserves_the_moved_encounter_without_reattaching_elsewhere(self):
        before = self.seed(); source = self.c.active_campaign(); encounter = self.encounter()
        target = self.c.STORAGE.create_campaign('Destination', '', 'now')
        self.c.STORAGE.save_characters(target, [])
        name = self.c.STORAGE.transfer_setup(source, target, 'default', 'move')
        self.assertFalse(self.c.STORAGE.setup_exists(source, 'default'))
        self.assertEqual(self.encounter(target,name), encounter)
        self.assertEqual(self.stored(target,name)['m'], before)
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')), [])

    def test_save_as_preserves_content_in_the_new_setup(self):
        before = self.seed(); campaign = self.c.active_campaign()
        self.c.STORAGE.save_setup(campaign, 'save-as', self.c.setup_snapshot(self.c.STATE))
        copied = self.stored(campaign, 'save-as')
        self.assertIn('m', copied); self.assert_content(copied['m'], before)
        self.assertEqual(copied['m']['revision'], 1)
        self.assertEqual(self.stored()['m'], before)

    def test_setup_import_remaps_monster_binding_and_keeps_reference_graph(self):
        before = self.seed()
        handler = AdminSetupsMixin(); handler.context = self.c
        payload = SimpleNamespace(name='default', campaign=self.c.active_campaign(), kind='monsters', life_filter='all')
        asyncio.run(transactional_handler(self.c, handler.import_setup)(payload))
        clones = [item for item in self.c.STATE['monsters'] if item['id'] != 'm']
        self.assertEqual(len(clones), 1); ident = clones[0]['id']
        self.assertIn(ident, private_map(self.c.STATE))
        self.assert_content(private_map(self.c.STATE)[ident], before)
        stored = self.stored(); self.assertIn(ident, stored)
        self.assert_content(stored[ident], before)
        self.assertEqual(stored[ident]['revision'], 1)
        self.assertEqual(stored['m'], before)

    def test_private_only_change_affects_recovery_fingerprint(self):
        self.seed(); before = copy.deepcopy(self.c.STATE)
        self.seed('Private-only replacement'); after = self.c.STATE
        self.assertEqual(dict(before), dict(after))
        self.assertNotEqual(private_map(before), private_map(after))
        self.assertNotEqual(fingerprint(before), fingerprint(after))

    def test_failed_restore_rolls_back_state_content_and_revision(self):
        self.seed(); ident = self.call('save_checkpoint', {'name':'Before'})['id']
        self.seed('Current'); before = copy.deepcopy(self.c.STATE); stored = copy.deepcopy(self.stored())
        revision = self.f.store.revision(); original = self.f.restore_state
        def fail_after_restore(state):
            original(state); self.c.save_active_setup_monsters()
            raise OSError('injected restore failure')
        with patch.object(self.f, 'restore_state', side_effect=fail_after_restore):
            with self.assertRaises(OSError):
                self.call('restore_checkpoint', ident, {'confirm':True, 'revision':revision})
        self.assertEqual(self.c.STATE, before)
        self.assertEqual(private_map(self.c.STATE), private_map(before))
        self.assertEqual(self.stored(), stored)
        self.assertEqual(self.f.store.revision(), revision)
        self.assertFalse(self.c.STORAGE.connection.in_transaction)


if __name__ == '__main__': unittest.main()
