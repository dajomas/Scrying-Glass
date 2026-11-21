"""Exact-source dataset index and bounded reference collection (022.04e).

FiveToolsData loads only allowlisted dataset files through a supplied fetch
callable, indexes records by (kind, name, source) the way the pinned runtime
matches them (case-insensitive URL hash) and serves exact matches to the
inheritance resolver. collect() walks supporting references breadth-first by
shortest path under the agreed limits; anything not collected is reported as
an explicit partial-content warning, never substituted from another source.
"""
from __future__ import annotations

import json
import re
from collections import OrderedDict, deque
from dataclasses import dataclass, fields

from .scrying_glass_fivetools_fetch import allowed_dataset_path
from .scrying_glass_fivetools_resolution import Identity, ResolutionError
from .scrying_glass_fivetools_ordered_resolution import OrderedResolver
from .scrying_glass_fivetools_tags import collect_references

DATASET = '5etools'
FILE_NAME = re.compile(r'[A-Za-z0-9_.-]+\.json\Z')
# kind -> list of (file, property); 'monster'/'spell' use their index files.
FIXED = {
    'monsterTemplate': [('bestiary/template.json', 'monsterTemplate')],
    'legendaryGroup': [('bestiary/legendarygroups.json', 'legendaryGroup')],
    'condition': [('conditionsdiseases.json', 'condition')],
    'disease': [('conditionsdiseases.json', 'disease')],
    'status': [('conditionsdiseases.json', 'status')],
    'item': [('items.json', 'item'), ('items.json', 'itemGroup'), ('items-base.json', 'baseitem')],
    'skill': [('skills.json', 'skill')],
    'sense': [('senses.json', 'sense')],
    'action': [('actions.json', 'action')],
    'variantrule': [('variantrules.json', 'variantrule'), ('generated/gendata-variantrules.json', 'variantrule')],
}
INDEXED = {'monster': ('bestiary/index.json', 'bestiary', 'monster'), 'spell': ('spells/index.json', 'spells', 'spell')}
INHERITING = frozenset(('monster', 'monsterTemplate', 'legendaryGroup', 'item'))
SCAN_KEYS = {
    'spell': ('entries', 'entriesHigherLevel', 'components', 'time'),
    'item': ('entries', 'additionalEntries', '_fullEntries'),
    'legendaryGroup': ('lairActions', 'regionalEffects', 'mythicEncounter'),
}
MONSTER_SKIP = frozenset(('name', 'source', 'page', '_copy_templates', '_versions', 'legendaryGroup',
                          'otherSources', 'referenceSources', 'reprintedAs', 'attachedItems'))
SELECTED_SKIP = MONSTER_SKIP | frozenset(('ac', 'hp', 'initiative'))
PARTIAL_CODES = frozenset(('reference_unavailable', 'reference_ambiguous', 'reference_depth_limit',
                           'supporting_definitions_limit', 'supporting_reference_bytes_limit',
                           'reference_resolution_failed', 'legendary_group_unavailable',
                           'dataset_file_limit'))


@dataclass(frozen=True)
class CollectionLimits:
    reference_steps: int = 16
    supporting_definitions: int = 256
    supporting_reference_bytes: int = 16777216
    dataset_files: int = 64

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) is not int or not 0 < value <= 2**63 - 1:
                raise ValueError('invalid_limit:' + field.name)


class DatasetLimit(Exception):
    pass


def key_of(kind, name, source):
    return kind, name.lower(), source.lower()


class FiveToolsData:
    """Lazy exact index over fetched dataset files; also an ExactLoader."""

    def __init__(self, fetch, *, check, response_bytes=10485760, dataset_files=64):
        self._fetch, self._check = fetch, check
        self._response_bytes, self._max_files = response_bytes, dataset_files
        self._files, self._indexed, self._records = {}, set(), {}
        self._base_items, self._generated = None, False
        self.fetched_bytes = 0

    def _file(self, path):
        if path in self._files:
            return self._files[path]
        if not allowed_dataset_path(path):
            raise ValueError('dataset_path_not_allowed')
        if len(self._files) >= self._max_files:
            raise DatasetLimit('dataset_file_limit')
        self._check()
        raw = self._fetch(path)
        if type(raw) is not bytes or len(raw) > self._response_bytes:
            raise ValueError('response_bytes_limit')
        self.fetched_bytes += len(raw)
        data = json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite')))
        if type(data) is not dict:
            raise ValueError('malformed_dataset')
        self._files[path] = data
        return data

    def _index(self, path, prop, kind):
        marker = (path, prop, kind)
        if marker in self._indexed:
            return
        data = self._file(path)
        if prop == 'baseitem':
            self._base_items = list(data.get(prop) or [])  # in file order, for generated variants
        for record in data.get(prop) or []:
            self._check()
            if type(record) is dict and type(record.get('name')) is str and type(record.get('source')) is str:
                encoded = json.dumps(record, ensure_ascii=False, separators=(',', ':')).encode()
                self._records.setdefault(key_of(kind, record['name'], record['source']), []).append(encoded)
        self._indexed.add(marker)
        if type(data) is dict:
            data.pop(prop, None)

    def _paths(self, kind, source):
        if kind in INDEXED:
            index_path, folder, prop = INDEXED[kind]
            index = self._file(index_path)
            names = {k.lower(): v for k, v in index.items() if type(k) is str} if type(index) is dict else {}
            name = names.get(source.lower())
            if type(name) is not str or not FILE_NAME.match(name):
                return []
            path = f'{folder}/{name}'
            return [(path, prop)] if allowed_dataset_path(path) else []
        return FIXED.get(kind, [])

    def load(self, identity):
        """ExactLoader: every record matching the runtime's entity hash."""
        for path, prop in self._paths(identity.kind, identity.source):
            self._index(path, prop, identity.kind)
        key = key_of(identity.kind, identity.name, identity.source)
        if identity.kind == 'item' and key not in self._records and not self._generated:
            self._generate_items()
        return tuple(self._records.get(key, ()))

    def _generate_items(self):
        """SG-TODO-033: index the runtime's generic and specific magic-item variants."""
        from .scrying_glass_fivetools_items import ItemVariantError, _entity_source, generate_variants
        self._generated = True
        variants = self._file('magicvariants.json')
        try:
            generics, specifics = generate_variants({'baseitem': self._base_items or []}, variants)
        except (ItemVariantError, ValueError):
            return  # references stay unavailable, as before
        for record in generics + specifics:
            self._check()
            name, source = record.get('name'), _entity_source(record)
            if type(name) is str and type(source) is str:
                encoded = json.dumps(record, ensure_ascii=False, separators=(',', ':')).encode()
                self._records.setdefault(key_of('item', name, source), []).append(encoded)
        variants.pop('magicvariant', None)

    def records(self, kind, source):
        """Every indexed record of ``kind`` from the file(s) holding ``source`` (encoded JSON)."""
        paths = self._paths(kind, source)
        for path, prop in paths:
            self._index(path, prop, kind)
        files = {key for key in self._records if key[0] == kind} if paths else set()
        return [raw for key in sorted(files) for raw in self._records[key]]


@dataclass
class Definition:
    local_id: str
    kind: str
    record: dict
    depth: int
    provenance: tuple
    raw_bytes: int
    legendary_group: dict | None = None


def scan_value(kind, record, *, selected=False):
    if kind == 'monster':
        skip = SELECTED_SKIP if selected else MONSTER_SKIP
        return {k: v for k, v in record.items() if k not in skip}
    keys = SCAN_KEYS.get(kind, ('entries',))
    return {k: record[k] for k in keys if k in record}


class Collector:
    """Resolve the selected creature and its supporting definitions."""

    def __init__(self, data, *, resolution_limits, limits, deadline, cancelled, clock):
        self.data, self.limits, self.deadline = data, limits, deadline
        self.cancelled, self.clock = cancelled, clock
        self.resolver = OrderedResolver(data, limits=resolution_limits, clock=clock)
        self.definitions, self.warnings = OrderedDict(), []
        self.reference_bytes, self._done, self._count = 0, set(), 0

    def warn(self, code, message, path=None):
        self.warnings.append((code, message, path))

    def resolve(self, kind, name, source):
        """Return (record, provenance) or raise ResolutionError/DatasetLimit."""
        identity = Identity(DATASET, kind, source, name)
        if kind in INHERITING:
            result = self.resolver.resolve(identity, deadline=self.deadline, cancelled=self.cancelled)
            record = result.record()
            record.pop('_isCopy', None)
            return record, result.provenance
        matches = self.data.load(identity)
        if len(matches) != 1:
            raise LookupError('reference_unavailable' if not matches else 'reference_ambiguous')
        return json.loads(matches[0]), ()

    def resolve_selected(self, name, source, version_of=None):
        """The selected creature: a monster, or a version of one (SG-TODO-033).

        Without ``version_of`` an exact monster wins; otherwise the version's base is
        searched among the monsters stored with the version's source.
        """
        from .scrying_glass_fivetools_versions import resolve_version
        if version_of is None:
            if self.data.load(Identity(DATASET, 'monster', source, name)):
                return self.resolve('monster', name, source)
            version_of = self._version_base(name, source)
        parent, _ = self.resolve('monster', *version_of)
        record, provenance = resolve_version(self.data, parent, name, source, limits=self.resolver.limits,
                                             deadline=self.deadline, cancelled=self.cancelled, clock=self.clock,
                                             dataset=DATASET)
        record.pop('_isCopy', None)
        return record, provenance

    def _version_base(self, name, source):
        from .scrying_glass_fivetools_versions import version_names
        wanted = (name.lower(), source.lower())
        for raw in self.data.records('monster', source):
            self._check()
            record = json.loads(raw)
            if not (record.get('_versions') or record.get('variant') or record.get('_copy')):
                continue
            if '_copy' in record:
                record, _ = self.resolve('monster', record['name'], record['source'])
            if any((n.lower(), s.lower()) == wanted for n, s in version_names(record)):
                return record['name'], record['source']
        raise LookupError('selected_unavailable')

    def legendary_group(self, record):
        meta = record.get('legendaryGroup')
        if type(meta) is not dict or type(meta.get('name')) is not str or type(meta.get('source')) is not str:
            return None, ()
        try:
            return self.resolve('legendaryGroup', meta['name'], meta['source'])
        except (ResolutionError, LookupError, DatasetLimit, ValueError):
            self.warn('legendary_group_unavailable', f"Legendary group {meta['name']} ({meta['source']}) is unavailable.")
            return None, ()

    def collect(self, selected_record, extra_scans=()):
        found = OrderedDict()
        collect_references(scan_value('monster', selected_record, selected=True), found, self._check)
        for kind, value in extra_scans:
            collect_references(scan_value(kind, value), found, self._check)
        queue = deque((identity, 1) for identity in found)
        while queue:
            self._check()
            (kind, name, source), depth = queue.popleft()
            key = key_of(kind, name, source)
            if key in self._done:
                continue
            self._done.add(key)
            label = f'{name} ({source})'
            if depth > self.limits.reference_steps:
                self.warn('reference_depth_limit', f'{label} is beyond the reference depth limit.')
                continue
            if len(self.definitions) >= self.limits.supporting_definitions:
                self.warn('supporting_definitions_limit', f'{label} exceeds the supporting definition limit.')
                continue
            try:
                record, provenance = self.resolve(kind, name, source)
            except ResolutionError as exc:
                if exc.diagnostic.code in ('deadline', 'cancelled'):
                    raise
                code = 'reference_unavailable' if exc.diagnostic.code == 'missing_dependency' and len(exc.diagnostic.chain) == 1 else 'reference_resolution_failed'
                self.warn(code, f'{label} could not be resolved ({exc.diagnostic.code}).')
                continue
            except LookupError as exc:
                self.warn(str(exc.args[0]), f'{label} is not available from the configured source.')
                continue
            except DatasetLimit:
                self.warn('dataset_file_limit', f'{label} needs more dataset files than allowed.')
                continue
            size = len(json.dumps(record, ensure_ascii=False, separators=(',', ':')).encode())
            if self.reference_bytes + size > self.limits.supporting_reference_bytes:
                self.warn('supporting_reference_bytes_limit', f'{label} exceeds the supporting reference size limit.')
                continue
            self.reference_bytes += size
            self._count += 1
            group = None
            if kind == 'monster':
                group, _ = self.legendary_group(record)
            definition = Definition(f'd{self._count}', kind, record, depth, tuple(provenance), size, group)
            self.definitions[key] = definition
            nested = OrderedDict()
            collect_references(scan_value(kind, record), nested, self._check)
            if group is not None:
                collect_references(scan_value('legendaryGroup', group), nested, self._check)
            queue.extend((identity, depth + 1) for identity in nested)

    def _check(self):
        if self.cancelled():
            raise PreparationStop('cancelled')
        if self.clock() >= self.deadline:
            raise PreparationStop('deadline')


class PreparationStop(Exception):
    """Preparation-wide stop (deadline/cancellation) raised outside the resolver."""
