"""04c.1 pure literal-property executor; graph/worker integration is 04c.2.

Consumes compiler-shaped immutable instructions (property, mode, payload_json).
No selected-identity normalization, substitutions, regex, formulas or networking.
Caller supplies its deadline/cancellation check; later integration must run inside
the existing limited worker and wrap local diagnostics in graph provenance.
"""
import json
from dataclasses import dataclass
from .scrying_glass_fivetools_resolution_bounds import measure_json

ENTRY_PROPS = ('action', 'bonus', 'reaction', 'trait', 'legendary', 'mythic',
    'variant', 'spellcasting', 'actionHeader', 'bonusHeader', 'reactionHeader',
    'legendaryHeader', 'mythicHeader')
LITERAL_MODES = frozenset(('appendStr', 'setProp', 'prefixSuffixStringProp'))

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
    dangerous/empty path segments and dynamic substitution fail explicitly.
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
    def string_option(info, key):
        value = info.get(key)
        if value is None:
            return ''
        if type(value) is not str:
            fail('malformed_modification_payload')
        return value
    def reject_dynamic(value):
        stack = [value]
        while stack:
            check()
            item = stack.pop()
            if type(item) is str and '<$' in item:
                fail('dynamic_substitution_pending_04d')
            if type(item) is dict:
                stack.extend(item.keys()); stack.extend(item.values())
            elif type(item) is list:
                stack.extend(item)
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
    for prop in sorted(groups, key=lambda p: 1 if p == '_' else 2 if p == '*' else 0):
        for target in ENTRY_PROPS if prop == '*' else (prop,):
            for ordinal, instruction in enumerate(groups[prop]):
                context[:] = prop, ordinal, instruction.mode
                check()
                if instruction.mode not in LITERAL_MODES:
                    fail('modification_execution_pending_04c')
                try:
                    info = json.loads(instruction.payload_json, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
                except (ValueError, UnicodeError, RecursionError):
                    fail('malformed_modification_payload')
                if type(info) is not dict or info.get('mode') != instruction.mode:
                    fail('malformed_modification_payload')
                reject_dynamic(info)
                keys = () if target == '_' else path(target)
                if instruction.mode != 'appendStr':
                    keys += path(info.get('prop'))
                if not keys:
                    if instruction.mode == 'appendStr':
                        fail('malformed_modification_path')
                    continue
                old = get(output, keys)
                if instruction.mode == 'setProp':
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
