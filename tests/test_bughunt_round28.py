"""UTF-8 BOM support must not weaken monster-file validation."""
import asyncio
import json
import unittest
import test_bughunt_round21 as fixture
from test_sqlite_storage import HTTPError

BOM=b'\xef\xbb\xbf'

class MonsterBomImportTests(unittest.TestCase):
    setUp=fixture.BoundedCombatantImportTests.setUp
    tearDown=fixture.BoundedCombatantImportTests.tearDown
    monster=fixture.BoundedCombatantImportTests.monster

    def payload(self,**changes):
        data={'name':'Goblin','type':'goblin','ac':12,'hp':10};data.update(changes)
        return json.dumps(data,ensure_ascii=False).encode('utf-8')

    def parse(self,raw):
        self.monster(raw)
        return self.c.parse_monster(raw)

    def test_bom_prefixed_monster_is_accepted(self):
        self.assertEqual(self.parse(BOM+self.payload())['name'],'Goblin')

    def test_bom_prefixed_unicode_and_zero_values_are_preserved(self):
        fields=self.parse(BOM+self.payload(name='蘭 🌙',ac=0,hp=0))
        self.assertEqual(fields['name'],'蘭 🌙')
        self.assertEqual(fields['ac'],0);self.assertEqual(fields['hp'],0)

    def test_actual_bom_import_persists_normally(self):
        upload,call=self.monster(BOM+self.payload())
        created=asyncio.run(call())
        self.assertEqual(len(created),1)
        stored=self.c.STORAGE.load_setup(self.c.active_campaign(),'default')['monsters']
        self.assertIn(created[0]['id'],[x['id'] for x in stored])

    def test_duplicate_keys_remain_rejected_with_bom(self):
        raw=BOM+b'{"name":"Goblin","type":"goblin","ac":12,"hp":10,"hp":20}'
        with self.assertRaises(HTTPError) as error:self.parse(raw)
        self.assertEqual(error.exception.status_code,400)
        self.assertIn('duplicate',error.exception.detail.lower())

    def test_other_encodings_and_duplicate_bom_remain_rejected(self):
        plain=self.payload()
        for raw in (BOM+BOM+plain,plain.decode().encode('utf-16')):
            with self.subTest(raw=raw[:6]):
                with self.assertRaises(HTTPError) as error:self.parse(raw)
                self.assertEqual(error.exception.status_code,400)

    def test_plain_utf8_and_in_string_bom_are_unchanged(self):
        name='Goblin'+chr(0xFEFF)+' label'
        self.assertEqual(self.parse(self.payload(name=name))['name'],name)
        self.assertEqual(self.parse(self.payload())['hp'],10)

if __name__=='__main__':unittest.main()
