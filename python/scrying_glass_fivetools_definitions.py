"""Supporting definition facts for 5e.tools references (022.04e).

Spells, conditions/diseases/statuses, items, skills, senses, actions, variant
rules and legendary groups become definition-owned facts plus entry nodes.
Formatting follows the pinned runtime's Parser helpers in plain text; shapes
it does not recognize are kept as readable text with a warning.
"""
from .scrying_glass_fivetools_tags import strip_tags
from .scrying_glass_fivetools_nodes import spell_level

SCHOOLS = {'A': 'Abjuration', 'C': 'Conjuration', 'D': 'Divination', 'E': 'Enchantment', 'V': 'Evocation',
           'I': 'Illusion', 'N': 'Necromancy', 'T': 'Transmutation', 'P': 'Psionic'}
UNITS = {'action': 'action', 'bonus': 'bonus action', 'reaction': 'reaction', 'minute': 'minute',
         'hour': 'hour', 'round': 'round', 'day': 'day', 'week': 'week', 'year': 'year', 'turn': 'turn'}
RARITY_NONE = frozenset(('none', 'unknown', 'unknown (magic)', None))
# Entry properties shown for each definition kind, in order.
ENTRY_KEYS = {
    'spell': (('entries', None), ('entriesHigherLevel', None)),
    'condition': (('entries', None),), 'disease': (('entries', None),), 'status': (('entries', None),),
    'item': (('entries', None), ('additionalEntries', None)),
    'skill': (('entries', None),), 'sense': (('entries', None),), 'action': (('entries', None),),
    'variantrule': (('entries', None),),
    'legendaryGroup': (('lairActions', 'Lair Actions'), ('regionalEffects', 'Regional Effects'),
                       ('mythicEncounter', 'Mythic Encounter')),
}


def _plural(number, word):
    return f"{number} {word}{'' if number == 1 else 's'}"


def spell_level_school(spell):
    level, school = spell.get('level'), SCHOOLS.get(spell.get('school'), str(spell.get('school') or ''))
    if type(level) is not int:
        return school
    if level == 0:
        return f'{school} Cantrip'
    text = f'Level {level} {school}'
    if spell.get('meta', {}).get('ritual') if type(spell.get('meta')) is dict else False:
        text += ' (Ritual)'
    return text


def casting_time(spell):
    out = []
    for time in spell.get('time') or []:
        if type(time) is not dict:
            continue
        unit = UNITS.get(time.get('unit'), str(time.get('unit', '')))
        number = time.get('number', 1)
        text = f'{number} {unit}' if unit in ('action', 'bonus action', 'reaction') and number == 1 else _plural(number, unit)
        if type(time.get('condition')) is str:
            text += ', ' + strip_tags(time['condition'])
        if type(time.get('note')) is str:
            text += f" ({strip_tags(time['note'])})"
        out.append(text)
    return ' or '.join(out)


def _distance(distance):
    if type(distance) is not dict:
        return ''
    kind, amount = distance.get('type'), distance.get('amount')
    if kind in ('self', 'touch', 'sight', 'unlimited'):
        return {'self': 'Self', 'touch': 'Touch', 'sight': 'Sight', 'unlimited': 'Unlimited'}[kind]
    if kind == 'feet':
        return _plural(amount, 'foot').replace('foots', 'feet')
    if kind == 'miles':
        return _plural(amount, 'mile')
    return f'{amount} {kind}' if amount is not None else str(kind or '')


def spell_range(spell):
    value = spell.get('range')
    if type(value) is not dict:
        return ''
    kind = value.get('type')
    if kind == 'special':
        return 'Special'
    if kind == 'point':
        return _distance(value.get('distance'))
    if kind in ('radius', 'sphere', 'cone', 'line', 'cube', 'hemisphere', 'cylinder', 'emanation'):
        distance = value.get('distance') or {}
        size = f"{distance.get('amount')}-{'foot' if distance.get('type') == 'feet' else distance.get('type', '')}"
        return f'Self ({size} {kind})'
    return str(kind or '')


def components(spell):
    value = spell.get('components')
    if type(value) is not dict:
        return ''
    out = [letter.upper() for letter in ('v', 's') if value.get(letter)]
    material = value.get('m')
    if material:
        text = material.get('text') if type(material) is dict else material
        out.append(f'M ({strip_tags(text)})' if type(text) is str else 'M')
    if value.get('r'):
        out.append('R')
    return ', '.join(out)


def duration(spell):
    out = []
    for item in spell.get('duration') or []:
        if type(item) is not dict:
            continue
        kind = item.get('type')
        if kind == 'instant':
            out.append('Instantaneous')
        elif kind == 'timed':
            value = item.get('duration') or {}
            amount, unit = value.get('amount', 1), value.get('type', '')
            text = ('Up to ' if value.get('upTo') else '') + _plural(amount, unit)
            out.append(f'Concentration, up to {_plural(amount, unit)}' if item.get('concentration') else text)
        elif kind == 'permanent':
            ends = item.get('ends') or []
            words = {'dispel': 'dispelled', 'trigger': 'triggered', 'discharge': 'discharged'}
            out.append('Until ' + ' or '.join(words.get(e, str(e)) for e in ends) if ends else 'Permanent')
        elif kind == 'special':
            out.append('Special')
        else:
            out.append(str(kind or ''))
    return ' or '.join(out)


def item_line(item):
    parts = []
    rarity = item.get('rarity')
    if type(rarity) is str and rarity not in RARITY_NONE:
        parts.append(rarity)
    attune = item.get('reqAttune')
    if attune is True:
        parts.append('(requires attunement)')
    elif type(attune) is str:
        parts.append(f'(requires attunement {strip_tags(attune)})')
    return ' '.join(parts)


def item_value(value):
    if type(value) not in (int, float) or type(value) is bool:
        return ''
    if value >= 100 and value % 100 == 0:
        return f'{value // 100:,} gp'
    if value >= 10 and value % 10 == 0:
        return f'{value // 10:,} sp'
    return f'{value:,} cp'


def definition_facts(kind, record):
    """Ordered (key, label, text) tuples for a definition record."""
    out = []
    def add(key, label, text):
        if text:
            out.append((key, label, text))
    if kind == 'spell':
        add('level_school', 'Level and School', spell_level_school(record))
        add('casting_time', 'Casting Time', casting_time(record))
        add('range', 'Range', spell_range(record))
        add('components', 'Components', components(record))
        add('duration', 'Duration', duration(record))
    elif kind == 'item':
        add('rarity', 'Rarity', item_line(record))
        add('value', 'Value', item_value(record.get('value')))
        weight = record.get('weight')
        if type(weight) in (int, float) and type(weight) is not bool:
            add('weight', 'Weight', f'{weight} lb.')
        if record.get('dmg1'):
            add('damage', 'Damage', f"{record['dmg1']}{' ' + str(record.get('dmgType', '')) if record.get('dmgType') else ''}" +
                (f" (versatile {record['dmg2']})" if record.get('dmg2') else ''))
        if type(record.get('ac')) is int:
            add('armor_class', 'Armor Class', str(record['ac']))
        if type(record.get('range')) is str:
            add('range', 'Range', record['range'])
        properties = record.get('property')
        if type(properties) is list:
            add('properties', 'Properties', ', '.join(strip_tags(p.split('|')[0]) if type(p) is str else strip_tags(str(p.get('uid', ''))).split('|')[0] for p in properties if type(p) in (str, dict)))
    elif kind == 'skill':
        add('ability', 'Ability', str(record.get('ability') or '').upper())
    elif kind == 'action':
        add('time', 'Time', casting_time(record))
    elif kind == 'variantrule':
        add('rule_type', 'Rule Type', {'C': 'Core', 'O': 'Optional', 'V': 'Variant', 'VO': 'Variant Optional', 'VV': 'Variant Variant', 'U': 'Unknown'}.get(record.get('ruleType'), ''))
    return [(key, label, strip_tags(text)) for key, label, text in out]
