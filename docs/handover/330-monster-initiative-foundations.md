# 330. Monster initiative and refresh foundations

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-018](../todo/180-monster-initiative-bonus.md).
Status: in progress. Foundation/reset have covering CI; handler compatibility is
delivered with seven passing dedicated methods but failed full-suite validation.
The shared-initiative fixture repair below is prepared with covering CI pending.
All 018 writes target features/perplexity-018 until user sign-off. No merge or
write-back to features/perplexity is authorized.

## Delivered history

Foundation: 539697fabdde7e564b198104739870760032d638, containing pure initiative
rules, refresh planning, selection controller and 32 helper tests. It used the
user-requested [skip ci]. Reset/setup integration:
44e5c7640007601f801858d740dfdf66ab61e541, containing reset_initiative_patch,
reset_entity/reset_imported_monster wiring and 16 regressions. Reset clears a
stale current roll, retains bonus/origin and restores original totals as legacy.
Characters remain unchanged. Snapshots preserve current values; setup import
retains existing reset-on-import semantics, HP/Max HP and deep-copy isolation.
No schema migration or storage implementation change has been made.

## Verified covering CI for reset/setup import

Run 42302058360 attempt 1 tested exact 44e5c7640007601f801858d740dfdf66ab61e541
on features/perplexity-018. Results publication:
88461cc2891a935e541e881884ef6b1a6fabde5b, folder ci-results-42302058360-attempt-1.
run.json reports completed/success for workflow and tests job. All configured
steps, artifact upload and cleanup succeeded. Workflow chunks under
reader-chunks/file-000025 explicitly show:

- Parts 73-75: all 22 foundation Python and 16 reset/storage methods OK.
- Part 82: main Python suite, 1,112 tests in 106.131s, OK.
- Part 83: pytest, 43 passed in 1.29s.
- Parts 93-94: all 10 selection-controller tests passed, none skipped/cancelled.
- Parts 110-111: repeated 1,112-test suite, OK; 689 connections opened, zero
  without explicit close, connection audit PASS.

The repeated suite is not another set of unique tests. The publication commit
is evidence storage, not the tested code revision. Browser smoke explicitly uses
mocked HTTP/WS with real Chromium. Entity persistence tests use a minimal native
SQLite fixture, not full production schema/migration or authenticated live-server
verification. These results validate that increment, not all of 018.

## Handler compatibility stage

Delivered: 4e7128eb3e5349c186f0a80d34031031762a3d89.
Revised delivery sequence: handler compatibility and automatic rolling first;
state normalization and its tests follow separately. The stage did not change
StateService, add a raw-roll UI or enable source refresh. Existing manual APIs
still accept final totals: changed/cleared totals detach stale raw rolls and keep
bonus/origin, while unchanged totals and unrelated edits keep the existing roll.
This is a temporary compatibility bridge, not a new user-facing total override.
Individual automatic rolls and selected shared rolls retain raw rolls and add
each monster's own bonus once. Candidate changes are validated before assigning
the rolled values. Existing routes, authentication and character handlers stay.
Active-battle reordering remains outstanding; no new ordering claim is made.

The previous 16-test normalization/bridge fixture passed with stub feature rules
and a condensed normalization copy. It was not full-application validation and
was not shipped in the handler stage. The seven new direct-handler methods were
not run locally before delivery; their actual CI results follow.

## Failed compatibility CI - 2026-11-06

Run 42304851642 attempt 1 tested exact 4e7128eb3e5349c186f0a80d34031031762a3d89
on features/perplexity-018. Publication: ea9804a2ebf43fc26bdb2554601f0d8923518933,
folder ci-results-42304851642-attempt-1. run.json reports completed/failure for
workflow and tests job 128191490047. Syntax/import, pytest, JavaScript and visual
artifact upload passed. Main Python and standalone audit steps failed. Post
setup-node/setup-python cleanup was skipped, not passed; checkout cleanup passed.

Workflow chunks under reader-chunks/file-000025:

- Parts 73-74 explicitly show all seven new handler methods OK.
- Parts 82-84 show test_duplicates and test_single_roll_selected_only in
  test_shared_monster_initiative failing with KeyError: "'__name__' not in globals".
  The main suite executed 1,119 tests in 109.161s, FAILED (errors=2).
- Parts 113-114 show the same two errors during the repeated 1,119-test audit
  suite, 108.032s. These are repeated errors, not four distinct defects.
- Part 114 reports 689 opened connections and zero without explicit close.
  That tracking count does not turn the failed suite/audit into a pass.

The older test AST-extracts bulk_monsters and executes it with namespace={}. The
new relative helper import needs module/package globals; the fixture fails before
its shared-roll assertions. No initiative-calculation assertion failed in these
two cases. Do not relabel the workflow as successful because dedicated tests pass.

## Prepared fixture repair and checks

Only tests/test_shared_monster_initiative.py changes executable content. Supply
__name__="python.scrying_glass_admin_monsters" and __package__="python" to the
AST execution namespace. All five test methods and assertions remain unchanged,
including selected-only behaviour, single random roll, duplicate IDs, missing-ID
atomicity, existing battle order and menu presence. No application or workflow
code changes in this correction.

Local preparation used copied bulk-handler/helper logic in an isolated temporary
package on Python 3.12. Four behavioural test methods reproduced the same two
errors before the namespace change and all four passed afterwards. AST parsing
passed. The fifth menu/template test was not executed locally. This is a narrow
import-context reproduction, not a complete checkout/full-suite or authenticated
application run. The prepared test file is 3,124 bytes. Full covering CI and the
menu check remain pending. No corrective commit SHA or passing CI is invented.

## Continuation and policy

After the approved fixture repair, continue preparing monster state defaults/
validation and complete-file tests. Then wire creation/.monster input, bonus
editing, raw-roll roster UI, provider/source identity, refresh preview/apply and
active ordering. The refresh planner still requires server-owned/authenticated
review data, scope/lifetime/replay guards, atomic health/statistics reconciliation
and sanitized UI offers. It is not a security boundary; source identity fixtures
are illustrative, not provider mappings. SG-TODO-018 remains incomplete.

Normal CI applies to this corrective test/documentation commit, without a skip
marker, workflow change or separate dispatch. Branch-filter commit:
3baf032c1e16a8b05befc2847f4e2dca98ffb049. The user will provide result locations
for review. Preparation of the next increment is not a passing-validation claim.
README and both root indexes were verified against prior complete reads and left
unchanged: runtime behaviour, index links and overall in-progress status remain
accurate. This section and the task detail record the failure and pending repair.
