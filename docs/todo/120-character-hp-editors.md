# 120. Character HP editor consistency

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-012
- Status: proposed
- Recorded: 2026-11-06
- Priority: not assigned.
- Dependencies: none established; coordinate with SG-TODO-009 Admin usability work.

## Requested change

Make the Current/Max HP edit boxes in the Characters pane the same as the HP column in the Monsters pane.

## Acceptance criteria

- Character Current HP and Max HP editors match the corresponding Monsters HP presentation and editor styling.
- Both values remain editable with existing save and validation behavior preserved.
- The change does not alter HP calculation, damage, healing or persistence semantics.

## Validation required

Compare both panes in the browser, edit and save character Current/Max HP, and verify persistence after reload. Add or update relevant UI regression coverage during implementation.

## Delivery status

Backlog entry only. Implementation and validation have not been performed for this task.
