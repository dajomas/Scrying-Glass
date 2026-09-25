# Monster Display Technical Documentation

## Scope

This document describes the current Monster Display implementation as represented by the latest working source: a single-process Python/FastAPI application with separate admin and client-display applications, JSON persistence, WebSocket state broadcasting, saved setup management, combatant editing, batch monster creation, setup import, random monster initiative generation, adaptive client grid rendering, and battle-order maintenance.

---

## Architecture

### Process model

One Python process starts two Uvicorn servers over two independent FastAPI application objects:

```text
                         ┌───────────────────────────────────────┐
                         │          Python process               │
                         │                                       │
Admin browser ─ HTTP ───►│ admin FastAPI app                     │
                         │ default TCP 3000                      │
                         │                                       │
Client browser ─ HTTP ──►│ client FastAPI app                    │
Client browser ─ WS ────►│ default TCP 4000                      │
                         │                                       │
                         │ Shared in-process objects:            │
                         │ - STATE                               │
                         │ - SESSIONS                            │
                         │ - SOCKETS                             │
                         │ - state.json / setups / uploads       │
                         └───────────────────────────────────────┘
```

### Design implications

- Use **one process and one worker**.
- Multiple Uvicorn workers or replicas are unsupported without a shared state/session backend.
- Admin and client applications share encounter state only because they reside in the same interpreter.
- The client application does not expose admin mutation routes.

---

## Dependencies

```text
fastapi
uvicorn[standard]
PyYAML
python-multipart
```

The rest of the application uses Python standard-library modules such as `asyncio`, `json`, `random`, `hashlib`, `secrets`, `uuid`, and `pathlib`.

Install:

```bash
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

---

## Configuration

Example YAML configuration:

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
      password: "change-me"
    - username: "table"
      role: "client"
      password: "change-me"

display:
  background: "#080b14"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  dndbeyond_image_lookup: true
```

| Configuration path | Type | Description |
|---|---|---|
| `network.bind` | string | Bind address for both Uvicorn servers |
| `network.admin_port` | integer | Admin listener; default 3000 |
| `network.client_port` | integer | Client listener; default 4000 |
| `storage_dir` | string | Parent directory for state, setups, and images |
| `security.users` | list | Configured login accounts |
| `security.users[].role` | enum | `admin` or `client` |
| `display.background` | CSS value | Client background |
| `display.entry_direction` | enum | `from_bottom` or `from_top` |
| `display.exit_direction` | enum | `to_bottom` or `to_top` |
| `display.monster_width_percent` | integer | Legacy/configurable display sizing value |
| `display.dndbeyond_image_lookup` | boolean | Enables optional remote image lookup |

Command-line values override configuration values:

```bash
python3.14 monster_display_server.py \
  --config config.yaml \
  --bind 0.0.0.0 \
  --admin-port 3000 \
  --client-port 4000 \
  --storage-dir /var/lib/monster-display
```

---

## Authentication

### Sessions

Successful login creates an in-memory random session token:

```python
token = secrets.token_urlsafe(32)
SESSIONS[token] = {
    "username": username,
    "role": role,
}
```

The application sets an `HttpOnly`, `SameSite=Lax` cookie named `monster_session`.

### Authorization

Admin mutation routes use a FastAPI dependency such as:

```python
Depends(require("admin"))
```

The dependency validates the session cookie and role against the in-memory session map.

### Password formats

The configuration accepts:

| Format | Example |
|---|---|
| Plaintext | `my-local-password` |
| Scrypt | `scrypt$<salt_hex>$<digest_hex>` |

Scrypt hashes can be generated with:

```bash
python3.14 -c 'from monster_display_server import password_hash; print(password_hash("replace-me"))'
```

### Limitations

Sessions are lost after process restart. This is expected in the current in-memory design.

---

## Persistent storage

For `storage_dir: /var/lib/monster-display`:

```text
/var/lib/monster-display/
├── state.json
├── uploads/
│   └── <uuid>.<extension>
└── setups/
    └── <normalized-setup-name>.json
```

| Item | Meaning |
|---|---|
| `state.json` | Current working encounter state |
| `uploads/` | Uploaded monster images |
| `setups/` | Named reusable setup snapshots |

### Atomic active-state writes

Current state writes use a temporary file followed by replace:

```python
temp = STATE_FILE.with_suffix(".tmp")
temp.write_text(json.dumps(STATE, indent=2), encoding="utf-8")
temp.replace(STATE_FILE)
```

### Setup naming

Names are normalized to a restricted slug:

```python
slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
```

The normalized value is limited to 80 characters and used as the setup filename stem. This prevents path traversal.

---

## State model

### Root state

```json
{
  "monsters": [],
  "characters": [],
  "battle_order": []
}
```

### Monster model

```json
{
  "id": "uuid-hex",
  "name": "Elven Ice Queen",
  "monster_type": "humanoid",
  "ac": 17,
  "hp": 285,
  "max_hp": 285,
  "original_hp": 285,
  "color": "#842029",
  "image_url": "/media/abc.png",
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

### Character model

```json
{
  "id": "uuid-hex",
  "name": "Arannis",
  "color": "#1f4e79",
  "hp": 24,
  "max_hp": 24,
  "original_hp": 24,
  "initiative": 16,
  "original_initiative": 16,
  "active": false,
  "alive": true,
  "visible": false,
  "in_turn": false
}
```

### Key semantics

| Field | Meaning |
|---|---|
| `active` | Monster renders on client stage; combatant is eligible for battle progression if alive |
| `alive` | Life state; HP below zero forces false |
| `visible` | Controls initiative-bar inclusion |
| `in_turn` | Current combatant; exclusive across all entities |
| `original_hp` | Monster reset baseline; character baseline follows edited Max HP semantics |
| `original_initiative` | Initiative restored by reset |
| `battle_order` | Ordered list of combatant IDs, independent of list order |

### Normalization and migration

`normalize_state()` fills missing fields when loading prior state or setup files. It allows old saved setups to acquire later fields such as HP, visibility, ally, display toggles, and reset values.

---

## HTTP API

Unless noted, mutation endpoints require an authenticated admin session.

### Shared state

| Method | Path | Description |
|---|---|---|
| GET | `/api/state` | Returns the public state snapshot; available on admin and client applications to authenticated users |

### Authentication/UI routes

| Application | Method | Path |
|---|---|---|
| Admin | GET/POST | `/login` |
| Admin | GET | `/` |
| Client | GET/POST | `/login` |
| Client | GET | `/display` |

### Setup routes

| Method | Path | Description |
|---|---|---|
| GET | `/api/setups` | Lists saved setup names |
| POST | `/api/setups/new` | Replaces current state with empty state |
| POST | `/api/setups/save` | Saves full current state under a name |
| POST | `/api/setups/load` | Replaces current state from saved setup |
| POST | `/api/setups/import` | Appends reset-state copies from a saved setup |

#### Import payload

```json
{
  "name": "throne-room-lytharia",
  "kind": "both"
}
```

`kind` must be one of:

```text
characters
monsters
both
```

### Monster routes

| Method | Path | Description |
|---|---|---|
| POST | `/api/monsters` | Add one or more manual monsters via multipart form |
| POST | `/api/monsters/import` | Import one or more monsters from `.monster` file |
| POST | `/api/monsters/roll-initiative` | Overwrite every monster initiative with random d20 values |
| POST | `/api/monsters/{id}/edit` | Multipart complete monster edit, including image replacement |
| PATCH | `/api/monsters/{id}` | JSON partial monster update |

#### Manual monster multipart fields

```text
name          required
monster_type  required
ac            required
hp            required
color         required
quantity      optional, integer 1..50, default 1
image         optional image upload
```

#### Partial monster update fields

```json
{
  "name": "Ogre",
  "monster_type": "giant",
  "ac": 11,
  "hp": 52,
  "max_hp": 59,
  "original_hp": 59,
  "color": "#842029",
  "active": true,
  "ally": false,
  "visible": true,
  "initiative": 14,
  "hp_delta": -7,
  "show_ac": true,
  "show_hp": true,
  "show_initiative": false,
  "in_turn": true
}
```

### Character routes

| Method | Path | Description |
|---|---|---|
| POST | `/api/characters` | Add character |
| PATCH | `/api/characters/{id}` | Partial character update |

Example creation body:

```json
{
  "name": "Arannis",
  "color": "#1f4e79",
  "hp": 24,
  "initiative": 16
}
```

### Battle routes

| Method | Path | Description |
|---|---|---|
| POST | `/api/combatants/{id}/reset` | Reset an individual combatant |
| POST | `/api/battle/reset-all` | Reset all combatants and clear battle order |
| POST | `/api/battle/start` | Validate and set supplied battle order |
| POST | `/api/battle/next` | Advance current turn |

---

## WebSocket protocol

### Endpoint

```text
ws://SERVER:4000/ws
```

### Message format

The server sends a complete state snapshot immediately after connection and after every mutation:

```json
{
  "type": "state",
  "state": {
    "monsters": [],
    "characters": [],
    "battle_order": [],
    "display": {
      "background": "#080b14",
      "entry_direction": "from_bottom",
      "exit_direction": "to_bottom",
      "monster_width_percent": 45
    }
  }
}
```

The protocol intentionally sends full snapshots rather than diffs. This simplifies client rendering and recovery.

---

## Battle logic

### Eligibility

A combatant is eligible for automated battle behavior when:

```python
combatant["active"] is True and combatant["alive"] is True
```

### Start Battle

The browser creates the order and sends it to `POST /api/battle/start`. The server validates that every active living combatant appears exactly once.

The admin UI groups combatants by numeric initiative descending. Blank initiative values are ordered after numeric values.

### Tie resolution

Every tied numeric-initiative group gets a full ordering UI. Each member receives a unique position 1 through group size. The client validates uniqueness and reconstructs the full battle order by replacing only that tie bucket.

Higher initiative buckets remain before lower initiative buckets.

### Mid-battle activation insertion

The current source includes `insert_into_battle_order(combatant)`. On activation of a living combatant during an existing battle:

1. It is ignored if no battle order exists.
2. It is ignored if already present.
3. Numeric initiative is inserted before the first lower numeric initiative.
4. Equal initiative values are skipped, so the newly activated combatant goes after existing equal initiatives.
5. Numeric initiative goes before initiative-less entries.
6. Initiative-less combatants append at the end.

This preserves the current battle turn.

### Next turn

`advance_turn()` filters to active living combatants, preserves existing battle order where valid, appends newly eligible missing combatants by descending initiative, then advances to the next combatant cyclically.

---

## Death, visibility, and reset logic

### Death

When HP is below zero:

```python
entity["alive"] = False
entity["visible"] = True
entity["in_turn"] = False
```

### Turn assignment

`set_turn()` clears every entity’s `in_turn`, then sets the target to:

```python
entity["in_turn"] = True
entity["visible"] = True
```

### Individual reset

Common reset values:

```python
active = False
alive = True
visible = False
in_turn = False
initiative = original_initiative
```

Monster reset additionally restores:

```python
hp = original_hp
max_hp = original_hp
show_ac = False
show_hp = False
show_initiative = False
```

Character reset restores:

```python
hp = max_hp
```

Character Max HP is preserved; a changed Max HP becomes the active character reset value.

### Reset All

Reset All resets every entity, sorts Monster and Character arrays independently by Max HP descending, clears `battle_order`, writes state, and broadcasts the result.

---

## Setup import

Setup import loads and normalizes the named source setup, then deep-copies selected entity types.

### Imported monsters

```python
id = new UUID
hp = original_hp
max_hp = original_hp
initiative = original_initiative
active = False
alive = True
visible = False
in_turn = False
show_ac = False
show_hp = False
show_initiative = False
```

### Imported characters

```python
id = new UUID
hp = max_hp
initiative = original_initiative
active = False
alive = True
visible = False
in_turn = False
```

The importer deliberately does not modify `STATE["battle_order"]`.

---

## Batch monster creation

The manual and file-import monster routes accept `quantity`, constrained to 1 through 50.

Image behavior for a batch:

- A supplied upload is written once.
- Remote image lookup runs once when no upload is supplied.
- Each created monster gets a unique ID but uses the same image URL.

---

## Random monster initiatives

Endpoint:

```text
POST /api/monsters/roll-initiative
```

Implementation:

```python
for monster in STATE["monsters"]:
    monster["initiative"] = random.randint(1, 20)
```

This intentionally overwrites every monster’s current initiative regardless of activity or life state.

The required module import is:

```python
import random
```

---

## Client display

### Initiative bar

The client receives full state and renders visible combatants. It displays names only.

| State | CSS effect |
|---|---|
| Normal visible | White border |
| Dead | Black border, grayscale/reduced opacity |
| Current turn | Red border and glow |

Text color is chosen from approximate RGB luminance of six-digit hex combatant colors.

### Monster grid

Active living monsters render in an adaptive CSS Grid. Grid dimensions follow:

```text
1 -> 1x1
2 -> 1x2
3-4 -> 2x2
5-6 -> 2x3
7-9 -> 3x3
10-12 -> 3x4
13-16 -> 4x4
```

The algorithm alternates column growth and row growth:

```javascript
function gridSize(n) {
  if (n <= 1) return [1, 1];

  let rows = 1;
  let cols = 1;

  while (rows * cols < n) {
    if (cols === rows) cols++;
    else rows++;
  }

  return [rows, cols];
}
```

Every render assigns explicit positions:

```javascript
const row = Math.floor(index / cols) + 1;
const col = (index % cols) + 1;

card.style.gridRow = String(row);
card.style.gridColumn = String(col);
```

This guarantees top-row-first, left-to-right placement even after dynamic grid reflow.

---

## Monster file parser

`.monster` files must be UTF-8 JSON. The parser extracts:

| Application field | Candidate source fields |
|---|---|
| Name | `name` |
| Type | `type` |
| HP | `hpText`, then `hp` |
| AC | `ac`, `armorClass`, `otherArmorDesc`, then `natArmorBonus` |

The parser extracts the first integer from string-formatted AC and HP values.

---

## Image handling

Allowed upload extensions:

```text
.png
.jpg
.jpeg
.gif
.webp
```

Uploaded images receive UUID-derived filenames under `uploads/` and are served at:

```text
/media/<uuid>.<extension>
```

If no upload is supplied, optional best-effort D&D Beyond lookup fetches a monster search page and attempts to read `og:image` metadata. This is not a guaranteed integration.

---

## Clean shutdown

`Ctrl-C` can trigger normal asyncio cancellation followed by `KeyboardInterrupt`. To avoid a traceback while allowing cleanup, use:

```python
try:
    asyncio.run(serve())
except KeyboardInterrupt:
    pass
```

For graceful embedded-Uvicorn shutdown, retain references to both `uvicorn.Server` objects, set `should_exit = True` on cancellation, and await both server tasks with `return_exceptions=True`.

---

## Deployment

### Basic systemd unit

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

### Operational commands

```bash
python3.14 -m py_compile monster_display_server.py
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
```

### Backup

Back up the complete storage directory:

```bash
tar -C /var/lib -czf monster-display-backup.tgz monster-display
```

---

## Security considerations

The current design is intended for trusted local/LAN use.

Current limitations include:

- In-memory sessions.
- Cookie `secure=False` for HTTP LAN compatibility.
- No CSRF protection.
- No login rate limiting.
- Extension-based image validation rather than content inspection.
- Direct outbound request attempt for remote image lookup.
- Client WebSocket route does not separately validate an authenticated cookie.
- Client receives full combatant state, including fields hidden only by UI logic.

For Internet exposure:

1. Add TLS through a reverse proxy.
2. Set secure cookies.
3. Restrict admin access with firewall/VPN/IP allow lists.
4. Use scrypt password hashes.
5. Run as a non-root service account.
6. Add CSRF protection and rate limiting.
7. Consider a separate redacted client state projection.

---

## Recommended future refactors

- Separate embedded HTML/CSS/JavaScript into static versioned assets.
- Add automated tests for parser behavior, setup migration, tie ordering, mid-battle insertion, reset behavior, and client grid placement.
- Add explicit combatant and setup deletion endpoints/UI.
- Introduce SQLite or another database.
- Use Redis/database state plus Pub/Sub before attempting multi-worker deployment.
- Add API/display token authentication for player displays.
