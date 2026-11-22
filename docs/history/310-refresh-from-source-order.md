# 310 - Refresh from source above Remove in the Monster bulk actions

[Back to history index](../../HISTORY.md)

## Task and status

SG-TODO-031 - implemented 2026-11-21 on `features/claude` ([handover 670](../handover/670-group-1-quick-wins.md)); completed and closed 2026-11-21 after CI 44888887657 and e2e 20261121T150318Z. Agreed for implementation group 1 (2026-11-21), originally requested by the user 2026-11-20. No owner, priority or
deadline has been agreed.

## Request

In the Monster bulk "Choose action" dropdown, move **Refresh from source** above
**Remove**.

## Current behaviour (code at `2e492b6`)

- The dropdown (`#monsterBulkAction`, `templates/admin/080_monster_display.html`) ends
  with Reset and Remove.
- `static/monster-refresh-review.js` appends "Refresh from source" at the end, below
  Remove. `static/monster-statblock-bulk.js` already inserts "Load statblocks" before
  Remove.

## Acceptance criteria (proposed)

- Remove is the last action; Refresh from source comes directly before it (after Load
  statblocks, unless agreed otherwise), whatever order the scripts load in.
- The action itself, its enabled/disabled state and its feedback are unchanged.

## Validation requirements

Admin browser test of the option order; existing refresh-review tests unchanged.
Changes to code or tests run CI normally.
