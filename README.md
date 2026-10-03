# Scrying Glass

Scrying Glass is a self-hosted, real-time tabletop encounter display for game masters. A private **Admin** interface prepares and runs encounters, while a separate **Client Display** presents the battle on a player screen, TV, or projector.

The application runs two FastAPI services from one Python process, stores encounter data as JSON, serves uploaded images, and pushes live Client Display updates through WebSockets.

> Formerly **Monster Display** (`monster_display_server`). See [Migrating from Monster Display](#migrating-from-monster-display) when upgrading an earlier installation.

## Features

- Separate Admin and Client Display applications with independent session cookies, so both can remain signed in in the same browser.
- Role-based `admin` and `client` accounts.
- Live Client Display updates through WebSockets.
- Manual monster and character creation.
- Manual monster HP ranges: each created monster receives an independently rolled, inclusive HP value between the configured **HP Range start** and **HP Range end**.
- Compatible `.monster` JSON imports and quantity-based creation of up to 50 monster copies at once.
- When a monster quantity is greater than one, copies receive numbered names in creation order, such as `Goblin - 1`, `Goblin - 2`, and `Goblin - 3`.
- Monster and character CSV imports, including generated IDs for blank ID fields.
- Optional uploaded monster images and best-effort D&D Beyond image lookup.
- Campaigns that group battle setups: create, edit, activate, delete, and move or copy setups between campaigns.
- Automatic migration of legacy unassigned setups into a **Default** campaign.
- Per-campaign battle setups with named New, Save, Load, Rename, Delete, and Import from setup actions.
- A named **New** action creates an empty working setup and immediately saves it under the entered unique name.
- Per-setup Client Display colors, CSS gradients, and uploaded background images.
- Initiative ordering, tie resolution, current-turn actions, turn advancement, and activity logging.
- Monster and character list color markers that match combatant colors.
- Selected-combatant bulk actions through row checkboxes in the Monster and Character panes.
- Local 15-second status notifications in the Add character, Add monster, Campaign Setup, and Battle setups panes.
- In-page `.monster` help describing compatible files and the imported fields.
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
git clone [https://github.com/dajomas/scrying-glass.git](https://github.com/dajomas/scrying-glass.git)
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
| Client Display | `http://SERVER:4000/` or `http://SERVER:4000/display` | Players, TV, or projector |

Opening `http://SERVER:4000/` redirects to the Client login page when there is no valid Client session. With a valid Client session, it redirects to the Client Display.

For local use:

```text
http://localhost:3000/
http://localhost:4000/
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
3. Enter a unique name in **Battle setup name** and click **New** to create and immediately save an empty encounter, load a saved setup, or import combatants from another setup.
4. Set the Client Display background for the working setup if desired.
5. Add monsters and characters manually, from `.monster` files, or from CSV.
6. Select repeated combatants with their checkboxes and use the relevant **Bulk** menu to prepare them efficiently.
7. Set initiative and activate the living combatants that will participate.
8. Save the battle setup again after making encounter changes that you want to retain.
9. Start the battle, resolve initiative ties, and use **Next** to advance turns.
10. Click the underlined current combatant in Battle order to apply Damage, Heal, Buff, or Debuff actions to one or more targets.
11. Export the activity log if required, then use **Reset All** when the encounter ends.

## Campaigns and setups

A campaign groups related battle setups. Each setup belongs to one campaign, and one campaign is active at a time.

- New campaigns receive an empty `default` setup and become active by default.
- Activating a campaign opens its recorded `last_setup`; if that file no longer exists, Scrying Glass opens the most recently modified setup instead.
- Existing setups from versions before campaigns are automatically moved to the **Default** campaign during startup.
- Setup names may be reused in different campaigns, but not within the same campaign.
- Enter a unique setup name and click **New** to discard the current working encounter, create an empty one, and immediately save it under that name.
- Switching campaigns, loading a setup, creating a campaign, and deleting the active campaign can replace the working encounter. Save first when changes matter.

See [Campaigns](docs/User-Guide.md#campaigns) and [Battle setups](docs/User-Guide.md#battle-setups) for the complete workflow.

## Pane notifications

The Add character, Add monster, Campaign Setup, and Battle setups panes display local status messages for actions started in that pane.

- Notifications disappear automatically after 15 seconds.
- A newer notification in the same pane replaces the earlier timer.
- The messages are browser-only feedback; they are not saved in setup files and are not shown on the Client Display.

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

## Manual monster HP ranges

The manual monster form uses **HP Range start** and **HP Range end** instead of a single HP value.

- The start value may not be greater than the end value.
- Both end points are included in the random selection.
- When start and end are equal, that value is assigned.
- Every created monster receives an independent HP roll.
- The rolled HP initializes the monster's current HP, maximum HP, and reset HP.

For example, creating three Goblins with a range of 7 to 12 can produce:

```text
Goblin - 1: 7 HP
Goblin - 2: 11 HP
Goblin - 3: 9 HP
```

The exact results vary because each monster receives its own random inclusive roll.

## Importing monsters

Scrying Glass accepts compatible `.monster` JSON files. The [Tetra-cube D&D 5e Statblock Generator](https://tetra-cube.com/dnd/dnd-statblock.html) is a useful external tool for authoring files with a name, type, Armor Class, and Hit Points.

The `.monster` importer reads these values:

|