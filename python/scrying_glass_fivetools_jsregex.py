"""Deliberate port of the JavaScript RegExp subset used by 5e.tools copy data.

The pinned runtime builds ``new RegExp(source, flags)`` from source data. This
module parses that source itself and emits an equivalent Python pattern for a
bounded subset; everything else fails with ``unsupported_regex`` or
``malformed_regex`` instead of being approximated:

- non-unicode (no ``u``/``v``/``y``/``d`` flags) JavaScript semantics: ``.``,
  ``^``/``$`` (with ``m``/``s``), ``\\b``/``\\B``/``\\d``/``\\w``/``\\s`` keep their
  ASCII/ECMAScript meaning, case-insensitive matching only for ASCII letters;
- no backreferences, lookarounds, legacy octal or control escapes;
- no quantified group containing another unbounded quantifier (catastrophic
  backtracking shape), counted repeats at most 1000, pattern at most 4096 chars;
- subjects containing non-BMP characters are refused when the pattern could
  split a surrogate pair (JS works on UTF-16 code units, Python on code points).

Python's ``re`` has no timeout; the isolated worker's deadline/CPU limits remain
the hard bound. Callers pass ``fail(code)``, which must raise.
"""
import re

from .scrying_glass_fivetools_jsvalues import JS_SPACE

WORD = 'A-Za-z0-9_'
LINE_TERMINATORS = '\n\r  '
MAX_PATTERN = 4096
MAX_REPEAT = 1000
_FLAGS = frozenset('gims')


def _ranges_class(ranges, negated=False):
    parts = []
    for lo, hi in sorted(ranges):
        parts.append(f'\\U{lo:08x}' if lo == hi else f'\\U{lo:08x}-\\U{hi:08x}')
    if not parts:
        return '[\\s\\S]' if negated else '(?!)'
    return '[' + ('^' if negated else '') + ''.join(parts) + ']'


def _chars(text):
    return [(ord(c), ord(c)) for c in text]


SPACE_RANGES = _chars(JS_SPACE)
DIGIT_RANGES = [(48, 57)]
WORD_RANGES = [(48, 57), (65, 90), (95, 95), (97, 122)]


def _complement(ranges):
    out, start = [], 0
    for lo, hi in sorted(ranges):
        if lo > start:
            out.append((start, lo - 1))
        start = max(start, hi + 1)
    if start <= 0x10FFFF:
        out.append((start, 0x10FFFF))
    return out


class _Node:
    __slots__ = ('text', 'min', 'wide', 'unbounded', 'groups')

    def __init__(self, text, minimum, *, wide=False, unbounded=False, groups=()):
        self.text, self.min, self.wide, self.unbounded, self.groups = text, minimum, wide, unbounded, tuple(groups)


class JsRegex:
    """One compiled RegExp object. ``last_index`` follows RegExp.prototype.test."""

    def __init__(self, source, flags, fail):
        self.fail = fail
        if type(source) is not str or (flags is not None and type(flags) is not str):
            fail('malformed_regex')
        flags = flags or ''
        if len(set(flags)) != len(flags) or set(flags) - set('dgimsuvy'):
            fail('malformed_regex')
        if set(flags) - _FLAGS:
            fail('unsupported_regex')
        if len(source) > MAX_PATTERN or any(ord(c) > 0xFFFF or 0xD800 <= ord(c) <= 0xDFFF for c in source):
            fail('unsupported_regex')
        self.flags, self.global_ = flags, 'g' in flags
        self._ignore, self._multi, self._dotall = 'i' in flags, 'm' in flags, 's' in flags
        self._src, self._pos, self._groups, self._names = source, 0, 0, {}
        self._reset_groups = set()
        node = self._disjunction(0)
        if self._pos != len(source):
            fail('malformed_regex')
        self.wide, self.can_be_empty = node.wide, node.min == 0
        self.group_count = self._groups
        try:
            self._re = re.compile(node.text)
        except (re.error, RecursionError, OverflowError):
            fail('unsupported_regex')
        self.last_index = 0

    # -- parser -------------------------------------------------------------
    def _peek(self, n=0):
        i = self._pos + n
        return self._src[i] if i < len(self._src) else None

    def _disjunction(self, depth):
        if depth > 32:
            self.fail('unsupported_regex')
        alternatives = [self._alternative(depth)]
        while self._peek() == '|':
            self._pos += 1
            alternatives.append(self._alternative(depth))
        if len(alternatives) == 1:
            return alternatives[0]
        return _Node('(?:' + '|'.join(a.text for a in alternatives) + ')',
                     min(a.min for a in alternatives),
                     wide=any(a.wide for a in alternatives),
                     unbounded=any(a.unbounded for a in alternatives),
                     groups=[g for a in alternatives for g in a.groups])

    def _alternative(self, depth):
        terms = []
        while self._peek() not in (None, '|', ')'):
            terms.append(self._term(depth))
        return _Node(''.join(t.text for t in terms), sum(t.min for t in terms),
                     wide=any(t.wide for t in terms), unbounded=any(t.unbounded for t in terms),
                     groups=[g for t in terms for g in t.groups])

    def _term(self, depth):
        c = self._peek()
        if c == '^':
            self._pos += 1
            return self._assertion('(?:\\A|(?<=[' + LINE_TERMINATORS + ']))' if self._multi else '\\A')
        if c == '$':
            self._pos += 1
            return self._assertion('(?:\\Z|(?=[' + LINE_TERMINATORS + ']))' if self._multi else '\\Z')
        if c == '\\' and self._peek(1) in ('b', 'B'):
            kind = self._peek(1)
            self._pos += 2
            w = '[' + WORD + ']'
            if kind == 'b':
                return self._assertion(f'(?:(?<={w})(?!{w})|(?<!{w})(?={w}))')
            return self._assertion(f'(?:(?<={w})(?={w})|(?<!{w})(?!{w}))')
        atom = self._atom(depth)
        return self._quantifier(atom)

    def _assertion(self, text):
        if self._peek() in ('*', '+', '?') or (self._peek() == '{' and self._braced(peek_only=True)):
            self.fail('malformed_regex')
        return _Node(text, 0)

    def _braced(self, peek_only=False):
        m = re.match(r'\{([0-9]+)(,([0-9]*))?\}', self._src[self._pos:])
        if not m:
            return None
        if not peek_only:
            self._pos += m.end()
        low = int(m.group(1))
        high = low if m.group(2) is None else (None if m.group(3) == '' else int(m.group(3)))
        return low, high

    def _quantifier(self, atom):
        c = self._peek()
        if c in ('*', '+', '?'):
            self._pos += 1
            low, high = {'*': (0, None), '+': (1, None), '?': (0, 1)}[c]
        elif c == '{' and self._braced(peek_only=True):
            low, high = self._braced()
            if high is not None and high < low:
                self.fail('malformed_regex')
        else:
            return atom
        if low > MAX_REPEAT or (high is not None and high > MAX_REPEAT):
            self.fail('unsupported_regex')
        lazy = self._peek() == '?'
        if lazy:
            self._pos += 1
        repeats = high is None or high > 1
        if repeats and atom.unbounded:
            self.fail('unsupported_regex')
        if repeats:
            self._reset_groups.update(atom.groups)
        text = '{' + str(low) + ',' + ('' if high is None else str(high)) + '}'
        return _Node('(?:' + atom.text + ')' + text + ('?' if lazy else ''),
                     atom.min * low, wide=atom.wide,
                     unbounded=atom.unbounded or high is None or high > 1, groups=atom.groups)

    def _literal(self, char):
        code = ord(char)
        if self._ignore and char.isalpha():
            if not char.isascii():
                self.fail('unsupported_regex')
            return _ranges_class([(ord(char.lower()),) * 2, (ord(char.upper()),) * 2])
        return _ranges_class([(code, code)])

    def _atom(self, depth):
        c = self._peek()
        if c is None or c in '*+?)':
            self.fail('malformed_regex')
        if c == '{':
            if self._braced(peek_only=True):
                self.fail('malformed_regex')
            self._pos += 1
            return _Node(self._literal('{'), 1)
        if c == '.':
            self._pos += 1
            ranges = [(0, 0x10FFFF)] if self._dotall else _complement(_chars(LINE_TERMINATORS))
            return _Node(_ranges_class(ranges), 1, wide=True)
        if c == '[':
            return self._class()
        if c == '(':
            return self._group(depth)
        if c == '\\':
            ranges, wide = self._escape(in_class=False)
            return _Node(_ranges_class(ranges), 1, wide=wide)
        self._pos += 1
        return _Node(self._literal(c), 1)

    def _group(self, depth):
        self._pos += 1
        name = None
        if self._peek() == '?':
            if self._peek(1) == ':':
                self._pos += 2
                inner = self._disjunction(depth + 1)
                if self._peek() != ')':
                    self.fail('malformed_regex')
                self._pos += 1
                return _Node('(?:' + inner.text + ')', inner.min, wide=inner.wide,
                             unbounded=inner.unbounded, groups=inner.groups)
            if self._peek(1) == '<' and self._peek(2) not in ('=', '!'):
                m = re.match(r'\?<([A-Za-z_][A-Za-z0-9_]*)>', self._src[self._pos:])
                if not m or m.group(1) in self._names:
                    self.fail('malformed_regex' if not m or m.group(1) in self._names else 'unsupported_regex')
                name = m.group(1)
                self._pos += m.end()
            else:
                self.fail('unsupported_regex')
        self._groups += 1
        index = self._groups
        if name:
            self._names[name] = index
        inner = self._disjunction(depth + 1)
        if self._peek() != ')':
            self.fail('malformed_regex')
        self._pos += 1
        prefix = f'(?P<{name}>' if name else '('
        return _Node(prefix + inner.text + ')', inner.min, wide=inner.wide,
                     unbounded=inner.unbounded, groups=(index,) + inner.groups)

    def _escape(self, in_class):
        self._pos += 1
        c = self._peek()
        if c is None:
            self.fail('malformed_regex')
        self._pos += 1
        if c in 'dDwWsS':
            base = {'d': DIGIT_RANGES, 'w': WORD_RANGES, 's': SPACE_RANGES}[c.lower()]
            return (base if c.islower() else _complement(base)), c.isupper()
        simple = {'t': '\t', 'n': '\n', 'r': '\r', 'f': '\f', 'v': '\v'}
        if c in simple:
            return _chars(simple[c]), False
        if in_class and c == 'b':
            return [(8, 8)], False
        if c == '0':
            if self._peek() is not None and self._peek().isdigit():
                self.fail('unsupported_regex')
            return [(0, 0)], False
        if c.isdigit() or c in 'ckpPq' or (c == '-' and not in_class):
            self.fail('unsupported_regex')
        if c in 'xu':
            width = 2 if c == 'x' else 4
            digits = self._src[self._pos:self._pos + width]
            if len(digits) == width and all(d in '0123456789abcdefABCDEF' for d in digits):
                self._pos += width
                code = int(digits, 16)
                if 0xD800 <= code <= 0xDFFF:
                    self.fail('unsupported_regex')
                char = chr(code)
            else:
                char = c  # Annex B identity escape
        else:
            char = c
        if self._ignore and char.isalpha():
            if not char.isascii():
                self.fail('unsupported_regex')
            return [(ord(char.lower()),) * 2, (ord(char.upper()),) * 2], False
        return [(ord(char), ord(char))], False

    def _class_atom(self):
        if self._peek() == '\\':
            return self._escape(in_class=True)
        c = self._peek()
        self._pos += 1
        return [(ord(c), ord(c))], False

    def _class(self):
        self._pos += 1
        negated = self._peek() == '^'
        if negated:
            self._pos += 1
        ranges, wide = [], negated
        while True:
            c = self._peek()
            if c is None:
                self.fail('malformed_regex')
            if c == ']':
                self._pos += 1
                break
            first, first_wide = self._class_atom()
            wide = wide or first_wide
            if self._peek() == '-' and self._peek(1) not in (None, ']'):
                self._pos += 1
                second, second_wide = self._class_atom()
                if len(first) != 1 or len(second) != 1 or first_wide or second_wide or first[0][0] != first[0][1] or second[0][0] != second[0][1]:
                    self.fail('unsupported_regex')
                lo, hi = first[0][0], second[0][0]
                if lo > hi:
                    self.fail('malformed_regex')
                ranges.append((lo, hi))
                if self._ignore:
                    for code in range(lo, hi + 1):
                        ch = chr(code)
                        if ch.isalpha():
                            if not ch.isascii():
                                self.fail('unsupported_regex')
                            ranges.append((ord(ch.swapcase()),) * 2)
            else:
                ranges.extend(first)
        if self._ignore:
            for lo, hi in list(ranges):
                if lo == hi and chr(lo).isalpha():
                    if not chr(lo).isascii():
                        self.fail('unsupported_regex')
                    ranges.append((ord(chr(lo).swapcase()),) * 2)
        if any(hi > 0xFFFF for lo, hi in ranges):
            wide = True
        return _Node(_ranges_class(ranges, negated), 1, wide=wide)

    # -- matching -----------------------------------------------------------
    def _subject(self, text):
        if type(text) is not str:
            self.fail('unsupported_regex_subject')
        if any(ord(c) > 0xFFFF for c in text) and (self.wide or self.can_be_empty):
            self.fail('unsupported_regex_subject')
        return text

    def search(self, text, pos=0):
        return self._re.search(self._subject(text), pos)

    def test(self, text):
        """RegExp.prototype.test, including global lastIndex state."""
        text = self._subject(text)
        start = self.last_index if self.global_ else 0
        if start > len(text):
            self.last_index = 0
            return False
        match = self._re.search(text, start)
        if self.global_:
            self.last_index = match.end() if match else 0
        return match is not None

    def exec_groups(self, text):
        match = self.search(text)
        if match is None:
            return None
        for group in range(1, self.group_count + 1):
            if group in self._reset_groups:
                self.fail('unsupported_regex')
        return [match.group(0)] + [match.group(i) for i in range(1, self.group_count + 1)]

    def _substitution(self, template, match, text):
        out, i, n = [], 0, len(template)
        m = self.group_count
        while i < n:
            c = template[i]
            if c != '$' or i + 1 >= n:
                out.append(c)
                i += 1
                continue
            nxt = template[i + 1]
            if nxt == '$':
                out.append('$'); i += 2
            elif nxt == '&':
                out.append(match.group(0)); i += 2
            elif nxt == '`':
                out.append(text[:match.start()]); i += 2
            elif nxt == "'":
                out.append(text[match.end():]); i += 2
            elif nxt.isdigit() and nxt.isascii():
                two = template[i + 1:i + 3]
                if len(two) == 2 and two.isdigit() and two.isascii() and 1 <= int(two) <= m:
                    index, i = int(two), i + 3
                elif 1 <= int(nxt) <= m:
                    index, i = int(nxt), i + 2
                else:
                    out.append('$' + nxt); i += 2
                    continue
                if index in self._reset_groups:
                    self.fail('unsupported_regex')
                out.append(match.group(index) or '')
            elif nxt == '<':
                close = template.find('>', i + 2)
                if not self._names or close < 0:
                    out.append('$<'); i += 2
                    continue
                name = template[i + 2:close]
                index = self._names.get(name)
                if index in self._reset_groups:
                    self.fail('unsupported_regex')
                out.append((match.group(index) or '') if index else '')
                i = close + 1
            else:
                out.append('$'); i += 1
        return ''.join(out)

    def replace(self, text, replacement, *, budget, check):
        """String.prototype.replace(regexp, replacement) with a UTF-8 byte budget."""
        text = self._subject(text)
        if type(replacement) is not str:
            self.fail('malformed_modification_payload')
        pieces, size, last, pos = [], 0, 0, 0
        def add(piece):
            nonlocal size
            size += len(piece.encode('utf-8', 'surrogatepass'))
            if size > budget:
                self.fail('intermediate_creature_bytes_limit')
            pieces.append(piece)
        while pos <= len(text):
            check()
            match = self._re.search(text, pos)
            if match is None:
                break
            add(text[last:match.start()])
            add(self._substitution(replacement, match, text))
            last = match.end()
            pos = match.end() + (1 if match.end() == match.start() else 0)
            if not self.global_:
                break
        add(text[last:])
        return ''.join(pieces)
