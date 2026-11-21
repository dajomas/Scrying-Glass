"""Windows resource limits for the isolated preparation workers (SG-TODO-022.15).

Linux bounds each worker with util-linux ``prlimit`` before Python starts. Windows
has no prlimit; its equivalent is a Job Object, set up here with ctypes (no new
dependency):

- ``JOB_OBJECT_LIMIT_PROCESS_MEMORY``: committed memory capped at the worker
  memory limit (Linux: address space, RLIMIT_AS);
- ``JOB_OBJECT_LIMIT_PROCESS_TIME``: user-mode CPU time capped at the seconds left
  before the job's deadline (Linux: RLIMIT_CPU);
- ``JOB_OBJECT_LIMIT_ACTIVE_PROCESS`` = 1: the worker cannot start processes;
- ``JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE``: closing the job handle kills the worker,
  also when the server itself exits; ``DIE_ON_UNHANDLED_EXCEPTION``: no error
  dialogs.

The child is started normally and assigned to the job at once; before it reads
any input it waits (at most ``ASSIGN_SECONDS``) until its own innermost job
carries exactly these limits and then proves the memory cap by failing a
cap-sized allocation (``guard_child``). Anything else fails explicitly with
``worker_enforcement_unavailable``, as on Linux. There is no Windows per-process
file-size limit (Linux: RLIMIT_FSIZE); the workers write no files.

Windows pipes do not work with ``select``; ``ThreadChannel`` gives the parent the
same non-blocking interface as the POSIX channel with one reader and one writer
thread. This is resource isolation, not a filesystem or network sandbox.
"""
from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import threading
import time
from collections import deque

ASSIGN_SECONDS = 5.0
JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS = 9
LIMIT_PROCESS_TIME = 0x00000002
LIMIT_ACTIVE_PROCESS = 0x00000008
LIMIT_PROCESS_MEMORY = 0x00000100
LIMIT_DIE_ON_UNHANDLED_EXCEPTION = 0x00000400
LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
REQUIRED = (LIMIT_PROCESS_TIME | LIMIT_ACTIVE_PROCESS | LIMIT_PROCESS_MEMORY | LIMIT_DIE_ON_UNHANDLED_EXCEPTION
            | LIMIT_KILL_ON_JOB_CLOSE)
CREATE_NO_WINDOW = 0x08000000
CREATE_NEW_PROCESS_GROUP = 0x00000200


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in (
        'ReadOperationCount', 'WriteOperationCount', 'OtherOperationCount',
        'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [('PerProcessUserTimeLimit', ctypes.c_longlong), ('PerJobUserTimeLimit', ctypes.c_longlong),
                ('LimitFlags', ctypes.c_uint32), ('MinimumWorkingSetSize', ctypes.c_size_t),
                ('MaximumWorkingSetSize', ctypes.c_size_t), ('ActiveProcessLimit', ctypes.c_uint32),
                ('Affinity', ctypes.c_size_t), ('PriorityClass', ctypes.c_uint32), ('SchedulingClass', ctypes.c_uint32)]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [('BasicLimitInformation', JOBOBJECT_BASIC_LIMIT_INFORMATION), ('IoInfo', IO_COUNTERS),
                ('ProcessMemoryLimit', ctypes.c_size_t), ('JobMemoryLimit', ctypes.c_size_t),
                ('PeakProcessMemoryUsed', ctypes.c_size_t), ('PeakJobMemoryUsed', ctypes.c_size_t)]


def limit_information(cap, cpu_seconds):
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    basic = info.BasicLimitInformation
    basic.LimitFlags = REQUIRED
    basic.PerProcessUserTimeLimit = int(cpu_seconds) * 10_000_000  # 100 ns units
    basic.ActiveProcessLimit = 1
    info.ProcessMemoryLimit = cap
    return info


def _kernel32():
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    handle = ctypes.c_void_p
    kernel32.CreateJobObjectW.restype = handle
    kernel32.CreateJobObjectW.argtypes = (ctypes.c_void_p, ctypes.c_wchar_p)
    kernel32.SetInformationJobObject.restype = ctypes.c_int
    kernel32.SetInformationJobObject.argtypes = (handle, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32)
    kernel32.QueryInformationJobObject.restype = ctypes.c_int
    kernel32.QueryInformationJobObject.argtypes = (handle, ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32,
                                                   ctypes.c_void_p)
    kernel32.AssignProcessToJobObject.restype = ctypes.c_int
    kernel32.AssignProcessToJobObject.argtypes = (handle, handle)
    kernel32.IsProcessInJob.restype = ctypes.c_int
    kernel32.IsProcessInJob.argtypes = (handle, handle, ctypes.POINTER(ctypes.c_int))
    kernel32.GetCurrentProcess.restype = handle
    kernel32.CloseHandle.restype = ctypes.c_int
    kernel32.CloseHandle.argtypes = (handle,)
    return kernel32


def launch(command, cap, cpu_seconds, *, kernel32=None, popen=subprocess.Popen, **popen_kwargs):
    """Start ``command`` (a Python worker) inside a new limited Job Object; -> Popen.

    The job handle is kept on the process (``_sg_job``); ``kill_and_reap`` closes it.
    Raises OSError when the process cannot start, ValueError('worker_enforcement_unavailable')
    when the job cannot be created or assigned (the process is then killed).
    """
    kernel32 = kernel32 or _kernel32()
    job = kernel32.CreateJobObjectW(None, None)
    if not job:
        raise ValueError('worker_enforcement_unavailable')
    info = limit_information(cap, cpu_seconds)
    if not kernel32.SetInformationJobObject(job, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
                                            ctypes.byref(info), ctypes.sizeof(info)):
        kernel32.CloseHandle(job)
        raise ValueError('worker_enforcement_unavailable')
    flags = popen_kwargs.pop('creationflags', 0) | CREATE_NO_WINDOW | CREATE_NEW_PROCESS_GROUP
    try:
        process = popen(command, creationflags=flags, **popen_kwargs)
    except OSError:
        kernel32.CloseHandle(job)
        raise
    if not kernel32.AssignProcessToJobObject(job, int(process._handle)):
        process.kill()
        process.wait()
        kernel32.CloseHandle(job)
        raise ValueError('worker_enforcement_unavailable')
    process._sg_job = job
    process._sg_kernel32 = kernel32
    return process


def kill_and_reap(process):
    if process.poll() is None:
        try:
            process.kill()
        except OSError:
            pass
    process.wait()
    job = getattr(process, '_sg_job', None)
    if job:
        process._sg_job = None
        process._sg_kernel32.CloseHandle(job)


def guard_child(cap, *, kernel32=None, clock=time.monotonic, sleep=time.sleep):
    """In the worker, before reading input: own job limits present, then the memory cap proven."""
    kernel32 = kernel32 or _kernel32()
    deadline = clock() + ASSIGN_SECONDS
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    while True:
        inside = ctypes.c_int(0)
        if (kernel32.IsProcessInJob(kernel32.GetCurrentProcess(), None, ctypes.byref(inside)) and inside.value
                and kernel32.QueryInformationJobObject(None, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION_CLASS,
                                                       ctypes.byref(info), ctypes.sizeof(info), None)
                and info.BasicLimitInformation.LimitFlags & REQUIRED == REQUIRED
                and info.ProcessMemoryLimit == cap and info.BasicLimitInformation.ActiveProcessLimit == 1):
            break
        if clock() >= deadline:
            raise ValueError('worker_enforcement_unavailable')
        sleep(0.01)
    try:
        probe = bytearray(cap)  # must fail: the interpreter already uses part of the cap
    except MemoryError:
        return
    del probe
    raise ValueError('worker_enforcement_unavailable')


class ThreadChannel:
    """Non-blocking pipe access for the parent: ``readable``/``read``, ``writable``/``write``.

    ``read`` raises BlockingIOError when nothing is buffered and returns b'' at end of
    output; ``write`` queues data for the writer thread and raises BrokenPipeError once
    the child stopped reading. ``writable`` is False while more than ``WRITE_QUEUE``
    bytes wait, so the parent keeps checking its deadline.
    """
    WRITE_QUEUE = 1 << 20

    def __init__(self, process):
        self.process = process
        self._lock = threading.Condition()
        self._chunks, self._eof, self._pending, self._broken = deque(), False, 0, False
        self._writes = deque()
        self._closed = False
        self._reader = threading.Thread(target=self._read_loop, name='statblock-worker-read', daemon=True)
        self._writer = threading.Thread(target=self._write_loop, name='statblock-worker-write', daemon=True)
        self._reader.start()
        self._writer.start()

    def _read_loop(self):
        stream = self.process.stdout
        try:
            while True:
                chunk = os.read(stream.fileno(), 1 << 20)
                with self._lock:
                    if not chunk:
                        self._eof = True
                        self._lock.notify_all()
                        return
                    self._chunks.append(chunk)
                    self._lock.notify_all()
        except (OSError, ValueError):
            with self._lock:
                self._eof = True
                self._lock.notify_all()

    def _write_loop(self):
        stream = self.process.stdin
        while True:
            with self._lock:
                while not self._writes and not self._closed:
                    self._lock.wait()
                if self._closed and not self._writes:
                    return
                data = self._writes.popleft()
            try:
                view = memoryview(data)
                while view:
                    view = view[os.write(stream.fileno(), view):]
            except (OSError, ValueError):
                with self._lock:
                    self._broken = True
                    self._writes.clear()
                    self._pending = 0
                    self._lock.notify_all()
                return
            with self._lock:
                self._pending -= len(data)
                self._lock.notify_all()

    def readable(self, timeout):
        with self._lock:
            if not self._chunks and not self._eof:
                self._lock.wait(timeout)
            return bool(self._chunks) or self._eof

    def read(self, size):
        with self._lock:
            if not self._chunks:
                if self._eof:
                    return b''
                raise BlockingIOError()
            out = bytearray()
            while self._chunks and len(out) < size:
                chunk = self._chunks.popleft()
                take = size - len(out)
                out.extend(chunk[:take])
                if len(chunk) > take:
                    self._chunks.appendleft(chunk[take:])
            return bytes(out)

    def writable(self, timeout):
        with self._lock:
            if self._pending > self.WRITE_QUEUE and not self._broken:
                self._lock.wait(timeout)
            return self._broken or self._pending <= self.WRITE_QUEUE

    def write(self, view):
        data = bytes(view)
        with self._lock:
            if self._broken:
                raise BrokenPipeError()
            self._writes.append(data)
            self._pending += len(data)
            self._lock.notify_all()
        return len(data)

    def close(self):
        with self._lock:
            self._closed = True
            self._lock.notify_all()
