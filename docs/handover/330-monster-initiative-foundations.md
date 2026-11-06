# 330. Monster initiative and refresh foundations

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-06. Task: [SG-TODO-018](../todo/180-monster-initiative-bonus.md).
Status: in progress. Foundation and reset/setup-import increment delivered with
covering CI; handler compatibility stage prepared with execution pending.
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

## Verified covering CI

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
verification. These results validate the delivered increment, not all of 018.

## Handler compatibility stage

Revised delivery sequence: handler compatibility and automatic rolling first;
state normalization and its tests follow separately. This commit does not change
StateService, add a raw-roll UI or enable source refresh. Existing manual APIs
still accept final totals: changed/cleared totals detach stale raw rolls and keep
bonus/origin, while unchanged totals and unrelated edits keep the existing roll.
This is a temporary compatibility bridge, not a new user-facing total override.
Individual automatic rolls and selected shared rolls now retain raw rolls and add
each monster's own bonus once. Candidate changes are validated before assigning
the rolled values. Existing routes, authentication and character handlers stay.
Active-battle reordering remains outstanding; no new ordering claim is made.

Seven direct handler tests are prepared in test_monster_initiative_handlers.py.
Their AST parsing passed in preparation; they were not executed locally. The
previous 16-test normalization/bridge fixture passed with stub feature rules and
a condensed normalization copy; it is not handler or full-application validation
and is not shipped in this stage. Full handler/application execution is delegated
to normal CI. No successful CI result is claimed for this new stage in advance.

## Continuation and policy

Next wire monster state defaults/validation with complete-file tests, then manual
creation/.monster input, bonus editing, raw-roll roster UI, provider/source
identity, refresh preview/apply and active ordering. The refresh planner still
requires server-owned/authenticated review data, scope/lifetime/replay guards,
atomic health/statistics reconciliation and sanitized UI offers. It is not a
security boundary. Source identity fixtures are illustrative, not provider mappings.

Normal CI applies to this code/test commit; no skip marker, workflow change or
separate dispatch. Branch-filter commit: 3baf032c1e16a8b05befc2847f4e2dca98ffb049.
README and both root indexes were reviewed/reused: links and overall in-progress
status remain valid. No completed feature, current CI pass or live-server
validation is claimed by this delivery. Earlier local preparation limitations
are superseded only where the covering CI evidence above actually extends them.
