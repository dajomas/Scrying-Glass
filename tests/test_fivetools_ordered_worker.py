"""04c.2c real ordered subprocess integration and enforcement checks."""
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
from unittest.mock import patch
from python import scrying_glass_fivetools_worker as worker
from python.scrying_glass_fivetools_resolution import Identity, Limits, DatasetLoader, ResolutionError
from python.scrying_glass_fivetools_ordered_resolution import OrderedResolver

def mod(mode, **values):
    return dict(mode=mode, **values)

def records(ops=None, template=None):
    a, b, t = [Identity('root', k, 'MM', n) for k, n in [('monster', 'A'), ('monster', 'B'), ('monsterTemplate', 'T')]]
    meta = dict(name='B', source='MM', _mod=ops or {})
    if template is not None:
        meta['_templates'] = [dict(name='T', source='MM')]
    rows = [(a, dict(name='A', source='MM', _copy=meta)), (b, dict(name='B', source='MM', trait=['base'], label='base'))]
    if template is not None:
        rows.append((t, dict(name='T', source='MM', apply={'_mod': template})))
    return a, tuple((i, json.dumps(r).encode()) for i, r in rows)

class WorkerBoundaryContracts(unittest.TestCase):
    def test_unsupported_and_expired_work_do_not_spawn(self):
        a, rows = records()
        with patch.object(worker.subprocess, 'Popen') as start:
            with patch.object(worker.sys, 'platform', 'unsupported'):
                with self.assertRaisesRegex(worker.WorkerError, 'worker_enforcement_unavailable'):
                    worker.resolve_ordered_isolated(a, rows, deadline=time.monotonic()+3)
            with self.assertRaisesRegex(worker.WorkerError, '^deadline$'):
                worker.resolve_ordered_isolated(a, rows, deadline=time.monotonic()-1)
            start.assert_not_called()

@unittest.skipUnless(sys.platform == 'linux' and any(os.access(p, os.X_OK) for p in ('/usr/bin/prlimit', '/bin/prlimit')), 'Linux system prlimit required')
class OrderedWorkerTests(unittest.TestCase):
    def run_ordered(self, ops=None, template=None, **kwargs):
        a, rows = records(ops, template)
        return worker.resolve_ordered_isolated(a, rows, deadline=time.monotonic()+5, **kwargs)
    def test_complete_pipeline_matches_direct_graph_and_all_six_modes(self):
        ops = {'label': [mod('appendStr', str='!'), mod('prefixSuffixStringProp', prefix='[', suffix=']')], 'trait': ['remove', mod('appendArr', items=['end']), mod('prependArr', items=['start'])], '_': mod('setProp', prop='extra.value', value=3)}
        a, rows = records(ops)
        expected = OrderedResolver(DatasetLoader('root', rows), limits=Limits(modification_operations=6)).resolve(a, deadline=time.monotonic()+5)
        actual = self.run_ordered(ops, limits=Limits(modification_operations=6))
        self.assertEqual(actual, expected); self.assertEqual(list(actual.record()), list(expected.record()))
        self.assertEqual(actual.record()['trait'], ['start', 'end']); self.assertEqual(actual.modification_operations, 6)
    def test_legacy_worker_and_plain_ordered_mode_are_compatible(self):
        a, rows = records()
        first = worker.resolve_isolated(a, rows, deadline=time.monotonic()+5)
        self.assertEqual(first, self.run_ordered())
        a, rows = records({'trait': 'remove'})
        with self.assertRaises(ResolutionError) as caught:
            worker.resolve_isolated(a, rows, deadline=time.monotonic()+5)
        self.assertEqual(caught.exception.diagnostic.code, 'modification_execution_pending_04c')
        self.assertNotIn('trait', self.run_ordered({'trait': 'remove'}).record())
    def test_template_groups_and_diagnostics_survive_transport(self):
        out = self.run_ordered({'_': mod('setProp', prop='label', value='tail')}, {'label': mod('appendStr', str='template')})
        self.assertEqual(out.record()['label'], 'tail')
        with self.assertRaises(ResolutionError) as caught:
            self.run_ordered({'trait': mod('appendArr', items=['s'])}, {'trait': mod('appendArr')})
        d = caught.exception.diagnostic
        self.assertEqual([i.name for i in d.chain], ['A', 'T'])
        self.assertEqual((d.selected.name, d.property, d.operation_index, d.mode, d.source_path), ('A', 'trait', 1, 'appendArr', '$/apply/_mod/trait'))
    def test_resource_budgets_and_dynamic_content_fail_without_success(self):
        for limits, code in [(Limits(modification_operations=1), 'modification_operations_limit'), (Limits(intermediate_creature_bytes=1), 'intermediate_creature_bytes_limit')]:
            with self.assertRaises(ResolutionError) as caught:
                self.run_ordered({'trait': ['remove', mod('appendArr', items=[])]}, limits=limits)
            self.assertEqual(caught.exception.diagnostic.code, code)
        with self.assertRaises(ResolutionError) as caught:
            self.run_ordered({'_': mod('setProp', prop='extra', value='<$name$>')})
        self.assertEqual(caught.exception.diagnostic.code, 'dynamic_substitution_pending_04d')
    def test_new_job_and_returned_content_are_independent(self):
        ops = {'trait': mod('appendArr', items=[{'name': 'new'}])}
        first = self.run_ordered(ops); first.record()['trait'].append('changed')
        self.assertEqual(self.run_ordered(ops).record()['trait'], ['base', {'name': 'new'}])
        self.assertEqual(ops['trait']['items'], [{'name': 'new'}])
    def fixture(self, root, addition='', worker_addition=''):
        package = Path(root)/'python'; package.mkdir(); (package/'__init__.py').write_text('')
        original = Path(worker.__file__).resolve().parent
        for name in ('worker', 'resolution', 'resolution_bounds', 'ordered_resolution', 'modifications'):
            filename = 'scrying_glass_fivetools_'+name+'.py'
            shutil.copyfile(original/filename, package/filename)
        with (package/'scrying_glass_fivetools_ordered_resolution.py').open('a') as stream:
            stream.write(addition)
        with (package/'scrying_glass_fivetools_worker.py').open('a') as stream:
            stream.write(worker_addition)
        return str(package/'scrying_glass_fivetools_worker.py')
    def test_real_kernel_allocation_refusal_and_recovery(self):
        with tempfile.TemporaryDirectory() as root:
            addition = '\ndef _memory(self, *args, **kwargs):\n    return bytearray(128*1024*1024)\nOrderedResolver._apply_compiled_modifications = _memory\n'
            path = self.fixture(root, addition)
            with patch.object(worker, '__file__', path):
                with self.assertRaisesRegex(worker.WorkerError, '^worker_memory_limit$'):
                    self.run_ordered({'trait': 'remove'}, worker_memory_bytes=64*1024*1024)
        self.assertNotIn('trait', self.run_ordered({'trait': 'remove'}).record())
    def test_unverified_child_enforcement_and_mode_downgrade_fail_closed(self):
        additions = [("\ndef _memory_guard(cap):\n    raise WorkerError('worker_enforcement_unavailable')\n", 'worker_enforcement_unavailable'),
                     ("\ndef _child():\n    sys.stdout.write('{\\\"ordered\\\":false}')\n", 'worker_protocol_error')]
        for addition, code in additions:
            with tempfile.TemporaryDirectory() as root:
                path = self.fixture(root, worker_addition=addition)
                with patch.object(worker, '__file__', path):
                    with self.assertRaisesRegex(worker.WorkerError, '^'+code+'$'):
                        self.run_ordered({'trait': 'remove'})
    def test_noncooperative_deadline_kills_and_reaps_ordered_worker(self):
        self.blocked(False)
    def test_inflight_cancellation_kills_and_reaps_ordered_worker(self):
        self.blocked(True)
    def blocked(self, cancelled):
        with tempfile.TemporaryDirectory() as root:
            marker = Path(root)/'started'
            addition = '\ndef _blocked(self, *args, **kwargs):\n    from pathlib import Path\n    Path(%r).write_text("ready")\n    while True: pass\nOrderedResolver._apply_compiled_modifications = _blocked\n' % str(marker)
            path = self.fixture(root, addition); processes = []; original = subprocess.Popen
            def start(*args, **kwargs):
                process = original(*args, **kwargs); processes.append(process); return process
            a, rows = records({'trait': 'remove'}); before = time.monotonic()
            with patch.object(worker, '__file__', path), patch.object(worker.subprocess, 'Popen', side_effect=start):
                with self.assertRaisesRegex(worker.WorkerError, '^'+('cancelled' if cancelled else 'deadline')+'$'):
                    worker.resolve_ordered_isolated(a, rows, deadline=before+1.5, cancelled=lambda: cancelled and marker.exists())
            self.assertTrue(marker.exists()); self.assertEqual(len(processes), 1)
            self.assertEqual(processes[0].returncode, -signal.SIGKILL)
            self.assertLess(time.monotonic()-before, 3)
            with self.assertRaises(ChildProcessError):
                os.waitpid(processes[0].pid, os.WNOHANG)

if __name__ == '__main__':
    unittest.main()
