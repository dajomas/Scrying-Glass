# 500 - Stage 2 select-dead feedback

[Back to handover index](../../HANDOVER.md)

## Implementation preparation - 2026-11-12

Prepared against ed6a211382d60110ecd008b19c4b88db46bd2bd3 (roll-all delivered,
combined validation pending). Scope is select-dead for both rosters only.
The effective bulk-select-all.js wrapper begins roster.select-dead before local
selection effects, targets characters/monsters independently and publishes explicit
pane success. Original count/plural wording and zero-result selection clearing
remain; zero is a completed local selection, not a request error. Success expires
after 3s. Matching outcomes and expiry preserve unrelated errors; stale tickets
cannot publish into another encounter and old timers cannot clear newer notices.
No request, refresh, combat/persistence/authorization, death-rule or selection-policy
change. Non-select-dead actions retain the original receiver/arguments/return.

## Preparation evidence and limits

The retained fixture keeps permanent-death, down/stable exclusion, monster death,
menu position, checkbox/set, pane-isolation, zero-result and select-all assertions.
It installs the production controller instead of collecting compatibility notices.
Twelve new cases cover identity/deadlines/isolation, matching recovery, replacement
timers, local state/transport boundaries, no-op/delegation and asset order. Combined
Node execution passed 13 tests (12 new cases plus the retained regression file),
zero failures/cancellations/skips. Three negative controls (shared target, info
instead of success, late ticket creation) failed; restored combined execution
passed. JavaScript syntax checks and exact source/base-identity checks passed.
Tests use the real controller with a scoped adapter and controlled DOM/timers,
not full Admin bootstrap/view, native-browser or live-server acceptance.

## Integration and remaining work

Only bulk-select-all.js's template reference advances from v=1 to v=2; script
count/order and core fragments/pins/failure marker are unchanged. Existing loaded
Admin composition assertions remain applicable. The index links this section;
[task status](../todo/098-character-edit-feedback.md#select-dead---2026-11-12)
tracks the bounded work. README and root TODO need no unrelated edits.
Per the user's Stage 2 staging instruction this mixed commit uses [skip ci],
without workflow edits or separate dispatch. Combined covering/browser validation
and acceptance remain pending until all Stage 2 changes/updates are pushed.
Bulk Join pane success and final Stage 2 reconciliation remain separate. No
compatibility retirement, test-suite cleanup, wider stage/deliverable/phase closure,
merge or deployment is included.
