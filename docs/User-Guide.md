# Scrying Glass User Guide

Scrying Glass lets a game master manage encounters privately in Admin while players see a live Client Display.

## Sign in

| Screen | Address | Role |
|---|---|---|
| Admin | `http://SERVER:3000/` | `admin` |
| Client Display | `http://SERVER:4000/` or `/display` | `client` or `admin` |

Admin and Client sessions use different cookies, so both can be open in one browser.

## Campaigns and setups

A campaign owns its character roster and groups saved battle setups. One campaign is active at a time.

- A new campaign receives an empty Default setup.
- Activating a campaign opens its last-used setup when available, otherwise its most recently modified setup.
- **New** creates and saves an empty named setup.
- **Save** writes the current working setup under the entered name.
- **Load** replaces the working encounter.
- **Import from setup** appends reset copies of monsters from another saved setup.

### Automatic saving

- Character additions, edits, damage/healing, resets, bulk actions, and removals are saved automatically to the active campaign.
- Monster additions, edits, damage/healing, resets, bulk actions, and removals are saved automatically to the loaded saved setup.
- If no setup is loaded, monster changes remain in the unsaved working encounter. Save before loading/switching to avoid losing intentionally unsaved work.

## Add monsters manually

| Field | Meaning |
|---|---|
| Name | Local encounter name, for example `Mimic 1` |
| Monster species | Canonical creature name for D&D Beyond, for example `Mimic` |
| AC | Armor Class |
| HP Range start | Fixed HP, range start, or dice expression |
| HP Range end | Numeric range end; blank for fixed/dice HP |
| Quantity | 1–50 copies |
| Image | Optional upload |

### HP choices

| HP Range start | HP Range end | Result |
|---|---|---|
| `17` | blank | Every copy gets fixed 17 HP |
| `10` | `20` | Every copy independently receives 10 through 20 HP |
| `3d8+9` | blank | Every copy independently rolls `3d8+9` |

Dice examples:

```text
1d8
2d10+4
3d8 + 9
1d20
1d100-10
```

Spaces around `+`/`-` are optional. Dice HP requires blank HP Range end. The created number becomes current HP, max HP, and reset HP.

### D&D Beyond AC/HP assistance

After entering Monster species, Scrying Glass can look up an exact D&D Beyond result. It prefers an available Legacy-marked match and prefers a source dice expression over average HP.

For example, `58 (9d8 + 18)` fills HP Range start with:

```text
9d8+18
```

The Add monster notification area shows lookup feedback. By default a result fills only blank AC/HP fields. Enable **Overwrite Armor Class and HP Range with found D&D Beyond values** when you want lookup results to replace entered values.

If lookup does not find usable stats, enter values normally; lookup failure does not prevent creation.

### Images and colors

An uploaded image overrides automatic lookup. Without an upload, a best-effort D&D Beyond image lookup uses Monster species.

Every Admin color picker has a dot after it showing the selected color, including default colors. This is visual feedback; the color picker itself is what gets saved.

Click **Edit** for a monster to update fields. The current image appears as a thumbnail no larger than 300px in either dimension. Selecting **Replace image** previews the file immediately, but it uploads only when **Save monster** is clicked. Cancel leaves the stored image unchanged.

## Characters and imports

Characters require name, color, and HP; initiative is optional.

Monster CSV requires:

```text
name,monster_species,ac,hp
```

Character CSV requires:

```text
name
```

Compatible `.monster` JSON imports read `name`, `type`, HP from `hpText` or `hp`, and AC from `ac`, `armorClass`, `otherArmorDesc`, or `natArmorBonus`. Quantity, color, and optional replacement image are selected in the import form.

## Initiative and Client card fields

A monster card can independently show AC, HP, and initiative.

To show initiative on the Client card:

1. Enter a numeric initiative in the Monster row and leave the field to save it.
2. Enable **Init on**.
3. Make the monster active/alive so it has a card during battle.

**Init on** only permits display. It cannot display a blank initiative value.

## Run a battle

1. Add/load combatants and set initiative.
2. Join living participants to battle.
3. Start the battle and resolve ties.
4. Use **Next** to advance active living combatants.
5. Click the underlined current combatant in the battle order for multi-target Damage, Heal, Buff, or Debuff actions.

Damage and Heal require a positive amount. Buff and Debuff use no amount. Actions are recorded in the Activity log.

## Client Display

Active living monsters render as cards. Visible combatants appear in the initiative bar. Monster card backgrounds can use images; card AC/HP/initiative fields appear only when enabled. Each setup can have its own display background color, CSS value, or uploaded image.

## Troubleshooting

| Issue | Check |
|---|---|
| Old behavior after update | Restart if necessary; hard-refresh with `Ctrl+Shift+R` or `Cmd+Shift+R` |
| D&D Beyond suggestion unavailable | Check canonical species spelling, configuration, and outbound connectivity |
| Dice expression rejected | Check syntax and leave HP Range end blank |
| Initiative absent from Client card | Enter a numeric initiative, then enable **Init on** |
| Remote image absent | Lookup is best effort; upload an image manually |
| Monster changes disappear | Save an unsaved encounter before loading/switching setup |
| CSV import fails | Check UTF-8, headers, numeric fields, and duplicate IDs |

## Backups

Back up all of `storage_dir`: `campaigns.json`, `characters/`, `setups/`, `state.json`, and `uploads/`.
