# 180. Monster initiative bonus

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-018
- Status: proposed; user clarified the required behaviour on 2026-11-06. Implementation and validation have not started.
- Recorded: 2026-11-06
- Priority: not assigned; delivery-order placement remains undecided and existing sequencing is unchanged by this clarification.
- Dependencies: inspect current provider mappings, .monster import, persistence and initiative assignment paths during implementation planning.
- Related tasks: [initiative keyboard navigation](130-initiative-keyboard-navigation.md), [source-based monster selection](160-source-based-monster-selection.md), [Open5e integration](170-open5e-monster-source.md), [Admin delivery sequence](115-admin-delivery-sequence.md).

## Requested change and agreed scope

Support a separately stored monster initiative bonus, populated from the selected
monster source where available or entered manually. Support assignment through
both manual Add Monster and .monster import. The bonus can be negative, zero or
positive. Missing provider data is not a verified zero and must not be invented.

These calculation changes apply to monsters only. Characters announce their
already calculated roll-plus-bonus total; their Initiative editor continues to
accept that final total without additional calculation.

## User-agreed interaction and calculation - 2026-11-06

- Set the monster bonus during creation in the Add Monster section, through manual
  entry or .monster import. Source-derived values can be corrected manually.
- Display the assigned bonus read-only in the Monsters roster, between HP/Max HP
  and the initiative roll editor. Do not make the bonus editable in the row.
- Edit an existing monster's bonus only in the monster Edit modal.
- The monster initiative editor accepts the raw dice roll, not a bonus or a final
  total. Display the calculated total separately and use it for turn ordering.
- Calculate monster initiative total as raw roll + stored bonus exactly once.
  Each entered roll replaces the previous raw roll; calculate from that new roll,
  not from the previous total. Re-entering a value is equivalent to rerolling.
- Refreshing or reloading must preserve the assigned roll/bonus/total relationship
  and must not add the bonus again or cause a new roll.
- Saving a changed bonus in the Edit modal immediately recalculates the total
  from the existing raw roll and updates turn ordering. Changing the raw roll
  likewise updates the calculated total and order.
- Leave character initiative entry and calculation unchanged.

Examples supplied or confirmed during clarification:

| Action | Raw roll | Bonus | Final total |
|---|---:|---:|---:|
| Adult Blue Dragon example | 16 | +12 | 28 |
| Replace the roll with 10 | 10 | +12 | 22 |
| Enter 16 again | 16 | +12 | 28 |
| Refresh without editing | 16 | +12 | 28 |
| Save bonus change to +10 | 16 | +10 | 26 |
| Negative-bonus example | 16 | -2 | 14 |
| Zero-bonus example | 16 | 0 | 16 |

The Adult Blue Dragon modifier is the user's illustrative input, not an
independently verified provider mapping or edition-specific stat claim.

## Acceptance criteria

- Manual monster creation and .monster import support a separate initiative bonus.
- Available source bonuses can populate creation; manual correction remains usable.
- Positive, zero and negative bonuses have unambiguous signed presentation.
- The roster bonus is read-only in the agreed position; existing-monster bonus
  changes are made in the Edit modal, not inline.
- The monster row distinguishes editable raw roll from displayed calculated total;
  ordering uses the total. Every new roll applies the bonus exactly once.
- Bonus edits recalculate from the retained raw roll and update ordering on save.
- Refresh/save/reload does not compound the bonus, reroll or lose assigned values.
- The bonus and required roll/total data persist across saving, reloading and
  supported encounter/setup reuse.
- Character announced-total input receives no additional calculation or bonus UI
  changes from this task.
- Existing monsters remain usable after any required migration; existing stored
  initiative totals are not silently reinterpreted as raw rolls or modified.
- Shared/group initiative, tie handling and initiative keyboard navigation remain
  consistent with explicitly agreed semantics; unresolved cases below must be
  settled before implementing affected behaviour.

## Remaining implementation decisions and compatibility gates

The raw-roll versus final-total question and roster-versus-modal bonus editing are
settled above; do not reopen them as unspecified design choices.

Inspect how each provider and .monster format represents initiative modifiers.
Define handling of absent/invalid bonuses, including whether any derivation is
allowed; do not assume the bonus always equals a Dexterity modifier. Agree legacy
and missing-value defaults and migration representation without silently converting
existing final totals into raw rolls. Specify behaviour when the raw roll is unset.

Inspect existing automatic/shared initiative assignment. Agree how a shared raw
roll interacts with different monster bonuses and grouping; the user's clarification
does not decide those potentially conflicting semantics. Review tie resolution and
active-battle reordering so the required total/order update does not silently
advance turns or replace unrelated combat state. No raw-roll bounds, new dice
roller, manual final-total override or automatic fallback order is agreed here.

Coordinate provider mapping with SG-TODO-016/017 without making their delivery an
assumed prerequisite. No new provider capability is claimed by this clarification.

## Validation required

Prepare provider/import, persistence and initiative regressions covering explicit
source bonuses, missing values, manual entry/correction, .monster import,
positive/zero/negative modifiers, exactly-once application, repeated raw-roll entry,
bonus edits with an existing roll, refresh/reload, legacy records, shared initiative
and tie/order behaviour. Retain character final-total regression coverage.

Verify the agreed examples, read-only roster placement, Edit-modal-only bonus
editing, distinct raw-roll/total presentation and recalculation/order updates.
Manually verify creation, import, save/reload and desktop/narrow usability, including
Tab/Shift+Tab initiative navigation without adding an inline bonus editor.

## Delivery status

Requirements clarification only. Implementation, migration planning, tests and
validation remain outstanding. Placement in the delivery sequence is not changed
or approved by saving these clarifications.

This update changes only this existing task document. README, TODO index and
HANDOVER index were reviewed/reused and remain accurate without edits: current
runtime behaviour, task status and links are unchanged. No application code, tests,
imports, persistence or workflows change, and no new tests were executed. The
commit message includes [skip ci]; no separate workflow is dispatched or observed
workflow state inferred from that marker.
