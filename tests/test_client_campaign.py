"""Player-safe campaign metadata and rename notification unit tests."""
import ast,asyncio,copy,unittest
from pathlib import Path
from types import SimpleNamespace

class HTTPError(Exception):
    def __init__(self,status_code):self.status_code=status_code

def method(file,name):
    tree=ast.parse((Path(__file__).resolve().parents[1]/'python'/file).read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef));node=next(n for n in cls.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
    future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0);scope={}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[future,node],type_ignores=[])),file,'exec'),scope);return scope[name]

class CampaignTests(unittest.TestCase):
    def context(self,name='Campaign name'):
        return SimpleNamespace(public_state=lambda:{'monsters':[],'characters':[],'battle_order':[],'battle_round':0,'display':{}},active_campaign=lambda:'7',read_campaigns=lambda:{'campaigns':{'7':{'name':name,'description':'Private GM data','password':'never expose'}}},HTTPException=HTTPError,copy=copy,admin_initiative_key=lambda x:0)
    def display(self,c):return method('scrying_glass_service_state.py','display_state')(SimpleNamespace(context=c))
    def test_campaign_id_and_name_only(self):self.assertEqual(self.display(self.context())['campaign'],{'id':'7','name':'Campaign name'})
    def test_name_is_raw_text_for_safe_textcontent_rendering(self):self.assertEqual(self.display(self.context('<script>x</script>'))['campaign']['name'],'<script>x</script>')
    def test_metadata_does_not_leak(self):self.assertNotIn('Private GM data',str(self.display(self.context())));self.assertNotIn('never expose',str(self.display(self.context())))
    def test_no_active_campaign(self):
        c=self.context()
        def missing():raise HTTPError(404)
        c.active_campaign=missing;self.assertIsNone(self.display(c)['campaign'])
    def test_unexpected_errors_not_hidden(self):
        c=self.context()
        def failed():raise HTTPError(500)
        c.active_campaign=failed
        with self.assertRaises(HTTPError):self.display(c)
    def test_rename_broadcasts_active_campaign(self):
        calls=[]
        async def broadcast():calls.append('broadcast')
        c=SimpleNamespace(require_campaign=lambda x:'7',active_campaign=lambda:'7',HTTPException=HTTPError,STORAGE=SimpleNamespace(campaign_name_exists=lambda *a,**kw:False,update_campaign=lambda *a,**kw:None),broadcast=broadcast,campaigns_payload=lambda:{})
        fn=method('scrying_glass_admin_campaigns.py','update_campaign');asyncio.run(fn(SimpleNamespace(context=c),'7',SimpleNamespace(name='Renamed',description=None)));self.assertEqual(calls,['broadcast'])

if __name__=='__main__':unittest.main()
