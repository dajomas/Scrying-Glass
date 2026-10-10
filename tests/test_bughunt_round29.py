"""CSV current HP bounds match values accepted by creation and healing."""
import asyncio
import types
import unittest
import test_bughunt_round11 as fixture
from test_sqlite_storage import HTTPError
from python.scrying_glass_database_transactions import transactional_handler
from python.scrying_glass_health_limits import MAX_STORED_HP

class CsvStoredHpBoundsTests(unittest.TestCase):
    setUp=fixture.CsvLairIdentityTests.setUp
    tearDown=fixture.CsvLairIdentityTests.tearDown

    def upload(self,kind,hp,max_hp=None,original_hp=None,ident=None):
        ident=ident or 'large-'+kind
        headers='id,name,hp,max_hp,original_hp'
        values=f'{ident},Imported,{hp},{"" if max_hp is None else max_hp},{"" if original_hp is None else original_hp}'
        if kind=='monsters':headers+=',monster_species,ac';values+=',goblin,12'
        raw=(headers+'\n'+values+'\n').encode()
        async def read(size=-1):return raw if size<0 else raw[:size]
        cls=fixture.load_class('scrying_glass_admin_'+kind+'.py',
            'AdminMonstersMixin' if kind=='monsters' else 'AdminCharactersMixin')
        handler=cls();handler.context=self.c
        method=handler.import_monsters_csv if kind=='monsters' else handler.import_characters_csv
        asyncio.run(transactional_handler(self.c,method)(types.SimpleNamespace(filename='import.csv',read=read)))
        return self.c.entity(ident)

    def test_monster_csv_accepts_hp_supported_by_creation(self):
        item=self.upload('monsters',150000)
        self.assertEqual((item['hp'],item['max_hp'],item['original_hp']),(150000,150000,150000))
        self.c.load_state();self.assertEqual(self.c.entity(item['id'])['hp'],150000)

    def test_character_current_hp_accepts_valid_healing_result(self):
        item=self.upload('characters',100019,max_hp=20,original_hp=20)
        self.assertEqual(item['hp'],100019)
        self.assertEqual(item['max_hp'],20)

    def test_monster_stored_hp_fields_accept_signed_upper_endpoint(self):
        item=self.upload('monsters',MAX_STORED_HP,max_hp=MAX_STORED_HP,original_hp=MAX_STORED_HP)
        self.assertEqual(item['hp'],MAX_STORED_HP)

    def test_storage_overflow_remains_controlled(self):
        for kind in ('monsters','characters'):
            with self.subTest(kind=kind):
                with self.assertRaises(HTTPError) as error:self.upload(kind,MAX_STORED_HP+1)
                self.assertEqual(error.exception.status_code,400)

    def test_negative_monster_hp_remains_rejected(self):
        with self.assertRaises(HTTPError) as error:self.upload('monsters',-1)
        self.assertEqual(error.exception.status_code,400)

    def test_historical_negative_character_hp_behavior_is_unchanged(self):
        item=self.upload('characters',-5,max_hp=20,original_hp=20)
        self.assertEqual(item['hp'],0);self.assertEqual(item['life_state'],'down')

    def test_character_maximum_and_baseline_limits_are_not_widened(self):
        with self.assertRaises(HTTPError) as error:self.upload('characters',10,max_hp=100000,original_hp=100000)
        self.assertEqual(error.exception.status_code,400)

    def test_identity_conflicts_remain_rejected(self):
        with self.assertRaises(HTTPError) as error:self.upload('monsters',150000,ident='c')
        self.assertEqual(error.exception.status_code,400)
        self.assertIn('already exists',error.exception.detail)

if __name__=='__main__':unittest.main()
