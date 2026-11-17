"""Monster facts and sections for version-one statblocks (022.04e).

Formats a resolved 5e.tools creature after the pinned runtime's statblock
order (Renderer.monster / Parser in 5etools-src 32ef600): header facts in
plain text, then Traits, Actions, Bonus Actions, Reactions, Legendary Actions,
Mythic Actions and Variants as section nodes. For the selected creature the
six Scrying Glass fields (name, species, AC, current/max HP and initiative
bonus) are never emitted as facts. Related creatures keep their own values.
Unrecognized meaningful properties are shown generically with a warning.
"""
from functools import cmp_to_key

from .scrying_glass_fivetools_tags import strip_tags
from .scrying_glass_fivetools_nodes import spellcasting_entries

SIZES = {'F': 'Fine', 'D': 'Diminutive', 'T': 'Tiny', 'S': 'Small', 'M': 'Medium', 'L': 'Large',
         'H': 'Huge', 'G': 'Gargantuan', 'C': 'Colossal', 'V': 'Varies'}
SIZE_ORDER = ('T', 'S', 'M', 'L', 'H', 'G', 'V')
ALIGNMENT = {'L': 'lawful', 'N': 'neutral', 'NX': 'neutral (law/chaos axis)', 'NY': 'neutral (good/evil axis)',
             'C': 'chaotic', 'G': 'good', 'E': 'evil', 'U': 'unaligned', 'A': 'any alignment'}
ABILITIES = (('str', 'Strength'), ('dex', 'Dexterity'), ('con', 'Constitution'),
             ('int', 'Intelligence'), ('wis', 'Wisdom'), ('cha', 'Charisma'))
SPEED_MODES = ('walk', 'burrow', 'climb', 'fly', 'swim')
TRAIT_ORDER = ('temporary statblock', 'special equipment', 'shapechanger')
SECTIONS = (('trait', 'Traits', None), ('action', 'Actions', 'actionHeader'), ('bonus', 'Bonus Actions', 'bonusHeader'),
            ('reaction', 'Reactions', 'reactionHeader'), ('legendary', 'Legendary Actions', 'legendaryHeader'),
            ('mythic', 'Mythic Actions', 'mythicHeader'))
SG_OWNED = frozenset(('name', 'ac', 'hp', 'initiative'))
HANDLED = frozenset(('size', 'sizeNote', 'type', 'typeNote', 'alignment', 'alignmentPrefix', 'level', 'speed',
                     'str', 'dex', 'con', 'int', 'wis', 'cha', 'save', 'skill', 'tool', 'gear', 'vulnerable',
                     'resist', 'immune', 'conditionImmune', 'senses', 'passive', 'languages', 'cr', 'pbNote',
                     'legendaryActions', 'legendaryActionsLair', 'environment', 'treasure', 'alias',
                     'trait', 'action', 'bonus', 'reaction', 'legendary', 'mythic', 'variant', 'spellcasting',
                     'actionHeader', 'bonusHeader', 'reactionHeader', 'legendaryHeader', 'mythicHeader',
                     'actionNote', 'reactionNote', 'legendaryGroup', 'shortName', 'isNamedCreature',
                     'summonedBySpell', 'summonedBySpellLevel', 'summonedByClass', 'group', 'footer'))
METADATA = frozenset(('source', 'page', 'otherSources', 'referenceSources', 'additionalSources', 'reprintedAs',
                      'isReprinted', 'srd', 'srd52', 'basicRules', 'basicRules2024', 'hasToken', 'hasFluff',
                      'hasFluffImages', 'tokenCredit', 'tokenCustom', 'tokenUrl', 'tokenHref', 'foundryTokenScale',
                      'altArt', 'soundClip', '_isCopy', '_copy_templates', '_versions', 'traitTags', 'senseTags',
                      'actionTags', 'languageTags', 'damageTags', 'damageTagsLegendary', 'damageTagsSpell',
                      'miscTags', 'conditionInflict', 'conditionInflictLegendary', 'conditionInflictSpell',
                      'spellcastingTags', 'savingThrowForced', 'savingThrowForcedLegendary',
                      'savingThrowForcedSpell', 'attachedItems', 'dragonCastingColor', 'dragonAge', 'familiar',
                      'isNpc', 'hasSpellcasting', 'legacy'))


def join_conjunct(values, joiner=', ', last=' or '):
    values = [v for v in values if v]
    if len(values) <= 1:
        return ''.join(values)
    if len(values) == 2:
        return last.join(values)
    return joiner.join(values[:-1]) + joiner.strip() + last + values[-1]


def title_words(text):
    from .scrying_glass_fivetools_substitutions import title_case
    return title_case(text)


def bonus(value):
    if type(value) in (int, float) and type(value) is not bool:
        return f"{'+' if value >= 0 else ''}{value}"
    return strip_tags(str(value))


def ability_mod(score):
    return (score - 10) // 2 if type(score) is int else None


def size_text(size):
    values = [size] if type(size) is str else size if type(size) is list else []
    ordered = sorted((v for v in values if type(v) is str), key=lambda v: SIZE_ORDER.index(v) if v in SIZE_ORDER else -1)
    return join_conjunct([SIZES.get(v, v) for v in ordered])


def type_text(value):
    if value is None:
        return ''
    if type(value) is str:
        return title_words(value)
    if type(value) is not dict:
        return strip_tags(str(value))
    inner = value.get('type')
    types = inner.get('choose') if type(inner) is dict else [inner]
    types = [t for t in (types or []) if type(t) is str]
    if value.get('swarmSize'):
        text = f"swarm of {SIZES.get(value['swarmSize'], value['swarmSize'])} {join_conjunct([title_words(t + 's') for t in types])}"
    else:
        text = join_conjunct([title_words(t) for t in types])
    tags = []
    for tag in value.get('tags') or []:
        if type(tag) is str:
            tags.append(title_words(tag))
        elif type(tag) is dict and type(tag.get('tag')) is str:
            tags.append(title_words(f"{tag['prefix']} {tag['tag']}" if tag.get('prefix') else tag['tag']))
    if tags:
        text += f" ({', '.join(tags)})"
    if type(value.get('note')) is str:
        text += ' ' + strip_tags(value['note'])
    return '' if value.get('typeHidden') else text


def alignment_text(values):
    if not values:
        return ''
    if type(values) is not list:
        values = [values]
    if any(type(v) is not str for v in values):
        parts = []
        for item in values:
            if type(item) is dict and (item.get('special') is not None or item.get('chance') is not None or item.get('note') is not None):
                if item.get('special') is not None:
                    parts.append(strip_tags(str(item['special'])))
                    continue
                text = alignment_text(item.get('alignment'))
                if item.get('chance'):
                    text += f" ({item['chance']}%)"
                if item.get('note'):
                    text += f" ({strip_tags(str(item['note']))})"
                parts.append(text)
            elif type(item) is dict and item.get('alignment') is not None:
                parts.append(alignment_text(item['alignment']))
            elif type(item) is str:
                parts.append(ALIGNMENT.get(item.upper(), item))
        return ' or '.join(parts)
    found = set(values)
    if len(values) == 1:
        return ALIGNMENT.get(values[0].upper(), values[0])
    if len(values) == 2:
        return ' '.join(ALIGNMENT.get(v.upper(), v) for v in values)
    if len(values) == 3 and {'NX', 'NY', 'N'} <= found:
        return 'any neutral alignment'
    if len(values) == 5:
        for letter, text in (('G', 'non-good'), ('E', 'non-evil'), ('L', 'non-lawful'), ('C', 'non-chaotic')):
            if letter not in found:
                return f'any {text} alignment'
    if len(values) == 4:
        for missing, text in ((('L', 'NX'), 'chaotic'), (('G', 'NY'), 'evil'), (('C', 'NX'), 'lawful'), (('E', 'NY'), 'good')):
            if not found & set(missing):
                return f'any {text} alignment'
    return ', '.join(ALIGNMENT.get(v.upper(), v) for v in values)


def type_line(mon):
    ptype = ' '.join(x for x in (type_text(mon.get('type')), strip_tags(mon['typeNote']) if type(mon.get('typeNote')) is str else '') if x)
    align = ''
    if mon.get('alignment'):
        prefix = strip_tags(mon['alignmentPrefix']) if type(mon.get('alignmentPrefix')) is str else ''
        align = prefix + title_words(alignment_text(mon['alignment']))
    level = f"{mon['level']}{'th' if 10 <= mon['level'] % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(mon['level'] % 10, 'th')}-level" if type(mon.get('level')) is int else ''
    tail = ('; ' if ',' in ptype else ', ').join(x for x in (ptype, align) if x)
    note = strip_tags(mon['sizeNote']) if type(mon.get('sizeNote')) is str else ''
    return ' '.join(x for x in (level, size_text(mon.get('size')), note, tail) if x)


def speed_text(mon):
    speed = mon.get('speed')
    if speed is None:
        return ''
    if type(speed) is not dict:
        return f'{speed} ft.' if speed != 'Varies' else 'Varies'
    hidden = speed.get('hidden') or []
    out = []
    def add(mode, value):
        if value is True:
            number, unit = ('equal to your walking speed' if mode != 'walk' else 0), ''
        else:
            number, unit = (value.get('number') if type(value) is dict else value), ' ft.'
        condition = f" {strip_tags(value['condition'])}" if type(value) is dict and type(value.get('condition')) is str else ''
        out.append(f"{'' if mode == 'walk' else mode.title() + ' '}{number}{unit}{condition}")
    for mode in SPEED_MODES:
        if mode in hidden:
            continue
        if speed.get(mode) or mode == 'walk':
            add(mode, speed.get(mode) or 0)
        for alternate in (speed.get('alternate') or {}).get(mode) or []:
            add(mode, alternate)
    joiner = ', '
    choose = speed.get('choose')
    if type(choose) is dict and 'choose' not in hidden:
        joiner = '; '
        names = join_conjunct([m.title() for m in sorted(choose.get('from') or [])])
        out.append(f"{names} {choose.get('amount')} ft.{' ' + strip_tags(choose['note']) if type(choose.get('note')) is str else ''}")
    return joiner.join(out) + (f" {strip_tags(speed['note'])}" if type(speed.get('note')) is str else '')


def _imm_simple(value):
    return type(value) is str or (type(value) is dict and 'special' in value)


def imm_res_text(values, mode='damage'):
    if not values:
        return ''
    if type(values) is not list:
        values = [values]
    parts = []
    for index, value in enumerate(values):
        simple = _imm_simple(value)
        if simple:
            text = strip_tags(str(value['special'] if type(value) is dict else value))
        elif type(value) is dict:
            stack = []
            if type(value.get('preNote')) is str:
                stack.append(strip_tags(value['preNote']))
            inner = next((value[k] for k in ('vulnerable', 'resist', 'immune', 'conditionImmune') if type(value.get(k)) is list), None)
            if inner is not None:
                stack.append(imm_res_text(inner, mode))
            if type(value.get('note')) is str:
                stack.append(strip_tags(value['note']))
            text = ' '.join(stack)
        else:
            text = strip_tags(str(value))
        if index == len(values) - 1:
            parts.append(text)
            continue
        next_simple = _imm_simple(values[index + 1])
        if not simple or not next_simple:
            parts.append(text + '; ')
        elif index != len(values) - 2 or len(values) < 2:
            parts.append(text + ', ')
        elif len(values) == 2:
            parts.append(text + ' and ')
        else:
            parts.append(text + ', and ')
    return ''.join(parts)


def cr_text(mon):
    from .scrying_glass_fivetools_jsvalues import XP_CHART, cr_to_pb
    cr = mon.get('cr')
    if cr is None:
        return ''
    value = cr.get('cr') if type(cr) is dict else cr
    if type(value) is not str:
        return strip_tags(str(value))
    xp = cr.get('xp') if type(cr) is dict and cr.get('xp') else XP_CHART.get(value)
    details = []
    if xp is not None:
        lair = cr.get('xpLair') if type(cr) is dict else None
        details.append(f'XP {xp:,}' + (f', or {lair:,} in lair' if type(lair) is int else ''))
    try:
        pb = cr_to_pb(cr, lambda code: (_ for _ in ()).throw(ValueError(code)))
    except ValueError:
        pb = None
    if type(mon.get('pbNote')) is str:
        details.append('PB ' + strip_tags(mon['pbNote']))
    elif pb is not None:
        details.append(f'PB +{pb}')
    text = value + (f" ({'; '.join(details)})" if details else '')
    if type(cr) is dict:
        for key, label in (('lair', 'when encountered in lair'), ('coven', 'when part of a coven')):
            if type(cr.get(key)) is str:
                text += f' or {cr[key]} {label}'
    return text


def _trait_cmp(a, b):
    sa, sb = a.get('sort') if type(a) is dict else None, b.get('sort') if type(b) is dict else None
    if sa is not None and sb is not None:
        return (sa > sb) - (sa < sb)
    if sa is not None:
        return -1
    if sb is not None:
        return 1
    na, nb = (x.get('name') if type(x) is dict else None for x in (a, b))
    if not na and not nb:
        return 0
    ca, cb = (strip_tags(n).lower().strip() if type(n) is str else '' for n in (na, nb))
    oa, ob = (type(n) is str and n.endswith(' Only)') for n in (na, nb))
    if oa != ob:
        return 1 if oa else -1
    ia = TRAIT_ORDER.index(ca) if ca in TRAIT_ORDER else -1
    ib = TRAIT_ORDER.index(cb) if cb in TRAIT_ORDER else -1
    if ia >= 0 and ib >= 0:
        return ia - ib
    if ia >= 0 or ib >= 0:
        return -1 if ia >= 0 else 1
    return (ca > cb) - (ca < cb)


def _spell_display(mon, prop):
    out = []
    for entry in mon.get('spellcasting') or []:
        if type(entry) is not dict or (entry.get('displayAs') or 'trait') != prop:
            continue
        if prop in ('legendary', 'mythic') and entry.get('headerEntries') and prop in (entry.get('hidden') or []):
            out.append({'type': 'item', 'name': entry.get('name'), 'entries': entry['headerEntries']})
        else:
            out.append({'type': 'entries', 'name': entry.get('name'), 'entries': spellcasting_entries(entry)[0]['entries'],
                        '_footer': spellcasting_entries(entry)[1:]})
    return out


def ordered(mon, prop):
    items = [x for x in (mon.get(prop) or []) if x is not None] if type(mon.get(prop)) is list else []
    spells = _spell_display(mon, prop)
    if prop == 'trait':
        combined = items + spells
        return sorted(combined, key=cmp_to_key(_trait_cmp)) if combined else []
    if not spells or not items:
        return items or spells
    last = -1
    for index, action in enumerate(items):
        entries = action.get('entries') if type(action) is dict else None
        if entries and type(entries[0]) is str and ('{@atk ' in entries[0] or '{@atkr ' in entries[0]):
            last = index
    attacks, other = (items[:last], items[last:]) if last >= 0 else ([], list(items))
    for spell in spells:
        if not spell.get('name'):
            other.append(spell)
            continue
        position = next((i for i, a in enumerate(other) if type(a) is dict and type(a.get('name')) is str
                         and a['name'].lower() >= str(spell['name']).lower()), -1)
        other.insert(position, spell) if position >= 0 else other.append(spell)
    return attacks + other


def monster_facts(mon, *, selected):
    """Ordered (key, label, display_text, integer_value) tuples."""
    facts = []
    def add(key, label, text, number=None):
        if text:
            facts.append((key, label, text, number))
    if not selected:
        ac = mon.get('ac')
        if ac is not None:
            add('armor_class', 'Armor Class', ', '.join(strip_tags(str(a.get('ac', '')) + (f" ({', '.join(strip_tags(f) for f in a.get('from') or [])})" if type(a) is dict and a.get('from') else '')) if type(a) is dict else strip_tags(str(a)) for a in (ac if type(ac) is list else [ac])))
        hp = mon.get('hp')
        if type(hp) is dict:
            add('hit_points', 'Hit Points', strip_tags(str(hp['special'])) if 'special' in hp else f"{hp.get('average', '')} ({hp.get('formula', '')})".strip())
    add('speed', 'Speed', speed_text(mon))
    for key, label in ABILITIES:
        score = mon.get(key)
        if type(score) is int:
            add(key, label, f'{score} ({bonus(ability_mod(score))})', score)
        elif type(score) is dict and 'special' in score:
            add(key, label, strip_tags(str(score['special'])))
    save = mon.get('save')
    if type(save) is dict:
        order = [k for k, _ in ABILITIES]
        keys = sorted(save, key=lambda k: order.index(k) if k in order else 99)
        add('saving_throws', 'Saving Throws', ', '.join(f'{k.title() if k in order else strip_tags(k)} {bonus(save[k])}' if k != 'special' else strip_tags(str(save[k])) for k in keys))
    skill = mon.get('skill')
    if type(skill) is dict:
        parts = [f'{title_words(k)} {bonus(v)}' for k, v in sorted(((k, v) for k, v in skill.items() if k not in ('other', 'special')), key=lambda kv: kv[0].lower())]
        for other in skill.get('other') or []:
            if type(other) is dict and type(other.get('oneOf')) is dict:
                parts.append('plus one of the following: ' + join_conjunct([f'{title_words(k)} {bonus(v)}' for k, v in other['oneOf'].items()]))
        if type(skill.get('special')) is str:
            parts.append(strip_tags(skill['special']))
        add('skills', 'Skills', ', '.join(parts))
    tool = mon.get('tool')
    if type(tool) is dict:
        add('tools', 'Tools', ', '.join(f'{title_words(k)} {bonus(v)}' for k, v in tool.items()))
    gear = mon.get('gear')
    if type(gear) is list:
        add('gear', 'Gear', ', '.join(strip_tags(g if type(g) is str else f"{g.get('item', '')}" + (f" ({g['quantity']})" if g.get('quantity') else '')) for g in gear if type(g) in (str, dict)))
    for key, label in (('vulnerable', 'Damage Vulnerabilities'), ('resist', 'Damage Resistances'),
                       ('immune', 'Damage Immunities'), ('conditionImmune', 'Condition Immunities')):
        add(key, label, imm_res_text(mon.get(key), 'condition' if key == 'conditionImmune' else 'damage'))
    senses = mon.get('senses')
    senses = [senses] if type(senses) is str else senses if type(senses) is list else []
    passive = mon.get('passive')
    if passive is None and type(mon.get('wis')) is int:
        passive = 10 + ability_mod(mon['wis'])
    sense_parts = [strip_tags(s) for s in senses if type(s) is str]
    if passive is not None:
        sense_parts.append(f'passive Perception {strip_tags(str(passive))}')
    add('senses', 'Senses', ', '.join(sense_parts))
    languages = mon.get('languages')
    languages = [languages] if type(languages) is str else languages if type(languages) is list else None
    if languages is not None:
        text = ', '.join(strip_tags(l) for l in languages if type(l) is str)
        add('languages', 'Languages', (text[:1].upper() + text[1:]) if text else '—')
    add('challenge', 'Challenge', cr_text(mon))
    if mon.get('legendaryActions') or mon.get('legendaryActionsLair'):
        count, lair = mon.get('legendaryActions'), mon.get('legendaryActionsLair')
        text = f'{count}' if count is not None else ''
        if lair:
            text = f'{text} ({lair} in lair)' if text else f'{lair} in lair'
        add('legendary_action_uses', 'Legendary Action Uses', text.strip())
    for key, label in (('environment', 'Environment'), ('treasure', 'Treasure'), ('alias', 'Also Known As')):
        value = mon.get(key)
        if type(value) is list:
            add(key, label, ', '.join(strip_tags(str(v)) for v in value if type(v) in (str, int)))
    for key, label in (('summonedBySpell', 'Summoned by Spell'), ('summonedByClass', 'Summoned by Class')):
        if type(mon.get(key)) is str:
            add(key, label, strip_tags(mon[key].split('|')[0]) + (f" (level {mon['summonedBySpellLevel']})" if key == 'summonedBySpell' and mon.get('summonedBySpellLevel') else ''))
    return facts
