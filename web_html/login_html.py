LOGIN = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Sign in — Scrying Glass</title>
  <link rel="icon" href="/static/favicon.ico" type="image/x-icon">
  <link rel="stylesheet" href="/static/login.css">
</head>
<body>
  <form method="post">
    <h1>Scrying Glass</h1>

    <input
      name="username"
      placeholder="Username"
      required
      autofocus
    >

    <input
      name="password"
      type="password"
      placeholder="Password"
      required
    >

    <button>Sign in</button>

    {error}
  </form>
</body>
</html>'''
