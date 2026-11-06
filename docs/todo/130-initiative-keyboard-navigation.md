# 130. Initiative keyboard navigation

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-013
- Status: in progress; agreed boundaries implemented, covering local/CI validation and user acceptance pending.
- Recorded: 2026-11-06. Boundaries and implementation requested: 2026-11-06.
- Priority, owner and deadline: not assigned.
- Coordination: follows completed 009.4/012 and precedes 009.5 in the agreed sequence.

## Approved behaviour

Within either Characters or Monsters, Tab moves to the next available initiative
editor and Shift+Tab to the previous, following displayed row order and skipping
unrelated row controls. Navigation does not cross roster boundaries or wrap. At
the first/last editor, native Shift+Tab/Tab resumes normal page navigation. The
user explicitly approved these boundaries before implementation. Hidden, disabled,
readonly, inert and negative-tabindex editors are excluded. Modified shortcuts and
composition are not intercepted.

Existing initiative change/save/validation and combat ordering remain authoritative.
Focus restoration after a same-scope table replacement follows combatant identity,
not an old row index. A draft typed in the destination while a preceding save
refreshes rows is retained. Already emitted changes are tracked to avoid replay;
a restored draft missing its native change emits one change on later blur through
the original delegated handler. There is no new network/save implementation.
Pointer/external focus, window blur, changed campaign/setup or a missing target
cancel restoration rather than move focus to another combatant or scope.

## Acceptance and validation

Verify forward/reverse navigation in both panels, displayed order after reorder,
normal first/last exit, no cross-panel jump/trap, single/empty/unavailable fields,
native save/rejection and save-triggered rerenders, draft retention, no duplicate
save, and access to other controls at desktop/narrow widths. Initiative validation,
permissions, API payloads and battle ordering must remain unchanged.

Executed preparation: JavaScript node --check and regression Python AST parsing
passed; all five isolated real-Chromium fixture methods passed, including
desktop/narrow traversal, boundaries, identity/draft restoration and exact change
counts. An intermediate duplicate-change fixture failed, then passed after
propagating already-attempted values across replacements. Full-Admin asset/save/
refresh/rejection regressions are prepared in the same test module, but have not
been executed during preparation. Existing CI discovery covers all seven methods.
Covering local/CI results and manual workflow acceptance remain pending; earlier
009.4/012 results do not validate this increment.

See [implementation and validation handover](../handover/320-initiative-keyboard-navigation.md).
