# Scrying Glass User Guide

Scrying Glass lets a GM manage encounters on the Admin page while players view a live Client Display.

## Start

```bash
python3.14 scrying_glass_server.py --config config.yaml
```

| Screen | Address |
|---|---|
| Admin | `http://SERVER:3000/` |
| Client Display | `http://SERVER:4000/` or `http://SERVER:4000/display` |

## Campaigns and battle setups

Campaigns own character rosters and group saved battle setups. Create/load/save setups from the Battle setups pane. Loading another setup or switching campaign can replace working encounter data.

### Automatic saving

- Character additions, edits, HP changes, resets, bulk actions, and removal save automatically to the active campaign.
- Monster additions, edits, HP changes, resets, bulk actions, and removal save automatically to the loaded battle setup.
- If no saved setup is loaded, monster changes remain in the unsaved working encounter until you use **Save**.

## Add monster manually

| Field | Meaning |
|---|---|
| Name | Local encounter name, such as `Mimic 1` |
| Monster species | Canonical creature name for lookup, such as `Mimic` |
| AC | Armor Class |
| HP Range start | Fixed HP, range start, or dice expression |
| HP Range end | Numeric range end; blank for fixed HP or dice |
| Quantity | 1–50 copies |
| Image | Optional uploaded image |

### HP options

| HP Range start | HP Range end | Result |
|---|---|---|
| `17` | blank | Fixed 17 HP |
| `10` | `20` | Independent 10–20 HP per copy |
| `3d8+9` | blank | Independent `3d8+9` roll per copy |

Dice examples:

```text
1d8
2d10+4
3d8 + 9
1d20
1d100-10
```

Spaces around `+` or `-` are optional. Leave HP Range end empty for dice. The resulting HP becomes current, maximum, and reset HP.

### D&D Beyond AC and HP suggestions

After entering Monster species, Scrying Glass can look up an exact D&D Beyond monster match. It tries an available Legacy-marked result before a current result. If a stat block supplies both an average and dice HP, dice HP is preferred.

For example, a source value of `58 (9d8 + 18)` fills HP Range start with:

```text
9d8+18
```

and leaves HP Range end empty.

Suggestions use the Add monster notification area. They fill only blank AC/HP fields by default. Enable **Overwrite Armor Class and HP Range with found D&D Beyond values** before lookup when you want found values to replace values already in the form.

Lookup is optional. If no exact usable result is found, enter AC and HP manually and create the monster normally.

### Monster images and editing

A manually uploaded image overrides remote lookup. Without one, Scrying Glass may retrieve the dedicated D&D Beyond monster image using Monster species.

Click **Edit** on a Monster row to alter its fields. The current image appears as a thumbnail no larger than 300px in either dimension. Choose a file in **Replace image** to preview it immediately; it is saved only after **Save monster**. Canceling leaves the existing image intact.

## Initiative display

To show initiative on a Monster card:

1. Enter a numeric initiative in the Monster row and commit it by leaving the field.
2. Enable **Init on** for that Monster.
3. Ensure the Monster is active and alive so it has a Client card during battle.

**Init on** only authorizes display. It cannot show a blank initiative value. AC, HP, and initiative displays are independent controls.

## Imports

Monster CSV requires:

```text
name,monster_species,ac,hp
```

Character CSV requires:

```text
name
```

Compatible `.monster` files use `name`, `type`, HP (`hpText` or `hp`), and AC (`ac`, `armorClass`, `otherArmorDesc`, or `natArmorBonus`).

## Battle

1. Set initiative for combatants.
2. Join living participants to battle.
3. Start battle and resolve ties.
4. Use **Next** to advance turns.
5. Click the underlined current combatant in battle order to apply Damage, Heal, Buff, or Debuff.

## Troubleshooting

| Issue | Check |
|---|---|
| Suggestion unavailable | Check outbound connectivity, lookup configuration, and canonical Monster species spelling |
| Dice HP rejected | Check syntax and leave HP Range end blank |
| Initiative absent from Client card | Enter a numeric initiative, then enable **Init on** |
| Browser uses old behavior | Restart if needed and hard-refresh with `Ctrl+Shift+R` or `Cmd+Shift+R` |
| Monster changes disappear | Save an intentionally unsaved encounter before loading/switching setup |
| Remote image missing | Lookup is best effort; upload an image manually |

## Backups

Back up all of `storage_dir`, including `campaigns.json`, `characters/`, `setups/`, `state.json`, and `uploads/`.
