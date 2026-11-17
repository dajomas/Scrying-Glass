"""Private Linux isolated inheritance runner; not an HTTP/job scheduler API.

Requires util-linux prlimit at a trusted system path. Kernel address-space and
file limits are set before Python starts. No shell, pickle or imported JS.
Caller supplies exact bounded bytes and its original absolute deadline. The
caller must run this blocking function outside the event loop and DB lock.
"""
from __future__ import annotations
import base64
import errno
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict
from .scrying_glass_fivetools_resolution import (
    Identity, Limits, Provenance, Result, Diagnostic, ResolutionError,
)

class WorkerError(ValueError):
    """Sanitized process/enforcement/transport error, never remote stderr."""
    pass

def _launcher():
    if sys.platform != 'linux':
        raise WorkerError('worker_enforcement_unavailable')
    for path in ('/usr/bin/prlimit', '/bin/prlimit'):
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    raise WorkerError('worker_enforcement_unavailable')

def _check(deadline, cancelled):
    if cancelled():
        raise WorkerError('cancelled')
    if time.monotonic() >= deadline:
        raise WorkerError('deadline')

def _write_json(stream, value, cap, check):
    for text in json.JSONEncoder(ensure_ascii=False, allow_nan=False, separators=(',', ':')).iterencode(value):
        check()
        if stream.tell() + len(text) + 1 > cap:
            raise WorkerError('worker_transport_limit')
        data = text.encode('utf-8')
        if stream.tell() + len(data) + 1 > cap:
            raise WorkerError('worker_transport_limit')
        stream.write(data)
    stream.write(b'\n')

def _kill_and_reap(process):
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait()

def resolve_isolated(selected, records, *, deadline, limits=None,
                     worker_memory_bytes=268435456, cancelled=lambda: False):
    """Resolve one immutable dataset generation in a fresh restricted process.

    records is an immutable tuple of (Identity, bytes); duplicate exact keys survive
    transport for the resolver's ambiguity checks. Input/output transport files
    each have a worker_memory_bytes allowance, NOT a saved-snapshot allowance.
    No failed result is cached and no process/cache survives this invocation.
    This is resource isolation, not a general malicious-code/filesystem sandbox.
    """
    limits = Limits() if limits is None else limits
    if not isinstance(selected, Identity) or not isinstance(limits, Limits) or type(records) is not tuple:
        raise ValueError('invalid_worker_input')
    if type(worker_memory_bytes) is not int or not 0 < worker_memory_bytes <= 2**63-1:
        raise ValueError('invalid_worker_memory_bytes')
    if type(deadline) not in (int, float) or not math.isfinite(deadline) or not callable(cancelled):
        raise ValueError('invalid_worker_deadline_or_callback')
    check = lambda: _check(deadline, cancelled)
    check()
    launcher = _launcher()
    cap = worker_memory_bytes
    with tempfile.TemporaryFile() as request, tempfile.TemporaryFile() as response:
        _write_json(request, {'selected': asdict(selected), 'limits': asdict(limits),
                             'deadline': deadline}, cap, check)
        for pair in records:
            check()
            if type(pair) is not tuple or len(pair) != 2:
                raise ValueError('invalid_dataset_record')
            identity, raw = pair
            if not isinstance(identity, Identity) or identity.dataset != selected.dataset or type(raw) is not bytes:
                raise ValueError('invalid_dataset_record')
            if len(raw) > limits.response_bytes:
                raise WorkerError('response_bytes_limit')
            _write_json(request, {'identity': asdict(identity), 'bytes': len(raw)}, cap, check)
            if request.tell() + len(raw) + 1 > cap:
                raise WorkerError('worker_transport_limit')
            for offset in range(0, len(raw), 65536):
                check()
                request.write(raw[offset:offset+65536])
            request.write(b'\n')
        check()
        request.seek(0)
        root = str(Path(__file__).resolve().parent.parent)
        bootstrap = "import sys;sys.path.insert(0,sys.argv[1]);from python.scrying_glass_fivetools_worker import _child;_child()"
        command = [launcher, '--core=0', '--as='+str(cap), '--fsize='+str(cap),
                   '--cpu='+str(max(1, math.ceil(deadline-time.monotonic()))), '--',
                   sys.executable, '-I', '-c', bootstrap, root, str(cap)]
        check()
        try:
            process = subprocess.Popen(command, stdin=request, stdout=response,
                                       stderr=subprocess.DEVNULL, close_fds=True,
                                       start_new_session=True)
        except OSError as exc:
            raise WorkerError('worker_start_failed') from exc
        try:
            while process.poll() is None:
                check()
                time.sleep(min(0.01, max(0, deadline-time.monotonic())))
            check()
            if process.returncode != 0:
                raise WorkerError('worker_resource_or_start_failure')
            if response.tell() > cap:
                raise WorkerError('worker_transport_limit')
            response.seek(0)
            payload = response.read(cap+1)
            check()
            if len(payload) > cap:
                raise WorkerError('worker_transport_limit')
            try:
                outcome = json.loads(payload)
                check()
                if 'error' in outcome:
                    d = outcome['error']
                    diagnostic = Diagnostic(d['code'], Identity(**d['selected']),
                        tuple(Identity(**i) for i in d['chain']), d['source_path'],
                        d['property'], d['operation_index'], d['mode'])
                    if diagnostic.selected != selected:
                        raise ValueError('identity_mismatch')
                    raise ResolutionError(diagnostic)
                if 'worker_error' in outcome:
                    if outcome['worker_error'] not in {'worker_enforcement_unavailable', 'worker_memory_limit', 'worker_input_invalid', 'worker_internal_error', 'worker_transport_limit'}:
                        raise ValueError('unknown_worker_error')
                    raise WorkerError(outcome['worker_error'])
                record = base64.b64decode(outcome['record'], validate=True)
                if len(record) > limits.intermediate_creature_bytes:
                    raise ValueError('record_limit')
                provenance = tuple(Provenance(Identity(**p['identity']), p['role'],
                    tuple(Identity(**i) for i in p['chain'])) for p in outcome['provenance'])
                result = Result(record, provenance, outcome['depth'], outcome['operations'])
                if not provenance or provenance[0] != Provenance(selected, 'selected', (selected,)):
                    raise ValueError('identity_mismatch')
                check()
                return result
            except (ResolutionError, WorkerError):
                raise
            except (ValueError, TypeError, KeyError, UnicodeError, RecursionError) as exc:
                raise WorkerError('worker_protocol_error') from exc
        finally:
            _kill_and_reap(process)

def _memory_guard(cap):
    import mmap
    import resource
    if sys.platform != 'linux' or resource.getrlimit(resource.RLIMIT_AS) != (cap, cap) or resource.getrlimit(resource.RLIMIT_FSIZE) != (cap, cap):
        raise WorkerError('worker_enforcement_unavailable')
    try:
        mapping = mmap.mmap(-1, cap)
    except MemoryError:
        return
    except OSError as exc:
        if exc.errno == errno.ENOMEM:
            return
        raise WorkerError('worker_enforcement_unavailable') from exc
    mapping.close()
    raise WorkerError('worker_enforcement_unavailable')

def _child():
    """Fixed entry point; never takes a callable/module name from source data."""
    try:
        cap = int(sys.argv[2])
        _memory_guard(cap)
        from .scrying_glass_fivetools_resolution import DatasetLoader, Resolver
        source = sys.stdin.buffer
        head = json.loads(source.readline(cap+1))
        selected, limits = Identity(**head['selected']), Limits(**head['limits'])
        def check():
            _check(head['deadline'], lambda: False)
        rows = []
        while True:
            check()
            header = source.readline(cap+1)
            if not header:
                break
            row = json.loads(header)
            size = row['bytes']
            if type(size) is not int or not 0 <= size <= limits.response_bytes:
                raise WorkerError('worker_input_invalid')
            raw = source.read(size)
            if len(raw) != size or source.read(1) != b'\n':
                raise WorkerError('worker_input_invalid')
            rows.append((Identity(**row['identity']), raw))
        result = Resolver(DatasetLoader(selected.dataset, rows), limits=limits).resolve(
            selected, deadline=head['deadline'])
        del rows
        check()
        outcome = {'record': base64.b64encode(result.record_json).decode('ascii'),
                   'provenance': [asdict(p) for p in result.provenance],
                   'depth': result.inheritance_depth, 'operations': result.modification_operations}
    except ResolutionError as exc:
        outcome = {'error': asdict(exc.diagnostic)}
    except MemoryError:
        outcome = {'worker_error': 'worker_memory_limit'}
    except WorkerError as exc:
        code = str(exc)
        outcome = {'worker_error': code if code in {'worker_enforcement_unavailable', 'worker_transport_limit'} else 'worker_input_invalid'}
    except Exception:
        outcome = {'worker_error': 'worker_internal_error'}
    try:
        _write_json(sys.stdout.buffer, outcome, cap, lambda: None)
        sys.stdout.buffer.flush()
    except Exception:
        os._exit(1)
