"""Compact JSON size preflight without serializing an expanded creature.

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
