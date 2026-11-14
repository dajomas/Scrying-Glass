CLIENT_HTML = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Scrying Glass</title>
  <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
  <link rel="stylesheet" href="/static/glass-theme.css?v=1">
  <link rel="stylesheet" href="/static/client.css?v=2">
  <link rel="stylesheet" href="/static/viewer-campaigns.css">
</head>
<body>
  <header class="client-toolbar" aria-label="Campaign and display status">
    <button id="clientCampaign" type="button" aria-live="polite" aria-haspopup="dialog" disabled>Campaign: …</button>
    <span id="displaySync" role="status" aria-live="polite">Connecting…</span>
    <form action="/logout" method="post">
      <button id="clientLogout" type="submit">Log out</button>
    </form>
  </header>
  <main>
    <h1 class="sg-visually-hidden">Scrying Glass display</h1>
    <div id="initiative"></div>
    <div id="stage"></div>
  </main>

  <script src="/static/viewer-campaigns.js" defer></script>
  <script src="/static/client.js?v=2" defer></script>
</body>
</html>'''