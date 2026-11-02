# 030 - Next combatant from Battle Actions

[Back to TODO index](../../TODO.md)

## SG-TODO-003 - Add Next to the Battle Actions modal

- Status: in progress; implementation and regression tests prepared, CI/live validation pending.
- Requested: 2026-11-02. Implementation requested: 2026-11-02.
- Priority, owner and deadline: not assigned.
- Preparation base: c858a92709c456c8a1c62e8a73e60614e469cfb6 on features/perplexity.

### Requested behavior and delivered design

Add a button labelled Next to Battle Actions, equivalent to Close, main Battle
Next, then clicking the new active participant. Discard pending actions, reactions
and statistics-reduction drafts without submitting them. Previously applied changes
remain committed and are not replayed or undone. Open the normal fresh actor screen
with current target/default/token context; do not copy old rows or selections.

The prepared controller reuses closeBattleActions, the existing /api/battle/next
endpoint, load(true) and openBattleActions (including its lair delegation). Both
Next buttons share a same-browser operation guard and the normal server turn rules.
A fresh preflight verifies encounter/actor context. After POST, refresh and a fresh
state read must agree with scope, returned actor, round and statistics token before
opening anything. No separate next-participant algorithm or backend change is added.

Pending rows are not Apply or Apply-and-Next. Close retains its existing semantics.
Start-of-turn application and action/reaction/reduction submission block Next while
in flight, including their disabled-submit refresh interval. Next blocks new modal
submissions. Repeated clicks cannot issue overlapping Next requests through either
button. Action request tracking composes with the existing global request helper.

### Acceptance criteria (validation pending; not completed)

- [ ] Clearly labelled Next appears inside Battle Actions.
- [ ] All three old row types, actor/targets/amounts/critical/source/stat selections and applied markers clear through normal Close; the next screen uses fresh defaults/token.
- [ ] Pending rows are discarded; committed damage/healing/reactions/reductions are neither replayed nor undone.
- [ ] Advance occurs exactly once through normal progression, preserving rounds, eligibility and start/end-turn processing.
- [ ] Refreshed active indication/player updates and fresh normal action screen agree with authoritative state.
- [ ] Double-clicks and overlapping Apply/start-of-turn/Next requests are guarded.
- [ ] Failed or uncertain advance never retries automatically; reconcile state, report the outcome and leave the shortcut screen closed on error.
- [ ] Scope changes, stale actors, intervening turns, no active participant and lair turns do not reopen old HP controls or invent an actor.
- [ ] Close, Apply, main Next, reactions and statistics workflows retain their existing regression coverage.
- [ ] Review normal CI and perform authenticated application/browser checks, including player display updates.

### Prepared tests and actual validation

Twelve Chromium fixture tests use extracted production action helpers, the real
modal template and the new controller with mocked progression/transport. They cover
row discard/fresh state, duplicate clicks, Apply/start-of-turn guards, blocked
submissions, returned round/lair routing, no next actor, response loss, refresh
failure, scope change, stale actor and standalone main Next. Round/eligibility/effect
engine behavior remains covered by existing backend regressions, not a mocked new
turn algorithm. Full configured CI must confirm compatibility with those suites.

Five limited local controller checks passed using stub close/open/render/transport
helpers: success, overlapping Next clicks, uncertain response, scope change and
refresh failure. Both fresh-screen success and safe closed-screen failure behavior
were checked. Python test source compiled. The complete twelve-test fixture and
full application suite have not been executed locally. No green CI is claimed.

### Remaining validation and limitations

After approval, push with normal CI (no skip marker), inspect results and repair
failures through the approved feedback workflow. Manually verify fresh start-of-turn
controls/reminders, lairs, round wrap, applied/pending reduction rows and connected
player updates against an authenticated running server. Keep this task open until
acceptance evidence is reviewed.

Guards coordinate this browser's existing request-based controls; they are not
server-side idempotency or multi-administrator optimistic concurrency. The existing
Next endpoint is unchanged. Cross-client races are handled conservatively by not
reopening a screen when refreshed identity/scope/revision disagrees; no claim of
server-enforced exactly-once across clients is made.

See [implementation handover](../handover/210-battle-actions-next.md),
[attack statistics](../handover/180-attack-statistics-delivery.md) and
[restore layout](../handover/190-statistics-restoration-layout.md).
