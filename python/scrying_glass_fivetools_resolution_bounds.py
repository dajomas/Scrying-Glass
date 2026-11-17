"""Compact JSON preflight and checked comparison for source intermediates.

Internal JSON-only data; finite numbers, string keys, no cyclic containers.
The isolated worker remains responsible for hard CPU/memory enforcement.
"""
import json

def measure_json(value, limit, check, fail):
    total = 0
    def add(amount):
        nonlocal total
        total += amount
        if total > limit:
            fail('intermediate_creature_bytes_limit')
    def string(text):
        add(2)
        for char in text:
            check()
            n = ord(char)
            if 0xD800 <= n <= 0xDFFF:
                fail('malformed_record')
            add(2 if char in '"\\\b\f\n\r\t' else 6 if n < 32 else
                1 if n < 128 else 2 if n < 2048 else 3 if n < 65536 else 4)
    def walk(item):
        check()
        if item is None:
            add(4)
        elif type(item) is bool:
            add(4 if item else 5)
        elif type(item) is str:
            string(item)
        elif type(item) in (int, float):
            try:
                encoded = json.dumps(item, allow_nan=False)
            except (ValueError, OverflowError):
                fail('malformed_record')
            add(len(encoded))
        elif type(item) in (list, dict):
            add(2)
            for index, key in enumerate(item):
                check()
                if index:
                    add(1)
                if type(item) is dict:
                    if type(key) is not str:
                        fail('malformed_record')
                    string(key)
                    add(1)
                    walk(item[key])
                else:
                    walk(key)
        else:
            fail('malformed_record')
    walk(value)
    return total

def json_equal(left, right, check, fail):
    """Pinned deepEquals for acyclic JSON; Object.is numbers, ordered arrays.

    Explicitly reject unsafe integers and hasOwnProperty-shadowing objects;
    these are not silently rounded or interpreted as normal JS objects.
    """
    import math
    pending = [(left, right)]
    while pending:
        check()
        a, b = pending.pop()
        ta, tb = type(a), type(b)
        if ta is bool or tb is bool:
            if ta is not bool or tb is not bool or a is not b:
                return False
        elif a is None or b is None:
            if a is not b:
                return False
        elif ta in (int, float) or tb in (int, float):
            if ta not in (int, float) or tb not in (int, float):
                return False
            for number in (a, b):
                if type(number) is int and abs(number) > 9007199254740991:
                    fail('unsupported_comparison_number')
                if not math.isfinite(number):
                    fail('malformed_record')
            if a != b or (a == 0 and math.copysign(1, a) != math.copysign(1, b)):
                return False
        elif ta is str or tb is str:
            if ta is not str or tb is not str or a != b:
                return False
        elif ta is list and tb is list:
            if len(a) != len(b):
                return False
            for x, y in zip(a, b):
                check()
                pending.append((x, y))
        elif ta is dict and tb is dict:
            if 'hasOwnProperty' in a or 'hasOwnProperty' in b:
                fail('unsupported_comparison_key')
            if len(a) != len(b):
                return False
            for key, value in a.items():
                check()
                if key not in b:
                    return False
                pending.append((value, b[key]))
        elif ta in (list, dict) or tb in (list, dict):
            return False
        else:
            fail('malformed_record')
    return True
