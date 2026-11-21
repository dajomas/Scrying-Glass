"""022.04c regex/number/expression ports: pinned JavaScript semantics, explicit refusals."""
import math
import unittest

from python.scrying_glass_fivetools_jsregex import JsRegex
from python.scrying_glass_fivetools_jsvalues import (
    cr_to_pb, cr_to_xp_number, number_to_string, object_keys, sort_lower, strict_equal, to_number,
)
from python.scrying_glass_fivetools_expressions import clean_math_expression, evaluate_clean_expression


class Failed(Exception):
    pass


def fail(code):
    raise Failed(code)


def rx(pattern, flags=''):
    return JsRegex(pattern, flags, fail)


def replace(pattern, flags, text, replacement):
    return rx(pattern, flags).replace(text, replacement, budget=10**6, check=lambda: None)


class RegexTests(unittest.TestCase):
    def refused(self, code, pattern, flags=''):
        with self.assertRaises(Failed) as caught:
            rx(pattern, flags)
        self.assertEqual(str(caught.exception), code)

    def test_word_boundaries_and_classes_use_ascii_javascript_meaning(self):
        self.assertEqual(replace(r'\bwolf\b', 'gi', 'wolf Wolf wolfy éwolf', 'X'), 'X X wolfy éX')
        self.assertEqual(replace(r'\w+', 'g', 'añb', '-'), '-ñ-')
        self.assertEqual(replace(r'\d', 'g', '1٣2', '#'), '#٣#')
        self.assertEqual(replace(r'\s', 'g', 'a b c', '_'), 'a_b_c')

    def test_dot_anchors_and_flags(self):
        self.assertEqual(replace('.', 'g', 'a\nb', '-'), '-\n-')
        self.assertEqual(replace('.', 'gs', 'a\nb', '-'), '---')
        self.assertEqual(replace('b$', 'g', 'ab\n', '!'), 'ab\n')
        self.assertEqual(replace('^b', 'gm', 'a\nb\rb', '!'), 'a\n!\r!')
        self.assertEqual(replace('the kuo-toa', 'gi', 'The Kuo-toa', 'X'), 'X')

    def test_javascript_replacement_patterns(self):
        self.assertEqual(replace('(a)(b)?', 'g', 'ab a', '[$2$1$&$$]'), '[baab$] [aa$]')
        self.assertEqual(replace('b', '', 'abc', "$`|$'"), 'aa|cc')
        self.assertEqual(replace('(?<n>x)', 'g', 'x', '<$<n>>'), '<x>')
        self.assertEqual(replace('x', 'g', 'x', '$<n>$9$0'), '$<n>$9$0')
        self.assertEqual(replace('(a)', 'g', 'a', '$10'), 'a0')

    def test_empty_matches_and_braces_follow_javascript(self):
        self.assertEqual(replace('x*', 'g', 'abxd', '-'), '-a-b--d-')
        self.assertEqual(replace('a*?', 'g', 'aa', '-'), '-a-a-')
        self.assertEqual(replace('a{,2}', 'g', 'a{,2}', 'X'), 'X')
        self.assertEqual(replace('}', 'g', '{a}', ')'), '{a)')

    def test_global_test_keeps_last_index(self):
        regex = rx('^(Multiattack|Bite)$', 'g')
        self.assertTrue(regex.test('Multiattack'))
        self.assertFalse(regex.test('Bite'))
        self.assertTrue(regex.test('Bite'))

    def test_unsupported_and_malformed_patterns_are_refused(self):
        for pattern in (r'(a)\1', '(?=a)', '(?<!a)b', '(a+)+', '(?:a*b)*', 'a{1001}', r'\p{L}', 'x' * 4097, '😀'):
            with self.subTest(pattern=pattern):
                self.refused('unsupported_regex', pattern)
        self.refused('unsupported_regex', 'é', 'i')
        for flags in ('u', 'y', 'd'):
            self.refused('unsupported_regex', 'a', flags)
        for pattern, flags in (('(', ''), ('*a', ''), ('[b-a]', ''), ('a', 'gg'), ('a', 'z'), ('{2}', '')):
            with self.subTest(pattern=pattern, flags=flags):
                self.refused('malformed_regex', pattern, flags)

    def test_astral_subjects_and_growth_are_bounded(self):
        with self.assertRaises(Failed):
            rx('.', 'g').replace('a😀', '-', budget=100, check=lambda: None)
        self.assertEqual(rx('a', 'g').replace('a😀', 'b', budget=100, check=lambda: None), 'b😀')
        with self.assertRaises(Failed) as caught:
            rx('a', 'g').replace('aaaa', 'xxxxxxxx', budget=20, check=lambda: None)
        self.assertEqual(str(caught.exception), 'intermediate_creature_bytes_limit')


class ValueTests(unittest.TestCase):
    def test_number_conversion(self):
        cases = {' 5 ': 5, '+5': 5, '0x1F': 31, '1e3': 1000.0, '.5': 0.5, '': 0, None: 0, True: 1}
        for value, expected in cases.items():
            self.assertEqual(to_number(value, fail), expected)
        for value in ('abc', '1.2.3', '-0x5', '1_0'):
            self.assertTrue(math.isnan(to_number(value, fail)))
        with self.assertRaises(Failed):
            to_number([1], fail)

    def test_number_to_string_matches_ecmascript(self):
        for value, text in ((5.0, '5'), (2.5, '2.5'), (1e21, '1e+21'), (1e-7, '1e-7'), (0.000001, '0.000001'),
                            (-0.0, '0'), (0.1 + 0.2, '0.30000000000000004'), (123e-20, '1.23e-18'), (1e20, '100000000000000000000')):
            self.assertEqual(number_to_string(value), text)

    def test_equality_keys_sorting_and_challenge_rating(self):
        self.assertTrue(strict_equal(1, 1.0))
        self.assertFalse(strict_equal(True, 1))
        self.assertFalse(strict_equal({}, {}))
        self.assertEqual(object_keys({'b': 1, '10': 2, '2': 3, 'a': 4}), ['2', '10', 'b', 'a'])
        self.assertEqual(sort_lower(['b', 'A', 'a', 'C'], fail), ['A', 'a', 'b', 'C'])
        self.assertEqual([cr_to_pb(cr, fail) for cr in ('1/2', '4', '5', '13', '30', None, 'Unknown')], [2, 2, 3, 5, 9, 0, 0])
        self.assertIsNone(cr_to_pb('x/y/z', fail))
        self.assertEqual(cr_to_xp_number({'cr': '13', 'xp': 7}), 7)
        self.assertEqual(cr_to_xp_number('1/4'), 50)


class ExpressionTests(unittest.TestCase):
    def test_restricted_arithmetic(self):
        for text, expected in (('2.5+3', 5.5), ('2**3**2', 512), ('2**-2', 0.25), ('1,2', 2), ('10/4', 2.5),
                               ('+-+3', -3), ('1/2**2000', 0), ('2 * 1.5', 3)):
            self.assertEqual(evaluate_clean_expression(text, fail), expected)
        self.assertEqual(clean_math_expression('2 * <$x$> + abc'), '2*+')

    def test_refusals(self):
        for text, code in (('-2**2', 'malformed_expression'), ('2--3', 'malformed_expression'), ('', 'malformed_expression'),
                           ('01', 'unsupported_expression'), ('2//3', 'unsupported_expression'), ('1/0', 'nonfinite_numeric_result'),
                           ('2*/3/', 'malformed_expression'), ('1.2.3', 'malformed_expression')):
            with self.subTest(text=text):
                with self.assertRaises(Failed) as caught:
                    evaluate_clean_expression(text, fail)
                self.assertEqual(str(caught.exception), code)


if __name__ == '__main__':
    unittest.main()
