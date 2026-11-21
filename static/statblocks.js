/* Statblock listener viewer: tiles, one expanded statblock, keyboard and live updates
 * (SG-TODO-022.10-022.12). Needs statblocks-render.js.
 *
 * - Tiles follow the server's logical membership and monster order; each
 *   monster instance is its own tile, bordered in its configured colour.
 * - At most one tile is expanded. Its heading button (click, Enter or Space)
 *   expands or collapses it; another tile replaces it. Escape collapses and
 *   returns focus to the tile. Text, scrolling, links and reference controls
 *   inside the statblock never collapse it.
 * - Arrow keys move between tiles by their on-screen rows (any grid width,
 *   incomplete last rows); Home/End go to the first/last tile. One tile is in
 *   the tab order (roving tabindex).
 * - Live frames update names, species, colours and the six values in place;
 *   a statblock is fetched only for the expanded tile and only when its
 *   revision is new (cached by revision; stale responses are ignored).
 * - Revocation, sign-out or a campaign/encounter change clears all content.
 */
(() => {
  'use strict';
  const render = () => window.ScryingStatblock;
  const STATUS = {
    available: '', partial: 'Partial', missing: 'No statblock', loading: 'Loading…',
    unavailable: 'Unavailable', error: 'Load failed',
  };

  function start(doc) {
    const statusLine = doc.getElementById('status');
    const grid = doc.getElementById('tiles');
    const tiles = new Map();
    const cache = new Map();
    let key = null, expanded = null, current = null, socket = null, retry = 1000, sequence = 0, closed = false;

    function say(text) { if (statusLine.textContent !== text) statusLine.textContent = text; }

    function reset(text) {
      tiles.clear(); cache.clear(); expanded = null; current = null; key = null; sequence++;
      grid.replaceChildren();
      say(text);
    }

    function toggles() { return [...grid.querySelectorAll('.sb-toggle')]; }

    function rove(target) {
      for (const button of toggles()) button.tabIndex = button === target ? 0 : -1;
    }

    function detail(summary) {
      const extra = summary.status_detail || {};
      const words = {
        missing: 'No statblock is saved for this monster.',
        loading: 'Loading the original statblock…',
        unavailable: 'The original statblock is unavailable' + (extra.message ? ': ' + extra.message : '.'),
        error: 'The original statblock could not be loaded' + (extra.message ? ': ' + extra.message : '.') +
          (extra.retry_at ? ' Retry after ' + new Date(extra.retry_at).toLocaleTimeString() + '.' : ''),
      };
      return words[summary.status] || '';
    }

    function makeTile(summary) {
      const id = summary.monster_id;
      const panelId = 'sb-panel-' + String(id).replace(/[^A-Za-z0-9_-]/g, '_');
      const item = doc.createElement('li');
      item.className = 'sb-tile';
      item.dataset.id = id;
      const heading = doc.createElement('h2');
      heading.className = 'sb-tile-heading';
      const button = doc.createElement('button');
      button.type = 'button';
      button.className = 'sb-toggle';
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-controls', panelId);
      button.tabIndex = -1;
      const name = doc.createElement('span'); name.className = 'sb-name';
      const species = doc.createElement('span'); species.className = 'sb-species';
      const badge = doc.createElement('span'); badge.className = 'sb-badge';
      button.append(name, species, badge);
      heading.append(button);
      const panel = doc.createElement('div');
      panel.className = 'sb-panel'; panel.id = panelId; panel.hidden = true;
      panel.setAttribute('role', 'region');
      item.append(heading, panel);
      button.addEventListener('click', () => toggle(id));
      button.addEventListener('focus', () => rove(button));
      const tile = {id, item, button, name, species, badge, panel, summary};
      tiles.set(id, tile);
      return tile;
    }

    function paint(tile, summary) {
      tile.summary = summary;
      const text = (value) => (value === null || value === undefined ? '' : String(value));
      if (tile.name.textContent !== text(summary.name)) tile.name.textContent = text(summary.name);
      const species = summary.species && summary.species !== summary.name ? summary.species : '';
      if (tile.species.textContent !== species) tile.species.textContent = species;
      const badge = STATUS[summary.status] === undefined ? summary.status : STATUS[summary.status];
      if (tile.badge.textContent !== badge) tile.badge.textContent = badge;
      tile.badge.hidden = !badge;
      tile.item.dataset.status = summary.status;
      tile.item.style.setProperty('--sb-tile-color', typeof summary.color === 'string' ? summary.color : '');
      tile.panel.setAttribute('aria-label', 'Statblock: ' + text(summary.name));
    }

    function live(summary) {
      return {name: summary.name, species: summary.species, ac: summary.ac, hp: summary.hp,
              max_hp: summary.max_hp, initiative_bonus: summary.initiative_bonus};
    }

    function message(tile, text, retryable) {
      const note = doc.createElement('p');
      note.className = 'sb-note';
      note.textContent = text;
      const nodes = [note];
      if (retryable) {
        const again = doc.createElement('button');
        again.type = 'button'; again.className = 'sb-retry'; again.textContent = 'Retry';
        again.addEventListener('click', () => { cache.delete(tile.id); show(tile, true); });
        nodes.push(again);
      }
      tile.panel.replaceChildren(...nodes);
      tile.view = null;
    }

    function draw(tile, entry) {
      const view = render().render(entry.statblock, live(tile.summary), {prefix: tile.panel.id + '-'});
      tile.panel.replaceChildren(view);
      tile.view = view;
      tile.shown = entry.revision;
    }

    async function show(tile, force) {
      const summary = tile.summary;
      if (!summary.statblock_revision) {
        message(tile, detail(summary) || 'No statblock is saved for this monster.', false);
        tile.shown = 0;
        return;
      }
      const cached = cache.get(tile.id);
      if (cached && cached.revision === summary.statblock_revision && !force) {
        if (tile.shown !== cached.revision || !tile.view) draw(tile, cached);
        else render().updateLive(tile.view, live(summary));
        return;
      }
      if (tile.fetching === summary.statblock_revision && !force) return;
      tile.fetching = summary.statblock_revision;
      if (!tile.view) message(tile, 'Loading statblock…', false);
      const ticket = ++sequence, wanted = key;
      const known = cached ? '?known_revision=' + cached.revision : '';
      let response, body;
      try {
        response = await fetch('/api/statblocks/monsters/' + encodeURIComponent(tile.id) + known,
          {credentials: 'same-origin', cache: 'no-store', headers: {Accept: 'application/json'}});
        body = await response.json();
      } catch (error) {
        response = null;
      }
      if (tile.fetching === summary.statblock_revision) tile.fetching = null;
      if (ticket !== sequence || wanted !== key || expanded !== tile.id || !tiles.has(tile.id)) return;
      if (response && (response.status === 401 || response.status === 403)) {
        reset((body && body.message) || 'Access ended. Reload to sign in again.');
        return;
      }
      if (!response || !response.ok || !body) {
        message(tile, (body && body.message) || 'The statblock could not be loaded.', true);
        return;
      }
      if (body.encounter_token !== key.split('\u0000')[1]) return;
      if (body.unchanged && cached) {
        draw(tile, cached);
      } else if (body.statblock) {
        const entry = {revision: body.statblock_revision, statblock: body.statblock};
        cache.set(tile.id, entry);
        draw(tile, entry);
      } else {
        cache.delete(tile.id);
        message(tile, detail(Object.assign({}, tile.summary, {status: body.status, status_detail: body.status_detail})) ||
          'No statblock is saved for this monster.', false);
      }
      if (tile.summary.statblock_revision !== tile.shown && expanded === tile.id) show(tile);
    }

    function collapse(focus) {
      const tile = tiles.get(expanded);
      expanded = null;
      if (!tile) return;
      tile.item.classList.remove('sb-expanded');
      tile.button.setAttribute('aria-expanded', 'false');
      tile.panel.hidden = true;
      tile.panel.replaceChildren();
      tile.view = null; tile.shown = null;
      if (focus) { rove(tile.button); tile.button.focus(); }
    }

    function toggle(id) {
      if (expanded === id) { collapse(true); return; }
      collapse(false);
      const tile = tiles.get(id);
      if (!tile) return;
      expanded = id;
      tile.item.classList.add('sb-expanded');
      tile.button.setAttribute('aria-expanded', 'true');
      tile.panel.hidden = false;
      rove(tile.button);
      show(tile);
    }

    function apply(state) {
      const next = state.campaign_id + '\u0000' + state.encounter_token;
      if (key !== null && key !== next) reset('');
      key = next; current = state;
      const active = doc.activeElement;
      const focusedIndex = toggles().findIndex((button) => button === active || button.parentNode.parentNode.contains(active));
      const wanted = new Set(state.tiles.map((summary) => summary.monster_id));
      for (const [id, tile] of [...tiles]) {
        if (wanted.has(id)) continue;
        if (expanded === id) expanded = null;
        tile.item.remove(); tiles.delete(id); cache.delete(id);
      }
      let previous = null;
      for (const summary of state.tiles) {
        const tile = tiles.get(summary.monster_id) || makeTile(summary);
        paint(tile, summary);
        const position = previous ? previous.item.nextSibling : grid.firstChild;
        if (position !== tile.item) grid.insertBefore(tile.item, position);
        previous = tile;
      }
      const buttons = toggles();
      if (!buttons.some((button) => button.tabIndex === 0) && buttons.length) rove(buttons[0]);
      if (focusedIndex >= 0 && !grid.contains(doc.activeElement) && buttons.length) {
        const target = buttons[Math.min(focusedIndex, buttons.length - 1)];
        rove(target); target.focus();
      }
      if (expanded !== null) show(tiles.get(expanded));
      say(state.tiles.length ? state.tiles.length + (state.tiles.length === 1 ? ' monster' : ' monsters') + ' in battle.'
                             : 'No monsters in battle.');
    }

    function neighbour(button, direction) {
      const buttons = toggles();
      const index = buttons.indexOf(button);
      if (index < 0) return null;
      if (direction === 'ArrowRight') return buttons[index + 1] || null;
      if (direction === 'ArrowLeft') return buttons[index - 1] || null;
      if (direction === 'Home') return buttons[0];
      if (direction === 'End') return buttons[buttons.length - 1];
      const box = (b) => b.closest('.sb-tile').getBoundingClientRect();
      const here = box(button), centre = here.left + here.width / 2;
      const down = direction === 'ArrowDown';
      const rows = buttons.map((b) => ({b, r: box(b)}))
        .filter(({r}) => (down ? r.top >= here.bottom - 1 : r.bottom <= here.top + 1));
      if (!rows.length) return null;
      const edge = down ? Math.min(...rows.map(({r}) => r.top)) : Math.max(...rows.map(({r}) => r.top));
      const row = rows.filter(({r}) => Math.abs(r.top - edge) < 2);
      row.sort((a, b) => Math.abs(a.r.left + a.r.width / 2 - centre) - Math.abs(b.r.left + b.r.width / 2 - centre));
      return row[0].b;
    }

    grid.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && expanded !== null) {
        event.preventDefault();
        collapse(true);
        return;
      }
      const button = event.target.closest && event.target.closest('.sb-toggle');
      if (!button || !['ArrowRight', 'ArrowLeft', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) return;
      const target = neighbour(button, event.key);
      event.preventDefault();
      if (target) { rove(target); target.focus(); }
    });

    function connect() {
      if (closed) return;
      const scheme = location.protocol === 'https:' ? 'wss://' : 'ws://';
      socket = new WebSocket(scheme + location.host + '/ws');
      socket.onopen = () => { retry = 1000; };
      socket.onmessage = (event) => {
        let data;
        try { data = JSON.parse(event.data); } catch (error) { return; }
        if (data.type === 'state' && data.state) apply(data.state);
        else if (data.type === 'revoked') reset(data.message || 'Access ended.');
      };
      socket.onclose = (event) => {
        if (event.code === 1008) {
          closed = true;
          reset('Signed out or no access to the active campaign. Reload to sign in again.');
          return;
        }
        say('Connection lost; reconnecting…');
        setTimeout(connect, retry);
        retry = Math.min(retry * 2, 30000);
      };
    }

    say('Connecting…');
    return {apply, reset, connect, toggle, collapse, state: () => ({expanded, key, current, cache, tiles})};
  }

  window.ScryingStatblockViewer = {start};
  if (document.getElementById('tiles') && document.body.dataset.autostart !== 'false') {
    start(document).connect();
  }
})();
