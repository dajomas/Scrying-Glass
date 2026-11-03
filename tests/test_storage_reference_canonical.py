"""Stable original-AST fingerprints across supported interpreter dump formats."""
import ast
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import storage_split_reference as reference


class StorageReferenceCanonicalTests(unittest.TestCase):
    def test_original_pins_and_reference_class(self):
        self.assertEqual(len(reference.reference_methods()), 38)
        self.assertEqual(len(reference.field_nodes()), 7)
        cls = reference.reference_class()
        s = reference.base_storage(self, cls)
        campaign = s.create_campaign('Canonical fixture', '', 'now')
        self.assertTrue(s.campaign_exists(campaign))
        self.assertEqual(cls.SCHEMA_VERSION, 8)

    def test_optional_lists_are_explicit_without_ast_dump(self):
        tree = ast.parse('def f():\n    return call(None)\n')
        with patch.object(ast, 'dump', side_effect=AssertionError('Do not use version-dependent dump')):
            value = reference.canonical(tree)
        for text in ('posonlyargs=[]', 'args=[]', 'defaults=[]', 'keywords=[]', 'decorator_list=[]', 'Constant(value=None)'):
            self.assertIn(text, value)
        self.assertNotIn('type_params=[]', value)
        shifted = ast.increment_lineno(ast.parse('def f():\n    return call(None)\n'), 20)
        self.assertEqual(reference.canonical(shifted), value)

    def test_semantic_values_and_nonempty_type_parameters_remain(self):
        values = [reference.canonical(ast.parse(source)) for source in ('x = None', 'x = False', 'x = 0', 'x = 1', 'x = "None"')]
        self.assertEqual(len(set(values)), len(values))
        node = ast.parse('def f(): pass').body[0]
        node.type_params = [ast.Name(id='T', ctx=ast.Load())]
        if 'type_params' in node._fields:
            self.assertIn('type_params=[', reference.canonical(node))

    def test_pins_reject_changed_sql_and_field_definitions(self):
        root = reference.ROOT
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            shutil.copytree(root/'python', target/'python')
            operation = target/'python/scrying_glass_storage_operations.py'
            source = operation.read_text(encoding='utf-8')
            changed = source.replace('INSERT INTO campaigns(', 'INSERT INTO changed_campaigns(', 1)
            self.assertNotEqual(source, changed)
            operation.write_text(changed, encoding='utf-8')
            with patch.object(reference, 'ROOT', target):
                with self.assertRaisesRegex(AssertionError, 'Original method bodies'):
                    reference.reference_methods()
            operation.write_text(source, encoding='utf-8')
            field = target/'python/scrying_glass_storage_fields.py'
            tree = ast.parse(field.read_text(encoding='utf-8'))
            tree.body.append(ast.parse('EXTRA_FIELD = 1').body[0])
            field.write_text(ast.unparse(tree), encoding='utf-8')
            with patch.object(reference, 'ROOT', target):
                with self.assertRaisesRegex(AssertionError, 'Original field expressions'):
                    reference.field_nodes()


if __name__ == '__main__':
    unittest.main()
