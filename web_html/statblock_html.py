"""Statblock listener page (SG-TODO-022.10-022.12).

The page shell only: tiles and statblocks are built by /static/statblocks.js
and /static/statblocks-render.js from the private read API and WebSocket,
with DOM text nodes only. Sign-in and access checks are server-side.
"""

STATBLOCK_HTML = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Statblocks — Scrying Glass</title>
  <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
  <link rel="stylesheet" href="/static/glass-theme.css?v=1">
  <link rel="stylesheet" href="/static/statblocks.css?v=2">
</head>
<body class="sb-page">
  <header class="sb-page-header">
    <h1>Statblocks</h1>
    <form method="post" action="/logout"><button class="sb-signout">Sign out</button></form>
  </header>
  <main>
    <p id="status" class="sb-status" role="status" aria-live="polite">Connecting…</p>
    <ul id="tiles" class="sb-grid" aria-label="Monsters in battle"></ul>
  </main>
  <script src="/static/statblocks-render.js?v=2"></script>
  <script src="/static/statblocks.js?v=1"></script>
</body>
</html>'''
