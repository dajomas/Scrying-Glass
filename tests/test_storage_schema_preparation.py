"""Unused schema mixin: AST parity and limited real in-memory SQLite checks.

The original constructor, backups and later v4-v8 upgrades are not executed.
"""
import ast
import copy
import hashlib
import inspect
import json
from pathlib import Path
import sqlite3
import time
import unittest
from unittest.mock import patch
import uuid
from contextlib import contextmanager
from python import scrying_glass_storage_fields as fields
from python.scrying_glass_storage_schema import StorageSchemaMixin

ROOT = Path(__file__).resolve().parents[1]
METHODS = ("_create_schema", "convert_campaign_references", "_upgrade")


def original_methods():
    tree = ast.parse((ROOT / "python/scrying_glass_storage.py").read_text(encoding="utf-8"))
    storage = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "SQLiteStorage")
    return {node.name: node for node in storage.body if isinstance(node, ast.FunctionDef)}


def original_harness():
    methods = original_methods()
    names = (*METHODS, "transaction", "_check_foreign_keys", "set_value")
    node = ast.ClassDef(name="OriginalSchemaHarness", bases=[], keywords=[],
                        body=[copy.deepcopy(methods[name]) for name in names], decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    namespace = dict(copy=copy, json=json, time=time, uuid=uuid, contextmanager=contextmanager)
    namespace.update({name: getattr(fields, name) for name in
                      ("TEXT_FIELDS", "INT_FIELDS", "BOOL_FIELDS", "ENTITY_FIELDS", "LOG_FIELDS", "LIST_FIELDS", "STATE_FIELDS")})
    exec(compile(module, "<original schema harness>", "exec"), namespace)
    return namespace["OriginalSchemaHarness"]


class StorageSchemaPreparationTests(unittest.TestCase):
    def setUp(self):
        self.original = original_harness()
        self.proposed = type("StagedSchemaHarness", (StorageSchemaMixin, self.original), {})

    def storage(self, kind):
        storage = kind()
        storage.connection = sqlite3.connect(":memory:", isolation_level=None)
        storage.connection.row_factory = sqlite3.Row
        storage.connection.execute("PRAGMA foreign_keys=ON")
        storage.migration_backup = Path("fixture.backup")
        self.addCleanup(storage.connection.close)
        return storage

    def legacy(self, storage, version, runtime=None):
        db = storage.connection
        if version == 1:
            db.execute("CREATE TABLE campaigns(slug TEXT PRIMARY KEY,metadata_json TEXT NOT NULL)")
            owner = "campaign_slug"
        else:
            db.execute("CREATE TABLE campaigns(id INTEGER PRIMARY KEY,name TEXT,description TEXT,created TEXT,metadata_json TEXT)")
            owner = "campaign_id"
        db.execute(f"CREATE TABLE campaign_characters({owner} TEXT,characters_json TEXT)")
        db.execute(f"CREATE TABLE battle_setups({owner} TEXT,name TEXT,snapshot_json TEXT,updated_at REAL)")
        db.execute("CREATE TABLE application_state(key TEXT PRIMARY KEY,value_json TEXT)")
        if runtime is not None:
            db.execute("INSERT INTO application_state VALUES ('runtime_state',?)", (json.dumps(runtime),))
        db.execute(f"PRAGMA user_version={version}")

    def test_method_ast_equivalence(self):
        tree = ast.parse((ROOT / "python/scrying_glass_storage_schema.py").read_text(encoding="utf-8"))
        mixin = next(node for node in tree.body if isinstance(node, ast.ClassDef))
        proposed = {node.name: node for node in mixin.body if isinstance(node, ast.FunctionDef)}
        self.assertEqual(set(proposed), set(METHODS))
        original = original_methods()
        for name in METHODS:
            self.assertEqual(ast.dump(proposed[name], include_attributes=False),
                             ast.dump(original[name], include_attributes=False), name)

    def test_signatures_and_static_descriptor(self):
        for name in METHODS:
            self.assertEqual(inspect.signature(getattr(StorageSchemaMixin, name)),
                             inspect.signature(getattr(self.original, name)))
        self.assertIsInstance(inspect.getattr_static(StorageSchemaMixin, "convert_campaign_references"), staticmethod)
        self.assertNotIn("__init__", vars(StorageSchemaMixin))

    def test_base_schema_matches_original(self):
        original = self.storage(self.original)
        proposed = self.storage(self.proposed)
        for storage in (original, proposed):
            storage._create_schema()
            self.assertEqual(list(storage.connection.execute("PRAGMA foreign_key_check")), [])
        self.assertEqual(list(original.connection.iterdump()), list(proposed.connection.iterdump()))

    def test_empty_legacy_upgrades_match_original(self):
        for version in (1, 2):
            with self.subTest(version=version):
                original = self.storage(self.original)
                proposed = self.storage(self.proposed)
                for storage in (original, proposed):
                    self.legacy(storage, version)
                    with patch.object(time, "time", return_value=123456.0):
                        storage._upgrade(version)
                    self.assertEqual(storage.connection.execute("PRAGMA user_version").fetchone()[0], 3)
                    self.assertFalse(storage.connection.in_transaction)
                    self.assertEqual(list(storage.connection.execute("PRAGMA foreign_key_check")), [])
                self.assertEqual(list(original.connection.iterdump()), list(proposed.connection.iterdump()))

    def test_failed_upgrade_restores_old_schema(self):
        for version in (1, 2):
            for kind in (self.original, self.proposed):
                with self.subTest(version=version, kind=kind.__name__):
                    storage = self.storage(kind)
                    self.legacy(storage, version, {"active_setup": {"campaign": "missing", "name": "saved"}})
                    before = list(storage.connection.iterdump())
                    with self.assertRaisesRegex(ValueError, "Unknown campaign reference"):
                        storage._upgrade(version)
                    self.assertEqual(storage.connection.execute("PRAGMA user_version").fetchone()[0], version)
                    self.assertEqual(list(storage.connection.iterdump()), before)
                    self.assertFalse(storage.connection.in_transaction)

    def test_reference_conversion_parity_and_copy(self):
        samples = [None, {}, {"active_setup": None}, {"active_setup": []},
                   {"active_setup": {"campaign": "old", "name": "saved"}},
                   {"active_setup": {"campaign_id": 42, "name": "saved"}},
                   {"active_setup": {"campaign": "missing", "name": "saved"}}]
        for sample in samples:
            for strict in (False, True):
                outcomes = []
                for kind in (self.original, StorageSchemaMixin):
                    value = copy.deepcopy(sample)
                    try:
                        result = kind.convert_campaign_references(value, {"old": "7", "42": "9"}, strict=strict)
                        outcomes.append(("ok", result))
                    except ValueError as exc:
                        outcomes.append(("error", str(exc)))
                    self.assertEqual(value, sample)
                self.assertEqual(outcomes[0], outcomes[1])
        original = {"nested": [{"value": 1}]}
        converted = StorageSchemaMixin.convert_campaign_references(original, {})
        converted["nested"][0]["value"] = 2
        self.assertEqual(original["nested"][0]["value"], 1)

    def test_staged_size_dependencies_and_original_identity(self):
        path = ROOT / "python/scrying_glass_storage_schema.py"
        self.assertLessEqual(len(path.read_bytes()), 20000)
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = [node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
        self.assertEqual(imports, ["scrying_glass_storage_fields"])
        data = (ROOT / "python/scrying_glass_storage.py").read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        self.assertEqual(digest, "ea80b59cca80c6885f6ba1ba4d32b759beb187b5")


if __name__ == "__main__":
    unittest.main()
