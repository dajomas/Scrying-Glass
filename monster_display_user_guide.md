# Monster Display User Guide

## Purpose

Monster Display is a browser-based battle display tool for tabletop encounters. A game master operates an **admin screen** while players view a separate **client display**. Changes made by the administrator—combatants, hit points, initiative, visibility, and turns—are sent to connected client screens in real time.

The current application version documented here is **v4.3.1**.

---

## Contents

1. [What you need](#what-you-need)
2. [Starting the application](#starting-the-application)
3. [Opening the admin and client screens](#opening-the-admin-and-client-screens)
4. [Logging in](#logging-in)
5. [Admin screen overview](#admin-screen-overview)
6. [Managing battle setups](#managing-battle-setups)
7. [Adding monsters](#adding-monsters)
8. [Adding characters](#adding-characters)
9. [Combatant controls](#combatant-controls)
10. [Initiative and battle flow](#initiative-and-battle-flow)
11. [Client display behavior](#client-display-behavior)
12. [Saving and loading data](#saving-and-loading-data)
13. [Configuration](#configuration)
14. [Operational notes and troubleshooting](#operational-notes-and-troubleshooting)

---

## What you need

- Python 3.14 or later.
- A browser for the admin screen.
- One or more browsers, a TV, projector, or tablet for the client display.
- Network connectivity between the server and the devices viewing the display.

### Python dependencies

Install the required packages in a virtual environment if practical:

```bash
python3.14 -m venv .venv
. .venv/bin/activate
python3.14 -m pip install --upgrade pip
python3.14 -m pip install "fastapi>=0.115" "uvicorn[standard]>=0.30" "PyYAML>=6.0" python-multipart
```

---

## Starting the application

Start the server with a YAML or JSON configuration file:

```bash
python3.14 monster_display_server.py --config config.yaml
```

The example configuration uses these default ports:

| Service | Default port | Purpose |
|---|---:|---|
| Admin | 3000 | Create and manage combatants, battle controls, save/load setups |
| Client display | 4000 | Player-facing initiative bar and active monster display |

You can override network values on the command line:

```bash
python3.14 monster_display_server.py \
  --config config.yaml \
  --bind 0.0.0.0 \
  --admin-port 3000 \
  --client-port 4000 \
  --storage-dir /var/lib/monster-display
```

Command-line arguments override the corresponding configuration-file values.

---

## Opening the admin and client screens

Replace `SERVER` below with the server hostname or IP address.

| Screen | Address |
|---|---|
| Admin login | `http://SERVER:3000/login` |
| Admin home | `http://SERVER:3000/` |
| Client login | `http://SERVER:4000/login` |
| Client display | `http://SERVER:4000/display` |

For a local test on the same machine, use `localhost`:

```text
http://localhost:3000/
http://localhost:4000/display
```

Use the same hostname consistently. For example, avoid using `localhost` in one tab and a LAN IP address in another unless you intend to keep browser sessions separate.

---

## Logging in

Accounts are configured in `config.yaml` under `security.users`. Each account has:

- `username`
- `role`: `admin` or `client`
- `password`

Example:

```yaml
security:
  users:
    - username: "dm"
      role: "admin"
      password: "replace-this-admin-password"
    - username: "table"
      role: "client"
      password: "replace-this-client-password"
```

### Roles

| Role | Can do |
|---|---|
| Admin | Manage setups, add and update combatants, control turns, start/reset battles |
| Client | Open the player-facing display and receive live updates |

Use the admin account on port 3000. Use a client account on port 4000 for a player screen. The two ports host separate applications, so a client login cannot be used for admin actions.

---

## Admin screen overview

The admin screen has five practical areas:

1. **Setup controls** — New, Save, and Load named battle setups.
2. **Battle controls** — Start battle, Next, and Reset All.
3. **Add monster** — Add manually or import a `.monster` file.
4. **Add character** — Add player characters, allies, or other named combatants.
5. **Monster and character tables** — Update every combatant during play.

### Button appearance

Buttons that are currently enabled commonly appear green. A normal blue button is usually off or inactive. Red buttons are typically damage actions; purple buttons are reset actions.

---

## Managing battle setups

A battle setup is a named saved collection of monsters, characters, HP values, initiatives, visibility settings, colors, and the current battle order.

### Create a new setup

1. Click **New**.
2. Confirm the warning.
3. The current working encounter becomes empty.
4. Add monsters and characters for the new encounter.
5. Enter a setup name and click **Save**.

New does not delete existing saved setups. Save your current work first if you need it later.

### Save a setup

1. Type a name into **Battle setup name**.
2. Click **Save**.
3. A name such as `Throne Room — Lytharia` is stored using a safe normalized filename, for example:

   ```text
   throne-room-lytharia.json
   ```

4. Saving an existing name overwrites that saved setup.

### Load a setup

1. Select a setup from the **Load saved setup** dropdown.
2. Click **Load**.
3. Confirm replacement of the currently active setup.

Loading immediately updates the admin page and all client displays.

### Where setups are stored

Setups are JSON files stored in:

```text
<storage_dir>/setups/
```

For the default configuration, this is:

```text
./monster-display-data/setups/
```

Uploaded monster images are stored separately in:

```text
<storage_dir>/uploads/
```

Do not remove the upload directory if you want saved setups to retain their uploaded images.

---

## Adding monsters

### Add a monster manually

In **Add monster**, enter:

| Field | Required | Description |
|---|---|---|
| Name | Yes | Display name, such as `Ice Queen` |
| Monster type | Yes | Monster type, such as `humanoid`, `dragon`, or `goblin` |
| AC | Yes | Armor Class |
| HP | Yes | Starting and initial maximum HP |
| Color | Yes | Color used on the client display and initiative token |
| Image | No | PNG, JPG, GIF, or WebP image |

Click **Add manually**. The new monster is inactive, alive, and not visible in the initiative bar by default.

### Import a `.monster` file

1. Use the **Import .monster** form.
2. Choose a compatible `.monster` file.
3. Select a display color.
4. Optionally select an image.
5. Click **Import .monster**.

The importer reads JSON-formatted `.monster` files and extracts:

- Name
- Monster type
- AC
- HP

If no image is uploaded, the tool can attempt a best-effort public D&D Beyond image lookup based on monster type. A manual image upload is more reliable and always takes priority.

### Monster display controls

| Control | Meaning |
|---|---|
| Active / Off | Shows or removes the monster from the main client monster stage. Active living monsters are eligible for battle turns |
| Ally | Marks the monster as an ally. This is currently a saved classification flag; it does not change turn logic or visual styling |
| Visible | Shows or hides the monster in the client initiative bar |
| Turn | Makes the monster the current combatant, if it is active and alive |
| Reset | Restores original monster HP/max HP and initial combat/display state |
| AC on/off | Shows or hides AC on the main monster card |
| HP on/off | Shows or hides HP on the main monster card |
| Init on/off | Shows or hides initiative on the main monster card |
| Damage | Subtracts a chosen HP amount |
| Heal | Adds a chosen HP amount |

### Monster death

If monster HP drops below 0:

- The monster becomes dead.
- It leaves the main client monster stage with the configured exit animation.
- It cannot be assigned the battle turn.
- It is forced visible in the initiative bar.
- Its initiative token gets a black border.

Use **Reset** to restore a dead monster to its original alive state and original HP.

---

## Adding characters

In **Add character**, enter:

| Field | Required | Description |
|---|---|---|
| Name | Yes | Character or NPC name |
| Color | Yes | Initiative-bar token color |
| HP | Yes | Starting HP; prefilled with `1` |
| Initiative | No | Initiative value; can be entered or changed later |

Characters are created inactive, alive, and not visible in the initiative bar.

### Character controls

| Control | Meaning |
|---|---|
| Current HP | Editable current hit points |
| Max HP | Editable maximum hit points |
| Initiative | Editable initiative value |
| Active / Off | Makes the character eligible or ineligible for battle progression |
| Alive / Dead | Manually changes life state |
| Visible | Shows or hides the name from the initiative bar |
| Turn | Makes the character the current combatant, if active and alive |
| Reset | Restores combat state and heals the character to current Max HP |
| Damage | Subtracts a chosen HP amount |
| Heal | Adds a chosen HP amount |

### Character Max HP and reset behavior

Changing a character’s **Max HP** establishes the character’s new reset baseline.

For example:

1. Create a character with HP 10.
2. Change Max HP to 25.
3. Apply Damage until the character has 8 HP.
4. Click Reset.

The result is 25 current HP out of 25 Max HP. Reset does not restore the original creation-time Max HP.

### Character death

A character becomes dead when:

- HP falls below 0, or
- You press the Alive/Dead toggle to set the character to Dead.

When dead, the character:

- Cannot be assigned a battle turn.
- Becomes visible in the initiative bar automatically.
- Uses a black initiative-token border.

---

## Combatant visibility

**Visible** controls whether a combatant name appears in the initiative bar. It is independent from **Active**.

| Setting | Active | Visible | Result |
|---|---|---|---|
| Inactive, hidden | Off | Off | Not participating and absent from initiative bar |
| Active, hidden | On | Off | Participates in encounter but is not shown in initiative bar until made visible or given a turn |
| Active, visible | On | On | Participates and appears in initiative bar |
| Dead | Either | Automatically on | Appears in initiative bar with black border |

A combatant automatically has Visible enabled when:

- It is made the current battle turn.
- It dies.

Individual Reset and Reset All return Visible to off.

---

## Initiative and battle flow

### Enter initiative

Enter initiative directly in each combatant’s Initiative input. Press Enter or click elsewhere to save it.

### Start battle

1. Mark the required living combatants as **Active**.
2. Set their initiatives.
3. Click **Start battle**.

The tool builds a battle order from active, living combatants, sorted by initiative descending. Combatants without initiative are placed after numeric initiatives.

If two or more active living combatants have the same numeric initiative, the **Resolve tied initiative** dialog opens. Select which combatant acts first within each tied group, then click **Start battle** in the dialog.

The first combatant receives the battle turn and becomes visible automatically.

### Next

Click **Next** to:

1. Remove the battle turn from the current combatant.
2. Move it to the next active, living combatant in battle order.
3. Wrap back to the first living combatant after the final combatant.

Dead or inactive combatants are skipped.

### Manual turn control

You can use an individual combatant’s **Turn** button at any time. Only one combatant can have the battle turn. Setting a new combatant to Turn clears Turn from every other combatant.

### Initiative bar borders

| Initiative-token status | Border |
|---|---|
| Current battle turn | Red |
| Dead | Black |
| Other visible combatant | White |

The initiative bar displays only combatant names, not initiative values. Text color is selected automatically as black or white according to the combatant’s configured background color.

### Start Battle table sorting

After Start battle, the admin tables are sorted separately by initiative:

- Monster table: highest initiative first.
- Character table: highest initiative first.

This sorting changes the admin-table presentation only. It does not alter the battle order that was just created.

### Reset All table sorting

After Reset All, the admin tables are sorted separately by Max HP:

- Monster table: highest Max HP first.
- Character table: highest Max HP first.

---

## Client display behavior

The client display is intended for players, a TV, or a projector.

### Empty state

When no monsters are active, the client shows only the configured background plus any visible initiative tokens.

### Active monster card

When a living monster is active, the client displays a full-height monster card with:

- Monster name
- Monster type
- Optional image
- Optional AC
- Optional HP
- Optional initiative
- A turn indicator when it is the current combatant

The admin determines whether AC, HP, and initiative appear by using the three monster stat toggle buttons.

### Entry and exit animation

Monster entry and exit direction are configured in `config.yaml`:

```yaml
display:
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
```

Supported values are:

| Setting | Values |
|---|---|
| `entry_direction` | `from_bottom`, `from_top` |
| `exit_direction` | `to_bottom`, `to_top` |

Client screens receive updates through WebSocket. A reload is normally unnecessary.

---

## Saving and loading data

The application has two different persistent data concepts:

| Data | Location | Meaning |
|---|---|---|
| Current working state | `<storage_dir>/state.json` | The encounter that remains active after a server restart |
| Named setup | `<storage_dir>/setups/<name>.json` | A manually saved, reusable battle setup |
| Uploaded images | `<storage_dir>/uploads/` | Image files referenced by combatants |

### Recommended workflow

1. Click **New**.
2. Create an encounter.
3. Save it with a descriptive name before running it.
4. Run the encounter and track damage/turns.
5. Save again if you want to preserve its current in-progress state.
6. Load the saved setup later for a replay or continuation.

---

## Configuration

A YAML configuration file can look like this:

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
      password: "replace-this-admin-password"
    - username: "table"
      role: "client"
      password: "replace-this-client-password"

display:
  background: "radial-gradient(circle at 50% 15%, #16273d, #080b14 70%)"
  entry_direction: "from_bottom"
  exit_direction: "to_bottom"
  monster_width_percent: 45
  dndbeyond_image_lookup: true
```

### Security note

The example supports plain-text passwords for simple local/LAN usage. If the admin interface is reachable beyond a trusted local network, use HTTPS through a reverse proxy, restrict access to the admin port, and use password hashes instead of plain-text values.

Generate an scrypt password hash with:

```bash
python3.14 -c 'from monster_display_server import password_hash; print(password_hash("replace-me"))'
```

Then use the returned `scrypt$...` value as the configured password.

---

## Operational notes and troubleshooting

### Admin action says “Sign in required”

- Confirm you opened the admin UI on port 3000 and logged in using an `admin` role account.
- Clear cookies for the server host if you previously tested older application versions.
- Do not use a client-only account for admin operations.
- Use a consistent hostname or IP address for the admin screen.

### The page looks like an old version

Hard-refresh the browser:

- Linux/Windows: `Ctrl+Shift+R`
- macOS: `Cmd+Shift+R`

Then verify the server process and its listening ports:

```bash
sudo ss -lptn 'sport = :3000'
sudo ss -lptn 'sport = :4000'
```

### Verify the Python source before starting

Check syntax without starting the server:

```bash
python3.14 -m py_compile monster_display_server.py
```

No output means the syntax check passed.

### Client display is not updating

- Confirm the client is connected to port 4000.
- Refresh the client display page once.
- Confirm the firewall permits TCP port 4000 from client devices.
- Check that the Python process is listening on the configured bind address, typically `0.0.0.0` for LAN access.

### D&D Beyond image is missing

The lookup is best effort. It can fail if the remote site changes its HTML or refuses the request. Upload an image manually for reliable display.

### Saved setup has no image

The setup file stores an image reference, while the actual uploaded file remains in `<storage_dir>/uploads/`. Restore both the setup JSON and its referenced upload file if moving data between servers.

---

## Quick-reference encounter workflow

1. Open the admin page on port 3000 and log in.
2. Click **New** or **Load** an existing named setup.
3. Add/import monsters and add characters.
4. Set HP, Max HP, initiative, colors, Ally flags, and display preferences.
5. Save the setup.
6. Open the client display on port 4000.
7. Mark battle participants **Active**.
8. Click **Start battle** and resolve actual initiative ties if prompted.
9. Use **Next** to progress through turns.
10. Use Damage, Heal, alive/dead, and visibility controls during play.
11. Use **Reset All** to restore combatants for another encounter run, or save the current state as a named setup.
