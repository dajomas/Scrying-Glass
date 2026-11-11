# 383 - Next and End feedback history

[Back to handover index](../../HANDOVER.md) · [Feedback continuity index](380-feedback-delivery-plan.md)

Historical text preserved from the pre-split 380 record. Dated pending-status
notes describe their original checkpoint, not current acceptance or CI status.
See the [current task plan](../todo/097-feedback-delivery-plan.md) for current work.

<!-- BEGIN preserved 380 content -->
## 4A.5 bounded acceptance and close-out - 2026-11-10

The user explicitly requested bounded acceptance after successful covering CI was
reviewed. 4A.5 is completed/closed for End-battle feedback only. Implementation
2b358c7b963640b393fa91875bcfc574c9885ab3 on features/perplexity-009.7 is covered
by successful Branch tests 42833154095 attempt 1, published at
b545b2749d1ccf2390b63ce9d3731570db54710e under ci-results-42833154095-attempt-1.
Reviewed run.json and jobs.json agree on that exact implementation SHA and show
successful syntax/import, Python/browser, pytest, JavaScript and standalone
browser/audit stages. The evidence publication is not the tested source SHA.

Acceptance covers persistent operation-specific validation/request errors,
confirmed-valid validation resolution, matching-request success replacement,
unrelated-error isolation, stale scope/attempt suppression and separation of
successful End from subsequent load-owned refresh failure. The existing empty-order
gate, confirmation and non-resetting request/server behavior are preserved. No
Reset All migration, automatic POST retry or new concurrency policy is accepted.

Preparation's two syntax checks, 15 passing focused Node regressions, three detected
negative controls and restored-draft passes remain historical executed evidence.
The later covering configured CI success is separate evidence. This close-out
claims no new local execution, individual-test log/assertion review, authenticated
live-server or manual test. Historical delivery-time pending validation/acceptance
wording below is superseded by this bounded close-out, not a claim of additional
coverage. See the [completed task](../todo/097-feedback-delivery-plan.md#4a5-end-battle-feedback---2026-11-10).

4A.2/4A.3/4A.4 stay closed; 4A.1's formal status, SG-TODO-019 and agreed delivery
order are unchanged. Deliverable 1, Deliverable 2 and SG-TODO-009.7 remain open.
4A.6 Reset-all feedback is the next proposed bounded unit, not started by this
close-out. No whole-deliverable/phase acceptance, merge or deployment is implied.

This update changes only existing TODO/handover sections. Complete previously
approved contents were reused after live blob identities matched implementation
2b358c7b963640b393fa91875bcfc574c9885ab3: task
cd1541ae266ad5d9bbb3175de22f7cde8d17ff4b and handover
e26fbf614c82cf45bac032481176ef2d0838e67b. Live instructions were retrieved;
README, root indexes and maintenance rules retain accurate open-phase scope/links
without edits. No application/tests/configuration/workflow changes or new test
execution; no workflow separately dispatched. Proposed/approved/actual commit
message includes [skip ci], which does not itself verify a workflow-run state.
No documentation commit SHA is invented before delivery.

## 4A.5 End-battle feedback delivery - 2026-11-10

Historical preparation/delivery follows. Pending validation and acceptance wording
is superseded by the bounded close-out above.

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

<!-- END preserved 380 content -->
