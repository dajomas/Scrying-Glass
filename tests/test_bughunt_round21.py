"""Combatant import handlers must bound reads before decoding/parsing."""
import ast
import asyncio
import copy
import types
import unittest
from pathlib import Path
import test_bughunt_round11 as csv_fixture
import test_bughunt_round10 as helpers
from test_sqlite_storage import HTTPError
from python.scrying_glass_database_transactions import transactional_handler

LIMIT=5*1024*1024

class Upload:
    def __init__(self,filename,raw):self.filename=filename;self.raw=raw;self.calls=[]
    async def read(self,size=-1):
        self.calls.append(size)
        return self.raw if size<0 else self.raw[:size]

class BoundedCombatantImportTests(unittest.TestCase):
    setUp=csv_fixture.CsvLairIdentityTests.setUp
    tearDown=csv_fixture.CsvLairIdentityTests.tearDown

    def csv(self,kind,raw=None):
        if raw is None:
            raw=(b'id,name,monster_species,ac,hp\nbounded-monster,Goblin,goblin,12,10\n' if kind=='monsters'
                 else b'id,name,hp\nbounded-character,Hero,10\n')
        upload=Upload('import.csv',raw)
        cls=csv_fixture.load_class('scrying_glass_admin_'+kind+'.py',
             'AdminMonstersMixin' if kind=='monsters' else 'AdminCharactersMixin')
        handler=cls();handler.context=self.c
        method=handler.import_monsters_csv if kind=='monsters' else handler.import_characters_csv
        return upload,transactional_handler(self.c,method)

    def monster(self,raw):
        path=Path(__file__).resolve().parents[1]/'python/scrying_glass_monster_csv.py'
        nodes=[n for n in ast.parse(path.read_text()).body if not(isinstance(n,ast.ImportFrom) and n.module=='fastapi')]
        scope={'HTTPException':HTTPError}
        exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),str(path),'exec'),scope)
        self.c.parse_monster=scope['parse_monster']
        service=helpers.load_class('scrying_glass_service_images.py','ImagesService')(self.c)
        self.c.make_monster=service.make_monster;self.c.make_monsters=service.make_monsters
        self.c.dnd_image=lambda species:None
        cls=helpers.load_class('scrying_glass_admin_monsters.py','AdminMonstersMixin',dict(asyncio=asyncio))
        handler=cls();handler.context=self.c
        upload=Upload('import.monster',raw)
        async def run():return await transactional_handler(self.c,handler.import_monster)(
            upload,color='#842029',quantity=1,image=None)
        return upload,run

    def reject(self,upload,call):
        before=copy.deepcopy(self.c.STATE);campaigns=self.c.read_campaigns();revision=self.f.store.revision()
        with self.assertRaises(HTTPError) as error:asyncio.run(call())
        self.assertEqual(error.exception.status_code,413)
        self.assertEqual(upload.calls,[LIMIT+1])
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.c.read_campaigns(),campaigns)
        self.assertEqual(self.f.store.revision(),revision)

    def test_monster_csv_small_file_uses_bounded_read(self):
        upload,handler=self.csv('monsters')
        self.assertEqual(asyncio.run(handler(upload)),{'count':1})
        self.assertEqual(upload.calls,[LIMIT+1])

    def test_character_csv_small_file_uses_bounded_read(self):
        upload,handler=self.csv('characters')
        self.assertEqual(asyncio.run(handler(upload)),{'count':1})
        self.assertEqual(upload.calls,[LIMIT+1])

    def test_monster_json_small_file_uses_bounded_read(self):
        upload,call=self.monster(b'{"name":"Goblin","type":"goblin","ac":12,"hp":10}')
        self.assertEqual(len(asyncio.run(call())),1)
        self.assertEqual(upload.calls,[LIMIT+1])

    def test_monster_csv_oversize_rejected_before_parser(self):
        upload,handler=self.csv('monsters',b'x'*(LIMIT+1))
        self.reject(upload,lambda:handler(upload))

    def test_character_csv_oversize_rejected_before_parser(self):
        upload,handler=self.csv('characters',b'x'*(LIMIT+1))
        self.reject(upload,lambda:handler(upload))

    def test_monster_json_oversize_rejected_before_parser(self):
        upload,call=self.monster(b'x'*(LIMIT+1))
        self.reject(upload,call)

    def test_exact_limit_monster_json_is_allowed(self):
        payload=b'{"name":"Goblin","type":"goblin","ac":12,"hp":10}'
        upload,call=self.monster(payload+b' '*(LIMIT-len(payload)))
        self.assertEqual(len(asyncio.run(call())),1)
        self.assertEqual(upload.calls,[LIMIT+1])

    def test_exact_limit_character_csv_is_allowed(self):
        payload=b'id,name,hp\nbounded-character,Hero,10\n'
        upload,handler=self.csv('characters',payload+b'\n'*(LIMIT-len(payload)))
        self.assertEqual(asyncio.run(handler(upload)),{'count':1})
        self.assertEqual(upload.calls,[LIMIT+1])

if __name__=='__main__':unittest.main()
