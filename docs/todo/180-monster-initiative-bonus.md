# 180. Monster initiative bonus

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-018
- Status: in progress; state/compatibility/fixture stages have covering green CI; .monster bonus-import stage prepared with CI pending, remaining feature integration outstanding.
- Updated: 2026-11-07
- Branch: features/perplexity-018 until user sign-off; no merge/write-back without fresh approval.
- Priority: next before 009.5 in the [agreed sequence](115-admin-delivery-sequence.md). No owner/deadline assigned.
- Related: [initiative navigation](130-initiative-keyboard-navigation.md), [source selection](160-source-based-monster-selection.md), [Open5e](170-open5e-monster-source.md).
- Evidence and continuity: [handover](../handover/330-monster-initiative-foundations.md).

## Agreed initiative contract

Monsters have separate negative/zero/positive bonuses, supplied manually or from
selected sources when available, correctable at creation and through .monster
import. Missing bonuses default to 0 without blocking rolls; distinguish default
from explicit zero internally, reject malformed manual/import input and do not
invent source evidence or derive initiative from Dexterity. Characters retain
announced final totals with no bonus UI or additional calculation.

The roster bonus is read-only between HP/Max HP and the editable raw-roll input;
show calculated total separately and order by it. Existing-monster bonus edits
belong in Edit, not inline, with reviewed refresh another explicit replacement
path. Every raw entry replaces the old raw roll; add bonus exactly once. Bonus
edits with a retained roll immediately recalculate total/order. Reload never
rerolls or compounds. Unset roll means unset calculated total except legacy.

Preserve existing totals when defaulting old bonuses to zero; never invent old
raw rolls. Distinguish legacy total from unset raw input. Bonus changes/refresh
without a retained roll preserve a legacy total; the next manual/automatic raw
roll establishes roll-plus-bonus. Persist bonus/origin, roll and total relationship
through reload and supported setup reuse. Shared initiative is one d20 raw roll
plus each selected monster's own bonus, so totals/positions may differ. Retain
tie resolution and initiative keyboard navigation. Order updates preserve turn
owner, round and unrelated state without advancing turns. No new gameplay roll
bounds, dice roller, final-total override or fallback order was agreed; the old
final-total API bridge is temporary until the raw-roll UI is connected.

Illustrative examples: raw 16 + bonus12 =28; replace raw with10 =22; enter16 again
or reload =28; change bonus to10 =26. Raw16 with -2/0 gives14/16. Shared16 with
+12/+3/-2 gives28/19/14. Adult Blue Dragon +12 is user illustration, not a verified
provider/edition statistic.

## Agreed selected-monster refresh

Refresh from source is a monster bulk dropdown action, disabled without selection,
acting only on originally selected monsters, never the whole roster. Retrieve the
original selected source identity, never silently substitute edition/candidate.
Without retained identity, use existing lookup/candidate selection and require a
choice before applying. Resolve per-row candidates and return without losing
other selections. Verify actual provider formats; 016/017 remain separate, not
assumed prerequisites or newly delivered sources.

One desktop grid with per-monster rows and equivalent narrow cards shows source/
lookup status and current-to-proposed initiative bonus, AC, Max HP, Current HP.
Each available field has an independent checkbox. Missing/invalid/failed fields
are marked/disabled and cannot overwrite assigned values; a missing refreshed
bonus cannot replace an assigned one with default0. Apply only checked fields,
preserving everything else and all unselected monsters. Current HP starts
unchecked, changed only by explicit selection. Show HP dice formulas; generate
one value per monster only on HP apply, not open/review. Current HP and Max HP
are independent; selecting both uses one generated value. One Apply selected
changes commits choices; review/header/checkbox operations mutate no live state.
Refreshed bonus recalculates only with a retained roll, else preserves legacy.

Column headers select all enabled cells in that column; row headers select all
in that row. Fully selected headers clear their cells; partial headers select
the remainder. Preserve individual selection/deselection; skip disabled fields.
Expose unchecked/partial/checked states, keyboard activation and narrow-layout
equivalents. Explicit row/Current HP header selection may select Current HP despite
its unchecked default. Apply remains necessary; use one review, not a wizard.

## Delivered history and verified validation

Foundation 539697fabdde7e564b198104739870760032d638: pure modules and 32 helpers,
requested [skip ci]. Reset 44e5c7640007601f801858d740dfdf66ab61e541 preserves bonus/
origin, clears stale raw rolls, restores original legacy totals; snapshots preserve
current relationships and setup import retains HP/Max HP/new IDs/copy isolation.
Compatibility 4e7128eb3e5349c186f0a80d34031031762a3d89 adds legacy edit bridge and
automatic raw/bonus rolling; fixture repair bb866bd457f42e4a60a14e18c0c90177109e2db0
supplies AST package globals without weakening five tests. State normalization
cdd9957642a6754675dc7ace466def69c702b211 adds the monster-only hook and 20 tests.
No schema migration. Complete source/component preparation is not live-server proof.

CI 42302058360 attempt1 passed exact44e5c764, evidence
88461cc2891a935e541e881884ef6b1a6fabde5b / ci-results-42302058360-attempt-1:
1,112-test main/repeated suites OK, pytest43, connections689/0. CI42304851642
attempt1 failed exact4e7128eb, evidence ea9804a2ebf43fc26bdb2554601f0d8923518933 /
ci-results-42304851642-attempt-1: 1,119-test executions repeated the same two AST
import errors before assertions. Seven new handlers passed; syntax/import, pytest,
JavaScript/upload passed, setup-node/setup-python cleanup skipped. That run stays
failed; 689/0 connections do not turn it into a pass.

Covering CI42307450451 attempt1 passed exactcdd995764 on the dedicated branch,
evidence 5d218b4497391fc4fb52da2dd4ed2e823e29fe5c /
ci-results-42307450451-attempt-1. All configured steps and cleanup succeeded;
1,139-test main and repeated suites OK, pytest43, all20 state and all5 repaired
shared-roll methods explicitly OK, audit689 opened/0 without explicit close PASS.
This resolves the prior validation exception, not by relabelling old evidence.
Repeated runs are not unique test sets; publication is not tested code. See
handover for chunk references and mocked-browser/minimal-SQLite limitations.

## Agreed import-only stage

User agreed to .monster import first and manual creation/input initialization
immediately afterward as a separate write. This stage accepts optional
initiative_bonus: signed integer or integer text, import provenance for supplied
values and default zero for blank. Null/booleans/floats/containers/malformed or
out-of-storage-range explicit values are rejected, never silently zeroed. No
Dexterity or ambiguous initiative derivation; a file cannot spoof provider origin.
Absent-key parser output stays its original four fields; existing normalization/
calculation supplies default0. Existing construction carries parsed scalar fields
and quantity copies retain bonuses with unique IDs, without assigning a raw roll
or total. No constructor/handler/CSV workflow/schema changes are included. Help
identifies this optional Scrying Glass field, not a guaranteed exporter field.

Seven pure input methods passed locally; AST parsing passed. Thirteen parser/
construction/direct-import methods are prepared, not executed: collection failed
because FastAPI is absent. This is a collection/environment limitation, not passed
integration tests or assertion failures. No framework stand-in is used. The older
30-case draft is not this smaller stage's test payload. Normal CI discovers both
new modules and supplies dependencies. No import-stage CI success is claimed.
Normal CI, no [skip ci], workflow modification or separate dispatch. README and
root index links/overall in-progress status remain valid; details define stage scope.

## Outstanding acceptance work

- Review covering import CI and complete storage/setup/restart/HTTP/manual checks beyond component fixtures.
- Deliver the agreed following stage: active CandidateMonstersMixin bonus parameter, Add Monster form field and explicit constructor initialization, with regressions.
- Add existing-monster Edit bonus input, read-only signed roster bonus and editable raw-roll/separate total UI; preserve character behaviour.
- Verify repeated rolls, bonus edits, shared rolling, provenance, reload/reset/reuse and invalid input through actual application paths.
- Implement active ordering updates preserving ties, turn/round/unrelated state and Tab/Shift+Tab navigation.
- Implement provider extraction/validated retained identity, candidate review and authenticated refresh preview/apply.
- Bind server-owned/authenticated review to scope/lifetime and guard stale/deleted/changed/replayed apply; use atomic health/statistics reconciliation.
- Implement responsive review, header/individual selection, disabled fields, keyboard/accessibility, no preview mutations and HP generation only on apply.
- Do not mark 018 completed solely because a stage was pushed; user sign-off remains required.

Historical clarification da484d68d5ad39ef371ec8eeecb958149778fd8a; expanded agreement
d96048f852b32cd2fb32c2307595eb85e17b61e3 was carried from features/perplexity without
merging. Workflow branch filter: 3baf032c1e16a8b05befc2847f4e2dca98ffb049.
