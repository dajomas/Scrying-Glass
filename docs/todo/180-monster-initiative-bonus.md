# 180. Monster initiative bonus

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-018
- Status: in progress; implementation inspection started. Requirements agreed 2026-11-06; application changes, tests and validation remain outstanding.
- Recorded/updated: 2026-11-06
- Priority: next in the agreed remaining-work delivery sequence, before SG-TODO-009.5. No owner or deadline assigned.
- Dependencies: inspect provider mappings, .monster import, source identity, persistence, initiative assignment and refresh review paths.
- Related tasks: [initiative keyboard navigation](130-initiative-keyboard-navigation.md), [source-based monster selection](160-source-based-monster-selection.md), [Open5e integration](170-open5e-monster-source.md), [Admin delivery sequence](115-admin-delivery-sequence.md).

## Agreed scope and calculation

Support a separately stored monster initiative bonus, supplied by the selected
source where available or entered manually through Add Monster and .monster
import. Bonuses may be negative, zero or positive. Missing bonuses default to 0
and do not block manual or automatic rolling. Preserve the distinction between
a defaulted zero and an explicitly supplied zero internally; a default is not
evidence that a provider returned zero. Do not infer a bonus from Dexterity.
Reject malformed manually entered/imported bonuses rather than replacing them
with zero. Source-derived values remain manually correctable.

These calculation changes apply to monsters only. Characters continue to enter
their announced final initiative totals without any additional bonus calculation
or bonus UI.

- Set the bonus during creation in Add Monster or .monster import.
- Display it read-only in the Monsters roster between HP/Max HP and the raw-roll
  editor, with unambiguous signed presentation. No inline bonus editor.
- Edit an existing bonus in the monster Edit modal; the separately agreed reviewed
  source-refresh action can also replace it.
- The monster initiative editor accepts a raw roll. Display the calculated total
  separately and use that total for ordering.
- Calculate total = raw roll + bonus exactly once. Every entered roll replaces
  the previous raw roll, never the previous total.
- Refresh/reload preserves the relationship and neither rerolls nor compounds.
- Editing or refreshing the bonus with a retained raw roll immediately recalculates
  the total on save/apply and updates ordering.
- A known bonus without a raw roll leaves the calculated total unset, except for
  a preserved legacy total described below.
- Automatic individual rolls apply each monster's bonus. Shared initiative uses
  one shared raw d20 roll plus each selected monster's own bonus; totals and
  positions may differ. Equal totals retain the existing tie-resolution workflow.
- Reordering must preserve the current turn owner and round, without advancing a
  turn or replacing unrelated combat state. Retain initiative keyboard navigation.

## Agreed legacy compatibility

Existing monsters receive a default bonus of 0 without changing stored initiative
totals or inventing historical raw rolls. Distinguish a retained legacy total
from an unset raw roll in the roster. Setting or retrieving a bonus when no raw
roll exists preserves the legacy total. The next manual or automatic raw roll
replaces legacy state with the normal roll-plus-bonus relationship. Persist the
bonus, its default/source distinction, raw roll and legacy/total relationship
through save/reload and supported encounter/setup reuse.

## Agreed examples

| Action | Raw roll | Bonus | Total |
|---|---:|---:|---:|
| Adult Blue Dragon illustrative input | 16 | +12 | 28 |
| Replace roll with 10 | 10 | +12 | 22 |
| Enter 16 again | 16 | +12 | 28 |
| Reload without editing | 16 | +12 | 28 |
| Save bonus change to +10 | 16 | +10 | 26 |
| Negative bonus | 16 | -2 | 14 |
| Zero/default bonus | 16 | 0 | 16 |

The dragon modifier is user-supplied illustrative input, not a verified
provider/edition-specific statistic. With a shared roll of 16, bonuses +12, +3
and -2 produce totals 28, 19 and 14 respectively.

## Selected-monster source refresh - agreed 2026-11-06

Include a Refresh from source action in the existing monster bulk dropdown.
It acts only on monsters selected when the action opens, never the whole roster.
Disable it without a selection. One selected monster yields one review row;
multiple selections yield a per-monster review in one dialog.

Retrieve the original selected source record where its identity is available,
without silently substituting another edition/candidate. Without recorded source
identity, use the existing lookup/candidate-selection interaction and require a
selection before applying changes. Resolve candidate selection for its row and
return to the same review without losing other selections. No Open5e or new
source-selection capability is assumed; 016/017 remain separate tasks.

Show current and retrieved/proposed initiative bonus, AC, Max HP and Current HP,
plus each monster's source and lookup status. Each available field has its own
checkbox. Only checked fields are updated; all other values and all unselected
monsters remain untouched. Missing, invalid or failed retrievals are marked and
disabled; they must not overwrite existing values. In particular, a missing
bonus during refresh does not overwrite a previously assigned bonus with 0.

Current HP replacement is unchecked initially. Preserve current HP unless the
user explicitly selects its replacement. For a source supplying HP dice, show
the formula and generate one HP value only when applying an HP refresh, not
when opening/reviewing the dialog. Max HP and Current HP are independently
selectable; ensure coherent treatment when both use the same HP refresh value.

Use a grid on wider screens and equivalent per-monster cards within the same
dialog on narrow screens, not a one-monster-at-a-time wizard. A single Apply
selected changes button commits chosen changes; review/selection alone saves
nothing. Recalculate initiative using a retained raw roll, preserving legacy
totals when the raw roll is absent.

### Grid header selection

- Clicking a field column header selects all enabled checkboxes in that column.
- Clicking a monster row header selects all enabled checkboxes in that row.
- When all enabled checkboxes in that row/column are selected, clicking its header
  clears them; a partially selected header selects the remainder.
- Individual checkboxes remain independently selectable and deselectable.
- Skip disabled/missing/invalid/failed fields.
- Header controls expose unchecked, partial and checked states and support
  keyboard activation. Provide equivalent controls in the narrow layout.
- Current HP starts unchecked, but explicitly activating its column header or a
  row header can select an available Current HP replacement.
- Header controls change review selections only; Apply selected changes is still
  required. The review contains only the originally selected monsters.

## Acceptance criteria and required validation

- Cover manual creation/correction, explicit source bonuses, .monster import,
  missing default 0, explicit zero provenance and invalid input rejection.
- Cover positive/zero/negative bonuses, exactly-once application, repeated entry,
  automatic and shared raw rolls with different bonuses, and character totals.
- Cover bonus edits/refresh with and without a raw roll; legacy migration must
  preserve totals, with no invented roll, reroll or compounding on reload.
- Cover persistence, supported setup reuse/reset/import, tie resolution and
  ordering changes without turn/round advancement or unrelated state loss.
- Verify read-only bonus placement, Edit modal, distinct roll/total presentation
  and Tab/Shift+Tab navigation without an inline bonus editor.
- Cover original-source identity, missing identity/candidate selection, source
  failures, missing/invalid fields and isolation to the selected monsters.
- Cover per-field and bulk header selection/toggling, partial states, disabled
  skipping, independent overrides, keyboard controls and narrow cards.
- Cover no mutation during review, explicit Apply, current HP preservation by
  default, independent HP/Max HP choices and dice generation only on HP apply.
- Inspect refresh apply against changed/deleted monsters, campaign/setup changes
  and intervening edits so stale review cannot overwrite unrelated state.
- Prepare automated regressions and manually verify creation/import, refresh,
  save/reload and desktop/narrow usability. Report actual coverage limitations.

## Implementation work and delivery status

The user requested implementation on 2026-11-06. Initial live inspection covered
monster create/edit/update, individual/shared rolling, battle ordering, reset/setup
reuse and existing provider extraction. Further persistence/schema, imports, UI,
source identity, test and workflow inspection remains necessary before code
delivery. No new raw-roll bounds, manual total override or fallback ordering
is introduced by this agreement. Confirm actual provider representations through
code/fixtures; do not assume an initiative modifier equals Dexterity.

This update records agreed requirements and implementation commencement only.
It does not deliver the feature or claim passing tests. No application code, tests,
configuration or workflow changes are included. No tests were run for this
documentation update. The commit message includes [skip ci]; no workflow is
modified or separately dispatched, and no workflow state is inferred from it.
The later application/test delivery should run normal CI with separate exact
write approval, followed by review of user-provided result artifacts.

README and HANDOVER index were verified unchanged against their previously read
blob identities and remain accurate: no runtime delivery or new handover section
is claimed. TODO.md is updated to match this in-progress status. Historical
clarification commit da484d68d5ad39ef371ec8eeecb958149778fd8a preceded the
compatibility and source-refresh agreements recorded here.
