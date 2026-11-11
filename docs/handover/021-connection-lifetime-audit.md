# 021 - Connection-lifetime audit isolation

[Back to handover index](../../HANDOVER.md)

## Repair preparation - 2026-11-11

The supplied CI excerpt shows browser launch failures followed by an audit crash:
Cannot run the event loop while another loop is running. Live FeedbackLoadingTests
starts sync Playwright before Chromium launch and stops it only in tearDownClass;
a failed setUpClass does not run that teardown. This is a concrete contamination
path, not proof that every fixture or failing run has exactly that one cause.

The connection audit now enumerates the existing test*.py unittest modules and
runs each in a fresh process using the same interpreter and assembled checkout.
SQLite connect tracking is installed inside each worker before discovery/imports,
so isolation does not discard the tracking patch. Each module reports its own
opened/unclosed counts; the parent reports module failure counts, not an invented
cross-process connection total. Setup/import/test failures and detected leaks
remain nonzero, and later modules still execute. No async/browser modules are
excluded. Empty module discovery fails. The unchanged failed-PRAGMA propagation/
closure assertions run before the parent starts workers. Cleanup after measuring
leaks does not turn leaks into successes. Child processes spawned by tests are
not automatically instrumented, as with the earlier process-local audit.

Seven focused regression tests passed on Python 3.12.8. They exercise actual
subprocess workers, closed sync/async connections, import-time and test-body leaks,
a failed setup leaving a running-loop marker, import failure/continuation, probe
ordering/failure propagation and empty inventory. The synthetic shared-process
baseline reproduces the nested-loop error; isolated modules retain the setup
failure while the following async module completes without that secondary error.
The private asyncio marker is used only in the synthetic regression fixture, not
in the audit. AST parsing passed; the worker CLI also ran the seven tests and
reported zero tracked leaks for that regression module itself.

This is focused audit-control validation, not execution of the complete repository
audit, actual Playwright launch failure, real storage initialization probe or CI's
Python 3.14 environment. Covering repository validation remains pending. Browser
installation is not repaired: missing Chromium must still fail the relevant
module and audit. Browser-fixture cleanup within a failing module remains a
separate concern; process isolation prevents cross-module contamination, not all
possible within-module lifecycle faults. Per-module startup adds process overhead.

Application code, workflows, split runner, runtime dependencies and character-Edit
implementation are unchanged. Existing unittest/standalone discovery includes the
new regression and updated audit without workflow edits. Normal CI applies, with
no skip marker or separate dispatch. README and the CI coverage overview remain
accurate; the audit still repeats unittest discovery, now per module. The existing
[task record](../todo/100-httpx2-test-migration.md#connection-lifetime-audit-maintenance---2026-11-11)
tracks this independent maintenance correction without reopening accepted migration
scope. Stage 2, both feedback deliverables and 009.7 remain open. No commit identity,
CI success, full-suite success, merge or deployment is claimed before it occurs.
