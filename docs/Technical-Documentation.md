# Scrying Glass Technical Documentation

Scrying Glass is a single-process Python/FastAPI application with two applications in one interpreter: Admin and Client Display. They share state, sessions, a save lock, and WebSocket connections.

## Source layout

```text
scrying_glass_server.py  FastAPI apps, persistence, routes, parsing, rules
admin_html.py             Admin document shell
client_html.py            Client Display shell
login_html.py             Shared login template
static/admin.js           Admin rendering and API behavior
static/client.js          Client rendering and WebSocket handling
static/*.css              Browser styling
config.example.yaml       Example configuration
```

## Runtime model

```text
Admin browser ── HTTP ──► Admin FastAPI ── TCP 3000
                                  │
                                  ├── STATE / SESSIONS / SOCKETS
                                  ├── asyncio save lock
                                  └── state, campaigns, characters, setups, uploads
                                  │
Client browser ─ HTTP/WS ─► Client FastAPI ─ TCP 4000
```

Run one worker per storage directory. Multiple workers/repli­cas require external shared sessions, data, locks, and pub/sub.

## Storage and ownership

```text
storage_dir/
├── state.json
├── campaigns.json
├── characters/<campaign-slug>.json
├── uploads/<uuid>.<extension>
└── setups/<campaign-slug>/<setup-name>.json
```

| Store | Owner / purpose |
|---|---|
| Campaign character roster | Characters for one campaign |
| Saved setup | Monsters, monster-only battle order, activity log, display state |
| `state.json` | Runtime order/log/display and unsaved working monsters |
| Uploads | Monster and background images |

`setup_snapshot()` removes characters and character IDs from setup battle order. Character data therefore is never duplicated into setup files.

Target-aware persistence saves the correct owner after mutations:

```python
async def combatants_changed(*, monsters=False, characters=False):
    async with LOCK:
        if monsters:
            save_active_setup_monsters()
        if characters:
            save_active_campaign_characters()
        save_state()
    await broadcast()
```

A stale or absent active setup does not get recreated silently. Working monsters remain unsaved runtime state until an explicit setup save.

## Authentication

| App | Cookie |
|---|---|
| Admin | `scrying_glass_admin_session` |
| Client Display | `scrying_glass_client_session` |

Sessions are in memory and disappear on process restart. Admin mutations require an Admin session. Client login accepts client/admin users. Passwords may be plaintext or use `scrypt$<salt_hex>$<digest_hex>`.

## Core state

A Monster contains fields including:

```json
{
  "id": "uuid-hex",
  "name": "Mimic 1",
  "monster_species": "Mimic",
  "ac": 12,
  "hp": 58,
  "max_hp": 58,
  "original_hp": 58,
  "image_url": "/media/example.png",
  "initiative": null,
  "original_initiative": null,
  "show_ac": false,
  "show_hp": false,
  "show_initiative": false
}
```

Older `monster_type` records are normalized to `monster_species` on load.

## Manual monster API

`POST /api/monsters` uses multipart form data:

| Field | Meaning |
|---|---|
| `name` | Encounter/display name |
| `monster_species` | Canonical lookup name/type |
| `ac` | Armor Class |
| `hprangestart` | Required fixed/range/dice HP input |
| `hprangeend` | Optional numeric range end |
| `quantity` | 1–50 copies |
| `color` | Display color |
| `image` | Optional image upload |

The Admin success path uses `request()`, resets the form, calls `await load()`, and sends an Add monster pane notification. Omitting `load()` leaves the Admin list stale despite successful server persistence.

## HP parser and generation

Accepted modes:

| Start | End | Result |
|---|---|---|
| `17` | blank | fixed HP |
| `10` | `20` | inclusive random integer per monster |
| `3d8+9` | blank | independent dice roll per monster |

Dice grammar supports case-insensitive `d`, optional spaces around modifier operators, and multi-digit sides:

```text
3d8+9
3d8 + 9
2d10+4
1d20
1d100-10
```

Server limits: dice count <= 100, die sides <= 1000, modifier absolute value <= 100000. Dice count must be positive and die sides at least 2. Dice mode requires empty `hprangeend`. Numeric inputs must be non-negative whole numbers and start may not exceed end.

Every produced HP total initializes `hp`, `max_hp`, and `original_hp`. Dice notation itself is not persisted; reset uses the stored original result.

## D&D Beyond lookup

`display.dndbeyond_image_lookup` gates optional D&D Beyond lookup.

### Candidate selection

The server searches using canonical `monster_species`, retains exact normalized names from the established anchor matcher, and computes preference from the complete matching anchor:

```python
is_legacy = "legacy" in result.group(0).casefold()
candidates.sort(key=lambda candidate: not candidate[0])
```

Legacy-marked exact candidates are fetched first, then current exact candidates. Lookup failures are caught and must not block manual creation.

### Stat suggestions

`GET /api/dndbeyond/monster-stats?species=...` is read-only and never mutates `STATE`. It returns an exact candidate's AC and HP suggestion when available. D&D Beyond stat markup provides an average and sometimes a dice expression:

```html
<span class="mon-stat-block__attribute-label">Hit Points</span>
<span class="mon-stat-block__attribute-data-value">58</span>
<span class="mon-stat-block__attribute-data-extra">(9d8 + 18)</span>
```

The dice expression is preferred and normalized to `9d8+18`; average HP is fallback.

The Admin species listener debounces lookup, uses the existing Add monster notification area, fills blank AC/HP fields by default, and honors the overwrite checkbox. A returned dice expression fills `hprangestart` and clears `hprangeend`.

### Image lookup

Uploads take precedence. Without an upload, exact candidates are checked for the dedicated `<img class="monster-image">`, accepting either attribute order and normalizing relative/protocol-relative URLs. Do not use generic `og:image` metadata.

## Images and color previews

The dynamic edit form shows existing monster images using a thumbnail constrained to 300px width/height. A selected replacement file is previewed with `URL.createObjectURL()` and persists only after multipart `POST /api/monsters/{id}/edit` succeeds.

Native color picker internals are browser-managed. The Admin therefore renders adjacent color-preview dots using the same marker visual language as combatant rows. Static and dynamic color inputs update their preview dots on both `input` and `change`; dots are display-only and are not API fields.

## Client rendering

Client Display fetches initial state then accepts `/ws` state messages. Active living monsters become cards; visible combatants populate the initiative bar. AC/HP/initiative card fields are separate flags.

Initiative card text appears only when both are true:

```js
monster.show_initiative && monster.initiative !== null
```

The Admin **Init on** toggle changes only the display flag. It does not set initiative, so blank/null initiative is intentionally not rendered.

## Important routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/state` | Authenticated current state |
| GET | `/api/dndbeyond/monster-stats` | Non-persistent D&D Beyond AC/HP suggestion |
| POST | `/api/monsters` | Create manual monsters |
| POST | `/api/monsters/import` | Import `.monster` JSON |
| POST | `/api/monsters/import-csv` | Import Monster CSV |
| POST | `/api/monsters/{id}/edit` | Edit Monster; optional image |
| PATCH | `/api/monsters/{id}` | Partial Monster update / HP delta |
| POST | `/api/monsters/bulk` | Bulk Monster action |
| POST | `/api/characters` | Create Character |
| PATCH | `/api/characters/{id}` | Partial Character update |
| POST | `/api/characters/bulk` | Bulk Character action |
| POST | `/api/setups/save` | Save working setup |
| POST | `/api/setups/load` | Load setup |
| POST | `/api/battle/start` | Start validated order |
| POST | `/api/battle/next` | Advance turn |
| POST | `/api/battle/actions` | Apply current-turn actions |

## Operations

Static HTML/JS/CSS and Python must be deployed as a matching set. Hard-refresh Admin and Client browsers after static changes. Use HTTPS/proxy/VPN restrictions for remote access; sessions are process-local and cookies currently require deployment-specific TLS hardening before public exposure.
