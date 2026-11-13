# 382 - Start feedback history

[Back to handover index](../../HANDOVER.md) · [Feedback continuity index](380-feedback-delivery-plan.md)

Historical text preserved from the pre-split 380 record. Dated pending-status
notes describe their original checkpoint, not current acceptance or CI status.
See the [current task plan](../todo/097-feedback-delivery-plan.md) for current work.

<!-- BEGIN preserved 380 content -->
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

<!-- END preserved 380 content -->
