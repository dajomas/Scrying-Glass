"""022.15 Windows worker limits (Job Object) and thread channel.

On every platform: the Job Object structure layout and limits, ``launch`` and
``guard_child`` against a fake kernel32, and the real 5e.tools and source
workers with the Windows ``ThreadChannel`` in place of the POSIX selector
channel (on Linux still bounded by prlimit). On Windows only: a real worker in a
real Job Object (run ``python -m unittest test_worker_windows`` from the tests
folder on the Windows machine that runs the server).
"""
import ctypes
import glob
import json
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from python import scrying_glass_fivetools_preparation_worker as prep_worker
from python import scrying_glass_statblock_worker as source_worker
from python import scrying_glass_worker_windows as win
from python.scrying_glass_fivetools_worker import WorkerError, _launcher, _start_worker
from python.scrying_glass_statblock_model import ModelLimits

ROOT = Path(__file__).resolve().parents[1]
LINUX = sys.platform == 'linux' and any(Path(p).exists() for p in ('/usr/bin/prlimit', '/bin/prlimit'))
WINDOWS = sys.platform == 'win32'


class FakeKernel32:
    def __init__(self, *, create=True, configure=True, assign=True, inside=True, limits=None):
        self.create, self.configure, self.assign, self.inside, self.limits = create, configure, assign, inside, limits
        self.calls, self.closed, self.stored = [], [], None

    def CreateJobObjectW(self, *args):
        self.calls.append('create')
        return 77 if self.create else None

    def SetInformationJobObject(self, job, klass, pointer, size):
        self.calls.append(('set', job, klass, size))
        self.stored = ctypes.cast(pointer, ctypes.POINTER(win.JOBOBJECT_EXTENDED_LIMIT_INFORMATION)).contents
        return self.configure

    def AssignProcessToJobObject(self, job, handle):
        self.calls.append(('assign', job, handle))
        return self.assign

    def CloseHandle(self, handle):
        self.closed.append(handle)
        return 1

    def GetCurrentProcess(self):
        return -1

    def IsProcessInJob(self, process, job, result):
        inside = self.inside() if callable(self.inside) else self.inside
        ctypes.cast(result, ctypes.POINTER(ctypes.c_int)).contents.value = int(inside)
        return 1

    def QueryInformationJobObject(self, job, klass, pointer, size, returned):
        if self.limits is None:
            return 0
        ctypes.memmove(pointer, ctypes.byref(self.limits), size)
        return 1


class FakeProcess:
    def __init__(self, command, **kwargs):
        self.command, self.kwargs, self._handle = command, kwargs, 4242
        self.killed, self.returncode = False, None

    def poll(self):
        return self.returncode

    def kill(self):
        self.killed, self.returncode = True, 1

    def wait(self):
        return self.returncode


class JobObjectTests(unittest.TestCase):
    def test_structure_layout_and_limits(self):
        pointer = ctypes.sizeof(ctypes.c_void_p)
        self.assertEqual(ctypes.sizeof(win.JOBOBJECT_EXTENDED_LIMIT_INFORMATION), 144 if pointer == 8 else 112)
        info = win.limit_information(256 * 1024 * 1024, 7)
        self.assertEqual(info.ProcessMemoryLimit, 256 * 1024 * 1024)
        self.assertEqual(info.BasicLimitInformation.PerProcessUserTimeLimit, 70_000_000)
        self.assertEqual(info.BasicLimitInformation.ActiveProcessLimit, 1)
        self.assertEqual(info.BasicLimitInformation.LimitFlags, 0x2 | 0x8 | 0x100 | 0x400 | 0x2000)

    def test_launch_assigns_the_worker_to_a_limited_job(self):
        kernel32 = FakeKernel32()
        process = win.launch(['python', '-I'], 1024, 5, kernel32=kernel32, popen=FakeProcess, stdin=1)
        self.assertEqual(kernel32.calls[0], 'create')
        self.assertEqual(kernel32.calls[1][2], 9)  # JobObjectExtendedLimitInformation
        self.assertEqual((kernel32.stored.ProcessMemoryLimit, kernel32.stored.BasicLimitInformation.ActiveProcessLimit),
                         (1024, 1))
        self.assertEqual(kernel32.calls[2], ('assign', 77, 4242))
        self.assertTrue(process.kwargs['creationflags'] & win.CREATE_NO_WINDOW)
        self.assertEqual(process.kwargs['stdin'], 1)
        win.kill_and_reap(process)
        self.assertTrue(process.killed)
        self.assertEqual(kernel32.closed, [77])  # closing the job also kills anything left (KILL_ON_JOB_CLOSE)
        win.kill_and_reap(process)
        self.assertEqual(kernel32.closed, [77])

    def test_launch_fails_closed(self):
        for kernel32 in (FakeKernel32(create=False), FakeKernel32(configure=False)):
            started = []
            with self.assertRaisesRegex(ValueError, 'worker_enforcement_unavailable'):
                win.launch(['python'], 1024, 5, kernel32=kernel32, popen=lambda *a, **k: started.append(1))
            self.assertEqual(started, [])  # never started without a configured job
        kernel32, made = FakeKernel32(assign=False), []
        def popen(*args, **kwargs):
            made.append(FakeProcess(*args, **kwargs))
            return made[-1]
        with self.assertRaisesRegex(ValueError, 'worker_enforcement_unavailable'):
            win.launch(['python'], 1024, 5, kernel32=kernel32, popen=popen)
        self.assertTrue(made[0].killed)
        self.assertEqual(kernel32.closed, [77])

    def test_child_guard_waits_for_its_limits_and_proves_the_memory_cap(self):
        huge = 1 << 62  # an allocation the system refuses, as the job's cap makes it refuse
        answers = iter([False, False, True])
        self.assertIsNone(win.guard_child(huge, kernel32=FakeKernel32(inside=lambda: next(answers),
                                                                         limits=win.limit_information(huge, 5)),
                                          sleep=lambda s: None))
        clock = iter(range(100))
        for kernel32 in (FakeKernel32(inside=False), FakeKernel32(limits=win.limit_information(huge - 1, 5)),
                         FakeKernel32(limits=None)):
            with self.subTest(kernel32=vars(kernel32)), self.assertRaisesRegex(ValueError, 'worker_enforcement_unavailable'):
                win.guard_child(huge, kernel32=kernel32, clock=lambda: next(clock), sleep=lambda s: None)
        weak = win.limit_information(4096, 5)  # limits present, but a 4 KiB "cap" is not actually enforced here
        with self.assertRaisesRegex(ValueError, 'worker_enforcement_unavailable'):
            win.guard_child(4096, kernel32=FakeKernel32(limits=weak), sleep=lambda s: None)

    def test_platform_selection(self):
        with patch.object(sys, 'platform', 'win32'):
            self.assertEqual(_launcher(), 'windows-job-object')
        with patch.object(sys, 'platform', 'darwin'), self.assertRaisesRegex(WorkerError, 'worker_enforcement_unavailable'):
            _launcher()
        made = []
        def launch(command, cap, cpu, **kwargs):
            made.append((command, cap, cpu, kwargs))
            raise ValueError('worker_enforcement_unavailable')
        with patch.object(win, 'launch', launch), self.assertRaisesRegex(WorkerError, 'worker_enforcement_unavailable'):
            _start_worker('windows-job-object', 'pass', '/root', 1024, 3, stdin=-1)
        command, cap, cpu, kwargs = made[0]
        self.assertEqual((command[1:3], command[-2:], cap, cpu), (['-I', '-c'], ['/root', '1024'], 1024, 3))
        self.assertNotIn('start_new_session', kwargs)


@unittest.skipUnless(LINUX or WINDOWS, 'needs prlimit (Linux) or a Job Object (Windows)')
class ThreadChannelWorkerTests(unittest.TestCase):
    """The real workers with the Windows thread channel (on Linux still within prlimit)."""

    def setUp(self):
        channel = lambda process: win.ThreadChannel(process)
        for module in (prep_worker, source_worker):
            patcher = patch.object(module, 'open_channel', channel)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_monster_file_through_the_thread_channel(self):
        files = sorted(glob.glob(str(ROOT / 'monsters_examples' / 'tetra-cube' / '*.monster')))
        if not files:
            self.skipTest('monsters_examples/tetra-cube is not present')
        raw = Path(files[0]).read_bytes()
        snapshot, _ = source_worker.prepare_source_isolated(
            'file', {'filename': 'spider.monster'}, fetch=lambda url, deadline: b'', hosts=frozenset(),
            deadline=time.monotonic() + 20, limits=ModelLimits(), response_bytes=10 * 1024 * 1024, file_bytes=raw)
        self.assertEqual(snapshot['provenance'][0]['file_name'], 'spider.monster')

    def test_dndbeyond_fetch_round_trip_through_the_thread_channel(self):
        directory = ROOT / 'monsters_examples' / 'goblin'
        if not (directory / 'manifest.json').is_file():
            self.skipTest('captured monsters_examples evidence not present')
        manifest = json.loads((directory / 'manifest.json').read_text())
        row = next(r for r in manifest['requests'] if r['label'].startswith('dndbeyond-detail') and r.get('file'))
        page = (directory / row['file']).read_bytes()
        from python.scrying_glass_dndbeyond_statblock import HOSTS
        asked = []
        def fetch(url, deadline):
            asked.append(url)
            return page
        snapshot, _ = source_worker.prepare_source_isolated(
            'dndbeyond', {'path': row['url']}, fetch=fetch, hosts=HOSTS, deadline=time.monotonic() + 20,
            limits=ModelLimits(), response_bytes=10 * 1024 * 1024)
        self.assertEqual(asked, [row['url']])
        self.assertEqual(snapshot['provenance'][0]['provider'], 'D&D Beyond')

    def test_fivetools_preparation_through_the_thread_channel(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from test_fivetools_preparation_worker import parent_fetch
        from test_fivetools_preparation import Fetcher
        from python.scrying_glass_fivetools_preparation import prepare_statblock
        snapshot, _ = prep_worker.prepare_isolated('Grave Wight Elder', 'TST', fetch=parent_fetch(),
                                                   deadline=time.monotonic() + 20)
        expected = prepare_statblock('Grave Wight Elder', 'TST', fetch=Fetcher(), deadline=time.monotonic() + 20)
        self.assertEqual(snapshot, expected.snapshot)

    def test_adapter_errors_cross_the_thread_channel(self):
        with self.assertRaises(source_worker.SourceWorkerError) as caught:
            source_worker.prepare_source_isolated(
                'file', {'filename': 'bad.monster'}, fetch=lambda url, deadline: b'', hosts=frozenset(),
                deadline=time.monotonic() + 20, limits=ModelLimits(), response_bytes=1024, file_bytes=b'not json')
        self.assertEqual(caught.exception.code, 'malformed_file')


@unittest.skipUnless(WINDOWS, 'Windows Job Object enforcement')
class RealJobObjectTests(unittest.TestCase):
    def test_a_real_worker_runs_inside_a_limited_job(self):
        files = sorted(glob.glob(str(ROOT / 'monsters_examples' / 'tetra-cube' / '*.monster')))
        if not files:
            self.skipTest('monsters_examples/tetra-cube is not present')
        snapshot, _ = source_worker.prepare_source_isolated(
            'file', {'filename': 'spider.monster'}, fetch=lambda url, deadline: b'', hosts=frozenset(),
            deadline=time.monotonic() + 30, limits=ModelLimits(), response_bytes=10 * 1024 * 1024,
            file_bytes=Path(files[0]).read_bytes())
        self.assertEqual(snapshot['provenance'][0]['file_name'], 'spider.monster')

    def test_the_memory_cap_stops_a_large_allocation(self):
        import subprocess
        probe = ("import sys;sys.path.insert(0,sys.argv[1]);"
                 "from python.scrying_glass_fivetools_worker import _memory_guard;_memory_guard(int(sys.argv[2]));"
                 "import time\ntry:\n    b=bytearray(int(sys.argv[2])//2*3)\n    print('allocated')\n"
                 "except MemoryError:\n    print('refused')")
        process = _start_worker(_launcher(), probe, str(ROOT), 128 * 1024 * 1024, 10,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            out, err = process.communicate(timeout=30)
        finally:
            from python.scrying_glass_fivetools_worker import _kill_and_reap
            _kill_and_reap(process)
        self.assertEqual(out.decode().strip(), 'refused', err.decode())


if __name__ == '__main__':
    unittest.main()
