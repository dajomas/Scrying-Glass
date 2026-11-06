# 120. Character HP editor consistency

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-012
- Status: completed; closed at the user's explicit request after covering local/CI verification and visual/workflow acceptance, 2026-11-06.
- Updated: 2026-11-06
- Priority: not assigned.
- Dependencies: coordinated with completed SG-TODO-009.4 as the second of two approved increments.
- Implementation: `90dcfab919556ac94d05c44c0ec0e775fab32f9d`; subsequent Turn-control UI removal: `d91f73bfe121870296a1df79f58c58c21bcaeb59`.

## Agreed change

Option 2: show read-only character current/max HP like the Monsters roster, with both values editable through the existing row Edit dialog. Retain compact inline initiative, other row actions, HP rules, APIs, validation and persistence. SG-TODO-013 keyboard navigation and later Admin phases are not included.

## Implementation and acceptance

The loaded character-hp-display enhancement replaces only the rendered character HP cell inputs with current/max text, initially and after direct roster table replacement. Existing Edit and save handlers remain authoritative; no fetch or replacement save implementation is introduced. The assembled Admin core and tracked failure marker remain untouched. See [delivery, evidence and close-out](../handover/310-admin-rosters.md).

The user explicitly accepted the desktop/narrow roster presentation, selection/bulk workflows, character HP editing through Edit with values retained after reload, and absence of Turn in both roster UIs, then requested closure of 009.4 and 012 on 2026-11-06. This records user visual/workflow acceptance, not an assistant-executed authenticated-server or exhaustive accessibility/combat audit.

## Verified validation and close-out

CI run 42276181187 attempt 1, Branch tests, covered d91f73bfe121870296a1df79f58c58c21bcaeb59. Evidence publication: 386beabbcd6e39378014d4a86df24dd4d68f5b75, folder ci-results-42276181187-attempt-1. Workflow/job/configured steps succeeded; main unittest and repeated connection audit each report 1,066 tests OK; pytest reports 43 passes; audit reports 681 connections/zero without explicit close. The asset contract and Edit rejection/retry/reload methods explicitly passed, as did roster and Turn-removal regressions. Eighteen fixture images were uploaded, including desktop/narrow rosters; upload is not assistant visual inspection.

Local suite=all tested 386beabbcd6e39378014d4a86df24dd4d68f5b75, evidence 423ab05f08b4ec9f8d5e7c30d1bf600ea07ffb63 under local-tests-386beab/run-20261106T191207Z-NSLlFY. completed=1; overall and all 48 command exits zero; pytest 43 passed; complete connection-audit log reports 1,066 tests OK and 681/0 connections. The main unittest command exits zero; the local test count is taken from the complete audit log.

Earlier preparation passed node syntax, regression AST and a simplified Chromium fixture for zero/large HP, zero maximum, replacement/idempotence and retained initiative/Edit. The later covering results supersede its pending-full-suite status. Browser reload tests use mock-backed HTTP state, not database persistence evidence; the user supplied workflow acceptance. Earlier 720f876 evidence predates the HP increment and is not its closure evidence.

This close-out changes documentation only, executes no new tests and leaves application/tests/workflows unchanged. Commit message includes [skip ci]; no separate workflow is dispatched or new outcome inferred. No agreed 012 implementation work remains.
