"""Statblock listener page shell (SG-TODO-022.09).

Connection, campaign and membership states only: tiles and complete statblocks
are rendered in 022.10-022.12. Text is set with textContent, never as HTML;
on revocation or a campaign change all shown content is cleared.
"""

STATBLOCK_HTML = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Statblocks — Scrying Glass</title>
  <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
  <link rel="stylesheet" href="/static/glass-theme.css?v=1">
</head>
<body>
  <header>
    <h1>Statblocks</h1>
    <form method="post" action="/logout"><button>Sign out</button></form>
  </header>
  <main>
    <p id="status" role="status" aria-live="polite">Connecting…</p>
    <ul id="tiles" aria-label="Monsters in battle"></ul>
  </main>
  <script>
  (() => {
    const status = document.getElementById('status');
    const tiles = document.getElementById('tiles');
    let campaign = null, socket = null, retry = 1000;
    function clear(text) { tiles.replaceChildren(); status.textContent = text; }
    function render(state) {
      if (campaign !== null && state.campaign_id !== campaign) tiles.replaceChildren();
      campaign = state.campaign_id;
      const rows = state.tiles.map((tile) => {
        const item = document.createElement('li');
        item.textContent = tile.name + (tile.species ? ' (' + tile.species + ')' : '') + ' — ' + tile.status;
        if (typeof tile.color === 'string') item.style.borderLeft = '0.5rem solid ' + tile.color;
        return item;
      });
      tiles.replaceChildren(...rows);
      status.textContent = rows.length ? rows.length + ' monster(s) in battle' : 'No monsters in battle.';
    }
    function connect() {
      const scheme = location.protocol === 'https:' ? 'wss://' : 'ws://';
      socket = new WebSocket(scheme + location.host + '/ws');
      socket.onopen = () => { retry = 1000; };
      socket.onmessage = (event) => {
        let message;
        try { message = JSON.parse(event.data); } catch (error) { return; }
        if (message.type === 'state') render(message.state);
        else if (message.type === 'revoked') { campaign = null; clear(message.message || 'Access ended.'); }
      };
      socket.onclose = (event) => {
        if (event.code === 1008) { campaign = null; clear('Signed out or no access. Reload to sign in again.'); return; }
        status.textContent = 'Connection lost; reconnecting…';
        setTimeout(connect, retry); retry = Math.min(retry * 2, 30000);
      };
    }
    connect();
  })();
  </script>
</body>
</html>'''
