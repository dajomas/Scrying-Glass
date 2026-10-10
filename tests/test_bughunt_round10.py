"""HP arithmetic must remain inside the signed storage range."""
import ast
import asyncio
import copy
import types
import unittest
from datetime import datetime,timezone
from pathlib import Path
import test_encounter_features as fixture
from test_sqlite_storage import HTTPError
from python.scrying_glass_classes import MAX_STORED_HP
from python.scrying_glass_feature_rules import apply_hp,normalize_features
from python.scrying_glass_turn_rules import permanently_dead,can_take_turn
from python.scrying_glass_database_transactions import transactional_handler


def load_class(filename,name,extra=None):
    path=Path(__file__).resolve().parents[1]/'python'/filename
    cls=next(x for x in ast.parse(path.read_text()).body if isinstance(x,ast.ClassDef) and x.name==name)
    scope=dict(Form=lambda *a,**kw:None,File=lambda *a,**kw:None,**(extra or {}))
    future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),str(path),'exec'),scope)
    return scope[name]


class HpArithmeticBoundsTests(unittest.TestCase):
    setUp=fixture.FeatureTests.setUp
    tearDown=fixture.FeatureTests.tearDown
    call=fixture.FeatureTests.call
    item=fixture.FeatureTests.item

    def maximum_monster(self,hp=MAX_STORED_HP):
        self.item().update(hp=hp,max_hp=MAX_STORED_HP,original_hp=MAX_STORED_HP)
        self.c.save_active_setup_monsters();self.c.save_state()

    def test_feature_healing_overflow_returns_422_and_rolls_back(self):
        self.maximum_monster()
        before=copy.deepcopy(self.c.STATE);revision=self.f.store.revision()
        with self.assertRaises(HTTPError) as error:self.call('edit_features','m',{'hp_delta':1})
        self.assertEqual(error.exception.status_code,422)
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.f.store.revision(),revision)
        self.assertEqual(self.c.STORAGE.load_setup(self.c.active_campaign(),'default')['monsters'][0]['hp'],MAX_STORED_HP)

    def test_pure_health_operation_rejects_overflow_before_hp_change(self):
        self.maximum_monster()
        item=copy.deepcopy(self.item());normalize_features(item);before=copy.deepcopy(item)
        with self.assertRaises(ValueError):apply_hp(item,1)
        self.assertEqual(item,before)

    def test_exact_upper_boundary_is_allowed(self):
        self.maximum_monster(MAX_STORED_HP-1)
        self.call('edit_features','m',{'hp_delta':1})
        self.assertEqual(self.item()['hp'],MAX_STORED_HP)

    def test_damage_at_upper_boundary_is_allowed(self):
        self.maximum_monster()
        self.call('edit_features','m',{'hp_delta':-1})
        self.assertEqual(self.item()['hp'],MAX_STORED_HP-1)

    def test_zero_delta_at_upper_boundary_is_allowed(self):
        self.maximum_monster();self.call('edit_features','m',{'hp_delta':0})
        self.assertEqual(self.item()['hp'],MAX_STORED_HP)

    def test_ordinary_healing_semantics_are_unchanged(self):
        self.call('edit_features','m',{'hp_delta':5})
        self.assertEqual(self.item()['hp'],17)

    def test_battle_batch_overflow_rolls_back_all_rows(self):
        self.maximum_monster()
        self.c.datetime=datetime;self.c.timezone=timezone
        self.c.log_battle_action=load_class('scrying_glass_service_activity.py','ActivityService')(self.c).log_battle_action
        cls=load_class('scrying_glass_admin_battle.py','AdminBattleMixin',dict(apply_hp=apply_hp,permanently_dead=permanently_dead,can_take_turn=can_take_turn))
        handler=cls();handler.context=self.c
        payload=types.SimpleNamespace(actor_id='c',actions=[
            types.SimpleNamespace(target_id='c',action='damage',amount=1,critical_hit=False),
            types.SimpleNamespace(target_id='m',action='heal',amount=1,critical_hit=False)])
        before=copy.deepcopy(self.c.STATE);revision=self.f.store.revision()
        with self.assertRaises(HTTPError) as error:
            asyncio.run(transactional_handler(self.c,handler.apply_battle_actions)(payload))
        self.assertEqual(error.exception.status_code,422)
        self.assertEqual(self.c.STATE,before)
        self.assertEqual(self.f.store.revision(),revision)
        self.assertEqual(self.c.STORAGE.load_characters(self.c.active_campaign())[0]['hp'],20)

    def test_unrelated_value_errors_are_not_relabelled_as_client_errors(self):
        async def broken():raise ValueError('programming failure')
        with self.assertRaisesRegex(ValueError,'programming failure'):
            asyncio.run(transactional_handler(self.c,broken)())

if __name__=='__main__':unittest.main()
