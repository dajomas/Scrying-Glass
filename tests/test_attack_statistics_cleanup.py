"""Run the actual backup-test method with real SQLite and explicit-close tracking.

The method is AST-extracted to avoid importing unrelated test fixtures. A tiny
storage fixture creates exactly the tables needed by this resource-lifetime check;
this is not a replacement for the real migration or full connection audit.
"""
import ast
import sqlite3
import tempfile
import types
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

SOURCE = Path(__file__).with_name('test_attack_statistics.py')


def backup_test_method():
    tree = ast.parse(SOURCE.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'AttackStatisticsTests')
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == 'test_v7_backup')
    namespace = dict(sqlite3=sqlite3, closing=closing)
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace['test_v7_backup']


class BackupConnectionCleanupTests(unittest.TestCase):
    def exercise(self, fail_assertion=False):
        opened = []
        connect = sqlite3.connect
        class TrackedConnection(sqlite3.Connection):
            closed_explicitly = False
            def close(self):
                super().close()
                self.closed_explicitly = True
        def tracked_connect(*args, **kwargs):
            kwargs['factory'] = TrackedConnection
            connection = connect(*args, **kwargs)
            opened.append(connection)
            return connection
        class MinimalStorage:
            def __init__(self, path):
                self.connection = sqlite3.connect(path)
                self.migration_backup = path.with_suffix('.backup.sqlite3')
                if self.connection.execute('PRAGMA user_version').fetchone()[0] == 7:
                    with closing(sqlite3.connect(self.migration_backup)) as backup:
                        self.connection.backup(backup)
                    for table in ('characters', 'monsters', 'snapshot_characters'):
                        for column in ('mechanical_version', 'reduction_stat', 'reduction_amount'):
                            self.connection.execute(f'ALTER TABLE {table}_effects ADD COLUMN {column} INTEGER')
                else:
                    for table in ('characters', 'monsters', 'snapshot_characters'):
                        self.connection.execute(f'CREATE TABLE {table}_effects (id INTEGER, mechanical_version INTEGER, reduction_stat TEXT, reduction_amount INTEGER)')
                self.connection.execute('PRAGMA user_version=8')
                self.connection.commit()
            def close(self):
                self.connection.close()
        case = unittest.TestCase()
        if fail_assertion:
            def assert_equal(left, right):
                if right == 7:
                    raise AssertionError('injected backup assertion failure')
                unittest.TestCase().assertEqual(left, right)
            case.assertEqual = assert_equal
        try:
            with tempfile.TemporaryDirectory() as directory, patch('sqlite3.connect', side_effect=tracked_connect):
                initial = MinimalStorage(Path(directory) / 'initial.sqlite3')
                initial.close()
                case.c = types.SimpleNamespace(DATA_DIR=Path(directory), STORAGE=initial)
                try:
                    if fail_assertion:
                        with self.assertRaisesRegex(AssertionError, 'injected backup'):
                            backup_test_method()(case)
                    else:
                        backup_test_method()(case)
                    read_connections = [c for c in opened if not c.closed_explicitly]
                    # On assertion failure, the method's later db.close() is skipped;
                    # the final opened connection is the backup reader and must close.
                    self.assertTrue(opened[-1].closed_explicitly)
                    if not fail_assertion:
                        self.assertEqual(read_connections, [])
                finally:
                    for connection in opened:
                        if not connection.closed_explicitly:
                            connection.close()
        finally:
            for connection in opened:
                if not connection.closed_explicitly:
                    connection.close()

    def test_backup_reader_closes_after_success(self):
        self.exercise()

    def test_backup_reader_closes_after_assertion_failure(self):
        self.exercise(fail_assertion=True)


if __name__ == '__main__':
    unittest.main()
