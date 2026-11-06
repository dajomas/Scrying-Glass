# 180. Monster initiative bonus

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-018
- Status: in progress; foundation delivered, reset/setup-import integration increment prepared for delivery; full feature integration and validation outstanding.
- Updated: 2026-11-06
- Working branch: features/perplexity-018 for all 018 work until user sign-off. Do not merge back or write 018 changes to features/perplexity without fresh approval.
- Priority: next before SG-TODO-009.5 in the [agreed sequence](115-admin-delivery-sequence.md). No owner or deadline assigned.
- Related: [initiative navigation](130-initiative-keyboard-navigation.md), [source selection](160-source-based-monster-selection.md), [Open5e](170-open5e-monster-source.md).
- Continuity and validation: [foundation handover](../handover/330-monster-initiative-foundations.md).

## Agreed initiative behaviour - 2026-11-06

Support a separate signed monster initiative bonus in manual Add Monster and
.monster import, populated from the selected source when available and manually
correctable. Missing bonuses default to 0 and do not block rolling. Distinguish
a defaulted zero from an explicit zero internally; do not invent provider evidence
or derive a bonus from Dexterity. Reject malformed manual/import input.

Show the assigned bonus read-only between roster HP/Max HP and the raw-roll
editor. Existing-monster bonus editing belongs in the Edit modal, not inline;
the reviewed source-refresh action below is another explicit replacement path.
Show editable raw roll and calculated total separately. Calculate total as raw
roll plus stored bonus exactly once. Each entered roll replaces the old raw
roll, not the total. Saving a bonus change with a retained raw roll immediately
recalculates total and ordering. Reload must not reroll or compound the bonus.
Without a raw roll, the total is unset except for a retained legacy total.

Characters continue to enter announced final totals with no added calculation
or bonus UI. Automatic individual rolls use each monster's bonus. Shared
initiative uses one shared raw d20 roll plus individual bonuses, so totals and
positions can differ. Equal totals retain existing tie resolution. Reordering
preserves current turn owner, round and unrelated state without advancing turns.
Retain existing initiative keyboard navigation. No new raw-roll bounds, manual
final-total override or fallback ordering was agreed.

## Legacy compatibility and examples

Default existing bonuses to 0 without changing stored totals or inventing old
raw rolls. Distinguish legacy totals from unset raw rolls in the roster. Changing
or retrieving a bonus without a retained raw roll preserves the legacy total;
the next manual/automatic raw roll establishes the normal relationship. Persist
bonus, origin, raw roll and legacy/total semantics through save/reload and supported
setup reuse. The reset increment below covers stale-roll clearing; full setup/
storage route validation remains outstanding.

| Action | Raw roll | Bonus | Total |
|---|---:|---:|---:|
| Illustrative dragon input | 16 | +12 | 28 |
| Replace roll | 10 | +12 | 22 |
| Enter 16 again / reload unchanged | 16 | +12 | 28 |
| Save bonus edit | 16 | +10 | 26 |
| Negative bonus | 16 | -2 | 14 |
| Zero/default bonus | 16 | 0 | 16 |

The Adult Blue Dragon +12 input is illustrative user input, not a verified
edition/source statistic. Shared raw 16 with bonuses +12/+3/-2 yields 28/19/14.

## Selected-monster source refresh - agreed 2026-11-06

Include Refresh from source in the monster bulk dropdown. Disable it without a
selection. Review only monsters selected when opening, never the entire roster.
Retrieve the original selected source identity without silently substituting
another edition/candidate. Without retained identity, use existing lookup and
candidate selection, requiring selection before applying. Resolve candidates per
row and return to the same review without losing other selections. Verify actual
provider representations; no new Open5e/source-selection capability is assumed.
Tasks 016/017 remain separate, not prerequisites.

Use one desktop grid with per-monster rows and equivalent narrow-screen cards,
not a wizard. Show source/lookup status and current-to-proposed initiative bonus,
AC, Max HP and Current HP. Each available field has an independent checkbox.
Missing, invalid and failed retrievals are marked/disabled and cannot overwrite
existing values. A missing refreshed bonus does not overwrite an assigned bonus
with default 0. Only checked fields and originally selected monsters can change.

Current HP starts unchecked. Preserve it unless explicitly selected. Show HP dice
formulas during review; generate one value per monster only on HP apply, not on
open/review. Max HP and Current HP are independent; when both are selected use the
same generated source HP value. A single Apply selected changes saves chosen
updates. Review and selection alone mutate no live state. Initiative refresh
recalculates only with an existing raw roll; otherwise preserve legacy totals.

### Row and column header controls

Click a field column header to select all enabled cells in that column; click a
monster row header to select all enabled cells in that row. If all enabled cells
are selected, the next header click clears them; a partial selection selects the
remainder. Individual cells remain independently selectable/deselectable. Skip
disabled fields. Expose unchecked/partial/checked states and keyboard activation,
with equivalent narrow-layout controls. Explicit row/Current HP column selection
can select Current HP despite its initially unchecked default. Header controls
only affect review selections; Apply remains required.

## Acceptance criteria and outstanding integration

- Wire creation, .monster import, manual correction, source bonuses and explicit/default zero provenance; reject invalid manual/import values.
- Wire Edit, individual/shared rolls and raw/total roster UI. Verify signed bonuses, exactly-once application, repeated entry, clearing, legacy transition and unchanged character totals.
- Verify complete database/state/setup route round-trips, normalization, reset/original values and reload without reroll/compounding. Isolated entity-record/reset tests below are partial coverage only.
- Verify ties and active ordering changes without turn/round advancement or unrelated state loss; retain Tab/Shift+Tab navigation.
- Implement validated source identity, provider extraction, candidate review and authenticated preview/apply. Review data must be server-owned or authenticated, not browser-trusted.
- Reject stale scope, deleted/changed monsters and intervening edits; bind review lifetime/replay protection in the eventual route layer.
- Integrate health/statistics reconciliation, source HP validation and atomic apply through existing transaction boundaries. HP dice must not roll during preview.
- Implement desktop grid/narrow cards, header/individual selection and keyboard/accessibility controls; disabled source failures cannot be applied.
- Prepare route/storage/provider/browser regressions and manually verify creation/import, refresh, save/reload and desktop/narrow workflows. Isolated helpers are not end-to-end coverage.

## Foundation delivery and evidence

Historical requirements clarification: da484d68d5ad39ef371ec8eeecb958149778fd8a.
Expanded agreement was recorded on features/perplexity in
d96048f852b32cd2fb32c2307595eb85e17b61e3; the foundation carried those decisions
onto the dedicated branch without merging. Workflow branch-filter commit:
3baf032c1e16a8b05befc2847f4e2dca98ffb049, with [skip ci]; workflow status unchecked.

Foundation commit 539697fabdde7e564b198104739870760032d638 added initiative rules,
pure refresh planning, a pure selection controller and tests. Prepared copies
passed 22 Python and 10 Node isolated helper tests before that user-requested
[skip ci] push. No runtime integration or usable feature was claimed at that
commit; no full application/storage/browser suite or CI run was checked.

## Reset/setup-import integration increment - 2026-11-06

Prepared for the user's requested push: reset_initiative_patch and calls from
reset_entity/reset_imported_monster clear the current raw roll while restoring
the original total as legacy and retaining assigned bonus/origin. Character reset
is unchanged. Setup import preserves source HP/Max HP, new identity and deep-copy
behaviour. Existing setup snapshots retain current roll/bonus/total data.

Sixteen new tests passed twice during preparation: ten reset/setup/character
methods and six native SQLite entity-record fixture methods. The suite against
the original reset implementation reported eight failures, including three
invalid-input subtest failures. Local SQLite checks used a minimal schema and
copied record methods, not the complete storage facade/production schema or
application transactions. The committed tests import the repository mixin.
Source identity values in the fixtures are illustrative scalars, not a delivered
provider mapping. No schema migration or storage implementation change is made.
Full integration and validation remain outstanding; do not mark 018 completed.

This code/test increment uses normal CI, without [skip ci], workflow changes or
separate dispatch. The earlier skip applied only to the foundation. CI execution
and results remain unverified until supplied artifacts are reviewed. The existing
32 helper tests were not rerun for this preparation. See the linked handover for
execution limitations and remaining work. README and both root indexes were
reviewed/reused unchanged: links and the overall in-progress status remain valid.
