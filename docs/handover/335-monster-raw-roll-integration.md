# 335. Prepared raw-roll API and roster integration

[Edit ordering](334-monster-initiative-edit-order.md) |
[Task SG-TODO-018](../todo/180-monster-initiative-bonus.md)

Prepared 2026-11-07 for features/perplexity-018. Task remains in progress.
No merge or write-back authorized.

## Baseline

Run 42359242384 attempt 1 reports success for exact tested commit
c77299c6a21ed19d18e0af8128201e47e4aff2d8. Its run.json was read at evidence
publication 8b7cb106ba21830a2eea3c596541685bd37e247e under
ci-results-42359242384-attempt-1. This verification is run-level metadata,
not a new audit of individual counts or logs. Prior failures retain their status.

## Scope of prepared patch

Adds PATCH /api/monsters/{ident}/initiative-roll under the existing AdminAPI
registration, admin dependency, same-origin guard, serialized ownership checks
and transaction wrapper. The body accepts only initiative_roll, an integer or
null. It reuses initiative_patch, preserves assigned bonus/origin, replaces the
previous raw roll and adds the bonus once. Raw/total storage bounds are signed
64-bit, not gameplay limits. Explicit null clears an inactive monster's raw and
total; clearing an active monster is rejected before mutation.

The raw mutation proposes stable ordering with the existing helper before
changing live state. It preserves membership, character totals, turn flags,
round and unrelated monster fields; it does not insert or activate participants.
Existing route transactions own rollback and persistence. Those transaction and
authorization properties still require runtime verification for this new route.

A deferred roster module wraps monsterRow before future table replacement,
setting raw defaultValue for serialization and keyboard draft tracking. It also
decorates already-rendered rows. The same data-mi hook is retained. A distinct
read-only output shows the authoritative total, marking retained legacy totals
without inventing a raw roll. The existing seven-column structure and separate
bonus column remain. Characters retain final-total behavior.

Monster change events stop before the old document-level final-total handler
and send only initiative_roll to the new endpoint. Reload does not roll or
calculate in the browser. Invalid/inexact browser input is not sent; raw values
not exactly representable in JavaScript are read-only/unavailable. Server
validation remains authoritative. Null initial state is handled. Failed refresh
after a successful save is distinguished from rejected mutation.

## Tests and limits

Nine pure rules tests, two static route/asset tests and three real Chromium
fixture tests passed locally, 14 total in the final run. The fixtures cover
raw/total separation, legacy display, request shape, character-event isolation,
integer rejection, null initial state and Tab/Shift+Tab/Escape draft restoration
using the verified existing navigation script. Node syntax checks passed.
Five direct mutation tests are prepared but not executed locally: FastAPI is
unavailable. Eight existing navigation test methods are retained; the assembled
save fixture now expects monster raw-roll payloads and the new path, while
character expectations remain unchanged. Its server-rejection case uses a valid
integer for monsters so the request still reaches the intercepted rejection.

No authenticated live HTTP, full assembled Admin, persistence/restart or complete
suite run is claimed. Review covering normal CI after committing. Automatic and
shared rolling already calculate raw plus bonus but their broader active-order
updates remain outstanding. Legacy total APIs remain a compatibility bridge.
Source extraction/selected-monster refresh and remaining agreed acceptance are
not delivered by this patch. No workflow changes or separate dispatch included.
