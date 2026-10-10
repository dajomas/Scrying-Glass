import sys, ast, textwrap, tempfile, json, csv, io, re, uuid, copy
from pathlib import Path
sys.path.insert(0, 'tests')
from test_sqlite_storage import context, HTTPError

def load_functions(path, names, namespace):
    text = Path(path).read_text()
    for node in ast.parse(text).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            code = '\n'.join(text.splitlines()[node.lineno-1:node.end_lineno])
            exec('from __future__ import annotations\n' + code, namespace)

with tempfile.TemporaryDirectory() as directory:
    c = context(Path(directory)); c.import_legacy_storage()
    campaign = c.active_campaign()
    longname = 'a'*80
    c.STORAGE.save_setup(campaign, longname, c.setup_snapshot(c.normalize_state({})))
    candidate = c.STORAGE.unique_setup_name(campaign, longname)
    assert len(candidate) <= 80 and candidate != longname
    assert c.setup_slug(candidate) == candidate
    c.STORAGE.save_setup(campaign, candidate, c.setup_snapshot(c.normalize_state({})))
    third = c.STORAGE.unique_setup_name(campaign, longname)
    assert third not in (longname,candidate) and len(third)<=80
    for raw in ({'unknown_nested': {'important': [1]}}, {'activity_log':[42]}):
        try: c.normalize_state(raw); raise AssertionError('Expected rejection')
        except ValueError: pass
    raw={'activity_log':[{'action':'damage','amount':2}]}
    normalized=c.normalize_state(raw)
    assert 'id' not in raw['activity_log'][0]
    c.STORAGE.save_setup(campaign,'log',c.setup_snapshot(normalized))
    before=[tuple(r) for r in c.STORAGE.connection.execute('SELECT id,event_id FROM activity_log_entries')]
    c.STORAGE.save_setup(campaign,'log',c.setup_snapshot(normalized))
    after=[tuple(r) for r in c.STORAGE.connection.execute('SELECT id,event_id FROM activity_log_entries')]
    assert before==after
    try: c.normalize_state({'activity_log':[{'id':'x'},{'id':'x'}]});raise AssertionError()
    except ValueError:pass
    c.STORAGE.close()
ns={'json':json,'csv':csv,'io':io,'re':re,'uuid':uuid,'HTTPException':HTTPError}
load_functions('python/scrying_glass_monster_csv.py',{'csv_text','csv_rows','parse_monster'},ns)
for data in (b'name,Name\nA,B\n',b'name,hp\nA,1,2\n',b'name,hp\n"unclosed,1',b'name,\nA,1\n'):
    try:ns['csv_rows'](data);raise AssertionError('Expected malformed CSV rejection')
    except HTTPError as e:assert e.status_code==400
assert ns['csv_rows'](b'name,hp\n"a\nb",1\n')[0]['name']=='a\nb'
for hp in (str(2**63), '9'*5000):
    raw=json.dumps({'name':'Goblin','type':'Goblin','ac':12,'hpText':hp}).encode()
    try:ns['parse_monster'](raw);raise AssertionError('Expected overflow rejection')
    except HTTPError as e:assert e.status_code==400
raw=('{'+'"name":"Goblin","type":"Goblin","ac":12,"hp":'+'9'*5000+'}').encode()
try:ns['parse_monster'](raw);raise AssertionError()
except HTTPError as e:assert e.status_code==400
assert ns['parse_monster'](b'{"name":"G","type":"G","ac":0,"hp":0}')['hp']==0
print('PASS: bounded setup suffixes, unknown state rejection, malformed log rejection, stable log IDs, duplicate log IDs, CSV validation/multiline preservation, monster integer bounds/JSON conversion, zero preservation')
