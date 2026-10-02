# Scrying Glass Technical Documentation

Scrying Glass is a single-process Python/FastAPI application for a game-master-controlled tabletop battle display. It runs separate Admin and Client FastAPI applications in one interpreter, keeps encounter state in shared memory, persists it as JSON, and broadcasts Client Display updates over WebSockets.

See the [README](../README.md) for installation and the [User Guide](User-Guide.md) for user-facing workflows.

## Source layout

```text
scrying_glass_server.py  # FastAPI apps, models, state, persistence, rules, routes, startup
admin_html.py             # Admin HTML document template
client_html.py            # Client Display HTML document template
login_html.py             # Shared login HTML template
static/
├── admin.css             # Admin styles
├── admin.js              # Admin state, rendering, dialogs, API interaction, selections
├── client.css            # Client Display styles
├── client.js             # Client rendering and WebSocket client
└── login.css             # Login styles
config.example.yaml       # Example deployment configuration
run.sh                    # Convenience launcher
```

HTML templates define document structure. Browser behavior belongs in the static JavaScript and CSS files, which the FastAPI applications serve as static assets.

## Runtime architecture

```text
Admin browser ── HTTP ──► Admin FastAPI app ── TCP 3000 by default
                                  │
                                  ├── shared STATE
                                  ├── shared SESSIONS
                                  ├── shared SOCKETS
                                  ├── async save lock
                                  └── state.json, campaigns.json, setups/<campaign>/, uploads/
                                  │
Client browser ── HTTP/WS ► Client FastAPI app ── TCP 4000 by default
```

Both apps share one process and one in-memory state model. Run exactly one worker and one service instance per storage directory. A multi-worker or multi-replica deployment requires external shared state, session storage, locking, and publish/subscribe synchronization before it is safe.

## Dependencies and configuration

Install dependencies:

```bash
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

Configuration can be YAML or JSON. Command-line values override matching file values.

```yaml
network:
  bind: "0.0.0.0"
  admin_port: 3000
  client_port: 4000

storage_dir: "./scrying-glass-data"

security:
  users:
    - username: "dm"
      role: "admin"
      password: "replace-this-admin-password"
    - username: "table"
      role: "client"
      password: "replace-this-client-password"

display:
  background: "#080b14"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  default_monster_color: "#842029"
  default_character_color: "#1f4e79"
  dndbeyond_image_lookup: true
```

| Key | Purpose |
|---|---|
| `network.bind` | Interface used by both HTTP services |
| `network.admin_port` | Admin listener; default 3000 |
| `network.client_port` | Client Display listener; default 4000 |
| `storage_dir` | Parent directory for state, campaigns, setups, and uploads |
| `security.users` | Username, role, and plaintext or scrypt password records |
| `display.background` | Fallback for legacy setup files and initial background for new setups |
| `display.entry_direction` | `from_bottom` or `from_top` |
| `display.exit_direction` | `to_bottom` or `to_top` |
| `display.monster_width_percent` | Display sizing configuration retained in public display state |
| `display.dndbeyond_image_lookup` | Enables optional remote image lookup |

Example:

```bash
python3.14 scrying_glass_server.py   --config /etc/scrying-glass/config.yaml   --bind 0.0.0.0   --admin-port 3000   --client-port 4000   --storage-dir /var/lib/scrying-glass
```

## Authentication

Login creates a `secrets.token_urlsafe(32)` token held in the in-memory session store. A session holds username and role.

| Application | Cookie |
|---|---|
| Admin | `scrying_glass_admin_session` |
| Client Display | `scrying_glass_client_session` |

Cookies are scoped by hostname instead of port. Separate cookie names therefore allow Admin and Client Display sessions in the same browser. Legacy cookie names are cleared after successful login.

Admin mutation routes require an Admin session. Client state routes and WebSocket connections require a Client cookie; Client login accepts both `client` and `admin` roles.

Passwords may be plaintext or use this format:

```text
scrypt$<salt_hex>$<digest_hex>
```

Generate a hash with:

```bash
python3.14 -c 'from scrying_glass_server import password_hash; print(password_hash("replace-me"))'
```

Sessions are lost when the process restarts.

## Persistence and campaigns

For `storage_dir: /var/lib/scrying-glass`:

```text
/var/lib/scrying-glass/
├── state.json
├── campaigns.json
├── uploads/
│   └── <uuid>.<extension>
└── setups/
    └── <campaign-slug>/
        └── <normalized-setup-name>.json
```

| Location | Purpose |
|---|---|
| `state.json` | Working encounter, battle order, activity log, and working display background |
| `campaigns.json` | Active campaign plus campaign metadata and most recently worked-on setup |
| `uploads/` | Uploaded Monster and setup-background images, mounted below `/media/` |
| `setups/<campaign-slug>/` | Named complete-state snapshots belonging to one campaign |

State and campaign data are written by temporary-file replacement. Campaign and setup names are normalized to lower-case safe slugs limited to 80 characters.

A campaign registry has this general shape:

```json
{
  "active": "curse-of-strahd",
  "campaigns": {
    "default": {
      "name": "Default",
      "description": "Battle setups that were not connected to a campaign",
      "created": "2026-09-29T06:00:05+00:00",
      "last_setup": "goblin-ambush",
      "last_setup_at": "2026-09-29T08:12:44+00:00"
    }
  }
}
```

At startup and during campaign/setup operations, migration detects `*.json` files directly inside the old `setups/` directory. It moves them into `setups/default/`, creates and registers Default as needed, resolves naming collisions with numeric suffixes, registers unlisted campaign folders, and ensures that an active campaign exists.

Each newly created campaign receives `default.json`, an empty normalized setup. Activating a campaign opens its recorded `last_setup` when present; otherwise it opens the most recently modified setup. If no setup exists, working state is left unchanged.

## State model

The normalized root state is:

```json
{
  "monsters": [],
  "characters": [],
  "battle_order": [],
  "activity_log": [],
  "display": {
    "background": "#080b14"
  }
}
```

`normalize_state()` fills fields absent from older state and setup files, initializes legacy setup backgrounds from configured fallback, and removes battle-order IDs that no longer identify an entity.

A Monster includes identity, display, combat, and Client-card fields:

```json
{
  "id": "uuid-hex",
  "name": "Ice Guard",
  "monster_species": "humanoid",
  "ac": 16,
  "hp": 45,
  "max_hp": 45,
  "original_hp": 45,
  "color": "#842029",
  "image_url": "/media/uuid.png",
  "active": false,
  "alive": true,
  "visible": false,
  "ally": false,
  "initiative": null,
  "original_initiative": null,
  "show_ac": false,
  "show_hp": false,
  "show_initiative": false,
  "in_turn": false
}
```

A Character uses the corresponding shared combat fields but no Monster image, type, AC, ally, or card-stat visibility fields.

`STATE.display.background` applies to the current working encounter and is saved into named setup snapshots. It accepts Client-supported CSS values, including colors and gradients. Uploaded backgrounds are represented as `url("/media/<uuid>.<extension>")`. The configured background is an initial or legacy fallback, not a replacement for an already saved per-setup background.

An Activity Log record includes an ID, ISO-8601 timestamp, actor and target identifiers/names/states, action, and optional amount. Valid actions are `damage`, `heal`, `buff`, and `debuff`; Buff and Debuff have a null amount.

## Synchronization and selections

Mutation handlers save and broadcast through `changed()`:

```python
async def changed() -> None:
    async with LOCK:
        save_state()
    await broadcast()
```

The Client fetches `/api/state` initially, then renders WebSocket state messages. The Admin page refreshes state after mutations.

Selected Monster and Character IDs are different: they are Admin-browser-only state maintained in `static/admin.js`. They are not part of `STATE`, `state.json`, campaign data, saved setup snapshots, or Client Display state.

| Event | Selection behavior |
|---|---|
| Select all | Replaces a pane selection with all current entities of that type |
| Unselect all | Clears that pane selection |
| Join, leave, visibility, display, or reset action | Keeps selected IDs that still exist |
| Remove action | Deleted IDs disappear on next state render |
| Setup load or campaign switch | Stale IDs are pruned because the loaded state has different entities |
| Monster selection action | Does not affect Character selection |
| Character selection action | Does not affect Monster selection |

The browser should prune stale IDs during render. Server-side selected-bulk operations must validate every submitted ID before mutating any combatant, so stale input fails without partially applying an action.

## API inventory

Unless stated otherwise, Admin mutation routes require an Admin session.

### Pages and live state

| App | Method | Path | Purpose |
|---|---|---|---|
| Admin | GET/POST | `/login` | Admin login |
| Admin | GET | `/` | Admin UI |
| Client | GET/POST | `/login` | Client or Admin login |
| Client | GET | `/display` | Client Display UI |
| Admin | GET | `/api/state` | Current state for Admin session |
| Client | GET | `/api/state` | Current state for Client session |
| Client | WebSocket | `/ws` | Authenticated Client live updates |

### Campaign and setup routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/campaigns` | Migrates/returns campaigns, active campaign, setup metadata, and moved legacy setups |
| POST | `/api/campaigns` | Creates campaign and empty `default` setup; may activate and open it |
| PATCH | `/api/campaigns/{slug}` | Renames or edits campaign metadata |
| DELETE | `/api/campaigns/{slug}` | Deletes campaign; moves or deletes setups as explicitly requested |
| POST | `/api/campaigns/{slug}/activate` | Activates campaign and opens selected preferred setup |
| POST | `/api/campaigns/{slug}/setups` | Moves or copies setup from another campaign |
| GET | `/api/setups` | Lists setups in active or supplied campaign |
| POST | `/api/setups/new` | Replaces working state with blank state |
| POST | `/api/setups/save` | Saves complete state under normalized name |
| POST | `/api/setups/load` | Replaces working state with snapshot |
| POST | `/api/setups/rename` | Renames saved setup |
| DELETE | `/api/setups/{name}` | Deletes setup and opens next or fresh default setup |
| POST | `/api/setups/import` | Appends runtime-reset copies from setup |

### Display and combatant routes

| Method | Path | Purpose |
|---|---|---|
| PATCH | `/api/display/background` | Updates working background and broadcasts it |
| POST | `/api/display/background-image` | Stores allowed image and assigns it as working background |
| POST | `/api/monsters` | Creates one or more Monsters from multipart form data |
| POST | `/api/monsters/import` | Imports compatible `.monster` JSON |
| POST | `/api/monsters/import-csv` | Imports Monster CSV |
| POST | `/api/monsters/roll-initiative` | Assigns d20 initiative to every Monster |
| POST | `/api/monsters/bulk-toggle` | Legacy whole-list toggle for supported Monster fields |
| POST | `/api/monsters/{id}/edit` | Edits Monster with optional image replacement |
| PATCH | `/api/monsters/{id}` | Updates Monster fields or applies HP delta |
| POST | `/api/characters` | Creates Character |
| POST | `/api/characters/import-csv` | Imports Character CSV |
| PATCH | `/api/characters/{id}` | Updates Character fields or applies HP delta |
| DELETE | `/api/combatants/{id}` | Removes one Monster or Character from working encounter |
| POST | `/api/combatants/{id}/reset` | Resets one combatant |

The legacy Monster whole-list bulk toggle accepts `active`, `ally`, `show_ac`, `show_hp`, or `show_initiative`. Selected-combatant bulk actions use the current implementation's bulk endpoint(s) and should retain the atomic all-ID validation rule documented above.

### Battle and activity routes

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/battle/reset-all` | Resets every combatant and clears battle order |
| POST | `/api/battle/start` | Starts a battle from validated full ordered IDs |
| POST | `/api/battle/next` | Advances to next eligible combatant |
| POST | `/api/battle/actions` | Atomically applies current-turn multi-target actions |
| GET | `/api/activity-log.json` | Downloads complete log as JSON |
| GET | `/api/activity-log.csv` | Downloads complete log as CSV |
| POST | `/api/activity-log/clear` | Clears the activity log |

## Imports and combat rules

CSV imports require UTF-8 data, permit a BOM, require a header and at least one nonblank row, trim and case-fold headers, and accept `true`/`false`, `yes`/`no`, `on`/`off`, or `1`/`0` for booleans.

Monster CSV requires `name`, `monster_type` or `type`, `ac`, and `hp`. Character CSV requires `name`. Missing IDs receive generated UUID hex values; duplicate IDs or conflicts with current encounter IDs return an error.

Setup import deep-copies selected combatants, generates fresh IDs, preserves current/max HP, derives alive state from HP, restores initiative from original initiative, clears active/visible/turn flags, resets Monster card flags, and leaves the existing battle order unchanged.

Battle start requires every active living combatant exactly once in the supplied order. Admin code sorts by descending initiative and resolves equal numeric initiative through a tie dialog. During battle, activating a living combatant inserts it after equal initiatives and before lower or initiative-less appropriate entries. Advancing skips dead/inactive combatants and clears battle state when no eligible combatants remain.

Current-turn action requests validate all rows before applying any. The actor must be active, alive, and in turn; targets must be active and alive. Damage and Heal require positive integer amounts; Buff and Debuff do not take amounts. Every applied action writes a log entry.

Deleting a combatant removes its ID from battle order. Upload files are not deleted automatically because other saved states may reference them.

## Client rendering

The Client Display renders visible initiative tokens and active living Monster cards. Characters appear in the initiative bar only.

- The Monster-card stage uses an adaptive grid.
- Enabled AC, HP, and initiative fields render in Monster-card text.
- Text uses an opaque contrast-aware panel for readability over images.
- Ally Monsters render with ` - Ally` appended without changing stored names.
- The initiative bar hides when empty, allowing the stage to use the full viewport.
- Setup background values come from `state.display.background`.
- Image backgrounds are centered, cover the viewport, do not repeat, and use fixed attachment.

Admin color markers use combatant colors with Monster fallback `#842029` and Character fallback `#1f4e79`. Checkbox selections and bulk menus are Admin-only and do not appear in Client state or rendering.

## Security and operations

- Cookies currently use `secure=False`; terminate TLS at a reverse proxy and revise cookie settings before public exposure.
- Sessions are process-local and disappear at restart.
- No built-in CSRF protection, rate limiting, audit trail, or multi-Admin concurrency coordination exists.
- Client access should be considered access to encounter state, even when not every detail is visibly rendered.
- Uploads are extension-checked and statically served. Restrict filesystem permissions and network reachability.
- D&D Beyond image lookup is best effort and depends on an external website.
- Setup and campaign deletion is permanent. Uploads are not garbage-collected automatically.

Validate a source update with:

```bash
python3.14 -m py_compile scrying_glass_server.py admin_html.py client_html.py login_html.py
find static -maxdepth 1 -type f \( -name '*.js' -o -name '*.css' \) -printf '%f\n' | sort
```

Hard-refresh Admin and Client pages after a static asset update.
