"""Focused service-method regressions for commit 4eb87b6.

Extracts the production FeaturesService class via AST to avoid unrelated imports.
External collaborators are fixtures; checkpoint name storage uses real SQLite.
This does not test FastAPI routing, full storage, transactions or server startup.
"""
import ast
import asyncio
import copy
import sqlite3
import types
import unittest
import uuid
from pathlib import Path

class HTTPError(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)

SOURCE = Path(__file__).resolve().parents[1] / 'python' / 'scrying_glass_service_features.py'
tree = ast.parse(SOURCE.read_text())
cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'FeaturesService')
scope = dict(copy=copy, uuid=uuid, normalize_features=lambda item: item,
             FeatureStorage=lambda store: store, fingerprint=lambda state: 'digest',
             can_take_turn=lambda item: bool(item.get('active')),
             feature_changes=lambda *args: [])
exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])), str(SOURCE), 'exec'), scope)
FeaturesService = scope['FeaturesService']

class Store:
    def __init__(self):
        self.db = sqlite3.connect(':memory:')
        self.db.execute('CREATE TABLE snapshots (id INTEGER PRIMARY KEY, name TEXT)')
        self.rev = 1
        self.loaded = 0
        self.deleted = 0
    def save_snapshot(self, campaign, state, kind, name):
        return self.db.execute('INSERT INTO snapshots(name) VALUES (?)', (name,)).lastrowid
    def revision(self): return self.rev
    def latest_undo(self, campaign): return dict(id=1, after_digest='digest', name='Previous')
    def load(self, *args): self.loaded += 1; return {}
    def delete(self, *args): self.deleted += 1


def item(ident, **values):
    result = dict(id=ident, name=ident, hp=10, alive=True, active=True,
                  concentrating=False, effects=[])
    result.update(values)
    return result


def effect(**values):
    result = dict(id='effect', name='Condition', notes='', public=False,
                  concentration=False, source_id='source', anchor_id='anchor',
                  timing='end', turns=2)
    result.update(values)
    return result

class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.store = Store()
        self.hero = item('hero')
        self.state = dict(characters=[self.hero], monsters=[], lairs=[], activity_log=[])
        self.context = types.SimpleNamespace(STATE=self.state, STORAGE=self.store,
            HTTPException=HTTPError, active_campaign=lambda: 1,
            entities=lambda: self.state['characters'] + self.state['monsters'],
            remember_turn_successors=lambda: None, clean_order=lambda: None,
            insert_into_battle_order=lambda target: None)
        self.context.entity = lambda ident: next((x for x in self.context.entities()+self.state['lairs'] if x['id']==ident), None)
        self.f = FeaturesService(self.context)
        self.f.log = lambda *args, **kwargs: None
        self.f.restore_state = lambda state: None
        async def persist(): pass
        self.f.persist = persist
        self.f.target = self.context.entity
    def tearDown(self): self.store.db.close()
    def call(self, name, *args): return asyncio.run(getattr(self.f, name)(*args))
    def test_deleted_anchor_becomes_manual(self):
        self.hero['effects']=[effect(source_id=None)]
        self.f.reconcile()
        self.assertEqual((self.hero['effects'][0]['timing'],self.hero['effects'][0]['turns'],self.hero['effects'][0]['anchor_id']),('manual',None,None))
    def test_deleted_nonconcentration_source_is_cleared(self):
        self.hero['effects']=[effect(timing='manual',turns=None,anchor_id=None)]
        self.f.reconcile()
        self.assertIsNone(self.hero['effects'][0]['source_id'])
    def test_deleted_concentration_source_removes_effect(self):
        self.hero['effects']=[effect(concentration=True)]
        self.f.reconcile()
        self.assertEqual(self.hero['effects'],[])
    def test_existing_anchor_is_preserved(self):
        self.state['characters'].append(item('anchor'))
        self.hero['effects']=[effect(source_id=None)]
        self.f.reconcile()
        self.assertEqual(self.hero['effects'][0]['turns'],2)
        self.assertEqual(self.hero['effects'][0]['timing'],'end')
    def test_lair_anchor_and_source_preserved(self):
        self.state['lairs']=[dict(id='lair',kind='lair',active=True)]
        self.hero['effects']=[effect(source_id='lair',anchor_id='lair')]
        self.f.reconcile()
        self.assertEqual((self.hero['effects'][0]['source_id'],self.hero['effects'][0]['anchor_id']),('lair','lair'))
        self.assertEqual(self.hero['effects'][0]['timing'],'end')
    def test_inactive_existing_anchor_not_detached(self):
        self.state['characters'].append(item('anchor',active=False))
        self.hero['effects']=[effect(source_id=None)]
        self.f.reconcile()
        self.assertEqual(self.hero['effects'][0]['timing'],'end')
    def test_reconcile_is_idempotent(self):
        self.hero['effects']=[effect()]
        self.f.reconcile();before=copy.deepcopy(self.state);self.f.reconcile()
        self.assertEqual(self.state,before)
    def test_checkpoint_surrogate_rejected_before_sqlite(self):
        with self.assertRaises(HTTPError) as raised: self.call('save_checkpoint',{'name':'\ud800'})
        self.assertEqual(raised.exception.status_code,422)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM snapshots').fetchone()[0],0)
    def test_checkpoint_unicode_roundtrip(self):
        self.call('save_checkpoint',{'name':'  Café 🐉  '})
        self.assertEqual(self.store.db.execute('SELECT name FROM snapshots').fetchone()[0],'Café 🐉')
    def test_empty_checkpoint_rejected(self):
        with self.assertRaises(HTTPError): self.call('save_checkpoint',{'name':'  '})
    def test_integer_revision_accepted(self):
        self.call('restore_checkpoint',1,{'confirm':True,'revision':1})
        self.assertEqual(self.store.loaded,1)
    def test_stale_revision_rejected(self):
        with self.assertRaises(HTTPError): self.call('restore_checkpoint',1,{'confirm':True,'revision':2})
        self.assertEqual(self.store.loaded,0)
    def test_integer_undo_id_accepted(self):
        self.call('undo',{'id':1})
        self.assertEqual(self.store.deleted,1)
    def test_null_delta_rejected_without_mutation(self):
        before=copy.deepcopy(self.state)
        with self.assertRaises(HTTPError) as raised: self.call('edit_features','hero',{'hp_delta':None})
        self.assertEqual(raised.exception.status_code,422)
        self.assertEqual(self.state,before)
    def test_omitted_delta_allowed(self):
        self.call('edit_features','hero',{'temp_hp':4})
        self.assertEqual(self.hero['temp_hp'],4)


def invalid_revision(value):
    def test(self):
        with self.assertRaises(HTTPError) as raised: self.call('restore_checkpoint',1,{'confirm':True,'revision':value})
        self.assertEqual(raised.exception.status_code,409)
        self.assertEqual(self.store.loaded,0)
    return test
for label,value in (('bool',True),('float',1.0)):
    setattr(ServiceTests,'test_revision_rejects_'+label,invalid_revision(value))


def invalid_undo(value):
    def test(self):
        with self.assertRaises(HTTPError) as raised: self.call('undo',{'id':value})
        self.assertEqual(raised.exception.status_code,409)
        self.assertEqual((self.store.loaded,self.store.deleted),(0,0))
    return test
for label,value in (('bool',True),('float',1.0)):
    setattr(ServiceTests,'test_undo_rejects_'+label,invalid_undo(value))

if __name__=='__main__': unittest.main()
