# 380 - Feedback delivery plan and continuity

[Back to handover index](../../HANDOVER.md)

## 4A.2 preparation and baseline reconciliation - 2026-11-10

The user authorized continued 4A.2 preparation and compatibility review. This commit
contains the narrowly scoped Start/restart request migration and its 12-test Node
regression file, with README and [task status](../todo/097-feedback-delivery-plan.md#4a2-startrestart-request-feedback---2026-11-10)
reconciled. Implementation is prepared for delivery; covering CI/full-Admin validation
and acceptance remain pending. Deliverable 1 and SG-TODO-009.7 remain open. No
commit SHA is invented before the write. 4A.3 eligibility/tie-order producers and
all other bounded producers remain outside this change.

The effective override in static/admin-initial-visibility.js begins an encounter-scoped
battle.start ticket before POST /api/battle/start. Request failures publish explicit
persistent errors without collapse or refresh. Matching success silently resolves
only its error before the existing collapse and load(). Stale/superseded success
cannot collapse/refresh another encounter; stale failures cannot publish. load()
retains ownership of refresh errors, so an applied Start is not presented as a
failed request. No automatic POST retry, authorization/payload/eligibility change,
new success toast, controller fallback or source re-split is introduced.

Prior preparation executed two JavaScript syntax checks and 12 passing Node tests,
with zero failures/skips. Four temporary negative controls were detected: success
severity for request errors, removed stale-success guard, restored legacy message
route and delayed resolution after refresh. The restored draft passed all 12 again.
Unchanged controller and visibility reconstruction matched live Git blobs
c4a82d73b21f4657da651ce45f76003c3348a6ef and
59418bb55144693a959aa065c7faaf4683062e33 before modification. Draft sizes are
4,430 UTF-8 bytes for the visibility asset and 7,423 for the test. These results
are from preceding preparation, not new executions during the final review. The
complete visibility asset and real controller execute with mocked DOM/transport
and bootstrap adapter; they do not establish complete Admin or live-server behavior.
The refresh test simulates load-owned failure, not the full state-load pipeline.

Compatibility review reused verified complete reads against unchanged live source
trees and inspected header hierarchy, dependent-control fixtures and asset-cache
implementation/tests. Feedback bootstrap precedes core Admin; the visibility override
follows core Admin; main Start and tie confirmation resolve startBattle dynamically.
The header moves original controls without replacing handlers. Existing independent
panel page tests cover native Start/restart collapse and rejected-Start visibility;
minimal initial/dependent-control fixtures do not invoke a Start wrapper without
its feedback dependency. Their unchanged assertions remain required by CI. Per-render
cache busting supplies a fresh local script token, so no template-version change
is required. The eight core fragments, bundle pins/marker, initial visibility logic,
lair/workflow filtering, drafts and manual-reopening behavior remain unchanged.
Existing CI discovers all .cjs files and Python page fixtures; no workflow change
or separate dispatch. Full suites were not executed locally for this change.
Normal push-triggered CI is required: the mixed commit has no skip marker.

Baseline evidence is separate from the pending 4A.2 result. Most recently, Branch
tests 42796273382 attempt 1 completed/success for
ca1600003ac4de0809a348dec7cef18cc6875fc9; run.json was reviewed in publication
dfd56fbf419a6239cf45b7e2d3d6b42f795289d7 under
ci-results-42796273382-attempt-1. Earlier successful run 42791962823 attempt 1
covered add05c64a4d8ef88fdb39c1d589f3704237a1fd4, published at
ae06a050b439b8c8e4e3f8a2736d889c7c4df1c0. 4A.1 is delivered with covering
configured CI verified, not awaiting that baseline's CI. Reported fixture/identity
repair blockers were resolved for that baseline. The pending-CI/repair wording in
older dated sections below is historical, not a current blocker. Failed earlier
runs remain failed evidence; no individual-log re-review, manual acceptance or
formal 4A.1/phase closure is inferred from workflow success.

README now distinguishes the green baseline from pending 4A.2/final producer
validation. Root TODO/HANDOVER indexes retain correct links/open phase scope and
need no edits; SG-TODO-019 remains proposed in its own section. The earlier failed
approval attempts did not save the proposed green-baseline checkpoint. This mixed
implementation commit performs the necessary reconciliation without another planning
commit. Final caller migration/compatibility-route retirement, Deliverable 2 and
broader confirmation/accessibility/responsive acceptance remain outstanding.

## CI repair stages - 2026-11-10

The user approved all three corrective stages after review of run 42774406816
attempt 1, tested SHA f8f3918a00b2b863165edbe92cf66fe79c2e1d6c, evidence commit
4fd1bd2dc19b2a78da20bd9483c670cc84d02581. The failed Python suite reports
1,476 tests, 15 failures and 68 errors; this is not a count of independent bugs.
Published JavaScript logs confirm the 15 state-load regressions passed, but the
combined Python, JavaScript and standalone groups failed. Publication itself
worked and does not establish application test success.

Stage 1 is prepared in this commit: load the real feedback controller/view/Admin
bootstrap before the candidate and typing/focus browser source slices; route their
pane notifier through the actual controller instead of direct DOM writes; and
supply the real controller through the Join-gate VM fixture's region adapter.
The shared candidate fixture is also used by the source-bonus-offer browser tests.
Existing selection, draft/edit, signed-offer, focus, request-count, join prevention,
server-rejection and response-preservation assertions are retained. No production
fallback, production code change or validation-gate weakening is included.

Executed preparation: all 12 Join-gate Node tests passed, including two added
explicit operation/error identity and unrelated-error isolation checks. The exact
original fixture failed six checks against the same production gate as a negative
control. Reconstructed controller, gate and original Node fixture matched their
live blob identities. The new Python helper passed AST parsing. Repaired Chromium
fixtures and inherited source-offer cases were not executed locally; normal CI
must validate them. The helper only defines its loader when invoked by standalone
Python discovery and performs no network, browser launch or external write.

Stage 2 remains authorized/pending: reconcile managed-notification tests and the
modified bundle identity/isolation contracts while retaining fragment bounds and
regression assertions. Stage 3 remains authorized/pending: investigate remaining
layout/behavior failures and review combined corrective CI. Continue preparation
without requesting plan approval again; every external write still needs its own
complete exact-content approval. This stage is not a claim that all 68 errors or
all failed groups are fixed. The task plan at ../todo/097-feedback-delivery-plan.md
and root TODO still correctly leave 4A.1, Deliverable 1 and 009.7 open, so no task
closure or unrelated index/README edits are included. Earlier implementation and
skip notes below remain historical. No covering corrective CI or commit SHA is
invented before evidence exists.

## 4A.1 implementation checkpoint - 2026-11-10

Prepared for this commit on features/perplexity-009.7: state-load migration in static/admin/030-source.js and static/admin-feedback-admin.js, plus tests/admin-state-load-feedback.test.cjs. The [4A.1 task status](../todo/097-feedback-delivery-plan.md#4a1-implementation-checkpoint---2026-11-10) keeps the unit, deliverable and phase open pending covering validation. No merge or deployment-ready claim is made.

The existing request-start sequence is retained, with an encounter epoch rejecting responses whose original scope changed. load() verifies accepted sequence/epoch before assigning latest or rendering. Persistent errors use the explicit state.load identity; matching successful rendering silently resolves only that operation. A legitimate accepted scope transition rebinds its original ticket. The no-battle early return and strict load(true) original-error rethrowing remain intact, including stale failures whose notices are suppressed. Current malformed scope data produces an actionable reload error instead of rendering or silently resolving an error.

Executed during preparation: two JavaScript syntax checks; 15 passing Node VM regressions using the real controller/bootstrap and production request/load slices; and four detected temporary negative controls for error expiry, unrelated clearing, old-scope acceptance and broken rethrowing. Reconstructed unchanged 030, bootstrap and controller contents matched their live Git blob identities before modification. Modified 030-source.js is 19,565 UTF-8 bytes; the bootstrap is 6,630 bytes. Eight-part source order and the tracked admin.js failure marker are unchanged.

Evidence limits: mocked network/DOM slices, not a complete checkout, full-Admin browser, authenticated/live-server or assistive-technology verification. The local request function was reconstructed from the verified prior read; no complete local 010-file identity is claimed. Existing bundle-identity/legacy-fixture reconciliation, final combined regressions and covering CI review remain pending. Historical preparation results are not a new test run for this approval. The existing JavaScript CI discovery includes the new test. No commit SHA, workflow result or acceptance is invented before evidence exists.

Background uploads, character editing, Start/restart and other producers remain outside 4A.1; Deliverable 2 is unchanged. README and root TODO/HANDOVER were reviewed against unchanged live identities and remain accurate without unrelated edits. This mixed commit uses normal CI without [skip ci]. The older documentation-only and checkpoint-2 skip notes below are historical, not instructions to skip this implementation commit.

## Current status - 2026-11-09

SG-TODO-009.7 and Deliverable 1 remain in progress/open. The [seven-step plan and ten-point policy](../todo/097-feedback-delivery-plan.md) remain authoritative. The user explicitly approved two work-in-progress checkpoints on features/perplexity-009.7 before continuing step 4. This is not a complete integrated feedback delivery or phase acceptance. The accepted [009.6 baseline](370-live-encounter-workspace.md#sg-todo-0096-close-out---2026-11-09) must remain intact.

The original planning record and detailed checkpoint-1 preparation history remain in [this section at checkpoint 1](https://github.com/dajomas/Scrying-Glass/blob/51e3e3bfcc8e56176b8bcc2559e74bee46e5f493/docs/handover/380-feedback-delivery-plan.md). Live instructions were read before preparation; previously complete reads were reused against verified commit/file identities, not assumed temporary execution files.

## User-approved checkpoint 1 of 2 - 2026-11-09

Committed as 51e3e3bfcc8e56176b8bcc2559e74bee46e5f493 on features/perplexity-009.7. It saves the controller, view, CSS, 25-test Node suite and 14-test isolated Chromium suite, plus status documents. Its workflow change adds this branch to Branch tests while preserving existing branch targets and test steps. No [skip ci] marker was included. A covering CI run has not been checked; no workflow completion or success is claimed.

Historical local preparation: both JavaScript syntax checks, 25 Node tests, 14 Chromium component tests and Python AST parsing passed. Four temporary negative controls detected error expiry, unrelated clearing, stale-attempt acceptance and unsafe HTML rendering. These are not full-Admin, screen-reader or authenticated-server verification.

## User-requested checkpoint 2 of 2 - 2026-11-09

Committed as 8ba97701a76328909b9570a8bfbf523e80abf4f6 on features/perplexity-009.7 with [skip ci]. This checkpoint saves the prepared Admin bootstrap, header asset order, first core fragment, lookup/Join-gate routing, guarded obsolete timeout asset and loading fixture. It intentionally activates incomplete wiring on the topic branch only. No production deployment or merge is requested. The tracked admin.js failure marker, eight-part reader/order, permissions, server validation and combat rules are unchanged. The shared request helper observes state with request-start sequencing; older responses cannot select the feedback scope. The 030 fragment remains unchanged.

Incomplete behavior is explicit: remaining helper callers temporarily use persistent neutral info feedback, not final success/error metadata or complete stale-result protection. legacyRegions() exposes those destinations. Step 4 must eliminate production use of that route, migrate tools/lair/viewer direct writers, distinguish candidate cancellation/no-match/provider failure and reconcile duplicate Join reporting. Modal-only notices and persistent state/ownership guidance are not blanket success timers. Do not deploy this checkpoint as completed Deliverable 1.

Original step-3 preparation passed six JavaScript syntax checks and 15 real Chromium loading-slice tests; a temporary negative control detected the old timeout observer clearing managed errors. Original live-file blob identities and reconstructed component SHA-256 identities were checked. This checkpoint factors the loading fixture's repeated assertions/setup into helpers; that factored test file has not been rerun for this approval. Its prior 15-test result is historical, not a claimed result for the refactored file. Complete assembled Admin, existing suites, actual assistive-technology/live-server validation and covering CI remain pending.

The user explicitly requested [skip ci] for checkpoint 2. Its proposed/approved/actual message must contain that marker; no workflow configuration is changed or separately dispatched. No skipped-run state or test success is inferred from the marker, and no new checkpoint SHA is invented before the write. Normal CI applies again to subsequent implementation commits unless separately instructed.

README now identifies its fixed bundle hash as the accepted pre-009.7 baseline rather than the modified checkpoint. Bundle-identity assertions and legacy VM fixture contracts remain intentionally pending until the full producer migration is reconciled; do not describe the repository suite as passing. The current TODO index already records both checkpoint scopes and leaves 009.7 open, so no unrelated index change is needed.

## Continuation and remaining work

After this checkpoint is written, resume Deliverable 1 step 4 on features/perplexity-009.7 using the live source. Preserve original controls/drafts, independent panels/lairs, Start/restart collapse and failed-Start visibility, manual reopening, native roster/local scrolling and tools-dialog keyboard/focus/busy/nested behavior. Complete producer migration, full-Admin regressions, identity/fixture updates, documentation/TODO reconciliation, exact-payload review and bound approval.

Deliverable 2 remains connection failure/recovery warnings, polling deduplication, field/combatant-associated validation, scope/retry handling and combined keyboard/responsive regressions. Destructive-confirmation review and broader responsive/accessibility hardening remain open after both feedback deliverables.

## Bounded 4A planning reference - 2026-11-09

The user reported repeated interrupted attempts whose displayed output/artifacts disappeared, then requested smaller group-4A sub-tasks and asked that the suggestions be saved as documentation only. The cause of those interruptions has not been verified; do not label them a proven connector-size limit, timeout or temporary-file cleanup. Do not count disappeared output as durable implementation or validation evidence. The verified checkpoint above remains the continuation baseline.

The [13 proposed 4A execution units and per-task boundaries](../todo/097-feedback-delivery-plan.md#bounded-group-4a-sub-tasks---2026-11-09) are now recorded in the existing delivery plan, without creating new deliverables or changing the approved feedback policy. All 4A.1-4A.13 remain proposed/not completed by this update. The first bounded unit is 4A.1, state-load feedback only. Live source/effective handlers must be verified before implementation; unrelated operations sharing a file must not be pulled into the same task.

Each bounded unit should reach a reviewed result with focused executed checks and explicit dependencies before another begins. Every subsequent external write still needs complete bound approval and its relevant tests/documentation. Focused tests are not full-Admin or CI acceptance; temporary artifacts are not the sole recovery point. The normal implementation CI rule resumes after checkpoint 2's one-off skip.

This update changes only the existing task and handover documents and includes [skip ci]. Links, branch/checkpoint references and the proposed scope were reviewed. README and root TODO/HANDOVER were reviewed/reused against the verified baseline and remain accurate without edits. No automated tests were executed, no workflow was modified/dispatched and no 4A implementation or phase closure is claimed.

## Deadline fixture clock correction - 2026-11-10

At the user's request, this narrowly scoped stage-2 correction changes only
test_success_deadlines in tests/test_admin_feedback_loading.py and this record.
The fixture installed Playwright's clock without pausing it. Time could advance
between browser protocol calls, so run_for(2999) did not mean 2,999 milliseconds
since notice creation. Pause the clock after readiness and before both emits;
then assert visibility at 0, 2999, 3000, 4999 and 5000 ms. Both notices share the
frozen start time. Retain the exact three/five-second policy and add a no-write
assertion. Production timers, rendering and other tests are unchanged.

Executed: Python AST parsing of the revised method; a real Chromium Clock API
smoke with native timers passed all five boundary states. A controlled 500 ms
host-delay comparison reproduced the unpaused issue: 516 ms had elapsed before
run_for(2999), producing 3515 ms and a hidden pane. With pause_at, the same delay
left elapsed time at zero and the pane visible at 2999 ms. The numeric pause_at
argument uses Unix seconds; run_for uses milliseconds. The smoke used async
Playwright because this execution environment has a running asyncio loop.

These are clock-harness checks, not execution of the production feedback-loading
fixture or its full suite. Covering CI remains pending. Source CI run 42778760003
attempt 1 covers 122e131a83e0bbd4f314d8f6fd95ace8a6cea6bb and remains failed;
evidence is at e7130a196ca5211f66596cab03d14c3298928b39. Its Python summary is
1,476 tests, 15 failures and one error, compared with 68 errors before stage 1.
This correction does not resolve the other managed-notification, source-identity,
roster-rejection or layout failures, complete stage 2/3, or close 4A.1/009.7.
Normal CI applies without a skip marker. README, TODO and handover index links
remain accurate without edits; existing task statuses stay open.
