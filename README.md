# Monster Display

Monster Display is a self-hosted, real-time tabletop battle display for game masters. It provides a private **admin interface** for encounter preparation and control, plus a separate **client display** for players, a TV, or a projector.

The admin can manage monsters and characters, hit points, initiative, turn order, display visibility, reusable battle setups, and live battle changes. Connected client displays update in real time through WebSockets.

> The tool and the documentation in this repository hav been created using Perplexity.AI

> Current documented implementation: **v4.14** (with the current working source’s post-v4.14 additions: batch monster creation, import from setup, random monster initiatives, and active-combatant battle-order insertion).

## Features

- Separate admin and client applications on configurable TCP ports.
- Role-based accounts: `admin` and `client`.
- Real-time display updates over WebSockets.
- Manual monster creation and compatible `.monster` JSON-file import.
- Batch monster creation/import with a configurable quantity, default `1`.
- Optional monster image upload and best-effort D&D Beyond image lookup.
- Monster editing: name, type, AC, current/max/reset HP, color, initiative, Ally state, and image.
- Character editing: name, color, current HP, Max HP, and initiative.
- Editable character current HP and Max HP.
- Damage and healing controls for monsters and characters.
- Automatic death when HP drops below `0`.
- Manual character Alive/Dead toggle.
- Monster Ally flag.
- Initiative bar visibility controls.
- Automatic initiative visibility when a combatant takes a turn or dies.
- Initiative bar with high-contrast text, white normal borders, red current-turn borders, and black dead borders.
- Battle start, Next, individual Reset, and Reset All controls.
- Tie-resolution UI supporting complete ordering of any number of combatants tied at the same initiative.
- Random d20 initiative rolls for all monsters.
- Named New, Save, Load, and Import-from-setup workflows.
- Import characters, monsters, or both from saved setups as new reset-state copies.
- Adaptive client monster grid with explicit left-to-right, top-to-bottom placement.
- Persistent JSON state, named setups, and uploaded media references.

## Requirements

- Python **3.14** or newer.
- A modern browser.
- LAN connectivity between the server and player-display device(s), if applicable.

### Python dependencies

```text
fastapi
uvicorn[standard]
PyYAML
python-multipart
```

## Installation

```bash
git clone https://github.com/YOUR-ACCOUNT/monster-display.git
cd monster-display

python3.14 -m venv .venv
. .venv/bin/activate

python3.14 -m pip install --upgrade pip
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

Place the current source file at a stable repository path, for example:

```text
monster_display_server.py
```

## Quick start

### 1. Create `config.yaml`

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
  dndbeyond_image_lookup: true
```

### 2. Validate and start

```bash
python3.14 -m py_compile monster_display_server.py
python3.14 monster_display_server.py --config config.yaml
```

### 3. Open the screens

| Screen | Default URL | Purpose |
|---|---|---|
| Admin | `http://SERVER:3000/` | GM encounter management |
| Client display | `http://SERVER:4000/display` | Player-facing display |

For local testing:

```text
http://localhost:3000/
http://localhost:4000/display
```

Replace `SERVER` with the server hostname or IP address for LAN use.

## Encounter workflow

1. Log in to the admin interface using an `admin` account.
2. Click **New**, **Load**, or **Import from setup**.
3. Add monsters manually, import `.monster` files, or import combatants from saved setups.
4. Add characters and set HP, Max HP, colors, and initiatives.
5. Save the setup with a descriptive name.
6. Mark encounter participants **Active**.
7. Use **Roll monster initiatives (d20)** if desired. This overwrites every monster initiative.
8. Click **Start battle** and resolve numeric initiative ties.
9. Use **Next** to advance turns.
10. Use Damage, Heal, Active, Alive/Dead, Visible, Turn, and Edit controls during play.

## Battle setup management

| Control | Behavior |
|---|---|
| New | Replaces the working encounter with an empty setup after confirmation |
| Save | Saves the full working state under a normalized name |
| Load | Replaces the working encounter with a selected saved setup |
| Import from setup | Appends reset-state copies of selected saved characters, monsters, or both |

### Import from setup

Imported combatants receive fresh IDs and do not alter the current battle order.

| Property | Imported monster | Imported character |
|---|---|---|
| Active | Off | Off |
| Alive | Yes | Yes |
| Visible | Off | Off |
| In turn | Off | Off |
| Current HP | Original/reset HP | Current Max HP |
| Max HP | Original/reset HP | Preserved current Max HP |
| Initiative | Original/reset initiative | Original/reset initiative |

## Monsters

Monsters support:

- Name, type, AC, current HP, Max HP, and reset HP.
- Color, optional image, initiative, and Ally state.
- Active, Visible, Turn, Edit, Reset, Damage, and Heal controls.
- Independent toggles for displaying AC, HP, and initiative on the client monster card.
- Manual creation or `.monster` import.
- Batch quantity from 1 to 50, defaulting to 1.

A monster becomes dead when HP falls below `0`. Dead monsters leave the main stage, cannot receive the battle turn, and automatically become visible in the initiative bar.

## Characters

Characters support:

- Name, color, HP, Max HP, and optional initiative.
- Active, Alive/Dead, Visible, Turn, Edit, Reset, Damage, and Heal controls.

When character Max HP changes, it becomes the reset baseline. Reset restores current HP to the active Max HP without changing that Max HP value.

## Initiative and battle flow

### Start battle

- Includes active, living combatants.
- Orders combatants by initiative descending.
- Places combatants without initiative after numeric initiatives.
- Opens a tie dialog only for equal numeric initiative values.
- Supports a complete, unique relative order for every combatant in a tied initiative group.
- Keeps tied combatants inside their correct initiative bucket; a selected tied combatant never moves ahead of a higher initiative.

### Activating a combatant mid-battle

If `battle_order` already exists, changing an inactive, living combatant to **Active** adds it to the existing order:

- Before lower initiatives.
- After all existing combatants with the same initiative.
- Before initiative-less combatants when it has a numeric initiative.
- At the end when it has no initiative.

The current combatant keeps its turn; activating a new combatant does not steal it.

### Initiative bar

The client initiative bar shows names only.

| State | Border |
|---|---|
| Current battle turn | Red |
| Dead | Black |
| Other visible combatant | White |

Text is selected as black or white from the combatant’s configured hex color for readability.

## Client monster grid

All active, living monsters appear together in an adaptive grid. The grid fills top-to-bottom by rows, and left-to-right within each row.

| Monster count | Grid |
|---:|---|
| 1 | 1 × 1 |
| 2 | 1 × 2 |
| 3–4 | 2 × 2 |
| 5–6 | 2 × 3 |
| 7–9 | 3 × 3 |
| 10–12 | 3 × 4 |
| 13–16 | 4 × 4 |

After that, the grid alternates adding a column then a row: 4×5, 5×5, 5×6, and so on.

## Storage

All persistent data lives below `storage_dir`:

```text
monster-display-data/
├── state.json
├── uploads/
│   └── <uuid>.<image-extension>
└── setups/
    └── <setup-name>.json
```

| Location | Purpose |
|---|---|
| `state.json` | Current working encounter, saved after mutations |
| `setups/*.json` | Named reusable battle setups |
| `uploads/` | Uploaded monster images |

Back up the entire storage directory, not only `state.json`, so saved setup image references remain usable.

## Configuration and CLI

Command-line options override values in `config.yaml`:

```bash
python3.14 monster_display_server.py \
  --config config.yaml \
  --bind 0.0.0.0 \
  --admin-port 3000 \
  --client-port 4000 \
  --storage-dir /var/lib/monster-display
```

| Option | Description |
|---|---|
| `--config PATH` | YAML or JSON configuration file |
| `--bind ADDRESS` | Bind address for both applications |
| `--admin-port PORT` | Admin application port |
| `--client-port PORT` | Client display port |
| `--storage-dir PATH` | State, setup, and image directory |

## Passwords and security

The supplied configuration format supports plaintext passwords for trusted LAN use. Change example passwords before use.

Scrypt hashes are supported:

```bash
python3.14 -c 'from monster_display_server import password_hash; print(password_hash("replace-me"))'
```

Use the resulting `scrypt$...` string in the configuration.

### Internet exposure warning

Monster Display is designed for a trusted local network. Before exposing it beyond that:

1. Use an HTTPS reverse proxy.
2. Restrict admin access with firewall rules, VPN, or trusted source IPs.
3. Use scrypt password hashes.
4. Run the service as a dedicated non-root user.
5. Protect `config.yaml` and the persistent storage directory.

## Clean Ctrl-C shutdown

To suppress normal asyncio `CancelledError` / `KeyboardInterrupt` tracebacks on `Ctrl-C`, wrap the final `asyncio.run(serve())` call:

```python
try:
    asyncio.run(serve())
except KeyboardInterrupt:
    pass
```

For more controlled Uvicorn shutdown, retain the server objects, set `should_exit = True`, and await the Uvicorn tasks during cancellation cleanup.

## systemd example

```ini
[Unit]
Description=Monster Display
After=network.target

[Service]
Type=simple
User=monsterdisplay
Group=monsterdisplay
WorkingDirectory=/opt/monster-display
ExecStart=/opt/monster-display/.venv/bin/python /opt/monster-display/monster_display_server.py --config /etc/monster-display/config.yaml
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now monster-display
sudo systemctl status monster-display
```

## Troubleshooting

### Verify syntax

```bash
python3.14 -m py_compile monster_display_server.py
```

No output indicates valid syntax.

### Verify listeners

```bash
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
```

### Old browser UI after upgrade

Hard-refresh:

- Linux/Windows: `Ctrl+Shift+R`
- macOS: `Cmd+Shift+R`

### `Sign in required`

- Use an admin account at port 3000 for mutation actions.
- Clear cookies for the server host if upgrading across versions.
- Use the same hostname/IP consistently.

### Client is not updating

- Verify port 4000 is reachable.
- Refresh the client page to reconnect its WebSocket.
- Confirm firewalls permit TCP port 4000.

### D&D Beyond image missing

Remote lookup is best effort. Upload an image manually for reliable results.

## Architecture

The service starts two FastAPI applications in one Python process:

```text
Admin browser  -> FastAPI admin app  -> TCP 3000
Client browser -> FastAPI client app -> TCP 4000 + WebSocket
```

Both applications share in-memory state, sessions, JSON persistence, image storage, and connected display sockets. Run a single process/worker; multiple workers require external shared state/session infrastructure.

## Limitations

- Single-process design; no multi-worker synchronization.
- Sessions are in-memory and disappear on restart.
- No combatant deletion UI.
- No saved-setup deletion UI.
- Monster Max HP has no inline table editor, but it is editable in the Monster Edit dialog.
- Ally is persisted but does not yet alter gameplay logic or client styling.
- Characters render in the initiative bar but not as full stage cards.
- D&D Beyond image lookup may fail due to remote site changes or request blocking.
- Hidden monster information is visually hidden but remains in the client state payload.

## License

Add your chosen license, for example:

```text
MIT License
```
