"""Bundle media references retain URL suffixes and reject empty files."""
import copy
import io
import json
import unittest
import zipfile
import test_encounter_features as fixture
from test_sqlite_storage import HTTPError

class BundleMediaPortabilityTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown
    call=fixture.FeatureTests.call

    def media(self,suffix='',data=b'image fixture'):
        path=self.c.UPLOAD_DIR/'portrait.png';path.write_bytes(data)
        url='/media/portrait.png'+suffix
        self.c.entity('m')['image_url']=url
        self.c.save_active_setup_monsters()
        return url

    def roundtrip(self,suffix):
        original=self.media(suffix)
        raw=self.f.export_bundle()
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            self.assertIn('media/portrait.png',archive.namelist())
            self.assertEqual(archive.read('media/portrait.png'),b'image fixture')
        result=self.call('import_bundle',raw)
        monster=self.c.STORAGE.load_setup(result['campaign_id'],'default')['monsters'][0]
        url=monster['image_url']
        self.assertNotEqual(url,original)
        self.assertTrue(url.endswith(suffix))
        filename=url.split('#',1)[0].split('?',1)[0].split('/')[-1]
        self.assertEqual((self.c.UPLOAD_DIR/filename).read_bytes(),b'image fixture')

    def test_image_query_suffix_is_packed_and_rewritten(self):self.roundtrip('?v=2')
    def test_image_fragment_is_packed_and_rewritten(self):self.roundtrip('#portrait')
    def test_query_media_text_is_not_a_second_dependency(self):
        self.roundtrip('?fallback=/media/not-a-file.png')

    def test_external_url_with_suffix_is_not_treated_as_local_media(self):
        url='https://example.invalid/media/portrait.png?v=2'
        self.c.entity('m')['image_url']=url;self.c.save_active_setup_monsters()
        raw=self.f.export_bundle()
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:self.assertEqual(archive.namelist(),['campaign.json'])
        result=self.call('import_bundle',raw)
        monster=self.c.STORAGE.load_setup(result['campaign_id'],'default')['monsters'][0]
        self.assertEqual(monster['image_url'],url)

    def test_empty_media_import_is_rejected_atomically(self):
        self.media()
        with zipfile.ZipFile(io.BytesIO(self.f.export_bundle())) as archive:
            members={name:archive.read(name) for name in archive.namelist()}
        members['media/portrait.png']=b''
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,data in members.items():archive.writestr(name,data)
        before=self.c.read_campaigns();state=copy.deepcopy(self.c.STATE);files=set(self.c.UPLOAD_DIR.iterdir())
        revision=self.f.store.revision()
        with self.assertRaises(HTTPError) as error:self.call('import_bundle',out.getvalue())
        self.assertEqual(error.exception.status_code,422)
        self.assertEqual(self.c.read_campaigns(),before)
        self.assertEqual(self.c.STATE,state)
        self.assertEqual(self.f.store.revision(),revision)
        self.assertEqual(set(self.c.UPLOAD_DIR.iterdir()),files)

    def test_export_rejects_empty_referenced_media(self):
        self.media(data=b'')
        with self.assertRaises(HTTPError) as error:self.f.export_bundle()
        self.assertEqual(error.exception.status_code,409)

if __name__=='__main__':unittest.main()
