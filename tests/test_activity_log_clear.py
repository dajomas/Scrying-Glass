"""Clear activity log: persistence, other-setup isolation, background separation and rollback.

Real SQLite through the production transactional handler (formerly tests/audit_log_clear.py).
"""
import asyncio
import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from python.scrying_glass_admin_activity import AdminActivityMixin
from python.scrying_glass_database_transactions import transactional_handler
from test_sqlite_storage import Handlers, context


class ActivityLogClearTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.c = context(Path(directory.name))
        self.addCleanup(self.c.STORAGE.close)
        self.c.import_legacy_storage()
        self.campaign = self.c.active_campaign()
        self.c.STATE = self.c.normalize_state({'activity_log': [{'id': 'event', 'action': 'damage', 'amount': 2}],
                                               'display': {'background': '#123456'}})
        asyncio.run(transactional_handler(self.c, Handlers(self.c).save_setup)(
            payload=SimpleNamespace(name='fight', campaign=None)))
        self.other = copy.deepcopy(self.c.STORAGE.load_setup(self.campaign, 'fight'))
        self.c.STORAGE.save_setup(self.campaign, 'other', self.other)
        self.c.STATE['display']['background'] = '#abcdef'

    def clear(self):
        handler = transactional_handler(self.c, AdminActivityMixin.clear_activity_log)
        return asyncio.run(handler(SimpleNamespace(context=self.c)))

    def test_clear_persists_and_keeps_other_setups_and_background(self):
        result = self.clear()
        self.assertEqual(result['cleared'], 1)
        self.assertEqual(self.c.STATE['activity_log'], [])
        self.assertEqual(self.c.load_setup_state('fight', self.campaign)['activity_log'], [])
        self.assertEqual(self.c.STORAGE.load_setup(self.campaign, 'other')['activity_log'], self.other['activity_log'])
        self.assertEqual(self.c.STORAGE.load_setup(self.campaign, 'fight')['display']['background'], '#123456')
        self.assertEqual(self.c.STATE['display']['background'], '#abcdef')
        self.c.load_state()
        self.assertEqual(self.c.STATE['activity_log'], [])
        self.assertEqual(self.c.STATE['display']['background'], '#abcdef')

    def test_failed_save_rolls_back(self):
        self.clear()
        self.c.STATE['activity_log'] = [{'id': 'rollback', 'action': 'heal', 'amount': 1}]
        self.c.save_state()
        before = copy.deepcopy(self.c.STATE)
        with patch.object(self.c, 'save_state', side_effect=RuntimeError('injected save failure')):
            with self.assertRaises(RuntimeError):
                self.clear()
        self.assertEqual(self.c.STATE, before)


if __name__ == '__main__':
    unittest.main()
