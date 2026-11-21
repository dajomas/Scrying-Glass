"""JavaScript value semantics needed by the pinned 5e.tools copy runtime.

Pure helpers for the 022.04 interpreter: Number()/ToString() conversions,
strict equality, key order, sorting and the Parser tables the runtime uses.
Values outside the supported JSON domain fail through the caller's ``fail``
callback instead of being silently coerced. Pinned to RUNTIME_COMMIT in
scrying_glass_fivetools_resolution (5etools-src 32ef600, js/parser.js and
js/utils.js).
"""
import math
import re

MAX_SAFE = 9007199254740991
# ECMAScript WhiteSpace + LineTerminator (String.prototype.trim / StringToNumber).
JS_SPACE = '\t\n\x0b\x0c\r \xa0                　﻿'
_DECIMAL = re.compile(r'[+-]?(?:(?:[0-9]+(?:\.[0-9]*)?)|(?:\.[0-9]+))(?:[eE][+-]?[0-9]+)?\Z')
_RADIX = re.compile(r'0([xXoObB])([0-9A-Za-z]+)\Z')
_UNSAFE_KEYS = frozenset(('__proto__', 'constructor', 'prototype', 'hasOwnProperty',
                          'toString', 'valueOf', '__defineGetter__', '__defineSetter__',
                          '__lookupGetter__', '__lookupSetter__', 'isPrototypeOf',
                          'propertyIsEnumerable', 'toLocaleString'))

SIZE_ABVS = ('T', 'S', 'M', 'L', 'H', 'G', 'V')
ABIL_ABVS = ('str', 'dex', 'con', 'int', 'wis', 'cha')
SKILL_TO_ABILITY = {
    'athletics': 'str', 'acrobatics': 'dex', 'sleight of hand': 'dex', 'stealth': 'dex',
    'arcana': 'int', 'history': 'int', 'investigation': 'int', 'nature': 'int',
    'religion': 'int', 'animal handling': 'wis', 'insight': 'wis', 'medicine': 'wis',
    'perception': 'wis', 'survival': 'wis', 'deception': 'cha', 'intimidation': 'cha',
    'performance': 'cha', 'persuasion': 'cha',
}
XP_CHART = {
    '0': 10, '1/8': 25, '1/4': 50, '1/2': 100, '1': 200, '2': 450, '3': 700,
    '4': 1100, '5': 1800, '6': 2300, '7': 2900, '8': 3900, '9': 5000, '10': 5900,
    '11': 7200, '12': 8400, '13': 10000, '14': 11500, '15': 13000, '16': 15000,
    '17': 18000, '18': 20000, '19': 22000, '20': 25000, '21': 33000, '22': 41000,
    '23': 50000, '24': 62000, '25': 75000, '26': 90000, '27': 105000, '28': 120000,
    '29': 135000, '30': 155000,
}
SPELL_USES_KEYS = frozenset(str(i) for i in range(1, 100)) | frozenset(f'{i}e' for i in range(1, 100))
CR_UNKNOWN, CR_CUSTOM = 100001, 100000


def is_number(value):
    return type(value) in (int, float)


def check_number(value, fail):
    """Reject values JS would not hold exactly as a finite double."""
    if type(value) is int and abs(value) > MAX_SAFE:
        fail('unsupported_numeric_value')
    if type(value) is float and not math.isfinite(value):
        fail('unsupported_numeric_value')
    return value


def truthy(value):
    return not (value is None or value is False or value == '' or
                (type(value) in (int, float) and value == 0))


def to_number(value, fail):
    """ECMAScript Number(value) for JSON values; NaN is returned as float nan."""
    if value is None:
        return 0
    if type(value) is bool:
        return int(value)
    if type(value) in (int, float):
        return check_number(value, fail)
    if type(value) is str:
        text = value.strip(JS_SPACE)
        if text == '':
            return 0
        if text in ('Infinity', '+Infinity', '-Infinity'):
            return math.inf if text[0] != '-' else -math.inf
        match = _RADIX.match(text)
        if match:
            base = {'x': 16, 'o': 8, 'b': 2}[match.group(1).lower()]
            try:
                number = int(match.group(2), base)
            except ValueError:
                return math.nan
            return float(number) if number > MAX_SAFE else number
        if not _DECIMAL.match(text):
            return math.nan
        if re.fullmatch(r'[+-]?[0-9]+', text) and abs(int(text)) <= MAX_SAFE:
            return int(text)
        return float(text)
    fail('unsupported_numeric_coercion')


def number_to_string(value):
    """ECMAScript Number::toString(10) for a finite or nonfinite number."""
    if type(value) is bool or type(value) not in (int, float):
        raise TypeError('number_required')
    if type(value) is float and math.isnan(value):
        return 'NaN'
    if type(value) is float and math.isinf(value):
        return 'Infinity' if value > 0 else '-Infinity'
    if value == 0:
        return '0'
    if type(value) is int and abs(value) < 10**21:
        return str(value)
    sign = '-' if value < 0 else ''
    text = repr(abs(float(value)))
    mantissa, _, exponent = text.partition('e')
    whole, _, fraction = mantissa.partition('.')
    digits = (whole + fraction).lstrip('0')
    point = len(whole) + (int(exponent) if exponent else 0)
    if whole == '0':
        stripped = fraction.lstrip('0')
        point = -(len(fraction) - len(stripped)) + (int(exponent) if exponent else 0)
        digits = stripped
    digits = digits.rstrip('0') or '0'
    k, n = len(digits), point
    if k <= n <= 21:
        return sign + digits + '0' * (n - k)
    if 0 < n <= 21:
        return sign + digits[:n] + '.' + digits[n:]
    if -6 < n <= 0:
        return sign + '0.' + '0' * (-n) + digits
    e = n - 1
    body = digits[0] + ('.' + digits[1:] if k > 1 else '')
    return f'{sign}{body}e{"+" if e > 0 else "-"}{abs(e)}'


def to_display_string(value, fail):
    """Template-literal ToString for JSON scalars used in generated text."""
    if type(value) is str:
        return value
    if value is None:
        return 'null'
    if type(value) is bool:
        return 'true' if value else 'false'
    if type(value) in (int, float):
        return number_to_string(check_number(value, fail))
    fail('unsupported_string_coercion')


def strict_equal(left, right):
    """JS === for JSON values; separately decoded objects/arrays never match."""
    if type(left) in (dict, list) or type(right) in (dict, list):
        return False
    if type(left) is bool or type(right) is bool:
        return type(left) is type(right) and left is right
    if left is None or right is None:
        return left is right
    if type(left) in (int, float) and type(right) in (int, float):
        return left == right
    return type(left) is str and type(right) is str and left == right


def number_result(value, fail):
    """Normalize a computed finite number to the JSON domain (int when integral)."""
    if type(value) is float:
        if not math.isfinite(value):
            fail('nonfinite_numeric_result')
        if value.is_integer() and abs(value) <= MAX_SAFE:
            return int(value)
        return value
    return check_number(value, fail)


def array_index_key(key):
    return (type(key) is str and key.isascii() and key.isdecimal() and
            str(int(key)) == key and int(key) < 4294967295)


def object_keys(obj):
    """Object.keys order: array-index keys ascending, then insertion order."""
    keys = list(obj)
    indices = sorted((k for k in keys if array_index_key(k)), key=int)
    return indices + [k for k in keys if not array_index_key(k)]


def safe_key(key, fail):
    if type(key) is not str or key in _UNSAFE_KEYS:
        fail('unsafe_modification_key')
    return key


def utf16_key(text):
    return text.encode('utf-16-be', 'surrogatepass')


def sort_lower(values, fail):
    """SortUtil.ascSortLower over strings (stable, UTF-16 code-unit order)."""
    for value in values:
        if value is not None and type(value) is not str:
            fail('unsupported_sort_value')
    def key(value):
        if value is None:
            return (0, b'')
        return (1, utf16_key(value.lower() if value else value))
    return sorted(values, key=key)


def ability_mod(score, fail):
    """Parser.getAbilityModNumber(score) with Number coercion of the score."""
    number = to_number(score, fail)
    if type(number) is float and not math.isfinite(number):
        fail('nonfinite_numeric_result')
    return math.floor((number - 10) / 2)


def ability_mod_of(record, key, fail):
    """getAbilityModNumber(record[key]); a missing key is undefined (NaN)."""
    if type(record) is not dict or key not in record:
        fail('nonfinite_numeric_result')
    return ability_mod(record[key], fail)


def cr_to_number(cr, fail):
    if cr is None or cr == 'Unknown' or cr == '—':
        return CR_UNKNOWN
    if type(cr) is dict:
        inner = cr.get('cr')
        if truthy(inner):
            return cr_to_number(inner, fail)
        fail('unsupported_cr_value')
    if type(cr) is not str:
        fail('unsupported_cr_value')
    parts = [p for p in cr.strip(JS_SPACE).split('/') if p]
    if not parts or len(parts) >= 3:
        return CR_CUSTOM
    first = to_number(parts[0], fail)
    if type(first) is float and math.isnan(first):
        return CR_CUSTOM
    if len(parts) == 2:
        second = to_number(parts[1], fail)
        if type(second) is float and math.isnan(second):
            return CR_CUSTOM
        if second == 0:
            fail('nonfinite_numeric_result')
        return first / second
    return first


def cr_to_pb(cr, fail):
    """Parser.crToPb; None stands for the runtime's null (custom/negative CR)."""
    number = cr_to_number(cr, fail)
    if number == CR_UNKNOWN:
        return 0
    if number == CR_CUSTOM or number < 0:
        return None
    if number < 5:
        return 2
    return math.ceil(number / 4) + 1


def cr_to_xp_number(cr):
    if type(cr) is dict and truthy(cr.get('xp')):
        return cr['xp']
    convert = (cr.get('cr') if truthy(cr.get('cr')) else cr) if type(cr) is dict else cr
    if convert is None or convert == 'Unknown':
        return None
    return XP_CHART.get(convert) if type(convert) is str else None


def skill_to_ability(skill, fail):
    if type(skill) is not str:
        fail('unsupported_skill_key')
    text = skill.strip(JS_SPACE)
    if text in _UNSAFE_KEYS:
        fail('unsafe_modification_key')
    return SKILL_TO_ABILITY.get(text, text)


def js_floor(value, fail):
    if type(value) is float and not math.isfinite(value):
        fail('nonfinite_numeric_result')
    return math.floor(value)
