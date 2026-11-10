# 390 - Reset-all feedback

[Back to handover index](../../HANDOVER.md)

## 4A.6 bounded acceptance and close-out - 2026-11-10

The user explicitly requested closing 4A.6 and updating documentation after review
of successful covering CI. 4A.6 is completed/closed for Reset-all feedback only.
Implementation 13ec059da5114f69c5f7613e186f7fb8789c8475 on features/perplexity-009.7
is covered by successful Branch tests 42842153909 attempt 1, published at
3b2a379af3b0fdc403a61e02698066b3f511c2a8 under ci-results-42842153909-attempt-1.
Reviewed run.json and jobs.json match the exact tested SHA and show successful
syntax/import, Python/browser, pytest, JavaScript and standalone browser/audit
stages. The evidence-publication commit is not the tested implementation SHA.

Acceptance covers persistent battle.reset-all request errors, silent matching
success resolution before load(), unrelated-error isolation, cancellation behavior,
stale scope/attempt suppression and separation of successful reset from refresh
failure. The original confirmation, bodyless POST, empty-order availability and
server reset semantics remain intact. No automatic retry, success toast, new
concurrency policy or individual combatant reset migration is included. Scope
checks do not revoke an already-sent mutation.

Preparation's two syntax checks, 16 passing focused Node regressions, three detected
negative controls and restored-draft passes remain historical executed evidence.
Covering configured CI subsequently passed. This close-out claims no new local
execution, individual-test log/assertion review, authenticated live-server or
manual test, and no exhaustive browser/rendering/accessibility validation. Pending
CI/acceptance wording in the historical delivery section below is superseded by
this record. See the [completed task](../todo/097-feedback-delivery-plan.md#4a6-reset-all-feedback---2026-11-10).

4A.2-4A.5 stay closed; 4A.1's formal status, SG-TODO-019 and agreed delivery order
are unchanged. Deliverable 1, Deliverable 2 and SG-TODO-009.7 remain open. 4A.7
individual combatant reset feedback is the next proposed bounded unit, not started
by this close-out. No full-deliverable/phase acceptance, merge or deployment.

Only the existing task plan and this handover section change. Live instructions
were read; complete prior contents were reused against verified identities:
task b68f9594a840c8452c75f3c99dcadb0fa154048a and handover
9352f33fbc50e052423b255164a3c149dbbf0331. README/root indexes and maintenance
rules retain accurate scope/links without edits; no index is touched merely for
status bookkeeping. No application/test/configuration/workflow changes, no tests
executed and no workflow separately dispatched. Proposed/approved/actual commit
message includes [skip ci]; that marker does not itself establish workflow state.
No documentation commit SHA is invented before the write succeeds.

## 4A.6 preparation and delivery - 2026-11-10

Historical delivery follows; pending CI/validation/acceptance wording is superseded
by the bounded close-out above, not a claim of new local executions.

At the user's request, prepare and deliver the bounded Reset All feedback migration
on features/perplexity-009.7. Baseline: accepted 4A.5 close-out
beb0f9431671d64993b489916b9e353bf55850ae. The [4A.6 task](../todo/097-feedback-delivery-plan.md#4a6-reset-all-feedback---2026-11-10)
remains in progress pending covering CI/full-Admin validation and bounded acceptance.
No new implementation SHA or passing CI run is invented before delivery/evidence.

The 978-byte admin-reset-all-feedback.js enhancement replaces only Reset All's
onclick after the existing End enhancement. It captures an encounter-scoped
battle.reset-all ticket after the unchanged confirmation, before the existing
bodyless POST. Request errors use explicit persistent error severity. Matching
success silently resolves only its request error before load(); refresh errors
remain owned by state.load. Cancellation, refresh alone and unrelated success do
not clear the error. Scope/attempt guards reject stale feedback and post-response
refreshes in another encounter, including away/back transitions. They do not revoke
an already-sent server mutation. Preserve empty-order availability, one POST per
confirmed invocation and existing reset semantics. No new success toast, automatic
retry, concurrency policy or individual combatant reset migration is introduced.

Executed during preceding preparation: two JavaScript syntax checks passed;
16 Node regressions passed with zero failures/skips; three temporary negative
controls were detected (success severity for errors, removed stale-success guard,
removed matching resolution); restored draft passed all 16 again. These are not
new executions during final delivery review. Complete handler, real controller and
complete Admin bootstrap execute with mocked DOM/network. A refresh-failure case
uses actual loadState handling with a rejected mock fetch and nonexecuted renderer;
this is not full browser/rendering, authenticated server or manual verification.
Full browser/combined suites and covering CI remain pending. Existing normal CI
discovers the new .cjs; no workflow changes or separate dispatch are needed.

Unchanged controller/bootstrap/template reconstructions matched live Git blobs
c4a82d73b21f4657da651ce45f76003c3348a6ef,
59553fdd9fc93ac8d23f3ea54536aded1a945ab5 and
178e76771d2bf3e9af02cb75a3d3c00602b1baaa before draft integration. The test fixture
is 9,580 UTF-8 bytes. Live instructions and write schemas were retrieved, branch
head verified unchanged, and complete prior reads reused against that baseline.
Core source, bundle pins/marker, server code and prior tests stay unchanged.
README and TODO index retain accurate open-phase scope/links without edits. This
dedicated handover section is linked from the existing index; earlier planning,
implementation and acceptance history remains unchanged in [380](380-feedback-delivery-plan.md).
No history is removed or task closed by this mixed normal-CI commit. 4A.2-4A.5
remain closed; 4A.1's formal status, SG-TODO-019 and delivery order are unchanged.
Deliverable 1, Deliverable 2 and SG-TODO-009.7 stay open; 4A.7 onward stays proposed.
No merge, deployment or phase acceptance is implied.
