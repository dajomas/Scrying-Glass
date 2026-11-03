"""Activation checks for the original field expressions and compatibility exports."""
import ast
import unittest
from python import scrying_glass_storage as facade
from python import scrying_glass_storage_fields as fields
from storage_split_reference import field_nodes, reference_methods

NAMES = ('TEXT_FIELDS', 'INT_FIELDS', 'BOOL_FIELDS', 'ENTITY_FIELDS', 'LOG_FIELDS', 'LIST_FIELDS', 'STATE_FIELDS')


class StorageFieldsPreparationTests(unittest.TestCase):
    def test_original_fields_and_method_surface(self):
        self.assertEqual(len(reference_methods()), 38)
        self.assertEqual([n.targets[0].id for n in field_nodes()], list(NAMES))

    def test_exports_and_mutability(self):
        namespace = {}
        exec(compile(ast.Module(body=field_nodes(), type_ignores=[]), '<field fixture>', 'exec'), namespace)
        for name in NAMES:
            self.assertEqual(getattr(fields, name), namespace[name])
            self.assertIs(type(getattr(fields, name)), type(namespace[name]))
            self.assertIs(getattr(facade, name), getattr(fields, name))
        try:
            fields.STATE_FIELDS.add('__probe__')
            self.assertIn('__probe__', facade.STATE_FIELDS)
            self.assertNotIn('__probe__', namespace['STATE_FIELDS'])
        finally:
            fields.STATE_FIELDS.discard('__probe__')
