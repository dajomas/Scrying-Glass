"""Focused damage, model, handler, persistence and turn regression tests."""
import ast,asyncio,copy,tempfile,types,unittest
from pathlib import Path
from python.scrying_glass_feature_rules import apply_hp,normalize_features
from python.scrying_glass_turn_rules import can_take_turn
from test_sqlite_storage import context,HTTPError

class DamageTests(unittest.TestCase):
    def item(self,hp=10,maximum=25,**kw):
        value=dict(id='c',name='Hero',hp=hp,max_hp=maximum,active=True,alive=hp>0,life_state='standing' if hp else 'down',death_successes=0,death_failures=0,temp_hp=0,in_turn=True)
        value.update(kw);return value
    def test_drop_exactly_to_zero_no_failed_save(self):
        x=self.item();apply_hp(x,-10);self.assertEqual((x['hp'],x['life_state'],x['death_failures']),(0,'down',0));self.assertTrue(x['in_turn'])
    def test_excess_below_maximum(self):
        x=self.item();apply_hp(x,-34);self.assertEqual((x['hp'],x['life_state']),(0,'down'))
    def test_excess_equal_maximum(self):
        x=self.item();r=apply_hp(x,-35);self.assertEqual((x['hp'],x['life_state']),(0,'dead'));self.assertTrue(r['instant_death']);self.assertFalse(can_take_turn(x))
    def test_excess_above_maximum(self):
        x=self.item();apply_hp(x,-36);self.assertEqual(x['life_state'],'dead')
    def test_zero_hp_damage_adds_one_failure(self):
        x=self.item(0);apply_hp(x,-1);self.assertEqual((x['hp'],x['death_failures'],x['life_state']),(0,1,'down'))
    def test_zero_hp_sub_maximum_damage(self):
        x=self.item(0);apply_hp(x,-24);self.assertEqual((x['hp'],x['death_failures'],x['life_state']),(0,1,'down'))
    def test_zero_hp_maximum_damage_instant_death(self):
        x=self.item(0);r=apply_hp(x,-25);self.assertTrue(r['instant_death']);self.assertEqual(x['hp'],0);self.assertEqual(x['life_state'],'dead')
    def test_failures_accumulate_not_negative_hp(self):
        x=self.item(0)
        for _ in range(2):apply_hp(x,-1);self.assertEqual(x['hp'],0);self.assertTrue(can_take_turn(x))
        apply_hp(x,-1);self.assertEqual(x['death_failures'],3);self.assertEqual(x['life_state'],'dead')
    def test_critical_hit_two_failures(self):
        x=self.item(0);apply_hp(x,-1,critical=True);self.assertEqual(x['death_failures'],2)
    def test_critical_with_one_failure_kills(self):
        x=self.item(0,death_failures=1);apply_hp(x,-1,critical=True);self.assertEqual((x['death_failures'],x['life_state']),(3,'dead'))
    def test_critical_initial_drop_no_extra_failures(self):
        x=self.item();apply_hp(x,-10,critical=True);self.assertEqual(x['death_failures'],0)
    def test_instant_death_takes_precedence(self):
        x=self.item(0);r=apply_hp(x,-25,critical=True);self.assertTrue(r['instant_death']);self.assertEqual(r['failed_saves'],0)
    def test_temporary_hp_before_current_hp(self):
        x=self.item(temp_hp=7);apply_hp(x,-12);self.assertEqual((x['hp'],x['temp_hp']),(5,0))
    def test_temp_reduces_massive_damage_excess(self):
        x=self.item(temp_hp=7);apply_hp(x,-35);self.assertEqual(x['life_state'],'down');self.assertEqual(x['hp'],0)
    def test_temp_absorbed_damage_at_zero_still_fails(self):
        x=self.item(0,temp_hp=7);apply_hp(x,-1);self.assertEqual((x['hp'],x['temp_hp'],x['death_failures']),(0,6,1))
    def test_damage_bypass(self):
        x=self.item(temp_hp=7);apply_hp(x,-10,absorb=False);self.assertEqual((x['hp'],x['temp_hp']),(0,7))
    def test_healing_resets_saves(self):
        x=self.item(0,death_successes=1,death_failures=2);apply_hp(x,4);self.assertEqual((x['hp'],x['life_state'],x['death_successes'],x['death_failures']),(4,'standing',0,0))
    def test_dead_not_healed(self):
        x=self.item(0,life_state='dead');apply_hp(x,5);self.assertEqual((x['hp'],x['life_state']),(0,'dead'))
    def test_stable_damage_restarts_saves(self):
        x=self.item(0,life_state='stable',death_successes=3);apply_hp(x,-1);self.assertEqual((x['life_state'],x['death_successes'],x['death_failures']),('down',0,1))
    def test_stabilization_resets_counters(self):
        x=self.item(0,life_state='stable',death_successes=3,death_failures=1);normalize_features(x);self.assertEqual((x['death_successes'],x['death_failures']),(0,0))
    def test_zero_damage_no_failure(self):
        x=self.item(0);apply_hp(x,0);self.assertEqual(x['death_failures'],0)
    def test_monster_no_death_saves(self):
        x=self.item(monster_species='goblin');apply_hp(x,-10);self.assertEqual(x['hp'],0);self.assertEqual(x['death_failures'],0);self.assertFalse(can_take_turn(x))
    def test_legacy_negative_hp_clamped_not_damage(self):
        x=self.item(-4,life_state='down');normalize_features(x);self.assertEqual((x['hp'],x['death_failures']),(0,0))
    def test_negative_maximum_is_not_death_marker(self):
        x=self.item(0,maximum=-1);normalize_features(x);self.assertEqual(x['max_hp'],0);self.assertEqual(x['life_state'],'down');self.assertTrue(can_take_turn(x))
    def test_all_damage_results_nonnegative(self):
        for hp in (0,1,10,25):
            for damage in range(1,60):
                x=self.item(hp);apply_hp(x,-damage);self.assertGreaterEqual(x['hp'],0)
    def test_models_reject_negative_stored_hp(self):
        from python.scrying_glass_classes import CharacterUpdate,MonsterUpdate
        for model in (CharacterUpdate,MonsterUpdate):
            with self.assertRaises(ValueError):model(hp=-1)
        with self.assertRaises(ValueError):CharacterUpdate(max_hp=-1)
    def handler(self,name,file,scope):
        tree=ast.parse((Path(__file__).resolve().parents[1]/'python'/file).read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef));method=next(n for n in cls.body if isinstance(n,ast.AsyncFunctionDef) and n.name==name)
        future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[future,method],type_ignores=[])),file,'exec'),scope);return scope[name]
    def test_actual_battle_handler_accepts_downed_target(self):
        actor=self.item(id='a',name='Actor');target=self.item(0,id='b',in_turn=False);items={'a':actor,'b':target};events=[]
        async def persist(**kwargs):pass
        c=types.SimpleNamespace(entity=items.get,HTTPException=HTTPError,remember_turn_successors=lambda:None,clean_order=lambda:None,save_active_campaign_characters=lambda:None,combatants_changed=persist,log_battle_action=lambda *a:None,insert_into_battle_order=lambda *a:None,features=types.SimpleNamespace(log=lambda *a,**kw:events.append((a,kw))))
        from python.scrying_glass_turn_rules import permanently_dead
        fn=self.handler('apply_battle_actions','scrying_glass_admin_battle.py',{'apply_hp':apply_hp,'can_take_turn':can_take_turn,'permanently_dead':permanently_dead})
        payload=types.SimpleNamespace(actor_id='a',actions=[types.SimpleNamespace(target_id='b',action='damage',amount=1,critical_hit=False)])
        c.STATE={'activity_log':[]};asyncio.run(fn(types.SimpleNamespace(context=c),payload));self.assertEqual(target['death_failures'],1);self.assertEqual(target['hp'],0);self.assertEqual(events[0][0][0],'death-save-failure')
    def test_actual_character_delta_handler(self):
        x=self.item(0);events=[]
        async def persist(**kwargs):pass
        c=types.SimpleNamespace(STATE={'characters':[x]},HTTPException=HTTPError,remember_turn_successors=lambda:None,clean_order=lambda:None,set_turn=lambda *a:None,insert_into_battle_order=lambda *a:None,combatants_changed=persist,log_hp_change=lambda *a:events.append(a))
        fn=self.handler('update_character','scrying_glass_admin_characters.py',{'__package__':'python','can_take_turn':can_take_turn})
        update=types.SimpleNamespace(model_dump=lambda **kwargs:{'hp_delta':-2});asyncio.run(fn(types.SimpleNamespace(context=c),'c',update));self.assertEqual((x['hp'],x['death_failures']),(0,1));self.assertTrue(x['in_turn'])
    def test_actual_battle_critical_flag(self):
        actor=self.item(id='a');target=self.item(0,id='b',in_turn=False);items={'a':actor,'b':target}
        async def persist(**kwargs):pass
        c=types.SimpleNamespace(STATE={'activity_log':[]},entity=items.get,HTTPException=HTTPError,remember_turn_successors=lambda:None,clean_order=lambda:None,save_active_campaign_characters=lambda:None,combatants_changed=persist,log_battle_action=lambda *a:None,insert_into_battle_order=lambda *a:None)
        from python.scrying_glass_turn_rules import permanently_dead
        fn=self.handler('apply_battle_actions','scrying_glass_admin_battle.py',{'apply_hp':apply_hp,'can_take_turn':can_take_turn,'permanently_dead':permanently_dead});row=types.SimpleNamespace(target_id='b',action='damage',amount=1,critical_hit=True)
        asyncio.run(fn(types.SimpleNamespace(context=c),types.SimpleNamespace(actor_id='a',actions=[row])));self.assertEqual(target['death_failures'],2)
    def test_save_and_restart_zero_hp_turn(self):
        with tempfile.TemporaryDirectory() as directory:
            c=context(Path(directory));c.import_legacy_storage();c.load_state();c.STATE=c.normalize_state({'characters':[self.item(0)],'battle_order':['c'],'battle_round':2})
            # Baseline SQLite fixture is v4; omit empty effects, which normalization supplies.
            for x in c.entities():x.pop('effects',None)
            c.save_active_campaign_characters();c.save_state();c.STORAGE.close();c.STORAGE=c.STORAGE.__class__(Path(directory)/'scrying-glass.sqlite3');c.load_state()
            self.assertTrue(c.STATE['characters'][0]['in_turn']);self.assertEqual(c.STATE['characters'][0]['hp'],0);c.STORAGE.close()

if __name__=='__main__':unittest.main()
