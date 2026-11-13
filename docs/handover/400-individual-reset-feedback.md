# 400 - Individual combatant reset feedback

[Back to handover index](../../HANDOVER.md)

## 4A.7 bounded acceptance and close-out - 2026-11-10

The user explicitly requested closing 4A.7 and updating documentation after reviewed
successful covering CI. 4A.7 is completed/closed for bounded character/monster
individual-reset feedback. Implementation ffcca4e9b85a9bc90ba39c495213de608b9a04c2
on features/perplexity-009.7 is covered by successful Branch tests 42852710398
attempt 1, published at 05324088a62b7db78b6cc8834593e9c4001972ac under
ci-results-42852710398-attempt-1. Reviewed run.json and jobs.json match the exact
implementation SHA and show successful syntax/import, Python/browser, pytest,
JavaScript and standalone browser/audit stages. Publication is not the tested SHA.

Acceptance covers persistent encounter-scoped combatant.reset errors with JSON
[kind,id] target isolation and submitted-name labels; silent matching-success
resolution before load(); unrelated/combatant/Reset All/End/load isolation; stale
scope/attempt suppression; and separation of successful mutation from refresh
failure. Preserve encoded/bodyless POST, existing server reset semantics, absence
of an individual-reset confirmation and existing delegated-handler precedence.
No automatic retry, success toast, new concurrency policy, bulk-reset/removal
migration or revocation of already-sent mutations is implied. The core-fragment
integration and corresponding identity/size expectation update are accepted for
this unit, not a general weakening of identity or fragment-bound contracts.

Preparation's 17 passing Node regressions, four detected negative controls and
restored-draft passes remain historical executed evidence. Final integration's
complete-fragment syntax, size/digest agreement, pin-file AST check and reverse
source comparison remain separate static evidence. Configured covering CI stages
subsequently passed. No new local test execution, individual-test CI log/assertion
review, authenticated live-server or manual test is claimed by this close-out.
Successful configured CI does not establish exhaustive rendering/browser/security/
accessibility coverage; final combined producer-specific Admin validation remains
open at Deliverable 1 level. Pending validation/acceptance wording in the historical
delivery section below is superseded by this record, not an invented extra run.
See the [completed task](../todo/097-feedback-delivery-plan.md#4a7-individual-combatant-reset-feedback---2026-11-10).

4A.1-4A.6 stay closed. 4A.8 global removal fallback feedback is the next proposed
bounded unit, not started by this close-out; later units remain proposed. Deliverable
1, Deliverable 2 and SG-TODO-009.7 remain open. SG-TODO-019, agreed delivery order,
priorities, owners and deadlines are unchanged. No full-deliverable/phase acceptance,
merge or deployment is included.

Only the existing task plan and this handover section change. Live instructions
were retrieved; complete current files reviewed: task blob
1a622836eed937396233786aedbeecd1a19ae234 and handover blob
c02d8123693c2257e1652446bfdac44e5ef6a695. README, root indexes and maintenance
rules retain accurate scope/links without edits; no index is touched merely for
status bookkeeping. No application/test/configuration/workflow changes, no tests
executed and no workflow separately dispatched. Proposed/approved/actual message
includes [skip ci], which does not itself establish workflow-run state. No new
documentation commit SHA is invented before delivery.

## 4A.7 preparation and delivery - 2026-11-10

Historical delivery follows; pending CI/validation/acceptance statements are
superseded by the bounded close-out above, not by a new local behavioral run.

Prepared at the user's finish/push request on features/perplexity-009.7, baseline
502cfafa24658cd2b6ca75c9cdbf202a8f51647d. [4A.7](../todo/097-feedback-delivery-plan.md#4a7-individual-combatant-reset-feedback---2026-11-10)
remains in progress pending covering CI/full-Admin validation and bounded acceptance.
No implementation SHA or passing covering run is invented before evidence exists.

Only 070-source.js gains resetCombatantWithFeedback and the two native r/cr reset
branches call it. Encounter-scoped combatant.reset targets are JSON [kind,id];
submitted names are captured for labels. Explicit persistent failures and silent
matching-success resolution are combatant-specific, distinct from Reset All/End/
load errors. Resolve before refresh; load() owns refresh errors. Reject stale/
superseded publication and old-scope post-response refresh. Scope guards do not
revoke already-sent mutations. Preserve encoded/bodyless POST, server reset rules,
current absence of individual-reset confirmation, and existing delegated-handler
precedence. No new success toast, automatic retry, concurrency policy, bulk-reset,
removal or other producer migration. Server code/templates/assets remain unchanged.

Historical focused preparation executed helper/click-slice and test syntax checks,
17 passing Node regressions with zero failures/skips, four detected negative
controls (success severity, collapsed target, removed stale guard, removed matching
resolution), and restored-draft 17 passes. Real controller/bootstrap and production
helper/delegated-click slices run with mocked DOM/network, including actual loadState
error handling with a rejected mock fetch; not complete Admin/rendering/live-server
or manual verification. No behavioral suite was rerun during final integration.

Final integration reconstructed original 070 exactly against Git blob
627e6e2e3586126e1f8ae6d9c81a8e60c69bac3a. The complete modified fragment passed
node --check; reverse comparison verified unchanged source except helper/two reset
branches. Size 19,437 UTF-8 bytes, below 20,000; new SHA-256
 a79eefbe4acf159e5fb52a8cb9bf2a2d8da1fe8d3a1c647a5def116dbcdcde7a.
Calculated complete assembled size is 115,006 bytes (606-byte increase), using
unchanged live sizes for seven other parts. Update only 070's digest and total size
in test_admin_source_preparation.py; Python AST parsing and digest agreement passed.
Its size/order/tamper tests remain intact; source-complete tests import the updated
expectations. Full assembled-bundle/reader/isolation tests, browser/combined suites
and covering CI remain pending, not claimed executed from these static checks.
Eight-part order, other pins and tracked admin.js failure marker remain unchanged.

Live instructions/read/write schemas and branch head were checked; prior complete
reads reused against unchanged identities. README/open phase and TODO index links
remain accurate without edits. Task plan replaces duplicated closed-unit narratives
with evidence-linked summary and retained incoming anchors; no open work is deleted.
Detailed history remains in 380/385/390 and the pre-4A.7 Git revision. Add this focused
handover to the existing index. Existing CI discovers the new .cjs and Python source
contracts; no workflow changes/dispatch. This mixed commit has no skip marker.
4A.1-4A.6 stay closed; 4A.8 onward stays proposed. Deliverable 1, Deliverable 2 and
SG-TODO-009.7 stay open. SG-TODO-019 and agreed delivery order are unchanged.
No merge, deployment or task/phase acceptance is included.
