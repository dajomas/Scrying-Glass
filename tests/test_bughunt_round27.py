"""Import JSON must reject non-finite numbers before business processing."""
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

class NonFiniteImportNumberTests(unittest.TestCase):
    setUp=fixture.BoundedCombatantImportTests.setUp
    tearDown=fixture.BoundedCombatantImportTests.tearDown
    monster=fixture.BoundedCombatantImportTests.monster
    call=features.FeatureTests.call

    def monster_raw(self,value):
        return json.dumps({'name':'Goblin','type':'goblin','ac':12,'hp':10,'extra':value}).encode()

    def reject_monster(self,raw):
        self.monster(raw)
        with self.assertRaises(HTTPError) as error:self.c.parse_monster(raw)
        self.assertEqual(error.exception.status_code,400)
        self.assertIn('finite',error.exception.detail.lower())

    def test_monster_nan_in_ignored_field_is_rejected(self):self.reject_monster(self.monster_raw(float('nan')))
    def test_monster_infinities_in_array_are_rejected(self):
        self.reject_monster(self.monster_raw([float('inf'),float('-inf')]))
    def test_monster_exponent_overflow_is_rejected(self):
        self.reject_monster(b'{"name":"Goblin","type":"goblin","ac":12,"hp":10,"extra":1e999}')

    def bundle(self,mutate):
        with zipfile.ZipFile(io.BytesIO(self.f.export_bundle())) as archive:
            members={name:archive.read(name) for name in archive.namelist()}
        data=json.loads(members['campaign.json']);mutate(data)
        members['campaign.json']=json.dumps(data).encode()
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as archive:
            for name,value in members.items():archive.writestr(name,value)
        return out.getvalue()

    def reject_bundle(self,mutate):
        before=copy.deepcopy(self.c.STATE);campaigns=self.c.read_campaigns();revision=self.f.store.revision()
        with self.assertRaises(HTTPError) as error:self.call('import_bundle',self.bundle(mutate))
        self.assertEqual(error.exception.status_code,422)
        self.assertIn('finite',error.exception.detail.lower())
        self.assertEqual(self.c.STATE,before);self.assertEqual(self.c.read_campaigns(),campaigns)
        self.assertEqual(self.f.store.revision(),revision)

    def test_bundle_infinite_display_font_is_not_silently_defaulted(self):
        self.reject_bundle(lambda p:p['encounter']['display'].update(battle_order_font_size=float('inf')))
    def test_bundle_nan_in_ignored_nested_metadata_is_rejected(self):
        self.reject_bundle(lambda p:p.update(extra={'value':float('nan')}))

    def test_rejection_happens_before_campaign_record_creation(self):
        raw=self.bundle(lambda p:p.update(extra=float('inf')))
        with patch.object(self.c.STORAGE,'create_campaign',wraps=self.c.STORAGE.create_campaign) as create:
            with self.assertRaises(HTTPError):self.call('import_bundle',raw)
        self.assertEqual(create.call_count,0)

    def test_finite_numbers_and_nan_words_in_text_remain_valid(self):
        raw=self.monster_raw({'value':1.25,'text':'NaN and Infinity are words'})
        self.monster(raw)
        self.assertEqual(self.c.parse_monster(raw)['hp'],10)
        result=self.call('import_bundle',self.bundle(lambda p:p['campaign'].update(name='NaN and Infinity')))
        self.assertEqual(result['name'],'NaN and Infinity')

    def test_actual_monster_import_nonfinite_rejection_is_atomic(self):
        upload,call=self.monster(self.monster_raw(float('nan')))
        before=copy.deepcopy(self.c.STATE);lookups=[]
        self.c.dnd_image=lambda species:lookups.append(species)
        with self.assertRaises(HTTPError) as error:asyncio.run(call())
        self.assertEqual(error.exception.status_code,400)
        self.assertEqual(self.c.STATE,before);self.assertEqual(lookups,[])

if __name__=='__main__':unittest.main()
