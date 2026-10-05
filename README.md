# Scrying Glass

Scrying Glass is a self-hosted, real-time tabletop encounter display for game masters. The private **Admin** interface prepares and runs encounters; a separate **Client Display** presents the battle to players.

The application runs Admin and Client FastAPI services in one Python process, persists JSON data, serves uploads, and sends Client Display state through WebSockets.

## Features

- Separate Admin and Client Display logins with independent session cookies.
- Campaign-owned character rosters and campaign-specific battle setups.
- Automatic persistence: character mutations save to the active campaign roster; monster mutations save to the loaded battle setup.
- Manual monster creation with fixed HP, numeric HP ranges, or D&D dice HP.
- Dice expressions support optional modifier spaces and multi-digit dice: `3d8+9`, `3d8 + 9`, `2d10+4`, `1d20`, and `1d100`.
- Each created monster independently rolls numeric-range or dice HP; the result becomes current, maximum, and reset HP.
- Optional D&D Beyond monster lookup using canonical **Monster species** values, with exact-match and legacy-first behavior.
- Lookup can suggest AC and HP; dice HP is preferred when D&D Beyond provides both average HP and a dice expression.
- A checkbox can allow lookup results to overwrite entered AC and HP; otherwise existing values are preserved.
- Optional uploaded monster images, D&D Beyond dedicated monster-page image lookup, and edit-dialog image thumbnails/replacement previews.
- Initiative, battle order, ties, current-turn actions, activity logs, CSV/.monster imports, and bulk actions.

## Documentation

- [User Guide](docs/User-Guide.md)
- [Technical Documentation](docs/Technical-Documentation.md)
- [Systemd Deployment](docs/Systemd-Deployment.md)

## Requirements

- Python **3.14** or newer.
- A modern browser.
- LAN connectivity between server and display devices.

```bash
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

## Quick start

```bash
git clone https://github.com/dajomas/scrying-glass.git
cd scrying-glass
cp config.example.yaml config.yaml
python3.14 scrying_glass_server.py --config config.yaml
```

| Screen | Address |
|---|---|
| Admin | `http://SERVER:3000/` |
| Client Display | `http://SERVER:4000/` or `http://SERVER:4000/display` |

## Manual monster HP

| HP Range start | HP Range end | Result |
|---|---|---|
| `17` | blank | Fixed 17 HP for every copy |
| `10` | `20` | Independent inclusive 10–20 HP per copy |
| `3d8+9` | blank | Independent `3d8+9` roll per copy |

Dice notation is case-insensitive and permits optional whitespace around `+` or `-`. Dice mode requires a blank HP Range end. Dice results are stored as `hp`, `max_hp`, and `original_hp`; reset restores the original rolled total rather than rerolling.

## D&D Beyond suggestions

Enter a canonical creature name in **Monster species**, such as `Mimic`, `Goblin`, or `Ancient Red Dragon`. Scrying Glass can search D&D Beyond for an exact match, tries a result marked Legacy first, and may suggest AC plus HP. When the page contains `Hit Points 58 (9d8 + 18)`, the suggested HP is `9d8+18`, not `58`.

By default, lookup fills only blank AC and HP fields. Enable the **Overwrite Armor Class and HP Range with found D&D Beyond values** checkbox to permit replacing entered values. Lookup feedback uses the existing Add monster notification area. Remote lookup remains optional; creation continues when no usable match is found.

## Monster images

An uploaded image wins over automatic lookup. Without an upload, Scrying Glass uses Monster species for D&D Beyond image lookup and extracts the dedicated monster-page `monster-image`, not a generic social image. The edit dialog displays a thumbnail at most 300px wide/high. Selecting a replacement previews it locally and uploads it only after **Save monster**.

## Initiative on Client Display

Enable **Init on** for a monster to show initiative on its Client card. The monster must also have a numeric initiative value; if initiative is blank, there is no value to display. AC, HP, and initiative card fields are independently controlled.

## Data storage

```text
storage_dir/
├── state.json
├── campaigns.json
├── characters/<campaign-slug>.json
├── uploads/
└── setups/<campaign-slug>/<setup>.json
```

Back up the entire `storage_dir`, including `characters/`, `setups/`, and `uploads/`.

## Browser cache

After deploying static updates, hard-refresh browser pages:

- Linux/Windows: `Ctrl+Shift+R`
- macOS: `Cmd+Shift+R`

Use Chrome DevTools → Network → **Disable cache** while testing.

## Security

Scrying Glass is intended for a trusted local network. Do not expose default HTTP ports directly to the public internet. Use HTTPS, a reverse proxy or VPN, strong credentials, and a non-root service account when remote access is needed.
