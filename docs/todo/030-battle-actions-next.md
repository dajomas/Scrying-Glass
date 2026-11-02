# 030 - Next combatant from Battle Actions

[Back to TODO index](../../TODO.md)

## SG-TODO-003 - Add Next to the Battle Actions modal

- Status: in progress; implementation delivered in f9fa3c76b6f7c078b3d0a5c63679eea2892dff9a; script-order correction prepared, corrective CI/live validation pending.
- Requested: 2026-11-02. Implementation requested: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Initial preparation base: c858a92709c456c8a1c62e8a73e60614e469cfb6 on features/perplexity.
- Correction base/evidence snapshot: b2b2023417489d73796cff1e99381d8cc609bd18.

### Requested behavior and delivered design

Add a button labelled Next to Battle Actions, equivalent to Close, main Battle
Next, then clicking the new active participant. Discard pending actions, reactions
and statistics-reduction drafts without submitting them. Previously applied changes
remain committed and are not replayed or undone. Open the normal fresh actor screen
with current target/default/token context; do not copy old rows or selections.

The controller reuses closeBattleActions, the existing /api/battle/next endpoint,
load(true) and openBattleActions (including its lair delegation). Both Next buttons
share a same-browser operation guard and normal server turn rules. A fresh preflight
verifies encounter/actor context. After POST, refresh and a fresh state read must
agree with scope, returned actor, round and statistics token before reopening.
No separate next-participant algorithm or backend change is added.

Pending rows are not Apply or Apply-and-Next. Close retains its existing semantics.
Start-of-turn application and action/reaction/reduction submission block Next while
in flight, including their disabled-submit refresh interval. Next blocks new modal
submissions. Repeated clicks cannot issue overlapping Next requests through either
button. Action request tracking composes with the existing global request helper.

### Acceptance criteria (validation pending; not completed)

- [ ] Clearly labelled Next appears inside Battle Actions and is bound on the assembled page.
- [ ] All three old row types, actor/targets/amounts/critical/source/stat selections and applied markers clear through normal Close; the next screen uses fresh defaults/token.
- [ ] Pending rows are discarded; committed damage/healing/reactions/reductions are neither replayed nor undone.
- [ ] Advance occurs exactly once through normal progression, preserving rounds, eligibility and start/end-turn processing.
- [ ] Refreshed active indication/player updates and fresh normal action screen agree with authoritative state.
- [ ] Double-clicks and overlapping Apply/start-of-turn/Next requests are guarded.
- [ ] Failed or uncertain advance never retries automatically; reconcile state, report the outcome and leave the shortcut screen closed on error.
- [ ] Scope changes, stale actors, intervening turns, no active participant and lair turns do not reopen old HP controls or invent an actor.
- [ ] Close, Apply, main Next, reactions and statistics workflows retain their existing regression coverage.
- [ ] Review corrective CI and perform authenticated application/browser checks, including player display updates.

### CI diagnosis and correction - 2026-11-02

Inspected run 41522989190, attempt 1, against f9fa3c76b6f7c078b3d0a5c63679eea2892dff9a.
Evidence: ci-results-41522989190-attempt-1 at b2b2023417489d73796cff1e99381d8cc609bd18.
run.json reports overall failure: syntax/import, unittest/browser, pytest and
JavaScript steps succeeded, but the standalone step failed. Log chunk 000096
shows browser_smoke_272cc73.py reporting admin: request is not defined. That chunk
also records the audit's 953-test rerun as OK and zero unclosed connections out of
647. These successful isolated checks did not establish correct page boot.

The controller include appeared in fragment 180, before admin.js in fragment 190.
A parser-inserted deferred script sees readyState=interactive and immediately runs
install, which accesses request before the later Admin script exists. The correction
moves the include once to the end of fragment 190 after Admin/extensions. Existing
controller/turn logic and full-page smoke assertions are unchanged.

A new boot-order fixture uses the actual two fragments and real controller with
stub Admin helpers/other scripts. It passed locally with the corrected ordering,
including clicking the actual button and observing exactly one Next POST and the
new actor opening. Restoring the old ordering made the same fixture fail with
request is not defined. Python source compiled. This is parser/defer integration
coverage, not authenticated full-application validation. Corrective full CI remains
pending; the existing twelve interaction fixtures remain unchanged.

### Remaining validation and limitations

Deploy both changed HTML fragments, restart for imported markup and reload the
browser. Verify the new button actually advances in the running application.
Inspect normal corrective CI (no skip marker), including the unchanged complete
page smoke. Manually verify fresh start-of-turn controls/reminders, lairs, round
wrap, applied/pending reduction rows and connected player updates. Keep this task
open until acceptance evidence is reviewed.

Guards coordinate this browser's existing request-based controls; they are not
server-side idempotency or multi-administrator optimistic concurrency. The existing
Next endpoint is unchanged. Cross-client races are handled conservatively by not
reopening a screen when refreshed identity/scope/revision disagrees; no claim of
server-enforced exactly-once across clients is made.

See [implementation handover](../handover/210-battle-actions-next.md),
[attack statistics](../handover/180-attack-statistics-delivery.md) and
[restore layout](../handover/190-statistics-restoration-layout.md).
