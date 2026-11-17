"""Real Linux subprocess/resource tests plus fail-closed portable contracts."""
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from dataclasses import replace
from unittest.mock import patch
from python import scrying_glass_fivetools_worker as worker
from python.scrying_glass_fivetools_resolution import (
    Identity, Limits, Resolver, DatasetLoader, ResolutionError,
)

def wire(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode()

def supported():
    return sys.platform == 'linux' and any(os.access(p, os.X_OK) for p in ('/usr/bin/prlimit', '/bin/prlimit'))

class WorkerContracts(unittest.TestCase):
    def setUp(self):
        self.a = Identity('root', 'monster', 'MM', 'A')
        self.rows = ((self.a, wire({'name': 'A', 'source': 'MM'})),)
    def test_unsupported_platform_fails_closed_without_start(self):
        with patch.object(worker.sys, 'platform', 'unsupported'), patch.object(worker.subprocess, 'Popen') as start:
            with self.assertRaisesRegex(worker.WorkerError, 'worker_enforcement_unavailable'):
                worker.resolve_isolated(self.a, self.rows, deadline=time.monotonic()+3)
            start.assert_not_called()
    def test_missing_launcher_fails_closed(self):
        with patch.object(worker.os.path, 'isfile', return_value=False):
            with self.assertRaisesRegex(worker.WorkerError, 'worker_enforcement_unavailable'):
                worker._launcher()
    def test_invalid_configuration_and_expired_queued_work_never_spawn(self):
        with patch.object(worker.subprocess, 'Popen') as start:
            for memory in (True, 0, -1, 1.5, 2**63):
                with self.assertRaises(ValueError):
                    worker.resolve_isolated(self.a, self.rows, deadline=time.monotonic()+3, worker_memory_bytes=memory)
            for deadline in (True, float('nan'), float('inf')):
                with self.assertRaises(ValueError):
                    worker.resolve_isolated(self.a, self.rows, deadline=deadline)
            with self.assertRaisesRegex(worker.WorkerError, 'deadline'):
                worker.resolve_isolated(self.a, self.rows, deadline=time.monotonic()-1)
            with self.assertRaisesRegex(worker.WorkerError, 'cancelled'):
                worker.resolve_isolated(self.a, self.rows, deadline=time.monotonic()+3, cancelled=lambda: True)
            start.assert_not_called()
    def test_transport_utf8_equality_and_one_over(self):
        payload = {'é': '😀'}; size = len(wire(payload))+1
        for cap in (size-1, size):
            with tempfile.TemporaryFile() as stream:
                if cap < size:
                    with self.assertRaisesRegex(worker.WorkerError, 'worker_transport_limit'):
                        worker._write_json(stream, payload, cap, lambda: None)
                else:
                    worker._write_json(stream, payload, cap, lambda: None)
                    self.assertEqual(stream.tell(), size)

@unittest.skipUnless(supported(), 'Linux system prlimit required; preparation fails closed otherwise')
class IsolatedWorkerTests(unittest.TestCase):
    setUp = WorkerContracts.setUp
    def run_worker(self, rows=None, **kwargs):
        return worker.resolve_isolated(self.a, self.rows if rows is None else rows,
            deadline=time.monotonic()+5, **kwargs)
    def test_plain_result_and_independent_processes(self):
        with patch.object(worker.subprocess, 'Popen', wraps=subprocess.Popen) as start:
            first = self.run_worker(); second = self.run_worker()
        self.assertEqual(first.record(), {'name': 'A', 'source': 'MM'})
        self.assertEqual(first, second); self.assertEqual(start.call_count, 2)
        self.assertTrue(all(call.kwargs['start_new_session'] for call in start.call_args_list))
        first.record()['name'] = 'changed'
        self.assertEqual(second.record()['name'], 'A')
    def test_real_graph_matches_in_process_result_and_order(self):
        b = replace(self.a, source='XMM', name='B')
        t = replace(self.a, kind='monsterTemplate', name='T')
        rows = ((self.a, wire({'name': 'A', 'source': 'MM', 'trait': None,
            '_copy': {'name': 'B', 'source': 'XMM', '_templates': [{'name': 'T', 'source': 'MM'}]*2}})),
            (b, wire({'name': 'B', 'source': 'XMM', 'str': 8, 'trait': ['base']})),
            (t, wire({'name': 'T', 'source': 'MM', 'apply': {'_root': {'str': 18}}})))
        expected = Resolver(DatasetLoader('root', rows)).resolve(self.a, deadline=time.monotonic()+5)
        actual = self.run_worker(rows)
        self.assertEqual(actual, expected)
        self.assertEqual(list(actual.record()), list(expected.record()))
        self.assertEqual(actual.modification_operations, 1)
    def test_resolution_errors_preserve_identity_chain_and_mode(self):
        cases = [([], 'missing_dependency'), (list(self.rows)*2, 'ambiguous_dependency'),
            ([(self.a, wire({'name': 'A', 'source': 'MM', '_copy': {'name': 'A', 'source': 'MM'}}))], 'inheritance_cycle')]
        for rows, code in cases:
            with self.subTest(code=code), self.assertRaises(ResolutionError) as caught:
                self.run_worker(tuple(rows))
            self.assertEqual(caught.exception.diagnostic.code, code)
            self.assertEqual(caught.exception.diagnostic.selected, self.a)
        b = replace(self.a, name='B')
        rows = ((self.a, wire({'name': 'A', 'source': 'MM', '_copy': {'name': 'B', 'source': 'MM', '_mod': {'trait': 'remove'}}})),
                (b, wire({'name': 'B', 'source': 'MM'})))
        with self.assertRaises(ResolutionError) as caught:
            self.run_worker(rows)
        d = caught.exception.diagnostic
        self.assertEqual((d.code, d.property, d.operation_index, d.mode), ('modification_execution_pending_04c', 'trait', 0, 'remove'))
    def test_response_and_intermediate_limits_propagate(self):
        with self.assertRaisesRegex(worker.WorkerError, 'response_bytes_limit'):
            self.run_worker(limits=Limits(response_bytes=1))
        with self.assertRaises(ResolutionError) as caught:
            self.run_worker(limits=Limits(intermediate_creature_bytes=1))
        self.assertEqual(caught.exception.diagnostic.code, 'intermediate_creature_bytes_limit')
    def test_oversize_staging_and_start_failure(self):
        with patch.object(worker.subprocess, 'Popen') as start:
            with self.assertRaisesRegex(worker.WorkerError, 'worker_transport_limit'):
                self.run_worker(worker_memory_bytes=1)
            start.assert_not_called()
        with patch.object(worker.subprocess, 'Popen', side_effect=OSError('private detail')):
            with self.assertRaisesRegex(worker.WorkerError, '^worker_start_failed$'):
                self.run_worker()
    def fixture(self, root, addition):
        package = Path(root)/'python'; package.mkdir(); (package/'__init__.py').write_text('')
        original = Path(worker.__file__).resolve().parent
        for name in ('scrying_glass_fivetools_worker.py', 'scrying_glass_fivetools_resolution.py', 'scrying_glass_fivetools_resolution_bounds.py'):
            shutil.copyfile(original/name, package/name)
        with (package/'scrying_glass_fivetools_resolution.py').open('a') as stream:
            stream.write(addition)
        return str(package/'scrying_glass_fivetools_worker.py')
    def test_unverified_child_enforcement_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            path = self.fixture(root, '')
            with Path(path).open('a') as stream:
                stream.write("\ndef _memory_guard(cap):\n    raise WorkerError('worker_enforcement_unavailable')\n")
            with patch.object(worker, '__file__', path):
                with self.assertRaisesRegex(worker.WorkerError, '^worker_enforcement_unavailable$'):
                    self.run_worker()
    def test_kernel_memory_limit_rejects_real_allocation_and_next_job_recovers(self):
        with tempfile.TemporaryDirectory() as root:
            path = self.fixture(root,
                '\n' + 'def _resource_fixture(self, *args, **kwargs):\n    return bytearray(128*1024*1024)\nResolver.resolve = _resource_fixture\n'.replace('\\n', '\n'))
            with patch.object(worker, '__file__', path):
                with self.assertRaisesRegex(worker.WorkerError, '^worker_memory_limit$'):
                    self.run_worker(worker_memory_bytes=64*1024*1024)
        self.assertEqual(self.run_worker().record()['name'], 'A')
    def test_noncooperative_deadline_kills_and_reaps_process(self):
        self.blocked_job(False)
    def test_inflight_cancellation_kills_and_reaps_process(self):
        self.blocked_job(True)
    def blocked_job(self, cancel):
        with tempfile.TemporaryDirectory() as root:
            marker = Path(root)/'started'
            addition = '\n' + ('def _blocked(self, *args, **kwargs):\n    from pathlib import Path\n    Path(%r).write_text("ready")\n    while True: pass\nResolver.resolve = _blocked\n' % str(marker)).replace('\\n', '\n')
            path = self.fixture(root, addition)
            processes = []; original = subprocess.Popen
            def start(*args, **kwargs):
                process = original(*args, **kwargs); processes.append(process); return process
            before = time.monotonic()
            with patch.object(worker, '__file__', path), patch.object(worker.subprocess, 'Popen', side_effect=start):
                with self.assertRaisesRegex(worker.WorkerError, '^'+('cancelled' if cancel else 'deadline')+'$'):
                    worker.resolve_isolated(self.a, self.rows, deadline=before+1.5,
                        cancelled=lambda: cancel and marker.exists())
            self.assertTrue(marker.exists()); self.assertEqual(len(processes), 1)
            self.assertEqual(processes[0].returncode, -signal.SIGKILL)
            self.assertLess(time.monotonic()-before, 3)
            with self.assertRaises(ChildProcessError):
                os.waitpid(processes[0].pid, os.WNOHANG)

if __name__ == '__main__':
    unittest.main()
