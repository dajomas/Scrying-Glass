"""Restricted replacement for the runtime's ``eval(getCleanMathExpression(x))``.

The pinned runtime strips every character except ``-+/*0-9.,`` and evaluates
the rest as JavaScript. This module never executes code: it tokenizes that
alphabet (plus the spaces the runtime inserts itself) and evaluates only number
literals, unary +/-, ``**``, ``*``, ``/``, binary +/- and the comma operator
with IEEE-754 double semantics. Constructs JavaScript would treat as regex
literals, comments, legacy octal literals or update operators fail explicitly.
"""
import math
import re

from .scrying_glass_fivetools_jsvalues import number_result

MAX_EXPRESSION = 1024
_CLEAN = re.compile(r'[^-+/*0-9.,]+')
_NUMBER = re.compile(r'(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)')


def clean_math_expression(text):
    return _CLEAN.sub('', text)


def _tokens(text, fail):
    if len(text) > MAX_EXPRESSION:
        fail('unsupported_expression')
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c == ' ':
            i += 1
            continue
        if text.startswith('//', i) or text.startswith('/*', i):
            fail('unsupported_expression')
        for op in ('**', '++', '--'):
            if text.startswith(op, i):
                if op != '**':
                    fail('malformed_expression')
                out.append(op)
                i += 2
                break
        else:
            if c in '+-*/,':
                out.append(c)
                i += 1
                continue
            match = _NUMBER.match(text, i)
            if not match:
                fail('malformed_expression')
            literal = match.group(0)
            whole = literal.split('.')[0]
            if len(whole) > 1 and whole.startswith('0'):
                fail('unsupported_expression')
            out.append(float(literal))
            i = match.end()
    return out


def js_pow(base, exponent):
    """Number::exponentiate for doubles."""
    if math.isnan(exponent):
        return math.nan
    if exponent == 0:
        return 1.0
    if math.isnan(base):
        return math.nan
    if abs(base) == 1 and math.isinf(exponent):
        return math.nan
    odd = exponent.is_integer() and not math.isinf(exponent) and int(exponent) % 2 == 1
    if base == 0:
        negative = math.copysign(1, base) < 0 and odd
        if exponent > 0:
            return -0.0 if negative else 0.0
        return -math.inf if negative else math.inf
    if base < 0 and not exponent.is_integer() and not math.isinf(exponent):
        return math.nan
    try:
        return math.pow(base, exponent)
    except OverflowError:
        return -math.inf if base < 0 and odd else math.inf


def js_div(left, right):
    if right == 0:
        if left == 0 or math.isnan(left):
            return math.nan
        sign = math.copysign(1, left) * math.copysign(1, right)
        return math.inf if sign > 0 else -math.inf
    return left / right


def evaluate_clean_expression(text, fail):
    """Evaluate a cleaned expression; returns a finite JSON number."""
    tokens = _tokens(text, fail)
    pos = 0

    def peek():
        return tokens[pos] if pos < len(tokens) else None

    def take():
        nonlocal pos
        pos += 1
        return tokens[pos - 1]

    def unary_only(depth):
        if depth > 256:
            fail('unsupported_expression')
        token = peek()
        if token in ('+', '-'):
            take()
            value = unary_only(depth + 1)
            return -value if token == '-' else value
        if type(token) is float:
            take()
            return token
        fail('malformed_expression')

    def exponent(depth):
        if depth > 256:
            fail('unsupported_expression')
        token = peek()
        if token in ('+', '-'):
            value = unary_only(depth + 1)
            if peek() == '**':
                fail('malformed_expression')
            return value
        if type(token) is float:
            take()
            if peek() == '**':
                take()
                return js_pow(token, exponent(depth + 1))
            return token
        fail('malformed_expression')

    def multiplicative():
        value = exponent(0)
        while peek() in ('*', '/'):
            op = take()
            right = exponent(0)
            value = value * right if op == '*' else js_div(value, right)
        return value

    def additive():
        value = multiplicative()
        while peek() in ('+', '-'):
            op = take()
            right = multiplicative()
            value = value + right if op == '+' else value - right
        return value

    if not tokens:
        fail('malformed_expression')
    value = additive()
    while peek() == ',':
        take()
        value = additive()
    if pos != len(tokens):
        fail('malformed_expression')
    if math.isnan(value) or math.isinf(value):
        fail('nonfinite_numeric_result')
    return number_result(value, fail)
