"""Optional character CSV baselines must stay valid with wide current HP."""
import asyncio
import types
import unittest
import test_bughunt_round11 as fixture
from test_sqlite_storage import HTTPError
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_health_limits import MAX_STORED_HP

class CharacterCsvDefaultTests(unittest.TestCase):
    setUp=fixture.CsvLairIdentityTests.setUp
    tearDown=fixture.CsvLairIdentityTests.tearDown

    def upload(self,hp,max_hp=None,original_hp=None,include_columns=True,ident='new-character'):
        header='id,name,hp';row=f'{ident},Imported,{hp}'
        if include_columns:
            header+=',max_hp,original_hp'
            row+=f',{"" if max_hp is None else max_hp},{"" if original_hp is None else original_hp}'
        raw=(header+'\n'+row+'\n').encode()
        async def read(size=-1):return raw if size<0 else raw[:size]
        cls=fixture.load_class('scrying_glass_admin_characters.py','AdminCharactersMixin')
        handler=cls();handler.context=self.c
        asyncio.run(transactional_handler(self.c,handler.import_characters_csv)(types.SimpleNamespace(filename='import.csv',read=read)))
        return self.c.entity(ident)

    def test_large_hp_with_missing_optional_columns_is_accepted(self):
        item=self.upload(100019,include_columns=False)
        self.assertEqual((item['hp'],item['max_hp'],item['original_hp']),(100019,99999,99999))

    def test_large_hp_with_blank_optional_values_is_accepted(self):
        item=self.upload(100019)
        self.assertEqual(item['max_hp'],99999);self.assertEqual(item['original_hp'],99999)

    def test_upper_current_hp_keeps_derived_defaults_in_range(self):
        item=self.upload(MAX_STORED_HP,include_columns=False)
        self.assertEqual(item['hp'],MAX_STORED_HP)
        self.assertEqual(item['max_hp'],99999)

    def test_explicit_valid_baselines_are_preserved(self):
        item=self.upload(100019,max_hp=20,original_hp=15)
        self.assertEqual((item['max_hp'],item['original_hp']),(20,15))

    def test_explicit_oversized_maximum_is_not_silently_clamped(self):
        with self.assertRaises(HTTPError) as error:self.upload(100019,max_hp=100000)
        self.assertEqual(error.exception.status_code,400)

    def test_small_current_hp_defaults_are_unchanged(self):
        item=self.upload(10,include_columns=False)
        self.assertEqual((item['max_hp'],item['original_hp']),(10,10))

    def test_historical_negative_current_hp_defaults_are_unchanged(self):
        item=self.upload(-5,include_columns=False)
        self.assertEqual((item['hp'],item['max_hp'],item['original_hp']),(0,0,0))

    def test_large_hp_and_defaults_survive_reload(self):
        item=self.upload(100019,include_columns=False)
        self.c.load_state()
        item=self.c.entity(item['id'])
        self.assertEqual((item['hp'],item['max_hp'],item['original_hp']),(100019,99999,99999))

if __name__=='__main__':unittest.main()
