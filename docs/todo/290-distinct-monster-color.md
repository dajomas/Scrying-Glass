# 290 - Distinct default monster color

[Back to TODO index](../../TODO.md)

## Task and status

SG-TODO-029 - proposed, requested by the user 2026-11-20. No owner, priority or
deadline has been agreed.

## Request

When adding a monster, the default color is a distinct color that is not yet used by
any monster in the current battle setup.

## Current behaviour (code at `c055cf1`)

- The Add Monster form (`templates/admin/060_monster_input.html`) and the
  Import .monster form start with the fixed color `#842029`; the color preview is
  installed in `static/admin/080-source.js`.
- The server falls back to `#842029` for monsters without a color
  (`python/scrying_glass_service_state.py`, CSV import in
  `python/scrying_glass_monster_csv.py`).
- Nothing compares the default with the colors already in the battle setup.

## Open decisions (to agree before implementation)

1. Which forms: Add Monster only, or also Import .monster (and CSV rows without a color).
2. When the default is chosen: when the form opens, after every add (so the next monster
   gets the next free color), and when the battle setup changes (load, remove, edit).
3. A color the user picked by hand stays as it is (proposed: yes, until the form is reset).
4. The palette: a fixed list of clearly different colors that stay readable on the
   Admin, Client Display and statblock tile backgrounds, and what happens when all are in
   use (proposed: the least used color, or a generated one far from those in use).
5. Whether "distinct" also considers the character colors.

## Acceptance criteria (proposed)

- A new monster's default color is not used by any monster in the current battle setup
  while palette colors are free.
- Adding several monsters in a row gives each add a different default.
- A hand-picked color is never replaced.
- Colors meet the existing contrast expectations on every display.

## Validation requirements

Unit tests for the color choice (empty setup, partly and fully used palette, hand-picked
color, quantity adds); Admin browser tests for the form default after load, add and
reset. Changes to code or tests run CI normally.
