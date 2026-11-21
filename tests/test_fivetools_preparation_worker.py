"""022.04f isolated preparation worker: RPC dataset access, limits and fail-closed transport."""
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from python import scrying_glass_fivetools_preparation_worker as worker
from python.scrying_glass_fivetools_fetch import FetchError
from python.scrying_glass_fivetools_preparation import PreparationError, prepare_statblock
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_fivetools_preparation import Fetcher, dataset  # noqa: E402

LINUX = sys.platform == 'linux' and any(Path(p).exists() for p in ('/usr/bin/prlimit', '/bin/prlimit'))


def parent_fetch(files=None):
    source = Fetcher(files)
    def fetch(path, deadline):
        try:
            return source(path)
        except LookupError:
            raise FetchError('not_found') from None
    return fetch


@unittest.skipUnless(LINUX, 'isolated preparation needs Linux prlimit enforcement')
class PreparationWorkerTests(unittest.TestCase):
    def run_worker(self, name='Grave Wight', **kwargs):
        kwargs.setdefault('fetch', parent_fetch())
        return worker.prepare_isolated(name, 'TST', deadline=time.monotonic() + 20, **kwargs)

    def test_isolated_result_matches_in_process_preparation(self):
        snapshot, measurements = self.run_worker('Grave Wight Elder')
        expected = prepare_statblock('Grave Wight Elder', 'TST', fetch=Fetcher(), deadline=time.monotonic() + 20)
        self.assertEqual(snapshot, expected.snapshot)
        self.assertEqual(measurements, expected.measurements)

    def test_errors_and_missing_files_cross_the_boundary(self):
        with self.assertRaises(PreparationError) as caught:
            self.run_worker('Nope')
        self.assertEqual(caught.exception.code, 'selected_unavailable')
        files = dataset()
        del files['variantrules.json']
        snapshot, _ = self.run_worker(fetch=parent_fetch(files))
        self.assertEqual(snapshot['completeness'], 'partial')
        self.assertIn('reference_unavailable', [w['code'] for w in snapshot['warnings']])

    def fixture(self, root, addition):
        package = Path(root) / 'python'
        package.mkdir()
        (package / '__init__.py').write_text('')
        original = Path(worker.__file__).resolve().parent
        for source in original.glob('scrying_glass_*.py'):
            shutil.copyfile(source, package / source.name)
        with (package / 'scrying_glass_fivetools_preparation_worker.py').open('a') as stream:
            stream.write(addition)
        return str(package / 'scrying_glass_fivetools_preparation_worker.py')

    def tampered(self, addition, **kwargs):
        with tempfile.TemporaryDirectory() as root:
            path = self.fixture(root, addition)
            processes, original = [], subprocess.Popen
            def start(*args, **kw):
                process = original(*args, **kw)
                processes.append(process)
                return process
            with patch.object(worker, '__file__', path), patch.object(worker.subprocess, 'Popen', side_effect=start):
                try:
                    return self.run_worker(**kwargs)
                finally:
                    for process in processes:
                        self.assertIsNotNone(process.returncode)

    def test_child_cannot_request_unlisted_paths(self):
        addition = "\ndef _child():\n    sys.stdout.buffer.write(b'{\"fetch\": \"../secret\"}\\n'); sys.stdout.buffer.flush(); sys.stdin.buffer.read()\n"
        with self.assertRaisesRegex(worker.WorkerError, '^worker_protocol_error$'):
            self.tampered(addition)

    def test_noncooperative_child_is_killed_at_the_deadline(self):
        addition = "\ndef _child():\n    while True: pass\n"
        started = time.monotonic()
        with tempfile.TemporaryDirectory() as root:
            path = self.fixture(root, addition)
            with patch.object(worker, '__file__', path):
                with self.assertRaisesRegex(worker.WorkerError, '^deadline$'):
                    worker.prepare_isolated('Grave Wight', 'TST', fetch=parent_fetch(), deadline=time.monotonic() + 1.5)
        self.assertLess(time.monotonic() - started, 4)

    def test_cancellation_and_memory_limit(self):
        with self.assertRaisesRegex(worker.WorkerError, '^cancelled$'):
            self.run_worker(cancelled=lambda: True)
        addition = "\n_original_child = _child\ndef _child():\n    _memory_guard(int(sys.argv[2]))\n    try:\n        bytearray(128*1024*1024)\n    except MemoryError:\n        _safe_emit(sys.stdout.buffer, {'worker_error': 'worker_memory_limit'})\n"
        with self.assertRaisesRegex(worker.WorkerError, '^worker_memory_limit$'):
            self.tampered(addition, worker_memory_bytes=64 * 1024 * 1024)


if __name__ == '__main__':
    unittest.main()
