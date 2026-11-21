"""2B.7 save-decision routing, not private graph persistence or authorization.

Signatures, saves and ownership gates are test doubles; SQLite only backs a
sentinel transaction. Canonical comparison coverage lives in test_statblock_fingerprints.
"""
import asyncio
import copy
import sqlite3
import unittest
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, call, patch
from python import scrying_glass_database_transactions as tx
from python import scrying_glass_statblock_changes as changes
from python.scrying_glass_statblock_loading import PrivateEncounterState


class TransactionDetectionTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:'); self.addCleanup(self.db.close)
        self.db.execute('CREATE TABLE sentinel(value INTEGER)'); self.db.commit()
        self.c = SimpleNamespace(
            STATE=PrivateEncounterState({'monsters':[{'id':'m','hp':7}]}, {'m':{'value':1}}),
            STORAGE=SimpleNamespace(transaction=lambda:self.db), active_campaign=lambda:'campaign',
            features=SimpleNamespace(reconcile=Mock(), after_transaction=Mock()), broadcast=AsyncMock())
        self.c.broadcast.side_effect = lambda: self.assertFalse(self.db.in_transaction)
        self.saves = Mock()
        for label, name in (('characters','save_active_campaign_characters'),
                            ('setup','save_active_setup_monsters'), ('runtime','save_state')):
            method = Mock(); setattr(self.c, name, method); self.saves.attach_mock(method, label)
        self.before = copy.deepcopy(self.c.STATE)
        def signature(state):
            self.c.features.reconcile.assert_called_once_with()
            return copy.deepcopy(getattr(state, '_statblocks', {}))
        for target, name, kwargs in (
            (changes,'private_signature',dict(side_effect=signature)),
            (changes,'state_changed',dict(wraps=changes.state_changed)),
            (tx,'ownership_request',dict(return_value=nullcontext())),
            (tx,'actor',dict(return_value=None)),
            (tx,'validate_initiative_request',{}), (tx,'validate_initiative_transition',{})):
            patcher = patch.object(target, name, **kwargs)
            value = patcher.start(); self.addCleanup(patcher.stop)
            if name == 'private_signature': self.signature = value
            if name == 'state_changed': self.compare = value

    def invoke(self, *, tracker=False, private=False):
        async def change():
            if tracker: self.c.STATE['monsters'][0]['hp'] = 5
            if private: self.c.STATE._statblocks['m']['value'] = 2
            if tracker or private:
                self.db.execute('INSERT INTO sentinel VALUES(1)')
                self.c._database_broadcast_pending = True
            return {'ok':True}
        return asyncio.run(tx.transactional_handler(self.c, change)())

    def assert_saved(self):
        self.assertEqual(self.saves.mock_calls, [call.characters(),call.setup(),call.runtime()])
        self.compare.assert_called_once()
        self.c.features.after_transaction.assert_called_once()
        self.c.broadcast.assert_awaited_once_with()
        self.assertFalse(self.db.in_transaction)
        self.assertEqual(self.db.execute('SELECT count(*) FROM sentinel').fetchone()[0], 1)

    def assert_rolled_back(self):
        self.assertEqual(self.c.STATE, self.before)
        self.assertEqual(self.c.STATE._statblocks, self.before._statblocks)
        self.assertEqual(self.db.execute('SELECT count(*) FROM sentinel').fetchone()[0], 0)
        self.c.features.after_transaction.assert_not_called()
        self.c.broadcast.assert_not_awaited()
        self.assertFalse(self.c._defer_database_broadcast)
        self.assertFalse(self.c._database_broadcast_pending)
        self.assertFalse(self.db.in_transaction)

    def test_unchanged_state_does_not_save(self):
        self.assertEqual(self.invoke(), {'ok':True})
        self.saves.assert_not_called(); self.assertEqual(self.saves.mock_calls, [])
        self.compare.assert_called_once()
        self.c.features.after_transaction.assert_called_once()
        self.c.broadcast.assert_not_awaited()

    def test_tracker_only_change_keeps_existing_save_order(self):
        self.invoke(tracker=True); self.assert_saved()
        self.assertEqual(self.c.STATE._statblocks, self.before._statblocks)

    def test_private_only_change_reaches_save_branch_despite_dict_equality(self):
        self.invoke(private=True); self.assert_saved()
        self.assertEqual(dict(self.c.STATE), dict(self.before))
        self.assertNotEqual(self.c.STATE._statblocks, self.before._statblocks)
        original, current = self.compare.call_args.args
        self.assertEqual(original._statblocks, self.before._statblocks)
        self.assertEqual(current._statblocks['m']['value'], 2)

    def test_combined_change_saves_once(self):
        self.invoke(tracker=True, private=True); self.assert_saved()
        self.assertNotEqual(dict(self.c.STATE), dict(self.before))
        self.assertNotEqual(self.c.STATE._statblocks, self.before._statblocks)

    def test_save_failure_rolls_back_memory_and_sentinel_without_broadcast(self):
        self.c.save_state.side_effect = OSError('injected save failure')
        with self.assertRaisesRegex(OSError, 'injected'): self.invoke(private=True)
        self.assert_rolled_back()

    def test_comparison_failure_rolls_back_before_any_save(self):
        self.signature.side_effect = ValueError('injected comparison failure')
        with self.assertRaisesRegex(ValueError, 'injected'): self.invoke(private=True)
        self.assertEqual(self.saves.mock_calls, []); self.assert_rolled_back()


if __name__ == '__main__': unittest.main()
