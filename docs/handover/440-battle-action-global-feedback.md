# 440 - Battle-action global feedback

[Back to handover index](../../HANDOVER.md)

## Initial checkpoint and evidence

Initial actor-specific eligibility/helper/relocation checkpoint:
00f065913d1068e4ed13df904cead507573f24eb. Published run 42881717311 attempt 1
and job 130059406530 succeeded for that SHA; publication
3b160730e444d028affd66a6379e5daaa952a467. This is not follow-up CI.
The complete initial scope, 16 regressions, five fault checks, original hashes,
legacy results and limitations remain in the [initial record](https://github.com/dajomas/Scrying-Glass/blob/00f065913d1068e4ed13df904cead507573f24eb/docs/handover/440-battle-action-global-feedback.md).

## Approved two-commit follow-up - 2026-11-10

The user approved two coherent writes, each with tests/docs and separate exact
approval. Commit 1 migrates active-target and living-target errors to independent
battle.actions.targets identities, plus actor-specific battle.actions.pending
info/matching resolution. Preserve eligibility, busy/lair/dead-actor gates,
modal-local feedback, payloads, applied rows, control restoration and explicit
retry. No automatic mutation replay. No server/markup/turn-helper changes here.

Commit 2 still required: start-of-turn completion success with encounter-ticket,
actor and modal-session guards; its tests and final status reconciliation.
It is not included in this commit. 4A.11 and both deliverables/009.7 remain open.

Core runtime/pins/legacy Apply changes are identical to the materialized follow-up:
complete 060/070/pair syntax and CJS checks passed; original blobs verified;
only two digests/total changed, with pin guard AST preserved. The prior combined
16-test suite passed with real controller/bootstrap, mock DOM/transport and fake
clock; legacy Apply/reaction passed against the temporary pair and verified
markup. Those results are not full-bundle or separate-commit CI evidence.
The new six-case core-only suite reuses the real-controller legacy fixture;
its separate execution remains pending. Normal configured CI discovers it.

060: 13,711 bytes, SHA-256
c0dd1752e624f3731c6b89d5821eeb79d0f930c2a8eb8d576fc0191935c45c78.
070: 19,250 bytes, SHA-256
68830a8efd3b02716c8253aeb24d4ac978d426880ce4438d1c7e0b0d4283a1ce.
Calculated total 117,318; six other fragments/order/admin.js marker untouched.
Full assembly/reader/isolation, initial eligibility/turn-helper reruns, combined/
browser, applicable manual/accessibility checks and covering CI review remain
pending. No live-server, renderer, delivery or acceptance claim. No workflow
edit/dispatch, merge, deployment or archive/Patch/. Roots reviewed, unchanged;
existing index still points here. [Task](../todo/097-feedback-delivery-plan.md#4a11-battle-action-global-notices---2026-11-10).
