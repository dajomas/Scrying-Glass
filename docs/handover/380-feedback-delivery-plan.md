# 380 - Feedback delivery plan and continuity

[Back to handover index](../../HANDOVER.md)

## 4A.5 End-battle feedback delivery - 2026-11-10

Prepared at the user's implementation/push request on features/perplexity-009.7:
static/admin-end-feedback.js, its deferred include after Start validation, the
15-test Node fixture and existing task/handover updates. The [4A.5 task](../todo/097-feedback-delivery-plan.md#4a5-end-battle-feedback---2026-11-10)
remains in progress pending covering CI/full-browser review and bounded acceptance.
Earlier acceptance intent did not close an unimplemented task. No commit or run
identifier is invented before the write/results exist.

The small enhancement overrides only End's onclick. Separate encounter-scoped
battle.end.validation and battle.end identities make actionable errors persistent.
A confirmed valid attempt silently resolves its validation error. Matching request
success replaces only its request error with the existing non-resetting success
message before load(); state.load retains ownership of subsequent refresh errors.
Cancellation leaves errors intact. Refresh alone, unrelated success and validation
rejection do not erase End request errors. Scope/attempt guards suppress stale
publication and post-response refresh in a different encounter, including away/back
transitions. Preserve the empty-order eligibility gate, exact confirmation, POST
method/body contract and server behavior. No automatic retry, combatant reset,
new concurrency policy or migration of Reset All/other producers is included.
Unexpected load rejection propagates without relabelling the successful End POST;
ordinary load() already handles and owns refresh failures.

Executed during this preparation: both JavaScript syntax checks passed; 15 Node
regressions passed with zero failures/skips; three temporary negative controls
(error severity changed to success, stale-success guard removed, validation
resolution removed) were detected; the restored draft passed all 15 again. The
complete End asset executes with the real controller and complete Admin bootstrap,
but mocked DOM, network and refresh. The refresh error is simulated through the
real feedback API, not a full loadState/render pipeline. Timers are controlled.
These are not complete Admin/browser, authenticated server, manual or covering CI
results. Full browser/combined suites and covering CI remain pending.

Unchanged controller/bootstrap/template reconstructions matched live Git blobs
c4a82d73b21f4657da651ce45f76003c3348a6ef,
59553fdd9fc93ac8d23f3ea54536aded1a945ab5 and
23abc263b69c92a1f85ec3d7d99fd78577a58bd1 before preparation. The End asset is
1,453 UTF-8 bytes; its Node fixture is 9,072 bytes. Live instructions/write schemas
were retrieved, complete source/config/index reads reused against unchanged live
identities, and current task/handover contents reviewed. A truncated handover read
was supplemented by the complete approved e4fda47eba99e58a921e82630983a8a8437ff80b
content with the same current blob identity e070ec12bf272773275a1d8bdd20669b2dca5f6d.
Existing CI discovers the .cjs with no workflow change or separate dispatch. Core
fragments, bundle identity pins/marker, server routes, styles and previous tests
are unchanged. README/root indexes retain accurate open-phase scope/links without
edits; historical notes below remain dated history. This mixed commit has no
skip marker. 4A.2/4A.3/4A.4 stay closed; 4A.1's formal status, SG-TODO-019 and
agreed delivery order are unchanged. Deliverable 1, Deliverable 2 and 009.7 remain
open. No merge, deployment or premature 4A.5 acceptance is included.

## 4A.4 bounded acceptance and close-out - 2026-11-10

The user explicitly accepted the bounded shared main/modal Next-turn feedback scope
following successful stage 2 CI and requested proceeding with bounded acceptance.
4A.4 is completed/closed, reconciling stage 1 fixture preparation and stage 2 runtime
migration. Stage 2 implementation baf7ddf4dc9059b11c9df06cd85d5e3e0f81fdcf is covered
by successful Branch tests 42818381973 attempt 1 on features/perplexity-009.7,
published at cf43f0373617b3b2a07f0207bc7143adc4ad3bad under
ci-results-42818381973-attempt-1. Reviewed run.json and jobs.json match that exact
SHA and show successful syntax/import, Python/browser, pytest, JavaScript and
standalone browser/audit stages. Stage 1 e07d5eb832ba8d80e02c9d9933ad7c0f5038936d
also has verified successful covering run 42814023791 attempt 1, evidence
50e52f692b1d08eb059a785b6937426229cf9934. Neither publication is the tested source SHA.

Acceptance covers persistent operation-specific Next errors, related-success-only
resolution, guard-safe report replacement, stale global/modal feedback suppression,
explicit informational no-participant feedback and preservation of the existing
mutation/refresh distinction, uncertainty wording, concurrency, control restoration,
actor-reopening safeguards and no automatic POST retry. It does not approve a new
turn algorithm, unrelated producers or near-field validation scope.

Preparation's two syntax checks, 20 passing focused Node tests, four detected
negative controls and restored-draft passes remain historical executed evidence.
The later covering configured CI success is separate evidence. No new local test,
individual-test log/assertion review, authenticated live-server or manual test is
claimed by this close-out. Delivery-time pending-CI/acceptance statements below
are historical and superseded by this record. See the [completed task](../todo/097-feedback-delivery-plan.md#4a4-stage-2-shared-next-feedback---2026-11-10).

4A.2/4A.3 remain closed; 4A.1's formal status, SG-TODO-019 and agreed delivery order
are unchanged. Deliverable 1, Deliverable 2 and SG-TODO-009.7 remain open. 4A.5
End-battle feedback is the next proposed bounded unit, not implemented or started
by this close-out. No full-deliverable/phase acceptance, merge or deployment.

This documentation-only update changes the existing task and continuity sections.
README/root indexes and maintenance rules were reviewed/reused against verified
identities; their scope/links remain accurate without edits. No application/tests/
configuration/workflows change, no tests run and no workflow is separately
dispatched. Proposed/approved/actual message includes [skip ci]; that token does
not verify a workflow-run state. No documentation commit SHA is invented.

## 4A.4 stage 2 shared Next feedback - 2026-11-10

Historical stage 2 delivery follows; its pending validation/acceptance statements
are superseded by the bounded close-out above.

The user requested stage 2 preparation and push for CI after stage 1 succeeded.
Stage 1 implementation e07d5eb832ba8d80e02c9d9933ad7c0f5038936d has verified
successful covering Branch tests 42814023791 attempt 1, published at
50e52f692b1d08eb059a785b6937426229cf9934 under ci-results-42814023791-attempt-1.
Run and job/step metadata match the exact SHA and show all configured test stages
successful. This is baseline evidence, not covering CI for the new Next handler.

Prepared stage 2 changes only static/battle-actions-next.js, the new 20-test Node
fixture and current [task/handover status](../todo/097-feedback-delivery-plan.md#4a4-stage-2-shared-next-feedback---2026-11-10).
The shared main/modal operation publishes explicit battle.next errors and resolves
only a related error on complete success. An unpublished encounter-scoped lifetime
guard survives a settled error ticket so failed follow-up reconciliation can
replace that report, without rebinding into another encounter. Guard retirement
publishes no notice. Stale global/modal feedback is suppressed; no-active-participant
is explicit info after related-error resolution. Preparation/uncertain/confirmed-
advancement wording, existing POST/concurrency/control/reopening safeguards and
no automatic retry are retained. Normal state refresh alone does not resolve Next.

Executed in the preceding preparation turn: handler and fixture syntax checks;
20 Node tests passed, zero failed/skipped; four temporary negative controls were
detected (success severity for errors, removed old-scope guard, removed matching
resolution, removed settled-ticket rebinding); restored draft passed all 20 again.
Unchanged source/controller reconstructions matched Git blobs
dfa305352daf297e87c018879fb48e9fbcb0effd and
c4a82d73b21f4657da651ce45f76003c3348a6ef. Handler is 7,655 UTF-8 bytes, Node test
12,075. Tests execute the complete Next asset with real controller but mocked
DOM, transport, refresh and bootstrap scope adapter. Refresh-error publication is
simulated, not a full loadState pipeline. These are not full-browser, authenticated
server or new final-review executions. Full browser/combined suites and covering
stage 2 CI remain pending. 4A.4, Deliverable 1 and 009.7 remain open.

Compatibility review retains the green stage 1 Python fixtures unchanged: real
feedback assets/scope observation are already loaded, all existing transport,
concurrency, drafts, round/lair, reopening and uncertainty assertions remain.
Modal/global substring assertions accept explicit feedback prefixes; stale-scope
report suppression does not weaken existing no-reopen/no-retry assertions.
Deferred boot already supplies feedback before the real Next script. Existing CI
discovers the new .cjs and Python fixtures, with no workflow edit or dispatch.
Core fragments, bundle pins/marker, templates and other runtime assets are unchanged.
README/root indexes retain accurate scope/links without edits. Live instructions,
write schema and unchanged baseline identities were verified. The mixed commit
has no skip marker; no commit SHA or covering CI result is invented. 4A.2/4A.3
stay closed; 4A.1's formal status, SG-TODO-019 and remaining producers are unchanged.

## 4A.4 stage 1 fixture preparation - 2026-11-10

Historical stage 1 preparation follows; its pending-CI wording is superseded by
the verified stage 1 result above, not by a new local browser run.

The user approved stage 1 fixture preparation after a two-stage delivery proposal.
This proposed commit changes tests/test_battle_actions_next.py and its deferred-boot
fixture, plus the existing [task status](../todo/097-feedback-delivery-plan.md#4a4-next-turn-feedback---stage-1-fixture-preparation---2026-11-10)
and this record. Production battle-actions-next.js and all runtime assets remain
unchanged. This foundation stage is not usable new Next feedback or completion
of 4A.4; the draft handler migration remains separate stage 2 with its own complete
payload/approval. No stage 2 write is approved here.

Both fixtures load the real feedback controller/view/bootstrap. The interaction
fixture reuses feedback_browser_fixture.install_feedback; the parser/defer fixture
serves real feedback scripts in order before its stub Admin. Fixture message()
uses the real global adapter, not direct DOM writes. Initial, fetched and refreshed
snapshots pass through the production request-sequence/scope observer with complete
campaign/setup identities; malformed fixture scope fails explicitly. The scope-
switch fixture retains its other-setup behavior with a valid campaign reference.
Other Admin transport/helpers remain stubbed, not authenticated/live-server tests.

All 12 existing interaction methods and boot assertions are retained. A new
interaction method verifies real dependency availability, a rendered scoped error,
retirement on a setup transition and zero mutation requests. The boot fixture also
checks real dependency availability and an initially empty controller snapshot.
No transport/concurrency/reopening assertion is weakened and no production
fallback is added merely to accommodate isolated fixtures.

Executed: AST parsing of the added test method and node --check of the added
scope helper/notice JavaScript snippet passed. This is not full-file Python
execution or execution of either Chromium fixture. Browser methods, full suites
and covering CI remain pending. Existing Python discovery includes both modules;
normal CI is required and no workflow change/dispatch is included. Do not infer
that the shared Next algorithm or the later feedback migration passed from these
limited preparation checks. No commit SHA or workflow result is invented.

Preparation reused complete reads against verified unchanged live identities,
including the original interaction/boot blobs cf947154bc6c87a61c0b4f8bd6d077dffee7016e
and 59bb1396e8c91e26be71afef1cb0654a60e2c014, shared feedback helper and current
instructions. README, root indexes and maintenance conventions remain accurate
without edits. 4A.4, Deliverable 1 and SG-TODO-009.7 remain open; 4A.2/4A.3 stay
closed, 4A.1's formal status and SG-TODO-019 are unchanged. The two-stage proposal
was for reviewability, not an observed connector limit. Stage 2 still requires
the shared Next feedback implementation/regressions, documentation and approval.

## 4A.3 acceptance and close-out - 2026-11-10

The user explicitly requested that 4A.3 acceptance and close-out be recorded after
successful covering CI. 4A.3 is completed/closed for Start eligibility and tie-order
rejection feedback only. Implementation: 64101f24e624e1cb7a7f1ea2cea2c933b100fb72,
features/perplexity-009.7. Branch tests 42808219579 attempt 1 completed/success
for that exact SHA, published at e70419875322239b3d70373110a7538948a70097 in
ci-results-42808219579-attempt-1. Reviewed run.json and jobs.json verify the tested
revision and successful syntax/import, Python/browser, pytest, JavaScript and
standalone browser/audit stages. No individual-test log review, new local run,
authenticated live-server or manual test is claimed. The 13 regressions were not
executed locally; covering configured CI is distinct evidence, not a retroactive
local result or a claim that every individual log/assertion was inspected.

Acceptance covers persistent operation-specific validation errors, matching
resolution, cancellation/open-dialog behavior and separation from accepted 4A.2
request and 4A.1 refresh feedback without changing gates/order/payloads. The small
ordered enhancement and its template/test integration are accepted for this unit.
Delivery-time pending statements below are historical and superseded by this
close-out. See the [completed task](../todo/097-feedback-delivery-plan.md#4a3-start-validation-feedback---2026-11-10).

4A.2 stays closed; 4A.1's formal status, SG-TODO-019 and agreed delivery order are
unchanged. Deliverable 1, Deliverable 2 and SG-TODO-009.7 remain open. 4A.4 (shared
main/modal Next-turn feedback) is the next proposed bounded unit, not implemented
or started by this close-out. Full producer migration and wider phase acceptance
remain separate. This is not a merge or production-deployment approval.

This update changes only the existing TODO and handover sections. README and root
indexes were reviewed/reused against verified identities and retain accurate scope
and links without edits. No code/tests/configuration/workflows change, no tests
execute and no workflow is separately dispatched. Proposed/approved/actual commit
message contains [skip ci]; that marker does not establish an observed run state.
No documentation commit SHA is invented before the write.

## 4A.3 Start validation delivery - 2026-11-10

Prepared for delivery on features/perplexity-009.7 at the user's integration/push
request: static/admin-start-validation.js, its ordered deferred template include,
13-test Node regression file and existing TODO/handover status updates. The
[4A.3 task](../todo/097-feedback-delivery-plan.md#4a3-start-validation-feedback---2026-11-10)
remains in progress pending behavioral/covering CI validation and acceptance.
No implementation SHA or passing workflow is invented before evidence exists.

The 2,011-byte enhancement replaces only the two synchronous validation handlers;
it calls the existing normalOrder, tiedBuckets, tieUI, readTieOrder and
initiativeBuckets helpers. Separate encounter-scoped battle.start.eligibility and
battle.start.tie-order identities retain actionable errors and resolve only on
related validation success. Opening/cancelling ties preserves tie errors; a valid
no-tie Start resolves an obsolete tie error. Request and state-load feedback remain
owned by 4A.2/4A.1. Existing gates, selected order, payloads and cancellation are
preserved; near-field associations remain Deliverable 2. No automatic POST retry.

The earlier draft proposed editing 070-source.js (projected 19,531 bytes); the
integrated design instead loads this small asset immediately after
admin-initial-visibility.js. Core fragments, bundle pins/marker and the accepted
4A.2 wrapper remain unchanged, so no source-identity expectation update is needed.
Header reparenting preserves handlers. No new stylesheet, workflow or runtime
configuration. Per-render local-asset cache busting continues to apply.

Executed during preparation: node --check for the asset and new regression file
passed. The test syntax check first detected a malformed regex, corrected to a
literal include assertion; the final syntax check passed. Thirteen behavioral
regressions were prepared but NOT executed locally; neither full Admin browser
nor combined suites ran. The tests load production ordering/validation helper
slices and the real feedback controller with mocked DOM, transport entry point
and bootstrap adapter. Existing CI discovers the new .cjs and existing page,
tie-default/swap and eligibility fixtures. Treat delivery as validation pending
until covering normal CI is reviewed; syntax checks are not regression success.

Live instructions and available read/write schemas were reviewed. Complete prior
reads were reused against unchanged live tree identities, including README,
indexes, feedback/core/template/test contracts and maintenance rules. README's
separate-4A.3 warning and root index links/open phase scope remain accurate without
edits. Existing documentation history is retained below. The mixed commit has no
skip marker and performs no workflow dispatch. 4A.2 remains closed at a58ea25;
4A.1's formal status, SG-TODO-019, remaining producers, Deliverable 2 and phase
acceptance are unchanged. No merge or deployment is included.

## 4A.2 close-out - 2026-11-10

4A.2 is completed and closed for its bounded Start/restart request-feedback scope
at the user's explicit request to prepare the close-out after review of remaining
requirements. Implementation b73908e1368cb38f9ad5f5eb028bcb638a8fbbba is covered by
successful Branch tests 42800259474 attempt 1 on features/perplexity-009.7.
Evidence publication: 31b6401daeb93085e131bf144f147330046466b1, directory
ci-results-42800259474-attempt-1. Reviewed run.json and jobs.json match that exact
implementation SHA, report completed/success and show successful Python/browser,
JavaScript, pytest and standalone browser/audit stages. No per-test log re-review,
new local execution, authenticated live-server or manual test is claimed.

The delivered pre-request battle.start identity, persistent request failures,
matching-success-only resolution, stale response protection and successful
collapse/failed-Start visibility satisfy the agreed bounded scope with focused
preparation regressions and covering configured CI. load() owns subsequent refresh
failures; no automatic POST retry was introduced. Acceptance is limited to this
unit by the user's close-out request, not inferred for neighboring producers or
the phase. No separate mandatory manual-test gate was agreed for 4A.2.

The [task record](../todo/097-feedback-delivery-plan.md#4a2-startrestart-request-feedback---2026-11-10)
and README remove stale pending-4A.2-validation wording. The preparation section
below remains historical; its delivery-time pending statements are superseded by
this close-out, not deleted or applied to the current result. 4A.1's formal status
is unchanged. Deliverable 1, Deliverable 2 and SG-TODO-009.7 remain open. 4A.3 is
the next proposed bounded unit: Start eligibility and tie-order rejection feedback,
without changing gates, ordering or payloads. No 4A.3 implementation is included.
SG-TODO-019 remains proposed and the agreed delivery order is unchanged.

This is a documentation-only update to README and the existing task/handover
sections. Root TODO/HANDOVER indexes and maintenance rules were reviewed/reused
against verified live identities; their links and open phase descriptions need
no edits. No application, tests, dependencies or workflows change, no tests run
and no workflow is separately dispatched. Proposed/approved/actual message must
contain [skip ci]; the marker does not itself verify any workflow-run state.
No merge, deployment, whole-deliverable acceptance or new commit SHA is claimed.

## 4A.2 preparation and baseline reconciliation - 2026-11-10

The user authorized continued 4A.2 preparation and compatibility review. This commit
contains the narrowly scoped Start/restart request migration and its 12-test Node
regression file, with README and [task status](../todo/097-feedback-delivery-plan.md#4a2-preparation-and-baseline-reconciliation---2026-11-10)
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
