CLIENT_HTML = r'''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Scrying Glass</title>
  <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
  <link rel="stylesheet" href="/static/client.css">
</head>
<body>
  <header class="client-toolbar" aria-label="Campaign and display status">
    <span id="clientCampaign" aria-live="polite">Campaign: …</span>
    <span id="displaySync" role="status" aria-live="polite">Connecting…</span>
    <form action="/logout" method="post">
      <button id="clientLogout" type="submit">Log out</button>
    </form>
  </header>
  <div id="initiative"></div>
  <div id="stage"></div>

  <script src="/static/client.js" defer></script>
</body>
</html>'''