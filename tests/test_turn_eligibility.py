"""Replaces the earlier tests that incorrectly used negative maximum HP as death."""
import ast,tempfile,unittest
from pathlib import Path
from test_sqlite_storage import context
from python.scrying_glass_turn_rules import can_take_turn
from python.scrying_glass_lair_rules import participants, initiative_key, place_lair
from python.scrying_glass_feature_rules import normalize_features,apply_hp

class TurnTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.c=context(Path(self.tmp.name));self.c.import_legacy_storage();self.c.load_state()
        tree=ast.parse((Path(__file__).resolve().parents[1]/'python/scrying_glass_service_battle.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef))
        future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0);scope={'can_take_turn':can_take_turn,'participants':participants,'initiative_key':initiative_key,'place_lair':place_lair}
        exec(compile(ast.fix_missing_locations(ast.Module(body=[future,cls],type_ignores=[])),'battle-service','exec'),scope)
        service=scope['BattleService'](self.c)
        for name in vars(scope['BattleService']):
            if not name.startswith('_') and callable(getattr(service,name,None)):setattr(self.c,name,getattr(service,name))
        from python.scrying_glass_combatant import numeric_initiative
        self.c.numeric_initiative=numeric_initiative
        self.c.STATE=self.c.normalize_state({'characters':[{'id':'a','name':'A','hp':10,'max_hp':25,'active':True,'initiative':20},{'id':'b','name':'B','hp':0,'max_hp':25,'active':True,'initiative':10}], 'monsters':[{'id':'m','name':'Monster','hp':5,'active':True,'initiative':5}]})
    def tearDown(self):self.c.STORAGE.close();self.tmp.cleanup()
    def test_down_takes_next_turn(self):self.c.begin_battle(['a','b','m']);self.assertEqual(self.c.advance_turn()['id'],'b')
    def test_stable_takes_next_turn(self):self.c.entity('b')['life_state']='stable';self.c.begin_battle(['a','b','m']);self.assertEqual(self.c.advance_turn()['id'],'b')
    def test_round_wrap(self):
        self.c.begin_battle(['a','b','m']);self.c.advance_turn();self.c.advance_turn();self.assertEqual(self.c.advance_turn()['id'],'a');self.assertEqual(self.c.STATE['battle_round'],2)
    def test_manual_down_turn(self):self.c.set_turn(self.c.entity('b'),True);self.assertTrue(self.c.entity('b')['in_turn'])
    def test_third_failure_removed(self):
        self.c.begin_battle(['a','b','m']);self.c.advance_turn();self.c.remember_turn_successors();self.c.entity('b')['death_failures']=2;apply_hp(self.c.entity('b'),-1);self.c.clean_order();self.assertNotIn('b',self.c.STATE['battle_order']);self.assertEqual(self.c.advance_turn()['id'],'m')
    def test_down_damage_preserves_turn(self):self.c.set_turn(self.c.entity('b'),True);apply_hp(self.c.entity('b'),-1);self.assertTrue(self.c.entity('b')['in_turn'])
    def test_zero_hp_monster_excluded(self):apply_hp(self.c.entity('m'),-5);self.assertFalse(can_take_turn(self.c.entity('m')))
    def test_negative_maximum_no_longer_means_death(self):x=self.c.entity('b');x['max_hp']=-1;normalize_features(x);self.assertEqual(x['life_state'],'down');self.assertTrue(can_take_turn(x))

if __name__=='__main__':unittest.main()
