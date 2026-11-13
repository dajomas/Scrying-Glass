"""Audit SQLite closure in isolated unittest modules, including async/browser tests."""
import argparse
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))


def check_failed_initialization():
    from python.scrying_glass_storage import SQLiteStorage

    class FailingConnection:
        row_factory = None
        closed = False

        def execute(self, sql):
            raise sqlite3.OperationalError("injected PRAGMA failure")

        def close(self):
            self.closed = True

    failed_connection = FailingConnection()
    with patch("python.scrying_glass_storage.sqlite3.connect", return_value=failed_connection):
        try:
            SQLiteStorage(REPOSITORY_ROOT / "injected.sqlite3")
        except sqlite3.OperationalError:
            pass
        else:
            raise AssertionError("The injected initialization failure was not propagated")
    if not failed_connection.closed:
        raise AssertionError("Failed initialization did not close its connection")


def run_suite(test_directory, pattern):
    original_connect = sqlite3.connect
    opened = []

    class TrackedConnection(sqlite3.Connection):
        closed_explicitly = False

        def close(self):
            super().close()
            self.closed_explicitly = True

    def connect(*args, **kwargs):
        kwargs["factory"] = TrackedConnection
        connection = original_connect(*args, **kwargs)
        opened.append(connection)
        return connection

    try:
        with patch("sqlite3.connect", side_effect=connect):
            suite = unittest.defaultTestLoader.discover(str(test_directory), pattern=pattern)
            result = unittest.TextTestRunner(verbosity=0).run(suite)
        leaks = [connection for connection in opened if not connection.closed_explicitly]
        print(f"{pattern}: connections opened: {len(opened)}; without explicit close: {len(leaks)}", flush=True)
        if not result.wasSuccessful() or leaks:
            return 1
        return 0
    finally:
        for connection in opened:
            if not connection.closed_explicitly:
                connection.close()


def run_modules(test_directory):
    test_directory = Path(test_directory).resolve()
    modules = sorted(test_directory.glob("test*.py"))
    if not modules:
        print(f"No unittest modules found in {test_directory}", file=sys.stderr)
        return 1
    failed = 0
    for module in modules:
        print(f"Connection audit: {module.name}", flush=True)
        # Discovery, imports, fixtures and SQLite tracking all run in the worker.
        # A failed browser setup cannot leave a loop active in the next module.
        result = subprocess.run([
            sys.executable, str(Path(__file__).resolve()),
            "--tests-dir", str(test_directory), "--test-file", module.name,
        ], cwd=REPOSITORY_ROOT)
        if result.returncode:
            failed += 1
            print(f"FAIL: {module.name} (exit {result.returncode})", flush=True)
    print(f"Connection audit modules: {len(modules)}; failed: {failed}", flush=True)
    if failed:
        return 1
    print("PASS: all audited modules passed and closed their tracked connections", flush=True)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tests-dir", type=Path, default=REPOSITORY_ROOT / "tests")
    parser.add_argument("--test-file")
    args = parser.parse_args(argv)
    if args.test_file:
        if Path(args.test_file).name != args.test_file or not args.test_file.startswith("test") or not args.test_file.endswith(".py"):
            parser.error("--test-file must be a unittest module filename")
        return run_suite(args.tests_dir.resolve(), args.test_file)
    check_failed_initialization()
    return run_modules(args.tests_dir)


if __name__ == "__main__":
    raise SystemExit(main())
