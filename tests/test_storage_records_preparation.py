"""Staged records: AST parity and real SQLite base-schema fixtures, not full v8."""
import ast
import copy
import hashlib
import inspect
from pathlib import Path
import sqlite3
import unittest
import uuid
from contextlib import contextmanager
from python import scrying_glass_storage_fields as fields
from python.scrying_glass_storage_records import StorageRecordsMixin

ROOT = Path(__file__).resolve().parents[1]
METHODS = ("_typed", "_attributes", "_read_attributes", "_save_entities", "_load_entities",
           "_save_log", "_load_log", "_save_lists", "_save_encounter", "_load_encounter")


def original_methods():
    tree = ast.parse((ROOT / "python/scrying_glass_storage.py").read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "SQLiteStorage")
    return {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}


def original_harness():
    methods = original_methods()
    names = (*METHODS, "_create_schema", "transaction", "_check_foreign_keys")
    cls = ast.ClassDef(name="OriginalRecords", bases=[], keywords=[],
                      body=[copy.deepcopy(methods[n]) for n in names], decorator_list=[])
    module = ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[]))
    namespace = dict(uuid=uuid, contextmanager=contextmanager, __package__="python",
                     __name__="python._records_fixture")
    namespace.update({n: getattr(fields, n) for n in
                      ("TEXT_FIELDS", "INT_FIELDS", "BOOL_FIELDS", "ENTITY_FIELDS",
                       "LOG_FIELDS", "LIST_FIELDS", "STATE_FIELDS")})
    exec(compile(module, "<original records fixture>", "exec"), namespace)
    return namespace["OriginalRecords"]


class StorageRecordsPreparationTests(unittest.TestCase):
    def setUp(self):
        self.original = original_harness()
        self.proposed = type("StagedRecords", (StorageRecordsMixin, self.original), {})

    def storage(self, kind):
        s = kind()
        s.connection = sqlite3.connect(":memory:", isolation_level=None)
        s.connection.row_factory = sqlite3.Row
        self.addCleanup(s.connection.close)
        s.connection.execute("PRAGMA foreign_keys=ON")
        s._create_schema()
        s.connection.execute("PRAGMA user_version=3")
        s.connection.execute("INSERT INTO campaigns(id,name,created) VALUES (1,'Fixture','now')")
        s.connection.execute("INSERT INTO character_rosters(id,campaign_id) VALUES (1,1)")
        s.connection.execute("INSERT INTO encounters(id) VALUES (1)")
        s.connection.execute("INSERT INTO battle_setups(id,campaign_id,name,encounter_id,updated_at) VALUES (1,1,'saved',1,0)")
        return s

    def test_method_ast_and_signatures(self):
        tree = ast.parse((ROOT / "python/scrying_glass_storage_records.py").read_text(encoding="utf-8"))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        staged = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
        original = original_methods()
        self.assertEqual(set(staged), set(METHODS))
        for name in METHODS:
            self.assertEqual(ast.dump(staged[name], include_attributes=False),
                             ast.dump(original[name], include_attributes=False), name)
            self.assertEqual(inspect.signature(getattr(StorageRecordsMixin, name)),
                             inspect.signature(getattr(self.original, name)))
        self.assertIsInstance(inspect.getattr_static(StorageRecordsMixin, "_typed"), staticmethod)

    def test_scalar_types_and_rejections(self):
        for kind in (self.original, self.proposed):
            for value, tag in ((None, 'null'), (True, 'boolean'), (2, 'integer'), (2.5, 'real'), ('x', 'text')):
                self.assertEqual(kind._typed(value)[0], tag)
            for value in ([], {}, float('nan'), float('inf')):
                with self.assertRaises(ValueError):
                    kind._typed(value)

    def test_entity_presence_ids_order_and_deletion(self):
        for kind in (self.original, self.proposed):
            s = self.storage(kind)
            for table, owner in (('monsters', 'encounter_id'), ('characters', 'roster_id')):
                items = [{'id': 'a', 'name': 'A', 'hp': 7, 'flag': True, 'ratio': 2.5},
                         {'id': 'b', 'hp': None, 'note': None}]
                s._save_entities(table, owner, 1, items)
                self.assertEqual(s._load_entities(table, owner, 1), items)
                ids = list(s.connection.execute(f'SELECT id,combatant_id FROM {table} ORDER BY id'))
                items.reverse()
                s._save_entities(table, owner, 1, items)
                self.assertEqual(list(s.connection.execute(f'SELECT id,combatant_id FROM {table} ORDER BY id')), ids)
                self.assertEqual(s._load_entities(table, owner, 1), items)
                s._save_entities(table, owner, 1, [items[0]])
                self.assertEqual(s._load_entities(table, owner, 1), [items[0]])
            self.assertEqual(list(s.connection.execute('PRAGMA foreign_key_check')), [])

    def test_log_presence_identity_and_updates(self):
        for kind in (self.original, self.proposed):
            s = self.storage(kind)
            items = [{'id': 'e', 'action': 'damage', 'amount': 2, 'note': None}, {'id': 'f', 'amount': None}]
            s._save_log(1, items)
            self.assertEqual(s._load_log(1), items)
            ident = s.connection.execute("SELECT id FROM activity_log_entries WHERE event_id='e'").fetchone()[0]
            items[0]['amount'] = 3
            s._save_log(1, items[:1])
            self.assertEqual(s._load_log(1), items[:1])
            self.assertEqual(s.connection.execute("SELECT id FROM activity_log_entries WHERE event_id='e'").fetchone()[0], ident)

    def test_repeated_ordered_ids_keep_occurrence_identity(self):
        for kind in (self.original, self.proposed):
            s = self.storage(kind)
            s._save_lists(1, {'battle_order': ['a', 'a', 'b']})
            query = 'SELECT id,list_kind,combatant_id,occurrence FROM ordered_combatants ORDER BY id'
            before = list(s.connection.execute(query))
            s._save_lists(1, {'battle_order': ['b', 'a', 'a']})
            self.assertEqual(list(s.connection.execute(query)), before)
            self.assertEqual(s._load_encounter(1)['battle_order'], ['b', 'a', 'a'])
            s._save_lists(1, {'battle_order': ['b']})
            self.assertEqual(s._load_encounter(1)['battle_order'], ['b'])

    def test_runtime_reference_marker_and_roundtrip_parity(self):
        outputs = []
        for kind in (self.original, self.proposed):
            s = self.storage(kind)
            state = {'monsters': [{'id': 'a', 'hp': 7}], 'battle_order': ['a'],
                     'active_setup': {'campaign_id': '1', 'name': 'saved'},
                     'active_turn_id': None, 'battle_round': 3,
                     'display': {'background': '#123456', 'battle_order_font_size': 24}}
            before = copy.deepcopy(state)
            with s.transaction():
                s._save_encounter(1, state, runtime=True)
            loaded = s._load_encounter(1)
            self.assertEqual(state, before)
            for key, value in state.items():
                self.assertEqual(loaded[key], value)
            self.assertFalse(loaded['has_lair'])
            self.assertEqual(loaded['lairs'], [])
            outputs.append(loaded)
            del state['active_turn_id']
            s._save_encounter(1, state, runtime=True)
            self.assertNotIn('active_turn_id', s._load_encounter(1))
        self.assertEqual(outputs[0], outputs[1])

    def test_partial_write_rollback_and_validation(self):
        for kind in (self.original, self.proposed):
            s = self.storage(kind)
            before = list(s.connection.iterdump())
            with self.assertRaises(ValueError):
                with s.transaction():
                    s._save_entities('monsters', 'encounter_id', 1, [{'id': 'a', 'hp': 4}, {'id': 'b', 'hp': True}])
            self.assertEqual(list(s.connection.iterdump()), before)
            self.assertFalse(s.connection.in_transaction)
            for state in ({'unknown': True}, {'characters': [{'id': 'x'}]}, {'battle_round': -1},
                          {'display': {'unknown': 1}}, {'active_turn_id': 4}):
                with self.assertRaises(ValueError):
                    s._save_encounter(1, state)
            self.assertEqual(list(s.connection.iterdump()), before)

    def test_size_top_level_dependencies_and_original_blob(self):
        data = (ROOT / 'python/scrying_glass_storage_records.py').read_bytes()
        self.assertLessEqual(len(data), 20000)
        tree = ast.parse(data.decode())
        self.assertEqual([n.module for n in tree.body if isinstance(n, ast.ImportFrom)], ['scrying_glass_storage_fields'])
        self.assertEqual([a.name for n in tree.body if isinstance(n, ast.Import) for a in n.names], ['uuid'])
        self.assertNotIn('__init__', vars(StorageRecordsMixin))
        original = (ROOT / 'python/scrying_glass_storage.py').read_bytes()
        digest = hashlib.sha1(b'blob ' + str(len(original)).encode() + b'\0' + original).hexdigest()
        self.assertEqual(digest, 'ea80b59cca80c6885f6ba1ba4d32b759beb187b5')


if __name__ == '__main__':
    unittest.main()
