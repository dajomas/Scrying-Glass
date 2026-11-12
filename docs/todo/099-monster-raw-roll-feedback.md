# 099 - SG-TODO-009.7 Stage 2 raw-roll feedback

[Back to TODO index](../../TODO.md)

## Step 1 - 2026-11-11

Status: in progress; implementation and regression tests prepared, covering
validation and acceptance pending. Scope is only the effective monster-row
raw-roll handler. [Implementation and preparation evidence](../handover/490-monster-raw-roll-feedback.md).

Acceptance: persistent operation/target-owned validation and request errors,
matching recovery with unrelated notices retained, duplicate prevention through
refresh, stale/superseded-result suppression, unchanged raw-roll transport and
server arithmetic, and separate mutation-success/refresh-failure reporting without
a success notice or automatic replay. The focused controller-backed suite covers
these boundaries; actual browser/full-suite/covering CI review remains required.

Remaining: review normal covering CI and native-browser regressions, correct any
failures with fresh approval, and obtain bounded acceptance. Do not mark completed
merely because a commit is pushed. Stage 2, Stage 1, both deliverables and 009.7
stay open. Monster Edit, roll-all, select-dead, bulk Join pane success, compatibility
retirement and phase close-out remain separate work. Accepted Join reporting and
combat/authorization rules are unchanged. No priority, owner or deadline changes.

## Step 1 local validation reconciled - 2026-11-11

Implementation 162a3892ef330c62961b05409d07916af7d8b4e6 has a green completed
local all-suite publication 50e3123ccec5d8cae2db727271a0ba8c434f3a52,
run-20261111T203731Z-cNHOP5. This supersedes the historical pending-local-validation
wording above, not wider acceptance boundaries or unreviewed GitHub Actions status.
[Evidence scope and review limits](../handover/490-monster-raw-roll-feedback.md#step-1-local-covering-evidence---2026-11-11).
The user requested proceeding to Step 2 when green; Stage 2 remains in progress.

## Related Step 2 - monster Edit - 2026-11-11

Status: in progress; implementation, reconciled native fixture and focused
production-controller tests prepared. Syntax/compilation checks passed; Step 2
runtime/browser/full-suite covering validation and acceptance remain pending.
Acceptance: preserve FormData, bonus/image behavior and character delegation;
persistent monster Edit-specific errors/matching recovery; independent targets;
duplicate prevention through refresh; encounter/session/supersession safety;
owned cleanup; separate saved/refresh-failed guidance, no replay or success notice.
[Implementation and pending checks](../handover/490-monster-raw-roll-feedback.md#related-step-2-monster-edit-checkpoint---2026-11-11).
Review normal covering results and correct failures with fresh approval before
bounded acceptance. Do not apply Step 1's green run to Step 2 or close Stage 2,
Stage 1, either deliverable or 009.7. Roll-all, select-dead, bulk Join pane success,
compatibility retirement and phase close-out remain separate unfinished work.

## Step 2 composition fixture correction - 2026-11-12

Status: in progress; fixture correction drafted, validation pending.
Expose openEdit in the shared character Edit VM harness without weakening
the retained delegation and monster FormData assertions.

Acceptance: both previously failing composition tests pass, the monster
Edit feedback suite remains green, and the complete configured JavaScript
step passes on the corrective revision. Review the full covering CI result
before bounded acceptance; do not close Stage 2 or 009.7.

[Diagnosis and correction](../handover/490-monster-raw-roll-feedback.md#step-2-composition-fixture-correction---2026-11-12).
