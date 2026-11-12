# 096 - Stage 1 campaign-operation feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 Stage 1 Step 1 - 2026-11-12

Status: 1D.2b published at 742697d86a76a657c92653dd6f1533135399f4b0. Covering
Branch tests 43234426795 attempt 1 failed on a stale asset-version assertion.
The targeted assertion correction is prepared; corrective push CI review, covering
validation and bounded acceptance remain pending.
[Parent plan](097-feedback-delivery-plan.md) and
[current evidence/limits](../handover/520-campaign-operation-feedback.md).
Prior full criteria/history remain in the
[pre-1D.2b task record](https://github.com/dajomas/Scrying-Glass/blob/c729cf5d7a7bcc4d37b7a6e26f7fb82a1ffaa26a/docs/todo/096-campaign-operation-feedback.md).

Agreed campaign Step 1 implementation preparation is complete across 1A create,
1B edit, 1C switch and 1D delete. The earlier 1D.1/1D.2a splits are retained as
published checkpoints, not additional requirements. This final 1D.2b delivers
explicit three-second deletion success, persistent completed-deletion/failed-
refresh feedback with reload/no-replay guidance, strict error propagation, guarded
setup/state observation/rendering and focused integration/regressions.

Preserve existing dialog/session/input/registry/scope/epoch identities, matching
resolution, unrelated/newer feedback, obsolete-result/timer guards and busy-state
restoration. Preserve options, confirmations, endpoints, queries/payloads, auth,
selection/drafts/files and setup-opening semantics. No mutation replay, new deletion
rule, dialog redesign, Deliverable 2 near-field/connection/polling work or suite audit.
Optional helper/transport/state-loader ownership callbacks default to old behavior;
wrapper forwarding/cache bumps are necessary scoped integration, not reopened Stage 2.

Executed locally on prepared revision: 115 scoped Node tests, 11 full-Admin Chromium
scenarios, four source/identity/assembly/pin/tamper/syntax checks and four detected
negative controls. All restored checks pass; see 520/logs for exact counts and
coverage limits. The missing fixture functions were an incorrect direct invocation;
assembled-runner core/next/Apply checks now pass. No marker/fixture workaround.

## CI assertion correction - 2026-11-12

Evidence publication: 332cbf05b9903f4b718fe223dca7e5a724497496. The Python suite
reports 1 failure among 1,552 tests; the audit repeats the same stale assertion.
JavaScript and pytest stages passed. Correct only the test expectations: candidate
selection v3, refresh review v2; retain exact-once, obsolete-version and order checks.
Local targeted suite: 3 passes; four wrong-version/duplicate negative controls were
detected and the restored suite passes. No runtime downgrade or workflow edit.
A new normal push CI result is required and not yet claimed; scope acceptance stays
pending. Earlier preparation counts above remain scoped historical evidence.

Remaining under the EXISTING sequence:
- Push the assertion correction without a skip marker; review its actual covering
  CI result, exact tested revision and workflow attempt. No separate dispatch.
- Review other agreed integrated evidence and obtain bounded campaign acceptance.
- Continue remaining Stage 1 steps and wider project plan. Do not mark Stage 1,
  Deliverable 1, 009.7 or 009 completed based on this archive or push alone.

The unchanged branch workflow runs normal push CI and discovers new Node/Python
suites. No workflow edit/dispatch. Full-suite/hosted CI, authenticated live-server,
human visual and screen-reader acceptance remain unclaimed. Prior accepted Stage 2,
4A.1-4A.13 and 009.1-009.6 stay closed. Stage 1, Stages 3-4, Deliverable 1 acceptance,
Deliverable 2 and 009.7/009 remain open; cleanup stays deferred until after 009.
