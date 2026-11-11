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
