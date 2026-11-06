# 180. Monster initiative bonus

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-018
- Status: in progress; foundation/reset have covering CI; handler compatibility delivered with failed full-suite validation; fixture correction prepared and awaiting covering CI.
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

## Delivery and validation

Foundation 539697fabdde7e564b198104739870760032d638 added pure modules and 32 helper
tests with the user's one-off [skip ci]. Reset/setup import increment
44e5c7640007601f801858d740dfdf66ab61e541 clears stale current rolls while preserving
bonus/origin and restoring original totals as legacy. Snapshots retain current
relationships; setup import keeps source HP/Max HP, new IDs and deep-copy isolation.
Characters remain unchanged. No schema/storage implementation changes were needed.

CI run 42302058360 attempt 1 completed successfully against exact 44e5c764 on the
dedicated branch. Evidence publication: 88461cc2891a935e541e881884ef6b1a6fabde5b,
ci-results-42302058360-attempt-1. Verified main suite 1,112 tests OK, pytest 43
passed, all 22+16 dedicated Python and 10 selection tests passed; repeated audit
suite OK with 689 opened connections and zero without explicit close. All job
steps succeeded. Repeated execution is not another unique test set. See handover
for chunk paths, fixture coverage and live-server/storage limitations.

Handler compatibility commit 4e7128eb3e5349c186f0a80d34031031762a3d89 wires existing
final-total edit compatibility and individual/shared automatic raw-roll calculation.
It does not wire state normalization or the raw-roll UI. Its seven direct-handler
methods passed in CI, but the full workflow did not pass; details below. The prior
16-test isolated normalization/bridge fixture is not shipped state wiring or
full-application evidence. Root indexes remain accurate at the in-progress level.

## Failed compatibility CI and prepared fixture correction

Run 42304851642 attempt 1 tested exact 4e7128eb3e5349c186f0a80d34031031762a3d89.
Evidence publication: ea9804a2ebf43fc26bdb2554601f0d8923518933, folder
ci-results-42304851642-attempt-1. Workflow and tests job completed/failure.
Syntax/import, pytest, JavaScript and artifact upload passed. Main Python suite:
1,119 tests, FAILED (errors=2). The repeated audit suite hit the same two errors;
689 opened connections, zero without explicit close. Cleanup for setup-node and
setup-python was skipped, not passed. All seven new direct-handler methods passed.

The two errors are test_duplicates and test_single_roll_selected_only in
SharedInitiativeTests. Its AST-extracted bulk_monsters method executes with empty
globals, so the relative helper import raises KeyError: "'__name__' not in globals"
before initiative assertions run. Preserve these errors as failure evidence,
not as calculation assertion failures or a passing workflow.

The corrective test change supplies __name__ and __package__ in the AST namespace.
All five methods and existing assertions remain. No application, template or
workflow changes are included. Local narrow reproduction against copied bulk/
helper logic reproduced two errors in four behavioural methods, then all four
passed with the fix. AST parsing passed. The menu/template method and full suite
were not executed locally. Covering CI remains required. See the handover for
source chunk locations and limitations; no passing correction result is claimed.

The corrective commit uses normal CI, without [skip ci], workflow modification or
separate dispatch. After its approved push, continue preparing state normalization;
that preparation does not close the outstanding validation exception or complete
018. Each later external write still needs exact-content approval.

## Outstanding acceptance work

- Review covering fixture-repair CI and resolve any remaining failures before claiming green compatibility validation.
- Wire monster-only state defaults/validation and complete state/storage/setup route tests; retain character/lair isolation, legacy totals and no compounding.
- Wire creation, .monster import, manual/source bonus assignment and correction, signed roster presentation, Edit-modal bonus input and raw-roll/total UI.
- Validate repeated raw entry, bonus edits, shared rolls, reload/reset/setup reuse, explicit/default zero and invalid input through real application paths.
- Implement active ordering updates while preserving ties, turn owner, round, unrelated state and Tab/Shift+Tab navigation.
- Implement provider extraction, retained validated source identity, candidate review and authenticated source-refresh preview/apply.
- Bind server-owned/authenticated reviews to scope/lifetime and prevent stale/deleted/changed/replayed apply; use existing atomic transactions and health/statistics reconciliation.
- Implement desktop/narrow review, per-field/header selection, disabled-source handling, keyboard/accessibility, no preview mutation and HP generation only on apply.
- Prepare and execute remaining HTTP/storage/provider/browser regressions and manual creation/import/refresh/reload/usability checks. Do not mark 018 completed solely because a stage was pushed.

Historical clarification: da484d68d5ad39ef371ec8eeecb958149778fd8a; expanded agreement
on features/perplexity: d96048f852b32cd2fb32c2307595eb85e17b61e3. Decisions were
carried onto the dedicated branch without merging. Branch-filter workflow commit:
3baf032c1e16a8b05befc2847f4e2dca98ffb049. No deadline or owner is invented.
README and root indexes were verified unchanged and require no edits for this
fixture-only correction; the task remains in progress and its links are unchanged.
