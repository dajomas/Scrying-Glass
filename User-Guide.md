# Monster Display User Guide

Monster Display lets a game master prepare and run an encounter from the **Admin** screen while players watch a separate, live **Client Display**. The Client Display receives encounter changes through a WebSocket connection.

For installation and configuration, see the repository [README](../README.md). For architecture and API details, see [Technical Documentation](Technical-Documentation.md).

## Start and sign in

Start the application with a configuration file:

```bash
python3.14 monster_display_server.py --config config.yaml
```

| Screen | Address | Login role |
|---|---|---|
| Admin | `http://SERVER:3000/` | `admin` |
| Client Display | `http://SERVER:4000/display` | `client` or `admin` |

Replace `SERVER` with the server hostname or IP address. For local testing, use `localhost`.

Admin and Client Display logins use separate session cookies, so both pages can remain open in different tabs or windows of the same browser.

## Admin panes

The Admin page is organized into panes. The top controls can show or hide the setup, add-monster, add-character, Monster list, and Character list panes.

When a battle starts, or when you load a setup with a battle order, hideable panes automatically collapse once. If you manually reopen a pane during that battle, it remains open until you hide it or the battle ends. **Reset All** restores the normal visible-pane layout.

| Pane | Purpose |
|---|---|
| Battle | Shows Active/Inactive status, battle controls, and battle order |
| Battle setups | New, Save, Load, setup import, and CSV imports |
| Add monster | Manual monster entry and `.monster` import |
| Add character | Manual character entry |
| Monsters | Monster controls, d20 initiative roll, and bulk controls |
| Characters | Character controls |
| Activity log | View, export, and clear recorded actions |

## Battle setups

### New

Click **New** and confirm to discard the working encounter. Existing named setups remain unchanged.

### Save

Enter a setup name and click **Save**. Names are normalized for storage; for example, `Throne Room — Lytharia` is stored under a slug similar to `throne-room-lytharia`.

Saving the same normalized name overwrites that saved setup.

### Load

Select a setup, click **Load**, and confirm. Loading replaces the complete working state: monsters, characters, HP, battle order, and activity log.

### Import from setup

**Import from setup** appends copies of monsters, characters, or both from another setup without replacing the current encounter.

Imported entries:

| Property | Monsters | Characters |
|---|---|---|
| ID | New unique ID | New unique ID |
| Current HP | Retained from source setup | Retained from source setup |
| Max HP | Retained from source setup | Retained from source setup |
| Initiative | Restored to original initiative | Restored to original initiative |
| Active | Off | Off |
| Visible | Off | Off |
| In turn | Off | Off |
| Alive | Derived from retained current HP | Derived from retained current HP |
| Monster AC/HP/Init display flags | Off | Not applicable |
| Current battle order | Unchanged | Unchanged |

The source setup is not changed.

## Add and import combatants

### Add monster manually

| Field | Meaning |
|---|---|
| Name | Display name |
| Monster type | Creature type or description |
| AC | Armor Class |
| HP | Initial current, maximum, and reset HP |
| Quantity | Number of independent copies, from 1 to 50 |
| Color | Card outline and initiative-token color |
| Image | Optional PNG, JPG, JPEG, GIF, or WebP image |

Each copy receives a unique ID and independent runtime values. Uploaded images take precedence over remote lookup.

### Import `.monster`

Monster Display imports compatible JSON `.monster` files. A recommended tool for creating or editing these files is the [Tetra-cube D&D 5e Statblock Generator](https://tetra-cube.com/dnd/dnd-statblock.html).

1. Open the Tetra-cube generator.
2. Create or edit the monster statblock.
3. Save or export the compatible `.monster` JSON file.
4. In Monster Display, choose the file in the Add monster pane.
5. Optionally select quantity, color, and an image.
6. Click **Import .monster**.

Monster Display reads the monster name, type, Armor Class, and Hit Points from the imported file. A manually selected image takes precedence over the optional D&D Beyond image lookup.

> The Tetra-cube generator is an external website and is not affiliated with Monster Display. Its availability and file-export behavior are controlled by that site.

### Add character

Characters require a name, color, and HP. Initiative is optional. New characters begin inactive, alive, hidden from the initiative bar, and out of turn.

### Import monster CSV

Use **Import monsters CSV**. Required fields are:

```text
name,monster_type,ac,hp
```

`type` may be used instead of `monster_type`.

Example:

```csv
id,name,monster_type,ac,hp,max_hp,initiative,color,ally,show_ac,show_hp,show_initiative
,Ice Guard,humanoid,16,45,45,14,#842029,false,true,true,true
ice-mage-1,Ice Mage,humanoid,13,52,52,17,#4c1d95,false,true,true,true
```

Optional fields include `id`, `max_hp`, `original_hp`, `color`, `image_url`, `active`, `alive`, `visible`, `ally`, `initiative`, `original_initiative`, `show_ac`, `show_hp`, and `show_initiative`.

### Import character CSV

Use **Import characters CSV**. The only required field is:

```text
name
```

Example:

```csv
id,name,hp,max_hp,initiative,color,active,visible
,Aelwyn,34,34,16,#1f4e79,false,false
brom-1,Brom,48,48,11,#0f766e,false,false
```

Optional fields include `id`, `hp`, `max_hp`, `original_hp`, `initiative`, `original_initiative`, `color`, `active`, `alive`, and `visible`.

For either CSV type, a provided non-empty ID is retained. If the `id` field is absent or blank, Monster Display generates a unique ID. Duplicate IDs in the CSV or conflicts with the active encounter are rejected. Boolean values accept `true`/`false`, `yes`/`no`, `on`/`off`, or `1`/`0`.

## Monster controls

| Control | Result |
|---|---|
| Edit | Edit name, type, AC, current/max/reset HP, color, initiative, Ally, and image |
| Active / Off | Enables/disables active battle eligibility and Client card visibility |
| Ally | Sets ally classification; ally monsters display as `Name - Ally` |
| Visible | Shows/hides the monster in the initiative bar |
| Turn | Sets the monster as current turn when active and alive |
| AC / HP / Init | Shows/hides each stat on the Client monster card |
| Reset | Restores reset HP, reset initiative, and default runtime state |
| Remove | Permanently removes the monster from the current encounter after confirmation |
| Damage / Heal | Prompts for HP change and writes an activity-log entry |

A monster at zero or lower HP is dead, leaves the Client stage, becomes visible in the initiative bar, and cannot receive the turn.

### Bulk controls

The Monster pane provides **Active all**, **Ally all**, **AC all**, **HP all**, and **Init all**.

A control enables its property for all monsters when any monster does not have it enabled. When every monster already has it enabled, it disables the property for all monsters. **Active all** activates living monsters only and inserts newly activated monsters into an active battle order according to initiative.

### Monster display order in Admin

The Admin Monster table is presentation-sorted as follows:

1. Active monsters first.
2. When a battle is active, active monsters in the battle order’s exact sequence.
3. Outside a battle, active monsters by Max HP descending.
4. Inactive monsters with numeric initiative first, highest initiative first.
5. Inactive monsters with no initiative after that, with Max HP as the secondary order.
6. Name as the final tie-breaker.

This does not modify the actual server monster list or stored battle order.

## Character controls

| Control | Result |
|---|---|
| Edit | Edit name, color, HP, max HP, and initiative |
| Current HP / Max HP | Inline edits; a Max HP update becomes the reset baseline |
| Initiative | Inline initiative edit |
| Active / Off | Enables/disables battle eligibility |
| Alive / Dead | Changes life state |
| Visible | Shows/hides the character in the initiative bar |
| Turn | Sets current turn when active and alive |
| Reset | Restores current HP, initiative, and default runtime state |
| Remove | Permanently removes the character from the current encounter after confirmation |
| Damage / Heal | Prompts for HP change and writes an activity-log entry |

Removing any combatant removes its ID from the current battle order. Saved setups are not affected until you explicitly save the edited working encounter.

## Run a battle

### Prepare and start

1. Add/load combatants and set initiatives.
2. Mark participating living combatants **Active**.
3. Click **Start battle**.
4. Resolve ties when prompted.

Active living combatants are ordered by descending numeric initiative. Combatants with no initiative are placed after numeric initiatives. Within an equal numeric initiative group, the tie dialog requires a unique order for every member.

### Activate during battle

Activating a living inactive combatant after battle start inserts it into the existing order:

- Before lower numeric initiatives.
- After existing combatants with equal initiative.
- Before initiative-less combatants when it has a numeric initiative.
- After numeric initiatives when it has no initiative.

The current turn does not change.

### Advance and reset

**Next** advances cyclically to the next active living combatant. Dead and inactive entries are skipped.

**Reset All** resets all combatants, clears `battle_order`, changes the status marker to **Inactive**, and restores panes that were automatically hidden at battle start.

## Current-turn actions

The current combatant in the Battle order is underlined and marked. Click that entry to open the action popup.

Every row contains:

- A target selector containing active living monsters and characters.
- An action selector: Damage, Heal, Buff, or Debuff.
- An amount field required for Damage and Heal.

Click **Add target** to add more action rows. Click **Apply** to validate every row and apply them together:

- Damage subtracts HP.
- Heal adds HP.
- Buff and Debuff do not alter HP and do not record an amount.
- Every row is added to the Activity Log.

The popup closes after successful application.

## Activity log

The Activity Log contains timestamp, active combatant, active state, target, target state after the action, action, and amount.

Actions are `damage`, `heal`, `buff`, or `debuff`. The amount is blank for Buff/Debuff. Direct HP changes outside a current turn are recorded with `System` as the acting combatant.

Use **Export CSV**, **Export JSON**, or **Clear log**. Clearing is permanent after confirmation.

## Client Display

Active living monsters appear as cards in an adaptive grid. Characters appear in the initiative bar but do not render as full monster cards.

Monster cards show name and type by default. AC, HP, and initiative appear only when the corresponding Monster controls are enabled. Ally monsters use the display name `Name - Ally`. Text is placed on a solid contrast-aware panel for readability over images.

The initiative bar uses:

| State | Border |
|---|---|
| Current turn | Red |
| Dead | Black |
| Other visible combatant | White |

The initiative bar automatically hides when empty, giving the monster stage the full browser viewport.

Client backgrounds accept CSS colors, gradients, and image URLs. Image URLs are centered, do not repeat, and cover the viewport.

## Backups and troubleshooting

Back up the whole configured `storage_dir`, including `uploads/`.

| Issue | What to check |
|---|---|
| Old Admin/Client page after an update | Hard-refresh: `Ctrl+Shift+R` on Linux/Windows or `Cmd+Shift+R` on macOS |
| Client Display does not update | Confirm port 4000 is reachable; refresh to reconnect the WebSocket |
| Sign-in failure | Use the correct role and port; log in again after a server restart |
| CSV import error | Verify UTF-8 encoding, header row, required fields, valid numbers, and unique IDs |
| Missing remote image | D&D Beyond lookup is best effort; upload an image manually |
