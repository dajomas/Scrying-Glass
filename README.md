# Scrying Glass

Scrying Glass is a self-hosted tabletop encounter manager: the game master uses
an authenticated Admin interface while players watch a separate live Client
Display. Both FastAPI applications run in one Python process, persist structured data in
SQLite (schema v4), and share encounter state. Client updates use WebSockets.

Formerly Monster Display. This documentation covers the supplied source snapshot,
including normalized SQLite storage, database-backed accounts and filtered player updates.
Database schema versions are distinct from application version labels.

## Documentation

- [User Guide](docs/User-Guide.md): campaigns, characters, setups, imports and combat.
- [Technical Documentation](docs/Technical-Documentation.md): modules, context, state, APIs and development.
- [User Management](docs/User-Management.md): first login, roles, account migration and recovery.
- [SQLite Migration](docs/SQLite-Migration.md): upgrade paths, backups and rollback.
- [Database Schema](docs/Database-Schema.sql): reference DDL, not a manual migration script.
- [Systemd Deployment](docs/Systemd-Deployment.md): Linux service installation, upgrades and backups.

## Features

- Separate Admin and Client applications with separate session cookies and logout.
- Database-backed client/admin/superadmin accounts and superadmin-only user management.
- Campaigns with campaign-owned character rosters and named battle setups.
- Manual monster creation with fixed, ranged or dice-expression HP.
- Monster quantities, .monster JSON import, and monster/character CSV import.
- Uploaded images and optional best-effort D&D Beyond image/stat suggestions.
- Battle initiative, tie resolution, round tracking, turn advancement, individual/bulk controls.
- Adjustable viewer battle-order text (12–40 px, in 2 px steps).
- Current-turn damage, healing, buff/debuff logging, and CSV/JSON log exports.
- Per-setup display backgrounds: colors, CSS gradients and uploaded images.
- Normalized SQLite persistence, stable campaign IDs, legacy migration and real-time player display updates.

## Requirements

Python 3.14 or newer, a modern browser, and network connectivity between the
server and intended display devices. Use one application process per storage
directory; shared runtime state is not distributed across workers.

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
│   ├── users.html              # Superadmin account-management page
│   └── admin/                  # 20 ordered HTML fragments
├── static/                     # Admin/client/login CSS and browser JavaScript
├── config.example.yaml
├── run.sh                      # Linux/macOS launcher; environment in ~/dnd
├── run.bat / run.ps1            # Windows launchers; environment in %USERPROFILE%\dnd
├── tests/                      # Python tests and JavaScript/audit checks
└── docs/
```

Deploy the complete layout, not just the root script. The existing corrected
helper modules must accompany the new service and admin-handler modules.
Keep `__init__.py` in both packages. The HTML package is `web_html`, not `html`,
to avoid colliding with Python's standard-library package.

## Installation

Obtain the repository revision containing the split layout and change into its
root. For the existing repository:

```bash
git clone https://github.com/dajomas/scrying-glass.git
cd scrying-glass
```

Select your intended branch or release; do not assume the split is on every
branch. Create the virtual environment and install dependencies:

```bash
python3.14 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install \
  'fastapi>=0.115' \
  'uvicorn[standard]>=0.30' \
  'PyYAML>=6.0' \
  python-multipart
```

Copy and edit the configuration:

```bash
cp config.example.yaml config.yaml
```

Accounts are not configured here on a fresh installation. Example configuration:

```yaml
network:
  bind: "0.0.0.0"
  admin_port: 3000
  client_port: 4000

storage_dir: "./scrying-glass-data"


display:
  background: "#080b14"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  dndbeyond_image_lookup: true
```

## Validate and launch

Run checks using the application's virtual environment:

```bash
.venv/bin/python -m compileall -q scrying_glass_server.py python web_html
.venv/bin/python -c "from web_html.admin_html import ADMIN_HTML; print('HTML loaded:', len(ADMIN_HTML), 'characters')"
.venv/bin/python -c "import scrying_glass_server; print('Server import passed')"
```

Compilation checks Python syntax; the import check also loads HTML fragments
and constructs routes. It does not initialize storage or start listeners.

```bash
.venv/bin/python scrying_glass_server.py --config config.yaml
```

Your existing shell launcher may activate the environment before running this
command. The direct virtual-environment executable also works without activation.

| Screen | Default address | Role |
|---|---|---|
| Battle Admin | `http://SERVER:3000/` | admin UI; superadmin redirects to /users |
| User Management | `http://SERVER:3000/users` | superadmin |
| Client Display | `http://SERVER:4000/display` | client, admin or superadmin |

Replace SERVER with the hostname/IP; use localhost for same-machine access.
The root script remains the entry point: do not replace it with an external
Uvicorn module command, which bypasses initialization under the main guard.

## First login and accounts

On first account initialization, a fresh installation creates a `superadmin` with a
random password and prints its credentials once to startup stdout (the journal for
systemd). Sign in on the Admin port: superadmins land on `/users`, not the battle UI.
Change the bootstrap password there, then create an `admin` for battle administration
and a `client` for players. No default player account is created. A superadmin can
call battle APIs and access the player display, but `/` redirects to user management.

Existing `security.users` is imported once. The first legacy admin is promoted if
there is no legacy superadmin; existing passwords remain usable. After verifying the
import, remove that section from your live configuration. Later configuration edits
do not reset database accounts. See [User Management](docs/User-Management.md).

## Included launchers

Run `bash run.sh`, `run.bat`, or `./run.ps1` from the appropriate shell after creating
`config.yaml`. Each launcher changes to the checkout root, checks sqlite3 support and
starts the root server with that config. They do not forward extra CLI arguments.
`run.sh` creates/uses `~/dnd` and skips pip when its dependency-spec marker matches;
the Windows launchers use `%USERPROFILE%\dnd` and invoke pip each time. Windows
environment creation specifically checks for Python 3.14. For custom ports/storage
or another environment, use the direct Python command instead.

## Encounter workflow

1. Sign into Admin; open and sign into the Client Display separately.
2. Select/create a campaign and maintain its character roster.
3. Create/load a battle setup and add or import monsters.
4. Choose a display background and save the setup.
5. Set initiative, activate participants, start battle and resolve ties.
6. Advance turns and use the active combatant's action dialog.
7. Export the activity log if needed; end/reset the battle as appropriate.

Characters belong to campaigns, not setup snapshots. New setups retain the
active campaign's characters. Setup import appends monsters only. Loading a
setup restores its encounter data and loads the campaign's current roster.

## Persistence and backups

Structured data lives in `storage_dir/scrying-glass.sqlite3`, now schema version 4.
The database stores individual values in typed columns and lists in ID-bearing child
rows; it does not store serialized JSON payloads. Uploaded images remain under
`storage_dir/uploads/`, and configuration remains a YAML/JSON file. JSON API responses
and in-memory dictionaries are unchanged as formats; JSON is not a database storage format.

Campaigns and battle setups have stable integer database IDs. Campaign renames update
one campaign row, without rewriting characters, setups or runtime references. Campaign
IDs are represented as decimal strings in API/form values. The admin frontend uses id,
not slug, for campaign selection. Existing monster/character combatant IDs remain intact.

Upgrades from slug-based SQLite v1 and campaign-ID SQLite v2 are backed up and converted
to normalized v3, followed by a separate account-table upgrade to v4.
Existing v3 databases are backed up before adding account tables. Existing v2 campaign
IDs are retained. Original JSON installations
are imported into the current v4 database without modifying source files. See
[SQLite migration instructions](docs/SQLite-Migration.md) and [database schema](docs/Database-Schema.sql).

Stop the application before backing up the entire storage directory plus configuration.
Keep matching pre-upgrade code and data for rollback. Archived JSON files are not updated
after import. Use one application process per data directory. sqlite3 is supplied by
Python, not pip; the launchers check its availability before starting.

## Editing the UI

Admin markup lives in ordered fragments in `templates/admin/`. The loader
exports ADMIN_HTML as before and reads fragments once at import; restart the
server after markup edits. Keep fragment order and element IDs intact.
CSS and JavaScript live in `static/`; hard-refresh the browser after changes.
No Jinja dependency was introduced by the split.

## Security

Use a trusted LAN. Do not expose default HTTP ports directly to the internet.
For remote access, use network restrictions/VPN and an HTTPS reverse proxy;
review cookie settings and application-level protections before exposure.
Sessions are in memory and are lost on restart. Player HTTP/WebSocket state is
filtered server-side: hidden monster stats, character stats, activity logs and setup
references are omitted. This is not complete secrecy: visible names, ordering and
image URLs remain available, and `/media` is an unauthenticated static mount.
Cross-origin browser mutations and display sockets with mismatched origins are
rejected; cookies still use `secure=False`. Logout revokes only that interface session.

## Upgrade and legacy names

Deploy all Python packages, HTML fragments and static assets together. Back up
configuration and storage, stop the application, update code, validate, then
restart. See [Systemd Deployment](docs/Systemd-Deployment.md#upgrade-procedure).

Earlier installations used monster_display_server.py and monster-display-data.
The current entry point is scrying_glass_server.py. If the new default storage
directory is absent, the legacy default directory can be used as a fallback.
Explicit storage_dir settings are unchanged. Legacy login cookies are removed
on successful login; everyone must sign in after a restart.

## License

See the repository [LICENSE](LICENSE) for the MIT license.
