# 030 - Next combatant from Battle Actions

[Back to TODO index](../../TODO.md)

## SG-TODO-003 - Add Next to the Battle Actions modal

- Status: proposed.
- Requested: 2026-11-02.
- Priority: not assigned.
- Owner: not assigned.
- Deadline: not assigned.
- Implementation and validation: not started; this delivery records the request only.

### Requested behavior

Add a button labelled Next in the Battle Actions modal. One click should produce
the same result as the existing manual sequence:

1. Click Close in the Battle Actions modal.
2. Click Next in the Battle section of the main admin screen.
3. Click the new active combatant to open its action screen.

The shortcut clears the previous modal's action, reaction and statistics-reduction
lines, advances combat to the next combatant, and opens that combatant's action
screen. It must use the normal combat progression rather than introducing a
separate next-combatant algorithm.

### Pending and applied rows

Match the existing Close behavior: discard unapplied rows without submitting them.
Next is not Apply, Apply and Next, or Undo. Previously applied damage, healing,
reactions and statistic reductions remain committed; clearing their displayed
rows does not reverse them or apply them again.

Do not carry the old actor, targets, amounts, critical-hit selections, reaction
sources, statistics-reduction selections, applied-row markers or stale concurrency
tokens into the next action screen. Open a fresh screen with the same initial
rows/defaults as clicking the new active combatant normally; it need not remain
literally empty if that existing click normally creates an initial row.

### Acceptance criteria

- [ ] The Battle Actions modal contains a clearly labelled Next button.
- [ ] Clicking it clears the old action, reaction and statistics-reduction rows.
- [ ] Pending rows are discarded, not silently applied; already committed changes
  remain intact and are neither replayed nor undone.
- [ ] Combat advances exactly once using the same rules and side effects as the
  main Battle section's Next button, including normal round wrapping, eligibility
  handling and end/start-of-turn processing.
- [ ] After a successful advance, the new active combatant's normal action screen
  opens with fresh actor/target context and current state/token/defaults.
- [ ] The visible active-turn indication and player display follow the existing
  successful Next behavior; the UI does not show the previous actor as current.
- [ ] Repeated clicks or overlapping Apply/Next requests cannot double-advance,
  duplicate applied actions or open a stale/wrong actor's screen.
- [ ] A failed or uncertain advance is reported; the shortcut does not blindly
  retry, skip another turn or pretend the advance succeeded. Refresh/reconcile
  authoritative state before deciding which action screen to show.
- [ ] No active/next combatant, encounter scope changes, and special active
  participants use the existing main-Next plus active-click behavior rather than
  inventing an actor or opening stale HP controls.
- [ ] Close, Apply, standalone main-screen Next, reaction resolution and statistics
  reduction workflows remain covered by regression tests.

### Dependencies and implementation considerations

Inspect the installed attack-statistics implementation, not just the original
attachment: it now contains statistics-reduction rows and applied-row locking.
Reuse the existing close, advance, refresh and active-combatant open paths where
appropriate, preserving their transaction, authorization, concurrency and
notification behavior. This is UI composition of normal turn progression, not a
new attack-resolution rule, reset, restoration operation or initiative policy.

During implementation, explicitly verify:

- Disable/guard Next while Apply or turn advancement is in flight, and prevent
  double-clicks from advancing twice.
- Refresh authoritative state after advancing before choosing the next actor.
- Scope changes during a request must not reopen another campaign/setup's stale
  actor. Use the existing identity/turn/token protection where applicable.
- Lair turns and terminal/no-next situations should follow the current normal
  Next and active-click paths, including their appropriate action UI or no modal.
- Preserve normal start-of-turn fields/defaults and reminders rather than copying
  drafts from the previous actor.

These are implementation/validation considerations derived from the requested
three-step equivalence, not a claim that new guards already exist. Do not assign
an owner, priority or deadline without agreement.

### Validation plan

Add deterministic interaction tests for the shortcut sequence, all three row types,
pending-row discard, applied-row non-replay, fresh next-actor state and round wrap.
Cover repeated clicks, Apply in flight, advance/refresh errors, uncertain responses,
no eligible next actor, special participants, and campaign/setup changes while
awaiting a response. Reuse existing turn/initiative/effect regressions; add backend
coverage only if implementation changes server behavior. Verify actual modal
behavior and player updates in a browser against a running server, distinguishing
mocked checks from authenticated live validation.

No application code, new runtime button or automated application tests are
implemented by this TODO entry. Required implementation tests above remain planned.

### Related documentation

See [TODO tracking handover](../handover/100-todo-tracking.md) for this documentation
addition, [attack statistics delivery](../handover/180-attack-statistics-delivery.md)
and [restore layout correction](../handover/190-statistics-restoration-layout.md)
for the preceding archive-delivered context. The latter features are separate from
this proposed shortcut.
