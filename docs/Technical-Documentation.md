> Account storage update: users now live in SQLite (schema v4). The new `superadmin` role manages users; existing `security.users` is a one-time migration input only. See [User management](User-Management.md) for upgrade instructions. This supersedes older configuration-account instructions below.

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
| `python/scrying_glass_storage.py` | Normalized schema-v3 columns/child records, backups, v1/v2 upgrades and CRUD |
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
6. Create uploads, open normalized schema-v3 SQLite, upgrade v1/v2 if present, and import original JSON only when needed.
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

Structured data lives in `storage_dir/scrying-glass.sqlite3`, now schema version 3.
The database stores individual values in typed columns and lists in ID-bearing child
rows; it does not store serialized JSON payloads. Uploaded images remain under
`storage_dir/uploads/`, and configuration remains a YAML/JSON file. JSON API responses
and in-memory dictionaries are unchanged as formats; JSON is not a database storage format.

Campaigns and battle setups have stable integer database IDs. Campaign renames update
one campaign row, without rewriting characters, setups or runtime references. Campaign
IDs are represented as decimal strings in API/form values. The admin frontend uses id,
not slug, for campaign selection. Existing monster/character combatant IDs remain intact.

Upgrades from slug-based SQLite v1 and campaign-ID SQLite v2 are backed up and converted
transactionally to v3. Existing v2 campaign IDs are retained. Original JSON installations
are imported directly into v3 without modifying source files. See
[SQLite migration instructions](SQLite-Migration.md) and [database schema](Database-Schema.sql).

Stop the application before backing up the entire storage directory plus configuration.
Keep matching pre-upgrade code and data for rollback. Archived JSON files are not updated
after import. Use one application process per data directory. sqlite3 is supplied by
Python, not pip; the launchers check its availability before starting.

### Relational model

- campaigns: integer id; name, description, creation and last-used setup columns.
- battle_setups: stable id, campaign_id, name, encounter_id and modification time.
- character_rosters: campaign-owned roster identity, including an explicit empty roster.
- characters: one record per campaign character; database id, combatant_id, position and attributes.
- encounters: scalar settings for saved and runtime encounters, including display/round/turn fields.
- monsters: one record per encounter monster; database id, combatant_id, position and attributes.
- ordered_combatants: one row per battle-order/successor entry, with id, kind and position.
- activity_log_entries: one record per log entry, with id, original event_id, position and scalar fields.
- application_state: singleton id=1, active campaign/runtime encounter and import status/counts.
- migration_runs, migration_campaign_maps, legacy_campaign_maps: historical mapping/upgrade rows.

See Database-Schema.sql for the complete generated CREATE statements. Typed attributes
extension tables store scalar extra properties and field-presence markers as individual
records. These preserve absent-versus-null semantics and compatible extra scalar fields;
they are not JSON blobs or serialized object trees. Unknown nested extras, unsupported
state/display fields and duplicate supplied IDs cause transaction rollback rather than
silent data loss. Missing legacy combatant/log IDs are generated once during import.

Main character/monster properties (HP, AC, initiative, names, visibility, status, images,
etc.) have named columns. Original combatant IDs remain separate from integer storage
record IDs. Record IDs survive edits/reordering through UPSERT by owner and logical ID.
List order uses position, never the record ID. Duplicate ordered references use an
occurrence index so every original list item can survive conversion as a distinct record.
Historical log actor/target and ordered combatant IDs are text references, not foreign
keys into one live combatant table: logs must survive combatant deletion and characters
and monsters occupy separate tables. Ownership relationships do have enforced foreign keys.

Setup and runtime scalar/list records belong to an encounter. Characters remain campaign-
owned and are loaded from the roster. Saved setups remain authoritative for their monsters;
unsaved runtime monsters have their own encounter records. Active and last-used setups
are database-ID references, rebuilt as campaign/name references for the existing service
interface. Setup rename/move preserves its database ID; copy allocates new record IDs.

The campaign API returns id instead of slug. Campaign route parameters, setup request
campaign/from_campaign and move_to query values carry decimal ID strings. Runtime
active_setup is {"campaign_id":"12","name":"fight"}. Hard-refresh admin.js after deployment.

### Transactions and migration

The existing mutation wrapper serializes mutating requests, rolls back SQL and in-memory
STATE on failure, and defers broadcasting until commit. Nested transactions join the outer
unit, not independent savepoints. One connection is owned by the event-loop thread. Media
uploads remain outside database rollback; failed uploads/mutations can leave orphaned files.

Schema-v1/v2 upgrades are backed up then rebuilt in one transaction, retaining v2 campaign
IDs, combatant/event IDs, order, timestamps, rosters, activity records and runtime settings.
Original JSON is read only by the one-time importer and old-schema migration. Database
writes do not serialize JSON. Normal domain startup validation follows a committed schema
upgrade; if it subsequently fails, use the pre-upgrade backup and matching old code to revert.

## Campaign lifecycle and migration

Campaigns use immutable integer IDs. Their names are editable and must be unique under
case-insensitive application checks. New campaigns get an empty default setup and roster.
Setup names still use normalized lowercase names capped at 80 characters, unique per campaign.
Last-used setup selection uses its ID reference, otherwise the newest stored modification time.

The original JSON importer discovers registry/folder campaigns, assigns IDs, imports loose
setups into Default with collision suffixes, seeds absent rosters and leaves every source file
untouched. Existing ID-based databases retain their campaign IDs. Normalized schema-v3 startup
is idempotent. Slugs persist only in historical migration mapping rows, not as live identifiers.

Deleting the last campaign is prohibited. Campaign deletion with setups requires move_to or
delete_setups. Setup deletion opens the next alphabetically, wrapping, or creates empty Default.

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
| PATCH | `/api/campaigns/{campaign_id}` | `update_campaign` | Required |
| DELETE | `/api/campaigns/{campaign_id}` | `delete_campaign` | Required |
| POST | `/api/campaigns/{campaign_id}/activate` | `activate_campaign` | Required |
| POST | `/api/campaigns/{campaign_id}/setups` | `add_setup_to_campaign` | Required |
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
| Missing campaign characters | Query characters through character_rosters and campaign_id |
| Unsuccessful D&D lookup | Upload image/input stats manually; inspect local imports/parser return arity |
| Permission error | Check writable storage_dir and readable package/assets/config |

Uploads are extension-checked, not comprehensively content-validated. They are
not automatically garbage-collected. Sessions are not durable; there is no
built-in rate limiting or distributed synchronization. Deletion is permanent.
