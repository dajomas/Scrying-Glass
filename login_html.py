LOGIN = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Sign in</title>

  <style>
    body {
      font-family: system-ui, sans-serif;
      background: #111827;
      color: #eef2ff;
      display: grid;
      place-items: center;
      height: 100vh;
      margin: 0;
    }

    form {
      background: #1f2937;
      padding: 2rem;
      border-radius: 12px;
      display: grid;
      gap: .7rem;
      width: min(360px, 90vw);
    }

    input,
    button {
      padding: .7rem;
      border-radius: 6px;
      border: 0;
    }

    button {
      background: #2563eb;
      color: #fff;
      cursor: pointer;
    }

    .error {
      color: #fca5a5;
    }
  </style>
</head>
<body>
  <form method="post">
    <h1>Monster Display</h1>

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
