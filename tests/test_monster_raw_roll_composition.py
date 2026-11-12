"""Static raw-roll route and script contracts."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class RawRollCompositionTests(unittest.TestCase):
    def test_authenticated_patch_route_and_body_parameter(self):
        tree=ast.parse((ROOT/'python/scrying_glass_api_admin.py').read_text())
        routes=next(node.value for node in tree.body if isinstance(node,ast.Assign)
                    and any(isinstance(target,ast.Name) and target.id=='ADMIN_ROUTES' for target in node.targets))
        entry=('/api/monsters/{ident}/initiative-roll','set_monster_initiative_roll','PATCH',True)
        self.assertEqual(ast.literal_eval(routes).count(entry),1)
        cls=next(node for node in tree.body if isinstance(node,ast.ClassDef) and node.name=='AdminAPI')
        method=next(node for node in cls.body if getattr(node,'name','')=='set_monster_initiative_roll')
        self.assertEqual(method.args.args[-1].annotation.id,'dict')
        self.assertEqual(method.args.defaults[-1].func.id,'Body')

    def test_script_loaded_once_after_roster_and_navigation(self):
        end=(ROOT/'templates/admin/190_document_end.html').read_text()
        marker='/static/monster-initiative-roll.js?v=3'
        self.assertEqual(end.count(marker),1)
        for predecessor in ('/static/admin.js','/static/initiative-keyboard-navigation.js','/static/monster-initiative-roster.js'):
            self.assertLess(end.index(predecessor),end.index(marker))
