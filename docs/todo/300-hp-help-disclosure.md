# 300 - HP field help in a folded block

[Back to TODO index](../../TODO.md)

## Task and status

SG-TODO-030 - implemented 2026-11-21 on `features/claude` ([handover 670](../handover/670-group-1-quick-wins.md)); CI and user check pending. Agreed for implementation group 1 (2026-11-21), originally requested by the user 2026-11-20. No owner, priority or
deadline has been agreed.

## Request

Move the explanation of the HP fields in Add Monster to a folded-up help block at the
bottom of the Combat statistics section.

## Current behaviour (code at `2e492b6`)

- The explanation (`#monsterHpRangeHelp`, a paragraph with a list: fixed value, numeric
  range, dice expression) is always visible at the top of the Add Monster panel
  (`templates/admin/060_monster_input.html`), above the form.
- The HP Range start and end fields refer to it with `aria-describedby`.
- `static/admin-panel-forms.js` builds the Combat statistics group (AC, HP Range start
  and end, initiative bonus, quantity); the initiative bonus has its own help
  (`#monsterInitiativeBonusHelp`).

## Acceptance criteria (proposed)

- The HP explanation sits in a closed disclosure (`details`/`summary`, for example
  "HP field help") as the last item of the Combat statistics group, and opens and closes
  with mouse and keyboard.
- The text is unchanged; the HP fields keep their accessible description.
- Nothing else in the panel moves; narrow layouts stay usable.

## Validation requirements

Admin browser test for the position, closed default, toggling and `aria-describedby`;
existing Add Monster form tests unchanged. Changes to code or tests run CI normally.
