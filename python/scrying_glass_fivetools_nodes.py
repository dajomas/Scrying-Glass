"""Convert 5e.tools entry trees to version-one statblock nodes (022.04e).

Builds rows for scrying_glass_statblock_model.validate_snapshot: block roots,
paragraph/inline runs, lists, tables and references. Imported HTML never
survives: every string is parsed with the tag port and emitted as text,
emphasis/strong, validated HTTPS link, reference or species placeholder nodes.
Entry types without a structural mapping keep their readable text and record a
warning instead of being discarded.
"""
import re

from .scrying_glass_fivetools_tags import parse_inline, strip_tags

CONTAINER_TYPES = frozenset(('entries', 'section', 'inset', 'insetReadaloud', 'variant', 'variantInner',
                             'variantSub', 'optfeature', 'patron', 'options', 'flowchart', 'flowBlock',
                             'homebrew', 'wrapper', 'item', 'itemSub', 'refClassFeature', 'refSubclassFeature',
                             'refOptionalfeature', 'tableGroup'))
SILENT_TYPES = frozenset(('hr',))
MEDIA_TYPES = frozenset(('image', 'gallery', 'gridImage'))


def ordinal(number):
    if 10 <= number % 100 <= 20:
        return f'{number}th'
    return f'{number}' + {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')


def spell_level(level):
    return 'Cantrip' if level == 0 else ordinal(level)


class NodeBuilder:
    """Accumulates node rows; positions are assigned per (definition, parent)."""

    def __init__(self, *, check, warn, reference):
        self.rows, self._count, self._positions = [], 0, {}
        self.check, self.warn, self.reference = check, warn, reference
        self.placeholder = None
        self.parser = parse_inline

    def add(self, kind, parent, owner, **fields):
        self.check()
        self._count += 1
        local_id = f'n{self._count}'
        key = (owner, parent)
        position = self._positions.get(key, 0)
        self._positions[key] = position + 1
        row = {'local_id': local_id, 'parent_local_id': parent, 'definition_id': owner,
               'position': position, 'kind': kind}
        row.update({k: v for k, v in fields.items() if v is not None})
        self.rows.append(row)
        return local_id

    # -- inline ------------------------------------------------------------
    def _text(self, parent, owner, text):
        if not text:
            return
        if owner is None and self.placeholder is not None:
            for kind, value in self.placeholder(text):
                if kind == 'text':
                    self.add('text', parent, owner, text=value)
                else:
                    self.add('species_placeholder', parent, owner, label=value)
            return
        self.add('text', parent, owner, text=text)

    def inline(self, parent, owner, items, *, in_link=False):
        for item in items:
            kind = item[0]
            if kind == 'text':
                self._text(parent, owner, item[1])
            elif kind == 'ref':
                _, ref_kind, name, source, label = item
                target = None if in_link else self.reference(ref_kind, name, source)
                if target is None:
                    self._text(parent, owner, label)
                else:
                    self.add('reference', parent, owner, target_definition_local_id=target, label=label or name)
            elif kind in ('strong', 'emphasis'):
                node = self.add(kind, parent, owner)
                self.inline(node, owner, item[1], in_link=in_link)
            elif kind == 'link':
                if in_link:
                    self.inline(parent, owner, item[2], in_link=True)
                else:
                    node = self.add('link', parent, owner, url=item[1])
                    self.inline(node, owner, item[2], in_link=True)
            elif kind == 'group':
                self.inline(parent, owner, item[1], in_link=in_link)
            elif kind == 'species':
                node = self.add('species_placeholder', parent, owner, label=item[1])
            elif kind == 'unknown':
                self.warn('unsupported_tag', f'Tag "{item[1]}" kept as text.', owner)
                self._text(parent, owner, item[2])

    def paragraph(self, parent, owner, text):
        if text is None or text == '':
            return
        node = self.add('paragraph', parent, owner)
        self.inline(node, owner, self.parser(text))

    def inline_text(self, parent, owner, text):
        self.inline(parent, owner, self.parser(text))

    # -- blocks ------------------------------------------------------------
    def entries(self, parent, owner, values, path):
        values = values if type(values) is list else [values]
        for index, value in enumerate(values):
            self.entry(parent, owner, value, f'{path}/{index}')

    def entry(self, parent, owner, value, path):
        self.check()
        if value is None:
            return
        if type(value) is str:
            self.paragraph(parent, owner, value)
            return
        if type(value) in (int, float) and type(value) is not bool:
            self.paragraph(parent, owner, str(value))
            return
        if type(value) is list:
            self.entries(parent, owner, value, path)
            return
        if type(value) is not dict:
            self.warn('unsupported_entry', 'An entry value could not be shown.', owner, path)
            return
        kind = value.get('type', 'entries')
        if kind in SILENT_TYPES:
            return
        if kind == 'wrapper' and ('wrapped' in value or 'wrappeds' in value):
            # Rendered in place, as the runtime does (Renderer._recursiveRender); SG-TODO-034
            # item text arrives this way.
            if 'wrappeds' in value:
                self.entries(parent, owner, value['wrappeds'], f'{path}/wrappeds')
            else:
                self.entry(parent, owner, value['wrapped'], f'{path}/wrapped')
            return
        if kind == 'inlineItems':
            node = self.add('paragraph', parent, owner)
            self.inline(node, owner, value.get('items') or [])
            return
        if kind == 'list':
            self._list(parent, owner, value, path)
        elif kind == 'table':
            self._table(parent, owner, value, path)
        elif kind in ('inline', 'inlineBlock'):
            node = self.add('paragraph', parent, owner)
            for child in value.get('entries') or []:
                if type(child) is str:
                    self.inline_text(node, owner, child)
                elif type(child) is dict and child.get('type') == 'link':
                    self._link_inline(node, owner, child)
                elif type(child) is dict:
                    self.inline_text(node, owner, self.plain(child))
        elif kind == 'link':
            node = self.add('paragraph', parent, owner)
            self._link_inline(node, owner, value)
        elif kind == 'quote':
            node = self.add('entry', parent, owner)
            self.entries(node, owner, value.get('entries') or [], path + '/entries')
            if value.get('by') or value.get('from'):
                by = ', '.join(x for x in (value.get('by'), value.get('from')) if type(x) is str)
                self.paragraph(node, owner, '— ' + by)
        elif kind == 'itemSpell':
            node = self.add('paragraph', parent, owner)
            strong = self.add('strong', node, owner)
            self.inline_text(strong, owner, value.get('name') or '')
            self._text(node, owner, ' ')
            self.inline_text(node, owner, value.get('entry') or '')
        elif kind == 'spellcasting':
            self.spellcasting(parent, owner, value, path)
        elif kind in ('dice', 'bonus', 'bonusSpeed', 'abilityDc', 'abilityAttackMod', 'abilityGeneric'):
            self.paragraph(parent, owner, self._formula_text(value))
        elif kind in ('statblock', 'statblockInline'):
            name, source = value.get('name'), value.get('source')
            target = self.reference('monster', name, source or 'MM') if value.get('tag', 'creature') == 'creature' and type(name) is str else None
            node = self.add('paragraph', parent, owner)
            if target:
                self.add('reference', node, owner, target_definition_local_id=target, label=value.get('displayName') or name)
            else:
                self._text(node, owner, str(value.get('displayName') or name or ''))
                self.warn('unsupported_entry', 'An embedded statblock is shown by name only.', owner, path)
        elif kind == 'code':
            self.paragraph(parent, owner, value.get('preformatted') if type(value.get('preformatted')) is str else '')
        elif kind in MEDIA_TYPES:
            title = value.get('title') if type(value.get('title')) is str else ''
            self.warn('media_omitted', 'An image is not shown.', owner, path)
            if title:
                self.paragraph(parent, owner, f'[Image: {title}]')
        elif kind in CONTAINER_TYPES or 'entries' in value or 'entry' in value or 'items' in value:
            if kind not in CONTAINER_TYPES:
                self.warn('unsupported_entry_type', f'Entry type "{kind}" shown as plain entries.', owner, path)
            label = strip_tags(value['name']) if type(value.get('name')) is str and value.get('name') else None
            node = self.add('entry', parent, owner, label=label)
            for key in ('entries', 'entry', 'items', 'tables', 'headerEntries'):
                if key in value:
                    self.entries(node, owner, value[key], f'{path}/{key}')
        else:
            self.warn('unsupported_entry_type', f'Entry type "{kind}" shown as text.', owner, path)
            self.paragraph(parent, owner, self.plain(value))

    def _link_inline(self, parent, owner, value):
        href = value.get('href') if type(value.get('href')) is dict else {}
        text = value.get('text') if type(value.get('text')) is str else ''
        url = href.get('url') if href.get('type') == 'external' else None
        from .scrying_glass_fivetools_tags import safe_https
        url = safe_https(url)
        if url:
            node = self.add('link', parent, owner, url=url)
            self.inline(node, owner, parse_inline(text or url), in_link=True)
        else:
            self.inline_text(parent, owner, text)

    def _list(self, parent, owner, value, path):
        node = self.add('list', parent, owner, ordered='decimal' in str(value.get('style', '')))
        for index, item in enumerate(value.get('items') or []):
            child = f'{path}/items/{index}'
            row = self.add('list_item', node, owner)
            if type(item) is str:
                self.inline_text(row, owner, item)
            elif type(item) is dict and item.get('type') in ('item', 'itemSub', 'itemSpell') and type(item.get('name')) is str:
                single = item.get('entry') if type(item.get('entry')) is str else None
                entries = item.get('entries')
                if single is None and type(entries) is list and len(entries) == 1 and type(entries[0]) is str:
                    single = entries[0]
                if single is not None:
                    strong = self.add('strong', row, owner)
                    self.inline_text(strong, owner, item['name'])
                    self._text(row, owner, ' ')
                    self.inline_text(row, owner, single)
                else:
                    self.entry(row, owner, item, child)
            else:
                self.entry(row, owner, item, child)

    def _table(self, parent, owner, value, path):
        caption = strip_tags(value['caption']) if type(value.get('caption')) is str else None
        node = self.add('table', parent, owner, label=caption)
        labels = value.get('colLabels')
        if type(labels) is list and labels:
            row = self.add('row', node, owner)
            for label in labels:
                cell = self.add('cell', row, owner)
                strong = self.add('strong', cell, owner)
                self.inline_text(strong, owner, label if type(label) is str else self.plain(label))
        for index, cells in enumerate(value.get('rows') or []):
            if type(cells) is dict and cells.get('type') == 'row':
                cells = cells.get('row')
            if type(cells) is not list:
                self.warn('unsupported_entry', 'A table row could not be shown.', owner, f'{path}/rows/{index}')
                continue
            row = self.add('row', node, owner)
            for cell_value in cells:
                cell = self.add('cell', row, owner)
                if type(cell_value) is str:
                    self.inline_text(cell, owner, cell_value)
                elif type(cell_value) is dict and cell_value.get('type') == 'cell':
                    self.inline_text(cell, owner, self._roll_text(cell_value.get('roll')))
                    if 'entry' in cell_value:
                        self.entry(cell, owner, cell_value['entry'], path)
                elif type(cell_value) in (int, float) and type(cell_value) is not bool:
                    self._text(cell, owner, str(cell_value))
                else:
                    self.entry(cell, owner, cell_value, path)

    @staticmethod
    def _roll_text(roll):
        if type(roll) is not dict:
            return ''
        if 'exact' in roll:
            return str(roll['exact'])
        if 'min' in roll or 'max' in roll:
            return f"{roll.get('min', '')}–{roll.get('max', '')}"
        return ''

    def _formula_text(self, value):
        kind = value.get('type')
        if kind == 'dice':
            roll = value.get('toRoll')
            if type(roll) is list:
                return ' + '.join(f"{r.get('number', 1)}d{r.get('faces', '')}" + (f"+{r['modifier']}" if r.get('modifier') else '')
                                  for r in roll if type(r) is dict)
            return str(roll or '')
        if kind == 'bonus':
            number = value.get('value', 0)
            return f"{'+' if type(number) in (int, float) and number >= 0 else ''}{number}"
        if kind == 'bonusSpeed':
            number = value.get('value', 0)
            return f"{'+' if type(number) in (int, float) and number >= 0 else ''}{number} ft."
        attributes = ' or '.join(str(a) for a in value.get('attributes') or [])
        if kind == 'abilityDc':
            return f"{value.get('name', '')} save DC = 8 + your proficiency bonus + your {attributes} modifier".strip()
        if kind == 'abilityAttackMod':
            return f"{value.get('name', '')} attack modifier = your proficiency bonus + your {attributes} modifier".strip()
        return self.plain(value)

    def plain(self, value):
        """Readable fallback text for an unrecognized structure (all string values)."""
        parts = []
        stack = [value]
        while stack:
            self.check()
            item = stack.pop()
            if type(item) is str:
                if item not in ('entries', 'list', 'item'):
                    parts.append(item)
            elif type(item) in (int, float) and type(item) is not bool:
                parts.append(str(item))
            elif type(item) is list:
                stack.extend(reversed(item))
            elif type(item) is dict:
                stack.extend(reversed([v for k, v in item.items() if k not in ('type', 'style', 'data')]))
        return ' '.join(p for p in parts if p)

    # -- spellcasting --------------------------------------------------------
    def spellcasting(self, parent, owner, value, path):
        self.entries(parent, owner, spellcasting_entries(value), path)


USES = (('recharge', None, True), ('legendary', ' legendary action', False), ('charges', ' charge', False),
        ('rest', '/rest', False), ('restLong', '/long rest', False), ('daily', '/day', False),
        ('weekly', '/week', False), ('monthly', '/month', False), ('yearly', '/year', False))
_USES_KEY = re.compile(r'([1-9][0-9]?)(e?)\Z')


def _spell_list(values):
    return ', '.join(item.get('entry') if type(item) is dict else item for item in (values or [])
                     if not (type(item) is dict and item.get('hidden')) and (type(item) is str or type(item) is dict and type(item.get('entry')) is str))


def spellcasting_entries(entry):
    """Port of Renderer._renderSpellcasting_getEntries as 5e.tools entries."""
    hidden = set(entry.get('hidden') or [])
    header = {'type': 'entries', 'name': entry.get('name'), 'entries': list(entry.get('headerEntries') or [])}
    items = []
    if entry.get('constant') and 'constant' not in hidden:
        items.append({'type': 'itemSpell', 'name': 'Constant:', 'entry': _spell_list(entry['constant'])})
    if entry.get('will') and 'will' not in hidden:
        items.append({'type': 'itemSpell', 'name': 'At will:', 'entry': _spell_list(entry['will'])})
    for prop, suffix, skip_prefix in USES:
        if not entry.get(prop) or prop in hidden or type(entry[prop]) is not dict:
            continue
        keys = [k for k in entry[prop] if _USES_KEY.match(k)]
        keys.sort(key=lambda k: (int(_USES_KEY.match(k).group(1)), k), reverse=True)
        for key in keys:
            number, each = int(_USES_KEY.match(key).group(1)), bool(_USES_KEY.match(key).group(2))
            if prop == 'recharge':
                duration = f'{{@recharge {number}|m}}'
            elif prop in ('legendary', 'charges'):
                duration = f"{suffix}{'' if number == 1 else 's'}"
            else:
                duration = suffix
            name = f"{'' if skip_prefix else number}{duration}{' each' if each else ''}:"
            items.append({'type': 'itemSpell', 'name': name, 'entry': _spell_list(entry[prop][key])})
    if entry.get('ritual') and 'ritual' not in hidden:
        items.append({'type': 'itemSpell', 'name': 'Rituals:', 'entry': _spell_list(entry['ritual'])})
    items = [item for item in items if item['entry'] != '']
    if items:
        header['entries'].append({'type': 'list', 'style': 'list-hang-notitle', 'items': items})
    spells = entry.get('spells')
    if type(spells) is dict and spells and 'spells' not in hidden:
        levels = []
        for level in sorted((k for k in spells if k.isdigit()), key=int):
            group = spells[level] if type(spells[level]) is dict else {}
            number = int(level)
            label = f"{spell_level(number)}{'s' if number == 0 else ' level'}"
            slots, lower = group.get('slots'), group.get('lower')
            at_will = ' (at will)'
            if type(slots) in (int, float) and slots >= 0:
                at_will = f" ({slots} slot{'s' if slots > 1 else ''})" if slots > 0 else ''
            if type(lower) is int and lower and lower != number:
                label = f'{spell_level(lower)}-{label}'
                if type(slots) in (int, float) and slots >= 0:
                    at_will = f" ({slots} {spell_level(number)}-level slot{'s' if slots > 1 else ''})" if slots > 0 else ''
            levels.append({'type': 'itemSpell', 'name': f'{label}{at_will}:', 'entry': _spell_list(group.get('spells')) or '—'})
        header['entries'].append({'type': 'list', 'style': 'list-hang-notitle', 'items': levels})
    out = [header]
    if entry.get('footerEntries'):
        out.append({'type': 'entries', 'entries': entry['footerEntries']})
    return out
