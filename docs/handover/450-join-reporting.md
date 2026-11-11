# 450 - Join reporting

[Back to handover index](../../HANDOVER.md)

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
