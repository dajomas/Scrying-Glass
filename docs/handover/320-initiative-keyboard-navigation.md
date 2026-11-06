# 320 - Initiative keyboard navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-013](../todo/130-initiative-keyboard-navigation.md).
Status: implementation included; covering local/CI and user acceptance pending.
Preparation base: a80a64ec29ad5c8bf3ca2e7220b3f150a8f0bd74 on features/perplexity.

## Decision and implementation

The user approved within-roster, displayed-row-order navigation without wrapping
or forced cross-panel movement. Tab/Shift+Tab skip unrelated controls only between
eligible initiative editors. At either boundary the event remains native, retaining
normal access to surrounding controls. Hidden/disabled/readonly/inert/negative-
tabindex fields are excluded; modified shortcuts and composition are untouched.

The deferred initiative-keyboard-navigation.js loads after character-hp-display.js.
It delegates keydown within each roster and observes only direct table replacement.
A navigation anchor stores destination combatant ID and campaign/setup identity,
so a save-triggered reorder restores the intended editor rather than a row index.
It restores only after the old editor disconnects and focus falls to the body or
region. Pointer interaction, external focus, window blur, changed scope or removed
destination cancel restoration. Local focus exposure continues through the existing
roster focus handlers. Installation is guarded against duplication.

Destination drafts survive a preceding save's rerender. WeakMaps track restored
drafts and values whose change was already emitted. If a restored draft did not
emit its native change, a microtask after blur emits one bubbling change through
the original handler; a native change clears that fallback. Attempt tracking is
propagated to replacement nodes to prevent replay or automatic retry of a rejected
value. No network code, replacement API or changed initiative validation/order is
introduced. The original delegated change handler remains the save authority.

Admin core fragments, marker, assembly identities, backend rules, permissions,
HP workflow and Turn-control removal remain unchanged. This is not 009.5 navigation.
Deploy the matching end fragment and full static tree, restart for assembled HTML,
and reload Admin browsers. No migration or dependency change is needed.

## Validation and limits

Executed node --check on the exact enhancement and Python AST parsing of the
regression module: passed. Five isolated Chromium unittest methods passed. They
cover both rosters, 1440/375 traversal, normal boundaries, idempotence, unavailable/
single/empty fields, modified-key noninterception, reordered refresh identity,
destination drafts, exact change counts, pointer/scope/deletion cancellation and
the one-missing-change fallback. An intermediate duplicate-change assertion exposed
a preparation defect; propagating attempted-value tracking corrected it, and all
five methods were rerun successfully. These are isolated DOM fixtures, not a
complete application or authenticated server.

The same new test module prepares two additional full-Admin methods: asset/order/
size contracts and original native change/PATCH, successful refresh with retained
destination focus, and rejected fractional initiative at 1440/375 for both rosters.
HTTP state and saves are intercepted, not real persistence or backend validation.
Those two methods and the complete application suite were not run in preparation.
Existing CI test_*.py discovery includes all seven methods without workflow edits.
CI-first delivery omits [skip ci]; no dispatch, triggered-run state or pass result
is claimed until evidence is reviewed. User manually publishes local/CI evidence.

User Guide documents the approved keys and boundaries; TODO index/task status and
HANDOVER index are updated. README was reviewed and remains accurate without edits.
The sequencing document's unresolved-boundary wording is historical; the explicit
approved decision is now recorded in the task and here. 009.4 and 012 remain closed;
013 remains in progress until covering results and user workflow acceptance.
