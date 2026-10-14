"""Selected-monster shared initiative regression checks."""
import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

ROOT = Path(__file__).resolve().parents[1]

class SharedInitiativeTests(unittest.TestCase):
    def setUp(self):
        tree = ast.parse((ROOT / "python/scrying_glass_admin_monsters.py").read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        method = next(n for n in cls.body if getattr(n, "name", "") == "bulk_monsters")
        module = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), method], type_ignores=[])
        namespace = {}
        exec(compile(ast.fix_missing_locations(module), "bulk_monsters", "exec"), namespace)
        self.method = namespace["bulk_monsters"]
        self.monsters = [{"id": i, "initiative": v} for i, v in [("a", 2), ("b", 19), ("c", 7)]]
        def select(kind, ids):
            by_id = {m["id"]: m for m in self.monsters}
            if any(i not in by_id for i in ids):
                raise ValueError("Missing monster")
            return [by_id[i] for i in dict.fromkeys(ids)]
        self.context = SimpleNamespace(STATE={"monsters": self.monsters, "battle_order": ["a", "c", "b"]},
            random=SimpleNamespace(randint=Mock(return_value=13)), selected_entities=select,
            remember_turn_successors=Mock(), combatants_changed=AsyncMock(),
            HTTPException=lambda code, detail: ValueError(detail))

    def action(self, ids, action="roll-shared-initiative"):
        return asyncio.run(self.method(SimpleNamespace(context=self.context), SimpleNamespace(action=action, ids=ids)))

    def test_single_roll_selected_only(self):
        self.assertEqual(self.action(["a", "b"]), {"count": 2})
        self.assertEqual([m["initiative"] for m in self.monsters], [13, 13, 7])
        self.context.random.randint.assert_called_once_with(1, 20)
        self.context.combatants_changed.assert_awaited_once_with(monsters=True, characters=False)
        self.assertEqual(self.context.STATE["battle_order"], ["a", "c", "b"])

    def test_missing_id_is_atomic(self):
        with self.assertRaises(ValueError):
            self.action(["a", "missing"])
        self.context.random.randint.assert_not_called()
        self.assertEqual(self.monsters[0]["initiative"], 2)
        self.context.combatants_changed.assert_not_awaited()

    def test_duplicates(self):
        self.assertEqual(self.action(["a", "a"]), {"count": 1})
        self.context.random.randint.assert_called_once()

    def test_invalid_action(self):
        with self.assertRaises(ValueError):
            self.action(["a"], "invalid")
        self.context.random.randint.assert_not_called()

    def test_menu_option(self):
        self.assertIn('value="roll-shared-initiative"', (ROOT / "templates/admin/080_monster_display.html").read_text())

if __name__ == "__main__":
    unittest.main()
