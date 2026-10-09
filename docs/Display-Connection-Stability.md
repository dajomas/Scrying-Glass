# Display connection stability and in-place reconnection

This overlay requires the earlier Encounter features and client campaign-label patch. It replaces
only python/scrying_glass_api_client.py and static/client.js. Backend state/damage/undo logic,
client toolbar/campaign/effect styling, both ports and authentication-cookie separation are retained.

## What caused the visible flash

The prior browser reconnect path called location.reload(), recreating the entire page whenever
a WebSocket closed. That was a direct cause of the screen flash. It also used a JavaScript timer
to close apparently stale sockets after a fixed silence period, while the server enforced a
separate application-message inactivity cutoff. Delayed/suspended browser JavaScript can trigger
those policies even when the underlying connection is otherwise viable.

The posted accepted/open messages establish reconnection, not the reason for the earlier close.
Timer delay is a plausible trigger, not a confirmed diagnosis of every connection loss. Network,
proxy, event-loop stalls, process restart and actual socket failures can still cause disconnects.

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
  configured WebSocket implementation; this patch does not disable it or alter its settings.
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

## Install

1. Stop the service and back up the two replacement files.
2. Extract the ZIP at the application root, retaining paths.
3. Restart Scrying Glass and hard-refresh the CLIENT page once to load the new code.
4. Leave the viewer idle, switch tabs, return, and verify connection/status behaviour.
5. Temporarily stop/restart the server and verify that the last screen is retained and later
   updates arrive without a page reload. Check sign-out/revocation still returns to login.

No database/schema/template change is included. Retain earlier client HTML/CSS and state service,
which provide campaign names, safe effect payloads and the status label used here.

## Validation

11 Python tests exercised the actual replacement ws function with a fake transport and real
asyncio locks: initial snapshot, no ACK/PONG reply loop, idle heartbeat without forced inactivity
close, ping, resync, invalid JSON, oversized messages, origins, missing/revoked sessions and cleanup.
8 Node tests exercised the actual connection manager with fake sockets/timers: in-place reconnect,
unchanged snapshot suppression, changed snapshots, PONG replies, delayed timers without closure,
resync, single pending retry, visibility resume and cleanup.
Python/JS syntax checks and ZIP integrity passed. These are targeted protocol/state-machine tests,
not a live browser/HTTP/WebSocket/proxy integration test. The full feature suite was not rerun.

    python -m unittest discover -s tests -p 'test_display_connection.py'
    node tests/test_display_reconnect.js

Rollback: restore the two prior replacement files and restart/hard-refresh. No DB rollback.
