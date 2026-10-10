"""Import JSON must not silently overwrite duplicate object keys."""
import asyncio
import copy
import io
import json
import unittest
import zipfile
import test_bughunt_round21 as fixture
import test_encounter_features as feature_fixture
from test_sqlite_storage import HTTPError

class DuplicateImportJsonTests(unittest.TestCase):
    setUp=fixture.BoundedCombatantImportTests.setUp
    tearDown=fixture.BoundedCombatantImportTests.tearDown
    monster=fixture.BoundedCombatantImportTests.monster
    call=feature_fixture.FeatureTests.call

    def parse_rejected(self,raw):
        self.monster(raw)
        with self.assertRaises(HTTPError) as error:self.c.parse_monster(raw)
        self.assertEqual(error.exception.status_code,400)
        self.assertIn('duplicate',error.exception.detail.lower())

    def test_monster_duplicate_hp_is_rejected(self):
        self.parse_rejected(b'{"name":"Goblin","type":"goblin","ac":12,"hp":10,"hp":20}')

    def test_monster_escaped_duplicate_name_is_rejected(self):
        self.parse_rejected(rb'{"name":"Goblin","\u006eame":"Orc","type":"goblin","ac":12,"hp":10}')

    def bundle(self,make_manifest):
        with zipfile.ZipFile(io.BytesIO(self.f.export_bundle())) as archive:
            members={name:archive.read(name) for name in archive.namelist()}
        data=json.loads(members['campaign.json'])
        members['campaign.json']=make_manifest(data).encode()
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,value in members.items():archive.writestr(name,value)
        return out.getvalue()

    def reject_bundle(self,make_manifest):
        before=copy.deepcopy(self.c.STATE);campaigns=self.c.read_campaigns();revision=self.f.store.revision()
        with self.assertRaises(HTTPError) as error:self.call('import_bundle',self.bundle(make_manifest))
        self.assertEqual(error.exception.status_code,422)
        self.assertIn('duplicate',error.exception.detail.lower())
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.c.read_campaigns(),campaigns)
        self.assertEqual(self.f.store.revision(),revision)
        self.assertEqual(list(self.c.UPLOAD_DIR.iterdir()),[])

    def test_bundle_duplicate_top_level_key_is_rejected(self):
        def manifest(data):return json.dumps(data)[:-1]+',"campaign":'+json.dumps(data['campaign'])+'}'
        self.reject_bundle(manifest)

    def test_bundle_duplicate_setup_name_is_rejected(self):
        def manifest(data):
            setup=data['setups']['default'];second=copy.deepcopy(setup)
            second['monsters'][0]['name']='Overwriting monster'
            other={key:value for key,value in data.items() if key!='setups'}
            setups='{"default":'+json.dumps(setup)+',"default":'+json.dumps(second)+'}'
            return json.dumps(other)[:-1]+',"setups":'+setups+'}'
        self.reject_bundle(manifest)

    def test_bundle_nested_duplicate_metadata_is_rejected(self):
        def manifest(data):
            other={key:value for key,value in data.items() if key!='campaign'}
            return json.dumps(other)[:-1]+',"campaign":{"name":"First","name":"Second","description":""}}'
        self.reject_bundle(manifest)

    def test_actual_monster_import_duplicate_is_atomic_before_lookup(self):
        raw=b'{"name":"Goblin","type":"goblin","ac":12,"hp":10,"hp":20}'
        upload,call=self.monster(raw);before=copy.deepcopy(self.c.STATE);lookups=[]
        self.c.dnd_image=lambda species:lookups.append(species)
        with self.assertRaises(HTTPError) as error:asyncio.run(call())
        self.assertEqual(error.exception.status_code,400)
        self.assertEqual(self.c.STATE,before);self.assertEqual(lookups,[])

    def test_repeated_array_values_and_key_words_in_strings_are_valid(self):
        raw=b'{"name":"name name","type":"goblin","ac":12,"hp":10,"tags":["hp","hp"]}'
        self.monster(raw)
        self.assertEqual(self.c.parse_monster(raw)['name'],'name name')

    def test_normal_bundle_remains_additive(self):
        active=self.c.active_campaign()
        result=self.call('import_bundle',self.f.export_bundle())
        self.assertNotEqual(result['campaign_id'],active)
        self.assertEqual(self.c.active_campaign(),active)

if __name__=='__main__':unittest.main()
