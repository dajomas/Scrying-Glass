# 096 - Stage 1 campaign-operation feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 Stage 1 Step 1 - 2026-11-12

Status: 1A-1D.2a implementations published; final 1D.2b implementation archive
prepared. Base: c729cf5d7a7bcc4d37b7a6e26f7fb82a1ffaa26a. Publication, normal push CI review,
covering integrated validation and bounded acceptance are pending, not inferred
from preparation. No new commit/push or CI result is claimed.
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

Remaining under the EXISTING sequence:
- Apply/review/commit/push final archive with the supplied message containing no
  skip marker; inspect actual CI results and their tested revision/attempt.
- Review other agreed integrated evidence and obtain bounded campaign acceptance.
- Continue remaining Stage 1 steps and wider project plan. Do not mark Stage 1,
  Deliverable 1, 009.7 or 009 completed based on this archive or push alone.

The unchanged branch workflow runs normal push CI and discovers new Node/Python
suites. No workflow edit/dispatch. Full-suite/hosted CI, authenticated live-server,
human visual and screen-reader acceptance remain unclaimed. Prior accepted Stage 2,
4A.1-4A.13 and 009.1-009.6 stay closed. Stage 1, Stages 3-4, Deliverable 1 acceptance,
Deliverable 2 and 009.7/009 remain open; cleanup stays deferred until after 009.
