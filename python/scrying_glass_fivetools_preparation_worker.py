"""Isolated 5e.tools statblock preparation (022.04e/f); not an HTTP/job API.

The whole preparation -- dataset parsing, inheritance, modifications,
reference collection and normalization -- runs in a fresh prlimit-bounded
child process (same Linux enforcement as scrying_glass_fivetools_worker).
The child has no network: it asks its parent for dataset files over a pipe,
and the parent fetches only ``allowed_dataset_path`` paths, enforcing the
response limit and the original absolute deadline. Late, malformed or
oversized child output is rejected; the child is always killed and reaped.
Run outside the event loop and database lock.
"""
from __future__ import annotations

import json
import math
import os
import selectors
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

from .scrying_glass_fivetools_fetch import FetchError, allowed_dataset_path
from .scrying_glass_fivetools_worker import WorkerError, _kill_and_reap, _launcher, _memory_guard

MAX_LINE = 65536
WORKER_ERRORS = frozenset(('worker_enforcement_unavailable', 'worker_memory_limit', 'worker_input_invalid',
                           'worker_internal_error', 'worker_transport_limit'))


def _limits_payload(limits):
    return {'resolution': asdict(limits.resolution), 'collection': asdict(limits.collection), 'model': asdict(limits.model)}


def prepare_isolated(name, source, *, fetch, deadline, limits=None, cancelled=lambda: False,
                     worker_memory_bytes=268435456, data_root='https://5e.tools/data', site='https://5e.tools'):
    """Return (snapshot, measurements) or raise PreparationError/WorkerError.

    fetch(path, deadline=...) -> bytes runs in this (parent) process.
    """
    from .scrying_glass_fivetools_preparation import PreparationError, PreparationLimits
    limits = PreparationLimits() if limits is None else limits
    if not isinstance(limits, PreparationLimits) or type(name) is not str or type(source) is not str:
        raise ValueError('invalid_worker_input')
    if type(worker_memory_bytes) is not int or not 0 < worker_memory_bytes <= 2**63 - 1:
        raise ValueError('invalid_worker_memory_bytes')
    if type(deadline) not in (int, float) or not math.isfinite(deadline) or not callable(cancelled) or not callable(fetch):
        raise ValueError('invalid_worker_deadline_or_callback')
    def check():
        if cancelled():
            raise WorkerError('cancelled')
        if time.monotonic() >= deadline:
            raise WorkerError('deadline')
    check()
    launcher = _launcher()
    cap = worker_memory_bytes
    response_cap = limits.resolution.response_bytes
    root = str(Path(__file__).resolve().parent.parent)
    bootstrap = ("import sys;sys.path.insert(0,sys.argv[1]);"
                 "from python.scrying_glass_fivetools_preparation_worker import _child;_child()")
    command = [launcher, '--core=0', '--as=' + str(cap), '--fsize=' + str(cap),
               '--cpu=' + str(max(1, math.ceil(deadline - time.monotonic()))), '--',
               sys.executable, '-I', '-c', bootstrap, root, str(cap)]
    try:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.DEVNULL, close_fds=True, start_new_session=True)
    except OSError as exc:
        raise WorkerError('worker_start_failed') from exc
    selector = selectors.DefaultSelector()
    buffer = bytearray()
    try:
        os.set_blocking(process.stdout.fileno(), False)
        os.set_blocking(process.stdin.fileno(), False)
        selector.register(process.stdout, selectors.EVENT_READ)
        def send(data):
            view = memoryview(data)
            while view:
                check()
                _, writable, _ = select_write(process.stdin, deadline)
                if writable:
                    try:
                        written = os.write(process.stdin.fileno(), view)
                    except BlockingIOError:
                        continue
                    except BrokenPipeError:
                        raise WorkerError('worker_resource_or_start_failure') from None
                    view = view[written:]
        def read_line():
            while True:
                index = buffer.find(b'\n')
                if index >= 0:
                    line = bytes(buffer[:index])
                    del buffer[:index + 1]
                    return line
                if len(buffer) > MAX_LINE:
                    raise WorkerError('worker_transport_limit')
                check()
                for _key, _mask in selector.select(timeout=min(0.05, max(0.0, deadline - time.monotonic()))):
                    try:
                        chunk = os.read(process.stdout.fileno(), 65536)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        raise WorkerError('worker_resource_or_start_failure')
                    buffer.extend(chunk)
                    if len(buffer) > max(MAX_LINE, cap):
                        raise WorkerError('worker_transport_limit')
                if process.poll() is not None and buffer.find(b'\n') < 0:
                    rest = b''
                    try:
                        rest = os.read(process.stdout.fileno(), 65536)
                    except (BlockingIOError, OSError):
                        pass
                    if not rest:
                        raise WorkerError('worker_resource_or_start_failure')
                    buffer.extend(rest)
        head = {'name': name, 'source': source, 'limits': _limits_payload(limits), 'deadline': deadline,
                'data_root': data_root, 'site': site}
        send(json.dumps(head).encode() + b'\n')
        while True:
            line = read_line()
            try:
                message = json.loads(line)
            except ValueError:
                raise WorkerError('worker_protocol_error') from None
            if type(message) is not dict:
                raise WorkerError('worker_protocol_error')
            if 'fetch' in message:
                path = message['fetch']
                if not allowed_dataset_path(path):
                    raise WorkerError('worker_protocol_error')
                try:
                    data = fetch(path, deadline=deadline)
                    if type(data) is not bytes or len(data) > response_cap:
                        raise FetchError('response_bytes_limit')
                    send(json.dumps({'bytes': len(data)}).encode() + b'\n' + data + b'\n')
                except FetchError as exc:
                    send(json.dumps({'fetch_error': str(exc)}).encode() + b'\n')
                continue
            if 'error' in message:
                error = message['error']
                if type(error) is not dict or type(error.get('code')) is not str:
                    raise WorkerError('worker_protocol_error')
                raise PreparationError(error['code'], error.get('detail'))
            if 'worker_error' in message:
                code = message['worker_error']
                raise WorkerError(code if code in WORKER_ERRORS else 'worker_protocol_error')
            if 'result' in message:
                length = message['result']
                if type(length) is not int or not 0 <= length <= cap:
                    raise WorkerError('worker_transport_limit')
                while len(buffer) < length + 1:
                    check()
                    for _key, _mask in selector.select(timeout=0.05):
                        chunk = os.read(process.stdout.fileno(), 1 << 20)
                        if not chunk:
                            raise WorkerError('worker_protocol_error')
                        buffer.extend(chunk)
                payload = bytes(buffer[:length])
                check()
                try:
                    result = json.loads(payload)
                    snapshot, measurements = result['snapshot'], result['measurements']
                    from .scrying_glass_statblock_model import validate_snapshot
                    snapshot = validate_snapshot(snapshot, limits.model)
                except (ValueError, KeyError, TypeError) as exc:
                    raise WorkerError('worker_protocol_error') from None
                return snapshot, measurements
            raise WorkerError('worker_protocol_error')
    finally:
        selector.close()
        for stream in (process.stdin, process.stdout):
            try:
                stream.close()
            except OSError:
                pass
        _kill_and_reap(process)


def select_write(stream, deadline):
    import select
    timeout = min(0.05, max(0.0, deadline - time.monotonic()))
    return select.select([], [stream], [], timeout)


def _child():
    """Fixed child entry point; reads the request header, then RPCs for files."""
    out = sys.stdout.buffer
    def emit(value, extra=b''):
        out.write(json.dumps(value).encode() + b'\n' + extra)
        out.flush()
    try:
        cap = int(sys.argv[2])
        _memory_guard(cap)
        from .scrying_glass_fivetools_collector import CollectionLimits
        from .scrying_glass_fivetools_preparation import PreparationError, PreparationLimits, prepare_statblock
        from .scrying_glass_fivetools_resolution import Limits
        from .scrying_glass_statblock_model import ModelLimits
        source = sys.stdin.buffer
        head = json.loads(source.readline(MAX_LINE))
        raw = head['limits']
        limits = PreparationLimits(Limits(**raw['resolution']), CollectionLimits(**raw['collection']), ModelLimits(**raw['model']))
        def fetch(path):
            emit({'fetch': path})
            reply = json.loads(source.readline(MAX_LINE))
            if 'fetch_error' in reply:
                raise LookupError('reference_unavailable' if reply['fetch_error'] == 'not_found' else 'provider_unavailable')
            size = reply['bytes']
            if type(size) is not int or not 0 <= size <= limits.resolution.response_bytes:
                raise WorkerError('worker_input_invalid')
            data = source.read(size)
            if len(data) != size or source.read(1) != b'\n':
                raise WorkerError('worker_input_invalid')
            return data
        try:
            prepared = prepare_statblock(head['name'], head['source'], fetch=fetch, deadline=head['deadline'],
                                         limits=limits, data_root=head['data_root'], site=head['site'])
        except PreparationError as exc:
            emit({'error': {'code': exc.code, 'detail': exc.detail if type(exc.detail) is str else None}})
            return
        payload = json.dumps({'snapshot': prepared.snapshot, 'measurements': prepared.measurements},
                             ensure_ascii=False, separators=(',', ':')).encode()
        emit({'result': len(payload)}, payload + b'\n')
    except MemoryError:
        _safe_emit(out, {'worker_error': 'worker_memory_limit'})
    except WorkerError as exc:
        code = str(exc)
        _safe_emit(out, {'worker_error': code if code in ('worker_enforcement_unavailable', 'worker_transport_limit') else 'worker_input_invalid'})
    except Exception:
        _safe_emit(out, {'worker_error': 'worker_internal_error'})


def _safe_emit(out, value):
    try:
        out.write(json.dumps(value).encode() + b'\n')
        out.flush()
    except Exception:
        os._exit(1)
