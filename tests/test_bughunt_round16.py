"""CSS background URL queries are opaque during bundle media handling."""
import io
import re
import unittest
import zipfile
import test_encounter_features as fixture

class BackgroundMediaUrlTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown
    call=fixture.FeatureTests.call

    def background(self,value,files=None):
        for name,data in (files or {}).items():(self.c.UPLOAD_DIR/name).write_bytes(data)
        self.c.STATE['display']['background']=value
        self.c.save_active_setup_monsters()
        return self.f.export_bundle()

    def imported(self,raw):
        result=self.call('import_bundle',raw)
        return self.c.STORAGE.load_setup(result['campaign_id'],'default')['display']['background']

    def test_local_background_query_does_not_add_phantom_dependency(self):
        value='url("/media/bg.png?fallback=/media/missing.png") center / cover'
        raw=self.background(value,{'bg.png':b'background fixture'})
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            self.assertEqual(set(archive.namelist()),{'campaign.json','media/bg.png'})
        result=self.imported(raw)
        self.assertIn('?fallback=/media/missing.png',result)
        self.assertNotIn('url("/media/bg.png?',result)
        name=re.search(r'/media/([0-9a-f]+\.png)',result).group(1)
        self.assertEqual((self.c.UPLOAD_DIR/name).read_bytes(),b'background fixture')

    def test_external_background_query_does_not_reference_local_file(self):
        value="url('https://example.invalid/bg.png?fallback=/media/missing.png')"
        raw=self.background(value)
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:self.assertEqual(archive.namelist(),['campaign.json'])
        self.assertEqual(self.imported(raw),value)

    def test_layered_quoted_and_unquoted_urls_keep_suffixes_and_css(self):
        value="URL('/media/a.png?v=2'), url( /media/b.png#layer ) center / cover"
        raw=self.background(value,{'a.png':b'a fixture','b.png':b'b fixture'})
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            self.assertEqual(set(archive.namelist()),{'campaign.json','media/a.png','media/b.png'})
        result=self.imported(raw)
        self.assertTrue(result.startswith("URL('/media/"))
        self.assertIn("?v=2'), url( /media/",result)
        self.assertTrue(result.endswith('#layer ) center / cover'))
        names=re.findall(r'/media/([0-9a-f]+\.png)',result)
        self.assertEqual([(self.c.UPLOAD_DIR/name).read_bytes() for name in names],[b'a fixture',b'b fixture'])

    def test_bare_local_background_reference_remains_supported(self):
        raw=self.background('/media/bg.png?v=2',{'bg.png':b'fixture'})
        result=self.imported(raw)
        self.assertNotEqual(result,'/media/bg.png?v=2')
        self.assertTrue(result.endswith('?v=2'))

    def test_css_comment_media_text_is_not_a_dependency(self):
        value='linear-gradient(#000,#111) /* /media/missing.png */'
        raw=self.background(value)
        self.assertEqual(self.imported(raw),value)

    def test_comment_markers_inside_url_query_remain_opaque(self):
        value='url("/media/bg.png?note=/*text*/&fallback=/media/missing.png")'
        raw=self.background(value,{'bg.png':b'fixture'})
        result=self.imported(raw)
        self.assertIn('?note=/*text*/&fallback=/media/missing.png',result)

    def test_unterminated_url_text_is_preserved(self):
        value='url('+(' '*4096)
        raw=self.background(value)
        self.assertEqual(self.imported(raw),value.rstrip())

    def test_commented_url_is_not_a_dependency(self):
        value="/* url('/media/missing.png') */ linear-gradient(#000,#111)"
        raw=self.background(value)
        self.assertEqual(self.imported(raw),value)

if __name__=='__main__':unittest.main()
