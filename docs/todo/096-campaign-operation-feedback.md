# 096 - Stage 1 campaign-operation feedback

[Back to TODO index](../../TODO.md)

## SG-TODO-009.7 Stage 1 Step 1 - accepted close-out, 2026-11-12

Status: completed and closed for the agreed campaign create/edit/switch/delete
scope (1A-1D). Following successful covering CI, the user explicitly requested
"Accept Stage 1 Step 1 now" on 2026-11-12. No campaign Step 1 implementation,
covering-CI correction or bounded acceptance action remains open.

Final tested revision: 4f0127b56550cacb821ae2c62cb2057265eaea2a; successful Branch
tests 43237771405 attempt 1, job 131249677511. Evidence publication:
ce05279711f29915b5f43132ff1078c3933fb4cf. Run/job metadata match the revision and
show all configured test stages succeeded. Earlier 1D.2b runtime implementation:
742697d86a76a657c92653dd6f1533135399f4b0. Failed run 43234426795 attempt 1 and the
subsequent asset-version assertion correction remain historical, not open blockers.

[Detailed accepted scope/evidence/limits](../handover/520-campaign-operation-feedback.md)
and [parent plan](097-feedback-delivery-plan.md). Full earlier criteria, delivery
history and preparation evidence remain in the
[pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/ce05279711f29915b5f43132ff1078c3933fb4cf/docs/todo/096-campaign-operation-feedback.md).
Earlier pending-publication/CI/acceptance wording is superseded for Step 1 only.

Accepted behavior preserves persistent independent errors, matching resolution,
three-second pane success, mutation/refresh distinction, context/session/revision/
registry/timer guards, busy restoration, original APIs/auth/confirmations/setup
options and drafts/selections, with no automatic mutation replay. The intermediate
1A/1B/1C/1D splits are delivery history, not new scope or future acceptance gates.

Acceptance is bounded to the stated automated/fixture evidence; it does not claim
unperformed human visual/manual, live-server, screen-reader or exhaustive
accessibility checks. Stage 1 as a whole is not closed.

Remaining work belongs to existing Stage 1 setup/background migration and wider
Stages 3-4, Deliverable 1 acceptance, Deliverable 2 and 009.7/009. Stage 2, accepted
4A.1-4A.13 and 009.1-009.6 remain closed. Do not reopen campaign Step 1 because of
historical pending notes. No new scope, owner/deadline or gate is added. Test-suite
cleanup stays deferred until after 009; source-selection/Open5e are not prerequisites.

This close-out is documentation only with [skip ci]. It runs no new tests, changes
no application/tests/templates/pins/workflows, and dispatches no workflow. It does
not invent a new CI run, merge, deployment or blanket future-write approval.
