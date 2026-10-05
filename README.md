# Scrying Glass

Scrying Glass is a self-hosted, real-time tabletop encounter display for game masters. The private **Admin** interface prepares and runs encounters; a separate **Client Display** presents the battle to players, a TV, or a projector.

The application runs Admin and Client FastAPI services in one Python process, keeps the current encounter in memory, persists campaign and setup data as JSON, serves uploaded images, and pushes live Client Display state over WebSockets.

> Formerly **Monster Display**. The application supports migration from the legacy storage directory and cookie names.

## Features

- Separate Admin and Client Display applications with independent session cookies.
- Role-based `admin` and `client` accounts; an admin account may also sign into Client Display.
- Campaigns with independent character rosters and named battle setups.
- Live Client Display updates through WebSockets.
- Manual monster creation with fixed HP, inclusive numeric ranges, or D&D dice notation.
- Dice expressions with optional spaces around modifiers: `3d8+9`, `3d8 +9`, `3d8+ 9`, and `3d8 + 9` are equivalent.
- Multi-digit dice sizes, including `d10`, `d12`, `d20`, and `d100`.
- Independent HP roll/range generation for every monster created in a quantity.
- Automatic persistence of character mutations to the active campaign and monster mutations to the active saved battle setup.
- Compatible `.monster` JSON imports and Monster/Character CSV imports.
- Optional uploaded monster images and best-effort D&D Beyond lookup for images, Armor Class, and Hit Points.
- Exact D&D Beyond match selection with legacy-marked candidates tried first.
- D&D Beyond dice HP preference: `58 (9d8 + 18)` is suggested as `9d8+18`.
- Monster edit image thumbnails, replacement-image preview before save, and color-preview dots beside Admin color controls.
- Initiative ordering, tie resolution, current-turn actions, activity logging, bulk controls, and background images.

## Documentation

- [User Guide](docs/User-Guide.md) — GM workflow and Admin/Client behavior.
- [Technical Documentation](docs/Technical-Documentation.md) — architecture, persistence, APIs, parsing, and implementation details.
- [Systemd Deployment](docs/Systemd-Deployment.md) — non-root systemd installation, upgrades, backups, and troubleshooting.

## Requirements

- Python **3.14** or newer.
- A modern browser.
- LAN connectivity between the server and Client Display devices.

```bash
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
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

Replace example passwords in `config.yaml` before starting the service.

## Quick start

```bash
python3.14 -m py_compile scrying_glass_server.py admin_html.py client_html.py login_html.py
python3.14 scrying_glass_server.py --config config.yaml
```

| Screen | Address | Typical user |
|---|---|---|
| Admin | `http://SERVER:3000/` | Game master |
| Client Display | `http://SERVER:4000/` or `http://SERVER:4000/display` | Players / display device |

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

`dndbeyond_image_lookup` enables optional outbound lookup. Lookup failures never prevent creating a monster; upload an image or enter stats manually when needed.

## Typical workflow

1. Sign in to Admin.
2. Create/select a campaign; activation opens the campaign's most recently used setup when available.
3. Create a named setup with **New**, or load an existing one.
4. Add characters and monsters, set their initiatives, and use **Join Battle** for participants.
5. Start the battle and resolve initiative ties.
6. Use **Next** to advance the turn; click the underlined current combatant in battle order for actions.
7. Use **Reset All** to restore combatants after the encounter.

## HP modes

| HP Range start | HP Range end | Outcome |
|---|---|---|
| `17` | blank | Every copy begins with fixed 17 HP |
| `10` | `20` | Every copy independently receives 10–20 HP, inclusive |
| `3d8+9` | blank | Every copy independently rolls `3d8+9` |

Dice results initialize `hp`, `max_hp`, and `original_hp`. Reset restores the generated result; it does not reroll dice.

## D&D Beyond assistance

Use **Monster species** for the canonical creature name, such as `Mimic`, `Goblin`, or `Ancient Red Dragon`. Scrying Glass can look up exact D&D Beyond candidates, tries a legacy-marked exact candidate first, and can suggest AC/HP and a dedicated monster image.

Suggested stats fill blank fields by default. Enable **Overwrite Armor Class and HP Range with found D&D Beyond values** to allow a lookup to replace entered AC/HP. If D&D Beyond supplies dice HP, that expression is placed in HP Range start and HP Range end remains empty.

## Persistence and storage

```text
storage_dir/
├── state.json
├── campaigns.json
├── characters/
│   └── <campaign-slug>.json
├── uploads/
│   └── <uuid>.<extension>
└── setups/
    └── <campaign-slug>/<setup-name>.json
```

Characters are campaign-owned. Monsters belong to a loaded saved setup; intentionally unsaved monster encounters remain in working `state.json` until explicitly saved. Back up the entire directory.

## Browser cache after updates

After changing or deploying static JavaScript/CSS files, hard-refresh:

- Linux/Windows: `Ctrl+Shift+R`
- macOS: `Cmd+Shift+R`

For Chrome testing, open DevTools → Network and enable **Disable cache**.

## Security

Scrying Glass is intended for trusted local networks. Do not expose its default HTTP listeners directly to the public internet. For remote use, add HTTPS, a reverse proxy or VPN, firewall restrictions, strong passwords/scrypt hashes, and a non-root service account.

## License

MIT License.
