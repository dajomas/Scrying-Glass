"""2B.9 production-fixture integration; not authenticated HTTP/browser coverage."""
import asyncio
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch
import test_statblock_private_transaction_saves as saves
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_service_features import fingerprint
from python.scrying_glass_statblock_loading import PrivateEncounterState, carry_private
from python.scrying_glass_statblock_model import ModelLimits, StatblockError, validate_snapshot
from python.scrying_glass_statblock_restore import restore_bindings
from python.scrying_glass_statblock_saving import flush_private_state


class PrivateLifecycleIntegrationTests(unittest.TestCase):
    setUp = saves.PrivateTransactionSaveTests.setUp
    tearDown = saves.PrivateTransactionSaveTests.tearDown
    call = saves.PrivateTransactionSaveTests.call
    encounter = saves.PrivateTransactionSaveTests.encounter
    seed = saves.PrivateTransactionSaveTests.seed
    stored = saves.PrivateTransactionSaveTests.stored

    def edit(self, label):
        async def edit_monster():
            value = self.c.STATE._statblocks['m']
            if value['source_label'] != label:
                value.pop('content_digest', None)
                value['source_label'] = label
        asyncio.run(transactional_handler(self.c, edit_monster)())

    def undo(self):
        self.call('undo', {'id':self.f.summary()['undo']['id']})

    def test_history_uses_saved_metadata_and_broadcast_observes_commit(self):
        original = self.seed(); revision = self.f.store.revision(); seen = []
        def committed():
            seen.append((self.c.STORAGE.connection.in_transaction, self.f.store.revision(),
                         copy.deepcopy(self.stored()), self.f.store.latest_undo(self.c.active_campaign())['after_digest']))
        self.c.broadcast = AsyncMock(side_effect=committed)
        self.edit('Changed')
        self.c.broadcast.assert_awaited_once_with()
        self.assertEqual(seen, [(False,revision+1,self.stored(),fingerprint(self.c.STATE))])
        top = self.f.store.latest_undo(self.c.active_campaign())
        image = self.f.store.load(top['id'], self.c.active_campaign(), 'undo')
        self.assertEqual(image._statblocks['m'], original)
        self.assertNotIn('Retain this supporting rule.', json.dumps(self.c.public_state()))
        self.assertNotIn('Retain this supporting rule.', json.dumps(self.c.display_state()))

    def test_two_private_edits_undo_in_sequence_with_monotonic_revisions(self):
        original = self.seed(); self.edit('Second'); self.edit('Third')
        revision = self.stored()['m']['revision']
        self.undo(); self.assertEqual(self.stored()['m']['source_label'], 'Second')
        self.assertGreater(self.stored()['m']['revision'], revision)
        revision = self.stored()['m']['revision']; self.undo()
        self.assertEqual(self.stored()['m']['content_digest'], original['content_digest'])
        self.assertGreater(self.stored()['m']['revision'], revision)
        self.assertEqual(self.c.STATE._statblocks, self.stored())

    def test_noop_does_not_change_history_revision_or_broadcast(self):
        self.seed(); self.edit('Second'); before = copy.deepcopy(self.stored())
        history = self.f.store.list(self.c.active_campaign(), 'undo'); revision = self.f.store.revision()
        self.c.broadcast = AsyncMock(); self.edit('Second')
        self.assertEqual(self.stored(), before)
        self.assertEqual(self.f.store.list(self.c.active_campaign(), 'undo'), history)
        self.assertEqual(self.f.store.revision(), revision); self.c.broadcast.assert_not_awaited()

    def test_failure_after_history_write_rolls_back_everything_without_broadcast(self):
        self.seed(); self.edit('Second'); before = copy.deepcopy(self.c.STATE)
        content = self.stored(); bindings = restore_bindings(self.c.STORAGE, self.encounter())
        history = self.f.store.list(self.c.active_campaign(), 'undo'); revision = self.f.store.revision()
        after = self.f.after_transaction
        def fail(*args): after(*args); raise OSError('injected after history')
        self.c.broadcast = AsyncMock()
        with patch.object(self.f, 'after_transaction', side_effect=fail):
            with self.assertRaises(OSError): self.edit('Third')
        self.assertEqual(self.c.STATE, before); self.assertEqual(self.c.STATE._statblocks, before._statblocks)
        self.assertEqual(self.stored(), content)
        self.assertEqual(restore_bindings(self.c.STORAGE, self.encounter()), bindings)
        self.assertEqual(self.f.store.list(self.c.active_campaign(), 'undo'), history)
        self.assertEqual(self.f.store.revision(), revision); self.c.broadcast.assert_not_awaited()

    def test_clear_reload_reopen_and_undo_keep_absence_and_counter_history(self):
        empty = self.call('save_checkpoint', {'name':'Empty'})['id']; original = self.seed()
        self.call('restore_checkpoint', empty, {'confirm':True,'revision':self.f.store.revision()})
        head = restore_bindings(self.c.STORAGE, self.encounter())['m'][1]
        self.assertEqual(head, original['revision'] + 1)
        storage = self.c.STORAGE; path = storage.connection.execute('PRAGMA database_list').fetchone()[2]
        storage.close(); self.c.STORAGE = storage.__class__(Path(path)); self.c.load_state()
        self.assertIsInstance(self.c.STATE, PrivateEncounterState)
        self.assertEqual(self.c.STATE._statblocks, {})
        self.assertEqual(restore_bindings(self.c.STORAGE, self.encounter())['m'][1], head)
        self.undo(); self.assertEqual(self.stored()['m']['content_digest'], original['content_digest'])
        self.assertGreater(self.stored()['m']['revision'], head)

    def test_lower_preparation_defaults_do_not_block_trusted_roundtrips(self):
        self.seed()
        with patch.object(ModelLimits.__init__, '__defaults__', (128,1,1,8,1)):
            with self.assertRaises(StatblockError): validate_snapshot(self.stored()['m'], ModelLimits())
            self.edit('Lowered limits')
            checkpoint = self.call('save_checkpoint', {'name':'Lowered'})['id']
            self.edit('Another version')
            self.call('restore_checkpoint', checkpoint, {'confirm':True,'revision':self.f.store.revision()})
            self.assertEqual(self.stored()['m']['source_label'], 'Lowered limits')
            self.assertEqual(self.c.STATE._statblocks, self.stored())

    def test_missing_and_foreign_setup_bindings_do_not_write_private_content(self):
        self.seed(); before = copy.deepcopy(self.c.STATE); content = self.stored()
        other = self.c.STORAGE.create_campaign('Other', '', 'now')
        self.c.STORAGE.save_setup(other, 'default', {'monsters':[{'id':'m','hp':8}]})
        foreign = self.stored(other)
        try:
            for reference in ({'campaign_id':self.c.active_campaign(),'name':'missing'},
                              {'campaign_id':other,'name':'default'}):
                self.c.STATE['active_setup'] = reference
                with self.c.STORAGE.transaction():
                    with self.assertRaises(ValueError): flush_private_state(self.c)
        finally: self.c.STATE = before
        self.assertEqual(self.stored(), content); self.assertEqual(self.stored(other), foreign)

    def test_revision_exhaustion_rolls_back_without_history_or_broadcast(self):
        self.seed(); db = self.c.STORAGE; owner = restore_bindings(db, self.encounter())['m'][0]
        with db.transaction(): db._record_statblock_revision(owner, 2**63-1)
        before = copy.deepcopy(self.c.STATE); content = self.stored(); revision = self.f.store.revision()
        self.c.broadcast = AsyncMock()
        with self.assertRaises(ValueError): self.edit('Overflow')
        self.assertEqual(self.c.STATE._statblocks, before._statblocks); self.assertEqual(self.stored(), content)
        self.assertEqual(restore_bindings(db, self.encounter())['m'][1], 2**63-1)
        self.assertEqual(self.f.store.revision(), revision)
        self.assertIsNone(self.f.summary()['undo']); self.c.broadcast.assert_not_awaited()


class CarryAbsenceTests(unittest.TestCase):
    def test_trusted_empty_map_survives_carry_deepcopy_and_json_projection(self):
        plain = {'monsters':[{'id':'m'}]}; source = PrivateEncounterState(plain, {})
        result = carry_private(source, plain)
        self.assertIsInstance(result, PrivateEncounterState); self.assertEqual(result._statblocks, {})
        clone = copy.deepcopy(result); clone._statblocks['m'] = {}
        self.assertEqual(result._statblocks, {}); self.assertEqual(source._statblocks, {})
        self.assertNotIn('_statblocks', json.dumps(result))

    def test_plain_source_does_not_gain_private_authority(self):
        plain = {'monsters':[{'id':'m'}]}; result = carry_private(plain, plain)
        self.assertIs(type(result), dict); self.assertFalse(hasattr(result, '_statblocks'))

    def test_invalid_empty_like_map_is_not_silently_dropped(self):
        plain = {'monsters':[{'id':'m'}]}
        for value in ([], False, None):
            with self.subTest(value=value):
                with self.assertRaises(ValueError): carry_private(PrivateEncounterState(plain, value), plain)


if __name__ == '__main__': unittest.main()
