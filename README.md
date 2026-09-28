# Monster Display

Monster Display is a self-hosted, real-time tabletop encounter display for game masters. It provides a private **Admin** interface for preparing and running encounters and a separate **Client Display** for players, a TV, or a projector.

The application runs two FastAPI services from one Python process, persists encounters as JSON, serves uploaded monster images, and pushes live display updates over WebSockets.

This project is for 98% Vibe-coded using Perplexity.ai

## Documentation

- [User Guide](docs/User-Guide.md) — GM workflow, encounter controls, imports, battle actions, and troubleshooting.
- [Technical Documentation](docs/Technical-Documentation.md) — architecture, state model, API routes, persistence, and operations.
- For a GitHub Wiki, add these documents as `Home.md`, `User-Guide.md`, and `Technical-Documentation.md`.

## Features

- Separate Admin and Client Display applications, with independently scoped login cookies so both can be open in one browser.
- Role-based `admin` and `client` accounts.
- Real-time Client Display updates using WebSockets.
- Manual creation of monsters and characters.
- `.monster` JSON import and quantity-based creation of up to 50 monster copies per submission.
- Recommended `.monster` file authoring with the [Tetra-cube D&D 5e Statblock Generator](https://tetra-cube.com/dnd/dnd-statblock.html).
- Monster and character CSV import, with generated IDs for rows without an ID.
- Monster images by upload or optional best-effort D&D Beyond lookup.
- Saved encounter setups: New, Save, Load, and selective Import from setup.
- Setup imports preserve source current HP and Max HP while creating new IDs and clearing active/visible/turn runtime state.
- Monster/character editing, individual reset, and permanent removal from the current encounter.
- Battle start, tie resolution, turn progression, active/inactive status, and battle-order-aware activation.
- Multi-target current-turn actions: Damage, Heal, Buff, and Debuff.
- Activity log with CSV/JSON export and clearing.
- Bulk Monster controls for Active, Ally, AC, HP, and Init display flags.
- Ally monster labels rendered as `Name - Ally` without changing stored names.
- Adaptive monster-card grid, contrast-aware text panels, initiative bar auto-hide, and color/gradient/image client backgrounds.

## Requirements

- Python **3.14** or newer.
- A modern browser.
- Network connectivity between the server and display devices for LAN use.

Install these Python packages:

```text
fastapi
uvicorn[standard]
PyYAML
python-multipart
```

## Installation

```bash
git clone https://github.com/dajomas/monster_display_server.git
cd monster_display_server

git checkout features/development

python3.14 -m venv .venv
. .venv/bin/activate
python3.14 -m pip install --upgrade pip
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

The current split UI/source layout uses these modules in the same directory:

```text
monster_display_server.py
admin_html.py
client_html.py
login_html.py
config.example.yaml
```

Create a configuration file from the example:

```bash
cp config.example.yaml config.yaml
```

Replace the example passwords before starting the service.

## Quick start

Validate and start the application:

```bash
python3.14 -m py_compile monster_display_server.py admin_html.py client_html.py login_html.py
python3.14 monster_display_server.py --config config.yaml
```

Open the following pages, replacing `SERVER` with the server hostname or IP address:

| Screen | Default address | Intended user |
|---|---|---|
| Admin | `http://SERVER:3000/` | Game master |
| Client Display | `http://SERVER:4000/display` | Players, projector, or TV |

For local use:

```text
http://localhost:3000/
http://localhost:4000/display
```

## Configuration example

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

`display.background` accepts a CSS color, gradient, or image URL. For example:

```yaml
display:
  background: "url('/media/bgimage.png')"
```

The Client Display centers image backgrounds, prevents tiling, and scales them with `cover`.

## Typical encounter workflow

1. Sign in to the Admin page with an `admin` account.
2. Create a new encounter, load a setup, or import combatants from a saved setup.
3. Add monsters and characters manually, from `.monster` files, or from CSV.
4. Set initiatives and activate the participants.
5. Save the setup if it will be reused.
6. Start the battle and resolve initiative ties.
7. Click the underlined active combatant in Battle order to apply one or more target actions.
8. Use **Next** to advance turns.
9. Export the Activity Log if needed.
10. Use **Reset All** to reset combatants and clear the battle order.

## Creating `.monster` files

Monster Display can import compatible `.monster` JSON files. A practical way to create or edit them is the [Tetra-cube D&D 5e Statblock Generator](https://tetra-cube.com/dnd/dnd-statblock.html).

When preparing a monster for import, ensure its statblock contains usable values for:

- Name
- Type
- Armor Class
- Hit Points

Monster Display uses those values when it creates the encounter entry. Add a color, quantity, and optional image in the Admin import form.

## Data storage

All persistent runtime data is stored under `storage_dir`:

```text
monster-display-data/
├── state.json
├── uploads/
│   └── <uuid>.<image-extension>
└── setups/
    └── <normalized-setup-name>.json
```

Back up the complete directory, including `uploads/`, because state/setup files can reference uploaded images.

## Security

Monster Display is designed for trusted local-network use. Do not directly expose its default HTTP listeners to the public internet. For broader deployment, use an HTTPS reverse proxy, network restrictions such as a firewall or VPN, strong passwords or scrypt hashes, and a dedicated non-root service account.

## License

This project is licensed under the [MIT License](LICENSE).
