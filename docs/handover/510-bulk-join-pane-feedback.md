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
