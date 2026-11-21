"""Tetra-cube ``.monster`` statblock ingestion (SG-TODO-022.07).

Follows the inspected statblock-script.js (external_sourcefiles, blob
a8520dcbf739ffb4f24ec7a50607bce29886d950): ReplaceTags placeholders (except
its lossy '[2d6+3]' parse, which drops the +3; here the bonus is kept), the
'_' / '**' formatting toggles, property lines and section flags. Identity is
the SHA-256 of the original bytes; the filename is metadata only. A file
never supplies Scrying Glass's six fields (name, species, AC, HP, initiative):
hpText, armour and the Tetra-cube short/plural names are ignored, and
[MON]/[MONS] become species placeholders. Sections whose flag is off but that
still contain entries stay readable, labelled disabled. Generated Tetra-cube
boilerplate (legendary/lair/mythic/regional descriptions) is shown only when
the section is enabled, because only then does the file present it.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import time

from .scrying_glass_fivetools_jsvalues import XP_CHART, cr_to_pb
from .scrying_glass_statblock_sources import SourceError, assemble, credit, toggle_items
from .scrying_glass_statblock_model import ModelLimits

ADAPTER_VERSION = 'tetracube-07-1'
MAX_FILE_BYTES = 5 * 1024 * 1024
STATS = ('str', 'dex', 'con', 'int', 'wis', 'cha')
STAT_NAMES = {'str': 'Strength', 'dex': 'Dexterity', 'con': 'Constitution', 'int': 'Intelligence', 'wis': 'Wisdom', 'cha': 'Charisma'}
BRACKET = re.compile(r'\[(.*?)\]')
DAMAGE = re.compile(r'\d*d\d+')
BONUS = re.compile(r'^[+-] ?(\d+)$')
KNOWN = frozenset((
    'name', 'size', 'type', 'tag', 'alignment', 'hitDice', 'armorName', 'shieldBonus', 'natArmorBonus', 'otherArmorDesc',
    'speed', 'burrowSpeed', 'climbSpeed', 'flySpeed', 'hover', 'swimSpeed', 'customHP', 'customSpeed', 'hpText', 'speedDesc',
    'strPoints', 'dexPoints', 'conPoints', 'intPoints', 'wisPoints', 'chaPoints', 'blindsight', 'blind', 'darkvision',
    'tremorsense', 'truesight', 'telepathy', 'cr', 'customCr', 'customProf', 'isLegendary', 'legendariesDescription',
    'isLair', 'lairDescription', 'lairDescriptionEnd', 'isMythic', 'mythicDescription', 'isRegional', 'regionalDescription',
    'regionalDescriptionEnd', 'properties', 'abilities', 'actions', 'bonusActions', 'reactions', 'legendaries', 'mythics',
    'lairs', 'regionals', 'sthrows', 'skills', 'damagetypes', 'specialdamage', 'conditions', 'languages', 'understandsBut',
    'shortName', 'pluralName', 'doubleColumns', 'separationPoint', 'damage'))
LAYOUT = frozenset(('doubleColumns', 'separationPoint', 'damage', 'shortName', 'pluralName', 'hpText', 'customHP', 'hitDice',
                    'armorName', 'shieldBonus', 'natArmorBonus', 'otherArmorDesc', 'properties'))


def _int(value, default=0):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return int(number) if math.isfinite(number) else default


def cr_proficiency(cr):
    if cr not in XP_CHART:
        return None
    return cr_to_pb(cr, lambda code: (_ for _ in ()).throw(ValueError(code)))


def cr_xp(cr):
    return XP_CHART.get(cr)


def _bonus(value):
    return f"{'+' if value >= 0 else ''}{value}"


class Monster:
    def __init__(self, data, warn):
        self.data, self.warn = data, warn

    def mod(self, stat):
        return math.floor((_int(self.data.get(stat + 'Points'), 10) - 10) / 2)

    def prof(self):
        cr = self.data.get('cr')
        if cr == '*':
            return _int(self.data.get('customProf'), 2)
        value = cr_proficiency(str(cr))
        if value is None:
            self.warn('unknown_challenge_rating', f'Challenge rating {cr!r} is not in the Tetra-cube table.')
            return _int(self.data.get('customProf'), 2)
        return value

    def tag_atoms(self, text):
        """ReplaceTags as atoms; [MON]/[MONS] -> species placeholders."""
        atoms, last = [], 0
        for match in BRACKET.finditer(text):
            atoms.append(('text', text[last:match.start()]))
            last = match.end()
            read = re.sub(r' +', ' ', match.group(1).lower()).strip()
            if read in ('mon', 'mons'):
                atoms.append(('species', match.group(0)))
                continue
            value = self._replacement(read)
            if value is None:
                if read:
                    self.warn('unresolved_placeholder', f'Placeholder [{match.group(1)}] kept as written.')
                atoms.append(('text', match.group(0)))
            else:
                atoms.append(('text', value))
        atoms.append(('text', text[last:]))
        return [a for a in atoms if a[0] == 'species' or a[1]]

    def _replacement(self, read):
        if not read:
            return None
        position, kind, bonus, roll = 0, None, 0, None
        if read[:3] in STATS:
            bonus, position, kind = self.mod(read[:3]), 3, 'stat'
            if read[3:7] == ' atk':
                bonus, position, kind = bonus + self.prof(), 7, 'atk'
            elif read[3:8] == ' save':
                bonus, position, kind = bonus + self.prof() + 8, 8, 'save'
            if position < len(read):
                if read[position] == ' ':
                    position += 1
                else:
                    return None
        if kind in (None, 'stat') and position < len(read):
            space = read.find(' ', position)
            token = read[position:space] if space >= 0 else read[position:]
            if DAMAGE.search(token):
                roll, position, kind = token, position + len(token), 'dmg'
                if position < len(read):
                    if read[position] == ' ':
                        position += 1
                    else:
                        return None
        if position < len(read):
            match = BONUS.match(read[position:])
            if not match:
                return None
            bonus += -int(match.group(1)) if read[position] == '-' else int(match.group(1))
        if kind in ('stat', 'atk'):
            return _bonus(bonus)
        if kind == 'save':
            return str(bonus)
        if kind == 'dmg':
            dice = re.fullmatch(r'(\d*)d(\d+)([+-]\d+)?', roll)
            if not dice:
                return None
            count = int(dice.group(1)) if dice.group(1) else 1
            size = int(dice.group(2))
            bonus += int(dice.group(3)) if dice.group(3) else 0
            if count > 1000 or size > 1000:
                return None
            average = max(math.floor(count * ((size + 1) / 2) + bonus), 1)
            return f"{average} ({count}d{size}" + (f' + {bonus}' if bonus > 0 else f' - {-bonus}' if bonus < 0 else '') + ')'
        return None

    def entries(self, text):
        """FormatString: newlines split paragraphs; '_' and '**' toggles."""
        if type(text) is not str:
            return []
        out = []
        for line in re.split(r'(?:\r\n|\r|\n)+', text):
            if line.strip():
                line = line[1:] if line.startswith('>') else line
                out.append({'type': 'inlineItems', 'items': toggle_items(self.tag_atoms(line.strip()))})
        return out

    def trait_entries(self, items, *, plain=False):
        out = []
        for item in items or []:
            if type(item) is not dict:
                continue
            name, body = item.get('name') if type(item.get('name')) is str else '', self.entries(item.get('desc'))
            if plain and not name:
                out.extend(body)
            else:
                out.append({'type': 'entries', 'name': re.sub(r'[*_]', '', name) or None, 'entries': body})
        return out


def facts_and_sections(data, warn):
    mon = Monster(data, warn)
    facts = []
    def add(key, label, text, number=None):
        if text:
            facts.append((key, label, text, number))
    if data.get('customSpeed'):
        speed = data.get('speedDesc') if type(data.get('speedDesc')) is str else ''
    else:
        parts = [f"{_int(data.get('speed'))} ft."]
        for key, label in (('burrowSpeed', 'burrow'), ('climbSpeed', 'climb'), ('flySpeed', 'fly'), ('swimSpeed', 'swim')):
            if _int(data.get(key)) > 0:
                parts.append(f"{label} {_int(data.get(key))} ft." + (' (hover)' if key == 'flySpeed' and data.get('hover') else ''))
        speed = ', '.join(parts)
    add('speed', 'Speed', speed)
    for stat in STATS:
        points = _int(data.get(stat + 'Points'), 10)
        add(stat, STAT_NAMES[stat], f'{points} ({_bonus(mon.mod(stat))})', points)
    prof = mon.prof()
    saves = [s for s in data.get('sthrows') or [] if type(s) is dict and s.get('name') in STATS]
    add('saving_throws', 'Saving Throws', ', '.join(f"{s['name'].capitalize()} {_bonus(mon.mod(s['name']) + prof)}" for s in saves))
    skills = []
    for skill in data.get('skills') or []:
        if type(skill) is dict and type(skill.get('name')) is str and skill.get('stat') in STATS:
            skills.append(f"{skill['name'].capitalize()} {_bonus(mon.mod(skill['stat']) + prof * (2 if 'note' in skill else 1))}")
    add('skills', 'Skills', ', '.join(skills))
    for code, key, label in (('v', 'damage_vulnerabilities', 'Damage Vulnerabilities'), ('r', 'damage_resistances', 'Damage Resistances'),
                             ('i', 'damage_immunities', 'Damage Immunities')):
        plain = [d['name'] for d in data.get('damagetypes') or [] if type(d) is dict and type(d.get('name')) is str and
                 (d.get('type') == code or (code == 'r' and d.get('type') not in ('v', 'i')))]
        special = [d['name'] for d in data.get('specialdamage') or [] if type(d) is dict and type(d.get('name')) is str and
                   (d.get('type') == code or (code == 'r' and d.get('type') not in ('v', 'i')))]
        add(key, label, '; '.join(x for x in (', '.join(plain), '; '.join(special)) if x).lower())
    add('condition_immunities', 'Condition Immunities',
        ', '.join(c['name'].lower() for c in data.get('conditions') or [] if type(c) is dict and type(c.get('name')) is str))
    senses = []
    for key in ('blindsight', 'darkvision', 'tremorsense', 'truesight'):
        if _int(data.get(key)) > 0:
            senses.append(f'{key} {_int(data.get(key))} ft.' + (' (blind beyond this radius)' if key == 'blindsight' and data.get('blind') else ''))
    perception = next((s for s in data.get('skills') or [] if type(s) is dict and str(s.get('name')).lower() == 'perception'), None)
    passive = 10 + mon.mod('wis') + (prof * (2 if 'note' in perception else 1) if perception else 0)
    senses.append(f'passive Perception {passive}')
    add('senses', 'Senses', ', '.join(senses))
    languages = [l for l in data.get('languages') or [] if type(l) is dict and type(l.get('name')) is str]
    speaks = [l['name'] for l in languages if l.get('speaks', True) is not False]
    understands = [l['name'] for l in languages if l.get('speaks', True) is False]
    parts = list(speaks)
    if understands:
        text = 'understands ' + (' and '.join(understands) if len(understands) <= 2 else ', '.join(understands[:-1]) + ', and ' + understands[-1])
        if type(data.get('understandsBut')) is str and data['understandsBut'].strip():
            text += ' but ' + data['understandsBut'].strip()
        parts.append(text)
    if _int(data.get('telepathy')) > 0:
        parts.append(f"telepathy {_int(data.get('telepathy'))} ft.")
    add('languages', 'Languages', ', '.join(parts) or '—')
    cr = data.get('cr')
    if cr == '*':
        add('challenge', 'Challenge', str(data.get('customCr') or '').strip())
    elif cr is not None:
        xp = cr_xp(str(cr))
        add('challenge', 'Challenge', f'{cr}' + (f' ({xp:,} XP)' if xp is not None else ''))
    add('proficiency_bonus', 'Proficiency Bonus', _bonus(prof))
    sections = []
    def section(label, items, enabled=None, intro=None, outro=None, listed=False):
        body = mon.trait_entries(items)
        if listed and body:
            body = [{'type': 'list', 'items': body}]
        if not body and not (enabled and (intro or outro)):
            return
        entries = (mon.entries(intro) if enabled and intro else []) + body + (mon.entries(outro) if enabled and outro else [])
        sections.append((label + ('' if enabled in (None, True) else ' (disabled)'), entries, enabled))
    section('Traits', data.get('abilities'))
    section('Actions', data.get('actions'))
    section('Bonus Actions', data.get('bonusActions'))
    section('Reactions', data.get('reactions'))
    section('Legendary Actions', data.get('legendaries'), bool(data.get('isLegendary')), data.get('legendariesDescription'))
    section('Mythic Actions', data.get('mythics'), bool(data.get('isMythic')), data.get('mythicDescription'))
    section('Lair Actions', data.get('lairs'), bool(data.get('isLair')), data.get('lairDescription'), data.get('lairDescriptionEnd'), True)
    section('Regional Effects', data.get('regionals'), bool(data.get('isRegional')), data.get('regionalDescription'),
            data.get('regionalDescriptionEnd'), True)
    known_traits = {(t.get('name'), t.get('desc')) for t in data.get('abilities') or [] if type(t) is dict}
    legacy = [p for p in data.get('properties') or [] if type(p) is dict and (p.get('name'), p.get('desc')) not in known_traits]
    if legacy:
        warn('legacy_properties', 'Older-format "properties" entries are shown separately.')
        section('Properties', legacy)
    return facts, sections


def subtitle(data):
    size = str(data.get('size') or '').strip()
    kind = str(data.get('type') or '').strip()
    tag = str(data.get('tag') or '').strip()
    alignment = str(data.get('alignment') or '').strip()
    head = ' '.join(x for x in (size.capitalize(), kind.lower() + (f' ({tag})' if tag else '')) if x)
    return head + (f', {alignment}' if alignment else '')


def prepare_monster_file(raw, *, filename=None, limits=None, deadline=None, cancelled=lambda: False):
    """raw: original .monster bytes -> (snapshot, measurements)."""
    if type(raw) is not bytes:
        raise SourceError('invalid_request')
    if len(raw) > MAX_FILE_BYTES:
        raise SourceError('file_too_large')
    deadline = time.monotonic() + 10 if deadline is None else deadline
    def check():
        if cancelled():
            raise SourceError('cancelled')
        if time.monotonic() >= deadline:
            raise SourceError('deadline')
    try:
        data = json.loads(raw.decode('utf-8-sig'), parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeError, RecursionError):
        raise SourceError('malformed_file') from None
    if type(data) is not dict or type(data.get('name')) is not str or not data['name'].strip():
        raise SourceError('malformed_file')
    for key in ('abilities', 'actions', 'bonusActions', 'reactions', 'legendaries', 'mythics', 'lairs', 'regionals',
                'sthrows', 'skills', 'damagetypes', 'specialdamage', 'conditions', 'languages', 'properties'):
        if key in data and type(data[key]) is not list:
            raise SourceError('malformed_file', key)
    warnings = []
    def warn(code, message, owner=None, path=None):
        if (code, message, path) not in warnings:
            warnings.append((code, message, path))
    for unknown in sorted(set(data) - KNOWN):
        warn('unrecognized_property', f'Property "{unknown}" is not shown.', None, f'$/{unknown}')
    facts, sections = facts_and_sections(data, warn)
    digest = hashlib.sha256(raw).hexdigest()
    safe_name = re.sub(r'[\x00-\x1f]', '', filename)[:255] if type(filename) is str and filename.strip() else None
    provenance = [{'role': 'selected', 'provider': 'file', 'entity_id': f'file|sha256:{digest}', 'file_name': safe_name,
                   'file_sha256': digest, 'credits': [credit(f"Imported from {safe_name or 'a Tetra-cube .monster file'}")]}]
    return assemble(source_label=data['name'].strip(), subtitle=subtitle(data), facts=facts, sections=sections,
                    provenance=provenance, warnings=warnings, check=check, parser=lambda s: toggle_items([('text', s)]),
                    limits=limits or ModelLimits(), adapter_version=ADAPTER_VERSION)
