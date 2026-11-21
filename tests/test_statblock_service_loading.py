"""Private service loading with real SQLite storage and actual persistence methods."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_sqlite_storage import context
from test_statblock_encounters import snapshot
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage


class ServicePrivateLoadTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name); self.c = context(self.directory)
        self.addCleanup(lambda: self.c.STORAGE.close())
        self.c.import_legacy_storage(); self.campaign = self.c.active_campaign()

    def setup_content(self, label='Private setup'):
        db = self.c.STORAGE
        db.save_setup(self.campaign, 'one', {'monsters':[{'id':'m','hp':7,'active':True}]})
        encounter = db.connection.execute(
            "SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name='one'", (self.campaign,)).fetchone()[0]
        api = PrivateEncounterStorage(db); value = api.load(encounter)
        value[PRIVATE_KEY]['m'] = snapshot(label)
        return api.save(encounter, value)[PRIVATE_KEY]

    def runtime_content(self, *, reference=None):
        db = self.c.STORAGE
        db.set_value('runtime_state', {'monsters':[{'id':'m','hp':3,'active':True}], 'active_setup':reference})
        encounter = db.connection.execute('SELECT runtime_encounter_id FROM application_state').fetchone()[0]
        api = PrivateEncounterStorage(db); value = api.load(encounter)
        value[PRIVATE_KEY]['m'] = snapshot('Private runtime')
        return api.save(encounter, value, runtime=True)[PRIVATE_KEY]

    def test_setup_load_retains_metadata_without_serialized_private_fields(self):
        expected = self.setup_content('SECRET_STATBLOCK_CONTENT')
        result = self.c.load_setup_state('one', self.campaign)
        self.assertEqual(result._statblocks, expected)
        self.assertNotIn(PRIVATE_KEY, result)
        self.assertNotIn('SECRET_STATBLOCK_CONTENT', json.dumps(result))
        self.c.STATE = result
        self.assertNotIn('SECRET_STATBLOCK_CONTENT', json.dumps(self.c.public_state()))
        self.assertNotIn('SECRET_STATBLOCK_CONTENT', json.dumps(self.c.display_state()))
        clone = copy.deepcopy(result); clone._statblocks['m']['source_label'] = 'Changed'
        self.assertEqual(result._statblocks, expected)

    def test_saved_setup_empty_runtime_fallback_uses_setup_metadata(self):
        expected = self.setup_content()
        self.c.STATE = self.c.load_setup_state('one', self.campaign)
        self.c.set_active_setup(self.campaign, 'one'); self.c.save_state()
        self.assertEqual(self.c.STORAGE.get_value('runtime_state')['monsters'], [])
        self.c.STATE = {}; self.c.load_state()
        self.assertEqual(self.c.STATE._statblocks, expected)
        self.assertEqual(self.c.STATE['monsters'][0]['hp'], 7)

    def test_nonempty_runtime_keeps_runtime_content_not_setup_content(self):
        self.setup_content()
        expected = self.runtime_content(reference={'campaign_id':self.campaign,'name':'one'})
        self.c.load_state()
        self.assertEqual(self.c.STATE._statblocks, expected)
        self.assertEqual(self.c.STATE['monsters'][0]['hp'], 3)

    def test_unsaved_restart_and_subsequent_save_keep_stored_content(self):
        expected = self.runtime_content()
        self.c.STORAGE.close(); self.c = context(self.directory)
        self.c.load_state(); self.assertEqual(self.c.STATE._statblocks, expected)
        self.c.STATE['monsters'][0]['hp'] = 1; self.c.save_state()
        self.c.STATE = {}; self.c.load_state()
        self.assertEqual(self.c.STATE._statblocks, expected)
        self.assertEqual(self.c.STATE['monsters'][0]['hp'], 1)

    def test_lower_default_preparation_limits_do_not_block_stored_load(self):
        expected = self.setup_content('x' * 70000)
        loaded = self.c.load_setup_state('one', self.campaign)
        self.assertEqual(loaded._statblocks, expected)

    def test_failed_private_read_does_not_replace_live_state(self):
        self.runtime_content(); before = self.c.STATE
        with patch('python.scrying_glass_statblock_storage.StatblockStorage.load', side_effect=ValueError('injected')):
            with self.assertRaises(RuntimeError): self.c.load_state()
        self.assertIs(self.c.STATE, before)

    def test_loading_setup_for_import_does_not_change_live_metadata(self):
        self.setup_content(); self.runtime_content(); self.c.load_state()
        before = self.c.STATE; expected = copy.deepcopy(before._statblocks)
        source = self.c.load_setup_state('one', self.campaign)
        self.assertEqual(source._statblocks['m']['source_label'], 'Private setup')
        self.assertIs(self.c.STATE, before); self.assertEqual(before._statblocks, expected)


if __name__ == '__main__': unittest.main()
