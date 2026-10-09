# Scrying Glass Technical Documentation

This document describes the split architecture agreed on 6 October 2026. See
[README](../README.md), [User Guide](User-Guide.md) and
[Systemd Deployment](Systemd-Deployment.md). No new release version is implied.

## Source layout

```text
repository/
├── scrying_glass_server.py       # Entry point, runtime context, apps and startup
├── python/
│   ├── __init__.py
│   ├── scrying_glass_services.py # Service installation/binding
│   ├── scrying_glass_service_*.py
│   ├── scrying_glass_api_admin.py
│   ├── scrying_glass_admin_*.py
│   ├── scrying_glass_api_client.py
│   ├── scrying_glass_classes.py
│   └── ...helper modules...
├── web_html/
│   ├── __init__.py
│   ├── admin_html.py            # ADMIN_HTML fragment loader
│   ├── client_html.py
│   └── login_html.py
├── templates/
│   └── admin/                  # 20 ordered HTML fragments
├── static/                     # Admin/client/login CSS and browser JavaScript
├── config.example.yaml
├── run.sh                      # Existing launcher, if used
└── docs/
```

## Runtime context and services

The root server owns CONFIG, STATE, LOCK, SESSIONS, SOCKETS, storage paths and
the two FastAPI applications. It retains the imported helpers and request-model
names needed by API handlers and annotation resolution.

`install_services(sys.modules[__name__])` creates nine service instances and
binds their methods onto the server module before API registration or startup
operations. The module remains the live context; it is not a state snapshot.

| Module | Responsibility |
|---|---|
| `python/scrying_glass_service_auth.py` | Configured-user lookup and cookie authorization dependencies |
| `python/scrying_glass_service_state.py` | Encounter normalization, lookup, public state and active setup references |
| `python/scrying_glass_service_campaigns.py` | Campaign metadata, setup paths and activation |
| `python/scrying_glass_service_migrations.py` | Non-destructive one-time legacy JSON import |
| `python/scrying_glass_storage.py` | SQLite schema, transactions and structured-data CRUD |
| `python/scrying_glass_database_transactions.py` | Mutating request serialization, rollback and post-commit broadcasting |
| `python/scrying_glass_service_persistence.py` | Campaign rosters, setup/state loading and writes |
| `python/scrying_glass_service_activity.py` | Battle action and direct HP-change log records |
| `python/scrying_glass_service_images.py` | Uploaded images, remote image lookup and monster construction |
| `python/scrying_glass_service_battle.py` | Battle order, initiative, activation and turn progression |
| `python/scrying_glass_service_notifications.py` | Save helpers, lock handling and WebSocket broadcasting |

Services call one another through self.context. In particular, state replacement
must assign self.context.STATE, not a local STATE variable. Services do not
import the root server, and the API classes receive the same live context.
The split changes ownership of code, not ownership of data.

## API composition

AdminAPI combines nine mixins from `scrying_glass_admin_<domain>.py`: pages,
display, setups, campaigns, monsters, characters, combatants, battle and activity.
The coordinator registers an explicit 41-route manifest in the original order.
Mixin files define handlers; they do not register routes independently.
ClientAPI retains its separate page, login, state and WebSocket handlers.

Handler annotations are resolved with get_type_hints using vars(context), so
FastAPIRequest, UploadFile, WebSocket, Response and request models must exist
in the root server namespace before constructing the API objects. Protected
admin routes attach Depends(context.require(...)) at registration time.

## Package imports

The root server uses absolute imports:

```python
from python.scrying_glass_services import install_services
from python.scrying_glass_api_admin import AdminAPI
from python.scrying_glass_api_client import ClientAPI
from web_html.admin_html import ADMIN_HTML
```

Sibling imports inside python use relative names, for example:

```python
from .scrying_glass_service_auth import AuthService
from .scrying_glass_admin_pages import AdminPagesMixin
```

The initialization helper imports the separate HTML package absolutely:

```python
from web_html.login_html import LOGIN
```

Standard-library and third-party imports are unchanged. Do not import a module
both as a bare name and as python.<name>; keep one consistent identity.
Do not add package directories to sys.path as a substitute for package imports.

## HTML and browser assets

web_html/admin_html.py exports ADMIN_HTML by concatenating 20 UTF-8 files in an
explicit order. With root templates/admin, its path is:

```python
_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "admin"
```

Fragments cover document framing, pane and battle controls, four input panes,
two display panes, the activity log and nine dialogs. They are partial markup,
not independent documents. The monster-display fragment closes the main element.
Fragment contents are trusted local files. Missing fragments fail during import.
HTML loads once; restart after edits. This is not a Jinja template system.

Client and login HTML remain in web_html modules. CSS/JavaScript are served
from root static/. Keep assets, markup IDs and browser handlers synchronized.
Do not publicly mount templates merely to assemble the page.

## Startup and execution

1. Import packages, helpers, models and HTML.
2. Create runtime state/context and bind services.
3. Construct Admin/Client apps and register routes.
4. Under the main guard, parse CLI arguments and load YAML/JSON configuration.
5. Apply overrides and resolve storage/static paths.
6. Create uploads, open SQLite and import legacy JSON once in a startup transaction.
7. Load state and the active campaign's authoritative character roster.
8. Clean order, save state, mount assets/media and start both Uvicorn servers.

Launch the root script directly. An external uvicorn module:app command imports
the module but skips steps under the main guard. One process shares state,
sessions, sockets and a lock; multiple workers or replicas are unsupported
without an external state/session store and update synchronization.

## Configuration

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
      password: "replace-with-a-strong-admin-password"
    - username: "table"
      role: "client"
      password: "replace-with-a-strong-client-password"

display:
  background: "#080b14"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  dndbeyond_image_lookup: true
```

CLI overrides are --config, --bind, --admin-port, --client-port and --storage-dir.
Configuration is merged with defaults. Relative storage_dir is resolved from
the working directory; HTML/static paths are relative to their source files.
Use absolute storage/configuration paths for a service deployment.

The configured display.background is the initial/fallback background. Working
and saved encounters carry their own display.background. dndbeyond_image_lookup
also gates optional monster stat suggestions. Remote failures do not block
manual creation. Passwords may be plaintext or scrypt$<salt_hex>$<digest_hex>.

## Persistence

Structured data is stored in `storage_dir/scrying-glass.sqlite3`. Uploaded monster
and background images remain in `storage_dir/uploads/`; configuration remains
in the existing YAML/JSON configuration file. SQLite uses Python's standard-library
`sqlite3` module, so no database server or additional dependency is required.

Campaign metadata, campaign-owned character rosters, named monster encounters,
and runtime state have separate database records. Existing dictionary/snapshot
formats remain JSON payloads inside SQLite. Saved setups remain authoritative for
their monsters; runtime state stores the active setup reference, active-turn marker,
battle round, successor lists, activity log, display settings and unsaved monsters.

The first startup imports existing `campaigns.json`, `characters/*.json`,
`setups/<campaign>/*.json`, loose `setups/*.json`, and `state.json`. It leaves all
source files untouched. Import and startup validation share a transaction; invalid
input aborts startup instead of silently skipping data. A database marker prevents
subsequent re-imports. Once imported, the old JSON files are archival copies, not
live data: do not edit them expecting the running application to change.

Stop the server before copying the entire storage directory and configuration.
The backup must include the database and uploaded images. Keep the pre-migration
backup for rollback. See [SQLite migration instructions](SQLite-Migration.md).

### SQLite schema and transactions

- `campaigns(slug, metadata_json)` stores campaign identity and metadata.
- `campaign_characters(campaign_slug, characters_json)` stores the campaign roster.
- `battle_setups(campaign_slug, name, snapshot_json, updated_at)` stores named encounters.
- `application_state(key, value_json)` stores the active campaign, runtime state and import marker.

The setup key is `(campaign_slug, name)`. Foreign keys cascade campaign slug
renames and campaign deletion to its setups/roster. Schema version is tracked by
`PRAGMA user_version`; unsupported versions fail rather than being overwritten.
Parameterized statements are used for values. Setup modification times are imported
and retained for the existing newest-setup fallback; explicit last_setup wins.

The server owns one SQLite connection on its event-loop thread. Mutating authenticated
admin requests are serialized by a separate operation lock and use `BEGIN IMMEDIATE`.
Specialized notification persistence operations join the request transaction or start
one when invoked directly. Nested transactions join the outer transaction (they are
not independent savepoints). Exceptions propagate to the outer transaction, which
rolls back the database and restores the pre-request in-memory state. Notifications
are deferred until commit. Uploaded files are outside SQL transactions: a failed
request can leave an unreferenced upload, but must not delete a previously referenced image.

This is not a multi-process runtime-state design. Use one process per data directory.
Synchronous database operations run on the event loop; no thread-shared connection
or ORM is introduced. This favors simplicity for the existing small single-GM app.

## Campaign lifecycle and migration

Campaign/setup names become lowercase slugs capped at 80 characters. New
campaigns receive an empty default setup and a character roster. Activation
opens last_setup if present, otherwise the newest setup by modification time;
no setup means no replacement is loaded by open_campaign_setup.

The one-time import copies loose setups/*.json into Default database records, adds numeric collision
suffixes, registers discovered campaign folders, and ensures a valid active campaign.
Missing campaign character rosters are seeded from an appropriate legacy
setup, or initialized empty. Existing rosters are not overwritten by migration.

Deleting the last campaign is prohibited. For a campaign with setups, select
move_to or delete_setups, not both. Deleting a setup opens the next alphabetic
setup (wrapping); an empty campaign receives a fresh default setup.

## Authentication

Admin and Client cookies are scrying_glass_admin_session and
scrying_glass_client_session. Login creates an in-memory token/role record;
restart clears sessions. Admin login requires admin role, while Client accepts
client or admin. Legacy cookies are removed after successful login.
Cookies currently use httponly and SameSite=lax with secure=False. Reassess TLS,
cookie policy, CSRF protection and access controls before public exposure.
The Client state payload exposes encounter data even when visually hidden.

## Admin route inventory

| Method | Path | Handler | Admin authentication |
|---|---|---|---|
| GET | `/login` | `admin_login_get` | Login/page handling |
| POST | `/login` | `admin_login_post` | Login/page handling |
| GET | `/` | `admin_home` | Login/page handling |
| GET | `/api/state` | `admin_get_state` | Required |
| GET | `/api/dndbeyond/monster-stats` | `dndbeyond_monster_stats` | Required |
| PATCH | `/api/display/background` | `update_display_background` | Required |
| POST | `/api/display/background-image` | `upload_display_background_image` | Required |
| GET | `/api/setups` | `get_setups` | Required |
| GET | `/api/campaigns` | `get_campaigns` | Required |
| POST | `/api/campaigns` | `create_campaign` | Required |
| PATCH | `/api/campaigns/{slug}` | `update_campaign` | Required |
| DELETE | `/api/campaigns/{slug}` | `delete_campaign` | Required |
| POST | `/api/campaigns/{slug}/activate` | `activate_campaign` | Required |
| POST | `/api/campaigns/{slug}/setups` | `add_setup_to_campaign` | Required |
| POST | `/api/setups/new` | `new_setup` | Required |
| POST | `/api/setups/save` | `save_setup` | Required |
| POST | `/api/setups/load` | `load_setup` | Required |
| POST | `/api/setups/rename` | `rename_setup` | Required |
| DELETE | `/api/setups/{name}` | `delete_setup` | Required |
| POST | `/api/setups/import` | `import_setup` | Required |
| POST | `/api/monsters/roll-initiative` | `roll_monster_initiative` | Required |
| POST | `/api/monsters` | `create_monster` | Required |
| POST | `/api/monsters/import` | `import_monster` | Required |
| POST | `/api/monsters/import-csv` | `import_monsters_csv` | Required |
| POST | `/api/characters/import-csv` | `import_characters_csv` | Required |
| POST | `/api/monsters/{ident}/edit` | `edit_monster` | Required |
| PATCH | `/api/monsters/{ident}` | `update_monster` | Required |
| POST | `/api/characters` | `create_character` | Required |
| PATCH | `/api/characters/{ident}` | `update_character` | Required |
| DELETE | `/api/combatants/{ident}` | `delete_combatant` | Required |
| POST | `/api/combatants/{ident}/reset` | `reset_one_combatant` | Required |
| POST | `/api/characters/bulk` | `bulk_characters` | Required |
| POST | `/api/monsters/bulk` | `bulk_monsters` | Required |
| POST | `/api/battle/end` | `battle_end` | Required |
| POST | `/api/battle/reset-all` | `reset_all` | Required |
| POST | `/api/battle/start` | `battle_start` | Required |
| POST | `/api/battle/next` | `battle_next` | Required |
| POST | `/api/battle/actions` | `apply_battle_actions` | Required |
| GET | `/api/activity-log.json` | `export_activity_log_json` | Required |
| GET | `/api/activity-log.csv` | `export_activity_log_csv` | Required |
| POST | `/api/activity-log/clear` | `clear_activity_log` | Required |

The existing client routes are GET / (login/display redirect), GET/POST /login,
GET /display, authenticated GET /api/state, and authenticated WebSocket /ws.
Both apps mount /static and /media during direct-script initialization.

## Request contracts

- Campaign create/update use name/description; create may activate the campaign.
- Setup save/load use name and optional campaign. Rename adds new_name.
- Setup import requires kind="monsters"; characters cannot be imported from setups.
- Monster creation is multipart: name, monster_species, ac, hprangestart,
  optional hprangeend, color, quantity (1..50) and optional image.
- Monster/character CSV upload uses csv_file; .monster upload uses monster_file.
- Bulk actions use {action, ids}; monster actions include join/leave battle,
  ally flags, stat visibility, reset and remove. Character actions include
  join/leave battle, reset and remove.
- Battle start supplies order; actions supply actor_id and action rows with
  target_id, action and an amount for damage/heal only.
- Background updates use {background}; background-image uploads use image.

CSV is UTF-8 (BOM accepted), has a header and at least one nonblank data row.
Monster columns require name, monster_species (or type), ac and hp; character
CSV requires name. Blank IDs receive generated UUIDs. Duplicate/conflicting
IDs are rejected. Boolean values support true/false, yes/no, y/n, on/off, 1/0.
The .monster parser reads compatible JSON name/type/AC/HP fields.

## Combat, logs and synchronization

Battle start validates every active living combatant appears exactly once in
order. Individual activation during battle can insert a combatant by initiative;
equal initiatives follow existing equals. Turn advancement filters eligibility,
adds omitted eligible IDs, cycles through order and clears turns if none remain.
Bulk and individual handlers retain their existing distinct behavior.

Actions validate all rows before applying them. Actor must be active, alive and
in turn; targets must be active/alive. Damage/heal require positive amounts;
buff/debuff are logged without HP changes or amounts. This validation-first
behavior is not database transactionality or concurrency isolation.
Direct HP deltas are also logged; without a current actor the log uses System.

WebSockets receive JSON {"type":"state","state":...}. Notifications broadcast
public_state and discard failed connections. The Admin refreshes state following
mutations. The lock protects save-helper operations, not every handler read,
validation or mutation; concurrent admins have no conflict/version resolution.

## Development checks

```bash
.venv/bin/python -m compileall -q scrying_glass_server.py python web_html
.venv/bin/python -c "from web_html.admin_html import ADMIN_HTML; print('HTML loaded:', len(ADMIN_HTML), 'characters')"
.venv/bin/python -c "import scrying_glass_server; print('Server import passed')"
```

Import checking requires the virtual environment and all fragment files.
After structural changes, test both logins, all campaign/setup transitions,
CSV/.monster imports, individual/bulk controls, battle actions, log exports,
WebSocket updates, backgrounds and restart persistence. AST/syntax checks do
not replace full runtime and browser tests.

## Limitations and troubleshooting

| Symptom | Investigation |
|---|---|
| Missing uvicorn/FastAPI | Use .venv/bin/python; inspect packages in that interpreter |
| Missing local module | Check package prefixes, sibling relative imports and deployed files |
| Missing HTML fragment | Check root templates/admin and loader parent.parent path |
| Old UI | Restart for HTML edits, then hard-refresh CSS/JavaScript |
| Missing campaign characters | Check campaign_characters in SQLite, not setup snapshots |
| Unsuccessful D&D lookup | Upload image/input stats manually; inspect local imports/parser return arity |
| Permission error | Check writable storage_dir and readable package/assets/config |

Uploads are extension-checked, not comprehensively content-validated. They are
not automatically garbage-collected. Sessions are not durable; there is no
built-in rate limiting or distributed synchronization. Deletion is permanent.
