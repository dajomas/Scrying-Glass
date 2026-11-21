"""Native 3A bundle roundtrip and rollback; HTTP/network coverage is separate."""
import asyncio
import copy
import io
import json
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
import test_statblock_stage2_contracts as base
from test_statblock_setup_importing import graph
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_statblock_detaching import detach_loaded_setup
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_loading import load_setup_private


def unpack(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as z: return json.loads(z.read('campaign.json'))


def pack(value):
    out=io.BytesIO()
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z: z.writestr('campaign.json',json.dumps(value))
    return out.getvalue()


class PrivateBundleTests(unittest.TestCase):
    setUp=base.StatblockStage2ContractTests.setUp
    tearDown=base.StatblockStage2ContractTests.tearDown
    encounter=base.StatblockStage2ContractTests.encounter
    stored=base.StatblockStage2ContractTests.stored
    seed=base.StatblockStage2ContractTests.seed
    call=base.StatblockStage2ContractTests.call
    assert_content=base.StatblockStage2ContractTests.assert_content

    def source(self):
        self.seed('Earlier'); api=PrivateEncounterStorage(self.c.STORAGE)
        state=api.load(self.encounter()); state[PRIVATE_KEY]['m']=graph('Portable private graph')
        saved=api.save(self.encounter(),state)[PRIVATE_KEY]['m']; self.c.load_state()
        return saved

    def capture(self):
        return (list(self.c.STORAGE.connection.iterdump()),copy.deepcopy(self.c.STATE),set(self.c.UPLOAD_DIR.iterdir()))

    def unchanged(self,before):
        dump,state,files=before
        self.assertEqual(list(self.c.STORAGE.connection.iterdump()),dump)
        self.assertEqual(dict(self.c.STATE),dict(state)); self.assertEqual(self.c.STATE._statblocks,state._statblocks)
        self.assertEqual(set(self.c.UPLOAD_DIR.iterdir()),files)
        self.assertFalse(self.c.STORAGE.connection.in_transaction)

    def test_roundtrip_setups_checkpoint_restore_source_isolation_and_privacy(self):
        original=self.source(); source=self.c.active_campaign(); raw=self.f.export_bundle()
        self.assertEqual(unpack(raw)['version'],2)
        result=self.call('import_bundle',raw); dest=result['campaign_id']
        self.assertEqual(self.c.active_campaign(),source)
        saved=load_setup_private(self.c.STORAGE,dest,'default')._statblocks['m']
        self.assert_content(saved,original); self.assertEqual(saved['revision'],1)
        self.assertNotEqual(self.encounter(dest),self.encounter(source))
        image=self.f.store.load(result['checkpoint_id'],dest,'checkpoint')
        self.assert_content(image._statblocks['m'],original); self.assertEqual(image._statblocks['m']['revision'],1)
        self.assertEqual(image['active_setup']['campaign_id'],dest)
        self.c.STORAGE.set_value('active_campaign',dest); self.c.STATE=copy.deepcopy(image)
        self.call('restore_checkpoint',result['checkpoint_id'],{'confirm':True,'revision':self.f.store.revision()})
        self.assert_content(self.stored(dest)['m'],original); self.assertEqual(self.stored(source)['m'],original)
        self.assertNotIn('Portable private graph',json.dumps(self.c.public_state()))
        self.assertNotIn('Private fixture credit',json.dumps(self.c.display_state()))
        self.c.load_state(); self.assert_content(self.c.STATE._statblocks['m'],original)
        self.assertEqual(list(self.c.STORAGE.connection.execute('PRAGMA foreign_key_check')),[])

    def test_runtime_private_content_is_separate_from_saved_setup(self):
        original=self.source()
        async def detach(): detach_loaded_setup(self.c)
        asyncio.run(transactional_handler(self.c,detach)())
        async def edit():
            value=self.c.STATE._statblocks['m']; value.pop('content_digest',None); value['source_label']='Runtime only'
        asyncio.run(transactional_handler(self.c,edit)())
        result=self.call('import_bundle',self.f.export_bundle()); dest=result['campaign_id']
        self.assert_content(load_setup_private(self.c.STORAGE,dest,'default')._statblocks['m'],original)
        image=self.f.store.load(result['checkpoint_id'],dest,'checkpoint')
        self.assertIsNone(image['active_setup']); self.assertEqual(image._statblocks['m']['source_label'],'Runtime only')
        self.assertEqual(image._statblocks['m']['revision'],1)

    def test_legacy_bundle_import_and_empty_export(self):
        self.assertEqual(unpack(self.f.export_bundle())['version'],1)
        self.source(); payload=unpack(self.f.export_bundle()); payload['version']=1; payload.pop('statblocks')
        result=self.call('import_bundle',pack(payload)); dest=result['campaign_id']
        self.assertEqual(load_setup_private(self.c.STORAGE,dest,'default')._statblocks,{})
        self.assertEqual(self.f.store.load(result['checkpoint_id'],dest,'checkpoint')._statblocks,{})

    def test_invalid_private_input_is_atomic(self):
        self.source(); payload=unpack(self.f.export_bundle()); cases=[]
        v=copy.deepcopy(payload); v['version']=3; cases.append(v)
        v=copy.deepcopy(payload); v['version']=1; cases.append(v)
        v=copy.deepcopy(payload); v['statblocks']['setups']['absent']={}; cases.append(v)
        v=copy.deepcopy(payload); v['statblocks']['encounter']['absent']=v['statblocks']['encounter'].pop('m'); cases.append(v)
        v=copy.deepcopy(payload); v['statblocks']['encounter']['m']['content_digest']='0'*64; cases.append(v)
        v=copy.deepcopy(payload); v['statblocks']['encounter']['m']['provenance'][0]['endpoint']='http://unsafe.invalid'; cases.append(v)
        v=copy.deepcopy(payload); v['encounter'][PRIVATE_KEY]={}; cases.append(v)
        before=self.capture()
        for index,value in enumerate(cases):
            with self.subTest(case=index):
                with self.assertRaises(self.c.HTTPException): self.call('import_bundle',pack(value))
                self.unchanged(before)

    def test_lowered_incoming_limit_preserves_export_and_stored_reads(self):
        original=self.source(); self.c.CONFIG['statblocks']={'limits':{'content_nodes':1}}
        raw=self.f.export_bundle(); self.assertEqual(self.stored()['m'],original); before=self.capture()
        with self.assertRaises(self.c.HTTPException): self.call('import_bundle',raw)
        self.unchanged(before)

    def test_aggregate_overflow_rejects_instead_of_dropping_private_content(self):
        self.source()
        with patch('python.scrying_glass_campaign_bundle.MANIFEST_LIMIT',64):
            with self.assertRaises(self.c.HTTPException) as raised: self.f.export_bundle()
        self.assertEqual(raised.exception.status_code,413)

    def test_late_private_database_failure_rolls_back(self):
        self.source(); raw=self.f.export_bundle(); before=self.capture()
        from python.scrying_glass_statblock_save_as import save_new_setup
        def fail(*args,**kwargs):
            save_new_setup(*args,**kwargs); raise OSError('after private setup write')
        with patch('python.scrying_glass_statblock_save_as.save_new_setup',side_effect=fail):
            with self.assertRaises(self.c.HTTPException): self.call('import_bundle',raw)
        self.unchanged(before)

    def test_partial_media_failure_cleans_files_and_database(self):
        self.source(); self.c.STATE['monsters'][0]['image_url']='/media/source.png'
        (self.c.UPLOAD_DIR/'source.png').write_bytes(b'fixture')
        raw=self.f.export_bundle(); before=self.capture(); write=Path.write_bytes
        def fail(path,data):
            write(path,data[:1]); raise OSError('partial media write')
        with patch.object(Path,'write_bytes',fail):
            with self.assertRaises(self.c.HTTPException): self.call('import_bundle',raw)
        self.unchanged(before)


if __name__=='__main__': unittest.main()
