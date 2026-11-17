"""Isolated Open5e, D&D Beyond and .monster statblock preparation (SG-TODO-022.08).

Same boundary as the 5e.tools preparation worker: the conversion -- parsing,
Markdown/HTML extraction, placeholder resolution, normalization and snapshot
validation -- runs in a fresh prlimit-bounded child (address space, file size
and CPU), started without network use of its own. The child asks its parent
for each URL; the parent fetches only HTTPS URLs on the provider's host
allowlist, through the shared bounded fetcher, within the job's original
absolute deadline. Late, malformed or oversized child output is rejected; the
child is always killed and reaped. Unsupported enforcement fails explicitly
(``worker_enforcement_unavailable``) instead of running unbounded.
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
from urllib.parse import urlsplit

from .scrying_glass_fivetools_preparation_worker import select_write
from .scrying_glass_fivetools_worker import WorkerError, _kill_and_reap, _launcher, _memory_guard

MAX_LINE = 65536
KINDS = frozenset(('open5e', 'dndbeyond', 'file'))
WORKER_ERRORS = frozenset(('worker_enforcement_unavailable', 'worker_memory_limit', 'worker_input_invalid',
                           'worker_internal_error', 'worker_transport_limit'))


class SourceWorkerError(ValueError):
    """Adapter failure reported by the child (SourceError code)."""

    def __init__(self, code, detail=None):
        self.code, self.detail = code, detail
        super().__init__(code)


def https_url_allowed(url, hosts):
    try:
        parts = urlsplit(url)
    except ValueError:
        return False
    return (type(url) is str and parts.scheme == 'https' and parts.hostname in hosts
            and not parts.username and not parts.password and len(url) <= 4096)


def prepare_source_isolated(kind, request, *, fetch, hosts, deadline, limits, response_bytes,
                            worker_memory_bytes=268435456, cancelled=lambda: False, file_bytes=None):
    """Return (snapshot, measurements) or raise SourceWorkerError/WorkerError.

    request: {'key','base_url'} (open5e), {'path'} (dndbeyond), {'filename'} (file).
    fetch(url, deadline=...) -> bytes runs in this (parent) process.
    """
    from .scrying_glass_statblock_model import ModelLimits, validate_snapshot
    if kind not in KINDS or type(request) is not dict or not isinstance(limits, ModelLimits):
        raise ValueError('invalid_worker_input')
    if kind == 'file' and type(file_bytes) is not bytes:
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
    root = str(Path(__file__).resolve().parent.parent)
    bootstrap = ("import sys;sys.path.insert(0,sys.argv[1]);"
                 "from python.scrying_glass_statblock_worker import _child;_child()")
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
        def fill(minimum):
            while len(buffer) < minimum:
                check()
                for _key, _mask in selector.select(timeout=min(0.05, max(0.0, deadline - time.monotonic()))):
                    try:
                        chunk = os.read(process.stdout.fileno(), 1 << 20)
                    except BlockingIOError:
                        continue
                    if not chunk:
                        raise WorkerError('worker_resource_or_start_failure')
                    buffer.extend(chunk)
                    if len(buffer) > max(MAX_LINE, cap) + MAX_LINE:
                        raise WorkerError('worker_transport_limit')
                if process.poll() is not None and len(buffer) < minimum:
                    try:
                        rest = os.read(process.stdout.fileno(), 1 << 20)
                    except (BlockingIOError, OSError):
                        rest = b''
                    if not rest:
                        raise WorkerError('worker_resource_or_start_failure')
                    buffer.extend(rest)
        def read_line():
            while True:
                index = buffer.find(b'\n')
                if index >= 0:
                    line = bytes(buffer[:index])
                    del buffer[:index + 1]
                    return line
                if len(buffer) > MAX_LINE:
                    raise WorkerError('worker_transport_limit')
                fill(len(buffer) + 1)
        head = {'kind': kind, 'request': request, 'limits': asdict(limits), 'deadline': deadline,
                'response_bytes': response_bytes,
                'file_bytes': len(file_bytes) if kind == 'file' else None}
        send(json.dumps(head).encode() + b'\n' + ((file_bytes + b'\n') if kind == 'file' else b''))
        while True:
            line = read_line()
            try:
                message = json.loads(line)
            except ValueError:
                raise WorkerError('worker_protocol_error') from None
            if type(message) is not dict:
                raise WorkerError('worker_protocol_error')
            if 'fetch' in message:
                url = message['fetch']
                if kind == 'file' or not https_url_allowed(url, hosts):
                    raise WorkerError('worker_protocol_error')
                try:
                    data = fetch(url, deadline=deadline)
                    if type(data) is not bytes or len(data) > response_bytes:
                        raise SourceWorkerError('response_bytes_limit')
                    send(json.dumps({'bytes': len(data)}).encode() + b'\n' + data + b'\n')
                except WorkerError:
                    raise
                except Exception as exc:
                    code = getattr(exc, 'code', None)
                    if code in ('deadline', 'cancelled'):
                        raise WorkerError(code) from None
                    send(json.dumps({'fetch_error': code if type(code) is str else 'provider_error',
                                     'retry_at': getattr(exc, 'retry_at', None)}).encode() + b'\n')
                continue
            if 'error' in message:
                error = message['error']
                if type(error) is not dict or type(error.get('code')) is not str:
                    raise WorkerError('worker_protocol_error')
                raise SourceWorkerError(error['code'], error.get('detail') if type(error.get('detail')) is str else None)
            if 'worker_error' in message:
                code = message['worker_error']
                raise WorkerError(code if code in WORKER_ERRORS else 'worker_protocol_error')
            if 'result' in message:
                length = message['result']
                if type(length) is not int or not 0 <= length <= cap:
                    raise WorkerError('worker_transport_limit')
                fill(length + 1)
                payload = bytes(buffer[:length])
                check()
                try:
                    result = json.loads(payload)
                    snapshot, measurements = result['snapshot'], result['measurements']
                    snapshot = validate_snapshot(snapshot, limits)
                except (ValueError, KeyError, TypeError):
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


def _child():
    """Fixed child entry point; the adapter is chosen by a fixed kind, never by data."""
    out = sys.stdout.buffer
    def emit(value, extra=b''):
        out.write(json.dumps(value).encode() + b'\n' + extra)
        out.flush()
    try:
        cap = int(sys.argv[2])
        _memory_guard(cap)
        from .scrying_glass_statblock_model import ModelLimits
        from .scrying_glass_statblock_sources import SourceError
        source = sys.stdin.buffer
        head = json.loads(source.readline(MAX_LINE))
        kind, request, deadline = head['kind'], head['request'], head['deadline']
        limits, response_bytes = ModelLimits(**head['limits']), head['response_bytes']
        if kind not in KINDS or type(request) is not dict or type(response_bytes) is not int:
            raise WorkerError('worker_input_invalid')
        raw = None
        if kind == 'file':
            size = head['file_bytes']
            if type(size) is not int or not 0 <= size <= cap:
                raise WorkerError('worker_input_invalid')
            raw = source.read(size)
            if len(raw) != size or source.read(1) != b'\n':
                raise WorkerError('worker_input_invalid')
        def fetch(url, *, deadline):
            emit({'fetch': url})
            reply = json.loads(source.readline(MAX_LINE))
            if 'fetch_error' in reply:
                raise SourceError(reply['fetch_error'] if type(reply['fetch_error']) is str else 'provider_error')
            size = reply['bytes']
            if type(size) is not int or not 0 <= size <= response_bytes:
                raise WorkerError('worker_input_invalid')
            data = source.read(size)
            if len(data) != size or source.read(1) != b'\n':
                raise WorkerError('worker_input_invalid')
            return data
        try:
            if kind == 'open5e':
                from .scrying_glass_open5e_statblock import prepare_open5e
                snapshot, measurements = prepare_open5e(request['key'], fetch=fetch, deadline=deadline,
                                                        base_url=request['base_url'], limits=limits)
            elif kind == 'dndbeyond':
                from .scrying_glass_dndbeyond_statblock import prepare_dndbeyond
                snapshot, measurements = prepare_dndbeyond(request['path'], fetch=fetch, deadline=deadline, limits=limits)
            else:
                from .scrying_glass_tetracube_statblock import prepare_monster_file
                snapshot, measurements = prepare_monster_file(raw, filename=request.get('filename'), limits=limits,
                                                              deadline=deadline)
        except SourceError as exc:
            emit({'error': {'code': exc.code, 'detail': exc.detail if type(exc.detail) is str else None}})
            return
        payload = json.dumps({'snapshot': snapshot, 'measurements': measurements},
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
