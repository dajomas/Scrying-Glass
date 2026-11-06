# 120. Character HP editor consistency

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-012
- Status: in progress; option 2 implementation included, covering local/CI validation and user acceptance pending.
- Updated: 2026-11-06
- Priority: not assigned.
- Dependencies: coordinated with SG-TODO-009.4 as the second of two approved increments.

## Agreed change

Option 2: show read-only character current/max HP like the Monsters roster, with both values editable through the existing row Edit dialog. Retain compact inline initiative, existing row actions, HP rules, APIs, validation and persistence. SG-TODO-013 keyboard navigation and later Admin phases are not included.

## Implementation and acceptance

The loaded character-hp-display enhancement replaces only the rendered character HP cell inputs with current/max text, initially and after direct roster table replacement. Existing Edit and save handlers remain authoritative; no fetch or replacement save implementation is introduced. The assembled Admin core and tracked failure marker remain untouched. See [delivery and validation record](../handover/310-admin-rosters.md).

Before closure, verify desktop/narrow read-only HP, keyboard access to Edit, both values editable, successful save and reload, rejected/invalid save and retry, and unchanged initiative/selection/bulk/damage/healing workflows. Confirm actual stored persistence on a copied live installation; intercepted-HTTP fixtures are not database persistence evidence.

## Validation status

Preparation passed node syntax and regression Python AST parsing. A simplified Chromium fixture passed zero/large HP, zero maximum, roster replacement, duplicate installation, unchanged initiative/dialog fields and retained Edit click with no page errors. Full-Admin tests are prepared under existing CI discovery, including rejection/retry/native validation/save/reload at 1440 and 375 pixels, but have not been executed during preparation. Covering CI, fresh fixture screenshot review and user workflow acceptance remain pending. The earlier successful local evidence for 720f876 predates this increment and does not validate it.
