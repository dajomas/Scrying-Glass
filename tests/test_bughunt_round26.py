"""Import JSON strings must be encodable as UTF-8 before later work."""
import asyncio
import copy
import io
import json
import unittest
import zipfile
from unittest.mock import patch
import test_bughunt_round21 as fixture
import test_encounter_features as features
from test_sqlite_storage import HTTPError

class ImportUnicodeTests(unittest.TestCase):
    setUp=fixture.BoundedCombatantImportTests.setUp
    tearDown=fixture.BoundedCombatantImportTests.tearDown
    monster=fixture.BoundedCombatantImportTests.monster
    call=features.FeatureTests.call

    def monster_raw(self,**changes):
        data={'name':'Goblin','type':'goblin','ac':12,'hp':10};data.update(changes)
        return json.dumps(data,ensure_ascii=True).encode()

    def rejected_monster(self,**changes):
        raw=self.monster_raw(**changes);self.monster(raw)
        with self.assertRaises(HTTPError) as error:self.c.parse_monster(raw)
        self.assertEqual(error.exception.status_code,400)
        self.assertIn('unicode',error.exception.detail.lower())

    def test_lone_high_surrogate_in_monster_name_is_rejected(self):self.rejected_monster(name=chr(0xD800))
    def test_lone_low_surrogate_in_monster_type_is_rejected(self):self.rejected_monster(type=chr(0xDC00))

    def test_actual_bad_unicode_monster_import_is_atomic_before_lookup(self):
        upload,call=self.monster(self.monster_raw(name=chr(0xD800)))
        before=copy.deepcopy(self.c.STATE);lookups=[]
        self.c.dnd_image=lambda species:lookups.append(species)
        with self.assertRaises(HTTPError) as error:asyncio.run(call())
        self.assertEqual(error.exception.status_code,400)
        self.assertEqual(self.c.STATE,before);self.assertEqual(lookups,[])

    def bundle(self,mutate):
        with zipfile.ZipFile(io.BytesIO(self.f.export_bundle())) as archive:
            members={name:archive.read(name) for name in archive.namelist()}
        data=json.loads(members['campaign.json']);mutate(data)
        members['campaign.json']=json.dumps(data,ensure_ascii=True).encode()
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,value in members.items():archive.writestr(name,value)
        return out.getvalue()

    def rejected_bundle(self,mutate):
        before=copy.deepcopy(self.c.STATE);campaigns=self.c.read_campaigns()
        with self.assertRaises(HTTPError) as error:self.call('import_bundle',self.bundle(mutate))
        self.assertEqual(error.exception.status_code,422)
        self.assertIn('unicode',error.exception.detail.lower())
        self.assertEqual(self.c.STATE,before);self.assertEqual(self.c.read_campaigns(),campaigns)
        self.assertEqual(list(self.c.UPLOAD_DIR.iterdir()),[])

    def test_invalid_unicode_nested_text_is_rejected(self):
        self.rejected_bundle(lambda p:p.update(extra={'text':chr(0xD800)}))

    def test_invalid_unicode_object_key_is_rejected(self):
        self.rejected_bundle(lambda p:p.update({chr(0xD800):'unused'}))

    def test_bad_campaign_name_rejected_before_record_creation(self):
        raw=self.bundle(lambda p:p['campaign'].update(name=chr(0xD800)))
        with patch.object(self.c.STORAGE,'create_campaign',wraps=self.c.STORAGE.create_campaign) as create:
            with self.assertRaises(HTTPError) as error:self.call('import_bundle',raw)
        self.assertEqual(error.exception.status_code,422)
        self.assertEqual(create.call_count,0)

    def test_valid_surrogate_pair_decodes_to_emoji(self):
        raw=self.monster_raw(name=chr(0x1F600))
        self.assertIn(b'\\ud83d\\ude00',raw)
        self.monster(raw)
        self.assertEqual(self.c.parse_monster(raw)['name'],chr(0x1F600))

    def test_valid_unicode_campaign_text_remains_supported(self):
        result=self.call('import_bundle',self.bundle(lambda p:p['campaign'].update(name='蘭 🌙',description='Café')))
        campaign=self.c.read_campaigns()['campaigns'][result['campaign_id']]
        self.assertEqual(campaign['name'],'蘭 🌙');self.assertEqual(campaign['description'],'Café')

if __name__=='__main__':unittest.main()
