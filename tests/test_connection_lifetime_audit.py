"""Regression coverage for audit process isolation and explicit SQLite closure."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest
from unittest.mock import patch

AUDIT = Path(__file__).with_name("audit_connection_lifetime.py")


class ConnectionLifetimeAuditTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)

    def write(self, name, source):
        (self.directory / name).write_text(textwrap.dedent(source), encoding="utf-8")

    def execute(self, function, pattern="test*.py"):
        code = (
            "import importlib.util,sys; from pathlib import Path; "
            "s=importlib.util.spec_from_file_location('audit',sys.argv[1]); "
            "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
            "raise SystemExit(m." + function + "(Path(sys.argv[2])"
            + (",sys.argv[3]" if function == "run_suite" else "") + "))"
        )
        return subprocess.run([sys.executable, "-c", code, str(AUDIT), str(self.directory), pattern],
                              capture_output=True, text=True, timeout=30)

    def test_sync_and_async_connections_are_tracked_and_closed(self):
        self.write("test_sync.py", """
            import sqlite3, unittest
            class Sync(unittest.TestCase):
                def test_close(self):
                    c = sqlite3.connect(':memory:')
                    c.close()
        """)
        self.write("test_async.py", """
            import asyncio, sqlite3, unittest
            class Async(unittest.IsolatedAsyncioTestCase):
                async def test_close(self):
                    c = sqlite3.connect(':memory:')
                    try:
                        await asyncio.sleep(0)
                        self.assertEqual(c.execute('SELECT 1').fetchone()[0], 1)
                    finally:
                        c.close()
        """)
        result = self.execute("run_modules")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.count('connections opened: 1; without explicit close: 0'), 2)
        self.assertIn('modules: 2; failed: 0', result.stdout)

    def test_connection_opened_during_import_is_not_missed(self):
        self.write("test_import_leak.py", """
            import sqlite3, unittest
            leaked = sqlite3.connect(':memory:')
            class ImportLeak(unittest.TestCase):
                def test_ok(self):
                    pass
        """)
        result = self.execute("run_modules")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('connections opened: 1; without explicit close: 1', result.stdout)

    def test_test_body_leak_fails_even_when_unittest_passes(self):
        self.write("test_leak.py", """
            import sqlite3, unittest
            class Leak(unittest.TestCase):
                def test_leak(self):
                    self.connection = sqlite3.connect(':memory:')
        """)
        result = self.execute("run_modules")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('without explicit close: 1', result.stdout)
        self.assertNotIn('PASS: all audited', result.stdout)

    def test_failed_setup_loop_cannot_contaminate_next_async_module(self):
        self.write("test_a_failed_setup.py", """
            import asyncio, unittest
            from asyncio import events
            class FailedSetup(unittest.TestCase):
                @classmethod
                def setUpClass(cls):
                    cls.loop = asyncio.new_event_loop()
                    events._set_running_loop(cls.loop)
                    raise RuntimeError('injected browser launch failure')
                def test_unreachable(self):
                    raise AssertionError('setup should fail')
        """)
        self.write("test_b_async.py", """
            import asyncio, sqlite3, unittest
            class Async(unittest.IsolatedAsyncioTestCase):
                async def test_async(self):
                    await asyncio.sleep(0)
                    c = sqlite3.connect(':memory:')
                    c.close()
                    print('ASYNC MODULE COMPLETED', flush=True)
        """)
        baseline = self.execute("run_suite")
        self.assertNotEqual(baseline.returncode, 0)
        self.assertIn('Cannot run the event loop while another loop is running', baseline.stderr)
        isolated = self.execute("run_modules")
        self.assertEqual(isolated.returncode, 1, isolated.stdout + isolated.stderr)
        self.assertIn('injected browser launch failure', isolated.stderr)
        self.assertIn('ASYNC MODULE COMPLETED', isolated.stdout)
        self.assertIn('connections opened: 1; without explicit close: 0', isolated.stdout)
        self.assertIn('modules: 2; failed: 1', isolated.stdout)
        self.assertNotIn('Cannot run the event loop while another loop is running', isolated.stderr)
        self.assertNotIn('was never awaited', isolated.stderr)

    def test_import_error_is_failure_and_later_module_still_runs(self):
        self.write("test_a_import.py", "raise RuntimeError('injected import failure')\n")
        self.write("test_b_ok.py", """
            import unittest
            class Good(unittest.TestCase):
                def test_ok(self):
                    print('LATER MODULE COMPLETED', flush=True)
        """)
        result = self.execute("run_modules")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn('injected import failure', result.stderr)
        self.assertIn('LATER MODULE COMPLETED', result.stdout)
        self.assertIn('modules: 2; failed: 1', result.stdout)

    def test_initialization_probe_precedes_workers_and_worker_status_propagates(self):
        spec = importlib.util.spec_from_file_location('audit_under_test', AUDIT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        order = []
        with patch.object(module, 'check_failed_initialization', side_effect=lambda: order.append('probe')), \
             patch.object(module, 'run_modules', side_effect=lambda path: order.append('workers') or 1):
            self.assertEqual(module.main([]), 1)
        self.assertEqual(order, ['probe', 'workers'])
        with patch.object(module, 'check_failed_initialization', side_effect=AssertionError('probe failed')), \
             patch.object(module, 'run_modules') as workers:
            with self.assertRaisesRegex(AssertionError, 'probe failed'):
                module.main([])
            workers.assert_not_called()

    def test_empty_inventory_is_not_a_success(self):
        result = self.execute('run_modules')
        self.assertEqual(result.returncode, 1)
        self.assertIn('No unittest modules found', result.stderr)


if __name__ == '__main__':
    unittest.main()
