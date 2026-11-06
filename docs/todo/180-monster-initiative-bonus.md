# 180. Monster initiative bonus

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-018
- Status: in progress; foundation/reset have covering CI; compatibility fixture repair delivered with covering CI unreviewed; state-normalization increment prepared with 20 passing component tests, full integration/validation outstanding.
- Updated: 2026-11-06
- Working branch: features/perplexity-018 until user sign-off; no merge/write-back to features/perplexity without fresh approval.
- Priority: next before SG-TODO-009.5 in the [agreed sequence](115-admin-delivery-sequence.md). No owner or deadline assigned.
- Related: [initiative navigation](130-initiative-keyboard-navigation.md), [source selection](160-source-based-monster-selection.md), [Open5e](170-open5e-monster-source.md).
- Delivery/evidence: [handover](../handover/330-monster-initiative-foundations.md).

## Agreed initiative contract - 2026-11-06

Monsters have a separate negative, zero or positive initiative bonus. Manual Add
Monster and .monster import must support it; source values can populate creation
and remain manually correctable. Missing bonuses default to 0 without blocking
rolling. Internally distinguish defaulted zero from explicit zero; do not invent
provider evidence or infer initiative from Dexterity. Reject malformed manual/
import values. Characters keep their announced final totals with no bonus UI
or additional calculation.

The monster roster shows read-only signed bonus between HP/Max HP and the editable
raw-roll input, plus a separate calculated total used for ordering. Existing bonus
edits belong in the Edit modal, not inline, with reviewed source refresh another
explicit replacement path. Each new raw roll replaces the old roll. Apply the
bonus exactly once; saving a bonus change with a retained roll recalculates total
and order. Reload never rerolls or compounds. An unset raw roll has no calculated
total except for a retained legacy total.

Existing totals remain unchanged when missing bonuses default to 0; never invent
old raw rolls. Distinguish legacy totals from unset roll inputs. Changing/retrieving
a bonus without a roll preserves a legacy total; the next manual/automatic roll
establishes roll-plus-bonus. Persist bonus/origin, roll and legacy/total semantics
through reload and supported setup reuse. Shared rolling uses one shared d20 raw
roll plus each selected monster's own bonus, so totals/positions can differ.
Retain tie resolution and initiative keyboard navigation. Reordering must preserve
current turn owner, round and unrelated state without advancing turns. No new
raw-roll bounds, new dice roller, manual final-total override or fallback order
was agreed; existing final-total API compatibility is temporary until UI integration.

Examples: raw 16 plus +12 gives 28; replace raw with 10 gives 22; enter 16 again
or reload gives 28; edit bonus to +10 gives 26. Raw 16 plus -2 gives 14, plus 0
(including default) gives 16. Shared raw 16 with +12/+3/-2 gives 28/19/14.
The Adult Blue Dragon +12 input is illustrative user input, not a verified
edition/provider statistic.

## Agreed selected-monster source refresh

Add Refresh from source to the monster bulk dropdown, disabled without selection.
Capture only the originally selected monsters, never the entire roster. Retrieve
the original selected source identity without silently substituting another
edition/candidate. Without retained identity, use existing lookup/candidate
selection and require selection before applying. Resolve candidates per row and
return without losing other review selections. Verify actual provider formats;
016/017 remain separate, not prerequisites or newly delivered capabilities.

One desktop review grid, with equivalent narrow-screen cards, shows per-monster
source/status and current-to-proposed initiative bonus, AC, Max HP and Current HP.
Each available field has an independent checkbox. Missing/invalid/failed retrievals
are marked and disabled and never overwrite existing values. A missing refreshed
bonus does not replace an assigned bonus with 0. Apply only checked fields for
originally selected monsters; preserve all other values and unselected monsters.
Current HP starts unchecked and changes only when explicitly selected. Show HP
dice formulas during review and generate one value per monster only on HP apply,
not on open/review. Current HP and Max HP are independent; selecting both uses
one generated value. One Apply selected changes commits choices. Review/header/
checkbox operations mutate no live state. Refreshed bonuses recalculate only
with an existing roll; legacy totals remain unchanged without one.

Column headers select all enabled cells in their column; row headers select all
enabled cells in their row. Clicking an already fully selected header clears its
cells; a partial selection selects the remainder. Individual checkboxes remain
independently selectable/deselectable; skip disabled fields. Expose unchecked,
partial and checked states with keyboard activation and narrow-layout equivalents.
Explicit row or Current HP header selection may select Current HP despite its
initial unchecked default. Apply remains required.

## Delivered work and covering evidence

Foundation 539697fabdde7e564b198104739870760032d638 added pure modules and 32 helper
tests with user-requested [skip ci]. Reset/setup increment
44e5c7640007601f801858d740dfdf66ab61e541 clears stale current rolls, preserves
bonus/origin and restores original totals as legacy. Snapshots preserve current
relationships; import retains HP/Max HP, new IDs and copy isolation. Characters
remain unchanged. No storage implementation/schema change was needed.

CI 42302058360 attempt 1 succeeded against exact 44e5c764. Evidence publication:
88461cc2891a935e541e881884ef6b1a6fabde5b, ci-results-42302058360-attempt-1.
Verified 1,112-test main suite OK, pytest 43 passed, all 22+16 dedicated Python
and ten selection methods passed, repeated audit OK with 689 opened connections
and zero without explicit close. All steps succeeded. Repeated execution is not
another unique test set; fixture/live-server limitations remain in the handover.

Handler compatibility 4e7128eb3e5349c186f0a80d34031031762a3d89 adds legacy-final-total
edit compatibility and individual/shared raw-roll calculation. It did not wire
state normalization or raw-roll UI. Seven direct-handler methods passed in CI,
but full workflow 42304851642 attempt 1 failed against that exact commit.
Publication: ea9804a2ebf43fc26bdb2554601f0d8923518933, folder
ci-results-42304851642-attempt-1. Main suite: 1,119 tests, errors=2; audit rerun
hit the same two errors, with 689 connections opened and zero without explicit
close. Syntax/import, pytest, JavaScript and upload passed; post setup-node/
setup-python cleanup was skipped. The two errors were older shared-initiative
AST fixture methods failing a relative import with empty globals before their
assertions, not calculation assertion failures. The workflow remains failed.

Fixture repair bb866bd457f42e4a60a14e18c0c90177109e2db0 supplies __name__/__package__
in that fixture, retaining all five methods/assertions and changing no application,
template or workflow code. A narrow Python 3.12 reproduction using copied bulk/
helper logic reproduced two errors in four behavioural methods, then all four
passed; AST parsing passed. Menu/template and full suite were not executed locally.
Covering corrective CI has not been reviewed. See handover for chunk references.

## Prepared state-normalization increment

Adds only the monster initiative normalization hook in StateService.normalize_state.
Missing bonuses become default-zero without inventing old rolls or changing legacy
totals. Retained rolls determine their calculated totals exactly once; explicit
zero origins persist, malformed initiative fields raise contextual errors, and
input is not mutated. Characters and lairs are not given monster initiative fields.
The existing API bridge lets edited legacy totals survive state normalization.
No new raw-roll editor, bonus input, provider mapping, schema migration or active-
battle reorder rule is delivered by this state increment.

Twenty regressions passed using complete StateService and real feature/statistics/
lair/turn/health modules, not condensed/stub feature logic. Original StateService
blob and five dependency blobs were checked against repository SHAs. The context
is still a minimal test object; no full server, HTTP, browser or SQLite lifecycle
coverage is claimed. Tests include actual Max HP reductions and invalid-effect
validation, nonmutation, JSON reload, legacy edit reload, stale-total correction
from a retained roll, character/lair isolation and existing turn/round/tie state.
The prior 18-case form failed five assertions/subtests and two cases with missing
fields against the unmodified service, then passed with the hook. Final 20 passed.

Source grows by 325 bytes to 20,903, within the existing-file 25,000-byte tolerance;
new test is 7,966 bytes, below 20,000. This does not require a size-only split.
Normal CI should discover test_monster_initiative_state.py. No helper change or
new gameplay bounds are included. Covering fixture/state CI and full application
validation remain outstanding; component passes do not complete SG-TODO-018.
This mixed runtime/test/docs commit uses normal CI, without [skip ci], workflow
change or separate dispatch. Root indexes remain in progress and unchanged.

## Outstanding acceptance work

- Review covering fixture/state CI and resolve failures before claiming green current integration validation.
- Complete state/storage/setup route and restart tests beyond component/record fixtures; preserve legacy totals, source provenance, no reroll/compounding and character/lair isolation.
- Wire creation, .monster import, manual/source bonus assignment and correction, signed roster presentation, Edit-modal bonus input and raw-roll/total UI.
- Validate repeated raw entry, bonus edits, shared rolls, reload/reset/setup reuse, explicit/default zero and invalid input through real application paths.
- Implement active ordering updates while preserving ties, turn owner, round, unrelated state and Tab/Shift+Tab navigation.
- Implement provider extraction, retained validated source identity, candidate review and authenticated source-refresh preview/apply.
- Bind server-owned/authenticated reviews to scope/lifetime and prevent stale/deleted/changed/replayed apply; use existing atomic transactions and health/statistics reconciliation.
- Implement desktop/narrow review, per-field/header selection, disabled-source handling, keyboard/accessibility, no preview mutation and HP generation only on apply.
- Execute remaining HTTP/storage/provider/browser regressions and manual creation/import/refresh/reload/usability checks. Do not mark 018 completed solely because a stage was pushed.

Historical clarification: da484d68d5ad39ef371ec8eeecb958149778fd8a; expanded agreement
on features/perplexity: d96048f852b32cd2fb32c2307595eb85e17b61e3. Decisions were
carried onto the dedicated branch without merging. Branch-filter workflow commit:
3baf032c1e16a8b05befc2847f4e2dca98ffb049. README/root indexes were reviewed and
remain accurate without edits for this partial data-normalization delivery.
