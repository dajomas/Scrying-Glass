# 320 - Clear selection next to Select all in the rosters

[Back to history index](../../HISTORY.md)

## Task and status

SG-TODO-032 - implemented 2026-11-21 on `features/claude` ([handover 670](../handover/670-group-1-quick-wins.md)); completed and closed 2026-11-21 after CI 44888887657 and e2e 20261121T150318Z. Agreed for implementation group 1 (2026-11-21), originally requested by the user 2026-11-20. No owner, priority or
deadline has been agreed.

## Request

In both the Characters and the Monsters display, move the **Clear selection** button to
the right of the **Select all** button.

## Current behaviour (code at `2e492b6`)

- Each roster toolbar (`.bulk-action-toolbar`, `templates/admin/070_character_display.html`
  and `080_monster_display.html`) holds Select all and the Bulk dropdown.
- `static/admin-rosters.js` adds the selected count at the start and appends Clear
  selection at the end, after the Bulk dropdown.

## Acceptance criteria (proposed)

- Order in both rosters: selected count, Select all, Clear selection, Bulk dropdown.
- Clear selection keeps its behaviour (disabled with nothing selected, focus returns to
  Select all) and the toolbar still wraps cleanly at narrow widths.

## Validation requirements

Admin browser test of the order and behaviour in both rosters; existing roster tests
unchanged. Changes to code or tests run CI normally.
