# Scrying Glass

> Formerly **Monster Display** (`monster_display_server`). Upgrading an existing installation? See [Renaming from Monster Display](#renaming-from-monster-display).

Scrying Glass is a self-hosted, real-time tabletop encounter display for game masters. It provides a private **Admin** interface for preparing and running encounters and a separate **Client Display** for players, a TV, or a projector.

The application runs two FastAPI services from one Python process, persists encounters as JSON, serves uploaded monster images, and pushes live display updates over WebSockets.

This project is for 98% Vibe-coded using Perplexity.ai

## Why "Scrying Glass"?

In fantasy stories, a scrying glass is a crystal ball or magic mirror that lets you watch events unfold from afar. That is exactly what this tool does at the table. The game master works behind the screen in the private **Admin** view, preparing encounters and running the battle. The players look into the glass, the **Client Display** on a TV or projector, and watch the fight appear as it happens: monsters entering and leaving the scene, turns passing, wounds and victories showing in real time. The glass only shows what the game master chooses to reveal, which suits a display the players watch but never control.

The project began as *Monster Display*, a name that described its first feature, showing monsters on a screen. Once it grew to include characters, campaigns, battle setups, and full turn-by-turn combat, that name no longer fit, and *Scrying Glass* describes what the players see.

## Documentation

- [User Guide](docs/User-Guide.md) — GM workflow, campaigns, battle setups, encounter controls, imports, battle actions, and troubleshooting.
- [Technical Documentation](docs/Technical-Documentation.md) — architecture, state model, campaign registry, API routes, persistence, and operations.
- [Systemd Deployment](docs/Systemd-Deployment.md) — running Scrying Glass as a hardened `systemd` service, including upgrades.
- For a GitHub Wiki, add these documents as `Home.md`, `User-Guide.md`, `Technical-Documentation.md`, and `Systemd-Deployment.md`.

### Campaign documentation

| Topic | Where to read |
|---|---|
| Using campaigns: switch, create, edit, delete, add setups to a campaign | [User Guide — Campaigns](docs/User-Guide.md#campaigns) |
| Battle setups within a campaign: Save, Load, Rename, Delete | [User Guide — Battle setups](docs/User-Guide.md#battle-setups) |
| The automatic **Default** campaign for setups from older versions | [User Guide — The Default campaign](docs/User-Guide.md#the-default-campaign) |
| `campaigns.json`, migration, and which setup opens on activation | [Technical Documentation — Campaigns](docs/Technical-Documentation.md#campaigns) |
| Campaign and setup API routes | [Technical Documentation — Campaign routes](docs/Technical-Documentation.md#campaign-routes) |
| Upgrading an existing installation to the campaign version | [Systemd Deployment — Upgrading to the campaign version](docs/Systemd-Deployment.md#upgrading-to-the-campaign-version) |

## Features

- Separate Admin and Client Display applications, with independently scoped login cookies so both can be open in one browser.
- Role-based `admin` and `client` accounts.
- Real-time Client Display updates using WebSockets.
- Manual creation of monsters and characters.
- `.monster` JSON import and quantity-based creation of up to 50 monster copies per submission.
- Recommended `.monster` file authoring with the [Tetra-cube D&D 5e Statblock Generator](https://tetra-cube.com/dnd/dnd-statblock.html).
- Monster and character CSV import, with generated IDs for rows without an ID.
- Monster images by upload or optional best-effort D&D Beyond lookup.
- **Campaigns** that group battle setups: create, edit, delete (moving or deleting their setups), switch, and move or copy setups between campaigns. See [Campaigns](docs/User-Guide.md#campaigns).
- Switching to a campaign automatically opens its most recently worked on battle setup. New campaigns start with an empty `default` setup.
- Setups saved before campaigns existed are moved into a **Default** campaign automatically.
- Saved encounter setups per campaign: New, Save, Load, Rename, Delete, and selective Import from setup (also from other campaigns).
- Campaign and battle setup dropdowns act immediately: selecting an entry switches campaign or loads the setup.
- Setup imports preserve source current HP and Max HP while creating new IDs and clearing active/visible/turn runtime state.
- Monster/character editing, individual reset, and permanent removal from the current encounter.
- Color markers in front of each monster and character name in the Admin lists, matching the battle order marker.
- Battle start, tie resolution, turn progression, active/inactive status, and battle-order-aware activation.
- Multi-target current-turn actions: Damage, Heal, Buff, and Debuff.
- Activity log with CSV/JSON export and clearing.
- Bulk Monster controls for Active, Ally, AC, HP, and Init display flags.
- Ally monster labels rendered as `Name - Ally` without changing stored names.
- Adaptive monster-card grid, contrast-aware text panels, initiative bar auto-hide, and per-battle-setup color, gradient, or image backgrounds.


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
git clone https://github.com/dajomas/scrying-glass.git
cd scrying-glass

git checkout features/development

python3.14 -m venv .venv
. .venv/bin/activate
python3.14 -m pip install --upgrade pip
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

The current split UI/source layout uses these modules in the same directory:

```text
scrying_glass_server.py
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
python3.14 -m py_compile scrying_glass_server.py admin_html.py client_html.py login_html.py
python3.14 scrying_glass_server.py --config config.yaml
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
  # Optional fallback used by legacy setups without their own background,
  # and as the initial background for a newly created setup.
  background: "#080b14"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  default_monster_color: "#842029"
  default_character_color: "#1f4e79"
  dndbeyond_image_lookup: true
```

## Per-setup view backgrounds

The Client Display background belongs to the active **battle setup**, not to the server-wide configuration. In the Admin page, use the **View screen background** controls in the Battle setups pane to choose a color, enter a CSS background value such as a gradient, or upload an image.

The change is applied to the Client Display immediately. Click **Save** for the battle setup to keep it. Loading or switching to another setup loads that setup's own background.

A newly created setup starts with `display.background` from `config.yaml`. Existing setup files that do not yet contain a saved background also use this value as a backward-compatible fallback. Once saved, each setup stores its own background independently.

Uploaded background images are saved in `storage_dir/uploads/` and referenced by the setup, so include `uploads/` when backing up or moving the installation. The Client Display centers image backgrounds, prevents tiling, and scales them with `cover`.

## Typical encounter workflow

1. Sign in to the Admin page with an `admin` account.
1. Select or create the campaign for this session in the **Campaign** dropdown. Its most recently worked on setup opens automatically.
1. Create a new encounter, load a setup, or import combatants from a saved setup.
1. In **View screen background**, choose the setup's color, CSS gradient, or uploaded background image.
1. Add monsters and characters manually, from `.monster` files, or from CSV.
1. Set initiatives and activate the participants.
1. Save the setup in the active campaign to retain combatants, battle state, Activity Log, and its view background.
1. Start the battle and resolve initiative ties.
1. Click the underlined active combatant in Battle order to apply one or more target actions.
1. Use **Next** to advance turns.
1. Export the Activity Log if needed.
1. Use **Reset All** to reset combatants and clear the battle order.

## Creating `.monster` files

Scrying Glass can import compatible `.monster` JSON files. A practical way to create or edit them is the [Tetra-cube D&D 5e Statblock Generator](https://tetra-cube.com/dnd/dnd-statblock.html).

When preparing a monster for import, ensure its statblock contains usable values for:

- Name
- Type
- Armor Class
- Hit Points

Scrying Glass uses those values when it creates the encounter entry. Add a color, quantity, and optional image in the Admin import form.

## Data storage

All persistent runtime data is stored under `storage_dir`:

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

`campaigns.json` records the campaigns, their descriptions, the active campaign, and each campaign's most recently worked on setup. Each campaign has its own folder under `setups/`. When upgrading from a version without campaigns, setups found directly in `setups/` are moved into `setups/default/` at the first start; see [Technical Documentation — Campaigns](docs/Technical-Documentation.md#campaigns).

Back up the complete directory, including `campaigns.json` and `uploads/`, because monster images and per-setup background images are referenced from state/setup files. Each saved setup includes its own `display.background` value.

## Renaming from Monster Display

Version 4.16 renames the project from Monster Display to Scrying Glass:

| Before | After |
|---|---|
| `monster_display_server.py` | `scrying_glass_server.py` |
| `./monster-display-data` (default `storage_dir`) | `./scrying-glass-data` |
| Cookies `monster_admin_session` / `monster_client_session` | `scrying_glass_admin_session` / `scrying_glass_client_session` |

- **Start command:** update scripts such as `run.sh` to start `scrying_glass_server.py`.
- **Data:** if your configuration sets `storage_dir` explicitly, nothing changes. If you rely on the default and `./scrying-glass-data` does not exist yet, the existing `./monster-display-data` folder is used automatically and a startup message suggests renaming it. To switch for good, stop the application and run `mv monster-display-data scrying-glass-data`.
- **Sign-in:** everyone signs in once after the upgrade. Sessions are in memory only, so a restart already requires this. The old cookies are removed at sign-in.
- **systemd installations:** see [Systemd Deployment — Migrating from Monster Display](docs/Systemd-Deployment.md#migrating-from-monster-display).

## Security

Scrying Glass is designed for trusted local-network use. Do not directly expose its default HTTP listeners to the public internet. For broader deployment, use an HTTPS reverse proxy, network restrictions such as a firewall or VPN, strong passwords or scrypt hashes, and a dedicated non-root service account.

## License

This project is licensed under the [MIT License](LICENSE).
