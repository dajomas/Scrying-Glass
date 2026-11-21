# 290 - Distinct default monster color

[Back to TODO index](../../TODO.md)

## Task and status

SG-TODO-029 - implemented 2026-11-21 on `features/claude` ([handover 670](../handover/670-group-1-quick-wins.md)); CI and user check pending. Agreed for implementation group 1 (2026-11-21), originally requested by the user 2026-11-20. No owner, priority or
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

## Decisions (user, 2026-11-21)

1. Forms: Add Monster, Import .monster **and** CSV rows without a color (each such CSV
   row gets the next free color; copies from one row share it).
2. Palette: a curated list of 12 clearly different colors, readable with white text and
   on the dark displays; the first unused one is the default.
3. When all 12 are in use: the palette color used by the fewest monsters.
4. Only monsters in the current battle setup count (not characters).
5. Timing: the default is recalculated when the page loads, after every add and when the
   battle setup changes (load, remove, edit); a color picked by hand is kept until the
   form is reset.

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
