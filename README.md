# Scrying Glass

Scrying Glass is a self-hosted tabletop encounter manager: the game master uses
an authenticated Admin interface while players watch a separate live Client
Display. Both FastAPI applications run in one Python process, persist data as
JSON, and share encounter state. Client updates use WebSockets.

Formerly Monster Display. This documentation describes the split-source layout
introduced on 6 October 2026; it does not designate a new software release.

## Documentation

- [User Guide](docs/User-Guide.md): campaigns, characters, setups, imports and combat.
- [Technical Documentation](docs/Technical-Documentation.md): modules, context, state, APIs and development.
- [Systemd Deployment](docs/Systemd-Deployment.md): Linux service installation, upgrades and backups.

## Features

- Separate Admin and Client applications with separate session cookies.
- Campaigns with campaign-owned character rosters and named battle setups.
- Manual monster creation with fixed, ranged or dice-expression HP.
- Monster quantities, .monster JSON import, and monster/character CSV import.
- Uploaded images and optional best-effort D&D Beyond image/stat suggestions.
- Battle initiative, tie resolution, turn advancement, individual/bulk controls.
- Current-turn damage, healing, buff/debuff logging, and CSV/JSON log exports.
- Per-setup display backgrounds: colors, CSS gradients and uploaded images.
- JSON persistence, legacy migration and real-time player display updates.

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
│   └── admin/                  # 20 ordered HTML fragments
├── static/                     # Admin/client/login CSS and browser JavaScript
├── config.example.yaml
├── run.sh                      # Existing launcher, if used
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

Replace all example passwords before use. Example configuration:

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
| Admin | `http://SERVER:3000/` | admin |
| Client Display | `http://SERVER:4000/display` | client or admin |

Replace SERVER with the hostname/IP; use localhost for same-machine access.
The root script remains the entry point: do not replace it with an external
Uvicorn module command, which bypasses initialization under the main guard.

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

```text
storage_dir/
├── state.json
├── campaigns.json
├── characters/
│   └── <campaign-slug>.json
├── setups/
│   └── <campaign-slug>/
│       └── <setup-slug>.json
└── uploads/
    └── <uuid>.<extension>
```

`state.json` stores working runtime state. With a valid active saved setup,
monster data is owned by that setup rather than duplicated in state.json.
Characters are persisted separately in `characters/<campaign>.json`.
Back up the complete storage directory, including campaign metadata, rosters,
setups and all images. Stop the server for a consistent filesystem backup.

The source split itself does not require moving or resetting runtime data.
Older loose setups are migrated into the Default campaign at startup; older
setup character data can seed a missing campaign roster.

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
Sessions are in memory and are lost on restart. Client access exposes the state
payload, not merely the details visually shown on cards.

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
