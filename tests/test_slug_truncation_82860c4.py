"""Truncation must not produce a slug that normalizes to a different name."""
import ast
from pathlib import Path
import re
import pytest
from test_sqlite_storage import HTTPError

source=Path(__file__).resolve().parents[1]/'python/scrying_glass_tools.py'
tree=ast.parse(source.read_text())
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('setup_slug','campaign_slug')]
scope={'re':re,'HTTPException':HTTPError}
exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),scope)

@pytest.mark.parametrize('function', ['setup_slug','campaign_slug'])
@pytest.mark.parametrize('name', ['a'*79+'-b', 'a'*79+' b', 'a'*78+'--bb', 'a'*80+' b', 'Dragon Lair'])
def test_slug_is_canonical_after_truncation(function,name):
    slug=scope[function](name)
    assert 1<=len(slug)<=80
    assert not slug.endswith('-')
    assert scope[function](slug)==slug

def test_saved_setup_remains_loadable_by_returned_name(tmp_path):
    from test_sqlite_storage import context
    c=context(tmp_path)
    try:
        c.setup_slug=scope['setup_slug']
        c.import_legacy_storage();c.load_state()
        campaign=c.active_campaign()
        name=c.setup_slug('a'*79+'-b')
        c.STORAGE.save_setup(campaign,name,c.setup_snapshot(c.STATE))
        assert c.load_setup_state(name,campaign)['monsters']==[]
    finally:
        c.STORAGE.close()
