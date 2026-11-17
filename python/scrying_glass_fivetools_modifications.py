"""Pure ordered property/array executor; used by OrderedResolver and its worker.

Consumes compiler-shaped immutable instructions (property, mode, payload_json)
and executes every mode of the pinned runtime (5etools-src 32ef600): the literal
and array modes here, the remaining general modes in
scrying_glass_fivetools_general_modes and the creature modes in
scrying_glass_fivetools_creature_modes. Dynamic ``<$...$>`` payload text is
resolved first against the record (scrying_glass_fivetools_substitutions),
as upstream does before any _mod runs. No selected-identity normalization or
networking. Caller supplies its deadline/cancellation check; OrderedResolver
wraps local diagnostics in graph provenance and the ordered worker enforces
process limits.
"""
import copy
import json
from dataclasses import dataclass
from .scrying_glass_fivetools_resolution_bounds import measure_json, json_equal
from .scrying_glass_fivetools_general_modes import GENERAL_MODES
from .scrying_glass_fivetools_creature_modes import CREATURE_MODES
from .scrying_glass_fivetools_substitutions import resolve_payload

ENTRY_PROPS = ('action', 'bonus', 'reaction', 'trait', 'legendary', 'mythic',
    'variant', 'spellcasting', 'actionHeader', 'bonusHeader', 'reactionHeader',
    'legendaryHeader', 'mythicHeader')
LITERAL_MODES = frozenset(('appendStr', 'setProp', 'prefixSuffixStringProp'))
ARRAY_MODES = frozenset(('appendArr', 'prependArr', 'appendIfNotExistsArr', 'insertArr'))
SUPPORTED_MODES = (LITERAL_MODES | ARRAY_MODES | frozenset(('remove',)) |
                   frozenset(GENERAL_MODES) | frozenset(CREATURE_MODES))

@dataclass(frozen=True)
class OperationDiagnostic:
    code: str
    property: str | None
    operation_index: int | None
    mode: str | None
    source_path: str

class ModificationError(ValueError):
    def __init__(self, diagnostic):
        self.diagnostic = diagnostic
        super().__init__(diagnostic.code)

def apply_modifications(record, instructions, *, check,
                        intermediate_creature_bytes=8388608,
                        modification_operations=1024):
    """Return an independent result; failures never mutate caller-owned data.

    Ordinary groups keep first-seen order, then _, then *. Selected/template
    instruction sequences must be supplied in append order; each group is merged
    before execution, and wildcard targets are property-major as upstream does.
    Charge logical input instructions (including no-ops) once, not 13 times for
    the fixed wildcard expansion. Array holes/coercive truthy non-string appends,
    dangerous/empty path segments and JavaScript TypeError/NaN outcomes fail
    explicitly instead of producing partially modified data.
    """
    for limit in (intermediate_creature_bytes, modification_operations):
        if type(limit) is not int or not 0 < limit <= 2**63-1:
            raise ValueError('invalid_modification_limit')
    if not callable(check) or type(record) is not dict or type(instructions) not in (tuple, list):
        raise ValueError('invalid_modification_input')
    context = [None, None, None]
    def fail(code):
        prop, index, mode = context
        path = '$/_copy/_mod' if prop is None else '$/_copy/_mod/'+prop.replace('~', '~0').replace('/', '~1')
        raise ModificationError(OperationDiagnostic(code, prop, index, mode, path))
    def size(value):
        try:
            return measure_json(value, intermediate_creature_bytes, check, fail)
        except RecursionError:
            fail('execution_stack_limit')
    def truth(value):
        return value is not None and value is not False and not (type(value) in (int, float) and value == 0) and not (type(value) is str and value == '')
    def path(text):
        if text is None or text == '':
            return ()
        if type(text) is not str:
            fail('malformed_modification_path')
        parts = tuple(text.split('.'))
        for part in parts:
            check()
            if not part or part in {'__proto__', 'prototype', 'constructor'}:
                fail('unsafe_modification_path')
        return parts
    def index(key, values):
        if len(key) > len(str(len(values))) or not key.isascii() or not key.isdecimal() or str(int(key)) != key:
            fail('unsupported_modification_path')
        number = int(key)
        if number >= len(values):
            fail('unsupported_modification_path')
        return number
    def get(obj, keys):
        for key in keys:
            check()
            if obj is None:
                return None
            if type(obj) is dict:
                obj = obj.get(key)
            elif type(obj) is list:
                if key.isascii() and key.isdecimal() and len(key) < 10 and str(int(key)) == key and int(key) >= len(obj):
                    return None
                obj = obj[index(key, obj)]
            else:
                if type(obj) is str and obj:
                    fail('unsupported_modification_path')
                return None
        return obj
    def put(obj, keys, value):
        check()
        key, *tail = keys
        if type(obj) is dict:
            result, slot = obj.copy(), key
            current = obj.get(key)
        elif type(obj) is list:
            slot = index(key, obj)
            result, current = obj.copy(), obj[slot]
        else:
            fail('unsupported_modification_path')
        try:
            result[slot] = put(current if truth(current) else {}, tail, value) if tail else value
        except RecursionError:
            fail('execution_stack_limit')
        return result
    def remove(obj, keys):
        check()
        if obj is None:
            return obj
        key, *tail = keys
        if type(obj) is dict:
            if key not in obj:
                return obj
            result, slot = obj.copy(), key
        elif type(obj) is list:
            slot = index(key, obj)
            if not tail:
                fail('unsupported_modification_path')
            result = obj.copy()
        else:
            fail('unsupported_modification_path')
        if tail:
            try:
                result[slot] = remove(obj[slot], tail)
            except RecursionError:
                fail('execution_stack_limit')
        else:
            del result[slot]
        return result
    def string_option(info, key):
        value = info.get(key)
        if value is None:
            return ''
        if type(value) is not str:
            fail('malformed_modification_payload')
        return value
    check()
    if len(instructions) > modification_operations:
        fail('modification_operations_limit')
    size(record)
    output = json.loads(json.dumps(record, ensure_ascii=False, allow_nan=False, separators=(',', ':')))
    groups = {}
    for instruction in instructions:
        check()
        if type(getattr(instruction, 'property', None)) is not str or type(getattr(instruction, 'payload_json', None)) is not bytes or type(getattr(instruction, 'mode', None)) is not str:
            fail('malformed_modification_instruction')
        groups.setdefault(instruction.property, []).append(instruction)
    resolved = {}
    for prop, group in groups.items():
        for ordinal, instruction in enumerate(group):
            context[:] = prop, ordinal, instruction.mode
            if instruction.mode not in SUPPORTED_MODES:
                fail('unknown_modification_mode')
            try:
                payload = json.loads(instruction.payload_json, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
            except (ValueError, UnicodeError, RecursionError):
                fail('malformed_modification_payload')
            try:
                payload = resolve_payload(payload, output, fail, check)
            except RecursionError:
                fail('execution_stack_limit')
            resolved[id(instruction)] = payload
    state = _State(output, fail, check, size, intermediate_creature_bytes, get, put)
    for prop in sorted(groups, key=lambda p: 1 if p == '_' else 2 if p == '*' else 0):
        for target in ENTRY_PROPS if prop == '*' else (prop,):
            for ordinal, instruction in enumerate(groups[prop]):
                context[:] = prop, ordinal, instruction.mode
                check()
                info = copy.deepcopy(resolved[id(instruction)])
                if instruction.mode == 'remove':
                    if info != 'remove':
                        fail('malformed_modification_payload')
                    keys = ('null',) if target == '_' else path(target)
                    if not keys:
                        fail('unsafe_modification_path')
                    proposed = remove(output, keys)
                    size(proposed)
                    output = proposed
                    continue
                if type(info) is not dict or info.get('mode') != instruction.mode:
                    fail('malformed_modification_payload')
                keys = () if target == '_' else path(target)
                if instruction.mode in CREATURE_MODES or instruction.mode in GENERAL_MODES:
                    state.output = output
                    state.begin()
                    try:
                        if instruction.mode in CREATURE_MODES:
                            CREATURE_MODES[instruction.mode](state, info)
                        else:
                            GENERAL_MODES[instruction.mode](state, keys, info)
                    except RecursionError:
                        fail('execution_stack_limit')
                    output = state.output
                    size(output)
                    continue
                if instruction.mode in LITERAL_MODES - {'appendStr'}:
                    keys += path(info.get('prop'))
                if not keys:
                    if instruction.mode in ARRAY_MODES or instruction.mode == 'appendStr':
                        fail('malformed_modification_path')
                    continue
                old = get(output, keys)
                if instruction.mode in ARRAY_MODES:
                    if 'items' not in info:
                        fail('malformed_modification_payload')
                    items = info['items'] if type(info['items']) is list else [info['items']]
                    if instruction.mode == 'insertArr' and not truth(old):
                        fail('missing_modification_target')
                    if truth(old) and type(old) is not list:
                        fail('unsupported_modification_target')
                    existing = old if type(old) is list else []
                    proposed = put(output, keys, [])
                    if instruction.mode == 'appendIfNotExistsArr':
                        json_equal(existing, existing, check, fail)
                        filtered = []
                        projected = size(proposed) + size(existing)-2
                        for item in items:
                            check()
                            json_equal(item, item, check, fail)
                            if any(json_equal(item, prior, check, fail) for prior in existing):
                                continue
                            projected += size(item) + bool(existing or filtered)
                            if projected > intermediate_creature_bytes:
                                fail('intermediate_creature_bytes_limit')
                            filtered.append(item)
                        items = filtered
                    projected = size(proposed) + size(existing)-2 + size(items)-2 + bool(existing and items)
                    if projected > intermediate_creature_bytes:
                        fail('intermediate_creature_bytes_limit')
                    if instruction.mode == 'insertArr':
                        position = insert_position(info.get('index'), len(existing), check, fail)
                        value = existing.copy()
                        value[position:position] = items
                    else:
                        value = items + existing if instruction.mode == 'prependArr' else existing + items
                    proposed = put(output, keys, value)
                elif instruction.mode == 'setProp':
                    if 'value' not in info:
                        fail('malformed_modification_payload')
                    proposed = put(output, keys, info['value'])
                else:
                    if instruction.mode == 'appendStr':
                        if type(info.get('str')) is not str:
                            fail('malformed_modification_payload')
                        if truth(old) and type(old) is not str:
                            fail('unsupported_modification_target')
                        parts = [old, string_option(info, 'joiner'), info['str']] if truth(old) else [info['str']]
                    else:
                        if type(old) is not str:
                            continue
                        parts = [string_option(info, 'prefix'), old, string_option(info, 'suffix')]
                    proposed = put(output, keys, '')
                    if size(proposed) + sum(size(part)-2 for part in parts) > intermediate_creature_bytes:
                        fail('intermediate_creature_bytes_limit')
                    proposed = put(output, keys, ''.join(parts))
                size(proposed)
                output = proposed
    check()
    return output

def insert_position(value, length, check, fail):
    """Pinned insertArr: ToInt32(index)==-1 appends, else splice clamps/truncates.

    Missing/null means zero. No boolean/string/object coercion or unsafe integer
    rounding; these leave an explicit diagnostic. length is an internal array len.
    """
    import math
    check()
    if value is None:
        value = 0
    if type(value) not in (int, float):
        fail('malformed_modification_index')
    if type(value) is int and abs(value) > 9007199254740991:
        fail('unsupported_modification_index')
    if not math.isfinite(value):
        fail('malformed_modification_index')
    number = math.trunc(value)
    if number & 0xFFFFFFFF == 0xFFFFFFFF:
        return length
    return min(number, length) if number >= 0 else max(length+number, 0)


class _State:
    """Mode context: the working copy, its accessors and the byte allowance.

    get/put keep MiscUtil.get/set path semantics; grow() charges text growth
    against the room measured when the operation started, so repeated
    replacements cannot allocate past the intermediate creature limit.
    """
    def __init__(self, output, fail, check, size, limit, get, put):
        self.output, self.fail, self.check = output, fail, check
        self._size, self._limit, self._get, self._put = size, limit, get, put
        self._room = 0
    def begin(self):
        self._room = self._limit - self._size(self.output)
    def record(self):
        return self.output
    def get(self, keys):
        return self._get(self.output, keys)
    def set(self, keys, value):
        self.output = self._put(self.output, keys, value)
    def room(self):
        return max(self._room, 0)
    def grow(self, delta):
        self._room -= delta
        if self._room < 0:
            self.fail('intermediate_creature_bytes_limit')
