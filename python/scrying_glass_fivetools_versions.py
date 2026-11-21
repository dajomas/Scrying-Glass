"""5e.tools monster versions (SG-TODO-033), pinned to RUNTIME_COMMIT (js/utils.js).

Mirrors ``DataUtil.monster.getVersions``: the ``_versions`` of a resolved monster, plus
the versions its ``variant`` entries declare with ``_version`` (addAs / addHeadersAs),
with ``_abstract``/``_implementations`` templates expanded and ``{{variable}}``
substituted. Each version is applied by ``copyApplier.getCopy`` to a copy of the parent
that lacks ``_versions`` and the token/fluff flags and whose source lists drop the
version's own source; the result carries the runtime's ``_versionBase_*`` fields.

The copy itself runs through the same OrderedResolver as ``_copy`` inheritance, over a
two-record loader (the prepared parent and the synthetic version) that delegates
templates to the real dataset. No network, no JavaScript execution.
"""
from __future__ import annotations

import copy
import json
import re

from .scrying_glass_fivetools_jsvalues import to_display_string
from .scrying_glass_fivetools_ordered_resolution import OrderedResolver
from .scrying_glass_fivetools_resolution import Identity, ResolutionError, entity_key

PARENT_STRIP = ('_versions', 'hasToken', 'hasFluff', 'hasFluffImages')
SOURCE_LISTS = ('additionalSources', 'otherSources', 'referenceSources')
VARIABLE = re.compile(r'{{([^}]+)}}')


class VersionError(ValueError):
    """A malformed version definition; the code is a stable identifier."""


def _fail(_code, *_args, **_kwargs):
    raise VersionError('malformed_version')


def _js_string(value):
    """String(value) as the runtime's replace callback returns it."""
    if value is None:
        return 'null'
    if type(value) in (dict, list):
        raise VersionError('malformed_version')  # [object Object] / joined arrays: not in data
    return to_display_string(value, _fail)


def _walk_strings(value, replace):
    if type(value) is str:
        return replace(value)
    if type(value) is list:
        return [_walk_strings(v, replace) for v in value]
    if type(value) is dict:
        return {k: _walk_strings(v, replace) for k, v in value.items()}
    return value


def _expand_copy(ent):
    """_getVersions_mutExpandCopy: _mod/_templates/_preserve become the copy metadata.

    As in the runtime, ``_templates`` also stays on the version itself.
    """
    meta = {'_preserve': ent.get('_preserve') or {'*': True}}
    for key in ('_mod', '_templates'):
        if ent.get(key) is not None:
            meta[key] = ent[key]
    ent['_copy'] = meta
    ent.pop('_mod', None)
    ent.pop('_preserve', None)


def _variant_versions(parent):
    """DataUtil.monster._getAdditionalVersionsData."""
    out = []
    for item in parent.get('variant') or []:
        if type(item) is not dict or not item.get('_version'):
            continue
        meta = item['_version']
        if type(meta) is not dict:
            raise VersionError('malformed_version')
        add = {'name': meta.get('name') or item.get('name'),
               'source': meta.get('source') or item.get('source') or parent.get('source'), 'variant': None}
        if meta.get('addAs'):
            entry = copy.deepcopy(item)
            for key in ('_version', 'type', 'source', 'page'):
                entry.pop(key, None)
            add['_mod'] = {meta['addAs']: {'mode': 'appendArr', 'items': entry}}
        elif meta.get('addHeadersAs'):
            entry = copy.deepcopy(item)
            if type(entry.get('entries')) is not list:
                raise VersionError('malformed_version')
            entry['entries'] = [e for e in entry['entries'] if type(e) is dict and e.get('name') and e.get('entries')]
            for e in entry['entries']:
                e.pop('type', None)
                e.pop('source', None)
            add['_mod'] = {meta['addHeadersAs']: {'mode': 'appendArr', 'items': entry['entries']}}
        else:
            continue  # the runtime's .filter(Boolean) drops it
        out.append(add)
    return out


def version_specs(parent):
    """Version objects in runtime order, before the copy is applied (each has ``_copy``)."""
    versions = parent.get('_versions')
    if versions is not None and type(versions) is not list:
        raise VersionError('malformed_version')
    out = []
    for ver in list(versions or []) + _variant_versions(parent):
        if type(ver) is not dict:
            raise VersionError('malformed_version')
        implementations = ver.get('_implementations')
        if ver.get('_abstract') and type(implementations) is list and implementations:
            for impl in implementations:
                if type(ver['_abstract']) is not dict or type(impl) is not dict:
                    raise VersionError('malformed_version')
                template, impl = copy.deepcopy(ver['_abstract']), copy.deepcopy(impl)
                _expand_copy(template)
                variables = impl.pop('_variables', None)
                if variables:
                    if type(variables) is not dict:
                        raise VersionError('malformed_version')
                    template = _walk_strings(template, lambda s: VARIABLE.sub(
                        lambda m: _js_string(variables[m.group(1)]) if m.group(1) in variables else 'undefined', s))
                template.update(impl)
                out.append(template)
        else:
            ver = copy.deepcopy(ver)
            _expand_copy(ver)
            out.append(ver)
    for ver in out:
        if type(ver.get('name')) is not str or type(ver.get('source')) is not str:
            raise VersionError('malformed_version')  # the runtime would copy the parent's identity
    return out


def version_names(parent):
    """[(name, source)] of every version, cheap enough for discovery."""
    return [(v['name'], v['source']) for v in version_specs(parent)]


def _stripped_parent(parent, version_source):
    out = copy.deepcopy(parent)
    for key in PARENT_STRIP:
        out.pop(key, None)
    for prop in SOURCE_LISTS:
        if type(out.get(prop)) is list and out[prop]:
            out[prop] = [m for m in out[prop] if not (type(m) is dict and m.get('source') == version_source)]
        if not out.get(prop):
            out.pop(prop, None)
    return out


def _hash(record):
    """UrlUtil.URL_TO_HASH_GENERIC: each part encodeURIComponent(lower).toLowerCase(), joined by '_'."""
    from urllib.parse import quote
    return '_'.join(quote(part.lower(), safe="-_.!~*'()").lower() for part in (record['name'], record['source']))


class _VersionLoader:
    def __init__(self, data, records):
        self.data, self.records = data, records

    def load(self, identity):
        hit = self.records.get(entity_key(identity))
        return (hit,) if hit is not None else self.data.load(identity)


def resolve_version(data, parent, name, source, *, limits, deadline, cancelled, clock, dataset):
    """Return (version record, provenance) for the version (name, source) of a resolved parent.

    ``parent`` is the resolved base monster (no ``_copy``). Raises LookupError
    ('selected_unavailable') when the parent has no such version.
    """
    wanted = (name.lower(), source.lower())
    specs = [v for v in version_specs(parent) if (v['name'].lower(), v['source'].lower()) == wanted]
    if not specs:
        raise LookupError('selected_unavailable')
    spec = specs[0]
    stripped = _stripped_parent(parent, spec['source'])
    spec['_copy'].update(name=parent['name'], source=parent['source'])
    parent_id = Identity(dataset, 'monster', parent['source'], parent['name'])
    version_id = Identity(dataset, 'monster', spec['source'], spec['name'])
    if entity_key(parent_id) == entity_key(version_id):
        raise VersionError('malformed_version')
    encode = lambda obj: json.dumps(obj, ensure_ascii=False, separators=(',', ':')).encode()
    loader = _VersionLoader(data, {entity_key(parent_id): encode(stripped), entity_key(version_id): encode(spec)})
    resolver = OrderedResolver(loader, limits=limits, clock=clock)
    result = resolver.resolve(version_id, deadline=deadline, cancelled=cancelled)
    record = result.record()
    record.update({'_versionBase_isVersion': True, '_versionBase_name': parent['name'],
                   '_versionBase_source': parent['source'], '_versionBase_hash': _hash(parent)})
    for flag in ('hasToken', 'hasFluff', 'hasFluffImages'):
        if flag in parent:
            record['_versionBase_' + flag[0].lower() + flag[1:]] = parent[flag]
    return record, result.provenance


__all__ = ['VersionError', 'ResolutionError', 'resolve_version', 'version_names', 'version_specs']
