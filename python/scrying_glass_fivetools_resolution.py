"""Exact-source inheritance core; modification execution remains 022.04c/d.

No network, persistence, JavaScript execution or public apply API. Instantiate
for one immutable configured dataset generation, inside a preparation worker.
"""
from __future__ import annotations
import json
import math
import time
from collections import OrderedDict
from dataclasses import dataclass, fields
from typing import Protocol
from .scrying_glass_fivetools_resolution_bounds import measure_json

RUNTIME_COMMIT = '32ef600fab87a585a61dd1a22e9b02dfc58c728a'
RUNTIME_BLOB = '80c10d0439a5179b7d7f6e1220b9efb535a626d2'
SCHEMA_COMMIT = '64e8ab38231972d8cc1572520978ccea92f17ecb'
COPY_SCHEMA_BLOB = '5842394edd2c1b47cebc6af27b06659964af2285'
TEMPLATE_SCHEMA_BLOB = '818c978880a75b02b4a8eebf768dd7554e5e056a'
MODES = frozenset(('replaceName replaceTxt appendStr prependArr appendArr '
    'appendIfNotExistsArr insertArr replaceArr replaceOrAppendArr removeArr '
    'renameArr setProp calculateProp scalarAddProp scalarMultProp '
    'prefixSuffixStringProp addSenses addSaves addAllSaves addSkills addAllSkills '
    'addSpells replaceSpells removeSpells scalarAddHit scalarAddDc maxSize scalarMultXp').split())
COPY_ENTRY_PROPS = ('action', 'bonus', 'reaction', 'trait', 'legendary', 'mythic',
    'variant', 'spellcasting', 'actionHeader', 'bonusHeader', 'reactionHeader',
    'legendaryHeader', 'mythicHeader')
PRESERVE_BASE = frozenset(('page otherSources referenceSources srd srd52 basicRules '
    'basicRules2024 reprintedAs hasFluff hasFluffImages hasToken tokenCredit '
    'tokenCustom foundryTokenScale altArt _versions').split())
PRESERVE_MONSTER = frozenset(('legendaryGroup environment soundClip altArt variant '
    'dragonCastingColor familiar').split())

@dataclass(frozen=True)
class Identity:
    dataset: str
    kind: str
    source: str
    name: str
    discriminator: str | None = None
    edition: str | None = None
    def __post_init__(self):
        for f in fields(self):
            v = getattr(self, f.name)
            if v is None and f.name in {'discriminator', 'edition'}:
                continue
            if type(v) is not str or not v.strip() or '\x00' in v:
                raise ValueError('invalid_identity:' + f.name)
            try:
                v.encode('utf-8')
            except UnicodeError as exc:
                raise ValueError('invalid_identity:' + f.name) from exc

@dataclass(frozen=True)
class Diagnostic:
    code: str
    selected: Identity
    chain: tuple[Identity, ...]
    source_path: str
    property: str | None = None
    operation_index: int | None = None
    mode: str | None = None

class ResolutionError(ValueError):
    def __init__(self, diagnostic):
        self.diagnostic = diagnostic
        super().__init__(diagnostic.code)

@dataclass(frozen=True)
class Limits:
    inheritance_steps: int = 16
    modification_operations: int = 1024
    intermediate_creature_bytes: int = 8388608
    response_bytes: int = 10485760
    cache_entries: int = 64
    cache_bytes: int = 67108864
    cache_seconds: int = 3600
    def __post_init__(self):
        for f in fields(self):
            v = getattr(self, f.name)
            if type(v) is not int or not 0 < v <= 2**63 - 1:
                raise ValueError('invalid_limit:' + f.name)

@dataclass(frozen=True)
class Provenance:
    identity: Identity
    role: str
    chain: tuple[Identity, ...]

@dataclass(frozen=True)
class Result:
    record_json: bytes
    provenance: tuple[Provenance, ...]
    inheritance_depth: int
    modification_operations: int
    def record(self):
        return json.loads(self.record_json)

def _cache_entry_bytes(identity, result):
    """Logical retained content bytes, not Python heap/RSS or loader storage.

    Count raw record bytes plus compact UTF-8 metadata: full cache key, every
    provenance identity/role/path occurrence, cached logical depth and work.
    Repeated identities are charged per occurrence; object sharing earns no
    discount. LRU links, TTL timestamps and Python allocator overhead are not
    content. The adapter/worker must separately enforce its memory ceiling.
    """
    def key(item):
        return tuple(getattr(item, f.name) for f in fields(item))
    metadata = {
        'key': key(identity),
        'provenance': [(key(p.identity), p.role, [key(i) for i in p.chain])
                       for p in result.provenance],
        'depth': result.inheritance_depth,
        'operations': result.modification_operations,
    }
    encoder = json.JSONEncoder(ensure_ascii=False, allow_nan=False, separators=(',', ':'))
    return len(result.record_json) + sum(len(s.encode('utf-8')) for s in encoder.iterencode(metadata))

class ExactLoader(Protocol):
    def load(self, identity: Identity) -> tuple[bytes, ...]:
        """Return all exact matches; never search or substitute editions."""
        ...

class DatasetLoader:
    """Immutable exact-record index; provider supplies already bounded bytes."""
    def __init__(self, dataset: str, records):
        if type(dataset) is not str or not dataset.strip():
            raise ValueError('invalid_dataset')
        grouped = {}
        for identity, payload in records:
            if not isinstance(identity, Identity) or identity.dataset != dataset or type(payload) is not bytes:
                raise ValueError('invalid_dataset_record')
            grouped.setdefault(identity, []).append(payload)
        self._records = {k: tuple(v) for k, v in grouped.items()}
    def load(self, identity: Identity) -> tuple[bytes, ...]:
        return self._records.get(identity, ())

@dataclass(frozen=True)
class Instruction:
    property: str
    index: int
    mode: str
    payload_json: bytes
    chain: tuple[Identity, ...] = ()

def compile_modifications(mods, *, check=lambda: None):
    """Freeze instructions in stable ordinary-property order, then _, then *."""
    if type(mods) is not dict or any(type(k) is not str for k in mods):
        raise ValueError('malformed_modifications')
    out = []
    for prop in sorted(mods, key=lambda k: 1 if k == '_' else 2 if k == '*' else 0):
        check()
        values = mods[prop] if type(mods[prop]) is list else [mods[prop]]
        for i, value in enumerate(values):
            check()
            mode = value if type(value) is str else value.get('mode') if type(value) is dict else None
            if not (value == 'remove' if type(value) is str else type(mode) is str and mode in MODES):
                raise ValueError('unknown_modification_mode', prop, i, mode if type(mode) is str else None)
            try:
                payload = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode()
            except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
                raise ValueError('malformed_modification', prop, i, mode) from exc
            out.append(Instruction(prop, i, mode, payload))
    return tuple(out)

class Resolver:
    """Caller supplies the existing absolute monotonic preparation deadline.

    Cache limits count record and identity/provenance content via a logical
    UTF-8 ledger. They do not enforce total Python heap or worker memory.
    """
    def __init__(self, loader: ExactLoader, *, limits=None, clock=time.monotonic):
        self.loader, self.limits, self.clock = loader, Limits() if limits is None else limits, clock
        if not isinstance(self.limits, Limits):
            raise ValueError('invalid_limits')
        self._cache, self._cache_times = OrderedDict(), {}
        self._cache_bytes = 0
        self._cache_limits = self.limits

    def _apply_compiled_modifications(self, record, mods, *, check, fail):
        item = mods[0]
        fail('modification_execution_pending_04c', '$/_copy/_mod', item.property, item.index, item.mode)

    def resolve(self, selected: Identity, *, deadline: float, cancelled=lambda: False):
        if not isinstance(selected, Identity):
            raise ValueError('invalid_selected_identity')
        if type(deadline) not in (int, float) or not math.isfinite(deadline):
            raise ValueError('invalid_deadline')
        if not isinstance(self.limits, Limits):
            raise ValueError('invalid_limits')
        if not callable(cancelled) or not callable(self.clock):
            raise ValueError('invalid_callback')
        if self.limits != self._cache_limits:
            self._cache.clear()
            self._cache_times.clear()
            self._cache_bytes = 0
            self._cache_limits = self.limits
        path, pending, used = [], OrderedDict(), 0
        def fail(code, source_path='$', prop=None, index=None, mode=None, *, chain=None):
            raise ResolutionError(Diagnostic(code, selected, tuple(path) if chain is None else chain, source_path, prop, index, mode))
        def now():
            value = self.clock()
            if type(value) not in (int, float) or not math.isfinite(value):
                fail('invalid_clock')
            return value
        def check():
            if cancelled():
                fail('cancelled')
            if now() >= deadline:
                fail('deadline')
        def charge(amount):
            nonlocal used
            used += amount
            if used > self.limits.modification_operations:
                fail('modification_operations_limit')
        def size(obj):
            return measure_json(obj, self.limits.intermediate_creature_bytes, check, fail)
        def assign(obj, key, value):
            projected = size(obj)
            if key in obj:
                projected -= size(obj[key])
            else:
                projected += size(key) + 1 + bool(obj)
            projected += size(value)
            if projected > self.limits.intermediate_creature_bytes:
                fail('intermediate_creature_bytes_limit')
            obj[key] = value
        def encode(obj):
            size(obj)
            parts, total = [], 0
            try:
                for piece in json.JSONEncoder(ensure_ascii=False, allow_nan=False, separators=(',', ':')).iterencode(obj):
                    check()
                    if len(piece) > self.limits.intermediate_creature_bytes - total:
                        fail('intermediate_creature_bytes_limit')
                    chunk = piece.encode('utf-8')
                    total += len(chunk)
                    if total > self.limits.intermediate_creature_bytes:
                        fail('intermediate_creature_bytes_limit')
                    parts.append(chunk)
            except (TypeError, ValueError, UnicodeError, RecursionError) as exc:
                if isinstance(exc, ResolutionError):
                    raise
                fail('malformed_record')
            return b''.join(parts)
        def identity(meta, owner, kind):
            if type(meta) is not dict:
                fail('malformed_identity', '$/_copy')
            try:
                return Identity(owner.dataset, kind, meta['source'], meta['name'], meta.get('discriminator'), meta.get('edition'))
            except (ValueError, KeyError, TypeError):
                fail('malformed_identity', '$/_copy')
        def instructions(mods, origin=None):
            try:
                if type(mods) is not dict:
                    fail('malformed_modifications', '$/apply/_mod' if origin else '$/_copy/_mod', chain=origin)
                for value in mods.values():
                    check()
                    charge(len(value) if type(value) is list else 1)
                return [Instruction(x.property, x.index, x.mode, x.payload_json,
                    tuple(path) if origin is None else origin) for x in compile_modifications(mods, check=check)]
            except ResolutionError:
                raise
            except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
                args = exc.args
                fail(args[0] if args else 'malformed_modifications', '$/apply/_mod' if origin else '$/_copy/_mod',
                     *(list(args[1:4]) + [None] * 3)[:3], chain=origin)
        def visit(ident, depth):
            check()
            path.append(ident)
            try:
                if ident in path[:-1]:
                    fail('inheritance_cycle')
                if depth > self.limits.inheritance_steps:
                    fail('inheritance_steps_limit')
                if ident in self._cache and now() - self._cache_times[ident] >= self.limits.cache_seconds:
                    self._cache_bytes -= _cache_entry_bytes(ident, self._cache.pop(ident))
                    self._cache_times.pop(ident, None)
                cached = pending.get(ident) or self._cache.get(ident)
                if ident in self._cache:
                    self._cache.move_to_end(ident)
                if cached is not None:
                    if depth + cached.inheritance_depth > self.limits.inheritance_steps:
                        fail('inheritance_steps_limit')
                    charge(cached.modification_operations)
                    check()
                    return cached
                matches = self.loader.load(ident)
                check()
                if type(matches) is not tuple or any(type(v) is not bytes for v in matches):
                    fail('malformed_loader_result')
                if len(matches) != 1:
                    fail('missing_dependency' if not matches else 'ambiguous_dependency')
                raw = matches[0]
                if len(raw) > self.limits.response_bytes:
                    fail('response_bytes_limit')
                def pairs(items):
                    out = {}
                    for k, v in items:
                        if k in out:
                            raise ValueError('duplicate_json_key')
                        out[k] = v
                    return out
                try:
                    obj = json.loads(raw, object_pairs_hook=pairs,
                        parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
                except (ValueError, UnicodeError, RecursionError):
                    fail('malformed_record')
                if type(obj) is not dict or identity(obj, ident, ident.kind) != ident:
                    fail('identity_mismatch')
                encode(obj)
                initial_used, provenance, relative_depth = used, [], 0
                if '_copy' in obj:
                    meta = obj['_copy']
                    base_id = identity(meta, ident, ident.kind)
                    base = visit(base_id, depth + 1)
                    relative_depth = base.inheritance_depth + 1
                    provenance.append(Provenance(base_id, 'base', (ident, base_id)))
                    provenance.extend(Provenance(p.identity, p.role, (ident,) + p.chain) for p in base.provenance)
                    templates, preserve = meta.get('_templates', []), meta.get('_preserve', {})
                    if type(templates) is not list or type(preserve) is not dict or any(v is not True for v in preserve.values()):
                        fail('malformed_copy_metadata', '$/_copy')
                    if templates:
                        assign(obj, '_copy_templates', [])
                        for t in templates:
                            entry = {'name': t.get('name'), 'source': t.get('source')} if type(t) is dict else {}
                            values = obj['_copy_templates']
                            if size(obj) + size(entry) + bool(values) > self.limits.intermediate_creature_bytes:
                                fail('intermediate_creature_bytes_limit')
                            values.append(entry)
                    original_keys = frozenset(obj)
                    mods = instructions(meta.get('_mod', {}))
                    gated = PRESERVE_BASE | (PRESERVE_MONSTER if ident.kind == 'monster' else frozenset())
                    for k, v in base.record().items():
                        check()
                        if k in obj and obj[k] is None:
                            charge(1)
                            del obj[k]
                        elif k not in obj and (k not in gated or preserve.get('*') or preserve.get(k)):
                            assign(obj, k, v)
                    for tm in templates:
                        check()
                        if ident.kind not in {'monster', 'legendaryGroup'}:
                            fail('unsupported_template_kind')
                        tid = identity(tm, ident, ident.kind + 'Template')
                        resolved = visit(tid, depth)
                        relative_depth = max(relative_depth, resolved.inheritance_depth)
                        provenance.append(Provenance(tid, 'template', (ident, tid)))
                        provenance.extend(Provenance(p.identity, p.role, (ident,) + p.chain) for p in resolved.provenance)
                        apply = resolved.record().get('apply')
                        if type(apply) is not dict or type(apply.get('_root', {})) is not dict:
                            fail('malformed_template')
                        for k, v in apply.get('_root', {}).items():
                            check()
                            if k not in original_keys:
                                assign(obj, k, v)
                        mods.extend(instructions(apply.get('_mod', {}), tuple(path)+(tid,)))
                    if mods:
                        obj = self._apply_compiled_modifications(obj, mods, check=check, fail=fail)
                    obj.pop('_copy', None)
                    assign(obj, '_isCopy', True)
                result = Result(encode(obj), tuple(provenance), relative_depth, used - initial_used)
                pending[ident] = result
                while len(pending) > self.limits.cache_entries or sum(_cache_entry_bytes(k, v) for k, v in pending.items()) > self.limits.cache_bytes:
                    pending.popitem(last=False)
                return result
            except RecursionError:
                fail('execution_stack_limit')
            finally:
                path.pop()
        result = visit(selected, 0)
        check()
        cache, cache_times, cache_bytes = self._cache.copy(), self._cache_times.copy(), self._cache_bytes
        for ident, item in pending.items():
            check()
            amount = _cache_entry_bytes(ident, item)
            if amount > self.limits.cache_bytes:
                continue
            previous = cache.pop(ident, None)
            if previous is not None:
                cache_bytes -= _cache_entry_bytes(ident, previous)
            cache[ident], cache_times[ident] = item, now()
            cache_bytes += amount
            while len(cache) > self.limits.cache_entries or cache_bytes > self.limits.cache_bytes:
                old_id, evicted = cache.popitem(last=False)
                cache_times.pop(old_id, None)
                cache_bytes -= _cache_entry_bytes(old_id, evicted)
        check()
        output = Result(result.record_json, (Provenance(selected, 'selected', (selected,)),) + result.provenance,
                        result.inheritance_depth, result.modification_operations)
        check()
        self._cache, self._cache_times, self._cache_bytes = cache, cache_times, cache_bytes
        return output
