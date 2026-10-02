# Scrying Glass

Scrying Glass is a self-hosted, real-time tabletop encounter display for game masters. A private **Admin** interface prepares and runs encounters, while a separate **Client Display** presents the battle on a player screen, TV, or projector.

The application runs two FastAPI services from one Python process, stores encounter data as JSON, serves uploaded images, and pushes live Client Display updates through WebSockets.

> Formerly **Monster Display** (`monster_display_server`). See [Migrating from Monster Display](#migrating-from-monster-display) when upgrading an earlier installation.

## Features

- Separate Admin and Client Display applications with independent session cookies, so both can remain signed in in the same browser.
- Role-based `admin` and `client` accounts.
- Live Client Display updates through WebSockets.
- Manual monster and character creation.
- Compatible `.monster` JSON imports and quantity-based creation of up to 50 monster copies at once.
- Monster and character CSV imports, including generated IDs for blank ID fields.
- Optional uploaded monster images and best-effort D&D Beyond image lookup.
- Campaigns that group battle setups: create, edit, activate, delete, and move or copy setups between campaigns.
- Automatic migration of legacy unassigned setups into a **Default** campaign.
- Per-campaign battle setups with New, Save, Load, Rename, Delete, and Import from setup actions.
- Per-setup Client Display colors, CSS gradients, and uploaded background images.
- Initiative ordering, tie resolution, current-turn actions, turn advancement, and activity logging.
- Monster and character list color markers that match combatant colors.
- Selected-combatant bulk actions through row checkboxes in the Monster and Character panes.
- CSV and JSON activity-log exports.

## Documentation

- [User Guide](docs/User-Guide.md) — GM workflow, campaigns, battle setups, imports, combat controls, bulk actions, and troubleshooting.
- [Technical Documentation](docs/Technical-Documentation.md) — architecture, persistence, state model, API routes, combat rules, and operational constraints.
- [Systemd Deployment](docs/Systemd-Deployment.md) — installation as a hardened non-root `systemd` service, upgrades, backups, and migration.

## Requirements

- Python **3.14** or newer.
- A modern browser.
- Network connectivity between the server and display devices for LAN use.

Required Python packages:

```text
fastapi
uvicorn[standard]
PyYAML
python-multipart
```

## Installation

```bash
git clone https://github.com/dajomas/scrying-glass.git
cd scrying-glass

git checkout features/development

python3.14 -m venv .venv
. .venv/bin/activate
python3.14 -m pip install --upgrade pip
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart

cp config.example.yaml config.yaml
```

Edit `config.yaml` and replace its example credentials before starting the application.

## Project layout

```text
scrying_glass_server.py  # FastAPI applications, models, state, persistence, routes, startup
admin_html.py             # Admin HTML document template
client_html.py            # Client Display HTML document template
login_html.py             # Shared login HTML template
static/
├── admin.css             # Admin styles
├── admin.js              # Admin rendering, dialogs, API calls, and browser-only selections
├── client.css            # Client Display styles
├── client.js             # Client Display rendering and WebSocket handling
└── login.css             # Login-page styles
config.example.yaml       # Example configuration
run.sh                    # Convenience launcher
```

The application serves the files in `static/`. After changing JavaScript or CSS, restart the service and hard-refresh the affected browser page.

## Quick start

Validate and start the application:

```bash
python3.14 -m py_compile scrying_glass_server.py admin_html.py client_html.py login_html.py
python3.14 scrying_glass_server.py --config config.yaml
```

Open the following pages, replacing `SERVER` with the hostname or IP address of the machine running Scrying Glass:

| Screen | Default address | Intended user |
|---|---|---|
| Admin | `http://SERVER:3000/` | Game master |
| Client Display | `http://SERVER:4000/display` | Players, TV, or projector |

For local use:

```text
http://localhost:3000/
http://localhost:4000/display
```

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
      password: "change-this-admin-password"
    - username: "table"
      role: "client"
      password: "change-this-client-password"

display:
  # Fallback for legacy setups and the initial background for a new setup.
  background: "#080b14"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  default_monster_color: "#842029"
  default_character_color: "#1f4e79"
  dndbeyond_image_lookup: true
```

Configuration may be YAML or JSON. Command-line values override the corresponding configuration values. Passwords may be plaintext or scrypt hashes; see the Technical Documentation for hash generation.

## Typical workflow

1. Sign in to the Admin page with an `admin` account.
2. Select an existing campaign or create a new one. Activating a campaign opens its most recently used setup where possible.
3. Create a new encounter, load a saved setup, or import combatants from another setup.
4. Set the Client Display background for the working setup if desired.
5. Add monsters and characters manually, from `.monster` files, or from CSV.
6. Select repeated combatants with their checkboxes and use the relevant **Bulk** menu to prepare them efficiently.
7. Set initiative and activate the living combatants that will participate.
8. Save the battle setup in the active campaign.
9. Start the battle, resolve initiative ties, and use **Next** to advance turns.
10. Click the underlined current combatant in Battle order to apply Damage, Heal, Buff, or Debuff actions to one or more targets.
11. Export the activity log if required, then use **Reset All** when the encounter ends.

## Campaigns and setups

A campaign groups related battle setups. Each setup belongs to one campaign, and one campaign is active at a time.

- New campaigns receive an empty `default` setup and become active by default.
- Activating a campaign opens its recorded `last_setup`; if that file no longer exists, Scrying Glass opens the most recently modified setup instead.
- Existing setups from versions before campaigns are automatically moved to the **Default** campaign during startup.
- Setup names may be reused in different campaigns, but not within the same campaign.
- Switching campaigns, loading a setup, creating a campaign, and deleting the active campaign can replace the working encounter. Save first when changes matter.

See [Campaigns](docs/User-Guide.md#campaigns) and [Battle setups](docs/User-Guide.md#battle-setups) for the complete workflow.

## Selected combatants

The Monster and Character panes use independent row selections. Select checkboxes and choose an action from the matching **Bulk** menu.

- Typical actions include Select all, Unselect all, Join Battle, Leave Battle, Reset, and Remove.
- Monster bulk controls also cover ally state and the AC, HP, and initiative fields displayed on Client Monster cards.
- Character bulk controls cover battle participation, initiative-bar visibility, reset, and removal.
- Selections remain after successful actions while the selected combatants still exist; **Select all** and **Unselect all** intentionally replace the selection.
- A bulk removal has one confirmation for the entire selected set.
- Browser selections are not stored in `state.json` or saved setups, and they are not visible to Client Display users.

## Per-setup backgrounds

The Client Display background belongs to the current working battle setup. In the Admin **Battle setups** pane, use **View screen background** to choose a color, enter a CSS background value such as a gradient, or upload an image.

Applying a background updates the Client Display immediately. Save the setup to retain it. A newly created setup starts with `display.background` from `config.yaml`; older setup files without a background use that value as a fallback until saved.

Background uploads are stored in `storage_dir/uploads/`. Include `uploads/` in backups because setup files can reference those images.

## Data storage

All persistent runtime data is stored below `storage_dir`:

```text
scrying-glass-data/
├── state.json
├── campaigns.json
├── uploads/
│   └── <uuid>.<image-extension>
└── setups/
    └── <campaign-slug>/
        └── <normalized-setup-name>.json
```

Back up the complete directory. `state.json` preserves the working encounter; `campaigns.json` preserves campaign metadata and the active campaign; setup snapshots preserve named encounters; and `uploads/` contains monster and background images referenced by state and setup files.

## Importing monsters

Scrying Glass accepts compatible `.monster` JSON files. The [Tetra-cube D&D 5e Statblock Generator](https://tetra-cube.com/dnd/dnd-statblock.html) is a useful external tool for authoring files with a name, type, Armor Class, and Hit Points.

Monster CSV imports require `name`, `monster_type` or `type`, `ac`, and `hp`. Character CSV imports require `name`. CSV must be UTF-8 with a header row. Missing IDs are generated, while duplicate IDs or IDs already used in the active encounter are rejected.

## Migrating from Monster Display

The project was renamed from Monster Display to Scrying Glass.

| Before | After |
|---|---|
| `monster_display_server.py` | `scrying_glass_server.py` |
| `./monster-display-data` | `./scrying-glass-data` |
| `monster_admin_session` / `monster_client_session` | `scrying_glass_admin_session` / `scrying_glass_client_session` |

If `storage_dir` is explicitly configured, keep its value or change it deliberately after making a backup. If the default data directory is used and `./scrying-glass-data` does not exist, the application can continue using the legacy `./monster-display-data` directory and logs a migration suggestion.

Users must sign in again after the rename because session cookies changed and sessions are in-memory. See [Migrating from Monster Display](docs/Systemd-Deployment.md#migrating-from-monster-display) for the full systemd procedure.

## Security

Scrying Glass is intended for a trusted local network. Do not expose its default HTTP listeners directly to the public internet.

For remote access, use an HTTPS reverse proxy, firewall or VPN restrictions, strong passwords or scrypt password hashes, and a dedicated non-root service account. The application has in-memory sessions and is designed to run as a single process with one worker per persistent storage directory.

## License

This project is licensed under the MIT License.
