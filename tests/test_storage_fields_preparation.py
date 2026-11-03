"""Preparation checks only: no storage import, database or application startup."""
import ast
import hashlib
from pathlib import Path
import unittest
from python import scrying_glass_storage_fields as staged

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("TEXT_FIELDS", "INT_FIELDS", "BOOL_FIELDS", "ENTITY_FIELDS",
         "LOG_FIELDS", "LIST_FIELDS", "STATE_FIELDS")


def definitions(source):
    tree = ast.parse(source)
    nodes = [node for node in tree.body if isinstance(node, ast.Assign)
             and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
             and node.targets[0].id in NAMES]
    if tuple(node.targets[0].id for node in nodes) != NAMES:
        raise AssertionError("Expected the seven ordered storage field definitions")
    return nodes


def original_fields():
    source = (ROOT / "python/scrying_glass_storage.py").read_text(encoding="utf-8")
    namespace = {}
    module = ast.Module(body=definitions(source), type_ignores=[])
    exec(compile(module, "<original storage field definitions>", "exec"), namespace)
    return namespace


class StorageFieldsPreparationTests(unittest.TestCase):
    def test_original_storage_is_unchanged(self):
        data = (ROOT / "python/scrying_glass_storage.py").read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        self.assertEqual(digest, "ea80b59cca80c6885f6ba1ba4d32b759beb187b5")

    def test_values_types_and_order_match(self):
        original = original_fields()
        for name in NAMES:
            with self.subTest(field=name):
                value = getattr(staged, name)
                self.assertIs(type(value), type(original[name]))
                self.assertEqual(value, original[name])

    def test_definition_expressions_match(self):
        original = (ROOT / "python/scrying_glass_storage.py").read_text(encoding="utf-8")
        proposed = (ROOT / "python/scrying_glass_storage_fields.py").read_text(encoding="utf-8")
        self.assertEqual([ast.dump(node, include_attributes=False) for node in definitions(original)],
                         [ast.dump(node, include_attributes=False) for node in definitions(proposed)])

    def test_mutable_state_fields_are_independent(self):
        original = original_fields()
        self.assertIsNot(staged.STATE_FIELDS, original["STATE_FIELDS"])
        sentinel = "__storage_split_mutation_probe__"
        self.assertNotIn(sentinel, staged.STATE_FIELDS)
        try:
            staged.STATE_FIELDS.add(sentinel)
            self.assertNotIn(sentinel, original["STATE_FIELDS"])
        finally:
            staged.STATE_FIELDS.discard(sentinel)
        self.assertEqual(staged.STATE_FIELDS, original["STATE_FIELDS"])

    def test_staged_module_size_and_dependencies(self):
        data = (ROOT / "python/scrying_glass_storage_fields.py").read_bytes()
        self.assertLessEqual(len(data), 20000)
        tree = ast.parse(data.decode("utf-8"))
        self.assertFalse(any(isinstance(node, (ast.Import, ast.ImportFrom))
                             for node in ast.walk(tree)))
        self.assertEqual({name for name in vars(staged) if not name.startswith("_")}, set(NAMES))


if __name__ == "__main__":
    unittest.main()
