# 330. Monster initiative and refresh foundations

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-07. Task: [SG-TODO-018](../todo/180-monster-initiative-bonus.md).
Status: in progress. Delivered runtime through state normalization has covering
successful CI; the agreed .monster import stage is prepared with validation
pending. All 018 writes stay on features/perplexity-018 until user sign-off;
no merge/write-back to features/perplexity is authorized.

## Delivered history and evidence

Foundation 539697fabdde7e564b198104739870760032d638: pure initiative/refresh rules,
selection controller and 32 helper tests, with requested [skip ci]. Reset
44e5c7640007601f801858d740dfdf66ab61e541: reset helper, two reset hooks, 16 tests.
Compatibility 4e7128eb3e5349c186f0a80d34031031762a3d89: legacy-total bridge,
automatic raw/bonus rolling, seven handler tests. Fixture correction
bb866bd457f42e4a60a14e18c0c90177109e2db0: package globals for the AST-extracted
shared-roll fixture, preserving all five methods/assertions. State normalization
cdd9957642a6754675dc7ace466def69c702b211: monster-only hook and 20 regressions.

Reset clears stale raw rolls, preserves bonus/origin and restores original totals
as legacy. Snapshots preserve current relationships; setup import retains reset-
on-import, HP/Max HP and copy isolation. Changed/cleared legacy totals detach old
rolls; unchanged/unrelated edits retain them. Individual/shared rolling stores raw
rolls plus individual bonuses. Normalization supplies default zero and preserves
legacy totals without invented rolls. Characters/lairs are not bonus-calculated.
No schema migration has been introduced. Full feature/UI delivery remains open.

CI 42302058360 attempt 1 passed exact 44e5c764; publication
88461cc2891a935e541e881884ef6b1a6fabde5b, ci-results-42302058360-attempt-1:
1,112-test main/repeated suites OK, pytest 43 passed, 689 opened connections and
zero without explicit close. CI 42304851642 attempt 1 failed exact 4e7128eb;
publication ea9804a2ebf43fc26bdb2554601f0d8923518933,
ci-results-42304851642-attempt-1. Both 1,119-test executions hit the same two
AST namespace import errors before shared-roll assertions, not four defects or
calculation assertion failures. Seven new handlers passed; syntax/import, pytest,
JavaScript and upload passed, setup-node/setup-python cleanup was skipped.
Connection tracking 689/0 did not make the failed suite pass. That run stays failed.

## Verified covering state/fixture CI

Run 42307450451 attempt 1 tested exact cdd9957642a6754675dc7ace466def69c702b211
on features/perplexity-018. Publication 5d218b4497391fc4fb52da2dd4ed2e823e29fe5c,
ci-results-42307450451-attempt-1. run.json reports completed/success for workflow
and tests job 128200269724; all steps, upload and cleanup succeeded.
Workflow reader-chunks/file-000025 parts 76-77 explicitly report all 20 state
methods OK; part 80 all five repaired shared-roll methods OK; part 83 main
1,139 tests in 80.641s OK; part 85 pytest 43 passed in 0.79s; part 112 repeated
1,139 tests in 76.828s OK, 689 connections opened and zero without explicit close,
audit PASS. JavaScript/standalone steps succeeded. This resolves the prior covering
validation exception without relabelling the failed run. Repetition is not another
unique test set; publication is not tested code. Mocked HTTP/WS Chromium fixtures,
minimal SQLite record tests and component checks are not complete production-
storage, authenticated live-server or full end-to-end validation.

## Agreed import-only stage

Support the explicit .monster initiative_bonus key as a signed integer or integer
text. Supplied nonblank values carry import origin; blank becomes default zero.
Absent-key parser output remains its existing four fields; delivered normalization/
calculation paths supply missing zero. Explicit null, booleans, floats, containers,
malformed text and out-of-signed-64-bit-storage values are rejected. These storage
limits are not new gameplay roll bounds. No Dexterity/ambiguous initiative-field
derivation, provider evidence, source identity or schema change is added. A file
cannot override the assigned import origin. Duplicate-key, HP/AC and CSV behaviour
remain. Help identifies this as a Scrying Glass field, not guaranteed exporter data.

Existing make_monster/make_monsters preserve additional scalar fields, so this
stage does not alter constructors or handlers. The inherited import handler parses
before image lookup/save and append. New records have no assigned total/raw roll;
existing helpers treat an absent roll key as unset. Quantity copies retain bonus
with distinct IDs. Manual Add Monster parameter/form and explicit constructor
initialization follow as the separately agreed next stage. Existing-monster bonus
editing, raw-roll roster UI, provider extraction, refresh and ordering stay open.

## Prepared checks and continuation

Seven framework-independent methods passed locally in this preparation. Both new
test modules/helper passed AST parsing. Thirteen parser/construction/direct-import
methods are prepared but were not executed: collection stopped with
ModuleNotFoundError: No module named 'fastapi'. This is an environment/collection
failure, not passing tests or executed assertion failures. No fake FastAPI package
was substituted. The prior broader 30-case creation draft is not this stage's
payload. Normal CI discovers the two test_*.py modules and supplies dependencies;
HTTP/browser/storage/manual acceptance remains distinct from these unit fixtures.

The live parser was verified as 742908fd67ad34dc6f21a6d9c0532f5d31da4a98 before
preparing the optional-field extension. New code/tests remain below 20,000 bytes;
existing parser remains below its allowance. Normal CI applies: no [skip ci],
workflow changes or separate dispatch. No stage CI result or completion is invented.
README and root indexes were reviewed/reused; overall task identity/status and
links remain in progress. Task details carry authoritative stage scope. No new
handover section/index link is needed. Continue manual creation next, then remaining
Edit/UI/provider/refresh/order integration with exact approval for each write.
