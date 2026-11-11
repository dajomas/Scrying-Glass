# 467 - Campaign-bundle import feedback

[Back to handover index](../../HANDOVER.md)

## 4A.13 bounded migration - 2026-11-11

Prepared against features/perplexity-009.7 at
86acacd09e497c3afba40489b31e541831d32753. This change replaces only the successful
campaign-bundle import alert in static/features.js. After file selection and
confirmation, an encounter-scoped campaign-bundle.import ticket targets import.
Confirmed POST success publishes explicit global success with the complete existing
campaign name and switch/Imported encounter checkpoint recovery instructions.
Controller attempt/scope guards suppress stale publication; the global success
uses the approved five-second lifetime, not the old blocking alert lifetime.

The original perform busy guard, confirmation, FormData POST, setup refresh,
file-input clearing, feature/core refresh and local error handling remain intact.
Import failures stay local in this bounded success migration. A later setup-list,
feature or core refresh failure does not withdraw or relabel confirmed global
import success. No automatic mutation retry, campaign switch or checkpoint restore
is added. Shared polling/draft machinery and non-import actions are unchanged.
The remaining full-page composition gate must verify this in the assembled UI.

The new 12-case CJS suite evaluates the complete production features script using
the existing real controller/Admin-bootstrap fixture with mocked DOM/HTTP and a
controllable clock. Cases cover FormData/wording/no alert, five-second expiry and
unrelated error isolation, cancellation/missing file, duplicate suppression,
rejection/no replay, scope/away-back epochs, three post-import refresh failures
and same-scope draft preservation. Existing feature test assertions are unchanged.
Code/test review performed; no local syntax or behavioral test execution is claimed.
Normal CI discovers the new CJS file without workflow changes. Review its results,
existing feature draft/polling regressions and relevant browser/loading checks for
the actual delivered SHA before acceptance. No delivery SHA or new run is invented.

## Statistics-open evidence reconciliation

Implementation 83fc58b07bbfee3e420ad37dcc2fdc3795ecad3f is covered by successful
Branch tests 42957102940 attempt 1, job 130314688066. Published run/job metadata
match the tested SHA; evidence publication is
86acacd09e497c3afba40489b31e541831d32753. Direct workflow reader file-000038
parts 171-173 confirms all 18 new statistics-open cases passed with zero failures,
cancellations/skips; parts 173-174 confirms the original restoration file passed.
Part 117 reports the isolated Chromium statistics-layout test ok; part 118 reports
1481 Python tests and OK. All main job steps succeeded. This supersedes the pending
covering-CI/browser-execution notes in 465 and the previous task/index snapshot;
it does not turn focused fixtures into full-page or authenticated live coverage.
The preparation negative controls in 465 remain historical local evidence.

## Remaining gates and limits

4A.13 remains in progress. Bundle-import covering CI, actual full-page/late request,
bulk and renderer composition, monitoring unintended legacy.global use, deliberate
global compatibility retirement/baseline-test replacement and explicit bounded
acceptance remain required. Retain pane compatibility and separate local-notice
integration obligations. Dedicated feature/lair/viewer dispositions and Deliverable 2
connection/polling/field-association work are not silently closed. No new human
visual, screen-reader, authenticated live-server or exhaustive accessibility pass.
4A.1-4A.12 remain closed; both feedback deliverables and 009.7 remain open.

This mixed runtime/test/docs commit uses normal CI, without [skip ci]; no workflow
change/dispatch, merge, deployment or future blanket write approval. README and
TODO root remain accurate and unchanged. [Task](../todo/097-feedback-delivery-plan.md#4a13-global-reconciliation---2026-11-11).
The [460 census](460-global-feedback-reconciliation.md) remains a dated pre-migration
source snapshot, not a current claim that the two alerts remain unmigrated.

## Bundle CI and full-page composition preparation - 2026-11-11

This entry supersedes earlier pending bundle-covering-CI notes here, in the task
record and the index. Bundle implementation 1fc5b724a47ff8dd29ef6c168d938dc818f86d0d
is covered by successful Branch tests 42959512777 attempt 1, job 130322466945;
evidence publication b610b93b7a2679178c685390a9ba2111d3ac66fa. Run/job identities
match. Direct reader file-000038 parts 162-163 confirms all 12 new cases passed,
zero failures/cancellations/skips. All main validation stages report success;
this is not a fresh individual-log review of every retained regression.

The next test/docs change is prepared against that publication. The new
GlobalFeedbackCompositionTests loads ADMIN_HTML and all 42 production script
includes in Chromium, serving actual static files from the disposable assembled
checkout. It rejects the tracked Admin marker by bundle size, records page errors,
missing static assets, alerts and mutation requests, and retains compatibility.
It uses the existing SQLite-generated fixture state with intercepted HTTP, not
an authenticated application server or real import/turn mutation backend.

Four scenarios are supplied, not four exhaustive acceptance requirements:
- Actual End/Reset handlers isolate failures and explicit retry; full load/render
  preserves a draft and selection, and late bulk select-dead/source-review
  delegation remains effective without unintended global compatibility traffic.
- DOMContentLoaded Join single/bulk ownership composes with the request/Next chain;
  matching resolution isolates targets and an uncertain Next result is not replayed.
- A held End response cannot publish after load(true) accepts another setup scope.
- Actual statistics click/retry and bundle file input coexist with independent
  Reset feedback, retaining literal recovery text and no alert/global legacy route.

Several controls are invoked through their installed onclick binding or delegated
function to reach the real handler without bypassing it; this is not a claim of
human pointer/keyboard coverage for every control. Assertions monitor global
compatibility for these exercised paths only, not every possible producer.
Python compilation/AST parsing passed locally; four test methods were enumerated.
Chromium and repository behavioral execution were not run locally. Configured
unittest discovery executes the file through run_split_tests.py in normal CI;
no workflow change or dispatch. Review covering evidence for the actual test
commit and correct failures under fresh approval. Earlier green CI does not
validate the newly added composition cases.

No runtime, shared-fixture, core, pin or markup change is included. README,
HANDOVER index and TODO root were reviewed/reused and left unchanged; the current
index's older pending wording is explicitly superseded by this linked section.
4A.13 remains open pending composition results, remaining disposition review,
deliberate global compatibility retirement with pane compatibility retained,
covering CI and explicit bounded acceptance. No merge/deployment or broader
feedback-deliverable/009.7 closure is implied.
