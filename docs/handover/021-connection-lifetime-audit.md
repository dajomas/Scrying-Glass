# 021 - Connection-lifetime audit isolation

[Back to handover index](../../HANDOVER.md)

Current status: both audit-isolation and Chromium-provisioning maintenance records
are completed and closed at the user's request on 2026-11-13 at 13:17 CET.
[Accepted close-out and covering evidence](#maintenance-records-accepted-close-out---2026-11-13)
supersede the dated delivery/validation-pending and open-feature statements below.
The original repair/failure history and validation limits remain historical.

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

## Maintenance records accepted close-out - 2026-11-13

The user explicitly requested "Please close out the 2 maintenance records" at
13:17 CET on 2026-11-13. Both connection-lifetime audit isolation and Chromium
provisioning are completed and closed for their agreed maintenance scope. The
[task statuses](../todo/100-httpx2-test-migration.md#connection-lifetime-audit-maintenance---2026-11-11)
are reconciled in the same documentation-only change. Earlier delivery/covering-CI/
acceptance-pending language is superseded; no additional acceptance gate is added.

### Covering evidence and implementation review

- Branch tests 43419501886, attempt 1, on features/perplexity tests 7e2579efcd3fc2833498edb1bc6e5093612cbc5e. Job 131865652023 is completed/success; every configured provisioning/test stage succeeded. Evidence publication: 49822ee7cacfd3bc4e2bd520b98917aef036db2c, directory ci-results-43419501886-attempt-1. jobs.json was directly reviewed for the tested SHA, branch, attempt and step outcomes.
- reader-chunks/index-000001.jsonl.txt maps workflow.log to file-000038. Directly read part-000012.txt records headless-shell download and "Chromium headless launch/render preflight passed."
- Directly read part-000290.txt reports "Connection audit modules: 190; failed: 0" and "PASS: all audited modules passed and closed their tracked connections". It also records successful browser smoke: real Chromium, mocked HTTP/WS, no page errors. The count is audited modules, not unique tests or an invented aggregate connection total.
- Current tests/audit_connection_lifetime.py (blob e06aa7eed5d034b088df9f6a1855258e861f3a6d) retains the failed-initialization probe, fresh workers, tracking before discovery/imports, nonzero setup/assertion/leak handling and continuation. Audit-isolation delivery was 3358400abc08c9ae38aee50942fe7e6cb47a5cfc.
- Current tools/prepare_ci_browser.py (blob 8d25d90c479731e614860bea3d969a53f18b0226) retains download-first provisioning, mandatory headless DOM-text preflight, one optional native-dependency attempt and fatal failure handling. The existing workflow prerequisite gates were reviewed during the immediately preceding Stage 3 reconciliation; no workflow change is proposed here.

### Limits and remaining work

This is direct review of existing hosted evidence and implementation, not a new
local/hosted test execution, full reread of every test/module log or screenshot,
complete package inventory, real APT-fallback/DNS-failure test, authenticated
live-server test or guarantee of every runner's native libraries/fonts. Earlier
seven audit and ten provisioning focused-control results retain their original
local/mock scope. Process isolation does not claim to fix all possible within-module
fixture lifecycle faults or instrument child processes spawned by tests.

No agreed delivery, covering-validation or acceptance action remains for either
maintenance record. SG-TODO-010 and all already accepted feature scopes remain
closed. Deferred post-009 test-suite cleanup is separate and is not started or
closed by this update. Earlier broad feature-pending statements are superseded by
their own later accepted close-outs, including 570 for 009/009.7.

README and TODO/HANDOVER indexes retain accurate links/status and need no cosmetic
edit. Only this handover and the existing 100 task details change. Commit message
uses [skip ci]; no code/tests/workflow/runtime change, fresh execution, separate
dispatch, merge, deployment, new owner/deadline or blanket future-write approval.
