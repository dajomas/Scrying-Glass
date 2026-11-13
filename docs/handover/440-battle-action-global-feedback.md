# 440 - Battle-action global feedback

[Back to handover index](../../HANDOVER.md)

Current status: completed and closed for the accepted bounded 4A.11 scope on
2026-11-10. The final close-out section below supersedes earlier pending-status
notes, not historical failures or evidence limitations. Wider deliverables stay open.

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

## Attack-statistics fixture correction - 2026-11-10

Selection correction delivered at 886056da5f03beb750f2f620b2f02f26e73150f3.
Covering run 42894039107 attempt 1 (job 130102316599) tested that SHA and failed
in JavaScript; publication bd38e92f564eb7a2d22b174a3f9896e66095da9d. The newer
lossless workflow chunk file-000038/part-000155.txt confirms selection now passes;
core 6/6, combined follow-up 16/16, reaction and turn-helper passes were also
observed. Earlier pending selection-delivery notes are historical, not green CI.

The newer part-000148.txt identifies attack-statistics.test.cjs:75:8:
ReferenceError: window is not defined, in battleActionFeedback called by
addStatisticsReductionRow. This is another legacy VM lacking the production
feedback bootstrap. This change adds exactly two lines to that test: import
installFeedback from battle-action-feedback-fixture.cjs and call it immediately
before VM evaluation. The whole existing test body/assertions remain byte-for-
byte unchanged, including statistics-token propagation, reductions/amounts,
ordered mixed batches, applied-row locking/no replay, close/cancellation, seven
choices, markup and character restore-control location. No new mock, bypass,
application, shared-fixture, markup, fragment/pin or workflow changes.

Executed preparation: verified original attack-test Git blob
 e10518835f2f6e729acc56d4d91d1d62fc51a9e9; exact reverse-edit comparison confirms
only the two installation lines differ; complete corrected CJS node --check
passed. Full attack-statistics test and related suites were not run locally in
this correction session; complete assembled checkout/dependencies were not
reconstructed. Syntax/review is not a behavioral pass. Normal configured CI
already discovers this test and must execute the complete original assertions.

The remaining JavaScript output/consumer audit is not complete; no claim this
is the only remaining failure. Exact-content approval, corrective delivery and
covering rerun review remain required. Both failed runs remain failures. 4A.11
acceptance and all wider gates stay open. README/HANDOVER/TODO indexes reviewed
and unchanged: paths and conservative pending-acceptance summaries remain valid.
No archive/Patch/, skip, workflow dispatch, merge or deployment.

## 4A.11 bounded close-out - 2026-11-10

Status: completed and closed for the explicitly accepted bounded scope. After
automated evidence reconciliation, the user explicitly accepted 4A.11 with the
stated evidence limits and requested close-out/push on 2026-11-10 at 21:45 CET.
This is not inferred from a push or a green status alone. Earlier pending or
blocked notes above describe their historical stage and are superseded for this
accepted unit; neither failed runs nor unperformed checks are relabeled as passed.

Accepted scope: actor-specific eligibility feedback/matching resolution;
independent active/living target errors/matching resolution; actor-specific
no-pending information; start-of-turn completion success and stale encounter,
actor and modal-session safeguards. Existing payloads, modal-local behavior,
busy/duplicate guards, applied rows and explicit retry/no replay are retained.

Final tested implementation including both repairs:
1b621c3909e751affc356fbbb98acc53a3f588e3. Attack-statistics repair delivered in
that commit; selection repair is 886056da5f03beb750f2f620b2f02f26e73150f3.
Successful covering Branch tests run 42896405201 attempt 1, job 130110564256,
reports headSha matching that final revision and completed/success in run.json
and jobs.json. Evidence publication: 477583dc63a6f88d7161bef913a27ca7a931f374;
source directory ci-results-42896405201-attempt-1/. Both implementation stages
272cfd73aa4c39602ed2dad96c1bd2e02ba28348 and
6e4bdd54f73df70bdb263493bf010ef3f0e9a0ad are included in the tested state.
Runs 42891311319 and 42894039107 remain failed historical runs; immutable earlier
publication snapshots preserve their evidence after latest-result rotation.

Detailed log evidence reconciled at reader-chunks/file-000038/ in the successful
publication (part numbers below are not individual test counts):
- 148-149: attack-statistics and legacy Apply file passes; core suite 6 passes.
- 149-152: eligibility suite 16 passes, zero failures/skips.
- 152-154: combined follow-up 16 passes, zero failures/skips, including completion/
  expiry/payloads, stale scope/session/actor, refresh failure and duplicate guards.
- 154-155: corrected selection, reaction and turn-helper file passes.
- 025: full assembled syntax/identity, reader bounds, runner isolation, pinned
  fragment identities/sizes/syntax and tamper guard, adapter serving/refresh/wiring.
- 021-022: browser loading/rendering, scope/retry/deadlines, safe text, dismissal/
  focus recovery, live-region structure, independent records and narrow wrapping.
- 023-026: relevant workspace/009.6, nested overlays, original controls/drafts/files,
  selection/visibility, native Next/history, focus/idempotence and navigation.
- 030: observed deferred-boot/reaction compatibility entries.
These are direct named-test results, beyond run/step metadata. The combined suite
includes overlapping core cases; no sum is presented as unique requirements.
The prior local full-assembly uncertainty is resolved by covering CI, not by
pretending the local check occurred. Targeted log passages were read; no complete
raw-log reconstruction, exhaustive log audit or visual-artifact review is claimed.

Acceptance limits retained: focused JavaScript tests use real production feedback
controller/bootstrap with mock DOM/transport and fake clocks; browser fixtures
add automated loading/rendering/workflow coverage. No new authenticated live-server
exercise, human visual/manual combat workflow, screen-reader test or exhaustive
accessibility/zoom/contrast acceptance was supplied or established. User acceptance
is explicitly bounded to the delivered unit on the reconciled evidence, not a
claim that those unperformed checks ran. Wider validation gates remain open.

This close-out is documentation-only: no runtime/test/pin/asset/workflow change,
new automated test execution or CI dispatch. Commit message contains [skip ci];
no new workflow outcome is inferred from that marker. Root README and TODO index
remain accurate and unchanged; HANDOVER status/link and task section reconcile
only this unit. No archive/Patch/, merge or deployment. 4A.12/4A.13, Deliverables
1/2, phase 009.7, SG-TODO-019 and agreed delivery order retain their existing
statuses and criteria. [Closed task](../todo/097-feedback-delivery-plan.md#4a11-battle-action-global-notices---2026-11-10).
