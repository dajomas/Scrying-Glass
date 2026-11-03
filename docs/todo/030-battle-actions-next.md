# 030 - Next combatant from Battle Actions

[Back to TODO index](../../TODO.md)

## SG-TODO-003 - Add Next to the Battle Actions modal

- Status: completed, 2026-11-02, at the user's request after verified successful corrective CI.
- Requested/implementation requested: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Initial implementation: f9fa3c76b6f7c078b3d0a5c63679eea2892dff9a.
- Script-order correction: 0759cc4b7bd78c4a7439c330d97c0661a6c4d864.

### Delivered behavior

Next in Battle Actions composes Close, the normal /api/battle/next progression,
authoritative refresh and the new active participant's ordinary action screen.
Pending action, reaction and statistics-reduction drafts are discarded without
submission; applied changes are not replayed or undone. Normal row defaults and
current actor/target/statistics-token context replace the previous drafts.

Both Next buttons share same-browser guards against overlapping action/start-of-turn
submissions and duplicate advancement. Preflight checks scope/actor. Refreshed and
fresh state must agree with the returned actor, round and statistics token before
opening. Existing lair delegation and no-active-participant behavior are reused.
Failed/uncertain responses reconcile without automatic POST retries. The server's
turn, eligibility, round, effect, persistence and broadcast rules are unchanged.

### Verification and close-out basis

Inspected ci-results-41525439558-attempt-1/run.json at evidence commit
b49c1068301c505331ec0836e53dbf8a583771c6. It records completed success for Branch
tests run 41525439558, attempt 1, against 0759cc4b7bd78c4a7439c330d97c0661a6c4d864
on features/perplexity. All configured execution steps succeeded: syntax/server
import, unittest/browser fixtures, pytest, JavaScript and standalone browser/audits.
The previously failing complete-page smoke is part of the successful standalone step.
No new test count or independently executed live scenario is inferred from metadata.

The user explicitly requested completion after this successful run. Closure is
recorded on that acceptance basis. Authenticated live/player-display validation
was not separately reported in this close-out request and is not claimed passed.
The earlier acceptance list's manual-validation requirement is not silently
relabelled as an executed test; this user-authorized CI-based close-out supersedes
the former pending status. Known limitations remain below and in the handover.

### Regression coverage and retained history

Twelve interaction fixtures cover row discard/fresh state, duplicate clicks,
Apply/start-of-turn guards, blocked submissions, returned round/lair routing,
no next actor, response loss, refresh failure, scope change, stale actor and main
Next. A thirteenth boot-order fixture covers parser/deferred initialization and
clicking the bound button. Existing Apply/reaction/reduction and backend progression
regressions remain unchanged. Mocked round results test composition, not a second
turn engine.

The initial failed run 41522989190 tested f9fa3c76. Its page smoke reported
request is not defined because fragment 180 loaded the controller before admin.js.
The correction moved the include exactly once to the end of fragment 190 after
Admin extensions. A local boot fixture passed with the correction and detected the
old ordering. Historical failed evidence was inspected at b2b2023417489d73796cff1e99381d8cc609bd18;
the verified successful corrective run above supersedes that failure for closure.

### Limitations and operation

Browser fixtures use mocked transport/helper boundaries, not full authenticated
application/player end-to-end coverage. Guards are same-browser coordination, not
server-side idempotency or cross-administrator optimistic concurrency. Unknown
cross-client races can prevent reopening; no rollback or globally exactly-once
claim is made. Deploy both HTML fragments and the controller, restart for imported
markup and reload browsers. No migration is required.

This close-out changes documentation only and runs no new application tests.
See [handover](../handover/210-battle-actions-next.md),
[attack statistics](../handover/180-attack-statistics-delivery.md) and
[restore layout](../handover/190-statistics-restoration-layout.md).
