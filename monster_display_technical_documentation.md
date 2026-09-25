# Monster Display Technical Documentation

## Scope

This document describes the architecture, data model, HTTP/WebSocket interfaces, persistence model, configuration, deployment considerations, operational constraints, and extension points of **Monster Display v4.3.1**.

The application is a single Python process that starts two FastAPI/ASGI applications:

- An **admin application** on the configured admin TCP port, default `3000`.
- A **client-display application** on the configured client TCP port, default `4000`.

The applications share one in-process encounter state, session store, persistent JSON state file, uploaded media directory, and WebSocket connection set.

---

## Contents

1. [System architecture](#system-architecture)
2. [Runtime components](#runtime-components)
3. [Network model](#network-model)
4. [Configuration](#configuration)
5. [Authentication and authorization](#authentication-and-authorization)
6. [State model](#state-model)
7. [Persistence](#persistence)
8. [Battle setup lifecycle](#battle-setup-lifecycle)
9. [API reference](#api-reference)
10. [WebSocket protocol](#websocket-protocol)
11. [Admin UI implementation](#admin-ui-implementation)
12. [Client display implementation](#client-display-implementation)
13. [Battle and reset algorithms](#battle-and-reset-algorithms)
14. [Monster-file import](#monster-file-import)
15. [Image handling](#image-handling)
16. [Deployment](#deployment)
17. [Operations and diagnostics](#operations-and-diagnostics)
18. [Security considerations](#security-considerations)
19. [Known limitations](#known-limitations)
20. [Extension guidance](#extension-guidance)

---

## System architecture

### Process topology

The implementation runs both applications in the same interpreter and event loop:

```text
                         ┌──────────────────────────────────────┐
                         │        Python 3.14 process           │
                         │                                      │
Admin browser ── HTTP ──►│  FastAPI admin app :3000             │
                         │      │                               │
                         │      ├── Shared STATE                │
                         │      ├── Shared SESSIONS             │
                         │      ├── state.json                  │
                         │      ├── setups/*.json               │
                         │      └── uploads/*                   │
                         │                                      │
Client browser ─ HTTP ──►│  FastAPI client app :4000            │
Client browser ── WS ───►│      │                               │
                         │      └── WebSocket broadcast set     │
                         └──────────────────────────────────────┘
```

### Why two FastAPI applications

The service exposes different capabilities on separate ports.

| Application | Default port | Intended audience | Mutation endpoints |
|---|---:|---|---|
| `admin` | 3000 | Game master/admin | Yes |
| `client` | 4000 | Table/player display | No |

This separation prevents the client port from exposing administrative combatant-mutation routes. Both applications share memory because they run in a single process.

### Consequence for scaling

The current design is deliberately **single-process** and should run with one worker. Running multiple worker processes or multiple container replicas would create independent in-memory `STATE`, `SESSIONS`, and WebSocket sets. A multi-worker deployment requires a shared backend such as Redis plus a database or durable shared state layer.

---

## Runtime components

| Component | Implementation | Responsibility |
|---|---|---|
| HTTP/ASGI framework | FastAPI | Routes, form/file handling, JSON validation, dependencies |
| ASGI server | Uvicorn | Runs each FastAPI app on a TCP listener |
| Configuration parser | PyYAML or `json` | Loads YAML/JSON runtime configuration |
| Validation | Pydantic | Validates JSON API request bodies |
| Persistence | Standard-library JSON | Saves current state and named setups |
| Authentication | In-memory signed-random session token | Role-aware cookie sessions |
| Password validation | `hashlib.scrypt` or constant-time plaintext comparison | Supports scrypt password hashes and simple plaintext configuration values |
| Client synchronization | FastAPI WebSockets | Pushes full encounter state after every mutation |
| Static media | FastAPI `StaticFiles` | Serves uploaded images from `/media/` |

### Python dependencies

```text
fastapi
uvicorn[standard]
PyYAML
python-multipart
```

The remaining imports are Python standard library modules.

---

## Network model

### Default listeners

```text
Admin:  0.0.0.0:3000
Client: 0.0.0.0:4000
```

Use `127.0.0.1` for local-only deployments, or a specific LAN address to constrain exposure.

### Administrative routes

The following paths are bound only to the admin app unless otherwise noted:

```text
GET/POST  /login
GET       /
GET       /api/state
GET       /api/setups
POST      /api/setups/new
POST      /api/setups/save
POST      /api/setups/load
POST      /api/monsters
POST      /api/monsters/import
PATCH     /api/monsters/{id}
POST      /api/characters
PATCH     /api/characters/{id}
POST      /api/combatants/{id}/reset
POST      /api/battle/reset-all
POST      /api/battle/start
POST      /api/battle/next
```

### Client routes

```text
GET/POST  /login
GET       /display
GET       /api/state
WS        /ws
GET       /media/{filename}
```

Both applications mount `/media/` from the same upload directory. This allows generated image URLs such as `/media/<uuid>.png` to resolve from either port.

### Reverse-proxy notes

For production-style deployment, place a TLS-aware reverse proxy in front of the application. Typical arrangements include:

```text
https://dm.example.net/       -> 127.0.0.1:3000
https://display.example.net/  -> 127.0.0.1:4000
```

The reverse proxy must support WebSocket upgrade forwarding for the client display path `/ws`.

---

## Configuration

### YAML configuration schema

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
  dndbeyond_image_lookup: true
```

### Configuration fields

| Path | Type | Default | Description |
|---|---|---|---|
| `network.bind` | string | `0.0.0.0` | Listen address for both Uvicorn servers |
| `network.admin_port` | integer | `3000` | Admin listener TCP port |
| `network.client_port` | integer | `4000` | Client listener TCP port |
| `storage_dir` | string | `./monster-display-data` | State, setup, and upload parent directory |
| `security.users` | list | Default admin/client examples | User accounts |
| `security.users[].username` | string | — | Login name |
| `security.users[].role` | string | — | `admin` or `client` |
| `security.users[].password` | string | — | Plaintext or `scrypt$...` password value |
| `display.background` | CSS value | `#080b14` | Client display background |
| `display.entry_direction` | enum | `from_bottom` | `from_bottom` or `from_top` |
| `display.exit_direction` | enum | `to_bottom` | `to_bottom` or `to_top` |
| `display.monster_width_percent` | integer | `45` | Client monster-card width in viewport-width units |
| `display.dndbeyond_image_lookup` | boolean | `true` | Enables optional best-effort remote image lookup |

### Command-line overrides

```bash
python3.14 monster_display_server_v4_3_1.py \
  --config config.yaml \
  --bind 0.0.0.0 \
  --admin-port 3000 \
  --client-port 4000 \
  --storage-dir /var/lib/monster-display
```

The application loads the configuration file first, then applies command-line values.

---

## Authentication and authorization

### Session design

Upon successful login, the relevant application creates a random session ID:

```python
token = secrets.token_urlsafe(32)
SESSIONS[token] = {"username": username, "role": role}
```

It sets a cookie named `monster_session`:

```text
HttpOnly: true
SameSite: Lax
Secure: false
```

The `Secure` setting is false to support plain HTTP LAN use. It should be made true when deployment is HTTPS-only.

### Role enforcement

Administrative mutation handlers use a FastAPI dependency equivalent to:

```python
Depends(require("admin"))
```

The dependency looks up the `monster_session` cookie in the in-memory `SESSIONS` map and verifies the requested role.

### Password modes

The application accepts two password formats:

| Format | Example | Behavior |
|---|---|---|
| Plaintext | `my-password` | Constant-time direct comparison |
| Scrypt | `scrypt$<salt_hex>$<digest_hex>` | Derives scrypt digest and performs constant-time comparison |

Generate a scrypt password hash with:

```bash
python3.14 -c 'from monster_display_server_v4_3_1 import password_hash; print(password_hash("replace-me"))'
```

### Session limitations

Sessions are intentionally in-memory. They are lost after process restart, deployment replacement, or crash. Users must log in again.

---

## State model

### Root structure

```json
{
  "monsters": [],
  "characters": [],
  "battle_order": []
}
```

### Monster object

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
  "image_url": "/media/abc123.png",
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

| Field | Semantics |
|---|---|
| `id` | Stable internal UUID-like identifier used in API paths and battle order |
| `name` | Displayed monster name |
| `monster_type` | Displayed type and remote-image lookup key |
| `ac` | Armor Class |
| `hp` | Current hit points |
| `max_hp` | Current maximum hit points; monsters reset to original value |
| `original_hp` | Imported/manual starting HP reset baseline |
| `color` | CSS color for display and initiative token |
| `image_url` | Optional local or remote image reference |
| `active` | Enables stage display and battle eligibility |
| `alive` | Death state; false when HP is below zero |
| `visible` | Controls initiative-bar inclusion |
| `ally` | Persisted monster classification flag |
| `initiative` | Current initiative, nullable |
| `original_initiative` | Reset initiative baseline |
| `show_ac`, `show_hp`, `show_initiative` | Per-stat monster-card visibility flags |
| `in_turn` | Current battle-turn marker; globally exclusive |

### Character object

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

### Character Max HP rule

When `max_hp` is changed through the API, the application also updates `original_hp`. Character reset then preserves the edited current `max_hp` and sets `hp` equal to it.

Conceptually:

```python
if "max_hp" in values:
    character["original_hp"] = values["max_hp"]

# On reset:
character["hp"] = character["max_hp"]
```

### Battle order

`battle_order` contains IDs, not embedded combatant copies:

```json
{
  "battle_order": [
    "5c713...",
    "8ca40...",
    "20f61..."
  ]
}
```

This maintains turn sequence independent of the ordering of `monsters` and `characters` arrays. The application filters invalid IDs on state/setup normalization.

---

## Persistence

### Directory layout

Given `storage_dir: /var/lib/monster-display`:

```text
/var/lib/monster-display/
├── state.json
├── uploads/
│   ├── 254b117f....png
│   └── 8cb1e11d....webp
└── setups/
    ├── throne-room-lytharia.json
    └── goblin-ambush.json
```

### Current state

`state.json` persists the live encounter state after mutations. State writes are atomic at the filesystem level by writing to a temporary file then replacing the target:

```python
temp = STATE_FILE.with_suffix(".tmp")
temp.write_text(json.dumps(STATE, indent=2), encoding="utf-8")
temp.replace(STATE_FILE)
```

### Named setups

Named setups are serialized copies of `STATE` and saved under `setups/`. Setup names are normalized to a restricted slug:

```python
slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
```

This prevents path traversal and creates predictable filenames.

### State normalization/migration

At startup and setup load, `normalize_state()` supplies defaults for earlier state files. It adds fields introduced across versions, including:

- Monster `ally` and `visible`
- Character HP, Max HP, and reset baseline
- Initiative display settings
- Active/alive/in-turn flags

This is forward-tolerant for missing fields, but it is not a formal schema-version migration system.

---

## Battle setup lifecycle

### New setup

`POST /api/setups/new` resets the in-memory root state to:

```json
{
  "monsters": [],
  "characters": [],
  "battle_order": []
}
```

The endpoint persists the result to `state.json` and broadcasts it to connected client WebSockets.

### Save setup

`POST /api/setups/save` writes the full current `STATE` to:

```text
<storage_dir>/setups/<normalized-name>.json
```

Saving an existing name replaces it.

### Load setup

`POST /api/setups/load` reads, validates, normalizes, installs, persists, and broadcasts a named setup. The active `state.json` is therefore always the most recently loaded or modified working setup.

### Image references

Setups store image URL strings only. Local uploads refer to `/media/<uuid>.<extension>`, which requires that the referenced file remain present in `uploads/`.

---

## API reference

All JSON mutation routes require an admin role. The server returns `401` when the session is missing or insufficient and `404` for unknown combatants/setups.

### Common state route

#### `GET /api/state`

Available on both applications to an authenticated session.

Response:

```json
{
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
```

### Setup routes

#### `GET /api/setups`

Response:

```json
{
  "names": ["goblin-ambush", "throne-room-lytharia"]
}
```

#### `POST /api/setups/new`

No request body.

Response: full public state.

#### `POST /api/setups/save`

Request:

```json
{
  "name": "Throne Room Lytharia"
}
```

Response:

```json
{
  "name": "throne-room-lytharia"
}
```

#### `POST /api/setups/load`

Request:

```json
{
  "name": "throne-room-lytharia"
}
```

Response:

```json
{
  "name": "throne-room-lytharia"
}
```

### Monster routes

#### `POST /api/monsters`

Multipart form fields:

| Field | Required | Type |
|---|---:|---|
| `name` | Yes | string |
| `monster_type` | Yes | string |
| `ac` | Yes | integer |
| `hp` | Yes | integer |
| `color` | Yes | string/CSS color |
| `image` | No | image upload |

#### `POST /api/monsters/import`

Multipart form fields:

| Field | Required | Type |
|---|---:|---|
| `monster_file` | Yes | `.monster` upload |
| `color` | Yes | string/CSS color |
| `image` | No | image upload |

#### `PATCH /api/monsters/{id}`

Supported JSON fields:

```json
{
  "active": true,
  "ally": false,
  "visible": true,
  "initiative": 14,
  "hp": 23,
  "hp_delta": -7,
  "show_ac": true,
  "show_hp": true,
  "show_initiative": false,
  "in_turn": true
}
```

Only supplied, non-null fields are processed. This is important: button clicks that send only one property do not clear initiative or HP.

### Character routes

#### `POST /api/characters`

Request body:

```json
{
  "name": "Arannis",
  "color": "#1f4e79",
  "hp": 24,
  "initiative": 16
}
```

`hp` defaults to `1` if omitted by an API caller, although the UI always supplies a value.

#### `PATCH /api/characters/{id}`

Supported JSON fields:

```json
{
  "active": true,
  "alive": true,
  "visible": true,
  "initiative": 16,
  "hp": 18,
  "max_hp": 24,
  "hp_delta": -6,
  "in_turn": true
}
```

### Reset and battle routes

#### `POST /api/combatants/{id}/reset`

Resets a single combatant.

#### `POST /api/battle/reset-all`

Resets all combatants, sorts separate admin arrays by Max HP descending, and clears `battle_order`.

#### `POST /api/battle/start`

Request:

```json
{
  "order": ["combatant-id-1", "combatant-id-2"]
}
```

The provided list must contain every active, living combatant exactly once. The endpoint saves this order, sets the first combatant as current turn, enables visibility for it, sorts the admin data arrays by initiative, and broadcasts the new state.

#### `POST /api/battle/next`

No body. Moves the battle turn to the next active, living combatant. If required, new eligible combatants absent from the existing battle order are appended by descending initiative.

---

## WebSocket protocol

### Endpoint

```text
ws://SERVER:4000/ws
```

Use `wss://` when a TLS reverse proxy serves the client application through HTTPS.

### Initial message

Immediately after connecting, the server sends a complete state message:

```json
{
  "type": "state",
  "state": {
    "monsters": [],
    "characters": [],
    "battle_order": [],
    "display": {}
  }
}
```

### Update messages

Every successful state mutation invokes `changed()`, which:

1. Writes `state.json`.
2. Broadcasts the full public state to every active WebSocket connection.

The protocol currently sends full snapshots rather than diffs. This favors simple, robust client rendering over bandwidth efficiency.

### Connection lifecycle

The client display reconnects by reloading itself after a WebSocket close. Failed send operations cause the server to remove stale WebSocket objects from its set.

---

## Admin UI implementation

The admin interface is embedded as `ADMIN_HTML` in the Python file. It contains no external JavaScript or CSS build pipeline.

### Rendering

The browser calls:

```text
GET /api/state
```

and renders the Monster and Character tables from the received JSON state.

### Mutations

Most control actions issue `PATCH` requests such as:

```javascript
fetch('/api/characters/' + id, {
  method: 'PATCH',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({hp_delta: -5})
})
```

The UI reloads state after each mutation.

### Tie modal

The modal starts with the `hidden` attribute:

```html
<div id="tieModal" class="modal" hidden>
```

The associated CSS must retain this rule:

```css
.modal[hidden] {
  display: none !important;
}
```

Without it, `.modal { display: grid; }` may override the browser’s default hidden behavior and cause the modal to appear unexpectedly.

### Setup controls

- **New** calls `POST /api/setups/new` after confirmation.
- **Save** calls `POST /api/setups/save` with the entered name.
- **Load** calls `POST /api/setups/load` using the selected setup after confirmation.

---

## Client display implementation

The client UI is embedded as `CLIENT_HTML`.

### Rendering path

1. Fetch `GET /api/state` for initial state.
2. Connect to `/ws`.
3. Render full state snapshots received from WebSocket.

### Initiative bar selection

The client includes:

- Combatants in `battle_order` only if `visible` is true.
- Other active and visible combatants as initiative-sorted extras.

The bar displays only name text. Initiative itself is not displayed.

### Token state styling

| State | CSS class/effect |
|---|---|
| Default visible | White border |
| Dead | `dead`, black border, grayscale/reduced opacity |
| Current turn | `turn`, red border and red glow |

### Text contrast

The display calculates an approximate RGB luminance from six-digit hex colors and chooses dark or light foreground text:

```javascript
(0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
```

Colors above the threshold use dark text; others use white text. Non-hex CSS colors fall back to white text.

### Main stage

Only active and alive monsters render on the full-height main stage. Characters are represented in the initiative bar only.

---

## Battle and reset algorithms

### Combatant eligibility

A combatant is eligible for automated battle order and Next progression when:

```python
entity["active"] is True and entity["alive"] is True
```

### Death behavior

A monster or character dies when its HP falls below zero.

On death:

```python
entity["alive"] = False
entity["visible"] = True
entity["in_turn"] = False
```

A manually dead character follows the same visible/in-turn behavior.

### Current turn invariant

At most one combatant may have `in_turn: true`. The helper clears all combatants before assigning a requested new turn.

### Visibility invariant

Assigning a battle turn always enables visibility:

```python
entity["in_turn"] = True
entity["visible"] = True
```

### Individual reset

Common reset fields:

```python
active = False
alive = True
visible = False
in_turn = False
initiative = original_initiative
```

Monster-specific reset:

```python
hp = original_hp
max_hp = original_hp
show_ac = False
show_hp = False
show_initiative = False
```

Character-specific reset:

```python
hp = max_hp
```

Character Max HP remains as currently edited.

### Reset All

Reset All applies individual reset behavior to every combatant, sorts separate admin arrays by Max HP descending, clears `battle_order`, persists, and broadcasts state.

### Start Battle

The browser derives a proposed descending-initiative order and resolves duplicate numeric initiatives through an admin modal. The backend validates that the final order contains each active, living combatant exactly once.

After validation, Start Battle:

1. Assigns the provided order to `battle_order`.
2. Clears old turns.
3. Marks the first combatant as in turn and visible.
4. Sorts admin monster and character arrays independently by initiative descending.
5. Persists and broadcasts state.

Critically, sorting the arrays is not a rewrite of `battle_order`.

---

## Monster-file import

`.monster` files are expected to be UTF-8 JSON. The parser accepts common properties from the supplied format:

| Required application field | Source candidates |
|---|---|
| Name | `name` |
| Monster type | `type` |
| HP | `hpText`, then `hp` |
| AC | `ac`, `armorClass`, `otherArmorDesc`, then `natArmorBonus` |

The parser finds the first integer in string-formatted HP or AC fields. For example:

```json
{
  "otherArmorDesc": "17 Ice bound robes (reinforced by magical ward)",
  "hpText": "285"
}
```

parses as AC 17 and HP 285.

---

## Image handling

### Manual uploads

Allowed image extensions:

```text
.png
.jpg
.jpeg
.gif
.webp
```

Uploaded files receive a UUID-derived filename and are stored under `uploads/`. The combatant stores the URL:

```text
/media/<uuid>.<extension>
```

### Remote lookup

If no upload is supplied and `dndbeyond_image_lookup` is enabled, the server makes a best-effort request to a public D&D Beyond monster-search page. It attempts to extract an `og:image` metadata value.

This path must be treated as opportunistic rather than a guaranteed or stable integration. It can fail due to remote site changes, bot mitigation, connectivity, or missing metadata.

---

## Deployment

### Local/LAN foreground run

```bash
python3.14 monster_display_server_v4_3_1.py --config /etc/monster-display/config.yaml
```

### Basic systemd unit

Create `/etc/systemd/system/monster-display.service`:

```ini
[Unit]
Description=Monster Display
After=network.target

[Service]
Type=simple
User=monsterdisplay
Group=monsterdisplay
WorkingDirectory=/opt/monster-display
ExecStart=/opt/monster-display/.venv/bin/python /opt/monster-display/monster_display_server_v4_3_1.py --config /etc/monster-display/config.yaml
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now monster-display
sudo systemctl status monster-display
```

### Firewall example

For a trusted LAN using UFW:

```bash
sudo ufw allow from 192.168.1.0/24 to any port 3000 proto tcp
sudo ufw allow from 192.168.1.0/24 to any port 4000 proto tcp
```

Restrict the admin port more tightly if possible.

### Backups

Back up the entire configured storage directory:

```bash
tar -C /var/lib -czf monster-display-backup.tgz monster-display
```

This preserves current state, named setups, and uploaded images together.

---

## Operations and diagnostics

### Syntax validation

```bash
python3.14 -m py_compile monster_display_server_v4_3_1.py
```

No output indicates successful compilation.

### Confirm listeners

```bash
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
```

### Check the running command

```bash
ps -fp <PID>
tr '\0' ' ' < /proc/<PID>/cmdline
```

### Confirm served version markers

The admin page can be checked from the local host:

```bash
curl -s http://127.0.0.1:3000/ | grep -o 'setupName'
```

Expected output:

```text
setupName
```

### Inspect persistent data

```bash
jq . /var/lib/monster-display/state.json
find /var/lib/monster-display/setups -maxdepth 1 -type f -name '*.json' -printf '%f\n'
```

### API test with an authenticated browser session

For normal operation, use browser developer tools rather than manually replaying cookie-authenticated requests. The admin page uses relative URLs and same-origin cookies automatically.

---

## Security considerations

### Current security posture

The application is suitable for trusted local/LAN tabletop use. It is not a hardened Internet-facing service by default.

Notable properties:

- Session data is in memory.
- No CSRF token is implemented.
- Default cookie uses `secure=False` for HTTP LAN compatibility.
- Plaintext configuration passwords are supported.
- No rate limiting or login lockout is present.
- Uploaded images are extension-validated, not content-sniffed.
- The D&D Beyond lookup makes outbound HTTP requests when enabled.

### Recommended hardening

For anything beyond a trusted LAN:

1. Terminate TLS at a reverse proxy.
2. Change the cookie to `secure=True`.
3. Use scrypt password hashes rather than plaintext passwords.
4. Restrict admin access by IP/VPN/firewall.
5. Run under a dedicated non-root system account.
6. Set restrictive filesystem permissions on configuration and storage directories.
7. Add CSRF protections if exposing browser sessions across untrusted origins.
8. Add upload content validation and file size limits.
9. Disable remote image lookup or route it through a controlled proxy if privacy is a concern.

---

## Known limitations

- One process/worker only; no multi-worker synchronization.
- No database or concurrent edit conflict handling.
- Sessions disappear after restart.
- No deletion UI for individual combatants or saved setups.
- Monster Max HP is not editable through the admin UI.
- Ally state is stored but does not change client styling or game mechanics.
- Character cards are not rendered on the main display stage.
- Client WebSocket endpoint accepts connections without cookie/session validation; the display page itself requires login, but direct WebSocket access is not separately authenticated.
- The state broadcast contains all current combatant data, including hidden monster stat values. The client JavaScript hides fields visually but receives full state.
- Remote D&D Beyond image lookup is fragile by design and may fail.
- The interface is embedded HTML/CSS/JS in one Python source file, which is convenient for deployment but less maintainable than separate static assets.

---

## Extension guidance

### Add entity deletion

Add an admin-only route:

```text
DELETE /api/monsters/{id}
DELETE /api/characters/{id}
```

The handler should:

1. Remove the object from the relevant list.
2. Remove its ID from `battle_order`.
3. Clear it as current turn if applicable.
4. Persist and broadcast via `changed()`.

### Add a database backend

Replace global `STATE` and JSON writes with a repository layer. A minimal interface could include:

```python
class EncounterRepository:
    def load_current(self) -> dict: ...
    def save_current(self, state: dict) -> None: ...
    def list_setups(self) -> list[str]: ...
    def load_setup(self, name: str) -> dict: ...
    def save_setup(self, name: str, state: dict) -> None: ...
```

SQLite is a reasonable first step for single-host durability and queryability.

### Scale to multiple workers

Required changes:

- Move sessions to Redis or signed/stateless cookies.
- Move state/setup persistence to a shared database.
- Broadcast mutations through Redis Pub/Sub or another message bus.
- Add optimistic concurrency/versioning to avoid lost updates.

### Use API tokens for displays

To avoid client login UI for player screens, add a display-specific signed token to the display URL and validate it in both `GET /display` and `/ws`.

### Separate static assets

Move `ADMIN_HTML`, `CLIENT_HTML`, CSS, and JavaScript into versioned files served via `StaticFiles`, or use templates. This supports browser cache-control, testability, linting, and easier UI iteration.

### Improve client-data privacy

Expose a dedicated client state projection that includes only fields allowed on the player display. For example, omit hidden HP, AC, initiative, and unrevealed monsters from the WebSocket payload rather than merely hiding them in CSS/DOM rendering.

### Add automated tests

High-value test targets include:

- `.monster` parsing variants.
- State normalization/migration.
- Death and visibility invariants.
- Character Max HP/reset behavior.
- Turn exclusivity.
- Battle-order validation.
- Setup save/load behavior.
- Setup-name path traversal prevention.
- Admin sorting without battle-order mutation.

---

## Version history summary

| Version | Major additions |
|---|---|
| v1 | Base two-port admin/client display, monsters, characters, WebSocket updates |
| v2 | Alive/dead behavior, battle turn, reset operations, battle controls |
| v3 | Initiative visibility control and readable token text |
| v4 | Monster Ally flag, character HP, character damage/heal |
| v4.1 | Editable character Max HP |
| v4.2 | Character reset preserves active Max HP and heals to it |
| v4.2.1 | Admin-table sorting after Start Battle and Reset All without changing battle order |
| v4.3 | Named New/Save/Load battle setups |
| v4.3.1 | Syntax correction for setup-list sorting |
