"""2C.3a native new-destination Save As tests; no handler integration yet."""
import copy
import unittest
from unittest.mock import patch
import test_statblock_encounters as fixtures
from test_statblock_clone_kernel import reference_snapshot
from python.scrying_glass_statblock_encounters import PRIVATE_KEY
from python.scrying_glass_statblock_loading import PrivateEncounterState
from python.scrying_glass_statblock_storage import StatblockStorage
from python.scrying_glass_statblock_save_as import save_new_setup


class NewSetupSaveAsTests(unittest.TestCase):
    setUp = fixtures.EncounterAdapterTests.setUp

    def image(self, label='Live source'):
        state = self.api.load(self.encounter)
        state[PRIVATE_KEY]['m'] = reference_snapshot(label)
        saved = self.api.save(self.encounter,state)
        metadata = saved.pop(PRIVATE_KEY)
        return PrivateEncounterState(saved,metadata)

    def owner(self, name):
        return self.storage.connection.execute('SELECT encounter_id FROM battle_setups WHERE campaign_id=? AND name=?',(self.campaign,name)).fetchone()[0]

    def dump(self):
        return '\n'.join(self.storage.connection.iterdump())

    def test_live_projection_gets_independent_rows_fresh_metadata_and_no_source_write(self):
        self.image('First'); image = self.image('Latest')
        source = copy.deepcopy(self.api.load(self.encounter)); before = copy.deepcopy(image)
        image['monsters'][0]['hp'] = 1
        image._statblocks['m'].pop('content_digest',None)
        image._statblocks['m']['source_label'] = 'Unsaved private edit'
        candidate = copy.deepcopy(image)
        result = save_new_setup(self.storage,self.campaign,'saved-as',image,updated_at=1234.5)
        owner = self.owner('saved-as'); loaded = self.api.load(owner)
        self.assertNotEqual(owner,self.encounter); self.assertEqual(loaded['monsters'][0]['hp'],1)
        self.assertEqual(result,loaded[PRIVATE_KEY]); self.assertEqual(result['m']['revision'],1)
        self.assertEqual(result['m']['source_label'],'Unsaved private edit')
        self.assertNotEqual(result['m']['prepared_at'],before._statblocks['m']['prepared_at'])
        for key in ('definitions','nodes','facts','warnings','provenance'):
            self.assertEqual(result['m'][key],before._statblocks['m'][key])
        source_id = self.storage.connection.execute('SELECT id FROM monsters WHERE encounter_id=?',(self.encounter,)).fetchone()[0]
        destination_id = self.storage.connection.execute('SELECT id FROM monsters WHERE encounter_id=?',(owner,)).fetchone()[0]
        self.assertNotEqual(source_id,destination_id)
        self.assertEqual(self.api.load(self.encounter),source)
        self.assertEqual(dict(image),dict(candidate)); self.assertEqual(image._statblocks,candidate._statblocks)
        self.assertEqual(self.storage.connection.execute('SELECT updated_at FROM battle_setups WHERE encounter_id=?',(owner,)).fetchone()[0],1234.5)
        result['m']['source_label'] = 'Returned map changed'
        self.assertEqual(self.api.load(owner)[PRIVATE_KEY]['m']['source_label'],'Unsaved private edit')

    def test_existing_destination_rejects_without_overwriting_anything(self):
        image = self.image(); before = self.dump()
        with self.assertRaises(FileExistsError): save_new_setup(self.storage,self.campaign,'one',image)
        self.assertEqual(self.dump(),before)

    def test_failure_after_private_write_rolls_back_new_tracker_and_graph(self):
        image = self.image(); before = self.dump(); save = StatblockStorage.save; observed = []
        def fail_after_save(writer,*args,**kwargs):
            result = save(writer,*args,**kwargs); observed.append(result['revision'])
            raise OSError('injected after private Save As write')
        with patch.object(StatblockStorage,'save',new=fail_after_save):
            with self.assertRaises(OSError): save_new_setup(self.storage,self.campaign,'failed',image)
        self.assertEqual(observed,[1]); self.assertEqual(self.dump(),before)
        self.assertFalse(self.storage.connection.in_transaction)

    def test_plain_empty_and_serialized_private_inputs_keep_authority_separate(self):
        image = self.image()
        for name, candidate in (('plain',dict(image)),('empty',PrivateEncounterState(dict(image),{}))):
            with self.subTest(name=name):
                self.assertEqual(save_new_setup(self.storage,self.campaign,name,candidate),{})
                self.assertEqual(self.api.load(self.owner(name))[PRIVATE_KEY],{})
        before = self.dump(); forged = dict(image); forged[PRIVATE_KEY] = image._statblocks
        with self.assertRaises(ValueError): save_new_setup(self.storage,self.campaign,'forged',forged)
        self.assertEqual(self.dump(),before)


if __name__ == '__main__': unittest.main()
