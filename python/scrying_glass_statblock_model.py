"""Version-one statblock validation; no persistence, network or rendering side effects."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass, fields
from datetime import datetime
from urllib.parse import urlsplit


class StatblockError(ValueError):
    """A stable validation code and a path, without embedding imported content."""
    def __init__(self, code, path):
        self.code, self.path = code, path
        super().__init__(f"{code}: {path}")


@dataclass(frozen=True)
class ModelLimits:
    snapshot_bytes: int = 2 * 1024 * 1024
    content_nodes: int = 16384
    content_depth: int = 16
    text_value_bytes: int = 64 * 1024
    supporting_definitions: int = 256

    def __post_init__(self):
        for field in fields(self):
            value = getattr(self, field.name)
            if type(value) is not int or not 0 < value <= 2**63 - 1:
                raise StatblockError('invalid_limit', field.name)

    @classmethod
    def from_mapping(cls, values):
        if type(values) is not dict or set(values) - {f.name for f in fields(cls)}:
            raise StatblockError('invalid_limits', 'limits')
        return cls(**values)


BLOCK = {'section', 'entry', 'paragraph', 'list', 'table'}
INLINE = {'text', 'emphasis', 'strong', 'line_break', 'link', 'species_placeholder', 'reference'}
CHILDREN = {
    'section': BLOCK, 'entry': BLOCK, 'list_item': BLOCK | INLINE,
    'cell': BLOCK | INLINE, 'paragraph': INLINE, 'emphasis': INLINE,
    'strong': INLINE, 'link': INLINE - {'link', 'reference'},
    'list': {'list_item'}, 'table': {'row'}, 'row': {'cell'},
}
KINDS = BLOCK | INLINE | {'list_item', 'row', 'cell'}
NODE_OPTIONAL = {'text', 'url', 'target_definition_local_id', 'source_path', 'label', 'enabled', 'ordered'}
PROVENANCE_OPTIONAL = {'endpoint', 'api_version', 'source_code', 'edition', 'source_url', 'file_name', 'file_sha256'}
HEX = re.compile(r'[0-9a-f]{64}\Z')
SQL_INT = (-2**63, 2**63 - 1)


def _fail(code, path):
    raise StatblockError(code, path)


def _object(value, required, optional, path):
    if type(value) is not dict or set(value) - required - optional or required - set(value):
        _fail('invalid_fields', path)


def _text(value, path, limits, *, nonempty=False, nullable=False):
    if value is None and nullable:
        return
    if type(value) is not str or (nonempty and not value.strip()):
        _fail('invalid_text', path)
    try:
        size = len(value.encode('utf-8'))
    except UnicodeError:
        _fail('invalid_unicode', path)
    if '\x00' in value:
        _fail('invalid_text', path)
    if size > limits.text_value_bytes:
        _fail('text_limit', path)


def _integer(value, path, minimum=0):
    if type(value) is not int or not max(minimum, SQL_INT[0]) <= value <= SQL_INT[1]:
        _fail('invalid_integer', path)


def _url(value, path, limits):
    if value is None:
        return
    _text(value, path, limits, nonempty=True)
    try:
        p = urlsplit(value)
        if p.scheme != 'https' or not p.hostname or p.username is not None or p.password is not None:
            _fail('unsafe_url', path)
        if p.port == 0 or any(c.isspace() or ord(c) < 32 for c in value) or '\\' in value:
            _fail('unsafe_url', path)
    except ValueError:
        _fail('unsafe_url', path)


def _preflight(value, limits):
    # Bound traversal before copying/serializing; reject Python-object cycles.
    active, budget = set(), 0
    stack = [('value', value, '$')]
    while stack:
        action, obj, path = stack.pop()
        if action == 'exit':
            active.remove(id(obj))
            continue
        if action == 'iterator':
            try:
                key, child = next(obj)
            except StopIteration:
                continue
            stack.append(('iterator', obj, path))
            if type(key) is str:
                _text(key, path, limits)
                budget += len(key.encode('utf-8')) + 3
            stack.append(('value', child, path + '/' + str(key)))
            continue
        budget += 1
        if type(obj) in (dict, list):
            if id(obj) in active:
                _fail('object_cycle', path)
            active.add(id(obj))
            stack.append(('exit', obj, path))
            if type(obj) is dict:
                if any(type(k) is not str for k in obj):
                    _fail('invalid_key', path)
                iterator = iter(obj.items())
            else:
                iterator = enumerate(obj)
            stack.append(('iterator', iterator, path))
        elif type(obj) is str:
            _text(obj, path, limits)
            budget += len(obj.encode('utf-8'))
        elif obj is not None and type(obj) not in (int, bool):
            _fail('invalid_scalar', path)
        if budget > limits.snapshot_bytes:
            _fail('snapshot_limit', '$')


def _positions(rows, path, owner=lambda row: None):
    seen = set()
    for row in rows:
        key = (owner(row), row['position'])
        _integer(row['position'], path + '/position')
        if key in seen:
            _fail('duplicate_position', path)
        seen.add(key)


def _record_rows(snapshot, limits):
    defs = {}
    identities = set()
    for i, row in enumerate(snapshot['definitions']):
        path = f'$/definitions/{i}'
        _object(row, {'local_id', 'kind', 'name', 'source_key', 'position'}, {'source_code'}, path)
        for key in ('local_id', 'kind', 'name', 'source_key'):
            _text(row[key], path + '/' + key, limits, nonempty=True)
        if 'source_code' in row:
            _text(row['source_code'], path + '/source_code', limits, nullable=True)
        ident = (row['kind'], row['source_key'])
        if row['local_id'] in defs or ident in identities:
            _fail('duplicate_definition', path)
        defs[row['local_id']] = row
        identities.add(ident)
    if len(defs) > limits.supporting_definitions:
        _fail('definition_limit', '$/definitions')
    _positions(snapshot['definitions'], '$/definitions')
    for group, required, optional in (
        ('facts', {'position', 'key', 'label', 'display_text'}, {'definition_id', 'integer_value'}),
        ('warnings', {'position', 'code', 'message'}, {'definition_id', 'source_path'}),
        ('provenance', {'position', 'role', 'provider', 'entity_id', 'adapter_version', 'credits'}, {'definition_id'} | PROVENANCE_OPTIONAL),
    ):
        for i, row in enumerate(snapshot[group]):
            path = f'$/{group}/{i}'
            _object(row, required, optional, path)
            owner = row.get('definition_id')
            if owner is not None and (type(owner) is not str or owner not in defs):
                _fail('unknown_definition', path)
            for key, value in row.items():
                if key in {'position', 'definition_id', 'credits'}:
                    continue
                if key == 'integer_value':
                    if value is not None:
                        _integer(value, path + '/' + key, SQL_INT[0])
                elif key in {'source_url', 'endpoint'}:
                    _url(value, path + '/' + key, limits)
                else:
                    _text(value, path + '/' + key, limits, nullable=key in optional,
                          nonempty=key in {'key', 'code', 'provider', 'entity_id', 'adapter_version'})
            if group == 'facts' and owner is None and row['key'].casefold() in {
                'name', 'species', 'monster_species', 'ac', 'armor_class', 'hp',
                'current_hp', 'hit_points', 'max_hp', 'initiative_bonus',
            }:
                _fail('sg_owned_fact', path)
            if group == 'provenance':
                if row['role'] not in {'selected', 'base', 'template', 'reference'}:
                    _fail('invalid_role', path)
                if row.get('file_sha256') is not None and not HEX.fullmatch(row['file_sha256']):
                    _fail('invalid_digest', path)
                if type(row['credits']) is not list:
                    _fail('invalid_credits', path)
                for j, credit in enumerate(row['credits']):
                    cp = path + f'/credits/{j}'
                    _object(credit, {'position', 'attribution'}, {'publisher', 'license_name', 'license_url'}, cp)
                    for key, value in credit.items():
                        if key == 'position':
                            continue
                        if key == 'license_url':
                            _url(value, cp + '/' + key, limits)
                        else:
                            _text(value, cp + '/' + key, limits, nullable=key != 'attribution')
                    _positions(row['credits'], path + '/credits')
        _positions(snapshot[group], '$/' + group, lambda row: row.get('definition_id'))
    if snapshot['completeness'] == 'partial' and not snapshot['warnings']:
        _fail('partial_without_warning', '$/warnings')
    selected = [p for p in snapshot['provenance'] if p['role'] == 'selected']
    if len(selected) != 1 or selected[0].get('definition_id') is not None:
        _fail('invalid_selected_provenance', '$/provenance')
    return defs


def _nodes(snapshot, definitions, limits):
    rows = snapshot['nodes']
    if len(rows) > limits.content_nodes:
        _fail('node_limit', '$/nodes')
    nodes = {}
    for i, row in enumerate(rows):
        path = f'$/nodes/{i}'
        _object(row, {'local_id', 'parent_local_id', 'definition_id', 'position', 'kind'}, NODE_OPTIONAL, path)
        _text(row['local_id'], path + '/local_id', limits, nonempty=True)
        if row['local_id'] in nodes:
            _fail('duplicate_node', path)
        if type(row['kind']) is not str or row['kind'] not in KINDS:
            _fail('invalid_node_kind', path)
        if row['definition_id'] is not None and (type(row['definition_id']) is not str or row['definition_id'] not in definitions):
            _fail('unknown_definition', path)
        if row['parent_local_id'] is not None:
            _text(row['parent_local_id'], path + '/parent_local_id', limits, nonempty=True)
        for key in ('enabled', 'ordered'):
            if key in row and row[key] is not None and type(row[key]) is not bool:
                _fail('invalid_boolean', path + '/' + key)
        for key in ('text', 'label', 'source_path'):
            if key in row:
                _text(row[key], path + '/' + key, limits, nullable=True)
        target = row.get('target_definition_local_id')
        if target is not None and (type(target) is not str or target not in definitions):
            _fail('unknown_reference', path)
        if row['kind'] == 'reference' and target is None:
            _fail('missing_reference_target', path)
        if row['kind'] != 'reference' and target is not None:
            _fail('unexpected_reference_target', path)
        _url(row.get('url'), path + '/url', limits)
        if row['kind'] == 'link' and not row.get('url'):
            _fail('missing_link_url', path)
        if row['kind'] != 'link' and row.get('url') is not None:
            _fail('unexpected_url', path)
        if row['kind'] == 'text' and type(row.get('text')) is not str:
            _fail('missing_text', path)
        if row['kind'] in {'species_placeholder', 'line_break', 'reference'} and row.get('text') is not None:
            _fail('unexpected_text', path)
        nodes[row['local_id']] = row
    _positions(rows, '$/nodes', lambda row: (row['definition_id'], row['parent_local_id']))
    depths = {}
    for ident in nodes:
        chain, seen, cursor = [], set(), ident
        while cursor is not None and cursor not in depths:
            if cursor in seen:
                _fail('content_cycle', '$/nodes/' + ident)
            seen.add(cursor)
            node = nodes.get(cursor)
            if node is None:
                _fail('unknown_parent', '$/nodes/' + ident)
            chain.append(cursor)
            cursor = node['parent_local_id']
        depth = depths.get(cursor, 0)
        for key in reversed(chain):
            depth += 1
            if depth > limits.content_depth:
                _fail('depth_limit', '$/nodes/' + key)
            depths[key] = depth
    for ident, row in nodes.items():
        parent = nodes.get(row['parent_local_id'])
        if parent is None:
            if row['kind'] not in BLOCK:
                _fail('invalid_root', '$/nodes/' + ident)
        elif parent['definition_id'] != row['definition_id']:
            _fail('cross_owner_parent', '$/nodes/' + ident)
        elif row['kind'] not in CHILDREN.get(parent['kind'], set()):
            _fail('invalid_child', '$/nodes/' + ident)
    # Count a paragraph/inline run before style splitting, not just each leaf.
    totals = {}
    for ident in sorted(nodes, key=depths.get, reverse=True):
        row = nodes[ident]
        amount = totals.get(ident, 0) + len((row.get('text') or '').encode('utf-8'))
        if row['kind'] in INLINE | {'paragraph'} and amount > limits.text_value_bytes:
            _fail('text_limit', '$/nodes/' + ident)
        if row['parent_local_id'] is not None and row['kind'] in INLINE:
            parent = row['parent_local_id']
            totals[parent] = totals.get(parent, 0) + amount


def _dump(value):
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (TypeError, ValueError, UnicodeError, RecursionError):
        _fail('invalid_json', '$')


def _canonical(snapshot, *, digest=False):
    result = copy.deepcopy(snapshot)
    defs = sorted(result['definitions'], key=lambda row: row['position'])
    dm = {row['local_id']: f'd{i}' for i, row in enumerate(defs)}
    children = {}
    for row in result['nodes']:
        children.setdefault((row['definition_id'], row['parent_local_id']), []).append(row)
    ordered = []
    for owner in [None] + [row['local_id'] for row in defs]:
        stack = list(reversed(sorted(children.get((owner, None), []), key=lambda row: row['position'])))
        while stack:
            row = stack.pop()
            ordered.append(row)
            stack.extend(reversed(sorted(children.get((owner, row['local_id']), []), key=lambda row: row['position'])))
    nm = {row['local_id']: f'n{i}' for i, row in enumerate(ordered)}
    for row in defs:
        row['local_id'] = dm[row['local_id']]
    result['definitions'], result['nodes'] = defs, ordered
    for group in ('nodes', 'facts', 'provenance', 'warnings'):
        for row in result[group]:
            if row.get('definition_id') is not None:
                row['definition_id'] = dm[row['definition_id']]
            if group == 'nodes':
                row['local_id'] = nm[row['local_id']]
                if row['parent_local_id'] is not None:
                    row['parent_local_id'] = nm[row['parent_local_id']]
                if row.get('target_definition_local_id') is not None:
                    row['target_definition_local_id'] = dm[row['target_definition_local_id']]
            if group == 'provenance':
                row['credits'].sort(key=lambda credit: credit['position'])
        if group != 'nodes':
            result[group].sort(key=lambda row: (row.get('definition_id') or '', row['position']))
    if digest:
        for key in ('revision', 'prepared_at', 'content_digest'):
            result.pop(key, None)
    return result


def validate_snapshot(snapshot, limits=None):
    """Return an independent validated snapshot; supplied digests must be correct."""
    limits = ModelLimits() if limits is None else limits
    if not isinstance(limits, ModelLimits):
        _fail('invalid_limits', 'limits')
    _preflight(snapshot, limits)
    _object(snapshot, {'model_version', 'source_label', 'subtitle', 'completeness', 'provenance', 'facts', 'definitions', 'nodes', 'warnings'},
            {'revision', 'prepared_at', 'content_digest'}, '$')
    if type(snapshot['model_version']) is not int or snapshot['model_version'] != 1:
        _fail('unsupported_version', '$/model_version')
    _text(snapshot['source_label'], '$/source_label', limits, nonempty=True)
    _text(snapshot['subtitle'], '$/subtitle', limits)
    if type(snapshot['completeness']) is not str or snapshot['completeness'] not in {'available', 'partial'}:
        _fail('invalid_completeness', '$/completeness')
    for key in ('provenance', 'facts', 'definitions', 'nodes', 'warnings'):
        if type(snapshot[key]) is not list:
            _fail('invalid_array', '$/' + key)
    if 'revision' in snapshot:
        _integer(snapshot['revision'], '$/revision', 1)
    if 'prepared_at' in snapshot:
        value = snapshot['prepared_at']
        try:
            if type(value) is not str or not re.fullmatch(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z', value):
                raise ValueError()
            datetime.fromisoformat(value[:-1] + '+00:00')
        except ValueError:
            _fail('invalid_timestamp', '$/prepared_at')
    definitions = _record_rows(snapshot, limits)
    _nodes(snapshot, definitions, limits)
    actual = hashlib.sha256(_dump(_canonical(snapshot, digest=True))).hexdigest()
    if 'content_digest' in snapshot:
        if type(snapshot['content_digest']) is not str or not HEX.fullmatch(snapshot['content_digest']) or snapshot['content_digest'] != actual:
            _fail('digest_mismatch', '$/content_digest')
    if len(_dump(snapshot)) > limits.snapshot_bytes:
        _fail('snapshot_limit', '$')
    return copy.deepcopy(snapshot)


def canonical_bytes(snapshot, limits=None):
    """Validate then encode deterministic local IDs/order, including metadata."""
    return _dump(_canonical(validate_snapshot(snapshot, limits)))


def content_digest(snapshot, limits=None):
    """SHA-256 excluding revision/time/digest; live SG fields are not model fields."""
    return hashlib.sha256(_dump(_canonical(validate_snapshot(snapshot, limits), digest=True))).hexdigest()
