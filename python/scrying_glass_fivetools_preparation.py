"""Prepare a validated version-one statblock snapshot from 5e.tools (022.04e).

Pipeline: exact selected record -> ordered inheritance/templates/substitutions
(OrderedResolver) -> integral legendary group -> bounded supporting reference
collection -> safe node conversion -> species placeholders for the selected
creature's own text -> validate_snapshot. The result is a private, unsaved
preparation; apply/persistence/API binding belongs to 022.08. The six Scrying
Glass fields are never emitted as selected-creature facts.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, fields
from urllib.parse import quote

from .scrying_glass_fivetools_collector import (
    DATASET, PARTIAL_CODES, CollectionLimits, Collector, DatasetLimit, FiveToolsData, PreparationStop,
)
from .scrying_glass_fivetools_definitions import ENTRY_KEYS, definition_facts
from .scrying_glass_fivetools_nodes import NodeBuilder
from .scrying_glass_fivetools_resolution import Identity, Limits, ResolutionError
from .scrying_glass_fivetools_statblock import (
    HANDLED, METADATA, SECTIONS, SG_OWNED, monster_facts, ordered, type_line,
)
from .scrying_glass_fivetools_tags import strip_tags
from .scrying_glass_statblock_model import ModelLimits, StatblockError, canonical_bytes, content_digest, validate_snapshot

ADAPTER_VERSION = '5etools-04f-1'
PROVIDER = '5e.tools'
PAGES = {'monster': 'bestiary.html', 'spell': 'spells.html', 'condition': 'conditionsdiseases.html',
         'disease': 'conditionsdiseases.html', 'status': 'conditionsdiseases.html', 'item': 'items.html',
         'action': 'actions.html', 'variantrule': 'variantrules.html'}
SRD = {
    'srd52': ('This work includes material from the System Reference Document 5.2 ("SRD 5.2") by Wizards of the Coast LLC, '
              'available at https://www.dndbeyond.com/srd. The SRD 5.2 is licensed under the Creative Commons Attribution '
              '4.0 International License.'),
    'srd': ('This work includes material taken from the System Reference Document 5.1 ("SRD 5.1") by Wizards of the Coast '
            'LLC. The SRD 5.1 is licensed under the Creative Commons Attribution 4.0 International License.'),
}
CC_BY = ('CC-BY-4.0', 'https://creativecommons.org/licenses/by/4.0/legalcode')
GROUP_SECTIONS = (('lairActions', 'Lair Actions'), ('regionalEffects', 'Regional Effects'), ('mythicEncounter', 'Mythic Encounter'))


class PreparationError(ValueError):
    def __init__(self, code, detail=None):
        self.code, self.detail = code, detail
        super().__init__(code)


@dataclass(frozen=True)
class PreparationLimits:
    resolution: Limits = Limits()
    collection: CollectionLimits = CollectionLimits()
    model: ModelLimits = ModelLimits()

    def __post_init__(self):
        for field, kind in (('resolution', Limits), ('collection', CollectionLimits), ('model', ModelLimits)):
            if not isinstance(getattr(self, field), kind):
                raise ValueError('invalid_limits:' + field)

    @classmethod
    def from_mapping(cls, values):
        """Build from the agreed statblocks.limits names; unknown names are rejected."""
        values = dict(values or {})
        groups = {}
        for name, kind in (('resolution', Limits), ('collection', CollectionLimits), ('model', ModelLimits)):
            names = {f.name for f in fields(kind)}
            groups[name] = kind(**{k: values.pop(k) for k in list(values) if k in names})
        if values:
            raise ValueError('unknown_limits:' + ','.join(sorted(values)))
        return cls(**groups)


@dataclass(frozen=True)
class Prepared:
    snapshot: dict
    measurements: dict
    selected: Identity
    adapter_version: str = ADAPTER_VERSION


def _species_splitter(label, protected):
    if not label or not label.strip():
        return None
    words = [re.escape(part) for part in label.split()]
    pattern = re.compile(r'(?<!\w)' + r'\s+'.join(words) + r'(?!\w)', re.IGNORECASE)
    guards = [re.compile(r'(?<!\w)' + r'\s+'.join(re.escape(p) for p in phrase.split()) + r'(?!\w)', re.IGNORECASE)
              for phrase in protected]
    def split(text):
        blocked = [(m.start(), m.end()) for guard in guards for m in guard.finditer(text)]
        out, last = [], 0
        for match in pattern.finditer(text):
            if any(start <= match.start() < end for start, end in blocked):
                continue
            if match.start() > last:
                out.append(('text', text[last:match.start()]))
            out.append(('species', match.group(0)))
            last = match.end()
        if last < len(text):
            out.append(('text', text[last:]))
        return out
    return split


def _page_url(site, kind, record):
    page = PAGES.get(kind)
    if not page:
        return None
    return f"{site}/{page}#" + quote(f"{record['name']}_{record['source']}".lower(), safe='')


def _credits(record, kind):
    credits = [{'position': 0, 'attribution': f"{record.get('name')} ({record.get('source')}), {kind} data from 5e.tools",
                'publisher': None, 'license_name': None, 'license_url': None}]
    for flag in ('srd52', 'srd'):
        if record.get(flag):
            credits.append({'position': len(credits), 'attribution': SRD[flag], 'publisher': 'Wizards of the Coast LLC',
                            'license_name': CC_BY[0], 'license_url': CC_BY[1]})
            break
    return credits


def prepare_statblock(name, source, *, fetch, deadline, cancelled=lambda: False, limits=None,
                      data_root='https://5e.tools/data', site='https://5e.tools', clock=time.monotonic,
                      version_of=None):
    """Return Prepared or raise PreparationError. fetch(path) -> bytes for allowlisted paths.

    ``version_of`` (base name, base source) selects a version of that monster (SG-TODO-033).
    """
    limits = PreparationLimits() if limits is None else limits
    if not isinstance(limits, PreparationLimits) or type(name) is not str or type(source) is not str or not name.strip() or not source.strip():
        raise PreparationError('invalid_request')
    if version_of is not None and (type(version_of) not in (tuple, list) or len(version_of) != 2
                                   or any(type(v) is not str or not v.strip() for v in version_of)):
        raise PreparationError('invalid_request')
    def check():
        if cancelled():
            raise PreparationStop('cancelled')
        if clock() >= deadline:
            raise PreparationStop('deadline')
    data = FiveToolsData(lambda path: fetch(path), check=check, response_bytes=limits.resolution.response_bytes,
                         dataset_files=limits.collection.dataset_files)
    collector = Collector(data, resolution_limits=limits.resolution, limits=limits.collection,
                          deadline=deadline, cancelled=cancelled, clock=clock)
    try:
        selected = Identity(DATASET, 'monster', source, name)
        record, provenance = collector.resolve_selected(name, source, tuple(version_of) if version_of else None)
        group, group_provenance = collector.legendary_group(record)
        collector.collect(record, [('legendaryGroup', group)] if group else [])
        snapshot = _assemble(record, group, group_provenance, provenance, collector, limits, data_root, site, check)
    except PreparationStop as exc:
        raise PreparationError(str(exc)) from None
    except ResolutionError as exc:
        code = exc.diagnostic.code
        if code == 'missing_dependency' and len(exc.diagnostic.chain) == 1:
            code = 'selected_unavailable'
        raise PreparationError(code, exc.diagnostic) from None
    except LookupError as exc:
        raise PreparationError(str(exc.args[0])) from None
    except DatasetLimit:
        raise PreparationError('dataset_file_limit') from None
    except StatblockError as exc:
        raise PreparationError(exc.code, exc.path) from None
    except (ValueError, UnicodeError) as exc:
        raise PreparationError(exc.args[0] if exc.args and type(exc.args[0]) is str and exc.args[0].isidentifier() else 'malformed_dataset') from None
    except RecursionError:
        raise PreparationError('execution_stack_limit') from None
    canonical = canonical_bytes(snapshot, limits.model)
    depths, parents = {}, {n['local_id']: n['parent_local_id'] for n in snapshot['nodes']}
    for node in snapshot['nodes']:
        depth, cursor = 0, node['local_id']
        while cursor is not None:
            depth += 1
            cursor = parents[cursor]
        depths[node['local_id']] = depth
    measurements = {
        'snapshot_bytes': len(canonical),
        'content_nodes': len(snapshot['nodes']),
        'content_depth': max(depths.values(), default=0),
        'max_text_value_bytes': max((len(n.get('text', '').encode()) for n in snapshot['nodes'] if n.get('text')), default=0),
        'supporting_definitions': len(snapshot['definitions']),
        'supporting_reference_bytes': collector.reference_bytes,
        'fetched_dataset_bytes': data.fetched_bytes,
        'warnings': len(snapshot['warnings']),
    }
    return Prepared(snapshot, measurements, selected)


def _assemble(record, group, group_provenance, provenance, collector, limits, data_root, site, check):
    warnings = []
    def warn(code, message, owner=None, path=None):
        warnings.append({'position': len([w for w in warnings if w.get('definition_id') == owner]),
                         'code': code, 'message': message, 'definition_id': owner, 'source_path': path})
    for code, message, path in collector.warnings:
        warn(code, message, None, path)
    lookup = {key: d.local_id for key, d in collector.definitions.items()}
    def reference(kind, name, source):
        if type(name) is not str or type(source) is not str:
            return None
        return lookup.get((kind, name.lower(), source.lower()))
    builder = NodeBuilder(check=check, warn=warn, reference=reference)
    protected = [d.record['name'] for d in collector.definitions.values() if d.kind == 'monster']
    splitter = _species_splitter(record.get('name'), protected)
    builder.placeholder = splitter
    facts = []
    def fact(owner, key, label, text, number=None):
        if not text:
            return
        position = len([f for f in facts if f.get('definition_id') == owner])
        facts.append({'position': position, 'key': key, 'label': label, 'display_text': text,
                      'definition_id': owner, 'integer_value': number})
    for key, label, text, number in monster_facts(record, selected=True):
        fact(None, key, label, text, number)
    _monster_sections(builder, None, record, group, warn, fact)
    definitions, provenance_rows = [], []
    def add_provenance(role, kind, entity, owner):
        row = {'position': len([p for p in provenance_rows if p.get('definition_id') == owner]), 'role': role,
               'provider': PROVIDER, 'entity_id': f"{kind}|{entity['name']}|{entity['source']}",
               'adapter_version': ADAPTER_VERSION, 'credits': _credits(entity, kind), 'definition_id': owner,
               'endpoint': data_root, 'source_code': entity['source'], 'source_url': _page_url(site, kind, entity)}
        provenance_rows.append(row)
    add_provenance('selected', 'monster', record, None)
    for item in provenance[1:]:
        add_provenance(item.role, item.identity.kind, {'name': item.identity.name, 'source': item.identity.source}, None)
    if group is not None:
        add_provenance('reference', 'legendaryGroup', group, None)
    for index, definition in enumerate(collector.definitions.values()):
        check()
        entity = definition.record
        definitions.append({'local_id': definition.local_id, 'kind': definition.kind, 'name': entity['name'],
                            'source_key': f"{entity['name']}|{entity['source']}", 'source_code': entity['source'],
                            'position': index})
        add_provenance('reference', definition.kind, entity, definition.local_id)
        for item in definition.provenance[1:]:
            add_provenance(item.role, item.identity.kind, {'name': item.identity.name, 'source': item.identity.source}, definition.local_id)
        if definition.kind == 'monster':
            for key, label, text, number in monster_facts(entity, selected=False):
                fact(definition.local_id, key, label, text, number)
            _monster_sections(builder, definition.local_id, entity, definition.legendary_group, warn, fact)
            continue
        for key, label, text in definition_facts(definition.kind, entity):
            fact(definition.local_id, key, label, text)
        for prop, label in ENTRY_KEYS.get(definition.kind, (('entries', None),)):
            if not entity.get(prop):
                continue
            parent = builder.add('section', None, definition.local_id, label=label) if label else None
            builder.entries(parent, definition.local_id, entity[prop], f'$/{prop}')
    completeness = 'partial' if any(w['code'] in PARTIAL_CODES for w in warnings) else 'available'
    snapshot = {
        'model_version': 1, 'source_label': record['name'], 'subtitle': type_line(record),
        'completeness': completeness, 'provenance': provenance_rows, 'facts': facts,
        'definitions': definitions, 'nodes': builder.rows, 'warnings': warnings,
    }
    for group_rows in (snapshot['facts'], snapshot['warnings'], snapshot['provenance']):
        for row in group_rows:
            for optional in [k for k, v in row.items() if v is None and k in ('definition_id', 'integer_value', 'source_path', 'source_url')]:
                del row[optional]
    snapshot = validate_snapshot(snapshot, limits.model)
    snapshot['content_digest'] = content_digest(snapshot, limits.model)
    return snapshot


def _monster_sections(builder, owner, mon, group, warn, fact):
    for note, label in (('actionNote', 'Action Note'), ('reactionNote', 'Reaction Note')):
        if type(mon.get(note)) is str:
            fact(owner, note, label, strip_tags(mon[note]))
    for prop, label, header in SECTIONS:
        items = ordered(mon, prop)
        heading = mon.get(header) if header else None
        if not items and not heading:
            continue
        section = builder.add('section', None, owner, label=label)
        if heading:
            builder.entries(section, owner, heading, f'$/{header}')
        for index, item in enumerate(items):
            footer = item.pop('_footer', None) if type(item) is dict else None
            builder.entry(section, owner, item, f'$/{prop}/{index}')
            if footer:
                builder.entries(section, owner, footer, f'$/{prop}/{index}/footer')
    if group is not None:
        for prop, label in GROUP_SECTIONS:
            if group.get(prop):
                section = builder.add('section', None, owner, label=label)
                builder.entries(section, owner, group[prop], f'$/legendaryGroup/{prop}')
    if mon.get('variant'):
        section = builder.add('section', None, owner, label='Variants')
        builder.entries(section, owner, mon['variant'], '$/variant')
    if mon.get('footer'):
        builder.entries(builder.add('section', None, owner, label=None), owner, mon['footer'], '$/footer')
    for key in mon:
        if key in HANDLED or key in METADATA or key in SG_OWNED or key.startswith('_'):
            continue
        warn('unrecognized_property', f'Property "{key}" is shown as plain text.', owner, f'$/{key}')
        fact(owner, 'source_' + re.sub(r'[^A-Za-z0-9_]', '_', key), key, builder.plain(mon[key]) or json.dumps(mon[key], ensure_ascii=False)[:2000])
