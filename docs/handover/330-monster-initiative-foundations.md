# 330. Monster initiative and refresh foundations

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-018](../todo/180-monster-initiative-bonus.md).
Status: in progress. Foundation/reset have covering CI. Handler compatibility
is delivered; its fixture correction is delivered but covering CI is unreviewed.
State normalization is prepared with 20 passing component tests and full CI pending.
All 018 writes target features/perplexity-018 until user sign-off. No merge or
write-back to features/perplexity is authorized.

## Delivered history

Foundation: 539697fabdde7e564b198104739870760032d638, pure initiative/refresh rules,
selection controller and 32 helper tests, with user-requested [skip ci]. Reset/setup
integration: 44e5c7640007601f801858d740dfdf66ab61e541, reset helper and two reset-path
hooks plus 16 tests. Reset clears the current raw roll, preserves bonus/origin,
restores original totals as legacy and does not invent historical rolls. Characters
are unchanged. Snapshots preserve current values; setup import retains reset-on-
import semantics, HP/Max HP and copy isolation. No storage schema change was made.

Handler compatibility: 4e7128eb3e5349c186f0a80d34031031762a3d89. Changed/cleared
final-total edits detach stale raw rolls; unchanged totals/unrelated edits retain
them. Automatic individual/shared rolling stores raw roll plus individual bonus.
The bridge preserves the old UI temporarily, not a new manual-total override.
Seven direct-handler regressions were added. No raw-roll UI, creation bonus input,
source refresh or active-battle reordering was delivered by those stages.

## Verified reset/setup covering CI

Run 42302058360 attempt 1 tested exact 44e5c7640007601f801858d740dfdf66ab61e541.
Evidence publication: 88461cc2891a935e541e881884ef6b1a6fabde5b, folder
ci-results-42302058360-attempt-1. Workflow/tests job and all steps succeeded.
Workflow reader-chunks/file-000025 parts 73-75 show all 22+16 dedicated Python
methods OK; part 82 reports 1,112 tests in 106.131s, OK; part 83 reports pytest
43 passed in 1.29s; parts 93-94 show ten selection tests passed, no skips/cancels;
parts 110-111 show the repeated 1,112-test suite OK, 689 connections opened,
zero without explicit close, connection audit PASS. Repeated execution is not
another unique test set; the publication commit is not the tested code revision.
Browser smoke uses mocked HTTP/WS with real Chromium. Entity storage fixtures
use a minimal SQLite schema, not complete production schema/migration or live-
authentication coverage. These results do not complete SG-TODO-018.

## Failed compatibility CI and fixture correction

Run 42304851642 attempt 1 tested exact 4e7128eb3e5349c186f0a80d34031031762a3d89.
Publication: ea9804a2ebf43fc26bdb2554601f0d8923518933, folder
ci-results-42304851642-attempt-1. run.json reports completed/failure for workflow
and job 128191490047. Syntax/import, pytest, JavaScript and visual upload passed.
Main Python and standalone audit steps failed. Post setup-node/setup-python
cleanup was skipped, not passed; checkout cleanup passed.

Workflow reader-chunks/file-000025 parts 73-74 show all seven new handler methods
OK. Parts 82-84 show test_duplicates and test_single_roll_selected_only failing
with KeyError: "'__name__' not in globals"; 1,119 tests in 109.161s, errors=2.
Parts 113-114 show the same two errors during the 1,119-test audit rerun, 108.032s.
They are repeated errors, not four defects. Part 114 tracks 689 opened connections
and zero without explicit close; that does not make the failed suite a pass.

The older fixture AST-extracts bulk_monsters into empty globals. The new relative
helper import needs module/package globals, so it fails before shared-roll
assertions. No calculation assertion failed in those two cases. The failed run
remains failed evidence despite the dedicated tests passing.

Fixture correction: bb866bd457f42e4a60a14e18c0c90177109e2db0. It sets __name__ and
__package__ in tests/test_shared_monster_initiative.py. All five methods/assertions
remain; application/templates/workflows are unchanged. A Python 3.12 isolated
reproduction using copied bulk/helper logic reproduced two errors in four
behavioural methods, then all four passed. AST parsing passed. The menu/template
method and full suite were not run locally. Covering corrective CI is still
unreviewed; no green-validation claim is made for that repair.

## State-normalization increment - prepared 2026-11-06

Adds a 325-byte monster-only hook to StateService.normalize_state, calling the
existing initiative normalizer before feature normalization. Missing bonuses
become 0 with default origin and absent raw rolls remain null. Legacy totals are
preserved without invented rolls. A retained raw roll determines the derived
total exactly once, including repair of a stale derived total. Explicit-zero
origin persists; malformed initiative fields produce contextual monster-location
errors. Character/lair normalization is unchanged. The existing final-total bridge
allows edited legacy totals to survive subsequent full state normalization.

The rest of StateService source is unchanged. Its original blob was verified as
525b898f5cfb376cbdffdb1505764bd169186fcf before applying the hook. Five dependency
copies (feature/statistics/lair/turn/health rules) were verified against repository
blob SHAs. The tests use the complete StateService and real dependency modules,
not the earlier condensed method/stub feature fixture. Only a minimal context
object/display callback is supplied; these remain component-level checks.

Twenty regressions passed in preparation: 15 full-state cases and five bridge
cases, including real Max HP reduction normalization, rejection of invalid effects,
nonmutation, character/lair isolation, retained turn/round/tie state, JSON reload,
legacy-edit reload and stale-derived-total repair. The earlier 18-case form of
this suite produced five failures and two errors against the unmodified state
service, then passed with the hook; the final expanded 20-case suite passed.
Do not describe that baseline as a new failure of the delivered requirements.

Prepared state source: 20,903 bytes (20,578 plus 325), within the documented
25,000-byte existing-file tolerance; new test: 7,966 bytes, below 20,000. See
[source-size policy](../todo/080-source-size-refactors.md). No size-only refactor,
schema migration, helper change or new gameplay bounds are included. No full
server, SQLite lifecycle, HTTP, ordering or browser validation ran for this
increment. Normal CI should discover tests/test_monster_initiative_state.py.

## Continuation and delivery policy

Review covering fixture/state CI when the user supplies results; neither a push
nor the 20 component passes closes the outstanding validation exception. Next
wire creation/.monster bonus input, bonus editing, raw-roll roster UI, validated
provider/source identity, source-refresh preview/apply and active-order updates.
The planner still needs server-owned/authenticated review data, scope/lifetime/
replay guards, atomic health/statistics reconciliation and sanitized UI offers.
It is not a security boundary; source identity samples are illustrative.

This runtime/test/documentation increment uses normal CI, no [skip ci], workflow
change or separate dispatch. Branch filter: 3baf032c1e16a8b05befc2847f4e2dca98ffb049.
README and root indexes were verified against prior complete reads and left
unchanged: links, overall in-progress status and existing user workflows remain
accurate. Task detail records partial delivery/validation. No complete feature,
new workflow result or authenticated live-server success is claimed.
