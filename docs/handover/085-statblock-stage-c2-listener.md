# 085 - SG-TODO-022 Stage C2: protected statblock listener and read transport (022.09)

[Back to handover index](../../HANDOVER.md) · [Stage C1](084-statblock-stage-c1-import-apis.md) · [TODO 220](../todo/220-admin-statblock-viewer.md)

Date: 2026-11-17. Baseline: `ace9a5176e7bce2f9e90a9523e513c503d4c0930` (Stage C1) on
`features/claude-statblock`. Delivered as a zip archive; commit SHA not yet known.
CI not run (`[skip ci]`, agreed for Stages A-E until the last code delivery).
The user asked for "Stage C2" after C1 was pushed, consistent with the C1 = 022.08 /
C2 = 022.09 reading in [084](084-statblock-stage-c1-import-apis.md).

## Delivered

- A third FastAPI application, `statblock_app` in `scrying_glass_server.py`, served
  with the Admin and Client Display apps in one `asyncio.gather` (shared start-up,
  storage and shutdown; shutdown also stops the preparation scheduler).
  Configuration `network.statblock_port` (default **3200**), CLI `--statblock-port`.
- `scrying_glass_statblock_viewer_app.py`: `GET /` (page), `GET/POST /login`,
  `POST /logout`, `GET /api/statblocks/state`, `GET /api/statblocks/monsters/{id}`
  (the C1 read handlers, mounted read-only) and WebSocket `/ws`. Own cookie
  `scrying_glass_statblock_session` (HttpOnly, SameSite=Strict). Only `/static` is
  mounted (login/page styles); no `/media`, no import routes.
- Sign-in accepts only regular admins; superadmin and client accounts get the login
  page with an explanation and no session. Page, reads and every WebSocket frame
  also require a live session and assignment to the active campaign.
- `scrying_glass_statblock_transport.py`: private update transport. Each committed
  change (`broadcast`) sends every statblock socket its own projection (tiles,
  revisions, encounter token; no statblock content) after authorizing it again;
  an unauthorized socket gets `{"type": "revoked", code, message}` and is closed
  with 1008. Heartbeats every 15 s also recheck access, so session expiry, role or
  ownership changes and a campaign switch to an unassigned campaign end access
  without a page reload. Statblock sockets are kept apart from `SOCKETS`: display
  frames never reach them and their frames never reach Client Displays.
- Logout on any interface closes that session's statblock sockets and releases its
  C1 references.
- Page shell `web_html/statblock_html.py`: connection, empty and revoked states and a
  plain list of tile names/species/status (textContent only). It clears everything
  on revocation or campaign change. Real tiles/statblocks are 022.10-022.12.
- Port preflight (`scrying_glass_port_check.py`): every listener port must be an
  integer 1-65535 and distinct (each duplicate combination is named) before any bind
  check; occupied ports are named per listener. Messages mention `--statblock-port`.
- e2e `Server` fixture gets a free statblock port. Docs: README, User Guide,
  technical 010, systemd guide (port 3200, `ss` check), `config.example.yaml`.

## Decisions

- The listener cannot be disabled; it always listens on its configured port. Treat it
  like the Admin port in firewall rules.
- Only regular admins may sign in at all (the contract requires regular-admin access
  for every page), rather than letting others sign in and see an error page.
- Sessions stay in the shared in-memory session table; restart clears them.

## Validation (Python 3.13.18, this environment)

- New `tests/test_statblock_listener.py` (8 tests: duplicate/invalid/occupied port
  combinations, defaults/CLI wiring, per-socket authorization, separation from
  display sockets, revocation on ownership/role/campaign change, logout): pass, with
  the C1 tests and the existing port, storage and feature tests.
- New `tests/test_statblock_listener_http.py` (4 FastAPI tests: sign-in roles, page and
  read cookies, read-only routes, WebSocket accept/refuse, logout): **not run** — FastAPI
  is not installed here.
- Whole-module regression comparison against `ace9a51`: see `Patch/` notes.
- Not run: CI, e2e (no browser here), a real three-port start-up (uvicorn/FastAPI
  missing), deployment on a host.

## Open work

- 022.10-022.12 (Stage D): tile and statblock rendering, keyboard/accessibility,
  live synchronization and original-source loading on this listener.
- Deployment guidance beyond the port notes (reverse proxy/TLS) remains with 022.15/16.
