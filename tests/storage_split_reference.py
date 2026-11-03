"""Test-only original-AST oracle; fingerprints come from monolith blob ea80b59.

No production source assembly: only tests build a pinned reference class.
"""
import __future__
import ast
import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import time
import uuid
from contextlib import contextmanager, closing
from python.scrying_glass_identity_rules import validate_roster_setup_ids

ROOT = Path(__file__).resolve().parents[1]
METHOD_NAMES = ('__init__', 'transaction', 'close', '_check_foreign_keys', '_backup', '_create_schema', '_typed', '_attributes', '_read_attributes', '_save_entities', '_load_entities', '_save_log', '_load_log', '_save_lists', '_save_encounter', '_load_encounter', 'create_campaign', '_campaign_metadata', 'read_campaigns', 'write_campaigns', 'update_campaign', 'campaign_exists', 'campaign_name_exists', 'load_characters', 'save_characters', 'list_setups', 'setup_exists', 'load_setup', 'save_setup', 'rename_setup', 'delete_setup', 'unique_setup_name', 'transfer_setup', 'newest_setup', 'get_value', 'set_value', 'convert_campaign_references', '_upgrade')
METHOD_PIN = 'b14c103b80c2c084413c83017206977fdfc47bbf0e7943f7fe3595f083c39d00'
FIELD_PIN = "063001ad08bedc2ce2a57f37483b383ad5ed212a85b2f5461ff45b4db0642f23"


def canonical(node):
    return ast.dump(node, include_attributes=False).replace(', type_params=[]', '')


def field_nodes():
    tree = ast.parse((ROOT/'python/scrying_glass_storage_fields.py').read_text(encoding='utf-8'))
    nodes = [n for n in tree.body if isinstance(n, ast.Assign)]
    digest = hashlib.sha256('\n'.join(canonical(n) for n in nodes).encode()).hexdigest()
    if digest != FIELD_PIN:
        raise AssertionError('Original field expressions changed')
    return nodes


def reference_methods():
    result = {}
    for suffix, count in (('', 5), ('_schema', 3), ('_records', 10), ('_operations', 20)):
        tree = ast.parse((ROOT/f'python/scrying_glass_storage{suffix}.py').read_text(encoding='utf-8'))
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef))
        nodes = [n for n in cls.body if isinstance(n, ast.FunctionDef)]
        if len(nodes) != count:
            raise AssertionError(f'Unexpected method count: {suffix}')
        for node in nodes:
            if node.name in result or node.name not in METHOD_NAMES:
                raise AssertionError(f'Original method changed: {node.name}')
            result[node.name] = node
    if set(result) != set(METHOD_NAMES):
        raise AssertionError('Incomplete original method surface')
    digest = hashlib.sha256('\n'.join(n+':'+canonical(result[n]) for n in sorted(result)).encode()).hexdigest()
    if digest != METHOD_PIN:
        raise AssertionError('Original method bodies/signatures/decorators changed')
    field_nodes()
    return result


def reference_class():
    cls = ast.ClassDef(name='OriginalStorage', bases=[], keywords=[], decorator_list=[],
                      body=[ast.parse('SCHEMA_VERSION = 8').body[0], *reference_methods().values()])
    module = ast.fix_missing_locations(ast.Module(body=[*field_nodes(), cls], type_ignores=[]))
    namespace = dict(copy=copy, json=json, sqlite3=sqlite3, time=time, uuid=uuid, Path=Path,
                     contextmanager=contextmanager, closing=closing,
                     validate_roster_setup_ids=validate_roster_setup_ids,
                     __name__='python._original_storage_fixture', __package__='python')
    exec(compile(module, '<pinned original storage AST>', 'exec', flags=__future__.annotations.compiler_flag), namespace)
    return namespace['OriginalStorage']


def base_storage(test, kind):
    value = object.__new__(kind)
    value.connection = sqlite3.connect(':memory:', isolation_level=None)
    value.connection.row_factory = sqlite3.Row
    test.addCleanup(value.close)
    value.connection.execute('PRAGMA foreign_keys=ON')
    value._create_schema()
    value.connection.execute('PRAGMA user_version=3')
    value.migration_backup = Path('fixture.backup')
    return value
