/* Safe statblock rendering for the statblock listener (SG-TODO-022.10).
 *
 * window.ScryingStatblock.render(snapshot, live, {prefix}) -> HTMLElement
 * window.ScryingStatblock.updateLive(element, live)         -> header and species placeholders
 *
 * Only DOM construction with textContent: imported text is never parsed as
 * HTML, no imported styles/handlers. Links must be https URLs without
 * credentials. The six Scrying Glass values (name, species, AC, HP, max HP,
 * initiative bonus) come from `live`, never from the snapshot. Supporting
 * definitions are shown once each, collapsed, under References; inline
 * reference buttons open the existing definition instead of nesting copies.
 */
(() => {
  'use strict';

  function el(tag, props, children) {
    const node = document.createElement(tag);
    for (const [key, value] of Object.entries(props || {})) {
      if (value === null || value === undefined || value === false) continue;
      if (key === 'text') node.textContent = value;
      else if (key === 'className') node.className = value;
      else node.setAttribute(key, value === true ? '' : String(value));
    }
    for (const child of children || []) if (child) node.append(child);
    return node;
  }

  function safeUrl(value) {
    if (typeof value !== 'string') return null;
    try {
      const url = new URL(value);
      return url.protocol === 'https:' && !url.username && !url.password ? url.href : null;
    } catch (error) {
      return null;
    }
  }

  function signed(value) {
    return typeof value === 'number' && Number.isFinite(value) ? (value >= 0 ? '+' + value : String(value)) : '—';
  }

  function plain(value) {
    return value === null || value === undefined || value === '' ? '—' : String(value);
  }

  function index(snapshot) {
    const children = new Map();
    const definitions = new Map();
    for (const node of snapshot.nodes || []) {
      const key = (node.definition_id || '') + '\u0000' + (node.parent_local_id || '');
      if (!children.has(key)) children.set(key, []);
      children.get(key).push(node);
    }
    for (const list of children.values()) list.sort((a, b) => a.position - b.position);
    for (const definition of snapshot.definitions || []) definitions.set(definition.local_id, definition);
    const owned = (rows, owner) => (rows || []).filter((row) => (row.definition_id || null) === owner)
      .sort((a, b) => a.position - b.position);
    return {
      children: (owner, parent) => children.get((owner || '') + '\u0000' + (parent || '')) || [],
      definitions,
      facts: (owner) => owned(snapshot.facts, owner),
      provenance: (owner) => owned(snapshot.provenance, owner),
      warnings: (owner) => owned(snapshot.warnings, owner),
    };
  }

  function referenceId(prefix, local) {
    return prefix + 'ref-' + String(local).replace(/[^A-Za-z0-9_-]/g, '_');
  }

  function renderNodes(ctx, owner, parent, container) {
    for (const node of ctx.idx.children(owner, parent)) container.append(renderNode(ctx, owner, node));
    return container;
  }

  function renderNode(ctx, owner, node) {
    const kids = (container) => renderNodes(ctx, owner, node.local_id, container);
    switch (node.kind) {
      case 'section': {
        const heading = el('h4', {className: 'sb-section-title', text: node.label || ''});
        if (node.enabled === false) heading.append(el('span', {className: 'sb-disabled', text: ' (not enabled)'}));
        return kids(el('section', {className: 'sb-section' + (node.enabled === false ? ' sb-section-disabled' : '')},
          node.label ? [heading] : []));
      }
      case 'entry': {
        const entry = el('div', {className: 'sb-entry' + (node.enabled === false ? ' sb-entry-disabled' : '')});
        if (node.label) entry.append(el('strong', {className: 'sb-entry-name', text: node.label.replace(/\.?$/, '.')}), ' ');
        return kids(entry);
      }
      case 'paragraph': return kids(el('p'));
      case 'list': return kids(el(node.ordered ? 'ol' : 'ul', {className: 'sb-list'}));
      case 'list_item': return kids(el('li'));
      case 'table': {
        const table = el('table', {className: 'sb-table'});
        if (node.label) table.append(el('caption', {text: node.label}));
        const body = el('tbody');
        table.append(body);
        renderNodes(ctx, owner, node.local_id, body);
        return table;
      }
      case 'row': return kids(el('tr'));
      case 'cell': return kids(el('td'));
      case 'text': return document.createTextNode(node.text || '');
      case 'emphasis': return kids(el('em'));
      case 'strong': return kids(el('strong'));
      case 'line_break': return el('br');
      case 'link': {
        const url = safeUrl(node.url);
        const link = url ? el('a', {href: url, target: '_blank', rel: 'noopener noreferrer nofollow'}) : el('span');
        kids(link);
        if (!link.textContent) link.textContent = node.text || node.label || url || '';
        return link;
      }
      case 'species_placeholder':
        return el('span', {className: 'sb-species-name', 'data-species': node.text || '',
                           text: ctx.live.species || node.text || ''});
      case 'reference': {
        const target = ctx.idx.definitions.get(node.target_definition_local_id);
        if (!target) return document.createTextNode(node.label || node.text || '');
        return el('button', {type: 'button', className: 'sb-ref', 'data-ref': referenceId(ctx.prefix, target.local_id),
                             'aria-controls': referenceId(ctx.prefix, target.local_id),
                             text: node.label || node.text || target.name});
      }
      default:
        return el('span', {text: node.text || node.label || ''});
    }
  }

  function facts(rows) {
    if (!rows.length) return null;
    const list = el('dl', {className: 'sb-facts'});
    for (const row of rows) list.append(el('div', {}, [el('dt', {text: row.label}), el('dd', {text: row.display_text})]));
    return list;
  }

  function sources(rows, title) {
    if (!rows.length) return null;
    const list = el('ul', {className: 'sb-sources'});
    for (const row of rows) {
      const item = el('li');
      const url = safeUrl(row.source_url);
      const label = [row.provider, row.source_code, row.edition, row.file_name].filter(Boolean).join(' · ');
      item.append(url ? el('a', {href: url, target: '_blank', rel: 'noopener noreferrer nofollow', text: label})
                      : document.createTextNode(label));
      if (row.role && row.role !== 'selected') item.append(el('span', {className: 'sb-role', text: ' (' + row.role + ')'}));
      for (const credit of row.credits || []) {
        const line = el('p', {className: 'sb-credit', text: credit.attribution});
        const licence = safeUrl(credit.license_url);
        if (credit.license_name) {
          line.append(' — ', licence ? el('a', {href: licence, target: '_blank', rel: 'noopener noreferrer nofollow',
                                                text: credit.license_name}) : credit.license_name);
        }
        if (credit.publisher) line.append(' — ' + credit.publisher);
        item.append(line);
      }
      list.append(item);
    }
    return el('div', {className: 'sb-source-block'}, [title ? el('h5', {text: title}) : null, list]);
  }

  function warnings(rows) {
    if (!rows.length) return null;
    const list = el('ul');
    for (const row of rows) list.append(el('li', {text: row.message}));
    return el('details', {className: 'sb-warnings'}, [el('summary', {text: 'Warnings (' + rows.length + ')'}), list]);
  }

  function header(live, snapshot) {
    const subtitle = [live.species, snapshot.subtitle].filter(Boolean).join(' — ');
    return el('header', {className: 'sb-header'}, [
      el('h3', {className: 'sb-title', 'data-live': 'name', text: plain(live.name)}),
      el('p', {className: 'sb-subtitle', 'data-live': 'subtitle', 'data-source-subtitle': snapshot.subtitle || '',
               text: subtitle}),
      el('dl', {className: 'sb-live'}, [
        el('div', {}, [el('dt', {text: 'Armor Class'}), el('dd', {'data-live': 'ac', text: plain(live.ac)})]),
        el('div', {}, [el('dt', {text: 'Hit Points'}),
          el('dd', {'data-live': 'hp', text: plain(live.hp) + ' / ' + plain(live.max_hp)})]),
        el('div', {}, [el('dt', {text: 'Initiative'}),
          el('dd', {'data-live': 'initiative_bonus', text: signed(live.initiative_bonus)})]),
      ]),
    ]);
  }

  function render(snapshot, live, options) {
    const prefix = (options && options.prefix) || 'sb-';
    const ctx = {idx: index(snapshot), live: live || {}, prefix};
    const root = el('article', {className: 'sb-statblock', 'data-completeness': snapshot.completeness});
    root.append(header(ctx.live, snapshot));
    if (snapshot.completeness === 'partial') {
      root.append(el('p', {className: 'sb-partial', role: 'note',
        text: 'Partial statblock: some source content could not be resolved. See Warnings.'}));
    }
    root.append(facts(ctx.idx.facts(null)) || '');
    renderNodes(ctx, null, null, root);
    root.append(warnings(ctx.idx.warnings(null)) || '');
    const definitions = [...ctx.idx.definitions.values()].sort((a, b) => a.position - b.position);
    if (definitions.length) {
      const refs = el('section', {className: 'sb-references', 'aria-label': 'References'},
        [el('h4', {className: 'sb-section-title', text: 'References'})]);
      for (const definition of definitions) {
        const body = el('div', {className: 'sb-ref-body'});
        body.append(facts(ctx.idx.facts(definition.local_id)) || '');
        renderNodes(ctx, definition.local_id, null, body);
        body.append(warnings(ctx.idx.warnings(definition.local_id)) || '');
        body.append(sources(ctx.idx.provenance(definition.local_id), 'Source') || '');
        refs.append(el('details', {className: 'sb-ref-details', id: referenceId(prefix, definition.local_id)}, [
          el('summary', {text: definition.name + (definition.kind ? ' (' + definition.kind + ')' : '')}), body]));
      }
      root.append(refs);
    }
    const credits = sources(ctx.idx.provenance(null), null);
    if (credits) root.append(el('section', {className: 'sb-credits', 'aria-label': 'Source and credits'},
      [el('h4', {className: 'sb-section-title', text: 'Source and credits'}), credits]));
    root.addEventListener('click', (event) => {
      const button = event.target.closest && event.target.closest('button.sb-ref');
      if (!button || !root.contains(button)) return;
      const target = root.querySelector('#' + CSS.escape(button.dataset.ref));
      if (!target) return;
      target.open = true;
      const summary = target.querySelector('summary');
      if (summary) {
        summary.focus({preventScroll: true});
        summary.scrollIntoView({block: 'nearest'});
      }
    });
    return root;
  }

  function updateLive(root, live) {
    const set = (key, text) => {
      const node = root.querySelector('[data-live="' + key + '"]');
      if (node && node.textContent !== text) node.textContent = text;
    };
    set('name', plain(live.name));
    const subtitle = root.querySelector('[data-live="subtitle"]');
    if (subtitle) set('subtitle', [live.species, subtitle.dataset.sourceSubtitle].filter(Boolean).join(' — '));
    set('ac', plain(live.ac));
    set('hp', plain(live.hp) + ' / ' + plain(live.max_hp));
    set('initiative_bonus', signed(live.initiative_bonus));
    for (const node of root.querySelectorAll('[data-species]')) {
      const text = live.species || node.dataset.species || '';
      if (node.textContent !== text) node.textContent = text;
    }
  }

  window.ScryingStatblock = {render, updateLive, safeUrl};
})();
