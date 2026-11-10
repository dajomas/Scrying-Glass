# 440 - Battle-action global feedback

[Back to handover index](../../HANDOVER.md)

## Initial checkpoint and evidence

Initial eligibility/helper/relocation checkpoint:
00f065913d1068e4ed13df904cead507573f24eb. Published run 42881717311 attempt 1
and job 130059406530 succeeded for that SHA; publication
3b160730e444d028affd66a6379e5daaa952a467. This does not validate follow-up commits.
[Complete initial scope, tests, faults and limits](https://github.com/dajomas/Scrying-Glass/blob/00f065913d1068e4ed13df904cead507573f24eb/docs/handover/440-battle-action-global-feedback.md).

## Approved follow-up commit 1 - 2026-11-10

Delivered at 272cfd73aa4c39602ed2dad96c1bd2e02ba28348 on features/perplexity-009.7:
independent active/living target errors and matching resolution, actor-specific
no-pending info, core regression file, legacy Apply assertion migration and pins.
The combined-state covering run is reviewed below. The six-case core-only suite
remains in the repository unchanged by commit 2; that run reports six passes.
[Complete commit-1 preparation evidence and limits](https://github.com/dajomas/Scrying-Glass/blob/272cfd73aa4c39602ed2dad96c1bd2e02ba28348/docs/handover/440-battle-action-global-feedback.md).

060 remains 13,711 bytes, SHA-256
c0dd1752e624f3731c6b89d5821eeb79d0f930c2a8eb8d576fc0191935c45c78;
070 remains 19,250 bytes, SHA-256
68830a8efd3b02716c8253aeb24d4ac978d426880ce4438d1c7e0b0d4283a1ce.
Calculated eight-part total 117,318; commit 2 does not alter fragments/pins/order
or the tracked admin.js marker. The six other fragments remain untouched.

## Approved follow-up commit 2 - 2026-11-10

This change set adds start-of-turn completion feedback through
battle.actions.turn-completion with encounter-ticket, actor and modal-session
ownership checks before post-request and post-refresh UI effects. Only the
existing no-longer-eligible completion becomes global success with controller-
owned five-second expiry. Still-eligible success, validation, request errors and
applied-but-refresh-failed messages remain modal-local. Damage-before-healing,
critical_hit false, request payloads, duplicate-submit locking, control-state
restoration, critical-field relocation and observer behavior remain unchanged.
No automatic mutation replay, server, markup, core-runtime or pin changes.

The turn helper is the exact materialized draft: 5,797 UTF-8 bytes, SHA-256
980473f4b5447bc6efcc5653dd806277aebd8786ae4197ff40f203e65b1f2bf7.
The new combined regression file is the exact previously materialized/tested
16-case suite: six core cases plus ten turn cases, including scope/session/actor
staleness, scope change during refresh, completion/expiry/payloads, local failure
paths and duplicate suppression. Commit-1 core tests are not replaced or removed.

Executed materialization evidence: original replaced blobs and read-only
controller/bootstrap/fixture/markup identities verified; complete changed core
fragments/pair, turn helper and CJS syntax passed; pin Python compilation and
unchanged guard AST passed. Combined suite: 16 passed, zero failed/skipped, with
real production feedback controller/bootstrap, mock DOM/transport and fake clock.
Legacy Apply/reaction passed against the temporary changed pair and verified
markup. The earlier draft's local test-double result was not real-controller
validation; its refresh-entry race was fixed with an explicit fixture barrier,
not a production change. These are prior focused preparation results, not new
CI, renderer, full-eight-fragment, browser or authenticated live-server results.

Current instructions/head verified; verified complete prior reads reused. README
and TODO root remain accurate and unchanged; HANDOVER index/status reconciled.
Normal configured CI discovers the new CJS file. No workflow edit/dispatch, skip,
archive/Patch/, merge or deployment. Commit 2 delivered at
6e4bdd54f73df70bdb263493bf010ef3f0e9a0ad; covering failure reviewed below.

## Remaining validation and acceptance

Review covering CI tied to the follow-up implementation SHA(s), including both
new suites and initial eligibility, legacy Apply/reaction and turn-helper tests.
Full assembly/identity/reader/isolation and relevant combined/browser checks,
applicable manual/accessibility evidence and explicit bounded acceptance remain
required. The complete eight-part bundle was not assembled/executed during
materialization. Preparation/push or earlier green CI alone does not close 4A.11.
Both feedback deliverables/009.7 and unrelated acceptance gates remain open.
[Task/status](../todo/097-feedback-delivery-plan.md#4a11-battle-action-global-notices---2026-11-10).

## Failed covering CI and selection-fixture correction - 2026-11-10

Run 42891311319 attempt 1 (job 130092877349) covers
6e4bdd54f73df70bdb263493bf010ef3f0e9a0ad and failed in JavaScript tests.
Publication: 4923005f720e6e95cfabb7de549178565047af0c;
ci-results-42891311319-attempt-1/run.json and jobs.json agree. Python/import,
unittest/browser-fixture, pytest and standalone browser/audit steps report
success; that is step metadata, not exhaustive per-test or visual review.

Lossless workflow reader file-000038/part-000155.txt identifies
battle-action-selection.test.cjs:84: ReferenceError: window is not defined,
from battleActionFeedback during addBattleActionRow. The legacy VM setup did
not install the production feedback dependency. Log chunks 150 and 152-156
also verify core feedback 6/6, eligibility 16/16, combined follow-up 16/16,
reaction and turn-helper passes. These passes do not make the run green.
The complete JavaScript step has not been exhaustively reviewed for other faults.

Correction: import the existing installFeedback fixture, initialize it before
production VM evaluation, expose its API to the test and assert no unexpected
feedback records or legacy-route use in all three selection scenarios. Every
original selection/required-placeholder/request assertion is retained unchanged.
No application runtime, shared fixture, markup, fragment/pin or workflow change.

Executed correction checks: original selection-test blob verified; reproduced
missing-window failure using a focused production-function extraction; corrected
selection suite passed with real controller/bootstrap and mocked DOM/transport;
removing bootstrap installation reproduced the failure, then restoration passed;
corrected CJS syntax passed. An added draft deep-array comparison initially failed
across VM realms; only that new check changed to length === 0, followed by passes.
This was a test-assertion correction, not a production defect. The first mutation
probe retained an undefined returned feedback binding; the probe was adjusted to
remove it and reproduce the original missing-window path. Original assertions
remain intact.

Local checks used selected production functions, not a complete assembled Admin
checkout, mounted renderer, browser or authenticated live server. Related suites
were not rerun locally in this correction session; their cited results are from
the failed CI run. Fresh exact-content approval, actual corrective delivery and
normal covering CI/rerun review are required. No corrective SHA or green result
is invented. 4A.11 acceptance remains blocked; wider scope/order stays unchanged.
