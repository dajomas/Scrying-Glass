# 440 - Battle-action global feedback

[Back to handover index](../../HANDOVER.md)

## Initial 4A.11 checkpoint - 2026-11-10

Approved stage: shared helper, actor-ID eligibility error/matching resolution,
openBattleActions relocation, fixtures/tests/pins/docs. Other four notices remain
deferred: active targets, living targets, no pending actions, async start-of-turn
completion with scope/session safeguards. WIP, not complete 4A.11 or Deliverable 1.
Baseline: 9d05e129cc2b85099cf0e3bf394a1fe398d0af24 on features/perplexity-009.7.

battle.actions.eligibility persists; valid opening resolves only its actor error.
Busy/lair/dead-actor gates, modal/token initialization and combat/Apply behavior
are preserved. Move opening function from start of 070 to end of 060, preserving
assembled order/fixture extraction; helper is inside the fixture slice. Reverse
comparisons retain other 060 code and all 070 remainder. No deferred caller,
modal-local, server or battle-turn-actions.js changes.

Executed preparation: verified original Git blobs; full 060/070 and pair syntax;
16 new real-controller/bootstrap regressions, zero failures/skips; both legacy
Apply/reaction suites with original assertions and verified production markup;
five detected faults (severity, collapsed IDs, resolution, busy, lair guards),
restored 16 passes; changed CJS syntax and revised pin AST/guards preserved.
Mocked UI/transport, no renderer mounting; legacy runs used a temporary pair,
not the eight-part bundle. No browser/live-server/manual/accessibility claim.
Full assembly/identity/reader/isolation/combined/browser and covering CI review
remain pending. Normal CI; no workflow changes/dispatch or success claimed.

060: 13,337 bytes, SHA-256
957faf90d70b8b459ef97771e6bc12750cd476f7e8d69add7ada1320095262a1.
070: 19,053 bytes, SHA-256
7c62228bdffcc9deb43495fc9f7b59f59db599e23054e4a43d4efa077000c819.
Calculated total 116,747 (+557); only these two pins/total change. Other sources,
eight-part order and tracked admin.js marker unchanged. No delivery SHA invented.

Instructions/head/path checked; verified prior docs/source/test/workflow reads
reused. Reduced docs link preserved full criteria/history, not delete unfinished
work. README/TODO root unchanged. [Task/status](../todo/097-feedback-delivery-plan.md#4a11-battle-action-global-notices---2026-11-10).
4A.11 stays open; 4A.1-4A.10 closed, 4A.12+ proposed; both deliverables/009.7 open.
SG-TODO-019/order/009.6 gates unchanged. No archive/Patch/, merge or deployment.
