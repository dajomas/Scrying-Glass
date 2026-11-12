# 520 - Stage 1 campaign-operation feedback

[Back to handover index](../../HANDOVER.md)

## Stage 1 Step 1 bounded close-out - 2026-11-12

Completed and closed for the agreed campaign-operation scope. After the verified
green covering CI run, the user explicitly requested "Accept Stage 1 Step 1 now"
on 2026-11-12. This records acceptance of campaign create, edit, switch and delete
(1A-1D, including the 1C/1D delivery splits), not all of Stage 1 or 009.7.

### Delivered scope

Explicit operation/target/scope identities; persistent actionable validation and
request errors with matching resolution; three-second pane successes; completed
mutation versus failed refresh; obsolete result/timer, dialog/session/revision,
registry and expected-transition guards; busy protection through refresh and no
automatic mutation replay. Existing payloads, endpoints, permissions, confirmations,
setup-opening and move/delete-setup options, drafts and selections are preserved.
Optional state/helper ownership and wrapper forwarding preserve other callers'
default behavior. Eight-fragment assembly, size/digest pins and marker remain.

### Covering evidence and correction history

- Final 1D.2b implementation: 742697d86a76a657c92653dd6f1533135399f4b0.
- Final tested assertion correction: 4f0127b56550cacb821ae2c62cb2057265eaea2a.
- Successful Branch tests run: 43237771405, attempt 1; job 131249677511.
- Evidence publication: ce05279711f29915b5f43132ff1078c3933fb4cf.
- Reviewed run/job metadata match the tested SHA and success. Provisioning,
  syntax/import, Python/browser suite, pytest, JavaScript and standalone browser/
  audit stages all succeeded. This is not a claim of individual re-review of every
  test or screenshot.
- Run 43234426795 attempt 1 remains a historical failure for the stale shared-v2
  asset assertion; publication 332cbf05b9903f4b718fe223dca7e5a724497496 preserves it.
  The correction expects candidate selection v3 and refresh review v2 while retaining
  exact-once, obsolete-version, order and bounded-asset checks.

Full prior implementation identities, scoped preparation tests/negative controls,
failed-run diagnosis and limits remain in the
[pre-close-out record](https://github.com/dajomas/Scrying-Glass/blob/ce05279711f29915b5f43132ff1078c3933fb4cf/docs/handover/520-campaign-operation-feedback.md).
Earlier archive-prepared, publication-pending and acceptance-pending wording is
historical and superseded for campaign Step 1 only.

### Acceptance boundary and continuation

The user's bounded sign-off closes campaign Step 1 on the stated automated/
fixture evidence. It does not fabricate authenticated live-server, human visual/
manual workflow, screen-reader or exhaustive accessibility checks. No additional
campaign gate is invented after acceptance. [Task close-out](../todo/096-campaign-operation-feedback.md).

Remaining Stage 1 setup/background work, Stages 3-4, both whole feedback deliverables,
009.7 and overall 009 remain open. Accepted Stage 2, 4A.1-4A.13 and 009.1-009.6 stay
closed. Test-suite cleanup stays deferred until after 009; unrelated source-selection/
Open5e backlog is not a prerequisite. Continue remaining setup-operation feedback
without reopening campaigns or silently expanding scope.

This close-out changes documentation only, runs no new tests and uses [skip ci].
No application, test, template, pin or workflow changes; no workflow dispatch, merge
or deployment. Root indexes are reconciled; README behavior remains accurate.
