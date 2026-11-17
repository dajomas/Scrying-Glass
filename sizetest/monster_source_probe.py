#!/usr/bin/env python3
"""Collect raw statblock evidence for one or more monster species.

Generalisation of sizetest/vampire_statblock_probe.py for SG-TODO-022 Stage B
(022.05 Open5e, 022.06 D&D Beyond). Python 3.10+, standard library only.

Usage:
  python sizetest/monster_source_probe.py "Lich" "Adult Red Dragon"
  python sizetest/monster_source_probe.py --species-file names.txt --out monsters_examples
  python sizetest/monster_source_probe.py --random 20

For each species it writes <out>/<slug>/ with raw responses (raw/), extracted
exact-name records, manifest.json and report.md. It never logs in, sends no
cookies, does not bypass access gates and does not substitute other names.
5e.tools records are optional (--include-fivetools): only the exact matching
records are saved, never whole datasets. Requests are sequential with a delay.
"""
import argparse
import hashlib
import json
import random
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote, urlencode, urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

# A mix of 2014/2024, SRD (public on D&D Beyond) and non-SRD (likely gated),
# spellcasters, legendary/lair/mythic, swarms, shapechangers and reactions.
SUGGESTED = [
    'Lich', 'Adult Red Dragon', 'Ancient Brass Dragon', 'Aboleth', 'Mummy Lord', 'Kraken', 'Tarrasque',
    'Beholder', 'Mind Flayer', 'Death Knight', 'Drow Mage', 'Flameskull', 'Archmage', 'Bandit Captain',
    'Goblin', 'Swarm of Bats', 'Werewolf', 'Gelatinous Cube', 'Hydra', 'Rakshasa', 'Unicorn',
    "Will-o'-Wisp", 'Couatl', 'Planetar', 'Animated Armor', 'Shambling Mound', 'Vampire Spawn', 'Wolf',
]
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
STATBLOCK_CLASSES = {'mon-stat-block', 'mon-stat-block-2024', 'stat-block'}


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def norm(value):
    return re.sub(r'[^a-z0-9]+', ' ', str(value).casefold()).strip()


def slug(value):
    return re.sub(r'[^a-z0-9]+', '-', value.casefold()).strip('-') or 'monster'


class Redirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        old, new = urlsplit(req.full_url), urlsplit(newurl)
        count = getattr(req, '_redirects', 0) + 1
        allowed = {old.hostname}
        if old.hostname in {'www.dndbeyond.com', 'dndbeyond.com'}:
            allowed |= {'www.dndbeyond.com', 'dndbeyond.com', 'marketplace.dndbeyond.com'}
        if new.scheme != 'https' or new.hostname not in allowed or new.username or new.password or count > 3:
            raise ValueError('Unapproved redirect to ' + newurl)
        result = super().redirect_request(req, fp, code, msg, headers, newurl)
        if result is not None:
            result._redirects = count
        return result


class Page(HTMLParser):
    """Anchors plus the text segments of recognised statblock roots."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.anchors, self.anchor, self.blocks, self.active = [], [], None, [], None

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        classes = (data.get('class') or '').split()
        if tag == 'a':
            self.anchor = {'href': data.get('href') or '', 'parts': [], 'legacy': 'legacy' in str(attrs).casefold()}
        if self.active is None and STATBLOCK_CLASSES & set(classes):
            self.active = {'level': len(self.stack), 'root_class': data.get('class'), 'segments': [], 'tags': 0, 'max_dom_depth': 0}
        if self.active is not None:
            self.active['tags'] += 1
            self.active['max_dom_depth'] = max(self.active['max_dom_depth'], len(self.stack) - self.active['level'] + 1)
        if tag not in VOID:
            self.stack.append((tag, data.get('class') or ''))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'a' and self.anchor is not None:
            self.anchor['text'] = ' '.join(self.anchor.pop('parts'))
            self.anchors.append(self.anchor)
            self.anchor = None
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break
        if self.active is not None and len(self.stack) <= self.active['level']:
            self.blocks.append(self.active)
            self.active = None

    def handle_data(self, text):
        if self.anchor is not None:
            self.anchor['parts'].append(text)
        text = text.strip()
        if self.active is not None and text and not any(t in {'script', 'style'} for t, _ in self.stack):
            tag, cls = self.stack[-1] if self.stack else ('', '')
            self.active['segments'].append({'element': tag, 'class': cls, 'text': text})


class Probe:
    def __init__(self, root, species, args, cfg):
        self.root, self.species, self.args, self.cfg = root, species, args, cfg
        self.requests, self.records, self.issues = [], [], []
        self.opener = build_opener(Redirects())
        self.last = 0.0

    def fetch(self, url, label, html=False):
        parts = urlsplit(url)
        if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password:
            raise ValueError('HTTPS URL without credentials required')
        wait = self.args.delay - (time.monotonic() - self.last)
        if wait > 0:
            time.sleep(wait)
        request = Request(url, headers={'User-Agent': 'Mozilla/5.0 compatible; ScryingGlass/1.0 (statblock research probe)',
                                        'Accept': 'text/html,application/xhtml+xml' if html else 'application/json',
                                        'Accept-Encoding': 'identity'})
        index = len(self.requests) + 1
        started = time.monotonic()
        meta = {'url': url, 'label': label, 'started_utc': datetime.now(timezone.utc).isoformat()}
        try:
            try:
                response = self.opener.open(request, timeout=self.args.timeout)
            except HTTPError as exc:
                response = exc
            with response:
                cap = self.args.max_response_mib * 1024 ** 2
                raw = response.read(cap + 1)
                meta.update(status=response.code, final_url=response.geturl(),
                            content_type=response.headers.get('Content-Type'),
                            content_encoding=response.headers.get('Content-Encoding'),
                            bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(), truncated=len(raw) > cap)
            name = f"raw/{index:03d}-{label}.{'html' if html else 'json'}"
            (self.root / name).write_bytes(raw)
            meta['file'] = name
            if meta['truncated']:
                raise ValueError('Response ceiling exceeded; saved response is truncated')
            if meta['status'] != 200:
                raise ValueError(f"HTTP {meta['status']}; saved response kept for inspection")
            if meta.get('content_encoding') not in (None, 'identity'):
                raise ValueError('Unexpected content encoding')
            return raw.decode('utf-8', 'replace') if html else json.loads(raw)
        except Exception as exc:
            meta['error'] = str(exc)
            raise
        finally:
            self.last = time.monotonic()
            meta['elapsed_seconds'] = round(self.last - started, 3)
            self.requests.append(meta)

    def issue(self, provider, message):
        self.issues.append({'provider': provider, 'error': str(message)})

    def add(self, provider, identity, value, note=''):
        path = f'{len(self.records) + 1:03d}-{provider}.json'
        data = compact(value)
        (self.root / path).write_bytes(data)
        self.records.append({'provider': provider, 'identity': identity, 'file': path, 'bytes': len(data), 'note': note})

    def open5e(self):
        base = str(self.cfg.get('open5e_base_url', 'https://api.open5e.com/v2')).rstrip('/')
        target = norm(self.species)
        url = base + '/creatures/?' + urlencode({'name__iexact': self.species, 'limit': 100, 'format': 'json'})
        seen, keys = set(), set()
        for page in range(10):
            if url in seen or urlsplit(url).hostname != urlsplit(base).hostname:
                raise ValueError('Pagination loop or host change')
            seen.add(url)
            listing = self.fetch(url, f'open5e-list-{page}')
            if not isinstance(listing, dict) or not isinstance(listing.get('results'), list):
                raise ValueError('Invalid list shape')
            for item in listing['results']:
                key = item.get('key')
                if norm(item.get('name')) != target or not isinstance(key, str) or key in keys:
                    continue
                if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,199}', key):
                    self.issue('open5e', f'Invalid creature key {key!r}')
                    continue
                keys.add(key)
                try:
                    detail = self.fetch(f"{base}/creatures/{quote(key, safe='')}/?format=json", f'open5e-detail-{len(keys)}')
                    if detail.get('key') != key:
                        raise ValueError('Detail identity mismatch')
                    self.add('open5e', {'key': key, 'document': detail.get('document')}, detail, 'Open5e v2 creature detail')
                except Exception as exc:
                    self.issue('open5e', exc)
            if not listing.get('next'):
                break
            url = urljoin(url, listing['next'])
        else:
            self.issue('open5e', 'More than ten pages; discovery incomplete')
        if not keys:
            self.issue('open5e', 'No exact-name records discovered')

    def fivetools(self):
        base = str(self.cfg.get('fivetools_data_base_url', 'https://5e.tools/data/bestiary')).rstrip('/')
        sources = self.cfg.get('fivetools_sources', ['MM', 'XMM', 'PHB', 'XPHB', 'DMG', 'XDMG'])
        index = self.fetch(base + '/index.json', 'fivetools-index')
        matches = 0
        for source in dict.fromkeys(sources):
            filename = index.get(source)
            if not isinstance(filename, str) or not re.fullmatch(r'[A-Za-z0-9_.-]+\.json', filename):
                continue
            data = self.fetch(f'{base}/{filename}', f'fivetools-{slug(source)}')
            raw = self.root / self.requests[-1]['file']
            raw.unlink()  # never keep whole third-party datasets; the hash stays in the manifest
            self.requests[-1]['file'] = None
            for position, item in enumerate(data.get('monster', [])):
                if isinstance(item, dict) and norm(item.get('name')) == norm(self.species):
                    matches += 1
                    self.add('fivetools', {'source': item.get('source'), 'name': item.get('name'), 'file': filename, 'index': position},
                             item, 'UNRESOLVED _copy record' if '_copy' in item else 'Raw 5e.tools record')
        if not matches:
            self.issue('fivetools', 'No exact-name records in configured sources')

    def dndbeyond(self):
        text = self.fetch('https://www.dndbeyond.com/monsters?' + urlencode({'filter-search': self.species}), 'dndbeyond-search', True)
        page = Page()
        page.feed(text)
        hrefs = list(dict.fromkeys(a['href'] for a in page.anchors
                                   if norm(a['text']) == norm(self.species) and re.fullmatch(r'/monsters/[^?#]+', a['href'])))
        if not hrefs:
            self.issue('dndbeyond', 'No exact-name links: search may be blocked or markup changed; not proof of absence')
        for number, href in enumerate(hrefs[:self.args.max_dndbeyond]):
            try:
                html = self.fetch('https://www.dndbeyond.com' + href, f'dndbeyond-detail-{number}', True)
                detail = Page()
                detail.feed(html)
                if not detail.blocks:
                    raise ValueError(f'{href}: no statblock root (access gate, changed markup or absent content); raw page saved')
                for block_number, block in enumerate(detail.blocks):
                    self.add('dndbeyond', {'href': href, 'block': block_number}, block, 'DOM text segments, not a normalized statblock')
            except Exception as exc:
                self.issue('dndbeyond', exc)
        if len(hrefs) > self.args.max_dndbeyond:
            self.issue('dndbeyond', f'{len(hrefs)} candidates; only the first {self.args.max_dndbeyond} were fetched')

    def run(self):
        (self.root / 'raw').mkdir(parents=True)
        providers = [('open5e', self.open5e), ('dndbeyond', self.dndbeyond)]
        if self.args.include_fivetools:
            providers.insert(1, ('fivetools', self.fivetools))
        for name, method in providers:
            if name in self.args.skip:
                continue
            try:
                method()
            except Exception as exc:
                self.issue(name, exc)
        manifest = {'created_utc': datetime.now(timezone.utc).isoformat(), 'species': self.species,
                    'probe': 'sizetest/monster_source_probe.py', 'requests': self.requests,
                    'records': self.records, 'issues': self.issues}
        (self.root / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        lines = [f'# {self.species}', '', '| Record | Provider | Bytes | Note |', '|---|---|---:|---|']
        lines += [f"| {r['file']} | {r['provider']} | {r['bytes']} | {r['note']} |" for r in self.records]
        lines += ['', '## Requests', '', '| Label | HTTP | Bytes | Seconds |', '|---|---:|---:|---:|']
        lines += [f"| {r['label']} | {r.get('status', 'failed')} | {r.get('bytes', '')} | {r['elapsed_seconds']} |" for r in self.requests]
        lines += ['', '## Issues', ''] + ([f"- {i['provider']}: {i['error']}" for i in self.issues] or ['- none'])
        (self.root / 'report.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        return {'species': self.species, 'directory': self.root.name, 'records': len(self.records),
                'by_provider': {p: sum(r['provider'] == p for r in self.records) for p in ('open5e', 'fivetools', 'dndbeyond')},
                'issues': len(self.issues)}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('species', nargs='*', help='Exact monster names, e.g. "Adult Red Dragon"')
    parser.add_argument('--species-file', type=Path, help='One species per line; # starts a comment')
    parser.add_argument('--random', type=int, default=0, help='Add N names from the built-in suggestion list')
    parser.add_argument('--list-suggestions', action='store_true')
    parser.add_argument('--out', type=Path, default=Path('monsters_examples'))
    parser.add_argument('--display-json', type=Path, help='Optional display configuration (provider URLs/sources)')
    parser.add_argument('--include-fivetools', action='store_true', help='Also save exact 5e.tools records (datasets are not kept)')
    parser.add_argument('--skip', action='append', default=[], choices=['open5e', 'fivetools', 'dndbeyond'])
    parser.add_argument('--max-dndbeyond', type=int, default=8, help='Detail pages per species')
    parser.add_argument('--delay', type=float, default=1.0, help='Seconds between requests')
    parser.add_argument('--timeout', type=float, default=30)
    parser.add_argument('--max-response-mib', type=int, default=64)
    args = parser.parse_args()
    if args.list_suggestions:
        print('\n'.join(SUGGESTED))
        return 0
    names = list(args.species)
    if args.species_file:
        names += [line.split('#')[0].strip() for line in args.species_file.read_text(encoding='utf-8').splitlines()]
    if args.random:
        names += random.sample(SUGGESTED, min(args.random, len(SUGGESTED)))
    names = [n for n in dict.fromkeys(n for n in names if n)]
    if not names:
        parser.error('Give at least one species, --species-file or --random N')
    if args.timeout <= 0 or args.delay < 0 or not 1 <= args.max_response_mib <= 256 or not 1 <= args.max_dndbeyond <= 32:
        parser.error('Invalid timeout, delay, response ceiling or --max-dndbeyond')
    cfg = json.loads(args.display_json.read_text(encoding='utf-8')) if args.display_json else {}
    cfg = cfg.get('display', cfg)
    args.out.mkdir(parents=True, exist_ok=True)
    summary = []
    for name in names:
        root = args.out / slug(name)
        if root.exists() and any(root.iterdir()):
            print(f'Skipping {name}: {root} already has results (earlier evidence is never overwritten)')
            continue
        print(f'Collecting {name} ...', flush=True)
        result = Probe(root, name, args, cfg).run()
        print(f"  {result['records']} records {result['by_provider']}, {result['issues']} issues")
        summary.append(result)
    index_path = args.out / 'index.json'
    previous = json.loads(index_path.read_text(encoding='utf-8')) if index_path.exists() else []
    index_path.write_text(json.dumps(previous + summary, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0 if any(r['records'] for r in summary) else 2


if __name__ == '__main__':
    raise SystemExit(main())
