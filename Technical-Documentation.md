# Monster Display Technical Documentation

Monster Display is a single-process Python/FastAPI application for running a GM-controlled tabletop battle display. It exposes separate Admin and Client FastAPI applications, stores the encounter in JSON, synchronizes client screens through WebSockets, and serves its UI from Python string modules.

For installation and a concise overview, see the [README](../README.md). For operational use, see the [User Guide](User-Guide.md).

## Architecture

### Process model

One Python process runs two Uvicorn servers concurrently. The Admin and Client applications share memory, persistent storage paths, sessions, and WebSocket connections.

```text
Admin browser ── HTTP ──► Admin FastAPI app  ── TCP 3000 by default
                                  │
                                  ├── shared STATE
                                  ├── shared SESSIONS
                                  ├── shared SOCKETS
                                  └── state.json, setups/, uploads/
                                  │
Client browser ─ HTTP/WS ─► Client FastAPI app ─ TCP 4000 by default
```

The UI source is split into Python modules:

```text
monster_display_server.py  # application, models, state, routes, startup
admin_html.py              # ADMIN_HTML: Admin markup, CSS, JavaScript
client_html.py             # CLIENT_HTML: player display markup, CSS, JavaScript
login_html.py              # LOGIN: shared login markup
config.example.yaml        # configuration template
```

### Operational implication

Run one process and one worker. The implementation relies on in-memory `STATE`, `SESSIONS`, and `SOCKETS`; multiple workers or replicas would need a shared persistence, session, locking, and pub/sub design before they can synchronize safely.

## Dependencies

Install the runtime dependencies:

```bash
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

The remainder uses Python standard library modules, including `asyncio`, `copy`, `csv`, `datetime`, `hashlib`, `hmac`, `io`, `json`, `random`, `re`, `secrets`, `shutil`, `uuid`, and `pathlib`.

## Configuration

Configuration loads from YAML or JSON. Command-line values override matching configuration values.

```yaml
network:
  bind: "0.0.0.0"
  admin_port: 3000
  client_port: 4000

storage_dir: "./monster-display-data"

security:
  users:
    - username: "dm"
      role: "admin"
      password: "replace-this-admin-password"
    - username: "table"
      role: "client"
      password: "replace-this-client-password"

display:
  background: "radial-gradient(circle at 50% 15%, #16273d, #080b14 70%)"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  default_monster_color: "#842029"
  default_character_color: "#1f4e79"
  dndbeyond_image_lookup: true
```

| Setting | Description |
|---|---|
| `network.bind` | Interface/address for both Uvicorn services |
| `network.admin_port` | Admin listener; default 3000 |
| `network.client_port` | Client listener; default 4000 |
| `storage_dir` | Parent directory for state, setups, and uploaded media |
| `security.users` | User records with username, role, and password/hash |
| `display.background` | CSS color, gradient, or image URL used by Client Display |
| `display.entry_direction` | `from_bottom` or `from_top` card entry animation |
| `display.exit_direction` | `to_bottom` or `to_top` card exit animation |
| `display.monster_width_percent` | Retained display configuration value |
| `display.default_monster_color` | Default monster color in the example configuration |
| `display.default_character_color` | Default character color in the example configuration |
| `display.dndbeyond_image_lookup` | Enables best-effort remote monster-image lookup |

Example command line:

```bash
python3.14 monster_display_server.py \
  --config /etc/monster-display/config.yaml \
  --bind 0.0.0.0 \
  --admin-port 3000 \
  --client-port 4000 \
  --storage-dir /var/lib/monster-display
```

## Authentication and authorization

Successful login creates an in-memory session token:

```python
token = secrets.token_urlsafe(32)
SESSIONS[token] = {"username": username, "role": role}
```

The browser receives a `monster_session` cookie configured as `HttpOnly` and `SameSite=Lax`. Admin routes use `Depends(require("admin"))`; the Client Display accepts authenticated `admin` or `client` users.

Passwords may be plaintext or scrypt values in this format:

```text
scrypt$<salt_hex>$<digest_hex>
```

Generate a hash with:

```bash
python3.14 -c 'from monster_display_server import password_hash; print(password_hash("replace-me"))'
```

Sessions are intentionally ephemeral and disappear when the process restarts.

## Persistence

For `storage_dir: /var/lib/monster-display`:

```text
/var/lib/monster-display/
├── state.json
├── uploads/
│   └── <uuid>.<extension>
└── setups/
    └── <normalized-setup-name>.json
```

| Path | Purpose |
|---|---|
| `state.json` | Current working encounter, battle state, and activity log |
| `uploads/` | Uploaded monster images served under `/media/` |
| `setups/` | Named full-state JSON snapshots |

Current state saves use a temporary file and atomic replace:

```python
temp = STATE_FILE.with_suffix(".tmp")
temp.write_text(json.dumps(STATE, indent=2), encoding="utf-8")
temp.replace(STATE_FILE)
```

Setup names are normalized to lower-case, hyphenated slugs and limited to 80 characters. This avoids path traversal in setup filenames.

## State model

### Root state

```json
{
  "monsters": [],
  "characters": [],
  "battle_order": [],
  "activity_log": []
}
```

`normalize_state()` fills missing fields when loading an older state or setup. It also removes battle-order IDs that no longer refer to a loaded monster or character.

### Monster record

```json
{
  "id": "uuid-hex",
  "name": "Ice Guard",
  "monster_type": "humanoid",
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

### Character record

```json
{
  "id": "uuid-hex",
  "name": "Aelwyn",
  "color": "#1f4e79",
  "hp": 34,
  "max_hp": 34,
  "original_hp": 34,
  "initiative": 16,
  "original_initiative": 16,
  "active": false,
  "alive": true,
  "visible": false,
  "in_turn": false
}
```

### Activity-log record

```json
{
  "id": "uuid-hex",
  "timestamp": "2026-09-27T10:00:00+00:00",
  "active_combatant_id": "uuid-hex-or-null",
  "active_combatant": "Ice Guard",
  "active_combatant_state": "alive",
  "target_combatant_id": "uuid-hex",
  "target_combatant": "Aelwyn",
  "target_combatant_state": "alive",
  "action": "damage",
  "amount": 7
}
```

`action` is one of `damage`, `heal`, `buff`, or `debuff`. `amount` is an integer for Damage and Heal and `null` for Buff and Debuff. Direct HP controls identify the actor as the current-turn combatant or `System` when no turn is assigned.

### Important semantics

| Field | Meaning |
|---|---|
| `active` | Eligible for battle behavior when alive; active monsters render as client cards |
| `alive` | Current life state; zero or lower HP is dead in current runtime logic |
| `visible` | Inclusion in the Client initiative bar |
| `in_turn` | Exclusive current turn indicator across all combatants |
| `original_hp` | Monster reset baseline; character reset baseline follows max HP updates |
| `original_initiative` | Initiative restored by reset |
| `battle_order` | Ordered IDs independent of list/table ordering |

## State synchronization

Every state-changing route calls `changed()`:

```python
async def changed() -> None:
    async with LOCK:
        save_state()
    await broadcast()
```

`broadcast()` sends a message like the following to connected Client WebSockets:

```json
{
  "type": "state",
  "state": {
    "monsters": [],
    "characters": [],
    "battle_order": [],
    "activity_log": [],
    "display": {}
  }
}
```

Client JavaScript fetches `/api/state` initially, then renders received WebSocket state messages. Admin JavaScript refreshes its own table and pane state by calling `load()` after mutation requests.

## HTTP routes

All mutation routes below require an authenticated Admin session unless stated otherwise.

### Pages and authentication

| App | Method | Path | Purpose |
|---|---|---|---|
| Admin | GET/POST | `/login` | Admin login |
| Admin | GET | `/` | Admin page |
| Client | GET/POST | `/login` | Client/admin login |
| Client | GET | `/display` | Player-facing display |
| Both | GET | `/api/state` | Authenticated public state snapshot |
| Client | WebSocket | `/ws` | Real-time state updates |

### Setup routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/setups` | List saved setup names |
| POST | `/api/setups/new` | Replace working state with a blank state |
| POST | `/api/setups/save` | Save current state under a normalized name |
| POST | `/api/setups/load` | Replace working state from a saved setup |
| POST | `/api/setups/import` | Append reset-state copies from a saved setup |

### Monster routes

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/monsters` | Create one or more manual monsters via multipart form |
| POST | `/api/monsters/import` | Import a `.monster` JSON file |
| POST | `/api/monsters/import-csv` | Import monster CSV rows |
| POST | `/api/monsters/roll-initiative` | Assign d20 initiatives to all monsters |
| POST | `/api/monsters/bulk-toggle` | Toggle a monster field across all monsters |
| POST | `/api/monsters/{id}/edit` | Save a multipart monster edit, optionally including an image |
| PATCH | `/api/monsters/{id}` | Update a monster JSON fields / HP delta |

The bulk-toggle field is one of `active`, `ally`, `show_ac`, `show_hp`, or `show_initiative`.

### Character routes

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/characters` | Create a character |
| POST | `/api/characters/import-csv` | Import character CSV rows |
| PATCH | `/api/characters/{id}` | Update character fields / HP delta |

### Combat and log routes

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/combatants/{id}/reset` | Reset one combatant |
| POST | `/api/battle/reset-all` | Reset all combatants and clear battle order |
| POST | `/api/battle/start` | Begin a battle using a complete ordered ID list |
| POST | `/api/battle/next` | Advance to the next eligible combatant |
| POST | `/api/battle/actions` | Apply one or more current-turn target actions atomically |
| GET | `/api/activity-log.json` | Download activity log JSON |
| GET | `/api/activity-log.csv` | Download activity log CSV |
| POST | `/api/activity-log/clear` | Clear persisted activity-log records |

### Battle actions payload

```json
{
  "actor_id": "current-turn-combatant-id",
  "actions": [
    {
      "target_id": "target-id",
      "action": "damage",
      "amount": 7
    },
    {
      "target_id": "another-target-id",
      "action": "buff",
      "amount": null
    }
  ]
}
```

The server requires that the actor is active, alive, and currently in turn. Targets must be active and alive at validation time. Damage and Heal require a positive amount; Buff and Debuff reject an amount. Validation occurs before any listed action is applied, preventing partial application caused by malformed input.

## CSV contracts

CSV must be UTF-8 (BOM accepted), contain a header row, and contain at least one nonblank data row. Header names are trimmed and case-folded. Boolean values accept `true`/`false`, `yes`/`no`, `on`/`off`, or `1`/`0`.

Monster import requires `name`, `monster_type` or `type`, `ac`, and `hp`. Character import requires `name`. A missing or blank `id` is replaced by a generated UUID hex string. Duplicate IDs inside an upload or conflicts with existing monster/character IDs return HTTP 400.

## Battle-order algorithms

`begin_battle()` validates that the submitted order contains each active living combatant exactly once. Admin JavaScript builds this list in descending initiative order and requests explicit ordering inside tied numeric-initiative groups.

`insert_into_battle_order()` handles newly activated living combatants when a battle order exists:

- Numeric initiative is inserted before lower numeric initiative.
- An equal initiative is inserted after existing entries at that value.
- Numeric initiative is inserted before initiative-less entries.
- Initiative-less entries are appended after numeric entries.

`advance_turn()` discards inactive/dead IDs from the active sequence, adds newly eligible missing combatants in initiative order, then advances cyclically.

## Client rendering

The Client Display renders:

- An initiative bar for visible battle-order combatants plus additional active/visible combatants.
- Active, living monster cards in an adaptive grid.
- A contrast-aware opaque text panel on each monster card.
- CSS background colors, gradients, or centered cover-sized image backgrounds.

When no initiative tokens exist, JavaScript sets the initiative bar’s `hidden` state. CSS removes the bar and expands the stage to the full viewport.

## Security and limitations

- Cookies use `secure=False`; run behind HTTPS and set appropriate proxy/cookie configuration before public deployment.
- Sessions are in-memory and vanish at restart.
- There is no built-in CSRF protection, rate limiting, audit identity beyond the action names stored in logs, or multi-user conflict resolution.
- Uploaded images are extension-checked but otherwise served as static files; restrict deployment access and storage permissions appropriately.
- D&D Beyond image lookup is best effort and may fail when remote markup or access rules change.
- The Client state payload includes information that may be hidden visually. Treat access to the Client service as access to encounter state.
- Combatants and saved setups do not currently have a dedicated deletion UI.

## Operations

Validate syntax before deployment:

```bash
python3.14 -m py_compile monster_display_server.py admin_html.py client_html.py login_html.py
```

A basic `systemd` service:

```ini
[Unit]
Description=Monster Display
After=network.target

[Service]
Type=simple
User=monsterdisplay
Group=monsterdisplay
WorkingDirectory=/opt/monster-display
ExecStart=/opt/monster-display/.venv/bin/python /opt/monster-display/monster_display_server.py --config /etc/monster-display/config.yaml
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Run the service as a non-root user and ensure that user can read the configuration and write the configured storage directory.

## Troubleshooting

| Symptom | Check |
|---|---|
| Admin page is stale | Hard-refresh after updating embedded HTML modules |
| `Sign in required` | Correct role, same hostname, valid session cookie, fresh login after restart |
| Client does not update | Port 4000 reachability and WebSocket reconnection after refresh |
| CSV import fails | UTF-8/header/required field/numeric and duplicate-ID requirements |
| Background image fails | Confirm image exists under `/media/` and CSS URL is valid |
| Image lookup fails | Upload a local image instead of depending on remote lookup |
