# 334. Existing monster Edit initiative ordering

[Roster bonus](333-monster-initiative-roster-bonus.md) |
[Task SG-TODO-018](../todo/180-monster-initiative-bonus.md)

Updated: 2026-11-07. Task incomplete on features/perplexity-018.
No merge or write-back authorized.

## Baseline and reason for this prerequisite

Covering run 42358468973 attempt 1 passed exact tested commit
6872ae04464a7da13162cbf578d87200b0318f53. Evidence publication is
bbd31ce5a5278a5b56ecfd6fa0e730fd0502546e with
ci-results-42358468973-attempt-1. The inspected main-suite log reports 1,197
tests in 102.625 seconds OK; jobs.json reports all test/audit/cleanup steps
successful. Earlier roster-layout failures remain failed evidence.

The planned raw-roll transport/UI iteration exposed an existing prerequisite:
insert_into_battle_order returns for already-present monsters. Recalculating an
existing monster total in Edit therefore did not reorder that monster. This
bounded iteration repairs that path before raw-roll API/UI integration; it does
not claim to deliver the coordinated raw-roll feature.

## Scope

A pure helper proposes a stable order using the existing creature/lair initiative
key. It retains membership and tie-relative order and does not mutate the state.
A target outside the order leaves it unchanged; an empty order is not started.
Missing/ambiguous participants and duplicate order IDs reject a needed reorder.

The active Edit handler computes the proposal only when its total changes,
before image saving or live-monster mutation. It then applies the candidate and
order within the existing route transaction, retaining existing insertion/cleanup
and notification hooks. The helper does not advance turns, change round/turn
flags, alter character totals or invent raw rolls. Existing Edit health logic
and successor bookkeeping remain; this is not a rewrite of those behaviors.
A legacy total retained during a bonus-only edit does not trigger a reorder.

No new endpoint, request field, UI, schema, auto/shared-roll path, keyboard rule
or workflow change is included. Raw-roll and broader active-order acceptance
remain outstanding. Normal CI applies, no skip marker or separate dispatch.

## Checks and limits

All 11 pure ordering methods passed locally against the final helper and the
verified original lair-rules module. They cover increases/decreases, stable ties,
lair tie placement, unchanged state/turn/round/membership, empty/outside order,
invalid identities and unset totals. The retrieved original Edit handler blob
was verified and the changed handler parsed successfully.

Three direct-handler methods are prepared for real bonus recalculation/order,
legacy-total preservation and invalid-order rejection before image/state effects.
They reuse the existing direct Edit fixture but have not run locally because
FastAPI is unavailable. They are not authenticated HTTP, persistence/restart or
production battle-turn tests. No full-suite/new-stage CI pass is claimed. Review
covering results and continue coordinated raw-roll API/total UI, auto/shared order
updates, source refresh and remaining agreed validation before completing 018.
