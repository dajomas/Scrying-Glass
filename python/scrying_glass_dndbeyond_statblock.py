"""Public D&D Beyond statblock adapter (SG-TODO-022.06), 2014 and 2024 markup.

Exact identity: the numeric monster id (canonical /monsters/<id>-<slug> URL).
Only the public page is read: no login, cookies or gate bypass. A page with no
statblock root (gated or changed markup) is ``unavailable`` -- never guessed.
Parsed: name/meta, attributes, ability table/blocks, tidbits, description
blocks (traits/actions/... with their intro text), the lair content below the
statblock and the habitat/treasure/source footer. Links stay links to D&D
Beyond (definitions there are not public); dice stay text. The six Scrying
Glass fields (name, species, AC, HP, initiative) are never facts.
"""
from __future__ import annotations

import re
import time
from html.parser import HTMLParser
from urllib.parse import urljoin, urlencode, urlsplit

from .scrying_glass_statblock_sources import SourceError, assemble, credit, name_key, toggle_items
from .scrying_glass_statblock_model import ModelLimits

ADAPTER_VERSION = 'dndbeyond-06-1'
PROVIDER = 'D&D Beyond'
SITE = 'https://www.dndbeyond.com'
HOSTS = frozenset(('www.dndbeyond.com', 'dndbeyond.com'))
MONSTER_PATH = re.compile(r'/monsters/([0-9]{1,12})(?:-[a-z0-9-]{1,200})?\Z')
VOID = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'))
SKIP = frozenset(('script', 'style', 'svg', 'noscript', 'template', 'iframe', 'button'))
SG_LABELS = frozenset(('armor class', 'ac', 'hit points', 'hp', 'initiative'))
MAX_ELEMENTS = 200000


class Element:
    __slots__ = ('tag', 'attrs', 'children', 'parent')

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.children, self.parent = tag, attrs, [], parent

    def classes(self):
        return (self.attrs.get('class') or '').split()

    def has(self, suffix):
        return any(c.endswith(suffix) for c in self.classes())

    def find_all(self, predicate):
        out, stack = [], list(reversed(self.children))
        while stack:
            node = stack.pop()
            if isinstance(node, Element):
                if predicate(node):
                    out.append(node)
                stack.extend(reversed(node.children))
        return out

    def find(self, predicate):
        found = self.find_all(predicate)
        return found[0] if found else None

    def text(self):
        parts = []
        for child in self.children:
            parts.append(child if isinstance(child, str) else child.text())
        return ''.join(parts)


class _Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element('#root', {}, None)
        self.current, self.count, self.skipping = self.root, 0, 0

    def handle_starttag(self, tag, attrs):
        if self.skipping:
            self.skipping += tag not in VOID
            return
        if tag in SKIP:
            self.skipping = int(tag not in VOID)
            return
        self.count += 1
        if self.count > MAX_ELEMENTS:
            raise SourceError('page_too_complex')
        node = Element(tag, {k: v or '' for k, v in attrs}, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        if self.skipping or tag in SKIP:
            return
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.current.tag == tag:
            self.current = self.current.parent

    def handle_endtag(self, tag):
        if self.skipping:
            self.skipping -= 1
            return
        node = self.current
        while node is not None and node.tag != tag:
            node = node.parent
        if node is not None and node.parent is not None:
            self.current = node.parent

    def handle_data(self, data):
        if not self.skipping:
            self.current.children.append(data)


def parse_html(text):
    tree = _Tree()
    tree.feed(text)
    tree.close()
    return tree.root


def clean(text):
    return re.sub(r'\s+', ' ', text.replace('\xa0', ' ')).strip()


def _link(href):
    if not href:
        return None
    url = urljoin(SITE + '/', href)
    parts = urlsplit(url)
    return url if parts.scheme == 'https' and parts.hostname in HOSTS else None


def inline_items(node):
    """Element -> inline items (strong/emphasis/link/text); whitespace collapsed."""
    items = []
    for child in node.children:
        if isinstance(child, str):
            text = re.sub(r'\s+', ' ', child.replace('\xa0', ' '))
            if text:
                items.append(('text', text))
            continue
        if child.tag == 'br':
            items.append(('text', ' '))
            continue
        inner = inline_items(child)
        if child.tag in ('strong', 'b'):
            items.append(('strong', inner))
        elif child.tag in ('em', 'i'):
            items.append(('emphasis', inner))
        elif child.tag == 'a' and _link(child.attrs.get('href')):
            items.append(('link', _link(child.attrs.get('href')), inner))
        else:
            items.append(('group', inner))
    return items


def _trim(items):
    while items and items[0][0] == 'text' and not items[0][1].strip():
        items = items[1:]
    if items and items[0][0] == 'text':
        items = [('text', items[0][1].lstrip())] + items[1:]
    return items


def block_entries(node, warn):
    """Block content (p, ul/ol, table, headings, divs) -> entries list."""
    entries, pending = [], None
    def flush_inline(items):
        items = _trim(items)
        if any(i[0] != 'text' or i[1].strip() for i in items):
            entries.append({'type': 'inlineItems', 'items': items})
    loose = []
    for child in node.children:
        if isinstance(child, str) or child.tag in ('a', 'span', 'strong', 'em', 'b', 'i', 'br'):
            loose.append(child)
            continue
        if loose:
            holder = Element('#text', {}, None)
            holder.children = loose
            flush_inline(inline_items(holder))
            loose = []
        if child.tag == 'p':
            flush_inline(inline_items(child))
        elif child.tag in ('ul', 'ol'):
            items = [{'type': 'entries', 'entries': block_entries(li, warn)} for li in child.children
                     if isinstance(li, Element) and li.tag == 'li']
            entries.append({'type': 'list', 'style': 'list-decimal' if child.tag == 'ol' else '', 'items': items})
        elif child.tag == 'table':
            rows = [r for r in child.find_all(lambda e: e.tag == 'tr')]
            table = {'type': 'table', 'rows': []}
            for index, row in enumerate(rows):
                cells = [clean(c.text()) for c in row.children if isinstance(c, Element) and c.tag in ('td', 'th')]
                if index == 0 and any(c.tag == 'th' for c in row.children if isinstance(c, Element)):
                    table['colLabels'] = cells
                else:
                    table['rows'].append(cells)
            entries.append(table)
        elif re.fullmatch(r'h[1-6]', child.tag):
            pending = {'type': 'entries', 'name': clean(child.text()), 'entries': []}
            entries.append(pending)
            continue
        elif child.tag in ('img', 'figure', 'picture'):
            warn('media_omitted', 'An image is not shown.', None)
        else:
            entries.extend(block_entries(child, warn))
        if pending is not None and entries and entries[-1] is not pending:
            pending['entries'].append(entries.pop())
    if loose:
        holder = Element('#text', {}, None)
        holder.children = loose
        flush_inline(inline_items(holder))
    return entries


def _description_block(block, warn):
    heading = block.find(lambda e: e.has('__description-block-heading'))
    content = block.find(lambda e: e.has('__description-block-content'))
    label = clean(heading.text()) if heading else None
    if content is None:
        return label, []
    entries = []
    for paragraph in block_entries(content, warn):
        items = paragraph.get('items') if paragraph.get('type') == 'inlineItems' else None
        if items and items[0][0] in ('emphasis', 'strong'):
            entries.append({'type': 'entries', 'entries': [paragraph]})
        else:
            entries.append(paragraph)
    return label, entries


def statblock_facts(root):
    facts = []
    def add(key, label, text, number=None):
        if text:
            facts.append((key, label, text, number))
    for attribute in root.find_all(lambda e: e.has('__attribute')):
        labels = attribute.find_all(lambda e: e.has('__attribute-label'))
        values = attribute.find_all(lambda e: e.has('__attribute-data') or e.has('__attribute-value'))
        if len(values) < len(labels):
            values = attribute.find_all(lambda e: e.has('__attribute-data-value'))
        for label_node, value_node in zip(labels, values):
            label = clean(label_node.text())
            if label.casefold() not in SG_LABELS:
                add('attribute_' + re.sub(r'[^a-z0-9]+', '_', label.casefold()).strip('_'), label, clean(value_node.text()))
    for row in root.find_all(lambda e: e.tag == 'tr' and e.find(lambda c: c.tag == 'th') is not None):
        cells = [clean(c.text()) for c in row.children if isinstance(c, Element) and c.tag in ('th', 'td')]
        if len(cells) >= 3 and cells[1].isdigit():
            number = int(cells[1])
            add(cells[0].lower(), cells[0], f'{cells[1]} ({cells[2]})' + (f', save {cells[3]}' if len(cells) > 3 else ''), number)
    for block in root.find_all(lambda e: e.has('ability-block__stat')):
        heading = block.find(lambda e: e.has('ability-block__heading'))
        score = block.find(lambda e: e.has('ability-block__score'))
        modifier = block.find(lambda e: e.has('ability-block__modifier'))
        if heading and score:
            text = clean(score.text())
            add(clean(heading.text()).lower(), clean(heading.text()), f'{text} {clean(modifier.text()) if modifier else ""}'.strip(),
                int(text) if text.isdigit() else None)
    for tidbit in root.find_all(lambda e: e.has('__tidbit')):
        label = tidbit.find(lambda e: e.has('__tidbit-label'))
        data = tidbit.find(lambda e: e.has('__tidbit-data'))
        if label and data:
            name = clean(label.text())
            add(re.sub(r'[^a-z0-9]+', '_', name.casefold()).strip('_'), name, clean(data.text()))
    return facts


def parse_page(text, monster_id):
    """-> (name, meta, facts, sections, footer_facts, warnings) or raise unavailable."""
    warnings = []
    def warn(code, message, owner=None, path=None):
        if (code, message, path) not in warnings:
            warnings.append((code, message, path))
    page = parse_html(text)
    roots = page.find_all(lambda e: e.tag == 'div' and ({'mon-stat-block', 'mon-stat-block-2024'} & set(e.classes())))
    if not roots:
        raise SourceError('statblock_unavailable')
    root = roots[0]
    link = root.find(lambda e: e.has('__name-link'))
    href = link.attrs.get('href', '') if link else ''
    match = MONSTER_PATH.match(href)
    if not match or match.group(1) != str(monster_id):
        raise SourceError('identity_mismatch')
    name = clean(link.text())
    meta_node = root.find(lambda e: e.has('__meta'))
    sections = []
    for block in root.find_all(lambda e: e.has('__description-block')):
        label, entries = _description_block(block, warn)
        if entries:
            sections.append((label, entries, None))
    more = page.find(lambda e: 'more-info-content' in e.classes())
    if more is not None:
        extra = block_entries(more, warn)
        if extra:
            sections.append(('Additional Information', extra, None))
    footer = []
    for tags in page.find_all(lambda e: e.tag == 'p' and ('tags' in e.classes() or 'source' in e.classes())):
        text = clean(tags.text())
        if ':' in text:
            label, _, value = text.partition(':')
            footer.append(('footer_' + re.sub(r'[^a-z0-9]+', '_', label.casefold()).strip('_'), label.strip(), value.strip(), None))
        elif text:
            footer.append(('footer_source', 'Source', text, None))
    return name, clean(meta_node.text()) if meta_node else '', statblock_facts(root), sections, footer, warnings


def canonical_url(path):
    if type(path) is not str:
        raise SourceError('invalid_request')
    if path.startswith(('http:', 'https:', '//')):
        parts = urlsplit(path)
        if parts.scheme != 'https' or parts.hostname not in HOSTS or parts.username or parts.password:
            raise SourceError('invalid_request')
        path = parts.path
    match = MONSTER_PATH.match(path)
    if not match:
        raise SourceError('invalid_request')
    return SITE + match.group(0), match.group(1)


def prepare_dndbeyond(path, *, fetch, deadline, limits=None, cancelled=lambda: False):
    """path: '/monsters/<id>-<slug>' or its URL. fetch(url, deadline=...) -> bytes."""
    url, monster_id = canonical_url(path)
    def check():
        if cancelled():
            raise SourceError('cancelled')
        if time.monotonic() >= deadline:
            raise SourceError('deadline')
    check()
    text = fetch(url, deadline=deadline).decode('utf-8', 'replace')
    check()
    name, meta, facts, sections, footer, warnings = parse_page(text, monster_id)
    provenance = [{'role': 'selected', 'provider': PROVIDER, 'endpoint': SITE, 'entity_id': f'monster|{monster_id}',
                   'source_url': url, 'source_code': next((f[2] for f in footer if f[0] == 'footer_source'), None),
                   'credits': [credit(f'{name} from D&D Beyond', publisher='Wizards of the Coast')]}]
    return assemble(source_label=name, subtitle=meta, facts=facts + footer, sections=sections, provenance=provenance,
                    warnings=warnings, check=check, parser=lambda s: toggle_items([('text', s)]),
                    limits=limits or ModelLimits(), adapter_version=ADAPTER_VERSION)


def discover_dndbeyond(species, *, fetch, deadline):
    """Exact-name public candidates [{path, name, legacy}] from the search page."""
    url = SITE + '/monsters?' + urlencode({'filter-search': species})
    page = parse_html(fetch(url, deadline=deadline).decode('utf-8', 'replace'))
    wanted, out = name_key(species), []
    for anchor in page.find_all(lambda e: e.tag == 'a'):
        href = anchor.attrs.get('href', '')
        if MONSTER_PATH.match(href) and name_key(clean(anchor.text())) == wanted and href not in [c['path'] for c in out]:
            row = anchor.parent
            legacy = 'legacy' in str(row.attrs).casefold() if row is not None else False
            out.append({'path': href, 'name': clean(anchor.text()), 'legacy': legacy})
    return out
