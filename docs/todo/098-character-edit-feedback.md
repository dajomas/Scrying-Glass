# 098 - Stage 2 character Edit feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 - Current checkpoint status - 2026-11-11

Status: in progress; neither Stage 2, either feedback deliverable nor 009.7 is
closed. No changed priority, owner, deadline or blanket future write approval.
4A.1-4A.13 remain closed only for their accepted scopes.

This task prose consolidates stale prepared/pending notes. Historical delivery,
failed-run identities, focused test counts, corrections and evidence limits are
preserved in the [Stage 2 handover](../handover/480-character-edit-feedback.md),
not silently accepted or removed from the backlog.

- Character Edit: fd13991c2c15cb6e15f056f0050431f5bc686ada plus composition correction
  7e49938c8064b7c70526583a2d4bfac358150cce has verified successful covering run
  43067755682 attempt 1; bounded acceptance remains separate.
- Entry forms (character/monster creation and .monster import): implementation
  37137b6367172549ffc7028b44af64e0e6534d75 plus lookup-focus correction
  8841bf0b99d3e48352f3f785819b759b4e180624 has verified successful covering run
  43082738853 attempt 1. This does not certify unperformed native/live/manual checks.
- CSV/setup import: complete 040 integration and ten grouped production-controller
  cases prepared and passed locally; exact approval/delivery, covering repository
  validation/corrections and bounded acceptance remain pending. Runtime import
  owners/bindings are replaced in 040; inactive older 030 source is not retired.
  [Integration, pin identity and limits](../handover/030-validation-and-next-steps.md#stage-2-modal-import-integration---2026-11-11).

## Preservation and remaining gates

Preserve JSON/FormData, HP/dice/bonus/source-token values, selected files, drafts,
server authorization/validation and accepted Join ownership. Require persistent
independent validation/request errors, matching recovery, 3s pane successes,
separate no-replay refresh errors, duplicate protection and stale session/scope
isolation. Newer files/options must not be discarded after an older import.

Remaining: native File/FormData/events/focus and loaded-Admin regression for new
paths; retained source/reader/runner/tamper/full suites; review equivalent covering
local or hosted evidence and correct failures; bounded acceptance with any
unperformed live/manual/accessibility checks stated rather than invented. Both
local and hosted success are not required; evidence counts for its revision/scope,
not future changes. Existing CI discovers the Node tests and retained browser
suites; focused mocked checks alone are not native browser acceptance.

Still unfinished: monster initiative/raw-roll/Edit/roll-all, select-dead, bulk
Join pane success, final Stage 2 fixture/caller/identity reconciliation and
acceptance. Inactive-source retirement and pane compatibility remain separate
later gates; do not retire compatibility prematurely. Stage 1, Stages 3-4,
Deliverable 2 and wider phase acceptance remain separate under the
[approved plan](097-feedback-delivery-plan.md). No merge/deployment.

## Select-dead - 2026-11-12

SG-TODO-009.7-S2-SELECT-DEAD. Status: in progress; implementation, retained fixture
reconciliation, 12 new regressions and cache-reference/documentation updates prepared.
Acceptance: unchanged death rules, selection sets/checkboxes and non-selection
delegation; original count text, explicit roster-specific pane success, 3s expiry,
matching recovery/unrelated-error retention and scope/timer safety. No network,
server mutation, refresh, Join-reporting or combat-rule changes.

Preparation: combined Node run passed 13 tests (12 new cases plus the retained
regression file), zero failures/cancellations/skips; three negative controls detected
regressions and restored execution passed. Syntax and exact source-preservation/
base-identity checks passed. [Implementation and evidence limits](../handover/500-select-dead-feedback.md).

Roll-all is already delivered as ed6a211382d60110ecd008b19c4b88db46bd2bd3;
raw-roll/Edit and prior imports are not restarted by this step. Historical pending
paragraphs above do not reverse later deliveries. Bulk Join pane success and final
Stage 2 reconciliation/acceptance remain separate next work. Keep other stages,
Deliverable 2, compatibility retirement and deferred test cleanup outside this scope.

Use [skip ci] for this intermediate Stage 2 push as requested on 2026-11-12; no
workflow edit or separate dispatch. Combined covering/native-browser validation
and bounded acceptance remain pending until the Stage 2 batch is pushed and tested.
Do not mark Stage 2 or 009.7 completed merely because this candidate is committed.
