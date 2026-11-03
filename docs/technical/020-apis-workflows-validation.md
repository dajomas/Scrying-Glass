# 020 - APIs, workflows and validation

[Back to technical documentation](../Technical-Documentation.md)

<!-- BEGIN preserved technical content -->
## HTTP route inventory

Paths are relative to the appropriate listener. Admin operations require admin/superadmin plus applicable campaign scope; account/ownership management requires superadmin.

### Core Admin

| Method | Path |
|---|---|
| GET, POST | /login |
| POST | /logout |
| GET | / |
| GET | /api/state |
| GET | /api/dndbeyond/monster-stats |
| POST | /api/display/battle-order-font |
| PATCH | /api/display/background |
| POST | /api/display/background-image |
| GET, POST | /api/campaigns |
| PATCH, DELETE | /api/campaigns/{campaign_id} |
| POST | /api/campaigns/{campaign_id}/activate |
| POST | /api/campaigns/{campaign_id}/setups |
| GET | /api/setups |
| POST | /api/setups/new |
| POST | /api/setups/save |
| POST | /api/setups/load |
| POST | /api/setups/rename |
| DELETE | /api/setups/{name} |
| POST | /api/setups/import |
| POST | /api/monsters/roll-initiative |
| POST | /api/monsters |
| POST | /api/monsters/import |
| POST | /api/monsters/import-csv |
| POST | /api/characters/import-csv |
| POST | /api/monsters/{ident}/edit |
| PATCH | /api/monsters/{ident} |
| POST | /api/characters |
| PATCH | /api/characters/{ident} |
| DELETE | /api/combatants/{ident} |
| POST | /api/combatants/{ident}/reset |
| POST | /api/characters/bulk |
| POST | /api/monsters/bulk |
| POST | /api/battle/start |
| POST | /api/battle/next |
| POST | /api/battle/end |
| POST | /api/battle/reset-all |
| POST | /api/battle/actions |
| GET | /api/activity-log.json |
| GET | /api/activity-log.csv |
| POST | /api/activity-log/clear |

### Accounts, ownership and grants

| Method | Path |
|---|---|
| GET | /api/me |
| GET | /users |
| GET, POST | /api/users |
| PATCH, DELETE | /api/users/{user_id} |
| GET | /api/campaign-ownership |
| PUT | /api/campaign-ownership/{campaign_id} |
| GET, PUT | /api/campaigns/{campaign_id}/viewers |

/api/me accepts admin/superadmin. Viewer grant routes require a permitted administrator. User APIs accept username, role, password only; PATCH omits password to preserve it, explicit empty/null is invalid. Errors: 401 unauthenticated, 403 denied, 404 unknown user, 409 duplicate/last-superadmin conflict, 422 validation.

### Features and lairs

| Method | Path |
|---|---|
| GET | /api/features |
| POST | /api/battle/undo |
| PATCH | /api/combatants/{ident}/features |
| POST | /api/combatants/{ident}/effects |
| DELETE | /api/combatants/{ident}/effects/{effect_id} |
| POST | /api/combatants/{ident}/concentration/end |
| POST | /api/checkpoints |
| GET, DELETE | /api/checkpoints/{ident} |
| POST | /api/checkpoints/{ident}/restore |
| GET, POST | /api/campaign-bundle |
| POST | /api/lairs |
| PATCH, DELETE | /api/lairs/{ident} |
| POST | /api/lairs/{ident}/actions |

Client exposes GET /, GET/POST /login, GET /display, GET /api/state, POST /logout and WebSocket /ws. Both apps mount /static and /media.

## Request contracts

- Setups use name and optional campaign ID; rename adds new_name. Import is monsters-only with life_filter=alive|dead|all.
- Monster creation multipart: name, monster_species, ac, hprangestart, optional hprangeend, color, quantity 1–50, optional image.
- CSV field csv_file; statblock field monster_file; bundle field file.
- Bulk: action and ids. Battle start: order. Action rows: actor_id plus targets/actions/amounts, optional source_id reactions and critical_hit damage.
- Background: background; image upload: image. Font: direction increase/decrease, 2 px steps, 12–40.
- Undo: current top id plus fingerprint validation. Checkpoint restore: confirm=true and current preview revision. Lair actions: name, current revision and target rows.

Consult request classes, domain handlers and running OpenAPI for exact schemas. This inventory is not a replacement for model validation.

## Health, turns, recovery and logging

Standing and future-turn eligibility are separate. Active down/stable characters retain manual death-save turns; dead characters and non-standing monsters are excluded from future turns. Unresolved current turn can remain after death. Remembered successors preserve next-turn and round boundary when a current participant disappears.

Round begins 1, increments on wrap, clears on End/reset/no eligible participants. Runtime restores authoritative turn only if valid. Creature joining requires integer initiative; zero/negative valid. Clearing while active is blocked unless deactivated simultaneously.

Actions validate together and apply sequentially. Ordinary actor must stand; reaction damage/healing permits independent active down/dead sources/targets. Shared rules absorb temporary HP, clamp HP, cap healing and calculate excess damage/death failures. Absolute corrections are not attacks. Critical-hit flag changes failures, not damage magnitude.

Effects use private/public names, optional concentration and start/end anchor occurrences. Manual turn assignment does not consume counters. One lair per encounter sits after creatures tied at 20 and uses revision-bound action batches.

Undo is bounded to 30 supported operations; checkpoints to 50 per campaign. Boundaries/unsupported operations clear history. Audit history is retained with recovery events. Bundle format/limits and health/lair workflows are consolidated in the User Guide.

Clear log removes runtime and associated saved-setup logs without persisting unrelated edits. CSV neutralizes formula-like text; JSON preserves it.

## Player state and WebSockets

Client HTTP and sockets use a campaign-authorized filtered display projection, not full Admin state. State envelopes are {"type":"state","state":...}.

Player data includes appropriate active monsters, visible characters/lairs, campaign identity, public effect names, life/turn flags, display, round and filtered order. Character stats, logs, setup references and private effect fields are omitted. Monster AC/HP/max HP/temp HP follow visibility; hidden initiative is null. Relative ordering can still disclose relative initiative. display_order adds visible participants absent from battle_order using server initiative sorting.

Broadcast snapshots use a separate lock and concurrent sends. Documented send timeout is 2 seconds, cleanup 0.5 seconds. Initial registration locks and rechecks sessions. Application heartbeats start after 15 seconds without incoming messages; ACK/PONG/resync track revisions. Missing application replies alone do not close viable transport. Browser reconnects with bounded backoff, keeps the last scene and skips identical snapshots.

## Persistent action/reaction modal

`static/admin.js` tracks submission activity with `battleActionsApplying` and row
completion with `data-applied="true"`. The form collects only pending
`.battle-action-row` elements in DOM order, preserving optional reaction source,
target, amount and damage-only critical-hit payloads. Native form validation still
runs before submission; disabled applied controls do not participate in validation.

A successful POST marks its captured rows applied before calling `load(true)`.
Each resolved row gets an Applied label, and all its controls remain disabled.
The modal remains open and retains the turn owner. New rows can then be added
and submitted without replaying history. An empty pending batch makes no POST.
The API contract, backend validation and database schema are unchanged.

During a batch, controls in both modal forms are disabled and their original disabled
states are captured. The finally block restores those states except for resolved
row controls, clears `aria-busy`, and releases the submission guard. Add/open/close
handlers also check the guard, preventing backdrop closure or draft replacement
while awaiting the POST and refresh. Start-of-turn submission retains its separate
handler and existing reset behavior.

`load(rethrowErrors = false)` preserves existing callers' error handling. The new
`load(true)` opt-in propagates refresh errors to the action handler, which reports
that changes were already applied without clearing completion markers. Ordinary
POST failures keep rows pending and restore controls. Completion is local to this
open modal, not persisted server-side: ambiguous network failures require checking
state/logs before retry, and reopening or another tab does not deduplicate requests.

`templates/admin/180_battle_action_modal.html` replaces Cancel with explicit Close
and includes an aria-live status notice. Close/backdrop discard pending drafts but
never undo previously submitted changes. `static/battle-turn-actions.css` styles
the Applied label and resolved-row border.

Focused checks (dependency-free Node mocks, not a real browser):

```bash
node --check static/admin.js
node tests/battle-action-apply.test.cjs
node tests/battle-action-selection.test.cjs
node tests/battle-reactions.test.cjs
node tests/battle-turn-actions.test.cjs
python -m pytest -q tests/test_battle_reactions.py tests/test_turn_eligibility.py
```

## Initiative tie regression fixtures

`tests/initiative-tie-defaults.test.cjs` exercises the actual `tieUI()` renderer
in a Node VM with only its data dependencies (`latest`, `tiedBuckets`, `esc`).
The source slice ends at `function swapTiePosition(`, not `readTieOrder()`:
the latter also includes the browser-only `#tieGroups` event registration and
therefore raises `document is not defined` in this intentionally DOM-free fixture.
Extraction asserts both function boundaries to diagnose later source layout changes.
Do not add a fake document merely to execute unrelated initialization.

The rendered-select parser allows attributes after `data-tie-member`, including
`data-tie-position`. The old expression required the ID attribute to end the
opening select tag and returned no matches once position tracking was added.
The fixture verifies one selected numeric position per select and the expected
combatant count, avoiding silent success when markup matching fails.

Coverage includes stable character-first ordering, homogeneous ties, empty ties,
independent one-based positions for multiple buckets, input immutability (including
frozen inputs), trailing attributes, invalid selected-option markup, DOM-free
extraction and explicit missing-boundary errors. The existing swap fixture checks
manual overrides, repeated swaps and bucket isolation. Runtime initiative behavior
is unchanged; these are test-harness fixes, not a combat-order change.

```bash
node --test tests/initiative-tie-defaults.test.cjs tests/initiative-tie-swap.test.cjs
node --test tests/*.test.cjs
```

The wildcard command covers that filename group only, not every JavaScript file
in tests or the Python/browser/HTTP suites. See
[the patch validation record](../../Patch/Deployment-Validation.md) for executed
results and investigation details.

## HTML, caching and validation

Admin HTML is concatenated from ordered UTF-8 fragments at import; restart after edits. This is not Jinja. Keep DOM IDs synchronized with scripts. HTML middleware rewrites local assets with per-response _cb tokens and no-cache; protected APIs use no-store. Existing tabs need reload.

```bash
.venv/bin/python -m compileall -q scrying_glass_server.py python web_html
.venv/bin/python -c "import sqlite3; import scrying_glass_server"
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
node --check static/client.js
node --check static/features.js
node --check static/campaign-viewer-admin.js
node --check static/initiative-join-gate.js
node tests/test_display_reconnect.js
node --test tests/initiative-join-gate.test.cjs
```

Browser tests can require Playwright/Chromium. Some tests use direct handlers, substitutions or mocked APIs, not real HTTP authentication. Validate actual lifespans, both logins, cross-owner denial, grants/revocation, imports, health/reactions/effects, restart recovery, checkpoint/bundle/media, lairs, rounds and proxy WebSockets on copied data.

These are validation instructions, not claims that this documentation build executed the application suite.

## 5e.tools monster fallback

Optional monster suggestions now try D&D Beyond first, then 5e.tools JSON data.
AC accepts numeric entries and AC objects; HP prefers a supported dice formula
and falls back to the numeric average. Names match exactly after case and
punctuation normalization. The UI labels the provider and source. Existing
AC/HP overwrite and in-flight edit protection are unchanged.

Image lookup follows the same provider order when creating a monster without an
uploaded image. 5etools supplies a token URL (explicit `tokenUrl` or a generated
WebP token path when `hasToken` is set), not necessarily a full illustration.
Existing monsters' images are not retroactively updated. Image URLs are remote;
they are not downloaded or cached locally, and availability is not probed.

Configuration under `display`:
```yaml
fivetools_fallback: true
fivetools_sources: ["MM", "XMM"]
fivetools_data_base_url: "https://5e.tools/data/bestiary"
fivetools_image_base_url: "https://5e.tools/img"
```

MM is tried before XMM to retain the older-edition preference. Only configured
sources are searched: add source identifiers from the bestiary index to extend
coverage. D&D Beyond and 5etools are independently controlled: disable both
`dndbeyond_image_lookup` and `fivetools_fallback` to prevent optional provider
lookups. No credentials are sent to 5etools. Remote JSON is bounded to 16 MB per
file, fetched with a five-second socket timeout, and cached in-process for one
hour with at most 32 entries. Restart clears the cache. Source files are loaded
sequentially; configured source count affects cold-lookup latency.

Unresolved `_copy` entries without their own usable values are skipped for stats;
this is not a complete implementation of 5etools inheritance. Special-only AC/HP
is not guessed. Fallback uses a single usable source entry and does not combine
missing fields across providers/editions. Browser access to remote token hosts
and server HTTPS access to data endpoints are required. Use third-party data
and images only where permitted; none are bundled with this patch.

Run offline tests from the repository root:
```bash
python -m unittest discover -s tests -p 'test_fivetools_fallback.py' -v
```

Live validation: enter Crawling Claw and check that the notification identifies
5e.tools after D&D Beyond fails. Add a monster without uploading an image and
check its token in the player view. If no result appears, inspect WARNING logs
and verify index/source URL reachability from the service account. Token paths
and live endpoints could not be verified from the patch-build environment.


<!-- END preserved technical content -->
