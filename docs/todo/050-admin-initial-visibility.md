# 050 - Initial Admin section visibility

[Back to TODO index](../../TODO.md)

## SG-TODO-005 - Hide already-active campaign/setup sections on initial opening

- Status: in progress; implementation/tests prepared, CI and live validation pending.
- Requested: 2026-11-02. Group scope and per-page behavior accepted: 2026-11-02.
- Preparation base: 6637a39ef21e0e035b849a7848ad0302c7ac7c33 on features/perplexity.
- Priority, owner and deadline: not assigned.

### Agreed behavior

On each initial opening/reload of the Admin page, evaluate the first complete
authoritative state once:

- An active campaign collapses Campaign setup and Character input.
- An active saved battle setup collapses Battle setup, Monster input and Lair input.
- Evaluate those conditions independently; otherwise preserve existing defaults.
- Leave Battle controls, Character display, Monster display and Activity log alone.

Reuse existing Show/Hide buttons and their visibility model. Already-hidden inputs
stay hidden rather than toggling open. The lair pane's existing has-lair gate still
applies; recording a collapsed preference must not reveal an unavailable lair pane.
Manual choices made before the initial response are respected for that pane.

First opening means once per page lifetime, not once per account/browser session.
No local/session storage or database preference is added. Subsequent polling,
loads, state renders and campaign/setup changes do not reapply the initial rule.
Users can show inputs normally. A reload starts a fresh initial decision.

### State and integration

Use active_campaign_id, not a dropdown selection or displayed campaign name.
An active_setup reference needs nonempty campaign_id/name strings; null means no
saved active setup. Missing/malformed initial state does not consume initialization.
The script loads after Admin/lair extensions, observes their existing state-render
hook and catches up from latest if the first load already completed. It performs
no new network requests or state mutations. Toggle labels/aria-expanded remain
synchronized through the existing toggle handlers.

### Acceptance criteria (pending completion)

- [ ] Both campaign inputs initially collapse when a campaign is active.
- [ ] All three setup inputs initially collapse when a saved setup is active.
- [ ] All four active/inactive combinations behave independently.
- [ ] Delayed/incomplete data is not mistaken for a final initial state.
- [ ] Manual choices, including choices before the response, are not overwritten.
- [ ] Later updates and scope changes do not recollapse inputs.
- [ ] Existing lair gating, display/log/Battle visibility and accessibility labels remain correct.
- [ ] Full assembled-page startup, initial state delivery and refresh preserve the behavior without new API mutations.
- [ ] Review CI and verify real first opening/reload plus manual Show/Hide in the deployed application.

### Validation evidence and remaining work

Eight focused Chromium tests passed locally, including the four-condition subtests,
cached initial state, invalid/incomplete state, subsequent scope changes, early user
interaction, hidden/already-collapsed panes, no-active initial state and duplicate
asset evaluation. They use the real new controller but stub pane handlers/state
renderers, not the entire application. New Python sources compile.

A ninth test assembles the actual Admin page, loads real scripts and uses intercepted
HTTP with a snapshot from the existing SQLite feature fixture. It checks all five
hidden properties/aria states, no initialization mutations and manual visibility
surviving load(true). This full-page fixture and the complete suite have not been
run locally; execution is pending normal CI. No green result is claimed.

Deploy the new script and updated fragment, restart for imported markup and reload.
Confirm the actual initial groups and manual toggles before closing. No backend,
configuration or migration changes are part of this task. See
[handover](../handover/220-admin-initial-visibility.md).
