# 450 - Join reporting

[Back to handover index](../../HANDOVER.md)

Current status: completed and closed for the accepted bounded 4A.12 scope on
2026-11-11. The close-out below supersedes historical pending-status notes,
not preparation limits or wider deliverable/phase gates.

## 4A.12 implementation - 2026-11-11

This change set supplies bounded Join reporting on features/perplexity-009.7.
Baseline: e633ca34d7dd651594470f7f6e64a3f9a3742da9. Covering CI and explicit
bounded acceptance remain pending; no implementation SHA or run is invented.

The existing fetch gate reports a failed Join globally, while the original core
patch/runBulkAction catches also report it in a pane. The updated gate installs
Join-only core wrappers after deferred scripts at DOMContentLoaded (or immediately
when injected after document completion). Non-Join operations delegate unchanged.
A private Symbol on RequestInit carries reporting ownership, not JSON/API data;
the owned core path uses request() formatting and publishes one roster.join error.
Standalone fetch keeps its existing rejection/response-clone behavior. Installation
is idempotent. Missing core functions in a partial fixture leave standalone reporting.

Single keys remain [kind,id]; bulk keys use sorted string IDs, independent of the
original request ID ordering. Matching success silently resolves only that key;
other combatants/operations remain untouched. Scope/supersession checks prevent
stale outcomes from publishing or starting success-side UI/refresh. Existing bulk
success wording/destination is retained. Refresh is outside the mutation catch;
production load() owns refresh failures. There is no automatic retry/replay.

The captured-click initiative guard, numeric/zero/negative and leave behavior,
server gates/rollback, methods/headers/URLs/JSON, selection behavior and unrelated
core functions are unchanged. No core-fragment, pin, marker, markup, workflow,
shared-fixture or server edit. Near-field association belongs to Deliverable 2.

## Executed preparation and limits

Prior preparation verified the original gate Git blob
39e08dfe3804308acfcf7e97b5b4efe425a28ef3, legacy test blob
2c4fcec949cba4caa0dc4980087e01a9207e667f and production controller blob
c4a82d73b21f4657da651ce45f76003c3348a6ef. Runtime draft: 6,636 UTF-8 bytes;
node --check passed. New suite: 26 passes; retained gate suite: 12 passes;
restored combined run: 38 passes, zero failures/skips. Four negative controls were
detected: omitted core binding, broken owner marker, omitted stale-success guard,
omitted matching resolution. Runtime was restored before the combined pass.
The legacy fixture only accommodates/fires the new lifecycle callback; all original
behavioral assertions remain. This delivery reuses those preparation results;
no fresh full-checkout test execution is claimed during payload preparation.

Focused checks used the real production controller, a scoped test adapter,
production core function text copied from verified reads, and mock DOM/transport.
They did not run the real Admin bootstrap, assembled eight-fragment bundle,
browser, authenticated live server or human accessibility checks. CI will read
actual unchanged core function boundaries from 010-source.js; local focused
materialization is not a full checkout. Header asset order, core/gate, server
initiative gates/tests and configured CI were reviewed, not behaviorally rerun.

## Delivery and remaining gates

Normal Branch tests auto-discovers the new .cjs suite and existing tests through
the split runner. This mixed runtime/test/docs commit omits the skip marker;
no workflow change or separate dispatch. Review covering results tied to the actual
delivered SHA, including both Join suites and existing browser/server/assembly
regressions; correct failures with fresh bound approval. Earlier 4A.11 CI does not
validate this change. Obtain explicit bounded acceptance before closing 4A.12.
README and TODO root remain accurate and unchanged; numbered handover/index and
task status are updated. 4A.11 remains closed; 4A.13, both feedback deliverables,
009.7 and wider gates remain open. No archive/Patch/, merge or deployment.

[Task and acceptance](../todo/097-feedback-delivery-plan.md#4a12-join-reporting---2026-11-11).

## 4A.12 bounded close-out - 2026-11-11

Implementation delivered at 981ffe61a9bb4da162944707b42132d384eea1ad.
Successful Branch tests 42949763708 attempt 1, job 130291065704, identifies that
exact head SHA on features/perplexity-009.7. Published run.json and jobs.json
agree on completed/success; all listed stages succeeded. Publication commit:
488997aacb50ed44d785c9738457fab1b854ad90. Evidence is pinned to that immutable
snapshot under ci-results-42949763708-attempt-1/, not to rotating latest results.

Detailed reconciliation read the lossless workflow reader at
reader-chunks/file-000038/ within that directory:

| Parts | Direct observed evidence |
|---|---|
| 131-134 | admin-join-feedback.test.cjs: all 26 named cases passed; zero failures, cancellations or skips. Both kinds, single/bulk HTTP and network failures, one rejection/no pane duplicate, matching retry/other-target isolation, bulk key vs payload ordering, structured/HTTP fallback errors, stale/superseded outcomes, refresh separation/no replay, non-Join delegation, empty selection, encoded ID and idempotent/late installation. |
| 162-163 | initiative-join-gate.test.cjs: 12 passed, zero failures/cancellations/skips. Blocked clicks, zero/negative initiative, leave, metadata refresh, original response consumption, rejection fallback, explicit identity and unrelated-error preservation on retry. |
| 080-081 | All 10 InitiativeJoinTests passed: individual/bulk rejection, atomicity/rollback, invalid types, imported/legacy invalid active state, leave/clear and valid zero/negative/positive values. |
| 021 | Browser loading/header order, Join persistence without mutation or unrelated clear, matching retry, old-scope suppression, keyboard fallback and preserved request-error shape passed. |
| 022 | Browser rendering: explicit severity/dismissal/live-region structure, narrow wrapping, safe text, deadlines, retry isolation, scope/timer suppression and stable existing error DOM passed. |
| 025 | Complete assembled syntax/identity, reader bounds, runner isolation, fragment size/identity/syntax, tamper guard and adapter serving/refresh/wiring passed; wrapped-message/header layout and relevant workspace-navigation entries also passed. |

These are individual result entries, not merely green job metadata. The 26 and
12 are separate suite counts (38 Join cases), not a count of unique requirements;
server/browser coverage is not added to invent a total acceptance count. The
server suite ran in CI; no local server-suite execution is retroactively claimed.
No blocking failure was found in reviewed evidence. Targeted passages were read;
no exhaustive raw-log reconstruction, screenshot assessment or unrelated test
audit is claimed. Original preparation limits remain historical and distinct.

The user's 2026-11-11 04:08 CET request to reconcile, close and push supplies
bounded acceptance conditional on supporting evidence; the above reconciliation
supports closure of 4A.12. Accepted scope is Join reporting only, preserving existing
client/server gates and action semantics. This does not claim new authenticated
live-server exercises, human visual/manual workflow, screen-reader verification
or exhaustive accessibility acceptance. Focused JS uses a scoped controller
adapter and mocks; existing browser/server fixtures provide additional automated
evidence, not universal full-Admin end-to-end coverage of every Join scenario.

This close-out changes only HANDOVER.md, this section and the 097 task plan.
Commit message includes [skip ci]; no runtime, tests, pins, markup or workflows
change, no new tests execute and no workflow is separately dispatched. The marker
is not proof of a new workflow state. README/TODO root remain accurate and unchanged.
4A.11 stays closed. 4A.13 remains proposed; pane/global compatibility retires only
after relevant migrations. Deliverable 2 near-field/connection work, Deliverables
1/2 acceptance and phase 009.7 hardening remain open. No merge or deployment.
