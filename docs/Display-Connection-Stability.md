# Display connection stability and in-place reconnection

Documented baseline: `features/development` at `4f401b4adfca92e9c9599aea8924c14efb49aea4`.

Both applications retain separate ports and sessions. The connection manager preserves the last rendered screen while it reconnects.

## Changes

- Reconnect the WebSocket in place; no page reload on ordinary disconnection.
- Keep the last successfully rendered encounter/campaign display visible while disconnected.
- Skip rendering an identical initial snapshot after reconnect, avoiding image/card rebuilds.
- One bounded retry timer with exponential backoff (1, 2, 4, 8, 16, 30 seconds, plus small jitter).
- Reset backoff only after receiving a valid state snapshot.
- Server sends application heartbeats on 15-second receive-idle intervals.
- Browser responds to incoming heartbeats immediately with PONG; no timer-driven client ping
  is needed for ordinary liveness.
- PONG and ACK are receive-only on the server, avoiding an accidental heartbeat-response loop.
- A delayed browser timer may show a warning but does not forcibly close an open socket.
- Server no longer disconnects solely because application ACK/PONG messages were delayed.
- Existing native WebSocket protocol keepalive/transport error detection remains under Uvicorn's
  configured WebSocket implementation; the implementation does not disable it or alter its settings.
- Visibility/online recovery requests a fresh state snapshot without recreating the page.
- Successful rendering is acknowledged as before; display connection status retains its meaning.
- Session revocation and same-origin checks remain. An unauthorized closed session is checked
  with the client-port /api/state and redirected to /login only on an actual 401.

A stale label is a last-contact metric, not a reason to disconnect. Browser/OS suspension can still
prevent any JS from running or freeze the tab entirely. No patch can guarantee uninterrupted
connections through a suspended device or a failed transport. Resume/reconnect will resynchronize.

## Diagnostics

The server now logs:

    Display WebSocket closed: code=... reason=... user=...
    Display WebSocket send timed out: user=...

The browser Console also logs the close code, reason and clean-close flag. These lines are more
useful than accepted/open alone for identifying recurring faults. A real reconnect still creates
an accepted/open entry in Uvicorn; the page and unchanged encounter stage should no longer flash.
Send timeouts remain enforced so a stalled client does not hold application locks indefinitely.

## Checks

```bash
python -m unittest discover -s tests -p 'test_display_connection.py'
node tests/test_display_reconnect.js
```

After code changes restart the server and reload existing viewer tabs. Test idle tabs, offline/online transitions, server restart and revoked sessions with your actual proxy/browser. Sessions are cleared on restart, so resynchronization may require login. The admin marks a socket stale after over 35 seconds without recorded contact; this is a status label, not an inactivity-disconnect policy.
