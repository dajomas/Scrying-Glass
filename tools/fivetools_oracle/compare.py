"""Compare OrderedResolver with pinned 5e.tools oracle output (022.04f evidence tool).

Not part of CI: needs a local 5etools-src checkout at the pinned commit
(32ef600fab87a585a61dd1a22e9b02dfc58c728a) and Node 20+. No third-party data
is stored in this repository.

  node tools/fivetools_oracle/copy_oracle.mjs <5etools-src> /tmp/copies.json
  python tools/fivetools_oracle/compare.py copies <5etools-src> /tmp/copies.json

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
    result = compare_copies(sys.argv[2], sys.argv[3]) if mode == 'copies' else compare_synthetic(sys.argv[2], sys.argv[3])
    print(json.dumps(result[0]))
    for item in result[1][:50]:
        print(item)
    sys.exit(1 if result[1] else 0)
