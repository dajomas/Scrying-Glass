"""Campaign-bundle name normalization regressions for source 9991101."""
import io
import json
import unittest
import zipfile
import test_encounter_features as fixture
from test_sqlite_storage import HTTPError

class BundleNameTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown
    call=fixture.FeatureTests.call

    def bundle(self,name):
        with zipfile.ZipFile(io.BytesIO(self.f.export_bundle())) as archive:
            members={key:archive.read(key) for key in archive.namelist()}
        payload=json.loads(members['campaign.json'])
        payload['campaign']['name']=name
        members['campaign.json']=json.dumps(payload).encode()
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
            for key,data in members.items():archive.writestr(key,data)
        return out.getvalue()

    def test_whitespace_only_name_rejected_atomically(self):
        before=self.c.read_campaigns()
        for name in ('   ','\t\n','\u2003'):
            with self.subTest(name=repr(name)):
                with self.assertRaises(HTTPError) as raised:
                    self.call('import_bundle',self.bundle(name))
                self.assertEqual(raised.exception.status_code,422)
                self.assertEqual(self.c.read_campaigns(),before)
                self.assertEqual(list(self.c.UPLOAD_DIR.iterdir()),[])

    def test_imported_name_is_trimmed(self):
        result=self.call('import_bundle',self.bundle('  New campaign  '))
        self.assertEqual(result['name'],'New campaign')
        self.assertEqual(self.c.read_campaigns()['campaigns'][result['campaign_id']]['name'],'New campaign')

    def test_trimmed_name_collision_gets_import_suffix(self):
        name=self.c.read_campaigns()['campaigns'][self.c.active_campaign()]['name']
        result=self.call('import_bundle',self.bundle(' '+name+' '))
        self.assertEqual(result['name'],name+' (import 2)')

    def test_regular_name_still_imports_without_activation(self):
        active=self.c.active_campaign()
        result=self.call('import_bundle',self.bundle('Normal campaign'))
        self.assertEqual(result['name'],'Normal campaign')
        self.assertEqual(self.c.active_campaign(),active)

if __name__=='__main__':unittest.main()
