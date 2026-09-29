# Monster Display Technical Documentation

Monster Display is a single-process Python/FastAPI application for a GM-controlled tabletop battle display. It runs distinct Admin and Client FastAPI applications, keeps their encounter state in shared process memory, persists the state as JSON, and sends Client Display updates through WebSockets.

See the [README](../README.md) for installation and [User Guide](User-Guide.md) for feature use.

## Source layout

The current project keeps server logic in one primary module and separates the embedded browser UIs into Python modules:

```text
monster_display_server.py  # FastAPI apps, state, models, rules, routes, startup
admin_html.py              # ADMIN_HTML: Admin HTML, CSS, JavaScript
client_html.py             # CLIENT_HTML: Client HTML, CSS, JavaScript
login_html.py              # LOGIN: shared login form
config.example.yaml        # Example deployment configuration
```

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

Both apps run in one interpreter and therefore share in-memory data. Run the service as **one process with one worker**. Multi-worker or multi-replica deployments require externally shared state, sessions, locks, and pub/sub synchronization before they are safe.

## Dependencies

```bash
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

The implementation also uses standard-library modules such as `asyncio`, `copy`, `csv`, `datetime`, `hashlib`, `hmac`, `io`, `json`, `random`, `re`, `secrets`, `shutil`, `uuid`, and `pathlib`.

## Configuration

Configuration may be YAML or JSON. CLI values override matching configuration values.

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

| Key | Purpose |
|---|---|
| `network.bind` | Host/interface used by both services |
| `network.admin_port` | Admin listener, default 3000 |
| `network.client_port` | Client listener, default 4000 |
| `storage_dir` | Parent directory for state, the campaign registry, setup snapshots, and uploads |
| `security.users` | Username, role, and plaintext/scrypt password records |
| `display.background` | CSS color, gradient, or image URL |
| `display.entry_direction` | `from_bottom` or `from_top` |
| `display.exit_direction` | `to_bottom` or `to_top` |
| `display.monster_width_percent` | Retained display sizing configuration |
| `display.dndbeyond_image_lookup` | Enables optional remote image lookup |

Example CLI:

```bash
python3.14 monster_display_server.py \
  --config /etc/monster-display/config.yaml \
  --bind 0.0.0.0 \
  --admin-port 3000 \
  --client-port 4000 \
  --storage-dir /var/lib/monster-display
```

## Authentication

Login generates an in-memory session token using `secrets.token_urlsafe(32)`. Session records hold the username and role.

The two applications use different cookie names:

| Application | Cookie |
|---|---|
| Admin | `monster_admin_session` |
| Client Display | `monster_client_session` |

Cookies are scoped by hostname rather than port, so the separate names allow both applications to be signed into in the same browser. The legacy `monster_session` cookie is deleted on successful login.

Admin-only mutation routes use:

```python
Depends(require("admin", ADMIN_SESSION_COOKIE))
```

Client state routes and WebSocket connections validate the Client cookie. The Client login accepts both `client` and `admin` users.

Passwords may be plaintext or scrypt values:

```text
scrypt$<salt_hex>$<digest_hex>
```

Generate a hash with:

```bash
python3.14 -c 'from monster_display_server import password_hash; print(password_hash("replace-me"))'
```

Sessions are lost at process restart.

## Persistence

For `storage_dir: /var/lib/monster-display`:

```text
/var/lib/monster-display/
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
| `state.json` | Working encounter, battle order, and activity log |
| `campaigns.json` | Campaign registry: active campaign, names, descriptions, most recently worked on setup |
| `uploads/` | Uploaded monster images, mounted at `/media/` |
| `setups/<campaign-slug>/` | Named full-state JSON snapshots belonging to one campaign |

State writes use a temporary file followed by replacement:

```python
temp = STATE_FILE.with_suffix(".tmp")
temp.write_text(json.dumps(STATE, indent=2), encoding="utf-8")
temp.replace(STATE_FILE)
```

Setup and campaign names are normalized to safe lower-case slugs limited to 80 characters. A campaign slug is also its folder name under `setups/`.

## Campaigns

### Registry

`campaigns.json` is written atomically in the same way as `state.json`:

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
    },
    "curse-of-strahd": {
      "name": "Curse of Strahd",
      "description": "Barovia",
      "created": "2026-09-29T06:10:00+00:00"
    }
  }
}
```

| Field | Meaning |
|---|---|
| `active` | Slug of the active campaign; setup routes without a `campaign` value use it |
| `name` / `description` | Display name and optional description |
| `created` | Creation timestamp (UTC, ISO 8601) |
| `last_setup` / `last_setup_at` | Most recently worked on setup, updated on save, load, and automatic opening |

### Migration of unconnected setups

`migrate_unassigned_setups()` runs at startup, on `GET /api/campaigns` and `GET /api/setups`, and before every campaign mutation. It:

1. Moves every `*.json` file found directly in `setups/` (the pre-campaign layout) into `setups/default/`, creating the **Default** campaign when needed. Name clashes get `-2`, `-3`, … suffixes. Moved setups are logged and returned as `moved`.
2. Registers campaign folders that have no registry entry, and recreates folders for registry entries without one.
3. Guarantees that at least one campaign exists and that `active` names an existing campaign.

When the migration creates **Default**, it also writes an empty `default` setup, unless a moved setup already uses that name, and records the most recently modified moved setup as `last_setup`.

### New campaigns and the empty default setup

`create_default_setup(slug)` writes an empty normalized state as `default.json` into a campaign folder when that file does not exist. It is called for every newly created campaign.

### Opening a setup on activation

`open_campaign_setup(slug)` loads a setup into `STATE`, records it with `remember_setup()`, and calls `changed()`. The setup is chosen by `pick_campaign_setup()`:

1. `last_setup`, if the file still exists.
2. Otherwise the setup file with the newest modification time.
3. `None` when the campaign has no setups; the working state is left unchanged.

It runs when a campaign is created with `activate: true`, when a campaign is activated, and when the active campaign is deleted. The responses of those routes include `opened_setup`.

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

`normalize_state()` fills missing fields in older states/setups and discards battle-order IDs that do not identify a loaded entity.

### Monster

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

### Character

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

### Activity log entry

```json
{
  "id": "uuid-hex",
  "timestamp": "2026-09-28T00:00:00+00:00",
  "active_combatant_id": "uuid-or-null",
  "active_combatant": "Ice Guard",
  "active_combatant_state": "alive",
  "target_combatant_id": "uuid",
  "target_combatant": "Aelwyn",
  "target_combatant_state": "alive",
  "action": "damage",
  "amount": 7
}
```

Actions are `damage`, `heal`, `buff`, and `debuff`. Buff/Debuff actions store `null` for `amount`.

## State changes and synchronization

Mutation handlers call `changed()` to save and broadcast the public state:

```python
async def changed() -> None:
    async with LOCK:
        save_state()
    await broadcast()
```

`broadcast()` sends a JSON message of the form:

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

The Client Display fetches `/api/state` at startup and then renders WebSocket state messages. The Admin UI refreshes from `/api/state` after mutations.

## Route inventory

Unless stated otherwise, Admin mutation routes require the Admin session cookie and Admin role.

### Pages, state, and socket

| App | Method | Path | Purpose |
|---|---|---|---|
| Admin | GET/POST | `/login` | Admin login |
| Admin | GET | `/` | Admin UI |
| Client | GET/POST | `/login` | Client/admin login |
| Client | GET | `/display` | Client Display UI |
| Admin | GET | `/api/state` | State for Admin session |
| Client | GET | `/api/state` | State for Client session |
| Client | WebSocket | `/ws` | Authenticated live Client updates |

### Campaign routes

| Method | Path | Body / query | Purpose |
|---|---|---|---|
| GET | `/api/campaigns` | – | Run the migration; return `active`, `campaigns` (slug, name, description, created, setups, last_setup), and `moved` |
| POST | `/api/campaigns` | `{name, description?, activate?=true}` | Create a campaign with an empty `default` setup; when activated, open it and return `opened_setup`. HTTP 409 if the slug exists |
| PATCH | `/api/campaigns/{slug}` | `{name?, description?}` | Rename or edit; a changed slug renames the folder. HTTP 409 if the new slug exists |
| DELETE | `/api/campaigns/{slug}` | `?move_to=<slug>` or `?delete_setups=true` | Delete a campaign. If it has setups, exactly one of the two options is required (HTTP 409 when missing, 400 when both). Returns `moved`, `deleted_setups`, and `opened_setup` when the active campaign was deleted. The last campaign cannot be deleted (HTTP 400) |
| POST | `/api/campaigns/{slug}/activate` | – | Make the campaign active and open its most recently worked on setup (`opened_setup`) |
| POST | `/api/campaigns/{slug}/setups` | `{setup, from_campaign, mode: "move" or "copy"}` | Add a setup from another campaign; name clashes get a numeric suffix. Returns `setup` and `campaign` |

### Setup routes

Every setup route accepts an optional `campaign` (slug). When omitted, the active campaign is used. An unknown campaign returns HTTP 404.

| Method | Path | Body / query | Purpose |
|---|---|---|---|
| GET | `/api/setups` | `?campaign=` | List setup names of a campaign; returns `{campaign, names}` |
| POST | `/api/setups/new` | – | Replace working state with blank state |
| POST | `/api/setups/save` | `{name, campaign?}` | Save complete state under a normalized name; records `last_setup` |
| POST | `/api/setups/load` | `{name, campaign?}` | Replace working state with saved state; records `last_setup` |
| POST | `/api/setups/rename` | `{name, new_name, campaign?}` | Rename a setup; HTTP 409 if the new name exists. `last_setup` follows the rename |
| DELETE | `/api/setups/{name}` | `?campaign=` | Delete a setup and open the next one alphabetically (wrapping to the first); when none remain, create and open an empty `default`. Returns `deleted`, `opened_setup`, `created_default` |
| POST | `/api/setups/import` | `{name, kind, campaign?}` | Append setup combatants as new runtime-reset copies retaining current HP/max HP |

### Monster and character routes

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/monsters` | Create one or more monsters by multipart form |
| POST | `/api/monsters/import` | Import a `.monster` file |
| POST | `/api/monsters/import-csv` | Import monster CSV |
| POST | `/api/monsters/roll-initiative` | Assign d20 initiative to every monster |
| POST | `/api/monsters/bulk-toggle` | Toggle a supported monster field across all monsters |
| POST | `/api/monsters/{id}/edit` | Multipart monster edit with optional replacement image |
| PATCH | `/api/monsters/{id}` | JSON monster field update / HP delta |
| POST | `/api/characters` | Create character |
| POST | `/api/characters/import-csv` | Import character CSV |
| PATCH | `/api/characters/{id}` | JSON character field update / HP delta |
| DELETE | `/api/combatants/{id}` | Permanently remove monster or character from current encounter |
| POST | `/api/combatants/{id}/reset` | Reset one combatant |

The Monster bulk field must be one of `active`, `ally`, `show_ac`, `show_hp`, or `show_initiative`.

### Battle and activity-log routes

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/battle/reset-all` | Reset every combatant and clear `battle_order` |
| POST | `/api/battle/start` | Start a battle using validated full ordered IDs |
| POST | `/api/battle/next` | Advance to next eligible combatant |
| POST | `/api/battle/actions` | Atomically apply current-turn multi-target actions |
| GET | `/api/activity-log.json` | Download full log as JSON |
| GET | `/api/activity-log.csv` | Download full log as CSV |
| POST | `/api/activity-log/clear` | Clear all log records |

## Import contracts

CSV data must be UTF-8, with BOM accepted, must include a header row, and must contain at least one nonblank row. Headers are trimmed and case-folded. Boolean fields accept `true`/`false`, `yes`/`no`, `on`/`off`, and `1`/`0`.

Monster CSV requires `name`, `monster_type` or `type`, `ac`, and `hp`. Character CSV requires `name`. Missing or blank IDs receive a generated UUID hex value. Duplicate CSV IDs and IDs already present in the working encounter return HTTP 400.

Setup import deep-copies selected combatants, generates fresh IDs, preserves source `hp` and `max_hp`, derives `alive` from current HP, restores `initiative` from `original_initiative`, clears active/visible/turn flags, and does not modify the current battle order.

### `.monster` files

The `.monster` import route accepts a UTF-8 JSON file and extracts usable values for:

- `name`
- `type`
- Armor Class from supported AC-related fields
- Hit Points from the supported HP text/value fields

The [Tetra-cube D&D 5e Statblock Generator](https://tetra-cube.com/dnd/dnd-statblock.html) is a recommended external authoring tool for compatible monster statblocks. Monster Display does not bundle, control, or depend on the Tetra-cube site at runtime; it only accepts an uploaded `.monster` file.

## Combat rules

### Battle start and ties

`begin_battle()` requires the supplied order to contain each active living combatant exactly once. Admin-side code builds the order by descending initiative and opens a tie dialog for equal numeric initiatives.

### Activation during battle

`insert_into_battle_order()` places a newly active living combatant in an existing order:

- Before lower numeric initiatives.
- After current entries at the same initiative.
- Before initiative-less entries when numeric.
- After numeric entries when initiative-less.

### Turn advancement

`advance_turn()` filters inactive/dead entries, adds omitted eligible combatants in initiative order, then advances cyclically. When no eligible combatants remain, it clears both turn state and `battle_order`.

### Current-turn actions

`/api/battle/actions` validates all requested rows before applying any changes. It requires an active, living actor currently marked `in_turn` and active/living targets. Damage and Heal require a positive integer amount; Buff and Debuff must not carry one. Every applied row produces an activity-log entry.

### Deletion

`DELETE /api/combatants/{id}` removes the entity from its list and removes its ID from `battle_order`. It does not delete uploads, because uploaded images may be referenced by saved setups or other entries.

## Client rendering

The Client Display renders visible initiative tokens and active living Monster cards. Character entries participate in the initiative bar but not in full card rendering.

- Cards use an adaptive grid.
- Enabled AC, HP, and initiative values are placed in card text.
- Text sits on an opaque contrast-aware panel so it remains readable over images.
- Ally monsters are displayed with the ` - Ally` suffix without changing stored `name`.
- The initiative bar becomes `hidden` when empty and CSS expands the stage to full viewport height.
- Image backgrounds are assigned as background images centered with `cover`, no repetition, and fixed attachment.

The Admin Monster and Character tables show a colored dot in front of each name. `colorMarker(combatant, fallback)` in `admin_html.py` renders it with the `.turn-marker` class also used for the current turn in the battle order line. It falls back to `#842029` for monsters and `#1f4e79` for characters when no color is stored.

The Admin Monster table uses a presentation-only sort: active first; active battle order when battle is active; active Max HP outside battle; then inactive numeric initiative and Max HP ordering. This does not change persisted list order or battle order.

## Security and limitations

- Cookies currently use `secure=False`; terminate TLS at a reverse proxy and revise cookie settings before internet exposure.
- Sessions exist only in memory and disappear at restart.
- No built-in CSRF protection, rate limiting, authorization audit trail, or multi-user concurrency coordination exists.
- Client state contains encounter data even when some details are not visually rendered; Client access should be treated as access to encounter state.
- Uploaded images are extension-checked and statically served. Restrict filesystem permissions and deployment reachability.
- D&D Beyond image lookup is best effort and dependent on external site behavior.
- Deleting a saved setup or a campaign with `delete_setups=true` is permanent; there is no recycle bin. Back up `storage_dir` regularly.
- Campaign and setup operations are not coordinated between several Admin browsers; the last action wins.

## Operations

Validate syntax after updates:

```bash
python3.14 -m py_compile monster_display_server.py admin_html.py client_html.py login_html.py
```

Minimal `systemd` unit:

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

Run as a non-root account that can read configuration and write `storage_dir`.

## Troubleshooting

| Symptom | Check |
|---|---|
| UI appears outdated | Hard-refresh after embedded HTML changes |
| Cannot keep Admin and Client logged in | Confirm the new separate cookie names are in use; clear old cookies and log in again |
| Client does not update | Verify port 4000 and reconnect the WebSocket by refreshing |
| CSV import fails | Check encoding, header, required fields, numeric values, and ID uniqueness |
| Setup import HP looks wrong | Confirm source saved state contains the expected current HP; current HP/max HP are preserved on import |
| Image lookup fails | Upload an image directly |
| Saved setups missing after upgrading | Setups from the pre-campaign layout were moved to `setups/default/`; check the startup log line `Moved N unassigned battle setup(s)…` |
| Campaign missing from the list | Check `campaigns.json`; folders under `setups/` without a registry entry are registered automatically on the next list request |
