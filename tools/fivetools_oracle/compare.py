"""Compare OrderedResolver with pinned 5e.tools oracle output (022.04f evidence tool).

Not part of CI: needs a local 5etools-src checkout at the pinned commit
(32ef600fab87a585a61dd1a22e9b02dfc58c728a) and Node 20+. No third-party data
is stored in this repository.

  node tools/fivetools_oracle/copy_oracle.mjs <5etools-src> /tmp/copies.json
  python tools/fivetools_oracle/compare.py copies <5etools-src> /tmp/copies.json

  node tools/fivetools_oracle/version_oracle.mjs <5etools-src> /tmp/versions.json
  python tools/fivetools_oracle/compare.py versions <5etools-src> /tmp/versions.json

  node tools/fivetools_oracle/item_oracle.mjs <5etools-src> /tmp/items.json
  python tools/fivetools_oracle/compare.py items <5etools-src> /tmp/items.json

  python tools/fivetools_oracle/generate_synthetic_cases.py /tmp/cases.json
  node tools/fivetools_oracle/synthetic_oracle.mjs <5etools-src> /tmp/cases.json /tmp/upstream.json
  python tools/fivetools_oracle/compare.py synthetic /tmp/cases.json /tmp/upstream.json
"""
import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from python.scrying_glass_fivetools_ordered_resolution import OrderedResolver  # noqa: E402
from python.scrying_glass_fivetools_resolution import DatasetLoader, Identity, Limits, ResolutionError  # noqa: E402


def same(a, b, path='$'):
    """First differing path; JSON numbers compare by value (1 == 1.0)."""
    numbers = (int, float)
    if type(a) in numbers and type(b) in numbers and type(a) is not bool and type(b) is not bool:
        return None if a == b else path
    if type(a) is not type(b):
        return path
    if type(a) is dict:
        if set(a) != set(b):
            return f'{path} keys {sorted(set(a) ^ set(b))[:5]}'
        return next((r for r in (same(a[k], b[k], f'{path}/{k}') for k in a) if r), None)
    if type(a) is list:
        if len(a) != len(b):
            return f'{path} length {len(a)} != {len(b)}'
        return next((r for r in (same(x, y, f'{path}/{i}') for i, (x, y) in enumerate(zip(a, b))) if r), None)
    return None if a == b else path


class Loader:
    def __init__(self, root):
        self.rows = {}
        for f in sorted(glob.glob(os.path.join(root, 'data/bestiary/bestiary-*.json'))):
            for record in json.load(open(f, encoding='utf-8')).get('monster', []):
                self.add('monster', record)
        for record in json.load(open(os.path.join(root, 'data/bestiary/template.json'), encoding='utf-8'))['monsterTemplate']:
            self.add('monsterTemplate', record)
        for record in json.load(open(os.path.join(root, 'data/bestiary/legendarygroups.json'), encoding='utf-8'))['legendaryGroup']:
            self.add('legendaryGroup', record)

    def add(self, kind, record):
        key = (kind, record['name'].lower(), record['source'].lower())
        self.rows.setdefault(key, []).append(json.dumps(record, ensure_ascii=False).encode())

    def load(self, identity):
        return tuple(self.rows.get((identity.kind, identity.name.lower(), identity.source.lower()), ()))


def compare_copies(root, oracle_path):
    oracle, loader = json.load(open(oracle_path, encoding='utf-8')), Loader(root)
    stats, failures = {'match': 0, 'mismatch': 0, 'python_error': 0, 'key_order_differs': 0}, []
    for kind in ('monsterTemplate', 'monster', 'legendaryGroup'):
        for key, expected in oracle[kind].items():
            name, source = key.rsplit('|', 1)
            try:
                got = OrderedResolver(loader, limits=Limits()).resolve(
                    Identity('5etools', kind, source, name), deadline=time.monotonic() + 30).record()
            except ResolutionError as exc:
                stats['python_error'] += 1
                failures.append((kind, key, exc.diagnostic.code))
                continue
            if 'error' in expected:
                stats['mismatch'] += 1
                failures.append((kind, key, 'upstream error, python ok'))
                continue
            diff = same(expected['ok'], got)
            stats['mismatch' if diff else 'match'] += 1
            if diff:
                failures.append((kind, key, diff))
            elif list(expected['ok']) != list(got):
                stats['key_order_differs'] += 1
    return stats, failures


def compare_versions(root, oracle_path):
    """SG-TODO-033: every upstream monster version against resolve_version."""
    from python.scrying_glass_fivetools_versions import resolve_version, version_names
    oracle, loader = json.load(open(oracle_path, encoding='utf-8')), Loader(root)
    stats, failures = {'match': 0, 'mismatch': 0, 'python_error': 0, 'missing': 0, 'key_order_differs': 0}, []
    expected_ids = set()
    for key, expected in oracle.items():
        name, source = key.rsplit('|', 1)
        base_name, base_source = expected['base'].rsplit('|', 1)
        expected_ids.add(key.lower())
        if 'error' in expected:
            stats['mismatch'] += 1
            failures.append((key, 'upstream error: ' + expected['error']))
            continue
        try:
            parent = OrderedResolver(loader, limits=Limits()).resolve(
                Identity('5etools', 'monster', base_source, base_name), deadline=time.monotonic() + 30).record()
            got, _ = resolve_version(loader, parent, name, source, limits=Limits(), deadline=time.monotonic() + 30,
                                     cancelled=lambda: False, clock=time.monotonic, dataset='5etools')
        except (ResolutionError, LookupError, ValueError) as exc:
            stats['python_error'] += 1
            failures.append((key, getattr(getattr(exc, 'diagnostic', None), 'code', None) or str(exc)))
            continue
        diff = same(expected['ok'], got)
        stats['mismatch' if diff else 'match'] += 1
        if diff:
            failures.append((key, diff))
        elif list(expected['ok']) != list(got):
            stats['key_order_differs'] += 1
    # Discovery names: every upstream version and nothing else.
    listed = set()
    for (kind, _, _), rows in loader.rows.items():
        if kind != 'monster':
            continue
        for raw in rows:
            record = json.loads(raw)
            if '_copy' in record:
                record = OrderedResolver(loader, limits=Limits()).resolve(
                    Identity('5etools', 'monster', record['source'], record['name']), deadline=time.monotonic() + 30).record()
            listed.update(f'{n}|{s}'.lower() for n, s in version_names(record))
    stats['missing'] = len(expected_ids - listed)
    stats['extra_names'] = len(listed - expected_ids)
    failures.extend(('names', k) for k in sorted(expected_ids ^ listed)[:20])
    return stats, failures


def compare_items(root, oracle_path):
    """SG-TODO-033 part 2: generated generic and specific magic-item variants, in order."""
    from python.scrying_glass_fivetools_items import generate_variants
    oracle = json.load(open(oracle_path, encoding='utf-8'))
    data = lambda name: json.load(open(os.path.join(root, 'data', name), encoding='utf-8'))
    generics, specifics = generate_variants(data('items-base.json'), data('magicvariants.json'),
                                            deadline=time.monotonic() + 120)
    stats, failures = {}, []
    for kind, got_list in (('generic', generics), ('specific', specifics)):
        expected_list = oracle[kind]
        stats[kind + '_count'] = [len(got_list), len(expected_list)]
        match = order = 0
        for index, (expected, got) in enumerate(zip(expected_list, got_list)):
            got = json.loads(json.dumps(got))
            diff = same(expected, got)
            if diff:
                failures.append((kind, index, expected.get('name'), expected.get('source'), diff))
            else:
                match += 1
                order += list(expected) != list(got)
        stats[kind + '_match'] = match
        stats[kind + '_key_order_differs'] = order
        if len(got_list) != len(expected_list):
            failures.append((kind, 'count', len(got_list), len(expected_list)))
    # items.json _copy records through the resolver (item preserve rule).
    records = data('items.json')['item']
    loader = DatasetLoader('5etools', [(Identity('5etools', 'item', r['source'], r['name']), json.dumps(r).encode())
                                       for r in records])
    stats['item_copies'] = [0, len(oracle.get('itemCopies', {}))]
    for key, expected in oracle.get('itemCopies', {}).items():
        name, source = key.rsplit('|', 1)
        got = OrderedResolver(loader, limits=Limits()).resolve(Identity('5etools', 'item', source, name),
                                                               deadline=time.monotonic() + 30).record()
        diff = same(expected, got)
        if diff:
            failures.append(('item copy', key, diff))
        else:
            stats['item_copies'][0] += 1
    # SG-TODO-034: every item enhanced, in the site's order, against the runtime.
    from python.scrying_glass_fivetools_items import ItemReference, enhance_item
    base_data = data('items-base.json')
    reference = ItemReference(base_data)
    items_data = data('items.json')
    resolved = []
    for record in items_data['item']:
        if '_copy' in record:
            record = OrderedResolver(loader, limits=Limits()).resolve(
                Identity('5etools', 'item', record['source'], record['name']), deadline=time.monotonic() + 30).record()
        resolved.append(record)
    groups = [dict(g, _isItemGroup=True) for g in items_data['itemGroup']]
    bases = [dict(b, _isBaseItem=True, _category='Basic', entries=b.get('entries') if b.get('entries') is not None else [])
             for b in base_data['baseitem']]
    every = resolved + groups + bases + [json.loads(json.dumps(g)) for g in generics] + [json.loads(json.dumps(v)) for v in specifics]
    from python.scrying_glass_fivetools_items import _entity_source
    inscope = lambda rows: None if rows is None else [r for r in rows if not (
        type(r) is dict and r.get('type') == 'wrapper' and (r.get('data') or {}).get('item__mergedEntryTag') == 'magicvariant')]
    # The site builds _fullEntries for item groups and generic variants only to add their item
    # lists (out of scope, filtered above); filtered, that equals their own entries. The port
    # leaves _fullEntries out there, and a reader falls back to entries, so absent counts as
    # the record's own entries on both sides.
    got_map = {}
    for item in every:
        own = json.loads(json.dumps(item.get('entries') or []))
        enhance_item(item, reference)
        full = inscope(item.get('_fullEntries'))
        got_map.setdefault(f"{item['name']}|{_entity_source(item)}", []).append(
            {'fullEntries': own if full is None else full, 'fullAdditionalEntries': inscope(item.get('_fullAdditionalEntries')),
             '_own': own})
    expected_map = oracle.get('enhanced', {})
    match = 0
    for key, expected in expected_map.items():
        got = json.loads(json.dumps(got_map.get(key)))
        if got is not None and len(got) == len(expected):
            expected = [dict(e, fullEntries=g['_own'] if e['fullEntries'] is None else e['fullEntries'])
                        for e, g in zip(expected, got)]
        for g in got or []:
            g.pop('_own', None)
        diff = same(expected, got)
        if diff:
            failures.append(('enhanced', key, diff))
        else:
            match += 1
    stats['enhanced'] = [match, len(expected_map), len(got_map)]
    return stats, failures


def compare_synthetic(cases_path, upstream_path):
    cases, upstream = json.load(open(cases_path)), json.load(open(upstream_path))
    stats, notes = {}, []
    for index, (case, expected) in enumerate(zip(cases, upstream)):
        copy_id = Identity('d', 'monster', 'SRC', case['copy']['name'])
        loader = DatasetLoader('d', [(copy_id, json.dumps(case['copy']).encode()),
                                     (Identity('d', 'monster', 'SRC', 'Base'), json.dumps(case['base']).encode())])
        try:
            got, error = OrderedResolver(loader).resolve(copy_id, deadline=time.monotonic() + 30).record(), None
        except ResolutionError as exc:
            got, error = None, exc.diagnostic.code
        if 'error' in expected:
            kind = 'both_error' if error else 'UPSTREAM_ERROR_PYTHON_OK'
        elif expected['dirty']:
            kind = 'upstream_nonjson_python_error' if error else 'UPSTREAM_NONJSON_PYTHON_OK'
        elif error:
            kind = 'python_error_only'
        else:
            got.pop('_isCopy', None)
            expected['ok'].pop('_isCopy', None)
            kind = 'MISMATCH' if same(expected['ok'], got) else 'match'
        stats[kind] = stats.get(kind, 0) + 1
        if kind.isupper() or kind == 'python_error_only':
            notes.append((index, kind, error, json.dumps(case['copy']['_copy']['_mod'])[:200]))
    return stats, notes


if __name__ == '__main__':
    mode = sys.argv[1]
    result = (compare_copies(sys.argv[2], sys.argv[3]) if mode == 'copies' else
              compare_versions(sys.argv[2], sys.argv[3]) if mode == 'versions' else
              compare_items(sys.argv[2], sys.argv[3]) if mode == 'items' else compare_synthetic(sys.argv[2], sys.argv[3]))
    print(json.dumps(result[0]))
    for item in result[1][:50]:
        print(item)
    sys.exit(1 if result[1] else 0)
