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

## Global compatibility retirement preparation - 2026-11-11

This entry supersedes pending composition execution and global-retirement delivery
notes above and in the older index, not their historical validation limits.
Composition commit 8d45d1c19e67b21c387205b1711956305d8a9823 is covered by successful
Branch tests 42967879960 attempt 1, job 130349218050; publication
 df4137b62c7668442c08e8ac9425c135c611c730. Run/job metadata match the tested SHA.
Direct reader file-000038 parts 022-023 confirms all four new Chromium scenarios
report ok; part 023 also confirms all three retained inventory checks report ok.
All main CI stages succeeded. These are actual assembled-page fixture results,
not every producer combination or authenticated live-server acceptance.

Prepared against publication df4137b62c7668442c08e8ac9425c135c611c730, this change
makes deliver('global', text) without options throw before any controller or legacy
state changes, including blank clear calls. Explicit ticket/severity delivery and
controller begin/publish/resolve are unchanged. Pane compatibility retains its
neutral persistent behavior and observability. No automatic fallback notice is
created for a programming error. The known replaced core message() bodies remain
in source as guarded by inventory tests; they are not effective installed handlers
in the covered assembled-page paths. This does not claim exhaustive dynamic aliases.

The eight-case Node reconciliation suite replaces its deliberate global legacy
baseline with rejection/noninterference/explicit-delivery assertions, retaining
pane isolation. The identity matrix adds statistics.open and campaign-bundle.import:
19 selected identities, 171 unordered pairs, not 171 actual handler combinations.
The four existing full-page composition scenarios and original assertions remain
unchanged and must pass again with this runtime revision. Code/test review only;
no new local syntax, Node or Chromium execution is claimed. Normal covering CI
for the actual delivered SHA is pending; prior green runs do not cover retirement.

### Remaining producer dispositions

The 460 source census plus the statistics/import migrations and actual composition
results support this bounded global-route retirement. Remaining dedicated writers
are not silently reclassified as global producers or accepted as completed D1 work:
- features.js featureNotice, modal operation outcomes and display connection status
  remain local; import success alone was migrated. Connection/recovery persistence
  and polling deduplication remain D2; local producer integration remains open.
- lairs.js lairNotice/lairActionNotice and lair-state-buttons' local feedback remain
  configuration/action-local. Their future integration must retain scope, drafts,
  validation/request/refresh distinctions and busy guards; no mutation redesign.
- campaign-viewer-admin.js campaignViewerNotice belongs to explicitly selected
  authorized-campaign viewer grants, not the active encounter. Retain its generation
  and save controls; later integration must not substitute encounter scope.
- Ownership guidance, previews, read-only status and tools busy-close guidance keep
  their dedicated roles. Pane consumers listed in 460 remain pending migrations.

These are retained/deferred local obligations, not new exclusions of an applicable
global alert and not blanket D1 acceptance. The separate /users page remains outside
the GM Admin global route. Review retirement covering CI, relevant retained tests
and any residual caller failure before requesting bounded 4A.13 acceptance. Both
deliverables/009.7 stay open. No merge/deployment, workflow change or dispatch.

## Retirement CI failure and browser fixture correction - 2026-11-11

Run 42969807025 attempt 1, job 130355375717, tested retirement
 e15ad2b18f308d116fab288e058b24f7842f8c98 and failed. Publication:
3ac3db9529d127e3922bbf0cd2d2d97ca25fc23c. Preserve this historical failure.
Python/browser errors at widths 1440/768/375 originate from the header layout
fixture's direct message() injection at test_admin_header_hierarchy.py:133.
Reader parts 120-123 show the retired-global guard rejecting it; part 213 shows
the standalone connection audit repeating the same three suite errors. These
are not three additional independent application defects. Part 023 confirms all
four composition scenarios and three inventory checks still report ok.

At the user's browser-only correction request, replace that single injection with
real feedback.begin/publish using global region, fixture.header-layout operation,
header target and explicit info severity. Text and all original assertions,
viewport widths, harness, scrolling/draft/pane/keyboard and mutation checks remain
unchanged. Persistent info avoids a success-expiry race in this layout fixture.
No runtime, shared-fixture, Node test or workflow change. Code review only; no new
local syntax or Chromium execution is claimed. Normal covering CI must verify
header subtests and the audit rerun for the actual corrective SHA.

The separate Node failure is still OPEN: reconciliation.test.cjs:81 expects true
from deliver(), but successful publish returns record ID 'sg-feedback-9'. Reader
parts 137-138 report seven passes/one failure. This browser-only commit does not
fix that assertion or claim the overall run can become green yet. 4A.13 remains
blocked on that correction, covering CI, final reconciliation and bounded acceptance.
No new acceptance, merge/deployment or broader deliverable/phase closure.
