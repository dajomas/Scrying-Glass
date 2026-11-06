# 130. Initiative keyboard navigation

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-013
- Status: in progress; wrapping and Escape exit implemented, covering local/CI validation and user acceptance pending.
- Recorded: 2026-11-06. Wrapping/Escape revision approved: 2026-11-06.
- Priority, owner and deadline: not assigned.
- Coordination: follows completed 009.4/012 and precedes 009.5.

## Current approved behaviour

Within Characters or Monsters, Tab moves to the next available initiative editor
and Shift+Tab to the previous in displayed row order. Last and first wrap to each
other in both directions. Navigation stays within the current roster and skips
unrelated controls and hidden/disabled/readonly/inert/negative-tabindex editors.
A single editor keeps focus on itself; empty rosters introduce no interception.
Modified shortcuts and composition are not intercepted.

Escape from an initiative editor focuses the roster's scroll region and clears
refresh restoration. Normal Tab/Shift+Tab navigation remains active within that
roster, allowing access to other row controls instead of immediately looping again.
Leaving the roster and re-entering, or pointer interaction, re-enables wrapping.
The user explicitly approved wrapping and Escape exit after finding the initial
native-boundary exit unintuitive. This supersedes the original non-wrapping rule
in initial implementation d23ee70d6beea3f6c5031f0102c27e5f537edbc8.

Existing change/save validation, permissions, API payloads and combat ordering
remain authoritative. Same-scope refresh follows destination combatant identity,
retains destination drafts and avoids replaying emitted changes. A restored draft
missing native change emits one change on later blur through the original handler.
Pointer/external focus, window blur, changed scope or a missing target cancel
restoration. No new network/save implementation is introduced.

## Validation and remaining acceptance

Executed correction preparation: node --check, regression AST parsing and all five
isolated real-Chromium fixture methods passed. Checks include both wrap directions,
1440/375 traversal, Escape focus, pass-through after Escape across rerender, normal
forward/reverse exit, re-entry, single/unavailable fields, draft identity/change
counts and cancellation. Three full-Admin methods are prepared, including new
wrapping/Escape/access-to-other-controls coverage plus retained asset/save/refresh/
rejection checks. Those full-Admin methods and the complete suite were not run
during preparation. Existing CI discovery covers all eight methods.

Covering local/CI results and desktop/narrow user workflow acceptance remain
pending. Results for the original non-wrapping revision would not validate this
correction. Earlier 009.4/012 results are not 013 evidence.
See [implementation and history](../handover/320-initiative-keyboard-navigation.md).
