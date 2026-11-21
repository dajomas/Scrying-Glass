"""3B bundle boundaries: native SQLite, actual ASGI installers and seeded sessions.
Recording sockets exercise production notifications, not network/browser delivery.
"""
import asyncio
import copy
import io
import json
import struct
import unittest
import warnings
import zipfile
from pathlib import Path
from unittest.mock import patch
import test_statblock_2b_boundaries as boundaries
import test_statblock_setup_importing as graphs
from python import scrying_glass_campaign_bundle as bundles
from python.scrying_glass_campaign_ownership import actor
from python.scrying_glass_campaign_viewers import viewers
from python.scrying_glass_database_transactions import operation_lock, transactional_handler
from python.scrying_glass_feature_storage import FeatureStorage
from python.scrying_glass_service_auth import AuthService
from python.scrying_glass_service_features import fingerprint
from python.scrying_glass_statblock_encounters import PRIVATE_KEY, PrivateEncounterStorage
from python.scrying_glass_statblock_loading import load_setup_private
from python.scrying_glass_statblock_model import canonical_bytes
from python.scrying_glass_statblock_restore import restore_bindings

MiB=1024*1024


def unpack(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        return json.loads(archive.read('campaign.json'))


def pack(payload, members=(), *, manifest_size=None, compression=zipfile.ZIP_DEFLATED):
    value=copy.deepcopy(payload)
    if manifest_size is not None:
        value['padding']=''
        size=len(json.dumps(value,separators=(',',':')).encode())
        if size>manifest_size: raise ValueError('Fixture manifest is already too large')
        value['padding']='x'*(manifest_size-size)
    manifest=json.dumps(value,separators=(',',':')).encode()
    if manifest_size is not None: assert len(manifest)==manifest_size
    out=io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter('ignore',UserWarning)
        with zipfile.ZipFile(out,'w',compression) as archive:
            archive.writestr('campaign.json',manifest)
            for name,data in members: archive.writestr(name,data)
    return out.getvalue()


class BundleFixture(boundaries.BoundaryFixture):
    secret='PRIVATE_3B_BUNDLE_BOUNDARY'

    def setUp(self):
        boundaries.BoundaryFixture.setUp(self)
        api=PrivateEncounterStorage(self.c.STORAGE); state=api.load(self.encounter())
        value=graphs.graph(self.secret)
        value['definitions'].append(dict(local_id='second',kind='spell',name='Second',source_key='fixture:second',position=1))
        next(node for node in value['nodes'] if node['kind']=='text')['text']='x'*128
        state[PRIVATE_KEY]['m']=value; api.save(self.encounter(),state); self.c.load_state()
        self.original_campaign=self.c.active_campaign(); self.original=copy.deepcopy(self.current_private())
        self.original_bindings=restore_bindings(self.c.STORAGE,self.encounter())
        self.checkpoint=self.f.store.save_snapshot(self.original_campaign,self.c.STATE,'checkpoint','Before bundle')
        self.undo=self.f.store.save_snapshot(self.original_campaign,self.c.STATE,'undo','Before bundle',fingerprint(self.c.STATE))
        self.raw=self.f.export_bundle(); self.payload=unpack(self.raw); self.sends.clear()

    def capture(self):
        return self.dump(),copy.deepcopy(self.c.STATE),{p.name:p.read_bytes() for p in self.c.UPLOAD_DIR.iterdir()}

    def unchanged(self,before):
        dump,state,files=before
        self.assert_unchanged(dump,state)
        self.assertEqual({p.name:p.read_bytes() for p in self.c.UPLOAD_DIR.iterdir()},files)
        self.assertEqual(self.c.active_campaign(),self.original_campaign)
        self.assertEqual(restore_bindings(self.c.STORAGE,self.encounter()),self.original_bindings)

    def run_import(self,raw):
        return asyncio.run(transactional_handler(self.c,self.f.import_bundle)(raw))

    def imported(self,result):
        campaign=result['campaign_id']
        state=load_setup_private(self.c.STORAGE,campaign,'default')
        image=self.f.store.load(result['checkpoint_id'],campaign,'checkpoint')
        self.assert_content(state._statblocks['m'],self.original['m'])
        self.assert_content(image._statblocks['m'],self.original['m'])
        self.assertEqual(state._statblocks['m']['revision'],1)
        self.assertEqual(image._statblocks['m']['revision'],1)
        self.assertEqual(self.stored(),self.original)
        return image

    def reject(self,raw,status=422):
        before=self.capture()
        with self.assertRaises(self.c.HTTPException) as raised: self.run_import(raw)
        self.assertEqual(raised.exception.status_code,status); self.unchanged(before)


class BundleNativeBoundaryTests(BundleFixture,unittest.TestCase):
    def test_real_manifest_limit_accepts_exactly_and_rejects_one_byte_over(self):
        self.imported(self.run_import(pack(self.payload,manifest_size=10*MiB)))
        self.reject(pack(self.payload,manifest_size=10*MiB+1))
        with zipfile.ZipFile(io.BytesIO(self.raw)) as archive: size=len(archive.read('campaign.json'))
        with patch.object(bundles,'MANIFEST_LIMIT',size): self.assertEqual(unpack(self.f.export_bundle())['version'],2)
        with patch.object(bundles,'MANIFEST_LIMIT',size-1):
            with self.assertRaises(self.c.HTTPException) as raised: self.f.export_bundle()
        self.assertEqual(raised.exception.status_code,413)

    def test_compressed_limit_accepts_valid_exact_size_and_rejects_one_byte_over(self):
        initial=pack(self.payload,[('media/pad.png',b'')],compression=zipfile.ZIP_STORED)
        raw=pack(self.payload,[('media/pad.png',b'x'*(25*MiB-len(initial)))],compression=zipfile.ZIP_STORED)
        self.assertEqual(len(raw),25*MiB)
        result=self.run_import(raw); self.imported(result)
        self.assertEqual(sum(p.stat().st_size for p in self.c.UPLOAD_DIR.iterdir()),25*MiB-len(initial))
        self.reject(raw+b'x',413)

    def test_member_count_includes_manifest_and_rejects_duplicate_and_unsafe_members(self):
        members=[('media/p%d.png'%i,b'x') for i in range(999)]
        self.imported(self.run_import(pack(self.payload,members)))
        self.assertEqual(len(list(self.c.UPLOAD_DIR.iterdir())),999)
        self.reject(pack(self.payload,members+[('media/overflow.png',b'x')]))
        for entries in ([('media/a.png',b'x'),('media/a.png',b'y')],
                        [('campaign.json',b'{}')],[('media/',b'')],
                        [('../escape.png',b'x')],[('/media/a.png',b'x')],
                        [('media/./a.png',b'x')],[('media/../a.png',b'x')],
                        [('media'+chr(92)+'a.png',b'x')],[('media/a.png',b'')],
                        [('media/a.exe',b'x')]):
            with self.subTest(entries=[name for name,_ in entries]): self.reject(pack(self.payload,entries))

    def test_expanded_metadata_limit_rejects_before_member_reads(self):
        raw=bytearray(pack(self.payload,[('media/bomb.png',b'x')]))
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            manifest_size=archive.getinfo('campaign.json').file_size
        cursor=0
        while True:
            cursor=raw.find(b'PK'+bytes([1,2]),cursor)
            self.assertGreaterEqual(cursor,0)
            length=struct.unpack_from('<H',raw,cursor+28)[0]
            name=bytes(raw[cursor+46:cursor+46+length])
            if name==b'media/bomb.png': break
            cursor+=46+length
        struct.pack_into('<I',raw,cursor+24,100*MiB-manifest_size+1)
        with patch.object(zipfile.ZipFile,'read',side_effect=AssertionError('oversized archive was read')):
            self.reject(bytes(raw))

    def test_actual_expanded_limit_accepts_exactly_and_rejects_one_byte_over(self):
        manifest_size=len(json.dumps(self.payload,separators=(',',':')).encode())
        raw=pack(self.payload,[('media/expanded.png',b'x'*(100*MiB-manifest_size))])
        self.assertLess(len(raw),25*MiB)
        self.imported(self.run_import(raw))
        self.assertEqual(sum(p.stat().st_size for p in self.c.UPLOAD_DIR.iterdir()),100*MiB-manifest_size)
        oversized=pack(self.payload,[('media/expanded.png',b'x'*(100*MiB-manifest_size+1))])
        self.reject(oversized)

    def test_all_operator_snapshot_budgets_accept_exact_and_reject_beyond(self):
        snapshot=self.payload['statblocks']['encounter']['m']
        limits={'snapshot_bytes':len(canonical_bytes(snapshot)),'content_nodes':len(snapshot['nodes']),
                'content_depth':2,'text_value_bytes':128,'supporting_definitions':2}
        for field,limit in limits.items():
            with self.subTest(field=field):
                self.c.CONFIG['statblocks']={'limits':{field:limit}}
                self.imported(self.run_import(self.raw))
                self.c.CONFIG['statblocks']={'limits':{field:limit-1}}
                self.assertEqual(self.stored(),self.original)
                self.assertEqual(unpack(self.f.export_bundle())['version'],2)
                self.reject(self.raw)
        self.c.CONFIG.pop('statblocks')

    def test_corrupt_graphs_credentials_and_false_authority_reject_atomically(self):
        for mutation in ('cycle','reference','credit-url','credentials','verified','duplicate-id'):
            value=copy.deepcopy(self.payload); graph=value['statblocks']['encounter']['m']
            graph.pop('content_digest',None)
            if mutation=='cycle': graph['nodes'][0]['parent_local_id']=graph['nodes'][0]['local_id']
            elif mutation=='reference':
                next(node for node in graph['nodes'] if node['kind']=='reference')['target_definition_local_id']='missing'
            elif mutation=='credit-url': graph['provenance'][0]['credits'][0]['license_url']='javascript:alert(1)'
            elif mutation=='credentials': graph['provenance'][0]['endpoint']='https://user:secret@example.org/data'
            elif mutation=='verified': graph['provenance'][0]['verified']=True
            else: value['encounter']['monsters'].append(copy.deepcopy(value['encounter']['monsters'][0]))
            with self.subTest(mutation=mutation): self.reject(pack(value))


if __name__=='__main__': unittest.main()
