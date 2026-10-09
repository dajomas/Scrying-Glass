"""Focused logging descriptions, actual logger, and CSV export regression tests."""
import ast,asyncio,copy,csv,io,unittest,uuid
from pathlib import Path
from types import SimpleNamespace
from python.scrying_glass_feature_logging import feature_changes

class LoggingTests(unittest.TestCase):
    def before(self): return dict(hp=12,temp_hp=7,life_state='standing',death_successes=0,death_failures=0,concentrating=False)
    def test_concentration_started(self):
        old=self.before();events=feature_changes(old,{**old,'concentrating':True})
        self.assertEqual(events,[('concentration-started',None,'Concentration started')])
    def test_concentration_ended(self):
        old={**self.before(),'concentrating':True};events=feature_changes(old,{**old,'concentrating':False})
        self.assertEqual(events[0][0],'concentration-ended');self.assertIn('linked effects',events[0][2])
    def test_duplicate_start_is_not_logged(self):
        item={**self.before(),'concentrating':True};self.assertEqual(feature_changes(item,dict(item)),[])
    def test_hp_and_temp_details(self):
        old=self.before();events=feature_changes(old,{**old,'hp':9,'temp_hp':0},-10)
        self.assertEqual(events,[('combat-features',10,'HP: 12 → 9; Temporary HP: 7 → 0')])
    def test_life_state_and_save_details(self):
        old={**self.before(),'life_state':'down','death_successes':2};events=feature_changes(old,{**old,'life_state':'stable','death_successes':3})
        self.assertIn('Life state: down → stable',events[0][2]);self.assertIn('Death-save successes: 2 → 3',events[0][2])
    def test_failures_identified(self):
        old=self.before();events=feature_changes(old,{**old,'death_failures':1})
        self.assertEqual(events[0][2],'Death-save failures: 0 → 1')
    def test_separate_feature_and_concentration_events(self):
        old={**self.before(),'concentrating':True};events=feature_changes(old,{**old,'hp':0,'life_state':'down','concentrating':False},-12)
        self.assertEqual([e[0] for e in events],['combat-features','concentration-ended'])
    def test_temp_pool_named(self):
        old=self.before();events=feature_changes(old,{**old,'temp_hp':10})
        self.assertEqual(events[0],('combat-features',None,'Temporary HP: 7 → 10'))
    def test_real_logger_preserves_effect_note(self):
        root=Path(__file__).resolve().parents[1]
        tree=ast.parse((root/'python/scrying_glass_service_features.py').read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef))
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='log')
        scope={'uuid':uuid}
        exec(compile(ast.Module(body=[method],type_ignores=[]),'logger','exec'),scope)
        context=SimpleNamespace(STATE={},active_combatant=lambda:None,now_iso=lambda:'now',combatant_state=lambda target:'standing' if target else 'unknown')
        service=SimpleNamespace(context=context);target={'id':'m','name':'Goblin'}
        scope['log'](service,'effect-added',target,note='Blessed')
        entry=context.STATE['activity_log'][0]
        self.assertEqual(entry['note'],'Blessed');self.assertEqual(entry['target_combatant'],'Goblin')
    def test_csv_note_included_and_formula_safe(self):
        root=Path(__file__).resolve().parents[1]
        tree=ast.parse((root/'python/scrying_glass_admin_activity.py').read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef))
        method=next(n for n in cls.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='export_activity_log_csv')
        future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
        scope={};exec(compile(ast.fix_missing_locations(ast.Module(body=[future,method],type_ignores=[])),'csv-export','exec'),scope)
        context=SimpleNamespace(STATE={'activity_log':[{'action':'effect-added','note':'=malicious'},{'action':'effect-removed','note':'Blessed'}]},io=io,csv=csv,Response=lambda **kwargs:SimpleNamespace(**kwargs))
        response=asyncio.run(scope['export_activity_log_csv'](SimpleNamespace(context=context)))
        rows=list(csv.DictReader(io.StringIO(response.content)))
        self.assertEqual(rows[0]['note'],"'=malicious");self.assertEqual(rows[1]['note'],'Blessed')

if __name__=='__main__':unittest.main()
