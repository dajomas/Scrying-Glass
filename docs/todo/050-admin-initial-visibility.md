# 050 - Initial Admin section visibility

[Back to TODO index](../../TODO.md)

## SG-TODO-005 - Hide already-active campaign/setup sections on initial opening

- Status: proposed/requested; implementation and validation not started.
- Requested: 2026-11-02.
- Priority, owner and deadline: not assigned.

### Requested behavior

On first opening of the Admin page:

- If a campaign is active, start with the campaign sections hidden.
- If a battle setup is active, start with the battle setup sections hidden.

Evaluate the two conditions independently using authoritative initial state. This
is an initial-visibility rule, not a request to hide sections again on every poll,
WebSocket update or render. Preserve the user's ability to show sections manually.
When a condition is false, leave existing visibility defaults unchanged unless
an additional policy is agreed.

### Implementation decisions to resolve

Identify the exact campaign and battle-setup pane groups in the installed UI.
Reconcile the requested initial defaults with any saved browser preferences;
the request does not define a new persistence policy or cross-page-session reset.
Do not treat a placeholder/default name as active state without checking its model.

### Acceptance and validation

- [ ] Active campaign initially hides its associated campaign sections.
- [ ] Active battle setup initially hides its associated setup sections.
- [ ] All four active/inactive combinations behave independently.
- [ ] Initial asynchronous loading does not produce a false active-state decision.
- [ ] Manual show/hide controls continue to work and later updates do not override them.
- [ ] Saved-preference interaction and the meaning of first opening are explicitly documented.

Add deterministic state/initialization checks and a browser test exercising real
first page load and subsequent refreshes. Distinguish mocked fixtures from full
running-server validation. No runtime visibility changes are made by this task entry.
