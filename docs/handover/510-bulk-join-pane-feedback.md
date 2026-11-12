# 510 - Stage 2 bulk Join pane feedback

[Back to handover index](../../HANDOVER.md)

## Implementation preparation - 2026-11-12

Prepared against ab730d4498ac1e7a4cadb321ea8f391f45a60eef. Only the effective
late bulk-Join wrapper in initiative-join-gate.js changes. The single-row patch,
click gate, fetch ownership and ownedJoin global rejection/resolution code are
unchanged. A rejection still has one global roster.join owner, not a pane duplicate.
Server/client initiative, authorization and combat rules are unchanged.

Confirmed bulk success now uses roster.bulk.join-battle in the relevant pane,
with target JSON of roster kind and canonically sorted selected IDs. Preserve the
original POST/header/JSON payload order, count fallback/plural wording and ownership
symbol. Success precedes strict load(true) and expires after 3s. A persistent
roster.bulk.join-battle.refresh error distinguishes an applied Join from a failed
reload and instructs reload rather than mutation replay. Matching refresh success
resolves only its own error. Nonempty selection resolves only matching empty-selection
validation. Empty selection and non-Join paths retain core delegation.

Pending ownership spans mutation plus refresh for each canonical roster/selection;
reordering selection cannot duplicate a request. Independent targets/rosters remain
independent. Encounter/global-owner/pane-ticket/refresh guards suppress obsolete
results, and old finally cleanup cannot delete a newer pending owner. Existing
scope changes cannot revoke already-sent server mutations. No automatic retry.

## Evidence and limits

The revised retained core/Join suite has 37 cases (26 retained, 11 added), and the
unchanged gate suite has 12: combined execution passed 49 tests, zero failures,
cancellations or skips. Four removed-guard negative controls (duplicate protection,
rejection ownership, strict reload and pane supersession) each failed; restored
combined execution passed 49/49. Handler/test syntax and exact reverse replacement
checks passed. The base asset and retained test match their live Git blob identities;
the production controller matches c4a82d73b21f4657da651ce45f76003c3348a6ef.

Tests execute the complete gate asset with the production controller, a scoped
adapter, deterministic timers and mocked DOM/transport. Local core functions were
reconstructed as production-derived request/roster/patch slices from the complete
live 010 read, not a locally verified full Admin bundle. In repository execution
the suite extracts those functions from actual 010. This is not full Admin bootstrap,
native browser, authenticated live-server or exhaustive accessibility acceptance.

Retained assertions still protect one rejection, error formatting, gate rules,
response preservation, payloads, stale scope and single-row behavior. Only the
bulk-success destination and bulk-refresh outcome assertions change for the intended
policy. No production core fragment, size/digest pin, script count/order, template,
other asset or workflow changes. The existing unversioned gate URL remains; existing
per-response HTML cache busting supplies fresh _cb tokens. Reload the Admin page.

## Delivery boundary

The index links this section and the existing Stage 2 task records its status.
README/root TODO links remain applicable without unrelated edits. Use [skip ci]
for this intermediate push, as requested; do not modify or separately dispatch CI.
Combined covering/full-Admin/browser validation and bounded acceptance remain pending
until the Stage 2 batch is pushed and tested. Final Stage 2 reconciliation follows;
no compatibility retirement, other-stage/D2 work, deferred test cleanup, phase close-out,
merge or deployment is included.
[Task status](../todo/098-character-edit-feedback.md#bulk-join-pane-success---2026-11-12).

## Final Stage 2 reconciliation - 2026-11-12

Reviewed revision: 09c2f0912c77efdeffcd00f007470aae57b80622. All named Stage 2
implementation groups are accounted for: candidate selection/pending submit, source
review, shared roster/row patches, creation/.monster import, CSV/saved-setup import,
character Edit, monster raw-roll/Edit, roll-all, select-dead and bulk Join pane
success. No further planned handler migration was identified in this bounded review.
This reconciles source/delivery records, not runtime acceptance. The current
[Stage 2 task record](../todo/098-character-edit-feedback.md) supersedes stale
prepared/unfinished wording without reopening or deleting delivered work.

The eight ordered fragment metadata sizes sum to 126,506 bytes, matching the pin;
each is <=20,000 bytes (largest 010: 19,772). The failure marker remains intact.
Candidate/review/raw-roll/select-dead asset references are v=2, and character Edit
still precedes monster Edit. The last three steps changed no script count. These
are metadata/source checks, not a fresh content-hash/assembly/tamper/runtime run.
Older inactive import code and pane compatibility remain outside this retirement
scope; effective later bindings and the late Join owner are deliberately retained.

This reconciliation adds one case to the existing complete-Admin intercepted-HTTP
fixture: select-dead, roll-all and bulk Join coexist with an unrelated Reset error;
selection remains local, Join rejection is single-owned, successful Join/failed
refresh has separate guidance, drafts/selections survive, and read-only reload does
not replay mutation. The complete original fixture matches Git blob
f2bcba1c811792ff27d57b63aa4774f2456cc863. All 15 existing class method ASTs are
unchanged; four existing browser scenarios and five inventory tests are retained.
The new fifth browser scenario and full module compile successfully. All five
inventory tests passed in AST-isolated execution without importing browser/server
fixtures. No browser scenario or full suite was executed during this preparation.
The earlier focused 15/13/49 passes are historical, not a new combined result.

Implementation is delivered through 09c2f091. Final test/status integration is
prepared; combined validation and bounded acceptance remain pending. The green
cd1599e7 run 43150070549 attempt 1 does not cover the later ed6a211/ab730d4/09c2f091
batch. After this reconciliation is committed, validate committed HEAD, for example
with bash runlocaltests.sh --suite all --no-publish. That runner excludes uncommitted
drafts and the flag prevents automatic Git publication. Review completed evidence
for the exact final SHA before acceptance; never use an older rerun as coverage.

This mixed test/documentation commit retains [skip ci] as requested. No runtime,
asset, template, pin, workflow, dispatch, merge, deployment, compatibility retirement
or test-suite cleanup change is included. README and root index links remain
applicable; no new handover section file or index entry is needed. Stage 2, both
feedback deliverables and 009.7 stay open pending their existing acceptance gates.

## Stage 2 bounded close-out - 2026-11-12

Completed and closed for the agreed Stage 2 scope. After the successful final
local evidence review, the user explicitly accepted Stage 2 and requested its
close-out on 2026-11-12. This supersedes historical pending Stage 2 wording in
this section and earlier checkpoints; it does not reopen accepted 4A.1-4A.13 or
close Stage 1, Stages 3-4, either whole feedback deliverable or 009.7.

Final tested revision: c7dce86f810e78858e361ac87cd7b9a8a5788deb. Local run
run-20261112T054019Z-4vJTEQ is published at
a65c0ed4240ad78868cab7cf3e79f132ad3da46a under
local-tests-c7dce86/run-20261112T054019Z-4vJTEQ. Reviewed environment.txt identifies
the exact committed revision, suite=all, completed=1, Python 3.14.7, Node v22.23.2,
a detached local clone, start 2026-11-12T05:40:19Z and finish 05:57:40Z.
exit-code.txt is 0. All 77 summary command invocations exit 0: syntax/import,
unittest including browser fixtures, selected pytest, 66 discovered JavaScript
files and seven standalone scripts. These invocation counts include helpers and
are not unique individual-test counts. This is local execution of the configured
CI-command suite, not a hosted GitHub Actions run.

Direct log review confirms the new test_stage2_selection_roll_all_and_bulk_join_feedback_coexist
and all four retained complete-Admin browser scenarios are marked ok, as are all
five inventory checks. Visible source/assembly/fragment identity/size/tamper/reader/
runner/static-adapter checks pass. Roll-all 15/15, select-dead feedback 12/12,
core/Join 37/37 and retained gate 12/12 pass with no failures/cancellations/skips
in those reviewed Node suites. The 247,723-byte Python log was truncated by the
connector; no exhaustive tail review, total Python-case count or suite-wide
zero-skips claim is made. Summary-level all-suite success and direct critical
composition evidence satisfy the accepted Stage 2 automated gate. No corrective
implementation is indicated by reviewed results; separate hosted success is not
required in addition to this accepted equivalent local covering run.

Accepted scope includes candidate/pending-submit and source-review feedback,
shared roster/row patches, creation/file/CSV/setup imports, character/monster Edit,
raw-roll/roll-all, select-dead and bulk Join pane success with global reporting
preserved. Prior failed runs remain historical failures, not relabelled successes.
No new authenticated live-server/provider, human visual/manual combat, screen-reader
or exhaustive accessibility exercise is inferred from fixture success. The user
accepted the bounded scope on these stated evidence limits, not fictional checks.
[Accepted task status and preserved wider boundaries](../todo/098-character-edit-feedback.md#stage-2-close-out---2026-11-12).

This close-out is documentation only with [skip ci]. It executes no new tests,
changes no runtime/test/template/asset/pin/workflow files and dispatches no workflow.
README and HANDOVER links remain applicable without edits; TODO root and the two
relevant Stage 2 task records are reconciled in the same close-out. Other stages,
D2, wider phase acceptance, compatibility retirement and deferred test cleanup
remain separate. The Stage 2-only implementation skip instruction is not a blanket
skip for future unrelated work. No merge, deployment, owner/deadline/priority/order
change or future external-write approval is included.
