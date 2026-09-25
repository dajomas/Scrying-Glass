# Monster Display User Guide

## Introduction

Monster Display is a game-master-controlled battle display for tabletop encounters. You work in the **admin screen** while players watch the separate **client display**. Changes to combatants, HP, initiative, visibility, and battle turn appear on the client display in real time.

This guide documents the current working tool, including batch monster creation, setup import, random monster initiative rolls, editable combatants, tied-initiative ordering, and the adaptive monster grid.

---

## Starting the tool

Start the application with its configuration file:

```bash
python3.14 monster_display_server.py --config config.yaml
```

Default addresses:

| Screen | Address |
|---|---|
| Admin | `http://SERVER:3000/` |
| Client display | `http://SERVER:4000/display` |

Replace `SERVER` with the server’s hostname or IP address. For local testing, use `localhost`.

```text
http://localhost:3000/
http://localhost:4000/display
```

---

## Logging in

Use an account configured with the correct role:

| Role | Use | Typical port |
|---|---|---:|
| Admin | Build encounters and control combat | 3000 |
| Client | View player-facing battle display | 4000 |

Log in as an admin before using creation, update, save, load, import, battle, or reset controls.

---

## Admin screen overview

The admin page has these areas:

1. **Setup management** — New, Save, Load, and Import from setup.
2. **Battle controls** — Start battle, Next, Reset All.
3. **Add monster** — Manual monster form and `.monster` import form.
4. **Add character** — Character form.
5. **Monsters** — Roll initiatives plus monster records and controls.
6. **Characters** — Character records and controls.

A green button normally indicates that a setting is on. Blue buttons are normal controls. Purple controls are setup import/reset-related; orange is used for the bulk monster initiative roll.

---

## Managing setups

A saved setup stores the monster list, character list, HP, initiative, colors, images, visibility, battle state, and battle order at the time you save it.

### New

Click **New** to clear the working encounter after confirmation.

- Existing saved setups are not deleted.
- The client display updates to background-only mode when no active monsters remain.
- Save first if you need the current working encounter later.

### Save

1. Enter a name in **Battle setup name**.
2. Click **Save**.

The name is normalized for storage. For example:

```text
Throne Room — Lytharia
```

becomes approximately:

```text
throne-room-lytharia
```

Saving the same name again overwrites the saved setup.

### Load

1. Select a saved setup from the dropdown.
2. Click **Load**.
3. Confirm the replacement.

Load replaces the complete current working encounter.

### Import from setup

Use **Import from setup** when you want to add combatants from a saved setup without replacing the encounter currently being prepared or played.

1. Click **Import from setup**.
2. Select the source saved setup.
3. Choose one of:
   - Characters only
   - Monsters only
   - Characters and monsters
4. Click **Import**.
5. Confirm the operation.

Imported combatants are independent copies with new IDs. They are reset and do not alter the active battle order.

| Imported property | Monsters | Characters |
|---|---|---|
| Active | Off | Off |
| Alive | Yes | Yes |
| Visible | Off | Off |
| Current turn | Off | Off |
| Current HP | Original/reset HP | Max HP |
| Max HP | Original/reset HP | Kept from saved setup |
| Initiative | Original/reset initiative | Original/reset initiative |

---

## Adding monsters

### Add a monster manually

Complete the manual monster form:

| Field | Meaning |
|---|---|
| Name | Monster display name |
| Monster type | Type such as `dragon`, `humanoid`, or `undead` |
| AC | Armor Class |
| HP | Starting HP and initial reset/max HP |
| Quantity | Number of copies to create; defaults to 1 |
| Color | Client card and initiative-token color |
| Image | Optional PNG, JPG, GIF, or WebP image |

Click **Add manually**.

### Add multiple copies

Set Quantity to a number from 1 to 50. Every copy:

- Has a unique internal ID.
- Starts inactive.
- Starts alive.
- Starts hidden from the initiative bar.
- Has its own HP, initiative, active status, and battle controls.
- Uses the same configured name, type, AC, HP, color, and image reference.

### Import a `.monster` file

Use the lower monster import form:

1. Choose a compatible JSON `.monster` file.
2. Set Quantity, default 1.
3. Choose a color.
4. Optionally choose an image.
5. Click **Import .monster**.

The importer uses name, type, AC, and HP from the file. It supports the supplied format where AC may be embedded in text such as:

```text
17 Ice bound robes (reinforced by magical ward)
```

### Monster image behavior

- A manually uploaded image is used first.
- If no image is uploaded, the tool can attempt a public D&D Beyond lookup based on monster type.
- Remote image lookup is best effort; use manual image upload for reliable results.

---

## Adding characters

Add a character with:

| Field | Meaning |
|---|---|
| Name | Character/NPC name |
| Color | Initiative-bar color |
| HP | Starting and initial Max HP; defaults to 1 |
| Initiative | Optional; may be changed later |

Characters begin inactive, alive, and hidden from the initiative bar.

---

## Edit combatants

Every monster and character has an **Edit** button.

### Edit a monster

The Monster Edit dialog supports:

- Name
- Monster type
- AC
- Current HP
- Max HP
- Reset HP
- Color
- Initiative
- Ally status
- Optional replacement image

**Reset HP** is what the monster’s individual Reset and Reset All restore for both current HP and Max HP.

### Edit a character

The Character Edit dialog supports:

- Name
- Color
- Current HP
- Max HP
- Initiative

Changing a character’s Max HP changes the amount restored by reset. For example, if Max HP changes from 12 to 30, a later Reset restores the character to 30/30.

### Close the Edit dialog

You can close Edit without saving by:

- Clicking **Cancel**.
- Pressing `Escape`.
- Clicking outside the dialog on the dark overlay.

---

## Monster controls

| Control | Action |
|---|---|
| Edit | Opens the complete monster editor |
| Active / Off | Adds/removes the monster from the client stage and battle eligibility |
| Ally | Marks the monster as an ally; this is currently classification only |
| Visible | Shows/hides the monster in the initiative bar |
| Turn | Makes the monster the current battle turn, if active and alive |
| Reset | Restores reset HP, reset initiative, and initial display/battle state |
| AC on/off | Shows/hides AC on the client monster card |
| HP on/off | Shows/hides HP on the client monster card |
| Init on/off | Shows/hides initiative on the client monster card |
| Damage | Subtracts entered damage from current HP |
| Heal | Adds entered healing to current HP |

### Monster death

When monster HP drops below 0:

- The monster becomes dead.
- It leaves the main client display stage.
- It cannot be set to Turn.
- It becomes Visible in the initiative bar automatically.
- Its initiative-bar token has a black border.

Use Reset to restore it to alive state and its configured Reset HP.

---

## Character controls

| Control | Action |
|---|---|
| Edit | Opens the character editor |
| Current HP | Inline editable current HP |
| Max HP | Inline editable Max HP; becomes reset baseline |
| Initiative | Inline editable initiative |
| Active / Off | Enables/disables battle eligibility |
| Alive / Dead | Manually changes life state |
| Visible | Shows/hides the character from initiative bar |
| Turn | Makes the character the current battle turn, if active and alive |
| Reset | Restores current HP to Max HP and initial battle/display state |
| Damage | Subtracts entered damage |
| Heal | Adds entered healing |

A character becomes dead when HP drops below 0 or when you set Alive/Dead to Dead.

---

## Roll monster initiatives

At the top of the Monster section, click:

```text
Roll monster initiatives (d20)
```

After confirmation, the tool overwrites the initiative of **every monster** with an independent random d20 result from 1 through 20.

This applies to active and inactive monsters, living and dead monsters. Existing initiative values are intentionally replaced.

---

## Visibility rules

Visible controls initiative-bar inclusion, not whether a monster card appears on the client stage.

| State | Active | Visible | Result |
|---|---|---|---|
| Inactive, hidden | Off | Off | Not in battle and absent from initiative bar |
| Active, hidden | On | Off | In battle but not currently shown in initiative bar |
| Active, visible | On | On | In battle and displayed in initiative bar |
| Dead | Either | Automatically on | Displayed in initiative bar with black border |

Visibility is turned on automatically when a combatant:

- Receives the current Turn.
- Dies.

Reset returns visibility to off.

---

## Initiative and battle flow

### Set initiative

Enter initiatives in the row inputs, edit dialogs, or use the monster d20 roll button. Click outside the input or press Enter to save an inline value.

### Start battle

1. Set desired combatants to **Active**.
2. Ensure they are alive.
3. Set initiatives.
4. Click **Start battle**.

The tool orders active living combatants by initiative descending. Combatants with blank initiative appear after combatants with numeric initiatives.

### Resolve ties

When two or more active living combatants have the same numeric initiative, a tie dialog appears.

For every tied combatant, choose a unique position:

```text
Initiative 18

Ogre       [ 2 ]
Ranger     [ 3 ]
Skeleton   [ 1 ]
```

Position 1 acts first inside that tied group.

Tie order never moves a combatant outside its initiative value. Given:

```text
Dragon 22
Ogre 18
Ranger 18
Skeleton 18
Goblin 14
```

and the selection Skeleton 1, Ogre 2, Ranger 3, the final order is:

```text
Dragon → Skeleton → Ogre → Ranger → Goblin
```

### Next

Click **Next** to remove the current turn and select the next active, living combatant. The order wraps back to the beginning after the last eligible combatant.

Dead and inactive combatants are skipped.

### Activate a combatant during battle

When a battle has already started and an Off, living combatant is changed to Active, it joins the existing battle order by initiative:

- Higher initiative before lower initiative.
- After existing combatants with the same initiative.
- Numeric initiatives before initiative-less combatants.
- Initiative-less combatants appended after numeric initiatives.

The currently active turn does not change.

Example existing order:

```text
Dragon 22 → Ranger 18 → Ogre 18 → Goblin 14
```

Activating Skeleton with initiative 18 results in:

```text
Dragon 22 → Ranger 18 → Ogre 18 → Skeleton 18 → Goblin 14
```

---

## Initiative bar

The client initiative bar displays names only.

| Combatant status | Border |
|---|---|
| Current Turn | Red |
| Dead | Black |
| Other visible combatant | White |

The text color is calculated as black or white based on the configured combatant color.

---

## Client monster display

Active, living monsters appear on the client stage in an adaptive grid.

| Active living monsters | Grid |
|---:|---|
| 1 | 1 row × 1 column |
| 2 | 1 row × 2 columns |
| 3–4 | 2 rows × 2 columns |
| 5–6 | 2 rows × 3 columns |
| 7–9 | 3 rows × 3 columns |
| 10–12 | 3 rows × 4 columns |
| 13–16 | 4 rows × 4 columns |

The grid continues by adding a column when full, then adding a row when full again.

Cards fill rows from left to right:

```text
Five monsters: 2 rows × 3 columns

Monster 1 | Monster 2 | Monster 3
Monster 4 | Monster 5 | empty
```

A monster card displays name and type by default. AC, HP, and initiative appear only if enabled by the associated monster controls.

---

## Reset behavior

### Individual Reset

| Entity | Result |
|---|---|
| Monster | Restores current HP and Max HP to Reset HP; clears Active, Visible, Turn, and monster stat display flags |
| Character | Restores current HP to current Max HP; clears Active, Visible, and Turn |

Both become alive and restore reset/original initiative.

### Reset All

Reset All resets every combatant, clears battle order, and sorts the admin tables separately by Max HP descending.

- Monster table: highest Max HP first.
- Character table: highest Max HP first.

---

## Persistence and backups

The configured storage directory contains:

```text
monster-display-data/
├── state.json
├── uploads/
└── setups/
```

| Path | Purpose |
|---|---|
| `state.json` | Active current encounter |
| `setups/*.json` | Named setups |
| `uploads/` | Uploaded images |

Back up the whole storage directory to preserve setups and their image references.

---

## Troubleshooting

### The page is an old version

Use a hard refresh:

- `Ctrl+Shift+R` on Linux/Windows.
- `Cmd+Shift+R` on macOS.

### Admin buttons do not work

Open browser developer tools with `F12`, select Console, and reload. A JavaScript error can stop later button handlers from registering.

### `Sign in required`

Use an admin-role account at the admin port. Clear cookies for the server hostname if moving between older versions.

### Client display does not update

Confirm port 4000 is accessible and refresh the client page to reconnect WebSocket updates.

### D&D Beyond image is missing

The lookup is best effort. Upload a monster image manually for reliable display.
