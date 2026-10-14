"""Real SQLite persistence, migration and request-scope regression checks."""
import asyncio
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from python.scrying_glass_storage import SQLiteStorage
from python.scrying_glass_setup_lair import update_setup_lair
from test_sqlite_storage import context, HTTPError

class SetupHasLairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'db.sqlite3'
        self.db = SQLiteStorage(self.path)
        self.campaign = self.db.create_campaign('Test', '', 'now')

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def state(self, enabled=False):
        return {'monsters': [], 'characters': [], 'lairs': [], 'has_lair': enabled,
                'battle_order': [], 'activity_log': [], 'display': {}}

    def test_setup_values_are_independent_and_survive_restart(self):
        self.db.save_setup(self.campaign, 'yes', self.state(True))
        self.db.save_setup(self.campaign, 'no', self.state(False))
        self.db.close()
        self.db = SQLiteStorage(self.path)
        self.assertTrue(self.db.load_setup(self.campaign, 'yes')['has_lair'])
        self.assertFalse(self.db.load_setup(self.campaign, 'no')['has_lair'])
        self.assertEqual(self.db.connection.execute('PRAGMA user_version').fetchone()[0], 7)

    def test_explicit_false_does_not_delete_lair(self):
        state = self.state(False)
        state['lairs'] = [{'id': 'l', 'name': 'Lair', 'active': True, 'visible': True, 'in_turn': False, 'color': '#8064a2'}]
        self.db.save_setup(self.campaign, 'test', state)
        loaded = self.db.load_setup(self.campaign, 'test')
        self.assertFalse(loaded['has_lair'])
        self.assertEqual(loaded['lairs'][0]['id'], 'l')
        self.assertTrue(loaded['lairs'][0]['active'])

    def test_v6_upgrade_checks_existing_lairs_and_creates_backup(self):
        state = self.state(True)
        state['lairs'] = [{'id': 'l', 'name': 'Lair', 'color': '#8064a2'}]
        self.db.save_setup(self.campaign, 'yes', state)
        self.db.save_setup(self.campaign, 'no', self.state())
        self.db.connection.execute('ALTER TABLE encounters DROP COLUMN has_lair')
        self.db.connection.execute('PRAGMA user_version=6')
        self.db.close()
        self.db = SQLiteStorage(self.path)
        self.assertTrue(self.db.load_setup(self.campaign, 'yes')['has_lair'])
        self.assertFalse(self.db.load_setup(self.campaign, 'no')['has_lair'])
        self.assertIsNotNone(self.db.migration_backup)

    def test_non_boolean_storage_value_is_rejected(self):
        state = self.state(); state['has_lair'] = 'false'
        with self.assertRaises(ValueError):
            self.db.save_setup(self.campaign, 'bad', state)

    def test_normalization_defaults_and_explicit_false(self):
        c = context(Path(self.temp.name))
        try:
            self.assertFalse(c.normalize_state({})['has_lair'])
            lair = {'id': 'l', 'name': 'Lair', 'color': '#8064a2'}
            self.assertTrue(c.normalize_state({'lairs': [lair]})['has_lair'])
            self.assertFalse(c.normalize_state({'lairs': [lair], 'has_lair': False})['has_lair'])
            with self.assertRaises(ValueError): c.normalize_state({'has_lair': 1})
        finally: c.STORAGE.close()

    def handler_context(self):
        return SimpleNamespace(STATE={'active_setup': {'campaign_id': '1', 'name': 'test'}, 'lairs': [{'id': 'l', 'active': True}]},
            active_campaign=lambda: '1', HTTPException=HTTPError,
            save_active_setup_monsters=Mock(), changed=AsyncMock())

    def test_handler_persists_without_mutating_lair(self):
        c = self.handler_context()
        body = {'has_lair': False, 'scope': {'campaign_id': '1', 'setup': c.STATE['active_setup']}}
        self.assertEqual(asyncio.run(update_setup_lair(c, body)), {'has_lair': False})
        c.save_active_setup_monsters.assert_called_once()
        c.changed.assert_awaited_once()
        self.assertTrue(c.STATE['lairs'][0]['active'])

    def test_stale_scope_is_rejected(self):
        c = self.handler_context()
        with self.assertRaises(HTTPError) as error:
            asyncio.run(update_setup_lair(c, {'has_lair': True, 'scope': {'campaign_id': '2', 'setup': None}}))
        self.assertEqual(error.exception.status_code, 409)
        c.save_active_setup_monsters.assert_not_called()
        self.assertNotIn('has_lair', c.STATE)

    def test_invalid_payload_is_rejected(self):
        c = self.handler_context()
        with self.assertRaises(HTTPError) as error:
            asyncio.run(update_setup_lair(c, {'has_lair': 'false', 'scope': {}}))
        self.assertEqual(error.exception.status_code, 422)

if __name__ == '__main__': unittest.main()
