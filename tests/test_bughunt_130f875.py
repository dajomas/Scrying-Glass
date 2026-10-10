"""Focused campaign-bundle regressions for 130f875.
The production module is executed with only relative-import collaborators replaced
by fixtures. ZIP parsing, compression, corruption and media I/O are real.
Full storage, normalization, transactional wrappers and HTTP routing are not tested.
"""
import ast
import copy
import io
import json
import struct
import tempfile
import types
import unittest
import zipfile
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]/'python'/'scrying_glass_campaign_bundle.py'
tree=ast.parse(SOURCE.read_text())
tree.body=[n for n in tree.body if not(isinstance(n,ast.ImportFrom) and n.level)]
scope=dict(load_import_json=json.loads,validate_roster_setup_ids=lambda *args,**kwargs:None)
exec(compile(tree,str(SOURCE),'exec'),scope)
import_bundle=scope['import_bundle']

class HTTPError(Exception):
    def __init__(self,status_code,detail):self.status_code=status_code;self.detail=detail;super().__init__(detail)

def state(**values):
    item=dict(monsters=[],characters=[],display={},active_setup=None)
    item.update(values);return item

def payload(version=1):
    return dict(format='scrying-glass-campaign',version=version,campaign=dict(name='Imported',description=''),
                setups={'default':state()},characters=[],encounter=state())

class Store:
    def __init__(self):self.created=[];self.setups={};self.rosters={}
    def campaign_name_exists(self,name):return False
    def create_campaign(self,name,description,now):self.created.append((name,description));return 2
    def save_characters(self,campaign,characters):self.rosters[campaign]=copy.deepcopy(characters)
    def save_setup(self,campaign,key,data):self.setups[key]=copy.deepcopy(data)


def archive(data,compression=zipfile.ZIP_DEFLATED,media=None):
    output=io.BytesIO()
    with zipfile.ZipFile(output,'w',compression) as z:
        z.writestr('campaign.json',json.dumps(data))
        for name,contents in (media or {}).items():z.writestr('media/'+name,contents)
    return output.getvalue()


def corrupt_member(raw,name,lzma=False):
    value=bytearray(raw)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        info=z.getinfo(name);offset=info.header_offset
        name_length,extra_length=struct.unpack_from('<HH',raw,offset+26)
        start=offset+30+name_length+extra_length
        if lzma:
            value[start:start+info.compress_size]=bytes(info.compress_size)
        else:
            value[start]=6  # Reserved DEFLATE block type: deterministic zlib.error.
    return bytes(value)

class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=Store();self.checkpoints=[]
        self.context=types.SimpleNamespace(HTTPException=HTTPError,UPLOAD_DIR=Path(self.tmp.name),
            STORAGE=self.store,_bundle_files=[],setup_slug=lambda key:key,
            normalize_state=lambda value:state(**copy.deepcopy(value)),now_iso=lambda:'now',
            features=types.SimpleNamespace(store=types.SimpleNamespace(save_snapshot=self.snapshot)))
    def tearDown(self):self.tmp.cleanup()
    def snapshot(self,*args):self.checkpoints.append(args);return 3
    def invalid(self,raw):
        with self.assertRaises(HTTPError) as exc:import_bundle(self.context,raw)
        self.assertEqual(exc.exception.status_code,422)
        self.assertEqual(self.store.created,[]);self.assertEqual(self.checkpoints,[])
        self.assertEqual(list(self.context.UPLOAD_DIR.iterdir()),[])
    def test_corrupt_deflate_manifest(self):
        self.invalid(corrupt_member(archive(payload()),'campaign.json'))
    def test_corrupt_deflate_media(self):
        self.invalid(corrupt_member(archive(payload(),media={'a.png':b'image contents'}),'media/a.png'))
    @unittest.skipIf(zipfile.lzma is None,'LZMA support unavailable')
    def test_corrupt_lzma_manifest(self):
        self.invalid(corrupt_member(archive(payload(),zipfile.ZIP_LZMA),'campaign.json',lzma=True))
    @unittest.skipIf(zipfile.lzma is None,'LZMA support unavailable')
    def test_corrupt_lzma_media(self):
        self.invalid(corrupt_member(archive(payload(),zipfile.ZIP_LZMA,{'a.png':b'image contents'}),'media/a.png',lzma=True))
    def test_boolean_version_rejected(self):self.invalid(archive(payload(True)))
    def test_float_version_rejected(self):self.invalid(archive(payload(1.0)))
    def test_unknown_version_rejected(self):self.invalid(archive(payload(2)))
    def test_string_version_rejected(self):self.invalid(archive(payload('1')))
    def test_invalid_zip_rejected(self):self.invalid(b'not a ZIP archive')
    def test_traversal_rejected(self):
        self.invalid(archive(payload(),media={'../a.png':b'image'}))
    def test_missing_referenced_media_rejected(self):
        data=payload();data['setups']['default']['monsters']=[dict(id='m',image_url='/media/missing.png')]
        self.invalid(archive(data))
    def test_empty_media_rejected(self):self.invalid(archive(payload(),media={'a.png':b''}))
    def test_media_rewrite_and_roundtrip(self):
        data=payload();data['setups']['default']['monsters']=[dict(id='m',image_url='/media/a.png?x=1#anchor')]
        data['setups']['default']['display']={'background':'url("/media/a.png")'}
        result=import_bundle(self.context,archive(data,media={'a.png':b'image fixture'}))
        self.assertEqual(result['campaign_id'],'2')
        path=self.store.setups['default']['monsters'][0]['image_url']
        self.assertNotEqual(path,'/media/a.png?x=1#anchor');self.assertTrue(path.endswith('?x=1#anchor'))
        self.assertEqual((self.context.UPLOAD_DIR/path.split('/media/')[1].split('?')[0]).read_bytes(),b'image fixture')
        self.assertIn(path.split('?')[0],self.store.setups['default']['display']['background'])


def valid_compression_test(codec):
    def test(self):
        result=import_bundle(self.context,archive(payload(),codec))
        self.assertEqual(result['checkpoint_id'],3);self.assertEqual(len(self.store.created),1)
    return test
for label,codec,available in (
    ('stored',zipfile.ZIP_STORED,True),('deflated',zipfile.ZIP_DEFLATED,True),
    ('bzip2',zipfile.ZIP_BZIP2,zipfile.bz2 is not None),('lzma',zipfile.ZIP_LZMA,zipfile.lzma is not None)):
    test=valid_compression_test(codec)
    if not available:test=unittest.skip('Compression support unavailable')(test)
    setattr(BundleTests,'test_valid_'+label,test)

if __name__=='__main__':unittest.main()
