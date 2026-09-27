# Monster Display

Monster Display is a self-hosted, real-time tabletop encounter display for game masters. It provides a private **Admin** interface for preparing and running encounters and a separate, player-facing **Client Display** for a TV, projector, or browser.

The current application is a Python 3.14+ FastAPI service with persistent JSON state, saved encounter setups, uploaded media, live WebSocket display updates, CSV import/export, activity logging, and multi-target turn actions.

## Documentation

- See the [User Guide](docs/User-Guide.md) for the GM workflow and CSV formats.
- See the [Technical Documentation](docs/Technical-Documentation.md) for architecture, state, API routes, persistence, and operations.
- For GitHub Wiki copies, use the same Markdown documents as `Home.md`, `User-Guide.md`, and `Technical-Documentation.md` in the repository Wiki.

## Features

- Separate Admin and Client Display applications on configurable ports.
- Role-based login accounts: `admin` and `client`.
- Real-time client refreshes through WebSockets.
- Manual creation of monsters and characters.
- `.monster` JSON import, including quantity-based monster creation.
- Monster and character CSV import; missing IDs are generated automatically.
- Optional monster image upload and optional best-effort D&D Beyond image lookup.
- Saved setup creation, loading, and selective import of characters, monsters, or both.
- Encounter combat flow with initiative ordering, tie resolution, Next, activation during a battle, and reset.
- Active/inactive battle-state indicator.
- Individual monster and character controls for HP, visibility, initiative, turn state, and reset.
- Bulk monster toggles for Active, Ally, AC, HP, and initiative display.
- Activity log for damage, healing, buffs, and debuffs, with CSV/JSON export and clearing.
- Current-turn action modal for applying multiple target actions in one operation.
- Responsive monster-card grid and a client initiative bar that hides when empty.
- Client background colors, gradients, and cover-sized centered background images.

## Requirements

- Python **3.14** or newer.
- A modern browser.
- Network access between the server and Admin/Client devices when used on a LAN.

Python dependencies:

```text
fastapi
uvicorn[standard]
PyYAML
python-multipart
```

## Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/dajomas/monster_display_server.git
cd monster_display_server

git checkout features/development

python3.14 -m venv .venv
. .venv/bin/activate

python3.14 -m pip install --upgrade pip
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

The split-source layout uses these Python modules in the same directory:

```text
monster_display_server.py
admin_html.py
client_html.py
login_html.py
config.example.yaml
```

Copy and edit the example configuration:

```bash
cp config.example.yaml config.yaml
```

Change the example passwords before starting the application.

## Quick start

Validate the source and start the server:

```bash
python3.14 -m py_compile monster_display_server.py admin_html.py client_html.py login_html.py
python3.14 monster_display_server.py --config config.yaml
```

Open the following addresses, replacing `SERVER` with the server hostname or IP address:

| Screen | Default URL | Intended user |
|---|---|---|
| Admin | `http://SERVER:3000/` | Game master / encounter controller |
| Client Display | `http://SERVER:4000/display` | Players, TV, or projector |

For a local installation, use `localhost`:

```text
http://localhost:3000/
http://localhost:4000/display
```

## Minimal configuration

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
      password: "change-this-admin-password"
    - username: "table"
      role: "client"
      password: "change-this-client-password"

display:
  background: "radial-gradient(circle at 50% 15%, #16273d, #080b14 70%)"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  default_monster_color: "#842029"
  default_character_color: "#1f4e79"
  dndbeyond_image_lookup: true
```

An image background may be configured with a CSS URL, for example:

```yaml
display:
  background: "url('/media/bgimage.png')"
```

The client display centers it and uses `cover` sizing.

## Typical GM workflow

1. Log in to the Admin screen with an `admin` account.
2. Create a new setup, load a saved setup, or import combatants from a saved setup.
3. Add monsters and characters manually, from `.monster` files, or from CSV.
4. Set initiatives and activate the combatants taking part in the encounter.
5. Save the setup if you want to reuse it.
6. Start the battle and resolve any tied initiatives.
7. Click the current combatant in the Battle order to apply damage, healing, buffs, or debuffs to one or more active targets.
8. Use **Next** to advance the turn.
9. Export the Activity Log when needed.
10. Use **Reset All** to restore combatants and clear the battle order.

## Persistent data

The configured `storage_dir` contains the working state, image uploads, and saved setups:

```text
monster-display-data/
├── state.json
├── uploads/
│   └── <uuid>.<image-extension>
└── setups/
    └── <normalized-setup-name>.json
```

Back up the entire storage directory. Setup and current-state JSON files can refer to files in `uploads/`.

## Security note

Monster Display is intended for a trusted local network. Do not expose the default HTTP service directly to the public internet. For wider access, use HTTPS through a reverse proxy, firewall or VPN restrictions, strong passwords or scrypt hashes, and a dedicated non-root service account.

## License

No license is declared by this documentation. Add a repository `LICENSE` file before distributing or accepting external contributions.
