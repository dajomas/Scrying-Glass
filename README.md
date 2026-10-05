# Scrying Glass

Scrying Glass is a self-hosted, real-time tabletop encounter display for game masters. A private **Admin** interface prepares and runs encounters, while a separate **Client Display** presents the battle on a player screen, TV, or projector.

The application runs two FastAPI services from one Python process, stores campaign and encounter data as JSON, serves uploaded images, and pushes live Client Display updates through WebSockets.

> Formerly **Monster Display** (`monster_display_server`). See [Migrating from Monster Display](#migrating-from-monster-display) when upgrading an earlier installation.

## Features

- Separate Admin and Client Display applications with independent session cookies.
- Role-based `admin` and `client` accounts.
- Live Client Display updates through WebSockets.
- Campaign-owned characters and campaign-specific saved battle setups.
- Manual monster creation with fixed HP, inclusive numeric HP ranges, or D&D-style dice expressions.
- Dice expressions accept optional spaces around modifiers: `3d8+9`, `3d8 +9`, `3d8+ 9`, and `3d8 + 9` are equivalent.
- Multi-digit dice sides are supported, including `d10`, `d12`, `d20`, and `d100`.
- Each monster created in a quantity receives an independent numeric-range selection or dice roll.
- Rolled initial HP is stored as the monster's current HP, maximum HP, and reset HP.
- Automatic persistence: character mutations save to the active campaign roster; monster mutations save to the loaded battle setup.
- Compatible `.monster` JSON imports and quantity-based creation of up to 50 monster copies at once.
- Monster and character CSV imports, including generated IDs for blank ID fields.
- Optional uploaded monster images and best-effort D&D Beyond image lookup using the canonical `monster_species` value.
- Legacy-marked exact D&D Beyond matches are tried before non-legacy exact matches; the dedicated monster-page image is used when available.
- Monster edit dialogs show a thumbnail of the current image, limited to 300px in either dimension, and preview a replacement file locally until **Save monster** is clicked.
- Per-setup Client Display colors, CSS gradients, and uploaded background images.
- Initiative ordering, tie resolution, current-turn actions, turn advancement, activity logging, and bulk actions.

## Documentation

- [User Guide](docs/User-Guide.md) — GM workflow, campaigns, battle setups, monster creation, images, combat controls, and troubleshooting.
- [Technical Documentation](docs/Technical-Documentation.md) — architecture, persistence, state model, APIs, HP grammar, image lookup, and operational constraints.
- [Systemd Deployment](docs/Systemd-Deployment.md) — hardened non-root `systemd` deployment, upgrades, backups, and migration.

## Requirements

- Python **3.14** or newer.
- A modern browser.
- LAN connectivity between the server and display devices.

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

Edit `config.yaml` and replace example credentials before starting the application.

## Quick start

```bash
python3.14 -m py_compile scrying_glass_server.py admin_html.py client_html.py login_html.py
python3.14 scrying_glass_server.py --config config.yaml
```

| Screen | Default address | Intended user |
|---|---|---|
| Admin | `http://SERVER:3000/` | Game master |
| Client Display | `http://SERVER:4000/` or `http://SERVER:4000/display` | Players, TV, or projector |

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
  background: "#080b14"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  dndbeyond_image_lookup: true
```

`display.dndbeyond_image_lookup` enables optional outbound HTTPS lookups to D&D Beyond. A lookup failure never blocks monster creation; upload a monster image directly when an exact matching remote image is unavailable.

## Typical workflow

1. Sign in to the Admin page.
2. Select or create a campaign; activating a campaign opens its preferred setup where available.
3. Create a named battle setup with **New**, or load an existing setup.
4. Add campaign characters and setup monsters.
5. Set initiative and join living combatants to the battle.
6. Start the battle, resolve ties, and use **Next** to advance turns.
7. Use the current-combatant action dialog to apply Damage, Heal, Buff, or Debuff actions.

Character changes are automatically written to the active campaign. Monster changes are automatically written to the currently loaded saved battle setup. An intentionally unsaved encounter is retained as runtime working state until it is saved under a setup name.

## Manual monster HP

The manual monster form supports three HP modes:

| HP Range start | HP Range end | Result |
|---|---|---|
| `17` | blank | Every created copy starts with 17 HP |
| `10` | `20` | Every created copy independently receives 10 through 20 HP, inclusive |
| `3d8+9` | blank | Every created copy independently rolls 3d8 and adds 9 |

Dice expressions use this form:

```text
<count>d<sides>[+|-<modifier>]
```

Spaces around `+` or `-` are optional. Common examples include:

```text
1d8
2d10+4
3d8 + 9
1d20
1d100-5
```

Dice mode requires an empty HP Range end field. The roll result is stored as `hp`, `max_hp`, and `original_hp`, so reset restores the original rolled value rather than rolling again.

## Monster images

A manually uploaded image always takes precedence. Without an upload, Scrying Glass can perform a best-effort D&D Beyond lookup using **Monster species** as the canonical D&D Beyond creature name. Use a canonical value such as `Mimic`, `Goblin`, or `Ancient Red Dragon`; the local encounter display name may be customized independently.

When editing a monster, its current image is displayed as a thumbnail no larger than 300px wide or high. Selecting a replacement file previews it locally; the replacement is uploaded only after clicking **Save monster**.

## Data storage

All persistent data is stored below `storage_dir`:

```text
scrying-glass-data/
├── state.json
├── campaigns.json
├── characters/
│   └── <campaign-slug>.json
├── uploads/
│   └── <uuid>.<image-extension>
└── setups/
    └── <campaign-slug>/
        └── <normalized-setup-name>.json
```

Back up the complete directory. It contains campaign character rosters, saved battle setups, the working state, activity logs, and uploaded monster/background images.

## Static assets after upgrades

After changing or deploying `admin.js` or `admin.css`, restart the service if necessary and hard-refresh the browser:

- Linux/Windows: `Ctrl+Shift+R`
- macOS: `Cmd+Shift+R`

With Chrome DevTools open, enable **Disable cache** while testing updates.

## Migrating from Monster Display

| Before | After |
|---|---|
| `monster_display_server.py` | `scrying_glass_server.py` |
| `./monster-display-data` | `./scrying-glass-data` |
| `monster_admin_session` / `monster_client_session` | `scrying_glass_admin_session` / `scrying_glass_client_session` |

If the default data directory is used and `./scrying-glass-data` does not exist, the application can continue using the legacy `./monster-display-data` directory and logs a migration suggestion.

## Security

Scrying Glass is intended for a trusted local network. Do not expose default HTTP listeners directly to the public internet. Use an HTTPS reverse proxy, firewall or VPN restrictions, strong passwords or scrypt hashes, and a dedicated non-root service account for remote use.

## License

MIT License.
