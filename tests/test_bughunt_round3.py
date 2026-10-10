"""Round-three upload rollback and bundle integer-bound regressions."""
import ast
import asyncio
import copy
import io
import json
import types
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
import test_encounter_features as fixture
from test_sqlite_storage import HTTPError
from python.scrying_glass_database_transactions import transactional_handler


def load_class(filename, name):
    path = Path(__file__).resolve().parents[1]/'python'/filename
    tree = ast.parse(path.read_text())
    cls = next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==name)
    scope = dict(Form=lambda *args,**kwargs:None, File=lambda *args,**kwargs:None)
    future = ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),str(path),'exec'),scope)
    return scope[name]


class ThirdBugHuntTests(unittest.TestCase):
    setUp = fixture.FeatureTests.setUp
    tearDown = fixture.FeatureTests.tearDown
    call = fixture.FeatureTests.call
    item = fixture.FeatureTests.item

    def image_service(self):
        cls = load_class('scrying_glass_service_images.py','ImagesService')
        self.c.Path = Path
        service = cls(self.c)
        self.c.save_image = service.save_image
        return service

    def upload(self):
        return types.SimpleNamespace(filename='test.png',size=None,file=io.BytesIO(b'image fixture'))

    def background_handler(self):
        cls = load_class('scrying_glass_admin_display.py','AdminDisplayMixin')
        handler = cls();handler.context=self.c
        return handler.upload_display_background_image

    def test_failed_background_update_removes_uploaded_file(self):
        self.image_service()
        before = copy.deepcopy(self.c.STATE)
        with patch.object(self.c,'save_state',side_effect=RuntimeError('forced persistence failure')):
            with self.assertRaises(RuntimeError):
                asyncio.run(transactional_handler(self.c,self.background_handler())(self.upload()))
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(list(self.c.UPLOAD_DIR.iterdir()),[])

    def test_cancelled_upload_transaction_removes_file(self):
        service = self.image_service()
        async def cancelled():
            service.save_image(self.upload())
            raise asyncio.CancelledError()
        with self.assertRaises(asyncio.CancelledError):
            asyncio.run(transactional_handler(self.c,cancelled)())
        self.assertEqual(list(self.c.UPLOAD_DIR.iterdir()),[])

    def test_standalone_image_upload_keeps_file(self):
        service = self.image_service()
        url = service.save_image(self.upload())
        self.assertEqual((self.c.UPLOAD_DIR/url.split('/')[-1]).read_bytes(),b'image fixture')

    def test_successful_background_update_keeps_file(self):
        self.image_service()
        result = asyncio.run(transactional_handler(self.c,self.background_handler())(self.upload()))
        path = self.c.UPLOAD_DIR/result['image_url'].split('/')[-1]
        self.assertEqual(path.read_bytes(),b'image fixture')
        self.assertIn(result['image_url'],self.c.STATE['display']['background'])
        self.assertEqual(self.c._bundle_files,[])

    def test_existing_media_survives_failed_replacement(self):
        service = self.image_service()
        original = self.c.UPLOAD_DIR/'original.png'
        original.write_bytes(b'original')
        async def failed():
            service.save_image(self.upload())
            raise RuntimeError('abort')
        with self.assertRaises(RuntimeError):
            asyncio.run(transactional_handler(self.c,failed)())
        self.assertEqual(list(self.c.UPLOAD_DIR.iterdir()),[original])
        self.assertEqual(original.read_bytes(),b'original')

    def bundle(self, mutate):
        raw = self.f.export_bundle()
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            members = {name:archive.read(name) for name in archive.namelist()}
        payload = json.loads(members['campaign.json'])
        mutate(payload)
        members['campaign.json']=json.dumps(payload).encode()
        output=io.BytesIO()
        with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,data in members.items():archive.writestr(name,data)
        return output.getvalue()

    def reject(self, raw):
        before = copy.deepcopy(self.c.STATE)
        campaigns = self.c.read_campaigns()
        revision = self.f.store.revision()
        with self.assertRaises(HTTPError) as raised:
            self.call('import_bundle',raw)
        self.assertEqual(raised.exception.status_code,422)
        self.assertEqual(self.c.read_campaigns(),campaigns)
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.f.store.revision(),revision)
        self.assertEqual(list(self.c.UPLOAD_DIR.iterdir()),[])

    def test_bundle_rejects_hp_above_storage_integer_range(self):
        raw = self.bundle(lambda p:p['characters'][0].update(hp=2**63,max_hp=2**63))
        self.reject(raw)

    def test_bundle_rejects_oversized_scalar_extension(self):
        raw = self.bundle(lambda p:p['characters'][0].update(extra_counter=2**63))
        self.reject(raw)

    def test_bundle_rejects_round_above_storage_integer_range(self):
        raw = self.bundle(lambda p:p['encounter'].update(battle_round=2**63))
        self.reject(raw)

    def test_bundle_rejects_log_amount_below_storage_integer_range(self):
        def mutate(p):
            p['encounter']['activity_log']=[{'id':'test-event','action':'damage','amount':-(2**63)-1}]
        self.reject(self.bundle(mutate))

    def test_bundle_accepts_signed_integer_boundaries(self):
        def mutate(p):
            p['characters'][0]['extra_counter']=2**63-1
            p['characters'][0]['extra_minimum']=-(2**63)
        result=self.call('import_bundle',self.bundle(mutate))
        character=self.c.STORAGE.load_characters(result['campaign_id'])[0]
        self.assertEqual(character['extra_counter'],2**63-1)
        self.assertEqual(character['extra_minimum'],-(2**63))

if __name__=='__main__':
    unittest.main()
