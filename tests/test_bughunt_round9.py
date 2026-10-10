"""Monster HP edit bounds agree with creation/import storage bounds."""
import ast
import asyncio
import types
import unittest
from pathlib import Path
import test_encounter_features as fixture
from python.scrying_glass_classes import MonsterUpdate
from python.scrying_glass_combatant import update_alive_state
from python.scrying_glass_database_transactions import transactional_handler

class MonsterHpBoundsTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown

    def test_model_accepts_hp_above_previous_edit_limit(self):
        MonsterUpdate(hp=150000,max_hp=150000,original_hp=150000)

    def test_model_accepts_signed_storage_maximum(self):
        maximum=2**63-1
        MonsterUpdate(hp=maximum,max_hp=maximum,original_hp=maximum)

    def test_negative_and_storage_overflow_are_rejected(self):
        for key in ('hp','max_hp','original_hp'):
            for value in (-1,2**63):
                with self.subTest(key=key,value=value):
                    with self.assertRaises(ValueError):MonsterUpdate(**{key:value})

    def test_delta_limits_remain_unchanged(self):
        with self.assertRaises(ValueError):MonsterUpdate(hp_delta=100000)
        MonsterUpdate(hp_delta=99999)

    def test_existing_large_hp_monster_can_be_renamed(self):
        monster=self.c.entity('m')
        monster.update(hp=150000,max_hp=150000,original_hp=150000)
        self.c.save_active_setup_monsters();self.c.save_state()
        self.c.update_alive_state=update_alive_state
        def validated(**kwargs):
            model=MonsterUpdate(**kwargs)
            def dump(**options):
                return model.model_dump(**options) if hasattr(model,'model_dump') else model.dict(**options)
            return types.SimpleNamespace(model_dump=dump)
        self.c.MonsterUpdate=validated
        path=Path(__file__).resolve().parents[1]/'python/scrying_glass_admin_monsters.py'
        cls=next(x for x in ast.parse(path.read_text()).body if isinstance(x,ast.ClassDef))
        future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
        scope=dict(Form=lambda *a,**kw:None,File=lambda *a,**kw:None)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),str(path),'exec'),scope)
        handler=scope['AdminMonstersMixin']();handler.context=self.c
        result=asyncio.run(transactional_handler(self.c,handler.edit_monster)(
            'm',name='Renamed goblin',monster_species='goblin',ac=10,hp=150000,
            max_hp=150000,original_hp=150000,color='#842029',initiative='',ally='false',image=None))
        self.assertEqual(result['name'],'Renamed goblin')
        self.assertEqual(result['hp'],150000)
        loaded=self.c.STORAGE.load_setup(self.c.active_campaign(),'default')['monsters'][0]
        self.assertEqual(loaded['name'],'Renamed goblin')
        self.assertEqual(loaded['hp'],150000)

if __name__=='__main__':unittest.main()
