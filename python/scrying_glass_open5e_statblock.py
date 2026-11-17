"""Open5e v2 statblock adapter (SG-TODO-022.05).

Exact identity: configured HTTPS endpoint + v2 creature key (+ its document).
prepare_open5e fetches /creatures/<key>/ and, for attribution and licence,
/documents/<document key>/ (callers should pass a CachingFetcher-style fetch).
Every supplied section is kept in statblock order; descriptions are the safe
Markdown subset. Lair actions, regional effects and legendary intros are not
supplied by the v2 API and are never invented. The six Scrying Glass fields
(name, species, AC, current/max HP, initiative bonus) are never facts.
discover_open5e lists exact-name candidates for 022.08.
"""
from __future__ import annotations

import json
import re
import time
from fractions import Fraction
from urllib.parse import quote, urlencode, urljoin, urlsplit

from .scrying_glass_statblock_sources import (
    SourceError, assemble, credit, markdown_entries, markdown_inline, name_key,
)
from .scrying_glass_statblock_model import ModelLimits

ADAPTER_VERSION = 'open5e-v2-05-1'
PROVIDER = 'Open5e'
KEY = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,199}\Z')
ABILITIES = ('strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma')
SECTION_ORDER = (('ACTION', 'Actions'), ('BONUS_ACTION', 'Bonus Actions'), ('REACTION', 'Reactions'),
                 ('LEGENDARY_ACTION', 'Legendary Actions'), ('MYTHIC_ACTION', 'Mythic Actions'),
                 ('LAIR_ACTION', 'Lair Actions'))
SG_OWNED = frozenset(('armor_class', 'armor_detail', 'hit_points', 'hit_dice', 'initiative_bonus', 'name'))
KNOWN = SG_OWNED | frozenset((
    'key', 'document', 'type', 'size', 'challenge_rating', 'proficiency_bonus', 'speed', 'speed_all',
    'category', 'subcategory', 'alignment', 'languages', 'experience_points', 'ability_scores', 'modifiers',
    'saving_throws', 'saving_throws_all', 'skill_bonuses', 'skill_bonuses_all', 'passive_perception',
    'resistances_and_immunities', 'normal_sight_range', 'darkvision_range', 'blindsight_range',
    'tremorsense_range', 'truesight_range', 'actions', 'traits', 'creaturesets', 'environments',
    'illustration', 'crossreferences', 'url'))


def _bonus(value):
    return f"{'+' if value >= 0 else ''}{value}" if type(value) is int else str(value)


def challenge_text(value):
    if type(value) not in (int, float) or type(value) is bool:
        return ''
    fraction = Fraction(value).limit_denominator(8)
    return str(fraction.numerator) if fraction.denominator == 1 else f'{fraction.numerator}/{fraction.denominator}'


def _named(value):
    return value.get('name') if type(value) is dict and type(value.get('name')) is str else None


def creature_facts(record):
    facts = []
    def add(key, label, text, number=None):
        if text:
            facts.append((key, label, text, number))
    speed = record.get('speed') if type(record.get('speed')) is dict else {}
    unit = 'ft.' if speed.get('unit') in (None, 'feet') else str(speed.get('unit'))
    parts = []
    for mode in ('walk', 'burrow', 'climb', 'fly', 'swim', 'crawl'):
        value = speed.get(mode)
        if type(value) in (int, float) and value and not (mode == 'walk' and value == 0):
            parts.append(f"{'' if mode == 'walk' else mode + ' '}{value} {unit}" + (' (hover)' if mode == 'fly' and speed.get('hover') else ''))
    add('speed', 'Speed', ', '.join(parts))
    scores, modifiers = record.get('ability_scores') or {}, record.get('modifiers') or {}
    for name in ABILITIES:
        score = scores.get(name)
        if type(score) is int:
            modifier = modifiers.get(name, (score - 10) // 2)
            add(name[:3], name.title(), f'{score} ({_bonus(modifier)})', score)
    saves = record.get('saving_throws') or {}
    add('saving_throws', 'Saving Throws', ', '.join(f'{k[:3].title()} {_bonus(v)}' for k, v in saves.items()))
    skills = record.get('skill_bonuses') or {}
    add('skills', 'Skills', ', '.join(f"{k.replace('_', ' ').title()} {_bonus(v)}" for k, v in skills.items()))
    resist = record.get('resistances_and_immunities') or {}
    for key, label in (('damage_vulnerabilities', 'Damage Vulnerabilities'), ('damage_resistances', 'Damage Resistances'),
                       ('damage_immunities', 'Damage Immunities'), ('condition_immunities', 'Condition Immunities')):
        text = resist.get(key + '_display')
        if not text and type(resist.get(key)) is list:
            text = ', '.join(filter(None, (_named(v) for v in resist[key])))
        add(key, label, text if type(text) is str else '')
    senses = [f"{label} {record[key]} ft." for key, label in (('blindsight_range', 'blindsight'), ('darkvision_range', 'darkvision'),
              ('tremorsense_range', 'tremorsense'), ('truesight_range', 'truesight')) if type(record.get(key)) in (int, float) and record[key]]
    if type(record.get('passive_perception')) is int:
        senses.append(f"passive Perception {record['passive_perception']}")
    add('senses', 'Senses', ', '.join(senses))
    languages = record.get('languages') or {}
    add('languages', 'Languages', languages.get('as_string') if type(languages.get('as_string')) is str else '')
    challenge = challenge_text(record.get('challenge_rating'))
    if challenge:
        details = [f"XP {record['experience_points']:,}"] if type(record.get('experience_points')) is int else []
        if type(record.get('proficiency_bonus')) is int:
            details.append(f"PB {_bonus(record['proficiency_bonus'])}")
        add('challenge', 'Challenge', challenge + (f" ({'; '.join(details)})" if details else ''))
    environments = [n for n in (_named(e) for e in record.get('environments') or []) if n]
    add('environment', 'Environment', ', '.join(environments))
    sets = [n for n in (_named(e) for e in record.get('creaturesets') or []) if n]
    add('creature_sets', 'Creature Sets', ', '.join(sets))
    return facts


def subtitle(record):
    size, kind = _named(record.get('size')) or '', _named(record.get('type')) or ''
    sub = record.get('subcategory')
    text = ' '.join(x for x in (size, kind + (f' ({sub})' if type(sub) is str and sub else '')) if x)
    alignment = record.get('alignment')
    return text + (f', {alignment}' if type(alignment) is str and alignment else '')


def action_name(action, kind):
    name = action.get('name') if type(action.get('name')) is str else ''
    usage = action.get('usage_limits')
    extras = []
    if type(usage) is dict:
        param, usage_type = usage.get('param'), usage.get('type')
        if usage_type == 'RECHARGE_ON_ROLL' and type(param) is int:
            extras.append(f'Recharge {param}–6' if param < 6 else 'Recharge 6')
        elif usage_type == 'PER_DAY' and type(param) is int:
            extras.append(f'{param}/Day')
        elif usage_type:
            extras.append(f"{str(usage_type).replace('_', ' ').title()}{f' {param}' if param is not None else ''}")
    cost = action.get('legendary_action_cost')
    if kind == 'LEGENDARY_ACTION' and type(cost) is int and cost > 1:
        extras.append(f'Costs {cost} Actions')
    form = action.get('limited_to_form')
    if type(form) is str and form:
        extras.append(f'{form} Form Only')
    return name + ''.join(f' ({e})' for e in extras)


def creature_sections(record, warn):
    sections = []
    traits = [t for t in record.get('traits') or [] if type(t) is dict]
    if traits:
        sections.append(('Traits', [{'type': 'entries', 'name': t.get('name') or None,
                                      'entries': markdown_entries(t.get('desc') or '', warn)} for t in traits], None))
    actions = [a for a in record.get('actions') or [] if type(a) is dict]
    known = {kind for kind, _ in SECTION_ORDER}
    for kind, label in SECTION_ORDER + tuple((k, str(k).replace('_', ' ').title() + 's') for k in
                                             dict.fromkeys(a.get('action_type') for a in actions) if k not in known):
        group = sorted((a for a in actions if a.get('action_type') == kind),
                       key=lambda a: a.get('order_in_statblock') if type(a.get('order_in_statblock')) is int else 10**6)
        if group:
            if kind not in known:
                warn('unrecognized_action_type', f'Action type "{kind}" shown as its own section.', None)
            sections.append((label, [{'type': 'entries', 'name': action_name(a, kind),
                                      'entries': markdown_entries(a.get('desc') or '', warn)} for a in group], None))
    return sections


def _document_credit(document, detail):
    publisher = _named(document.get('publisher'))
    name = document.get('display_name') or document.get('name') or document.get('key')
    licences = detail.get('licenses') if type(detail) is dict else None
    licence = licences[0] if type(licences) is list and licences and type(licences[0]) is dict else None
    url = None
    if licence:
        for key in ('url', 'permalink', 'link'):
            value = licence.get(key)
            if type(value) is str and urlsplit(value).scheme == 'https':
                url = value
                break
    return credit(f"{name} via Open5e", publisher=publisher,
                  license_name=(licence.get('name') or licence.get('key')) if licence else None, license_url=url)


def prepare_open5e(key, *, fetch, deadline, base_url='https://api.open5e.com/v2', limits=None, cancelled=lambda: False):
    """Return (snapshot, measurements); fetch(url, deadline=...) -> bytes."""
    if type(key) is not str or not KEY.match(key):
        raise SourceError('invalid_request')
    base = base_url.rstrip('/')
    def check():
        if cancelled():
            raise SourceError('cancelled')
        if time.monotonic() >= deadline:
            raise SourceError('deadline')
    def get(url):
        check()
        try:
            return json.loads(fetch(url, deadline=deadline), parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        except SourceError:
            raise
        except (ValueError, UnicodeError, RecursionError):
            raise SourceError('malformed_response') from None
    record = get(f"{base}/creatures/{quote(key, safe='')}/?format=json")
    if type(record) is not dict or record.get('key') != key or type(record.get('name')) is not str:
        raise SourceError('identity_mismatch')
    warnings = []
    def warn(code, message, owner=None, path=None):
        if (code, message, path) not in warnings:
            warnings.append((code, message, path))
    document = record.get('document') if type(record.get('document')) is dict else {}
    detail = None
    document_key = document.get('key')
    if type(document_key) is str and KEY.match(document_key):
        try:
            detail = get(f"{base}/documents/{quote(document_key, safe='')}/?format=json")
        except SourceError as exc:
            if exc.code in ('cancelled', 'deadline'):
                raise
            warn('license_unavailable', 'The document licence could not be retrieved.')
    if type(detail) is dict and not detail.get('licenses'):
        warn('license_unavailable', 'The document licence is not stated.')
    for unknown in sorted(set(record) - KNOWN):
        warn('unrecognized_property', f'Property "{unknown}" is not shown.', None, f'$/{unknown}')
    if record.get('illustration'):
        warn('media_omitted', 'The illustration is not shown.')
    sections = creature_sections(record, warn)
    gamesystem = _named(document.get('gamesystem'))
    provenance = [{'role': 'selected', 'provider': PROVIDER, 'endpoint': base, 'api_version': 'v2',
                   'entity_id': f'creature|{key}', 'source_code': document_key if type(document_key) is str else None,
                   'edition': gamesystem, 'source_url': f"https://open5e.com/monsters/{quote(key, safe='')}",
                   'credits': [_document_credit(document, detail)]}]
    title = subtitle(record) + (f' — {document.get("display_name") or document.get("name")}' if document.get('name') else '')
    return assemble(source_label=record['name'], subtitle=title, facts=creature_facts(record), sections=sections,
                    provenance=provenance, warnings=warnings, check=check, parser=markdown_inline,
                    limits=limits or ModelLimits(), adapter_version=ADAPTER_VERSION)


def discover_open5e(species, *, fetch, deadline, base_url='https://api.open5e.com/v2', max_pages=10):
    """Exact-name candidates [{key, name, document, gamesystem}]; raises when incomplete."""
    base = base_url.rstrip('/')
    url = f"{base}/creatures/?" + urlencode({'name__iexact': species, 'limit': 100, 'format': 'json'})
    wanted, out, seen = name_key(species), [], set()
    variants = {species, species.replace('’', "'"), species.replace("'", '’')}
    queue = [f"{base}/creatures/?" + urlencode({'name__iexact': v, 'limit': 100, 'format': 'json'}) for v in variants]
    pages = 0
    while queue:
        url = queue.pop(0)
        while url:
            pages += 1
            if pages > max_pages or url in seen or urlsplit(url).hostname != urlsplit(base).hostname:
                raise SourceError('discovery_incomplete')
            seen.add(url)
            listing = json.loads(fetch(url, deadline=deadline))
            if type(listing) is not dict or type(listing.get('results')) is not list:
                raise SourceError('malformed_response')
            for item in listing['results']:
                key = item.get('key') if type(item) is dict else None
                if type(key) is str and KEY.match(key) and name_key(item.get('name')) == wanted and key not in {c['key'] for c in out}:
                    document = item.get('document') if type(item.get('document')) is dict else {}
                    out.append({'key': key, 'name': item['name'], 'document': document.get('display_name') or document.get('name'),
                                'gamesystem': _named(document.get('gamesystem'))})
            url = urljoin(url, listing['next']) if listing.get('next') else None
    return out
