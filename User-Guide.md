# Monster Display User Guide

Monster Display lets a game master prepare and control a tabletop encounter from the **Admin** screen while players view a separate, live **Client Display**. The display updates after encounter changes through a WebSocket connection.

For installation and initial configuration, see the repository [README](../README.md). For implementation details and HTTP routes, see [Technical Documentation](Technical-Documentation.md).

## Start and sign in

Start the application with your configuration file:

```bash
python3.14 monster_display_server.py --config config.yaml
```

Open these default addresses:

| Screen | Address | Role required |
|---|---|---|
| Admin | `http://SERVER:3000/` | `admin` |
| Client Display | `http://SERVER:4000/display` | `admin` or `client` |

Replace `SERVER` with the hostname or IP address of the computer running Monster Display. Use `localhost` when both browser windows run on that computer.

## Admin screen

The Admin screen is organized into panes. The top pane has controls for showing or hiding the other hideable panes. During battle, those panes automatically collapse once; if you manually show one while the battle remains active, it stays visible until you hide it or the battle ends.

| Pane | Purpose |
|---|---|
| Battle | Shows battle state, starts/advances/resets combat, and displays the current order |
| Battle setups | New, save, load, import a saved setup, and import monster/character CSV files |
| Add monster | Manual monster creation and `.monster` JSON import |
| Add character | Manual character creation |
| Monsters | Monster list, individual controls, d20 initiative roll, and bulk controls |
| Characters | Character list and individual controls |
| Activity log | Review actions and export or clear the log |

A green control generally means enabled. The Battle pane shows **Active** when a battle order exists and **Inactive** when it does not.

## Manage setups

### New setup

Click **New** and confirm to replace the working encounter with an empty one. This does not delete saved setups. Save the current encounter first if it must be retained.

### Save setup

1. Enter a name in **Battle setup name**.
2. Click **Save**.

The name is normalized for storage. For example, `Throne Room — Lytharia` becomes a filename similar to `throne-room-lytharia.json`. Saving the same normalized name overwrites that setup.

### Load setup

1. Select a setup from the load list.
2. Click **Load** and confirm.

Loading replaces the complete working state, including combatants, current HP, battle order, and activity log. If the loaded setup has an active battle, the hideable panes collapse once.

### Import from setup

Import adds reset-state copies of saved combatants without replacing the working encounter.

1. Click **Import from setup**.
2. Choose the source setup.
3. Choose Characters, Monsters, or Both.
4. Click **Import** and confirm.

Imported combatants receive fresh IDs. They start inactive, alive, hidden from the initiative bar, and out of turn. Imported monsters restore to their reset HP; imported characters restore to their current maximum HP. The current battle order is not changed.

## Add combatants

### Add a monster manually

Use the Add monster form:

| Field | Meaning |
|---|---|
| Name | Display name |
| Monster type | Creature type or description |
| AC | Armor Class |
| HP | Initial current, max, and reset HP |
| Quantity | Number of identical independent entries, 1–50 |
| Color | Card outline and initiative-token color |
| Image | Optional PNG, JPG, JPEG, GIF, or WebP image |

Each created copy has its own ID, HP, initiative, and controls. A manually uploaded image takes precedence over optional remote image lookup.

### Import a `.monster` file

Choose a compatible JSON `.monster` file, then optionally choose quantity, color, and an image. The importer reads the file’s name, type, AC, and HP.

### Add a character

Characters need a name, color, and HP. Initiative is optional. A new character starts inactive, alive, and hidden from the initiative bar.

## Import CSV files

Use **Import monsters CSV** or **Import characters CSV** in the Battle setups pane. Imported entries are appended to the current encounter.

If the file contains an `id` column, non-empty IDs are preserved. If the column is absent or a row has an empty ID, Monster Display generates a unique ID. Duplicate IDs in the CSV or conflicts with the current encounter are rejected.

### Monster CSV

Required fields:

```text
name,monster_type,ac,hp
```

`type` can be used instead of `monster_type`. Example:

```csv
id,name,monster_type,ac,hp,max_hp,initiative,color,ally,show_ac,show_hp,show_initiative
,Ice Guard,humanoid,16,45,45,14,#842029,false,true,true,true
ice-mage-1,Ice Mage,humanoid,13,52,52,17,#4c1d95,false,true,true,true
```

Optional monster columns include `id`, `max_hp`, `original_hp`, `color`, `image_url`, `active`, `alive`, `visible`, `ally`, `initiative`, `original_initiative`, `show_ac`, `show_hp`, and `show_initiative`.

### Character CSV

Only `name` is required. Example:

```csv
id,name,hp,max_hp,initiative,color,active,visible
,Aelwyn,34,34,16,#1f4e79,false,false
brom-1,Brom,48,48,11,#0f766e,false,false
```

Optional character columns include `id`, `hp`, `max_hp`, `original_hp`, `initiative`, `original_initiative`, `color`, `active`, `alive`, and `visible`.

Boolean fields accept `true`/`false`, `yes`/`no`, `on`/`off`, or `1`/`0`.

## Monster controls

| Control | Result |
|---|---|
| Edit | Edit name, type, AC, HP, max/reset HP, color, initiative, Ally, and image |
| Active / Off | Includes or removes the monster from active battle eligibility and the client stage |
| Ally | Records ally classification |
| Visible | Shows or hides the monster in the initiative bar |
| Turn | Makes the monster the current turn when it is active and alive |
| Reset | Restores the monster’s reset HP, initiative, and default runtime state |
| AC, HP, Init | Shows or hides that stat on the client monster card |
| Damage / Heal | Prompts for and applies an HP change; records activity-log entries |

Dead monsters leave the main stage, become visible in the initiative bar, and cannot receive a turn. Monster Display treats HP of zero or lower as dead.

### Bulk monster controls

The Monster pane includes five bulk controls:

- **Active all**
- **Ally all**
- **AC all**
- **HP all**
- **Init all**

A bulk control enables the field for all monsters when any monster does not have it enabled. If all monsters already have it enabled, it disables the field for all monsters. Bulk activation activates only living monsters. Newly activated monsters are inserted into an existing battle order by initiative.

### Roll initiatives

**Roll monster initiatives d20** assigns an independent random value from 1 through 20 to every monster. It overwrites existing monster initiatives.

## Character controls

| Control | Result |
|---|---|
| Edit | Edit name, color, current HP, max HP, and initiative |
| Current HP | Direct inline HP edit |
| Max HP | Direct inline maximum-HP edit; becomes the reset baseline |
| Initiative | Direct inline initiative edit |
| Active / Off | Enables or disables battle eligibility |
| Alive / Dead | Changes character life state |
| Visible | Shows or hides the character in the initiative bar |
| Turn | Makes the character the current turn when active and alive |
| Reset | Restores current HP to max HP, reset initiative, and default runtime state |
| Damage / Heal | Prompts for an HP change and creates an activity-log entry |

## Run a battle

### Prepare combatants

1. Add or load the desired monsters and characters.
2. Set initiatives.
3. Mark participating living combatants **Active**.
4. Optionally use Visible controls to show initiative tokens before the first turn.

### Start battle and ties

Click **Start battle**. Active living combatants are ordered by descending numeric initiative. Entries without initiative are placed after numeric entries.

If multiple active living combatants have the same numeric initiative, a tie-resolution dialog appears. Choose a unique position for each member of the tied group. The selected ordering affects only that initiative group.

### Mid-battle activation

When a battle order already exists, activating an inactive living combatant adds it to the order:

- Before lower initiative entries.
- After existing entries with the same initiative.
- Before initiative-less entries when it has a numeric initiative.
- After numeric entries when it has no initiative.

The current turn does not change.

### Advance turn

Click **Next**. Monster Display advances to the next active living combatant and wraps to the first eligible entry after the last. Dead and inactive combatants are skipped.

### Current-turn action popup

The current combatant in the Battle order is underlined and marked. Click that combatant to open **Battle actions**.

Each action row contains:

- Target: any currently active, living monster or character.
- Action: Damage, Heal, Buff, or Debuff.
- Amount: required for Damage and Heal; not used for Buff or Debuff.

Click **Add target** to add more rows. Click **Apply** to validate and apply every row. Damage and Heal change HP; Buff and Debuff do not change HP. Every row creates an activity-log entry. The modal closes after successful application.

### Reset all

**Reset All** restores every combatant to its reset state, clears the battle order, returns the Battle marker to Inactive, and reopens panes that were automatically hidden for combat.

## Activity log

The Activity log records actions with these fields:

- Timestamp
- Active combatant
- Active combatant state: alive, dead, or unknown
- Target combatant
- Target combatant state after the action
- Action: damage, heal, buff, or debuff
- Amount for damage/heal; blank for buff/debuff

The active combatant is the current-turn combatant. If a direct damage/heal action happens outside an assigned turn, the log records `System` as the actor.

Use **Export CSV** or **Export JSON** to download the full persisted log. Use **Clear log** to permanently remove all entries after confirmation.

## Client Display

The Client Display shows active, living monsters as cards in an adaptive grid. Characters appear in the initiative bar but do not receive full monster-style cards.

Monster cards show name and type. AC, HP, and initiative appear only when the corresponding monster display toggles are enabled. Text sits on a solid contrast-aware panel for readability over images.

The initiative bar:

- Shows visible combatants from the battle order and additional active, visible combatants.
- Uses red borders for the current turn.
- Uses black borders for dead combatants.
- Uses white borders for other visible combatants.
- Hides completely when it contains no tokens, allowing the stage to use the full screen.

The client background accepts a CSS color, gradient, or image URL. Image backgrounds are centered, do not repeat, and cover the viewport.

## Save data and backups

Persistent files live under `storage_dir`:

```text
monster-display-data/
├── state.json
├── uploads/
└── setups/
```

Back up the full directory, including `uploads/`, not only the JSON files.

## Troubleshooting

### Browser shows an older UI

Hard-refresh after updating the server because HTML, CSS, and JavaScript are served from the Python modules:

- Linux/Windows: `Ctrl+Shift+R`
- macOS: `Cmd+Shift+R`

### Client does not update

Confirm that port 4000 is reachable, then refresh the Client Display to reconnect the WebSocket.

### Admin action says sign-in is required

Use an `admin` account on the Admin port. Clear browser cookies for the server host if sessions became stale after a restart or hostname change.

### CSV import fails

Confirm the file is UTF-8 CSV with a header row, required fields are present, numeric fields are whole numbers, and IDs do not duplicate existing encounter IDs.

### An image is missing

Remote D&D Beyond lookup is best effort. Upload an image manually for predictable results.
