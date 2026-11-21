"""5e.tools inline tag parsing for statblock normalization (022.04e).

Ported from the pinned runtime's ``Renderer.tag`` table, ``Renderer.splitByTags``,
``Renderer.splitTagByPipe`` and ``Renderer.stripTags`` (5etools-src 32ef600,
js/render.js). Text is converted to a small inline structure; nothing is
rendered as HTML and no imported markup survives. Entity tags whose kind is a
supported reference become reference items; every other tag keeps the
display text the runtime would strip it to.
"""
import re
from urllib.parse import urlsplit

from .scrying_glass_fivetools_general_modes import split_by_tags

ABILITY_NAMES = {'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution',
                 'int': 'Intelligence', 'wis': 'Wisdom', 'cha': 'Charisma'}
STYLE_TAGS = frozenset('b bold i italic s strike s2 strikeDouble u underline u2 underlineDouble sup sub kbd code style font comic comicH1 comicH2 comicH3 comicH4 comicNote note tip'.split())
FIRST_PART_TAGS = frozenset('5etools 5etoolsImg 5etoolsAudio adventure book filter footnote link loader color highlight help'.split())
# tag -> (display part index, default source) for entity tags (_TagPipedDisplayText*).
ENTITY_TAGS = {
    'action': (2, 'PHB'), 'background': (2, 'PHB'), 'backgroundFluff': (2, 'PHB'), 'boon': (2, 'MTF'),
    'charoption': (2, 'MOT'), 'class': (2, 'PHB'), 'classFluff': (2, 'PHB'), 'condition': (2, 'PHB'),
    'creature': (2, 'MM'), 'creatureFluff': (2, 'MM'), 'cult': (2, 'MTF'), 'deck': (2, 'DMG'),
    'disease': (2, 'DMG'), 'facility': (2, 'XDMG'), 'feat': (2, 'PHB'), 'hazard': (2, 'DMG'),
    'item': (2, 'DMG'), 'itemFluff': (2, 'DMG'), 'itemProperty': (2, 'PHB'), 'itemMastery': (2, 'XPHB'),
    'language': (2, 'PHB'), 'legroup': (2, 'MM'), 'object': (2, 'DMG'), 'optfeature': (2, 'PHB'),
    'psionic': (2, 'UATheMysticClass'), 'race': (2, 'PHB'), 'raceFluff': (2, 'PHB'), 'recipe': (2, 'HF'),
    'recipeFluff': (2, 'HF'), 'crochet': (2, 'CaBoMP'), 'crochetFluff': (2, 'CaBoMP'), 'reward': (2, 'DMG'),
    'vehicle': (2, 'GoS'), 'vehupgrade': (2, 'GoS'), 'sense': (2, 'PHB'), 'skill': (2, 'PHB'),
    'spell': (2, 'PHB'), 'spellFluff': (2, 'PHB'), 'status': (2, 'PHB'), 'table': (2, 'DMG'),
    'trap': (2, 'DMG'), 'variantrule': (2, 'DMG'), 'cite': (2, 'PHB'), 'card': (3, 'DMG'),
    'deity': (3, 'PHB'), 'subclass': (4, 'PHB'), 'subclassFluff': (4, 'PHB'), 'classFeature': (5, 'PHB'),
    'subclassFeature': (7, 'PHB'),
}
# Tags collected as saved supporting definitions -> dataset kind.
REFERENCE_KINDS = {'spell': 'spell', 'condition': 'condition', 'disease': 'disease', 'status': 'status',
                   'item': 'item', 'skill': 'skill', 'sense': 'sense', 'action': 'action',
                   'variantrule': 'variantrule', 'creature': 'monster', 'legroup': 'legendaryGroup'}
EMPHASIS_TAGS = frozenset('i italic note atk atkr h m hom actSave actSaveSuccess actSaveFail actSaveFailBy actSaveSuccessOrFail actTrigger actResponse'.split())
STRONG_TAGS = frozenset(('b', 'bold'))
VARIABLE_TEXT = {'name': '(name)', 'short_name': '(short name)', 'title_short_name': '(short title name)',
                 'damage_avg': '(damage average)', 'size_mult': '(size multiplier)'}
_VARIABLE = re.compile(r'<\$([^$]+)\$>')


def split_by_pipe(text):
    """Renderer.splitTagByPipe: split on '|' outside nested tags, keep '\\|'."""
    out, current, depth = [], '', 0
    for index, char in enumerate(text):
        previous = text[index - 1] if index else None
        following = text[index + 1] if index + 1 < len(text) else None
        if char == '{':
            if following == '@':
                depth += 1
            current += '{'
        elif char == '}':
            if depth:
                depth -= 1
            current += '}'
        elif char == '|' and previous != '\\':
            if depth:
                current += '|'
            else:
                out.append(current)
                current = ''
        else:
            current += char
    if current:
        out.append(current)
    return out


def _human_variables(text):
    def replace(match):
        mode, _, detail = match.group(1).partition('__')
        detail = detail.split('__')[0]
        if mode in VARIABLE_TEXT:
            return VARIABLE_TEXT[mode]
        if mode in ('dc', 'spell_dc', 'to_hit', 'damage_mod') and detail in ABILITY_NAMES:
            label = {'dc': 'DC', 'spell_dc': 'spellcasting DC', 'to_hit': 'to-hit', 'damage_mod': 'damage modifier'}[mode]
            return f'({detail.upper()} {label})'
        return match.group(0)
    return _VARIABLE.sub(replace, text)


def _number_text(text):
    try:
        number = float(text.strip())
    except ValueError:
        return None
    if number != number or abs(number) == float('inf'):
        return None
    value = int(number) if number.is_integer() else number
    return ('+' if number >= 0 else '') + str(value)


def _attack(text, roll):
    groups = [list(g.strip()) for g in text.lower().split(',') if g.strip()]
    if len(groups) > 1:
        seen = set(groups[-1])
        for i in range(len(groups) - 2, -1, -1):
            kept = []
            for letter in groups[i]:
                if letter not in seen:
                    kept.append(letter)
                seen.add(letter)
            groups[i] = kept
    def render(tags):
        kind = 'Melee ' if 'm' in tags else 'Ranged ' if 'r' in tags else 'Magical ' if 'g' in tags else 'Area ' if 'a' in tags else ''
        method = 'Weapon ' if 'w' in tags else 'Spell ' if 's' in tags else 'Power ' if 'p' in tags else ''
        return kind + method
    return ' or '.join(render(g) for g in groups) + 'Attack' + (' Roll' if roll else '') + ':'


def stripped_tag(tag, text):
    """Display text of one tag (without nested-tag stripping); None if unknown."""
    text = _human_variables(text)
    parts = split_by_pipe(text)
    first = parts[0] if parts else ''
    if tag in STYLE_TAGS or tag in FIRST_PART_TAGS:
        return first
    if tag in ENTITY_TAGS:
        index = ENTITY_TAGS[tag][0]
        return parts[index] if len(parts) > index else first
    if tag in ('damage', 'dice', 'autodice'):
        return parts[1] if len(parts) > 1 and parts[1] else first.replace(';', '/')
    if tag in ('d20', 'hit', 'initiative'):
        return parts[1] if len(parts) > 1 and parts[1] else (_number_text(first) or first)
    if tag == 'recharge':
        try:
            number = float(first or 6)
        except ValueError:
            return '(Recharge ?)'
        value = int(number) if number.is_integer() else number
        return f'(Recharge {value}{chr(0x2013) + "6" if number < 6 else ""})'
    if tag == 'chance':
        return parts[1] if len(parts) > 1 and parts[1] else f'{first} percent'
    if tag == 'ability':
        if len(parts) > 1 and parts[1]:
            return parts[1]
        words = [w for w in first.lower().split(' ') if w.strip()]
        try:
            score = int(float(words[1])) if len(words) > 1 else 0
        except ValueError:
            score = 0
        modifier = (score - 10) // 2
        return f'{score} ({"+" if modifier >= 0 else ""}{modifier})'
    if tag in ('savingThrow', 'skillCheck'):
        return parts[1] if len(parts) > 1 and parts[1] else first
    if tag in ('scaledice', 'scaledamage'):
        return parts[4] if len(parts) > 4 and parts[4] else (parts[2] if len(parts) > 2 else '')
    fixed = {'actSaveSuccess': 'Success:', 'actSaveSuccessOrFail': 'Failure or Success:', 'actTrigger': 'Trigger:',
             'h': 'Hit: ', 'm': 'Miss: ', 'hom': 'Hit or Miss: '}
    if tag in fixed:
        return fixed[tag]
    if tag == 'actSave':
        return f'{ABILITY_NAMES.get(text.strip(), text)} Saving Throw:'
    if tag == 'actSaveFail':
        return f'{_ordinal(first)} Failure:' if first else 'Failure:'
    if tag == 'actSaveFailBy':
        return f'Failure by {first} or More:'
    if tag == 'actResponse':
        return 'Response' + ('—' if 'd' in text else ':')
    if tag == 'atk':
        return _attack(text, False)
    if tag == 'atkr':
        return _attack(text, True)
    if tag == 'hitYourSpellAttack':
        return first or 'your spell attack modifier'
    if tag == 'dcYourSpellSave':
        return first or 'your spell save DC'
    if tag == 'dc':
        return 'DC ' + (parts[1] if len(parts) > 1 and parts[1] else first)
    if tag == 'coinflip':
        return first or 'flip a coin'
    if tag == 'unit':
        try:
            amount = float(first)
        except ValueError:
            return parts[1] if len(parts) > 1 else ''
        single = parts[1] if len(parts) > 1 else ''
        return single if amount <= 1 else (parts[2] if len(parts) > 2 and parts[2] else single + 's')
    if tag == 'quickref':
        return parts[4] if len(parts) > 4 and parts[4] else first
    if tag == 'area':
        flags = parts[2] if len(parts) > 2 else ''
        return first if 'x' in flags else f'{"A" if "u" in flags else "a"}rea {first}'
    if tag == 'homebrew':
        new, old = first, parts[1] if len(parts) > 1 else ''
        if new and old:
            return f'{new} [this is a homebrew addition, replacing the following: "{old}"]'
        return f'{new} [this is a homebrew addition]' if new else f'[the following text has been removed due to homebrew: {old}]'
    return None


def _ordinal(text):
    words = {'1': 'First', '2': 'Second', '3': 'Third', '4': 'Fourth', '5': 'Fifth'}
    return words.get(text.strip(), text)


def strip_tags(text):
    """Renderer.stripTags: recursively replace every tag with its display text."""
    if not text:
        return text
    out = []
    for part in split_by_tags(text):
        if not part.startswith('{@'):
            out.append(part)
            continue
        tag, _, body = part[2:-1].partition(' ')
        stripped = stripped_tag(tag, body)
        out.append(strip_tags(stripped if stripped is not None else body))
    return ''.join(out)


def safe_https(url):
    if type(url) is not str or len(url) > 2048:
        return None
    try:
        parts = urlsplit(url)
        if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password:
            return None
        if any(c.isspace() or ord(c) < 32 for c in url) or '\\' in url or parts.port == 0:
            return None
    except ValueError:
        return None
    return url


def reference_identity(tag, body):
    """(kind, name, source) for a collected reference tag, else None."""
    if tag not in REFERENCE_KINDS:
        return None
    parts = split_by_pipe(_human_variables(body))
    name = parts[0].strip() if parts else ''
    if not name:
        return None
    source = parts[1].strip() if len(parts) > 1 and parts[1].strip() else ENTITY_TAGS[tag][1]
    return REFERENCE_KINDS[tag], name, source


def parse_inline(text, depth=0):
    """Return inline items: ('text', s), ('strong'|'emphasis', items),
    ('link', url, items) or ('ref', kind, name, source, label)."""
    if depth > 8:
        return [('text', strip_tags(text))]
    items = []
    for part in split_by_tags(text):
        if not part.startswith('{@'):
            items.append(('text', part))
            continue
        tag, _, body = part[2:-1].partition(' ')
        identity = reference_identity(tag, body)
        stripped = stripped_tag(tag, body)
        label = strip_tags(stripped if stripped is not None else body)
        if identity:
            items.append(('ref',) + identity + (label,))
        elif tag == 'link':
            parts = split_by_pipe(body)
            url = safe_https(parts[1].strip()) if len(parts) > 1 else None
            inner = parse_inline(parts[0] if parts else '', depth + 1)
            items.append(('link', url, inner) if url else ('group', inner))
        elif tag in STRONG_TAGS:
            items.append(('strong', parse_inline(stripped or '', depth + 1)))
        elif tag in EMPHASIS_TAGS:
            items.append(('emphasis', parse_inline(stripped or '', depth + 1)))
        elif stripped is None:
            items.append(('unknown', tag, label))
        else:
            items.append(('group', parse_inline(stripped, depth + 1)))
    return items


def collect_references(value, found, check):
    """Add (kind, name, source) of every reference tag in all string values."""
    stack = [value]
    while stack:
        check()
        item = stack.pop()
        if type(item) is str:
            if '{@' in item:
                _collect_text(item, found, 0)
        elif type(item) is list:
            stack.extend(reversed(item))
        elif type(item) is dict:
            stack.extend(reversed(list(item.values())))


def _collect_text(text, found, depth):
    if depth > 8:
        return
    for part in split_by_tags(text):
        if not part.startswith('{@'):
            continue
        tag, _, body = part[2:-1].partition(' ')
        identity = reference_identity(tag, body)
        if identity and identity not in found:
            found[identity] = None
        if '{@' in body:
            _collect_text(body, found, depth + 1)
