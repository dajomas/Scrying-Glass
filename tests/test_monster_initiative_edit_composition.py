"""API composition contracts, not authenticated HTTP/storage acceptance."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


class EditCompositionStaticTests(unittest.TestCase):
    def tree(self):
        return ast.parse((ROOT / "python/scrying_glass_api_admin.py").read_text(encoding="utf-8"))

    def test_selected_mixin(self):
        imports = [node for node in self.tree().body if isinstance(node, ast.ImportFrom)
                   and node.module == "scrying_glass_monster_initiative_edit"]
        self.assertEqual(len(imports), 1)
        self.assertEqual([(item.name, item.asname) for item in imports[0].names],
                         [("InitiativeEditMonstersMixin", "AdminMonstersMixin")])

    def test_existing_edit_route_remains_authenticated_post(self):
        routes = next(node.value for node in self.tree().body
                      if isinstance(node, ast.Assign) and any(
                          isinstance(target, ast.Name) and target.id == "ADMIN_ROUTES"
                          for target in node.targets))
        matches = [row for row in ast.literal_eval(routes)
                   if row[0] == "/api/monsters/{ident}/edit"]
        self.assertEqual(matches, [("/api/monsters/{ident}/edit", "edit_monster", "POST", True)])

    def test_composition_contains_monster_group_once(self):
        cls = next(node for node in self.tree().body
                   if isinstance(node, ast.ClassDef) and node.name == "AdminAPI")
        self.assertEqual(sum(isinstance(base, ast.Name) and base.id == "AdminMonstersMixin"
                             for base in cls.bases), 1)


class EditCompositionRuntimeTests(unittest.TestCase):
    def test_edit_resolves_to_new_handler(self):
        from python.scrying_glass_api_admin import AdminAPI
        from python.scrying_glass_monster_initiative_edit import InitiativeEditMonstersMixin
        self.assertIs(AdminAPI.edit_monster, InitiativeEditMonstersMixin.edit_monster)

    def test_candidate_creation_and_lookup_are_retained(self):
        from python.scrying_glass_api_admin import AdminAPI
        from python.scrying_glass_monster_selection import CandidateMonstersMixin
        self.assertIs(AdminAPI.create_monster, CandidateMonstersMixin.create_monster)
        self.assertIs(AdminAPI.monster_lookup_candidates, CandidateMonstersMixin.monster_lookup_candidates)

    def test_character_and_legacy_update_handlers_are_retained(self):
        from python.scrying_glass_api_admin import AdminAPI
        from python.scrying_glass_admin_monsters import AdminMonstersMixin
        from python.scrying_glass_admin_characters import AdminCharactersMixin
        self.assertIs(AdminAPI.update_monster, AdminMonstersMixin.update_monster)
        self.assertIs(AdminAPI.update_character, AdminCharactersMixin.update_character)

    def test_registration_keeps_security_and_transaction_contract(self):
        from fastapi import FastAPI
        from fastapi.params import Form as FormParameter
        from python import scrying_glass_api_admin as api
        from python.scrying_glass_monster_initiative_edit import InitiativeEditMonstersMixin
        async def auth():
            return None
        context = SimpleNamespace(ADMIN_SESSION_COOKIE="admin-test", require=Mock(return_value=auth))
        instance = object.__new__(api.AdminAPI)
        instance.context = context
        instance.app = FastAPI()
        entry = ("/api/monsters/{ident}/edit", "edit_monster", "POST", True)
        with patch.object(api, "ADMIN_ROUTES", (entry,)), patch.object(
            api, "transactional_handler", side_effect=lambda context, handler, **kwargs: handler
        ) as transaction, patch.object(api, "serialized_handler") as serialized:
            instance.register_routes()
        context.require.assert_called_once_with("admin", "admin-test")
        transaction.assert_called_once_with(context, instance.edit_monster,
                                            role="admin", cookie_name="admin-test")
        serialized.assert_not_called()
        route = next(route for route in instance.app.routes if route.path == entry[0])
        self.assertEqual(route.methods, {"POST"})
        self.assertIs(route.endpoint.__func__, InitiativeEditMonstersMixin.edit_monster)
        self.assertEqual([dependency.dependency for dependency in route.dependencies],
                         [auth, api.same_origin])
        bonus = next(field for field in route.dependant.body_params if field.name == "initiative_bonus")
        self.assertIsInstance(bonus.field_info, FormParameter)
        self.assertFalse(bonus.field_info.is_required())
        self.assertEqual(bonus.field_info.default, "")
