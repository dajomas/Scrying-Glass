"""Shared pieces for the Open5e, D&D Beyond and .monster adapters (022.05-022.07).

- markdown_inline / markdown_entries: the safe Markdown subset the sources use
  (bold, italic, bullet lists, pipe tables, paragraphs). HTML tags are removed
  and reported; nothing is rendered as HTML.
- ProviderFetcher: bounded HTTPS GET for an allowlisted host set, at most three
  same-set redirects, response size enforced while reading, no cookies.
- assemble: facts + sections + provenance -> validated version-one snapshot
  with species placeholders for the selected creature's own text.
"""
from __future__ import annotations

import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, HTTPSHandler, Request, build_opener

from .scrying_glass_fivetools_nodes import NodeBuilder
from .scrying_glass_statblock_model import ModelLimits, StatblockError, canonical_bytes, content_digest, validate_snapshot

PARTIAL_CODES = frozenset(('reference_unavailable', 'section_unavailable', 'license_unavailable_partial'))
_TAG = re.compile(r'<[^>]{0,500}>')
_TABLE_RULE = re.compile(r'^\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$')
APOSTROPHES = str.maketrans({'’': "'", '‘': "'", 'ʼ': "'"})


class SourceError(ValueError):
    def __init__(self, code, detail=None):
        self.code, self.detail = code, detail
        super().__init__(code)


def name_key(name):
    """Compare names like the providers' users do: case, apostrophes, spacing."""
    return re.sub(r'\s+', ' ', str(name).translate(APOSTROPHES).casefold()).strip()


def toggle_items(atoms):
    """atoms: ('text', s) | ('species', label) -> nested inline items.

    Tetra-cube/Markdown toggles: '***' strong+emphasis, '**' strong, '*' or '_'
    emphasis; an unclosed toggle closes at the end, as Tetra-cube does.
    """
    root = []
    stack = [(None, root)]
    def toggle(kind):
        if any(k == kind for k, _ in stack[1:]):
            while stack[-1][0] != kind:
                stack.pop()
            stack.pop()
        else:
            node = []
            stack[-1][1].append((kind, node))
            stack.append((kind, node))
    for kind, value in atoms:
        if kind == 'species':
            stack[-1][1].append(('species', value))
            continue
        for part in re.split(r'(\*\*\*|\*\*|\*|(?<![A-Za-z0-9])_|_(?![A-Za-z0-9]))', value):
            if part == '***':
                toggle('strong')
                toggle('emphasis')
            elif part == '**':
                toggle('strong')
            elif part in ('*', '_'):
                toggle('emphasis')
            elif part:
                stack[-1][1].append(('text', part))
    return root


def strip_html(text, warn=None):
    if '<' in text and _TAG.search(text):
        if warn:
            warn('html_removed', 'Embedded HTML markup was removed; its text is kept.')
        text = _TAG.sub('', text)
    return text


def markdown_inline(text):
    return toggle_items([('text', strip_html(text))])


def markdown_entries(text, warn=None):
    """Paragraphs, bullet lists and pipe tables from Markdown-ish text."""
    text = strip_html(text.replace('\r\n', '\n').replace('\r', '\n'), warn)
    entries, lines = [], text.split('\n')
    index = 0
    while index < len(lines):
        line = lines[index].rstrip()
        stripped = line.strip()
        if not stripped:
            index += 1
            continue
        if re.match(r'^[*\-•]\s+', stripped):
            items = []
            while index < len(lines) and re.match(r'^\s*[*\-•]\s+', lines[index]):
                items.append(re.sub(r'^\s*[*\-•]\s+', '', lines[index]).strip())
                index += 1
            entries.append({'type': 'list', 'items': items})
            continue
        if stripped.startswith('|') and index + 1 < len(lines) and _TABLE_RULE.match(lines[index + 1].strip()):
            def cells(row):
                return [c.strip() for c in row.strip().strip('|').split('|')]
            table = {'type': 'table', 'colLabels': cells(stripped), 'rows': []}
            index += 2
            while index < len(lines) and lines[index].strip().startswith('|'):
                table['rows'].append(cells(lines[index]))
                index += 1
            entries.append(table)
            continue
        entries.append(stripped.lstrip('>').strip() if stripped.startswith('>') else stripped)
        index += 1
    return entries


class _Gated(Exception):
    """The provider answered with an access gate (paywall, sign-in) instead of the page."""


class _Redirects(HTTPRedirectHandler):
    def __init__(self, hosts, gate_redirect=None):
        super().__init__()
        self.hosts, self.count, self.gate_redirect = hosts, 0, gate_redirect

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.count += 1
        if self.gate_redirect is not None and self.gate_redirect(req.full_url, newurl):
            if fp is not None:
                fp.close()
            raise _Gated()  # not followed: the gate's host may be outside the allowlist
        target = urlsplit(newurl)
        if self.count > 3 or target.scheme != 'https' or target.hostname not in self.hosts:
            raise SourceError('unsafe_redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class ProviderFetcher:
    """fetch(url, deadline=...) -> bytes for HTTPS URLs on allowlisted hosts.

    Optional access-gate rules (D&D Beyond): ``gate_redirect(url, target)`` and
    ``gate_status(url, status, body)`` identify a paywall or sign-in answer. A gated
    request returns empty bytes -- "no statblock here", a cacheable answer -- as the
    Add Monster stats lookup does, instead of a provider failure.
    """

    GATE_BODY_BYTES = 128000

    def __init__(self, hosts, *, response_bytes=10485760, accept='application/json', opener_factory=None,
                 gate_redirect=None, gate_status=None):
        self.hosts, self.response_bytes, self.accept = frozenset(hosts), response_bytes, accept
        self._opener_factory = opener_factory
        self.gate_redirect, self.gate_status = gate_redirect, gate_status

    def __call__(self, url, *, deadline):
        parts = urlsplit(url)
        if parts.scheme != 'https' or parts.hostname not in self.hosts or parts.username or parts.password:
            raise SourceError('unsafe_url')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise SourceError('deadline')
        redirects = _Redirects(self.hosts, self.gate_redirect)
        opener = self._opener_factory(redirects) if self._opener_factory else build_opener(HTTPSHandler(), redirects)
        request = Request(url, headers={'User-Agent': 'ScryingGlass/1.0', 'Accept': self.accept, 'Accept-Encoding': 'identity'})
        try:
            with opener.open(request, timeout=max(0.1, min(remaining, 10))) as response:
                if urlsplit(response.geturl()).hostname not in self.hosts:
                    raise SourceError('unsafe_redirect')
                if (response.headers.get('Content-Encoding') or 'identity').lower() not in ('identity', ''):
                    raise SourceError('unsupported_content_encoding')
                chunks, total = [], 0
                while True:
                    if time.monotonic() >= deadline:
                        raise SourceError('deadline')
                    chunk = response.read(65536)
                    if not chunk:
                        return b''.join(chunks)
                    total += len(chunk)
                    if total > self.response_bytes:
                        raise SourceError('response_bytes_limit')
                    chunks.append(chunk)
        except _Gated:
            return b''
        except SourceError:
            raise
        except HTTPError as exc:
            if self.gate_status is not None:
                try:
                    with exc:
                        body = exc.read(self.GATE_BODY_BYTES + 1)
                except Exception:
                    body = b''
                if len(body) <= self.GATE_BODY_BYTES and self.gate_status(url, exc.code, body):
                    return b''
            raise SourceError('not_found' if exc.code == 404 else 'provider_error') from None
        except (URLError, OSError, ValueError):
            raise SourceError('provider_unavailable') from None


def species_splitter(label):
    """Complete, case-insensitive source-label matches -> species placeholders."""
    if not label or not label.strip():
        return None
    words = [re.escape(part.translate(APOSTROPHES)) for part in label.split()]
    body = r'\s+'.join(w.replace("'", "['’]") for w in words)
    pattern = re.compile(r'(?<!\w)' + body + r'(?!\w)', re.IGNORECASE)
    def split(text):
        out, last = [], 0
        for match in pattern.finditer(text):
            if match.start() > last:
                out.append(('text', text[last:match.start()]))
            out.append(('species', match.group(0)))
            last = match.end()
        if last < len(text):
            out.append(('text', text[last:]))
        return out
    return split


def credit(attribution, *, publisher=None, license_name=None, license_url=None, position=0):
    return {'position': position, 'attribution': attribution, 'publisher': publisher,
            'license_name': license_name, 'license_url': license_url}


def assemble(*, source_label, subtitle, facts, sections, provenance, warnings, check, parser=markdown_inline,
             limits=None, adapter_version):
    """sections: [(label or None, entries, enabled)] -> validated snapshot and measurements."""
    limits = ModelLimits() if limits is None else limits
    rows = []
    def warn(code, message, owner=None, path=None):
        rows.append({'position': len(rows), 'code': code, 'message': message, 'source_path': path})
    for code, message, path in warnings:
        warn(code, message, None, path)
    builder = NodeBuilder(check=check, warn=warn, reference=lambda *args: None)
    builder.parser = parser
    builder.placeholder = species_splitter(source_label)
    for index, (label, entries, enabled) in enumerate(sections):
        section = builder.add('section', None, None, label=label, enabled=None if enabled is None else bool(enabled))
        builder.entries(section, None, entries, f'$/sections/{index}')
    fact_rows = []
    for key, label, text, number in facts:
        if text:
            row = {'position': len(fact_rows), 'key': key, 'label': label, 'display_text': text}
            if number is not None:
                row['integer_value'] = number
            fact_rows.append(row)
    for row in rows:
        if row['source_path'] is None:
            del row['source_path']
    prov = []
    for index, row in enumerate(provenance):
        row = {k: v for k, v in row.items() if v is not None}
        row['position'] = index
        row['adapter_version'] = adapter_version
        prov.append(row)
    snapshot = {'model_version': 1, 'source_label': source_label, 'subtitle': subtitle or '',
                'completeness': 'partial' if any(r['code'] in PARTIAL_CODES for r in rows) else 'available',
                'provenance': prov, 'facts': fact_rows, 'definitions': [], 'nodes': builder.rows, 'warnings': rows}
    try:
        snapshot = validate_snapshot(snapshot, limits)
        snapshot['content_digest'] = content_digest(snapshot, limits)
        size = len(canonical_bytes(snapshot, limits))
    except StatblockError as exc:
        raise SourceError(exc.code, exc.path) from None
    parents = {n['local_id']: n['parent_local_id'] for n in snapshot['nodes']}
    def depth(node):
        count = 0
        while node is not None:
            count, node = count + 1, parents[node]
        return count
    measurements = {'snapshot_bytes': size, 'content_nodes': len(snapshot['nodes']),
                    'content_depth': max((depth(n) for n in parents), default=0),
                    'warnings': len(snapshot['warnings'])}
    return snapshot, measurements
