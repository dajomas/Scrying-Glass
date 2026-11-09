# 336. Automatic and shared monster roll active-order updates

[Raw-roll integration](335-monster-raw-roll-integration.md) |
[Task SG-TODO-018](../todo/180-monster-initiative-bonus.md)

Prepared 2026-11-07 for features/perplexity-018. Task remains incomplete.
No merge or write-back authorized.

## Covering baseline

Run 42376308445 attempt 1 passed exact tested commit
39d26fa5c17b8935a414140573198ba7616a7332. Evidence was reviewed at
publication 95d1472a8b016a4de0059f4fb89d0507288fd153 under
ci-results-42376308445-attempt-1. The main suite reported 1,230 tests in
111.175 seconds OK; jobs.json reported all test/audit/cleanup steps successful.
Raw-roll composition, five mutation, nine rules and three UI methods were
explicitly inspected as OK. This is covering CI, not live-server acceptance.
Earlier failed evidence retains its original status.

## This increment

The active InitiativeEditMonstersMixin adds automatic-roll and shared-roll bulk
overrides. Automatic rolling still targets every roster monster, including
inactive entries. Shared rolling resolves only selected monsters using the
existing selected_entities path, including ID deduplication/not-found behavior.
Every non-shared bulk action delegates to the previous handler unchanged.
Existing Edit code is unchanged; no route, UI, schema or workflow changes.

The planner verifies target identities and all selected initiative fields before
any die is consumed. It samples one d20 per monster or one shared d20, then reuses
the strict raw-roll calculation/storage checks. It overlays every final candidate
before proposing a single stable order using the existing ordering helper.
This avoids changing tie-relative order through intermediate per-monster sorts.
Creature/lair initiative-20 tie behavior is retained.

All final calculations and order validation precede live-state updates. Existing
order membership is retained; inactive/outside-order targets are rolled but not
inserted or activated. No order is started when none exists. Turn owner, round,
character totals, health, activity and successor caches are not changed by this
rolling path. The handler commits fields/order then notifies once through the
existing transaction-wrapped route. Final overflow or order rejection can occur
after dice have been sampled; no random-generator rollback is claimed.
Malformed fields fail with 422, unsafe order proposals with 409, before live
mutation. Existing route transactions remain responsible for persistence and
rollback if notification/storage later fails.

## Validation and remaining work

All 15 pure planner methods passed locally against verified copies of the
existing calculation, raw-roll, ordering and lair modules. They cover independent
and shared dice, signed totals, selection isolation, stable final ties, lair
placement, unchanged state/membership/turn/round, empty/outside order, invalid
fields/targets/dice, late overflow and repeat replacement without compounding.
The original active mixin blob was verified and an AST comparison confirmed the
Edit method itself is unchanged. Prepared Python sources parsed successfully.

Six direct active-handler methods are prepared for automatic reorder, selected
shared-roll deduplication, missing targets, invalid bonus/order atomicity and
other-action delegation. They have not executed locally because FastAPI is
unavailable; no substitute framework was used. Normal CI applies with no skip
marker or separate dispatch; no new-stage full-suite/CI pass is claimed.

These checks do not prove authenticated HTTP, real persistence/restart, complete
assembled Admin rolling flows, or turn advancement after later removals/reorders.
Review covering CI and complete those lifecycle regressions. Source bonus
extraction, retained source identity, selected-monster refresh preview/apply and
remaining agreed SG-TODO-018 acceptance still follow. No task completion or
merge is implied by this incremental delivery.
