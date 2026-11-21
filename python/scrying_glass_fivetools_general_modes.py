"""General copy modes completed in 022.04c.3c-04c.5 (pinned 5etools-src 32ef600).

replaceTxt/replaceName, replaceArr/replaceOrAppendArr, removeArr/renameArr,
scalarAddProp/scalarMultProp, calculateProp and the creature tag scalars
scalarAddHit/scalarAddDc. Each function mirrors the matching
``DataUtil.generic.copyApplier._doMod_*`` in js/utils.js on an already
independent working copy; JavaScript TypeErrors and NaN/Infinity results become
explicit diagnostics instead of partially applied or silently coerced data.
"""
import re

from .scrying_glass_fivetools_jsregex import JsRegex
from .scrying_glass_fivetools_jsvalues import (
    MAX_SAFE, array_index_key, check_number, is_number, number_result,
    number_to_string, object_keys, safe_key, strict_equal, to_number, truthy,
)
from .scrying_glass_fivetools_expressions import evaluate_clean_expression, clean_math_expression

HIT_TAG = re.compile(r'\{@hit ([-+]?[0-9]+)\}')
DC_TAG = re.compile(r'\{@dc ([0-9]+)(?:\|[^}]+)?\}')
FORMULA_VARIABLE = re.compile(r'<\$([^$]+)\$>')


def ensure_array(info, key, ctx):
    if key not in info:
        ctx.fail('malformed_modification_payload')
    value = info[key]
    return value if type(value) is list else [value]


def split_by_tags(text):
    """Renderer.splitByTags: top-level "{@"/"{=" tags become separate segments."""
    out, current, depth, i, n = [], '', 0, 0, len(text)
    while i < n:
        char = text[i]
        nxt = text[i + 1] if i + 1 < n else None
        if char == '{' and nxt in ('@', '='):
            if depth > 0:
                current += '{'
            else:
                if current:
                    out.append(current)
                current = '{' + nxt
                i += 1
            depth += 1
        elif char == '}':
            current += '}'
            if depth and depth - 1 == 0:
                depth = 0
                if current:
                    out.append(current)
                current = ''
            elif depth:
                depth -= 1
        else:
            current += char
        i += 1
    if current:
        out.append(current)
    return out


def walk_strings(value, handler, ctx):
    """MiscUtil walker with only a string handler; returns the walked value."""
    ctx.check()
    if type(value) is str:
        return handler(value)
    if type(value) is list:
        for index, item in enumerate(value):
            value[index] = walk_strings(item, handler, ctx)
    elif type(value) is dict:
        for key in list(value):
            value[key] = walk_strings(value[key], handler, ctx)
    return value


def _text_handler(info, ctx):
    pattern, flags, replacement = info.get('replace'), info.get('flags'), info.get('with')
    if type(pattern) is not str or type(replacement) is not str:
        ctx.fail('malformed_modification_payload')
    if flags is not None and type(flags) is not str:
        ctx.fail('malformed_modification_payload')
    regex = JsRegex(pattern, 'g' + (flags or ''), ctx.fail)
    insensitive = truthy(info.get('tagInsensitive'))
    def replace(text):
        old = len(text.encode('utf-8', 'surrogatepass'))
        result = regex.replace(text, replacement, budget=old + ctx.room(), check=ctx.check)
        ctx.grow(len(result.encode('utf-8', 'surrogatepass')) - old)
        return result
    def handler(text):
        if insensitive:
            return replace(text)
        return ''.join(part if part.startswith('{@') else replace(part) for part in split_by_tags(text))
    return handler


def _require_path(keys, ctx):
    if not keys:
        ctx.fail('malformed_modification_path')


def replace_txt(ctx, keys, info):
    _require_path(keys, ctx)
    ents = ctx.get(keys)
    if not truthy(ents):
        return
    handler = _text_handler(info, ctx)
    props = info.get('props') if truthy(info.get('props')) else [None, 'entries', 'headerEntries', 'footerEntries']
    if type(props) is not list or any(p is not None and type(p) is not str for p in props):
        ctx.fail('malformed_modification_payload')
    if not props:
        return
    if type(ents) is not list:
        ctx.fail('unsupported_modification_target')
    if None in props:
        mapped = [walk_strings(item, handler, ctx) if type(item) is str else item for item in ents]
        ctx.set(keys, mapped)
        ents = mapped
    for ent in ents:
        for prop in props:
            ctx.check()
            if prop is None:
                continue
            if ent is None:
                ctx.fail('unsupported_modification_target')
            if type(ent) in (str, list):
                if prop == 'length' or array_index_key(prop):
                    ctx.fail('unsupported_modification_target')
                continue
            if type(ent) is dict and truthy(ent.get(prop)):
                ent[prop] = walk_strings(ent[prop], handler, ctx)


def replace_name(ctx, keys, info):
    _require_path(keys, ctx)
    ents = ctx.get(keys)
    if not truthy(ents):
        return
    if type(ents) is not list:
        ctx.fail('unsupported_modification_target')
    handler = _text_handler(info, ctx)
    for ent in ents:
        ctx.check()
        if ent is None:
            ctx.fail('unsupported_modification_target')
        if type(ent) is dict and truthy(ent.get('name')):
            ent['name'] = walk_strings(ent['name'], handler, ctx)


def _list_target(ctx, keys, *, required):
    _require_path(keys, ctx)
    existing = ctx.get(keys)
    if not truthy(existing):
        if required:
            ctx.fail('missing_modification_target')
        return None
    if type(existing) is not list:
        ctx.fail('unsupported_modification_target')
    return existing


def _splice_start(index, length, ctx):
    """ToIntegerOrInfinity + relative clamp used by Array.prototype.splice."""
    import math
    if not is_number(index):
        ctx.fail('malformed_modification_index')
    check_number(index, ctx.fail)
    number = math.trunc(index)
    return min(number, length) if number >= 0 else max(length + number, 0)


def replace_arr(ctx, keys, info, *, raise_missing=True):
    items = ensure_array(info, 'items', ctx)
    existing = _list_target(ctx, keys, required=raise_missing)
    if existing is None:
        return False
    if 'replace' not in info or info['replace'] is None:
        ctx.fail('malformed_modification_payload')
    selector = info['replace']
    position = -1
    if type(selector) is dict and truthy(selector.get('regex')):
        regex = JsRegex(selector['regex'], selector.get('flags') or '', ctx.fail)
        for index, item in enumerate(existing):
            ctx.check()
            if item is None:
                ctx.fail('unsupported_modification_target')
            name = item.get('name') if type(item) is dict else None
            if truthy(name):
                if type(name) is not str:
                    ctx.fail('unsupported_modification_target')
                hit = regex.test(name)
            else:
                hit = regex.test(item) if type(item) is str else False
            if hit:
                position = index
                break
    elif type(selector) is dict and selector.get('index') is not None:
        index = selector['index']
        if not is_number(index):
            ctx.fail('malformed_modification_index')
        check_number(index, ctx.fail)
        import math
        int32 = math.trunc(index) & 0xFFFFFFFF
        position = -1 if int32 == 0xFFFFFFFF else _splice_start(index, len(existing), ctx)
    else:
        for index, item in enumerate(existing):
            ctx.check()
            if item is None:
                ctx.fail('unsupported_modification_target')
            name = item.get('name') if type(item) is dict else None
            if (strict_equal(name, selector) if truthy(name) else strict_equal(item, selector)):
                position = index
                break
    if position == -1:
        if raise_missing:
            ctx.fail('missing_modification_item')
        return False
    existing[position:position + 1] = items
    return True


def replace_or_append_arr(ctx, keys, info):
    if replace_arr(ctx, keys, info, raise_missing=False):
        return
    items = ensure_array(info, 'items', ctx)
    existing = ctx.get(keys)
    if truthy(existing) and type(existing) is not list:
        ctx.fail('unsupported_modification_target')
    ctx.set(keys, existing + items if truthy(existing) else items)


def remove_arr(ctx, keys, info):
    _require_path(keys, ctx)
    existing = ctx.get(keys)
    if type(existing) is not list:
        ctx.fail('missing_modification_target' if not truthy(existing) else 'unsupported_modification_target')
    if truthy(info.get('names')):
        for name in ensure_array(info, 'names', ctx):
            ctx.check()
            found = -1
            for index, item in enumerate(existing):
                if item is None:
                    ctx.fail('unsupported_modification_target')
                if type(item) is dict and 'name' in item and strict_equal(item['name'], name):
                    found = index
                    break
            if found >= 0:
                del existing[found]
            elif not truthy(info.get('force')):
                ctx.fail('missing_modification_item')
    elif truthy(info.get('items')):
        for target in ensure_array(info, 'items', ctx):
            ctx.check()
            found = next((i for i, item in enumerate(existing) if strict_equal(item, target)), -1)
            if found < 0:
                ctx.fail('missing_modification_item')
            del existing[found]
    else:
        ctx.fail('malformed_modification_payload')


def rename_arr(ctx, keys, info):
    renames = ensure_array(info, 'renames', ctx)
    existing = _list_target(ctx, keys, required=True)
    for rename in renames:
        ctx.check()
        if type(rename) is not dict or 'rename' not in rename or 'with' not in rename:
            ctx.fail('malformed_modification_payload')
        ent = next((item for item in existing if type(item) is dict and 'name' in item
                    and strict_equal(item['name'], rename['rename'])), None)
        if ent is None:
            ctx.fail('missing_modification_item')
        ent['name'] = rename['with']


def _scalar(ctx, keys, info, multiply):
    _require_path(keys, ctx)
    target = ctx.get(keys)
    if not truthy(target):
        return
    if type(target) is not dict:
        ctx.fail('unsupported_modification_target')
    scalar, prop = info.get('scalar'), info.get('prop')
    if not is_number(scalar) or type(prop) is not str:
        ctx.fail('malformed_modification_payload')
    check_number(scalar, ctx.fail)
    def apply_to(key):
        safe_key(key, ctx.fail)
        if key not in target:
            ctx.fail('nonfinite_numeric_result')
        current = target[key]
        number = to_number(current, ctx.fail)
        result = number * scalar if multiply else number + scalar
        if multiply and truthy(info.get('floor')):
            import math
            result = math.floor(result) if result == result and abs(result) != float('inf') else result
        result = number_result(result, ctx.fail)
        target[key] = (('+' if result >= 0 else '') + number_to_string(result)) if type(current) is str else result
    for key in (object_keys(target) if prop == '*' else [prop]):
        ctx.check()
        apply_to(key)


def scalar_add_prop(ctx, keys, info):
    _scalar(ctx, keys, info, False)


def scalar_mult_prop(ctx, keys, info):
    _scalar(ctx, keys, info, True)


def calculate_prop(ctx, keys, info):
    from .scrying_glass_fivetools_jsvalues import ability_mod_of, cr_to_pb, to_display_string
    _require_path(keys, ctx)
    target = ctx.get(keys)
    if target is None:
        ctx.set(keys, {})
        target = ctx.get(keys)
    formula, prop = info.get('formula'), info.get('prop')
    if type(formula) is not str or type(prop) is not str:
        ctx.fail('malformed_modification_payload')
    if type(target) is not dict:
        ctx.fail('unsupported_modification_target')
    record = ctx.record()
    def variable(match):
        name = match.group(1)
        if name == 'prof_bonus':
            pb = cr_to_pb(record.get('cr'), ctx.fail)
            return 'null' if pb is None else to_display_string(pb, ctx.fail)
        if name == 'dex_mod':
            return to_display_string(ability_mod_of(record, 'dex', ctx.fail), ctx.fail)
        ctx.fail('unknown_formula_variable')
    expression = FORMULA_VARIABLE.sub(variable, formula)
    target[safe_key(prop, ctx.fail)] = evaluate_clean_expression(clean_math_expression(expression), ctx.fail)


def _tag_scalar(ctx, keys, info, pattern, template):
    _require_path(keys, ctx)
    existing = ctx.get(keys)
    if not truthy(existing):
        return
    scalar = info.get('scalar')
    if not is_number(scalar):
        ctx.fail('malformed_modification_payload')
    check_number(scalar, ctx.fail)
    def handler(text):
        def sub(match):
            value = number_result(to_number(match.group(1), ctx.fail) + scalar, ctx.fail)
            if type(value) is int and abs(value) > MAX_SAFE:
                ctx.fail('unsupported_numeric_value')
            return template.format(number_to_string(value))
        result = pattern.sub(sub, text)
        ctx.grow(len(result.encode('utf-8', 'surrogatepass')) - len(text.encode('utf-8', 'surrogatepass')))
        return result
    ctx.set(keys, walk_strings(existing, handler, ctx))


def scalar_add_hit(ctx, keys, info):
    _tag_scalar(ctx, keys, info, HIT_TAG, '{{@hit {}}}')


def scalar_add_dc(ctx, keys, info):
    _tag_scalar(ctx, keys, info, DC_TAG, '{{@dc {}}}')


GENERAL_MODES = {
    'replaceTxt': replace_txt, 'replaceName': replace_name,
    'replaceArr': replace_arr, 'replaceOrAppendArr': replace_or_append_arr,
    'removeArr': remove_arr, 'renameArr': rename_arr,
    'scalarAddProp': scalar_add_prop, 'scalarMultProp': scalar_mult_prop,
    'calculateProp': calculate_prop, 'scalarAddHit': scalar_add_hit,
    'scalarAddDc': scalar_add_dc,
}
