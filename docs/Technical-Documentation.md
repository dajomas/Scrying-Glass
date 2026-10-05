# Scrying Glass Technical Documentation

Scrying Glass is a single-process Python/FastAPI application for a game-master-controlled tabletop battle display. It runs separate Admin and Client FastAPI applications in one interpreter, keeps working encounter state in shared memory, persists JSON data, and broadcasts Client Display updates through WebSockets.

## Runtime architecture

```text
Admin browser ── HTTP ──► Admin FastAPI app ── TCP 3000 by default
                                  │
                                  ├── shared STATE
                                  ├── shared SESSIONS
                                  ├── shared SOCKETS
                                  ├── async save lock
                                  └── state.json, campaigns.json, characters/, setups/, uploads/
                                  │
Client browser ── HTTP/WS ► Client FastAPI app ── TCP 4000 by default
```

Run one process and one worker per storage directory. Multi-worker or multi-replica deployments require external shared state, locking, sessions, and pub/sub before they are safe.

## Storage and ownership

For `storage_dir: /var/lib/scrying-glass`:

```text
/var/lib/scrying-glass/
├── state.json
├── campaigns.json
├── characters/
│   └── <campaign-slug>.json
├── uploads/
│   └── <uuid>.<extension>
└── setups/
    └── <campaign-slug>/
        └── <normalized-setup-name>.json
```

| Store | Owner | Contents |
|---|---|---|
| `characters/<campaign>.json` | Campaign | Character roster and character runtime values |
| `setups/<campaign>/<setup>.json` | Battle setup | Monsters, monster-only battle order, activity log, and setup display state |
| `state.json` | Runtime | Working battle order, activity log, display state, active-setup reference, and unsaved monsters when no setup is active |
| `uploads/` | Shared persistent files | Uploaded monster and background images |

`setup_snapshot()` excludes campaign-owned characters and filters the saved battle order to monster IDs. This prevents character records from being copied into every setup snapshot.

### Automatic persistence

Mutation handlers use target-aware persistence under the shared async lock:

```python
async def combatants_changed(
    *,
    monsters: bool = False,
    characters: bool = False,
) -> None:
    async with LOCK:
        if monsters:
            save_active_setup_monsters()
        if characters:
            save_active_campaign_characters()
        save_state()
    await broadcast()
```

- Character mutations persist the active campaign roster.
- Monster mutations persist the active saved setup when one exists.
- If `active_setup` is absent or stale, monster state remains an unsaved encounter in `state.json`; the server does not silently create or overwrite an arbitrary named setup.
- Mixed battle operations save both stores.
- Files are written through temporary-file replacement.

## State model

The normalized root state contains `monsters`, `characters`, `battle_order`, `activity_log`, `display`, and `active_setup`.

A Monster includes:

```json
{
  "id": "uuid-hex",
  "name": "Mimic 1",
  "monster_species": "Mimic",
  "ac": 12,
  "hp": 58,
  "max_hp": 58,
  "original_hp": 58,
  "color": "#842029",
  "image_url": "https://example.invalid/image.png",
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

`monster_species` is the canonical species/type field. Older `monster_type` values are migrated to `monster_species` by state normalization when needed.

## Manual monster API

`POST /api/monsters` accepts multipart form data because the same request may carry an uploaded image.

| Field | Type | Meaning |
|---|---|---|
| `name` | string | Local encounter/display name |
| `monster_species` | string | Canonical creature name/type; used for optional D&D Beyond lookup |
| `ac` | integer | Armor Class |
| `hprangestart` | string | Required fixed HP, numeric lower bound, or dice expression |
| `hprangeend` | string | Optional numeric upper bound; must be blank for dice mode |
| `quantity` | integer | 1 through 50 |
| `color` | string | Monster display color |
| `image` | file | Optional PNG, JPG/JPEG, GIF, or WebP upload |

The Admin form validates input for immediate feedback, but server validation remains authoritative.

### HP resolution

The server resolves HP once per monster inside the quantity loop. It supports:

| Start | End | Factory result |
|---|---|---|
| `17` | blank | `lambda: 17` |
| `10` | `20` | `lambda: random.randint(10, 20)` |
| `3d8+9` | blank | dice roller returning one independent total per call |

Each result initializes `hp`, `max_hp`, and `original_hp`. Dice notation is generation-only; it is not persisted as reset logic. Reset restores the concrete original result and never rerolls.

### Dice grammar

The accepted grammar is:

```text
<count>d<sides>[ optional-space ][ + | - ][ optional-space ]<modifier>
```

Whitespace around the operator is optional. The implementation must accept all of these equivalently:

```text
3d8+9
3d8 +9
3d8+ 9
3d8 + 9
```

The `d` is case-insensitive. Multi-digit die sizes are supported, including `d10`, `d12`, `d20`, and `d100`.

Examples:

```text
1d8
2d10+4
3d20 + 5
1d100-10
```

Validation rules:

- Dice count is a positive integer.
- Die sides must be at least 2.
- Server-side limits protect resources: `MAX_HP_DICE_COUNT = 100`, `MAX_HP_DIE_SIDES = 1000`, and `MAX_HP_MODIFIER = 100000`.
- A dice expression requires an empty `hprangeend`.
- Numeric values must be non-negative whole numbers.
- Numeric start cannot exceed numeric end.
- No `eval()` is used.

The client and server regexes must remain synchronized. A clear implementation is to capture one or more digits for sides and perform the minimum/maximum checks in ordinary validation code.

## D&D Beyond image lookup

`display.dndbeyond_image_lookup` controls optional lookup. It is best effort and must never prevent monster creation.

1. An uploaded `image` wins and is saved under `/media/`.
2. Without an upload, lookup uses `monster_species`, not the local encounter `name`.
3. The monster search response is scanned for exact normalized title matches using the established `<a ... href="/monsters/...">...</a>` matcher.
4. For each exact candidate, legacy preference is computed from the complete matched anchor:

   ```python
   is_legacy = "legacy" in result.group(0).casefold()
   ```

5. Candidates are sorted legacy first:

   ```python
   candidates.sort(key=lambda candidate: not candidate[0])
   ```

6. Each candidate page is fetched in order. The desired image is the dedicated page image carrying `class="monster-image"`, not a generic `og:image` social-media asset.
7. If a legacy candidate has no usable dedicated image, lookup continues to current candidates. If no candidate succeeds, `image_url` remains `None`.

The detail-page markup can place `class` before or after `src`; image extraction must support both attribute orders. Relative and protocol-relative URLs must be normalized before storing them.

The external site’s markup is not an API contract. Keep errors contained inside the optional lookup path, avoid logging full remote HTML in production, and use a manually uploaded image when lookup is unavailable or ambiguous.

## Edit-monster image handling

`monsterEdit(monster)` dynamically renders the edit form in `static/admin.js`.

- When `monster.image_url` is present, the form renders an image thumbnail at the top.
- CSS constrains it with `max-width: min(100%, 300px)` and `max-height: 300px`, preserving aspect ratio.
- The **Replace image** file input uses `URL.createObjectURL(file)` for browser-local preview only.
- The preview does not upload or persist data.
- The existing multipart `POST /api/monsters/{id}/edit` route uploads the selected file only after **Save monster** submits the form.
- Canceling the dialog or reloading the page discards an unsaved replacement selection.

## Browser synchronization

The Client fetches state initially and then consumes authenticated WebSocket state messages. The Admin page reloads authoritative state after mutations.

The manual monster form success branch must:

1. Submit multipart `FormData` to `POST /api/monsters`.
2. Parse/validate the response through the shared `request()` helper.
3. Reset the form after success.
4. Call `await load()` to redraw `#monsters` immediately.
5. Call `paneNotification('monsters', ...)` for local feedback.

Omitting the post-success `load()` leaves the browser list stale until a page reload even though server persistence succeeded.

Pane notifications are browser-only; they are not in state, saved setups, or Client Display messages.

## API inventory

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/state` | Current Admin or Client state for the authenticated application |
| POST | `/api/monsters` | Create manual monsters from multipart data |
| POST | `/api/monsters/import` | Import `.monster` JSON |
| POST | `/api/monsters/import-csv` | Import Monster CSV |
| POST | `/api/monsters/{id}/edit` | Edit Monster with optional image replacement |
| PATCH | `/api/monsters/{id}` | Update Monster state or HP delta |
| POST | `/api/monsters/bulk` | Apply selected-Monster actions |
| POST | `/api/characters` | Create character |
| POST | `/api/characters/import-csv` | Import Character CSV |
| PATCH | `/api/characters/{id}` | Update character |
| POST | `/api/characters/bulk` | Apply selected-Character actions |
| POST | `/api/setups/save` | Explicitly save current working setup under a name |
| POST | `/api/setups/load` | Load named setup into working state |
| POST | `/api/battle/start` | Validate/start battle order |
| POST | `/api/battle/next` | Advance turn |
| POST | `/api/battle/actions` | Apply validated multi-target current-turn actions |

## Operations and security

- Sessions are process-local and disappear on restart.
- Run one worker per storage directory.
- Uploads are extension-checked and statically served; protect the storage directory.
- D&D Beyond lookup requires outbound HTTPS and is best effort.
- Use an HTTPS reverse proxy and revise cookie settings before public exposure.
- Static HTML, JS, CSS, and server code should be deployed together.
- Hard-refresh browser pages after static asset changes.
