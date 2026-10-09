"""Check SQLite initialization cleanup and explicit closure during the test suite."""
import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from python.scrying_glass_storage import SQLiteStorage


def main() -> int:
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
            suite = unittest.defaultTestLoader.discover(str(REPOSITORY_ROOT / "tests"))
            result = unittest.TextTestRunner(verbosity=0).run(suite)
        leaks = [connection for connection in opened if not connection.closed_explicitly]
        print(f"Connections opened: {len(opened)}; without explicit close: {len(leaks)}")
        if not result.wasSuccessful() or leaks:
            return 1
        print("PASS: failed PRAGMA initialization closes connection; suite closes all tracked connections")
        return 0
    finally:
        for connection in opened:
            if not connection.closed_explicitly:
                connection.close()


if __name__ == "__main__":
    raise SystemExit(main())

