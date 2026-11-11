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

## Chromium provisioning correction - 2026-11-11

Audit isolation was subsequently delivered as 3358400abc08c9ae38aee50942fe7e6cb47a5cfc;
its full repository validation remains pending. The following separate correction
supersedes the earlier unchanged-workflow/missing-browser preparation notes and
the combined browser-installation/unconditional test-step descriptions in 020.

Published run 43053734732 attempt 1, job 130637532410, covers character-Edit commit
fd13991c2c15cb6e15f056f0050431f5bc686ada, not the later audit repair. Its jobs.json
records dependency installation failure. Workflow reader chunks file-000008 parts
10 and 16 show Python Playwright 1.65.0 installed, followed by Ubuntu repository
DNS failures during APT dependency setup. The combined --with-deps invocation
failed before browser provisioning, explaining subsequent missing headless-shell
errors. This is setup evidence, not a character-Edit assertion failure.

The new tools/prepare_ci_browser.py first downloads Chromium and its default
headless shell with the selected Python Playwright. It requires a real headless
launch and DOM text check. If preflight fails it prints the original reason,
attempts install-deps chromium once and requires preflight to succeed afterward.
Download failure, failed native dependency installation or a failed second launch
remain fatal. A working browser avoids the unnecessary APT/font installation
which failed in the reviewed run. This does not repair external DNS or promise
that every runner already has every native library/font; retained browser suites
must still validate their real rendering requirements.

Python dependency installation and Chromium readiness now have distinct workflow
step identities. Both mixed unittest/browser and standalone/browser/audit groups
require successful Python setup and Chromium preflight. Failed provisioning leaves
the job failed and those groups unexecuted, not passed. Syntax/import and pytest
remain eligible after Chromium failure if Python setup succeeded; JavaScript
retains its independent !cancelled() condition. Test-group failures still allow
later eligible groups to run. No continue-on-error, browser assertion removal,
OS pin, action-version change, dependency lock, arbitrary retry or workflow dispatch.

Ten focused control-flow/workflow tests passed on Python 3.12.8 with installer and
Playwright API mocks; YAML parsing, Python AST and both Bash-loop syntax checks
passed. Removing preflight, hiding failure or removing readiness gates caused
assertion failures in three negative controls; restored tests passed 10/10. The
mutation harness cleared bytecode caches to avoid same-size rapid-edit cache reuse.
These are not real downloads, APT execution, a native browser launch, GitHub's
condition evaluator or full repository validation. Covering CI remains required.
README, root indexes and the 020 overview were reviewed; this dated correction
provides current browser provisioning/gating guidance while preserving history.
Local runlocaltests.sh still requires users to provision their own dependencies;
its behavior is unchanged. Both deliverables, Stage 2 and 009.7 remain open.
