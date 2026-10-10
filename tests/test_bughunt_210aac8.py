"""Focused server regressions for 210aac8; real Pydantic v2 and SQLite.
D&D Beyond uses network/HTML fixtures; the handler is AST-extracted. No live
server, full database schema, routing or transaction integration is exercised.
"""
import ast,asyncio,copy,io,sqlite3,types,unittest
from pathlib import Path
from unittest.mock import patch
from pydantic import ValidationError
from python import scrying_glass_classes as models
from python import scrying_glass_dndbeyond as dnd
from python.scrying_glass_lair_rules import normalize_lairs
ROOT=Path(__file__).resolve().parents[1]
tree=ast.parse((ROOT/'python/scrying_glass_admin_display.py').read_text())
node=next(n for c in tree.body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='dndbeyond_monster_stats')
future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
ns={};exec(compile(ast.fix_missing_locations(ast.Module(body=[future,node],type_ignores=[])),'production-handler','exec'),ns)
lookup=ns['dndbeyond_monster_stats'];BAD=chr(0xD800)

class ModelTests(unittest.TestCase):
    def test_unicode_sqlite_roundtrip(self):
        value=models.CharacterCreate(name='José 🐉',color='#123456')
        with sqlite3.connect(':memory:') as db:
            self.assertEqual(db.execute('SELECT ?',(value.name,)).fetchone()[0],value.name)
    def test_sqlite_cannot_encode_surrogate(self):
        with sqlite3.connect(':memory:') as db:
            with self.assertRaises(UnicodeEncodeError):db.execute('SELECT ?',(BAD,))
    def test_exclude_unset_preserved(self):
        self.assertEqual(models.CharacterUpdate(name='Hero').model_dump(exclude_unset=True),{'name':'Hero'})
    def test_valid_critical_hit_preserved(self):
        self.assertTrue(models.MonsterUpdate(hp_delta=-1,critical_hit=True).critical_hit)
    def test_invalid_critical_hit_preserved(self):
        with self.assertRaises(ValidationError):models.CharacterUpdate(hp_delta=1,critical_hit=True)
    def test_nested_actions_preserved(self):
        value=models.BattleActions(actor_id='a',actions=[dict(target_id='b',action='damage',amount=2)])
        self.assertEqual(value.actions[0].amount,2)
    def test_optional_null_preserved(self):self.assertIsNone(models.CharacterUpdate(name=None).name)

def bad_model(name,data):
    def test(self):
        with self.assertRaises(ValidationError):getattr(models,name)(**copy.deepcopy(data))
    return test
cases=[('CharacterCreate',dict(name=BAD,color='#123456')),('CharacterCreate',dict(name='Hero',color=BAD)),
 ('CharacterUpdate',dict(name=BAD)),('MonsterUpdate',dict(name=BAD)),('MonsterUpdate',dict(monster_species=BAD)),
 ('MonsterUpdate',dict(color=BAD)),('CampaignCreate',dict(name=BAD)),('CampaignCreate',dict(name='Campaign',description=BAD)),
 ('CampaignUpdate',dict(description=BAD)),('DisplayBackgroundUpdate',dict(background=BAD)),('SetupName',dict(name=BAD)),
 ('SetupRename',dict(name='old',new_name=BAD)),('SetupImport',dict(name=BAD,kind='monsters')),
 ('CampaignSetupAdd',dict(setup=BAD,from_campaign='1')),('BattleStart',dict(order=[BAD])),
 ('BulkCombatantAction',dict(action='reset',ids=[BAD])),
 ('BattleActions',dict(actor_id='a',actions=[dict(target_id=BAD,action='damage',amount=1)]))]
for i,(name,data) in enumerate(cases):setattr(ModelTests,'test_bad_text_'+str(i)+'_'+name,bad_model(name,data))

class LairTests(unittest.TestCase):
    def test_valid_unicode_input_not_mutated(self):
        raw=[dict(id='l',name='Volcán 🐉',notes='Café')];before=copy.deepcopy(raw)
        result=normalize_lairs(raw);self.assertEqual(raw,before);self.assertEqual(result[0]['initiative'],20)
    def test_inactive_turn_rejected(self):
        with self.assertRaises(ValueError):normalize_lairs([dict(id='l',name='Lair',active=False,in_turn=True)])
    def test_color_validation_preserved(self):
        with self.assertRaises(ValueError):normalize_lairs([dict(id='l',name='Lair',color='red')])
def bad_lair(field):
    def test(self):
        raw=[dict(id='l',name='Lair',notes='')];raw[0][field]=BAD;before=copy.deepcopy(raw)
        with self.assertRaises(ValueError):normalize_lairs(raw)
        self.assertEqual(raw,before)
    return test
for field in ('id','name','notes'):setattr(LairTests,'test_bad_'+field,bad_lair(field))

class CandidateTests(unittest.TestCase):
    def candidates(self,name,html):
        with patch.object(dnd,'urlopen',return_value=io.BytesIO(html.encode())):return dnd.dnd_monster_candidates(name)
    def test_apostrophe_entity(self):
        self.assertEqual(self.candidates("Will-o'-Wisp",'<a href="/monsters/wisp">Will-o&#39;-Wisp</a>'),[(False,'/monsters/wisp')])
    def test_nbsp_entity(self):
        self.assertEqual(self.candidates('Red Dragon','<a href="/monsters/red">Red&nbsp;Dragon</a>'),[(False,'/monsters/red')])
    def test_ampersand_entity(self):
        self.assertEqual(self.candidates('A & B','<a href="/monsters/a">A &amp; B</a>'),[(False,'/monsters/a')])
    def test_href_decoded(self):
        self.assertEqual(self.candidates('Goblin','<a href="/monsters/g?q=1&amp;x=2">Goblin</a>'),[(False,'/monsters/g?q=1&x=2')])
    def test_decoded_href_deduplicated(self):
        html='<a href="/monsters/g?q=1&amp;x=2">Goblin</a><a href="/monsters/g?q=1&x=2">Goblin</a>'
        self.assertEqual(len(self.candidates('Goblin',html)),1)
    def test_legacy_preference_preserved(self):
        html='<a href="/monsters/new">Goblin</a><a href="/monsters/old" class="legacy">Goblin</a>'
        self.assertEqual(self.candidates('Goblin',html),[(True,'/monsters/old'),(False,'/monsters/new')])
    def test_nonmatching_name_rejected(self):
        self.assertEqual(self.candidates('Goblin','<a href="/monsters/orc">Orc</a>'),[])
    def test_nested_markup(self):
        self.assertEqual(self.candidates('Red Dragon','<a href="/monsters/red"><span>Red</span> Dragon</a>'),[(False,'/monsters/red')])
    def test_numeric_entity_text(self):
        self.assertEqual(dnd.html_to_text('<span>Will-o&#x27;-Wisp</span>'),"Will-o'-Wisp")

class StatsFallbackTests(unittest.TestCase):
    def context(self,detail,parse=lambda text:(12,'3d8+3','dice')):
        return types.SimpleNamespace(CONFIG={'display':{'dndbeyond_image_lookup':True}},
            dnd_monster_candidates=lambda species:[(True,'/monsters/old'),(False,'/monsters/new')],
            dnd_monster_detail_html=detail,dnd_monster_stats_from_html=parse)
    def call(self,c):return asyncio.run(lookup(types.SimpleNamespace(context=c),'Goblin'))
    def test_failed_legacy_uses_next(self):
        visited=[]
        def detail(href):
            visited.append(href)
            if href.endswith('old'):raise OSError('Unavailable')
            return 'current'
        result=self.call(self.context(detail));self.assertTrue(result['found']);self.assertFalse(result['legacy']);self.assertEqual(len(visited),2)
    def test_failed_parser_uses_next(self):
        def parse(text):
            if text.endswith('old'):raise ValueError('Bad candidate')
            return 12,'3d8+3','dice'
        result=self.call(self.context(lambda href:href,parse));self.assertTrue(result['found']);self.assertFalse(result['legacy'])
    def test_healthy_legacy_wins(self):
        result=self.call(self.context(lambda href:'valid'));self.assertTrue(result['found']);self.assertTrue(result['legacy'])
    def test_all_failed_optional(self):
        def detail(href):raise OSError('Unavailable')
        self.assertFalse(self.call(self.context(detail))['found'])
    def test_missing_stats_uses_next(self):
        result=self.call(self.context(lambda href:href,lambda text:(None,None,None) if text.endswith('old') else (12,'3d8+3','dice')))
        self.assertTrue(result['found']);self.assertFalse(result['legacy'])
    def test_disabled_no_network(self):
        c=self.context(lambda href:self.fail('Network should not run'));c.CONFIG['display']['dndbeyond_image_lookup']=False
        self.assertFalse(self.call(c)['found'])

if __name__=='__main__':unittest.main()
