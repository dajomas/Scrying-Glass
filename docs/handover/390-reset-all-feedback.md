# 390 - Reset-all feedback

[Back to handover index](../../HANDOVER.md)

## 4A.6 preparation and delivery - 2026-11-10

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
