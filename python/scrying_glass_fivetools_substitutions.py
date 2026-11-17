"""Dynamic ``<$mode__detail$>`` copy text (022.04d), pinned to 5etools-src 32ef600.

Mirrors ``DataUtil.generic.variableResolver.resolve``: before any _mod runs,
every string in the copy's modification payloads is resolved against the copy
record as it stands after base merge and template ``_root`` application.
Unknown modes stay verbatim, as upstream leaves them. Arithmetic uses the
restricted evaluator, never ``eval``; NaN/undefined values that upstream would
print as text fail explicitly.
"""
import math
import re

from .scrying_glass_fivetools_expressions import clean_math_expression, evaluate_clean_expression
from .scrying_glass_fivetools_jsvalues import (
    ABIL_ABVS, JS_SPACE, ability_mod_of, cr_to_pb, number_to_string, to_display_string, truthy,
)

VARIABLE = re.compile(r'<\$(?P<variable>[^$]+)\$>')
_W = '[A-Za-z0-9_]'
_B = f'(?:(?<={_W})(?!{_W})|(?<!{_W})(?={_W}))'
_S = '[' + JS_SPACE + ']'
ABILITY_WORD = re.compile(_B + '(?P<abil>[sS][tT][rR]|[dD][eE][xX]|[cC][oO][nN]|[iI][nN][tT]|[wW][iI][sS]|[cC][hH][aA])' + _B)
SIZE_MULT_WORD = re.compile(_B + 'size_mult' + _B)
DRAGON_AGE = re.compile('(?:[aA][dD][uU][lL][tT]|[aA][nN][cC][iI][eE][nN][tT]|[yY][oO][uU][nN][gG]) ' + _W +
                        '+ ([dD][rR][aA][gG][oO][nN]|[dD][rR][aA][cC][oO][lL][iI][cC][hH])')
SIZE_MULT = {'L': 2, 'H': 3, 'G': 4}

TITLE_LOWER = ('a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'as', 'at', 'by', 'for', 'from', 'in',
               'into', 'near', 'of', 'on', 'onto', 'to', 'with', 'over', 'von', 'between', 'per', 'beyond', 'among')
TITLE_UPPER = ('Id', 'Tv', 'Dm', 'Ok', 'Npc', 'Pc', 'Tpk', 'Wip', 'Dc', 'D&d', 'Ac', 'Hp')
TITLE_UPPER_PLURAL = ('Ids', 'Tvs', 'Dms', 'Oks', 'Npcs', 'Pcs', 'Tpks', 'Wips', 'Dcs')
_TITLE_INITIAL = re.compile(r'(?<!\{[@=])(' + _B + _W + r'+[^-—' + JS_SPACE + '/|]*) *')
_TITLE_LOWER = re.compile(_S + '(' + '|'.join(TITLE_LOWER) + ')(?=' + _S + ')', re.IGNORECASE | re.ASCII)
_TITLE_UPPER = re.compile(_B + '(' + '|'.join(re.escape(w) for w in TITLE_UPPER) + ')' + _B)
_TITLE_UPPER_PLURAL = re.compile(_B + '(' + '|'.join(TITLE_UPPER_PLURAL) + ')' + _B)
_TITLE_COMPOUND = re.compile('([a-z]-(?:Like|Kreen|Toa))')
_TITLE_POST_PUNCT = re.compile('([;:?!.])(' + _S + '*)([^' + JS_SPACE + '])')


def title_case(text):
    """StrUtil.toTitleCase (ASCII word semantics of the pinned runtime)."""
    text = _TITLE_INITIAL.sub(lambda m: m.group(0)[:1].upper() + m.group(0)[1:].lower(), text)
    text = _TITLE_LOWER.sub(lambda m: m.group(0).lower(), text)
    text = _TITLE_UPPER.sub(lambda m: m.group(0).upper(), text)
    text = _TITLE_UPPER_PLURAL.sub(lambda m: m.group(0)[:-1].upper() + m.group(0)[-1:].lower(), text)
    text = _TITLE_COMPOUND.sub(lambda m: m.group(0).lower(), text)
    return _TITLE_POST_PUNCT.sub(lambda m: m.group(1) + m.group(2) + m.group(3).upper(), text)


def short_name(mon, fail, *, title=False):
    """Renderer.monster.getShortName without display-name options."""
    name, short = mon.get('name'), mon.get('shortName')
    if type(name) is not str:
        fail('unsupported_substitution_value')
    named = truthy(mon.get('isNamedCreature'))
    prefix = '' if named else ('The ' if title else 'the ')
    if short is True:
        return prefix + name
    if truthy(short):
        if type(short) is not str:
            fail('unsupported_substitution_value')
        return prefix + (title_case(short) if not prefix and title else short.lower())
    base = DRAGON_AGE.sub(lambda m: m.group(1), name.split(',')[0])
    return prefix + (base.split(' ')[0] if named else base.lower())


def _ability(ent, detail, fail):
    if detail not in ABIL_ABVS:
        fail('unknown_substitution_ability')
    return ability_mod_of(ent, detail, fail)


def _size_mult(ent):
    size = ent.get('size')
    first = size[0] if type(size) in (list, str) and size else None
    return SIZE_MULT.get(first if truthy(first) else 'M', 1)


def resolve_variable(mode, detail, ent, fail):
    """Return the replacement text, or None when the runtime leaves it verbatim."""
    if mode == 'name':
        return to_display_string(ent.get('name'), fail) if 'name' in ent else fail('unsupported_substitution_value')
    if mode in ('short_name', 'title_short_name'):
        return short_name(ent, fail, title=mode == 'title_short_name')
    if mode in ('dc', 'spell_dc'):
        pb = cr_to_pb(ent.get('cr'), fail)
        return number_to_string(8 + _ability(ent, detail, fail) + (pb or 0))
    if mode == 'to_hit':
        pb = cr_to_pb(ent.get('cr'), fail)
        total = (pb or 0) + _ability(ent, detail, fail)
        return ('+' if total >= 0 else '') + number_to_string(total)
    if mode == 'damage_mod':
        total = _ability(ent, detail, fail)
        return '' if total == 0 else f' + {total}' if total > 0 else f' - {abs(total)}'
    if mode == 'damage_avg':
        if type(detail) is not str:
            fail('malformed_substitution')
        text = ABILITY_WORD.sub(lambda m: number_to_string(ability_mod_of(ent, m.group('abil'), fail)), detail)
        text = SIZE_MULT_WORD.sub(lambda m: str(_size_mult(ent)), text)
        return number_to_string(math.floor(evaluate_clean_expression(clean_math_expression(text), fail)))
    if mode == 'size_mult':
        mult = _size_mult(ent)
        if not detail:
            return str(mult)
        value = evaluate_clean_expression(f'{mult} * {clean_math_expression(detail)}', fail)
        return number_to_string(math.floor(value))
    return None


def resolve_text(text, ent, fail, check):
    def replace(match):
        check()
        parts = match.group('variable').split('__')
        detail = parts[1] if len(parts) > 1 else None
        value = resolve_variable(parts[0], detail, ent, fail)
        return match.group(0) if value is None else value
    return VARIABLE.sub(replace, text)


def resolve_payload(value, ent, fail, check):
    """Walk every string value (not keys) of a decoded _mod payload."""
    check()
    if type(value) is str:
        return resolve_text(value, ent, fail, check) if '<$' in value else value
    if type(value) is list:
        return [resolve_payload(item, ent, fail, check) for item in value]
    if type(value) is dict:
        return {key: resolve_payload(item, ent, fail, check) for key, item in value.items()}
    return value
