"""CSV health normalization must precede turn-order eligibility checks."""
import asyncio
import copy
import types
import unittest
import test_bughunt_round11 as csv_fixture
from test_sqlite_storage import HTTPError
from python.scrying_glass_database_transactions import transactional_handler

class CsvHealthEligibilityTests(unittest.TestCase):
    setUp=csv_fixture.CsvLairIdentityTests.setUp
    tearDown=csv_fixture.CsvLairIdentityTests.tearDown

    def upload(self,kind,hp,alive,active=True,duplicate=False):
        ident='imported-'+kind
        if kind=='monsters':
            header='id,name,monster_species,ac,hp,alive,active,initiative'
            row=f'{ident},Imported monster,goblin,12,{hp},{str(alive).lower()},{str(active).lower()},30'
            cls=csv_fixture.load_class('scrying_glass_admin_monsters.py','AdminMonstersMixin')
            method='import_monsters_csv'
        else:
            header='id,name,hp,alive,active,initiative'
            row=f'{ident},Imported character,{hp},{str(alive).lower()},{str(active).lower()},30'
            cls=csv_fixture.load_class('scrying_glass_admin_characters.py','AdminCharactersMixin')
            method='import_characters_csv'
        raw=(header+'\n'+row+'\n'+(row+'\n' if duplicate else '')).encode()
        async def read():return raw
        handler=cls();handler.context=self.c
        asyncio.run(transactional_handler(self.c,getattr(handler,method))(
            types.SimpleNamespace(filename='import.csv',read=read)))
        return self.c.entity(ident)

    def test_zero_hp_monster_with_alive_flag_does_not_enter_order(self):
        item=self.upload('monsters',0,True)
        self.assertFalse(item['alive'])
        self.assertNotIn(item['id'],self.c.STATE['battle_order'])

    def test_explicitly_dead_character_does_not_enter_order(self):
        item=self.upload('characters',10,False)
        self.assertEqual(item['life_state'],'dead')
        self.assertEqual(item['hp'],0)
        self.assertNotIn(item['id'],self.c.STATE['battle_order'])

    def test_living_monster_inserts_without_changing_current_turn(self):
        current=self.c.active_combatant()['id']
        item=self.upload('monsters',10,True)
        self.assertEqual(self.c.STATE['battle_order'][0],item['id'])
        self.assertEqual(self.c.active_combatant()['id'],current)

    def test_downed_character_keeps_turn_eligibility(self):
        item=self.upload('characters',0,False)
        self.assertEqual(item['life_state'],'down')
        self.assertIn(item['id'],self.c.STATE['battle_order'])

    def test_historical_negative_character_hp_normalizes_to_down(self):
        item=self.upload('characters',-5,False)
        self.assertEqual(item['hp'],0)
        self.assertEqual(item['life_state'],'down')
        self.assertIn(item['id'],self.c.STATE['battle_order'])

    def test_inactive_monster_does_not_enter_order(self):
        item=self.upload('monsters',10,True,active=False)
        self.assertNotIn(item['id'],self.c.STATE['battle_order'])

    def test_imported_order_does_not_change_after_reload(self):
        item=self.upload('monsters',0,True)
        before=list(self.c.STATE['battle_order'])
        self.c.load_state()
        self.assertEqual(self.c.STATE['battle_order'],before)
        self.assertNotIn(item['id'],self.c.STATE['battle_order'])

    def test_duplicate_batch_is_still_rejected_atomically(self):
        before=copy.deepcopy(self.c.STATE)
        with self.assertRaises(HTTPError) as error:self.upload('monsters',10,True,duplicate=True)
        self.assertEqual(error.exception.status_code,400)
        self.assertIn('duplicate',error.exception.detail.lower())
        self.assertEqual(self.c.STATE,before)

if __name__=='__main__':unittest.main()
