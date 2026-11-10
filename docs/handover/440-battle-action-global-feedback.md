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
Its covering CI has not been reviewed. The six-case core-only suite remains in
the repository unchanged by commit 2; no separate execution pass is invented.
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
archive/Patch/, merge or deployment. Actual delivery identity must come from the
successful approved write; no commit-2 SHA or CI result is invented here.

## Remaining validation and acceptance

Review covering CI tied to the follow-up implementation SHA(s), including both
new suites and initial eligibility, legacy Apply/reaction and turn-helper tests.
Full assembly/identity/reader/isolation and relevant combined/browser checks,
applicable manual/accessibility evidence and explicit bounded acceptance remain
required. The complete eight-part bundle was not assembled/executed during
materialization. Preparation/push or earlier green CI alone does not close 4A.11.
Both feedback deliverables/009.7 and unrelated acceptance gates remain open.
[Task/status](../todo/097-feedback-delivery-plan.md#4a11-battle-action-global-notices---2026-11-10).
