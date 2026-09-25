# Monster Display

A real-time, browser-based tabletop battle display for game masters. Run a private **admin interface** for encounter management and a separate **client display** for players, a TV, or a projector.

Monster Display tracks monsters and characters, HP, initiative, turns, death, visibility, and reusable battle setups. Admin changes are broadcast to connected client displays in real time using WebSockets.

> Current documented implementation: **v4.3.1**

## Features

- Separate admin and player/client applications on different TCP ports.
- Username/password accounts with `admin` and `client` roles.
- Real-time client updates through WebSockets.
- Manual monster creation and `.monster` JSON-file import.
- Optional image upload for monsters.
- Best-effort public D&D Beyond image lookup when no monster image is uploaded.
- Characters with editable current HP, Max HP, initiative, life state, color, and visibility.
- Monsters with AC, HP, initiative, ally classification, stat visibility controls, and image support.
- Damage and healing controls for both monsters and characters.
- Automatic death when HP drops below 0.
- Initiative bar with automatic readable text contrast.
- Red border for current turn, black border for dead combatants, and white border for other visible combatants.
- Current-turn and dead combatants automatically become visible in the initiative bar.
- Battle start, Next-turn, individual reset, and Reset All controls.
- Named New/Save/Load battle setups.
- JSON persistence of current state, setups, and uploaded media references.
- Configurable client background, animation direction, ports, bind address, storage path, and remote image lookup.

## Screenshots

The project currently does not ship with screenshots. The two interfaces are:

| Interface | Default URL | Purpose |
|---|---|---|
| Admin | `http://SERVER:3000/` | Encounter setup and real-time GM controls |
| Client display | `http://SERVER:4000/display` | Player-facing initiative bar and monster stage |

## Requirements

- Python **3.14** or newer.
- A modern browser.
- Network access between the host and client-display device(s), if using a TV/projector/tablet on the LAN.

### Python packages

```text
fastapi
uvicorn[standard]
PyYAML
python-multipart
```

## Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/YOUR-ACCOUNT/monster-display.git
cd monster-display

python3.14 -m venv .venv
. .venv/bin/activate

python3.14 -m pip install --upgrade pip
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

Place the application source at a predictable path, for example:

```text
monster_display_server.py
```

> The implementation has been delivered in versioned filenames during development. For normal repository use, choose the current versioned source and rename/copy it to `monster_display_server.py`.

## Quick start

### 1. Create configuration

Create `config.yaml`:

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

### 2. Start the server

```bash
python3.14 monster_display_server.py --config config.yaml
```

### 3. Open the applications

| Role | URL |
|---|---|
| Game master/admin | `http://SERVER:3000/` |
| Player/client display | `http://SERVER:4000/display` |

Replace `SERVER` with the hostname or IP address of the system running Monster Display. For local testing, use `localhost`.

```text
http://localhost:3000/
http://localhost:4000/display
```

## Usage

### Setup workflow

1. Log in to the admin interface with an account whose role is `admin`.
2. Click **New** to start a blank encounter, or **Load** a previously saved setup.
3. Add monsters manually or import compatible `.monster` files.
4. Add characters with name, color, HP, and optional initiative.
5. Set initiatives and enable **Active** for participating combatants.
6. Enter a battle-setup name and click **Save** to preserve the encounter.
7. Open the client display on the player-facing device.
8. Click **Start battle**. Resolve real duplicate initiative values when prompted.
9. Use **Next** to advance turns and use Damage/Heal controls as the encounter progresses.

### Monsters

A monster has:

- Name and monster type.
- Armor Class and HP.
- A configured color.
- Optional uploaded image.
- Optional D&D Beyond image lookup when no image is uploaded.
- Active, Ally, Visible, and Turn controls.
- Individual AC, HP, and initiative display toggles.
- Damage, Heal, and Reset controls.

Monsters become dead when HP is below 0. A dead monster is removed from the main client stage, becomes visible in the initiative bar, and cannot take a battle turn until reset.

### Characters

A character has:

- Name and color.
- Editable current HP and Max HP.
- Optional initiative.
- Active, Alive/Dead, Visible, and Turn controls.
- Damage, Heal, and Reset controls.

Changing a character’s Max HP changes the HP amount restored by reset. A character Reset keeps the current Max HP and restores current HP to that value.

### Initiative bar

The client initiative bar displays names only.

| State | Border color |
|---|---|
| Current battle turn | Red |
| Dead combatant | Black |
| Other visible combatant | White |

The application calculates whether black or white text provides better contrast against each combatant’s configured hex color.

### Visibility rules

- Combatants start with initiative-bar visibility off.
- Setting a combatant as the current turn automatically enables visibility.
- Death automatically enables visibility.
- Individual Reset and Reset All return visibility to off.

### Battle setup controls

| Control | Result |
|---|---|
| New | Replaces the working encounter with an empty one after confirmation |
| Save | Saves the current full state under a normalized name |
| Load | Replaces the working encounter with a selected saved setup |
| Start battle | Applies the initiative order and sets the first living active combatant to current turn |
| Next | Advances to the next active, living combatant |
| Reset All | Resets all combatants, clears battle order, and sorts admin tables by Max HP |

## Data storage

The configured `storage_dir` contains all persistent application data:

```text
monster-display-data/
├── state.json
├── uploads/
│   ├── <uuid>.png
│   └── <uuid>.webp
└── setups/
    ├── goblin-ambush.json
    └── throne-room-lytharia.json
```

| Path | Description |
|---|---|
| `state.json` | The active working encounter; persisted after mutations |
| `setups/*.json` | Named reusable battle setups |
| `uploads/` | Uploaded monster images |

Back up the complete `storage_dir`, rather than only `state.json`, so saved setup image references remain valid.

## Configuration

Command-line options override the configuration file:

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
| `--client-port PORT` | Client-display application port |
| `--storage-dir PATH` | Persistent state/media/setup directory |

## Passwords and security

The example configuration supports plaintext passwords for trusted local/LAN use. Change the sample passwords before use.

The application also supports scrypt password hashes. Generate one with:

```bash
python3.14 -c 'from monster_display_server import password_hash; print(password_hash("replace-me"))'
```

Use the returned `scrypt$...` value as the configured password.

### Important security notes

Monster Display is designed primarily for a trusted local network. Before exposing it to the Internet:

1. Put it behind an HTTPS reverse proxy.
2. Restrict admin-port access by firewall, VPN, or trusted IP ranges.
3. Use scrypt-hashed passwords.
4. Run it as a dedicated non-root user.
5. Set restrictive filesystem permissions on `config.yaml` and the storage directory.
6. Consider disabling D&D Beyond image lookup if outbound lookup requests are undesirable.

## Systemd service example

Create `/etc/systemd/system/monster-display.service`:

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

Enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now monster-display
sudo systemctl status monster-display
```

## Verification and troubleshooting

### Validate Python syntax

```bash
python3.14 -m py_compile monster_display_server.py
```

No output means compilation succeeded.

### Confirm listening ports

```bash
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
```

### Confirm the current admin UI is served

For the current setup-enabled build:

```bash
curl -s http://127.0.0.1:3000/ | grep -o 'setupName'
```

Expected output:

```text
setupName
```

### Common issues

| Symptom | Likely cause | Resolution |
|---|---|---|
| `Sign in required` from admin action | Logged into client app/port or stale cookies | Log in as an admin at port 3000; clear site cookies if upgrading from older versions |
| Old UI after upgrade | Browser retains an old page | Use `Ctrl+Shift+R` or `Cmd+Shift+R`; restart the correct process |
| Client display does not update | Firewall, wrong URL, lost WebSocket | Verify port 4000 access, refresh client page, inspect listener with `ss` |
| Monster image is missing | Remote lookup failed or upload file removed | Upload an image manually; preserve `uploads/` when backing up/migrating |
| Saved setup has no image | Referenced upload is absent | Restore the relevant file from `uploads/` |
| Setup list empty | No setup has been saved yet or wrong storage directory | Save a named setup and verify `<storage_dir>/setups/` |

## Architecture summary

Monster Display starts two FastAPI applications inside one Python process:

```text
Admin browser  -> Admin FastAPI app  -> TCP 3000
Client browser -> Client FastAPI app -> TCP 4000 + WebSocket
```

They share one in-memory state store and persist changes to JSON. This design is intentionally simple for a single-host tabletop deployment. Run one process/worker; multiple Uvicorn workers or multiple replicas require external shared state and session infrastructure.

## Limitations

- Intended for a single process and one Uvicorn worker.
- Sessions are stored in memory and disappear on restart.
- No individual combatant deletion UI yet.
- No saved-setup deletion UI yet.
- Monster Max HP is not editable through the admin UI.
- Ally is currently a persisted classification flag without display/gameplay effects.
- Characters appear in the initiative bar but not as full main-stage cards.
- D&D Beyond image lookup is best effort and may fail if the remote website changes or blocks requests.
- Client state contains full encounter information; hiding monster stats is currently a rendering feature, not a data-redaction boundary.

## Development

The source currently embeds the HTML, CSS, and JavaScript in one Python module for easy deployment. For larger feature work, consider separating static assets, adding automated tests, and moving persistent state to SQLite or another database.

High-value test areas include:

- `.monster` JSON parsing.
- Setup save/load and malformed setup rejection.
- State migration/default handling.
- Death, visibility, and current-turn invariants.
- Character Max HP and reset semantics.
- Battle-order validation.
- Admin-table sorting without battle-order mutation.

## License

Add the license for your repository here, for example:

```text
MIT License
```

## Contributing

Contributions should preserve the core operational model:

- Keep the admin and client ports separated.
- Maintain the single-current-turn invariant.
- Persist state changes through the existing mutation flow.
- Broadcast relevant state changes to client displays.
- Include migration defaults when adding fields to saved state.
