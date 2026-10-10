"""CSV imports must not collide with turn-only lair identities."""
import ast
import asyncio
import copy
import types
import unittest
from pathlib import Path
import test_encounter_features as fixture
from test_sqlite_storage import HTTPError
from python.scrying_glass_lair_rules import normalize_lairs
from python.scrying_glass_database_transactions import transactional_handler


def load_class(filename,name):
    path=Path(__file__).resolve().parents[1]/'python'/filename
    cls=next(x for x in ast.parse(path.read_text()).body if isinstance(x,ast.ClassDef) and x.name==name)
    future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
    scope=dict(Form=lambda *a,**kw:None,File=lambda *a,**kw:None)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),str(path),'exec'),scope)
    return scope[name]


class CsvLairIdentityTests(unittest.TestCase):
    def setUp(self):
        fixture.FeatureTests.setUp(self)
        path=Path(__file__).resolve().parents[1]/'python/scrying_glass_monster_csv.py'
        nodes=[n for n in ast.parse(path.read_text()).body if not(isinstance(n,ast.ImportFrom) and n.module=='fastapi')]
        scope={'HTTPException':HTTPError}
        exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(path),'exec'),scope)
        for name in ('csv_rows','csv_monster','csv_character'):setattr(self.c,name,scope[name])
        self.c.STATE['lairs']=normalize_lairs([{'id':'lair-existing','name':'Volcano'}])
        self.c.insert_into_battle_order(self.c.STATE['lairs'][0])
        self.c.save_active_setup_monsters();self.c.save_state()
    tearDown=fixture.FeatureTests.tearDown

    def upload(self,kind,ident):
        if kind=='monsters':
            raw=f'id,name,monster_species,ac,hp,active,visible,initiative\n{ident},Goblin import,goblin,12,10,true,true,30\n'.encode()
            cls=load_class('scrying_glass_admin_monsters.py','AdminMonstersMixin')
            method='import_monsters_csv'
        else:
            raw=f'id,name,hp\n{ident},Character import,10\n'.encode()
            cls=load_class('scrying_glass_admin_characters.py','AdminCharactersMixin')
            method='import_characters_csv'
        async def read(size=-1):return raw if size < 0 else raw[:size]
        handler=cls();handler.context=self.c
        return asyncio.run(transactional_handler(self.c,getattr(handler,method))(
            types.SimpleNamespace(filename='import.csv',read=read)))

    def rejected(self,kind,ident):
        before=copy.deepcopy(self.c.STATE);revision=self.f.store.revision()
        before_setup=self.c.STORAGE.load_setup(self.c.active_campaign(),'default')
        before_roster=self.c.STORAGE.load_characters(self.c.active_campaign())
        with self.assertRaises(HTTPError) as error:self.upload(kind,ident)
        self.assertEqual(error.exception.status_code,400)
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.f.store.revision(),revision)
        self.assertEqual(self.c.STORAGE.load_setup(self.c.active_campaign(),'default'),before_setup)
        self.assertEqual(self.c.STORAGE.load_characters(self.c.active_campaign()),before_roster)

    def test_monster_import_rejects_existing_lair_id(self):self.rejected('monsters','lair-existing')
    def test_character_import_rejects_existing_lair_id(self):self.rejected('characters','lair-existing')
    def test_character_import_rejects_monster_id_in_another_setup(self):
        state=self.c.normalize_state({'monsters':[{'id':'saved-monster','name':'Saved monster','hp':10}]})
        self.c.STORAGE.save_setup(self.c.active_campaign(),'other',self.c.setup_snapshot(state))
        self.rejected('characters','saved-monster')

    def test_character_import_rejects_lair_id_in_another_setup(self):
        state=self.c.normalize_state({'lairs':[{'id':'saved-lair','name':'Saved lair'}]})
        self.c.STORAGE.save_setup(self.c.active_campaign(),'other',self.c.setup_snapshot(state))
        self.rejected('characters','saved-lair')

    def test_existing_character_collision_remains_rejected(self):self.rejected('monsters','c')

    def test_valid_monster_import_and_restart_keep_distinct_ids(self):
        self.assertEqual(self.upload('monsters','new-monster'),{'count':1})
        self.c.load_state()
        self.assertEqual(self.c.entity('lair-existing')['kind'],'lair')
        self.assertEqual(self.c.entity('new-monster')['monster_species'],'goblin')
        self.assertIn('new-monster',self.c.STATE['battle_order'])

    def test_valid_character_import_and_restart_keep_distinct_ids(self):
        self.assertEqual(self.upload('characters','new-character'),{'count':1})
        self.c.load_state()
        self.assertEqual(self.c.entity('lair-existing')['kind'],'lair')
        self.assertIn('new-character',[x['id'] for x in self.c.STATE['characters']])

    def test_state_without_lairs_key_still_imports(self):
        self.c.STATE.pop('lairs')
        self.assertEqual(self.upload('monsters','new-monster'),{'count':1})
        self.assertIsNotNone(self.c.entity('new-monster'))

if __name__=='__main__':unittest.main()
