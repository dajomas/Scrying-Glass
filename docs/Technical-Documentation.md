# Scrying Glass Technical Documentation

Scrying Glass is a single-process Python/FastAPI tabletop encounter display. Admin and Client FastAPI applications share in-memory state, persistence helpers, sessions, and WebSocket connections.

## Persistence ownership

```text
storage_dir/
├── state.json
├── campaigns.json
├── characters/<campaign-slug>.json
├── uploads/
└── setups/<campaign-slug>/<setup>.json
```

| Data | Persistent owner |
|---|---|
| Characters | Active campaign roster |
| Monsters | Active saved battle setup, when loaded |
| Unsaved monsters | Working `state.json` state |
| Battle order/activity log/display | Runtime state and setup snapshot as applicable |
| Uploads | Shared `uploads/` directory |

Target-aware mutation persistence saves campaign characters and/or the active setup under one async lock, writes runtime state, then broadcasts. A stale/missing active setup is cleared instead of silently recreating an arbitrary setup.

## Manual monster request

`POST /api/monsters` accepts multipart fields:

| Field | Meaning |
|---|---|
| `name` | Encounter display name |
| `monster_species` | Canonical D&D Beyond lookup name/type |
| `ac` | Armor Class |
| `hprangestart` | Fixed HP, numeric lower bound, or dice expression |
| `hprangeend` | Optional numeric upper bound; empty for fixed/dice HP |
| `quantity` | 1–50 |
| `color` | Display color |
| `image` | Optional image upload |

The browser validates early, but Python is authoritative. On success, the Admin handler must reload `/api/state` and issue an Add monster pane notification so the list updates without a browser refresh.

## HP generation

| Start | End | Per-monster generator |
|---|---|---|
| `17` | blank | Fixed `17` |
| `10` | `20` | Inclusive `random.randint(10, 20)` |
| `3d8+9` | blank | Independent dice roll |

Dice syntax accepts optional modifier whitespace:

```text
3d8+9
3d8 +9
3d8+ 9
3d8 + 9
```

It supports multi-digit sides, including `d10`, `d12`, `d20`, and `d100`. Server limits protect resources: positive count, sides >= 2, `MAX_HP_DICE_COUNT = 100`, `MAX_HP_DIE_SIDES = 1000`, and bounded modifiers. Dice expressions require blank `hprangeend`.

Each generated result is stored as `hp`, `max_hp`, and `original_hp`; reset restores the concrete result and does not reroll.

## D&D Beyond lookup

The optional lookup is controlled by `display.dndbeyond_image_lookup`. It is read-only/convenience behavior and must never prevent manual creation.

### Candidate selection

1. Use `monster_species` as the D&D Beyond monster name.
2. Search the D&D Beyond monster listing.
3. Retain exact normalized title matches from the established anchor matcher:

```python
r'<a\b[^>]*href="(?P<href>/monsters/[^"]+)"[^>]*>' r'(?P<content>.*?)</a>'
```

4. Prefer legacy-marked matching anchors:

```python
is_legacy = "legacy" in result.group(0).casefold()
candidates.sort(key=lambda candidate: not candidate[0])
```

5. Fetch candidates in that order. A missing usable legacy result falls back to the next exact candidate.

### Suggested statistics

The stats suggestion endpoint returns non-persistent AC/HP data after matching a detail page. It extracts D&D Beyond stat-block markup:

```html
<span class="mon-stat-block__attribute-label">Hit Points</span>
<span class="mon-stat-block__attribute-data-value">58</span>
<span class="mon-stat-block__attribute-data-extra">(9d8 + 18)</span>
```

When both are present, return the normalized dice formula `9d8+18` instead of average HP `58`. If no dice formula is available, return the numeric average.

The browser uses the existing Add monster notification area for lookup progress/results. By default, suggestions fill only blank AC and HP fields. The **Overwrite Armor Class and HP Range with found D&D Beyond values** checkbox permits overwriting existing values. A suggested dice expression goes to `hprangestart` and clears `hprangeend`.

### Images

An uploaded file wins. Otherwise, lookup extracts the dedicated `<img class="monster-image">` on the matched monster page rather than generic `og:image` metadata. The extractor must accept either `class`/`src` attribute order and normalize relative/protocol-relative image URLs.

## Edit image preview

The dynamically generated Monster edit form renders `image_url` as a thumbnail constrained to 300px maximum width/height. Selecting **Replace image** creates a browser-local `URL.createObjectURL()` preview only. The selected file is uploaded only through multipart `POST /api/monsters/{id}/edit` after **Save monster**.

## Client initiative rendering

The Client card renderer independently supports AC, HP, and initiative fields. Initiative appears only when:

```js
monster.show_initiative && monster.initiative !== null
```

The Admin **Init on** control changes only `show_initiative`; it does not assign an initiative value. Therefore the monster must first have a numeric initiative. A blank/null initiative is intentionally omitted from the Client card.

## Client synchronization

The Client fetches initial state and receives live WebSocket state messages. The Client card stage contains active living monsters. Visibility controls initiative-bar entries separately from card-field visibility. Static asset changes require browser hard refresh.

## Operations

- Run one process/worker per storage directory.
- Sessions are process-local and disappear on restart.
- D&D Beyond lookup requires outbound HTTPS and is fragile external HTML scraping; contain exceptions and fall back to manual entry/upload.
- Deploy matching Python, HTML, JavaScript, and CSS versions.
- Use a trusted network, HTTPS reverse proxy/VPN restrictions, and strong credentials for remote deployment.
