# 130. Initiative keyboard navigation

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-013
- Status: proposed
- Recorded: 2026-11-06
- Priority: not assigned.
- Dependencies: none established; coordinate with SG-TODO-009 Admin usability work.

## Requested change

When focus is in an initiative edit box in the Characters or Monsters panel, Tab moves to the next initiative edit box and Shift+Tab moves to the previous initiative edit box.

## Acceptance criteria

- Forward and reverse keyboard navigation work for initiative editors in both panels.
- Navigation between initiative editors skips unrelated controls.
- Existing initiative validation, saving and combat ordering remain intact.
- Define and document first/last-field behavior and whether traversal crosses panel boundaries before implementation; these details were not specified in the request.

## Validation required

Add keyboard regression coverage for forward and reverse navigation in both panels. Manually verify focus movement, initiative editing and saving, including boundary behavior and any rerender caused by an edit.

## Delivery status

Backlog entry only. Implementation and validation have not been performed for this task.
