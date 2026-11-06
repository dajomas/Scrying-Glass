# 180. Monster initiative bonus

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-018
- Status: in progress; runtime through normalization has covering CI, import delivered with CI unreviewed, manual creation component included with validation pending.
- Updated: 2026-11-07
- Branch: features/perplexity-018 until sign-off; no merge/write-back without fresh approval.
- Priority: before 009.5 in the [agreed sequence](115-admin-delivery-sequence.md). No owner/deadline assigned.
- Related: [initiative navigation](130-initiative-keyboard-navigation.md), [source selection](160-source-based-monster-selection.md), [Open5e](170-open5open-monster-source.md).
- Detailed evidence/history: [handover](../handover/330-monster-initiative-foundations.md).

## Agreed initiative contract

Monsters have separate signed bonuses, set manually or from available selected
source data and correctable at creation/.monster import. Missing defaults to0,
without blocking rolls; internally distinguish default from explicit zero. Reject
malformed input and do not infer from Dexterity or invent source evidence.
Characters retain announced final totals with no bonus UI/additional calculation.

Roster bonus is read-only between HP/Max HP and editable raw roll; calculated
total is separate and orders turns. Existing-monster bonus editing belongs in
Edit, not inline, with reviewed source refresh another replacement path. Each
raw entry replaces the prior raw roll and adds the bonus exactly once. Bonus edits
with retained raw roll immediately recalculate total/order. Reload neither rerolls
nor compounds. Unset raw means unset calculated total except retained legacy.

Old stored totals stay unchanged when defaulting bonus0; never invent old rolls.
Distinguish legacy total from unset raw input. Bonus change/refresh without raw
preserves a legacy total; next manual/automatic raw roll establishes calculation.
Persist bonus/origin, raw and total semantics across reload/setup reuse. Shared
initiative is one d20 raw roll plus individual selected bonuses, so totals/order
may differ. Retain ties and keyboard navigation. Reordering preserves turn owner,
round and unrelated state without advancing turns. No new gameplay roll bounds,
dice roller, total override or fallback order agreed; old final-total API bridge
is temporary until raw-roll UI integration.

Examples:16+12=28; replace raw10 gives22; enter16 again/reload gives28; bonus edit10
gives26; raw16 with-2/0 gives14/16; shared16 with12/3/-2 gives28/19/14. Adult Blue
Dragon +12 is user illustration, not verified provider/edition data.

## Agreed selected-monster refresh

Monster bulk Refresh from source is disabled without selection and operates only
on originally selected monsters, never the whole roster. Use retained original
source identity without silent edition/candidate substitution; otherwise require
existing lookup/candidate selection. Resolve candidates per row and return without
losing other choices. Verify formats; 016/017 stay separate, not prerequisites.

One desktop grid/per-monster rows with equivalent narrow cards shows source/status
and current-to-proposed initiative bonus, AC, Max HP and Current HP. Each available
field has its own checkbox. Missing/invalid/failed fields are marked/disabled and
cannot overwrite assigned data; missing refreshed bonus cannot replace an assigned
one with0. Apply only checked fields for originally selected monsters; preserve
others. Current HP starts unchecked and changes only by explicit selection. Show
HP dice formulas and generate one value per monster only on HP apply, not review;
HP/Max HP are independent and selecting both uses one value. One Apply selected
changes saves choices; review/checkbox/header actions mutate no live state.
Refreshed bonuses recalculate only with retained raw, otherwise preserve legacy.

Column headers select all enabled cells in their column, row headers their row.
Fully selected headers clear; partial headers select the remainder. Preserve
individual select/deselect, skip disabled cells and expose unchecked/partial/
checked state with keyboard activation/narrow equivalents. Explicit row/Current HP
header action may select HP despite its unchecked default. Apply remains required;
use one review, not a one-monster-at-a-time wizard.

## Delivered history and evidence

Foundation539697fabdde7e564b198104739870760032d638 (32 helpers, requested [skip ci]);
reset44e5c7640007601f801858d740dfdf66ab61e541 (reset helper/hooks,16 tests);
compatibility4e7128eb3e5349c186f0a80d34031031762a3d89 (legacy bridge/automatic rolls,
7 handlers); fixturebb866bd457f42e4a60a14e18c0c90177109e2db0 (AST package context,
5 methods retained); statecdd9957642a6754675dc7ace466def69c702b211 (hook/20 tests).
Reset/import/snapshot semantics preserve bonus/origin, legacy totals and HP/copy
isolation as documented in handover. No schema migration; character/lair initiative
is unchanged.

CI42302058360 attempt1 passed exact44e5c764; evidence
88461cc2891a935e541e881884ef6b1a6fabde5b / ci-results-42302058360-attempt-1:
1,112-test executions OK, pytest43, connections689/0. CI42304851642 attempt1 failed
exact4e7128eb; evidence ea9804a2ebf43fc26bdb2554601f0d8923518933 /
ci-results-42304851642-attempt-1: two AST import errors repeated across1,119-test
runs before assertions, not four defects/calculation failures. Seven handlers
passed; syntax/import, pytest, JavaScript/upload passed; setup-node/setup-python
cleanup skipped. That old run stays failed despite connection tracking689/0.

Covering CI42307450451 attempt1 passed exactcdd995764; evidence
5d218b4497391fc4fb52da2dd4ed2e823e29fe5c / ci-results-42307450451-attempt-1.
All steps/cleanup succeeded:1,139-test main/repeated suites OK, pytest43, all20 state
and all5 repaired shared-roll methods explicitly OK, audit689 opened/0 without
explicit close PASS. This resolves that covering exception without relabelling old
failure. Repetition is not unique tests; publication is not tested code. Handover
records chunk paths and mocked-browser/minimal-SQLite limitations.

## Import and manual creation increments

Import4a1685cbe811c478ae44021ceb255fc1f8f964d8 supports optional .monster
initiative_bonus with import provenance for supplied values and default0 for blank.
Null/booleans/floats/containers/malformed/out-of-storage-range explicit input is
rejected, not inferred from Dexterity or ambiguous initiative fields. File origin
cannot spoof provider data. Absent-key parser output stays its original fields;
existing normalization/calculation supplies missing0. Existing construction carries
metadata and quantity IDs; no assigned raw/total. Seven pure methods passed;13
framework methods could not collect without FastAPI. Covering import CI remains
unreviewed; help identifies an optional Scrying Glass field, not guaranteed export.

This component adds the bonus field to Add Monster and the active
CandidateMonstersMixin Form parameter. Blank/omitted becomes default0; explicit0
is manual0. Validate before HP factory/image operations/append. Creation payload
explicitly initializes bonus/origin and raw=None; existing constructor preserves
these fields and leaves total/original initiative unset, so no factory rewrite is
needed. This covers active manual creation, not a change to all programmatic
factory paths. Existing scope guard and image-token/upload precedence remain.
FormData carries raw strings and reset returns blank; no Admin JS fragments change.

Three static and one real Chromium native FormData method passed locally using
complete prepared source/template copies. Original blobs were verified. The native
fixture is not assembled Admin/CSS, HTTP or desktop/narrow usability acceptance.
Eight direct-handler methods are prepared but not executed: FastAPI is absent and
collection stops. No framework substitute/passing API claim. Normal CI discovers
both test files and has configured dependencies. New-stage full/CI validation is
pending, not a completed SG-TODO-018 feature. Normal CI, no [skip ci], workflow
change or separate dispatch; root index links/overall in-progress status retained.

## Outstanding acceptance work

- Review covering import/manual CI and complete actual HTTP/storage/restart and manual creation/import checks.
- Add existing-monster Edit bonus input, read-only signed roster bonus and editable raw-roll/separate total UI; preserve character behaviour.
- Verify repeated rolls, bonus edits, shared rolling, provenance, reload/reset/setup reuse and rejection through complete application paths.
- Implement active-order updates preserving ties, turn/round/unrelated state and Tab/Shift+Tab navigation.
- Implement provider extraction/validated retained identity, candidate review and authenticated refresh preview/apply.
- Bind server-owned/authenticated review to scope/lifetime; guard stale/deleted/changed/replayed apply and use atomic health/statistics reconciliation.
- Implement responsive grid/cards, header/individual selection, disabled-source handling, keyboard/accessibility, no review mutation and HP generation only on apply.
- Require all agreed acceptance/validation and user sign-off; pushing a stage is not task completion.

Historical clarification da484d68d5ad39ef371ec8eeecb958149778fd8a; expanded agreement
d96048f852b32cd2fb32c2307595eb85e17b61e3 was carried without merging branches.
Workflow branch filter:3baf032c1e16a8b05befc2847f4e2dca98ffb049. README and indexes
were reviewed/reused unchanged; this detail defines partial stage scope.
