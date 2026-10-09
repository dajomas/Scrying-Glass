import ast, asyncio, copy, tempfile, textwrap, sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,'tests')
from test_sqlite_storage import context, Handlers
from python.scrying_glass_database_transactions import transactional_handler
text=Path('python/scrying_glass_admin_activity.py').read_text()
cls=next(n for n in ast.parse(text).body if isinstance(n,ast.ClassDef) and n.name=='AdminActivityMixin')
fn=next(n for n in cls.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='clear_activity_log')
ns={};exec('from __future__ import annotations\n'+textwrap.dedent('\n'.join(text.splitlines()[fn.lineno-1:fn.end_lineno])),ns)
with tempfile.TemporaryDirectory() as directory:
 c=context(Path(directory))
 try:
  c.import_legacy_storage();campaign=c.active_campaign();handlers=Handlers(c)
  c.STATE=c.normalize_state({'activity_log':[{'id':'event','action':'damage','amount':2}], 'display':{'background':'#123456'}})
  asyncio.run(transactional_handler(c,handlers.save_setup)(payload=SimpleNamespace(name='fight',campaign=None)))
  other=copy.deepcopy(c.STORAGE.load_setup(campaign,'fight'));c.STORAGE.save_setup(campaign,'other',other)
  c.STATE['display']['background']='#abcdef'
  result=asyncio.run(transactional_handler(c,ns['clear_activity_log'])(SimpleNamespace(context=c)))
  restored=c.load_setup_state('fight',campaign)
  print('returned count:',result['cleared'],'live entries:',len(c.STATE['activity_log']),'reloaded setup entries:',len(restored['activity_log']))
  if sys.argv[1]=='patched':
   assert result['cleared']==1 and restored['activity_log']==[] and c.STATE['activity_log']==[]
   assert c.STORAGE.load_setup(campaign,'other')['activity_log']==other['activity_log']
   assert c.STORAGE.load_setup(campaign,'fight')['display']['background']=='#123456'
   assert c.STATE['display']['background']=='#abcdef'
   c.load_state();assert c.STATE['activity_log']==[]
   assert c.STATE['display']['background']=='#abcdef'
   c.STATE['activity_log']=[{'id':'rollback','action':'heal','amount':1}]
   c.save_state();before=copy.deepcopy(c.STATE)
   with patch.object(c,'save_state',side_effect=RuntimeError('injected save failure')):
    try:asyncio.run(transactional_handler(c,ns['clear_activity_log'])(SimpleNamespace(context=c)))
    except RuntimeError:pass
    else:raise AssertionError('Expected failure')
   assert c.STATE==before
   print('PASS: reload/restart persistence, other-setup isolation, background separation and rollback')
 finally:c.STORAGE.close()

