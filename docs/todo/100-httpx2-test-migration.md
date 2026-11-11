# 100 - HTTPX2 test migration

[Back to TODO index](../../TODO.md)

## SG-TODO-010 - Migrate HTTP-client tests to HTTPX2

- Status: completed, 2026-11-06, at the user's explicit close-out request after review of successful local and covering CI evidence.
- Migration: 11835d414d701f0fc6a3a701def29594cab287a3.
- Validated layout-test correction: df16cc0ee798a07b5c219c3db06de54c913cb84f.
- Requested: 2026-11-06; [skip ci] was requested for the migration push and separately for this documentation close-out, not the corrective test push.
- Priority, owner and deadline: not assigned.
- Scope: direct HTTPX2 ASGI fixtures, shared test requirements and CI/local setup documentation. Runtime requirements and Python 3.10 application support remain unchanged; test environment requires Python 3.11+.
- Dependency: install requirements-test.txt and Playwright Chromium in the selected test environment; CI uses Python 3.14/Node 22.

### Delivered migration

FastAPI TestClient in test_admin_split_runtime.py was replaced with httpx2.AsyncClient/ASGITransport and isolated async unittest methods, retaining existing assertions and adding HTTPX2 type assertions. requirements-test.txt is used for CI dependency installation and cache inputs. No sys.modules patch, alias_httpx call, fallback to legacy httpx, runtime change or separate CI dispatch was introduced.

### Historical failed local run - 2026-11-06

Evidence commit: 72923ec4e34a6a1065332495015a0a768fe7a98f. Tested source commit: e7b229caa04494ec5a2b4fed7a0d66301359a12e. Run directory: local-tests-e7b229c/run-20261106T103855Z-QWqmWA. Environment: Python 3.14.7, Node 22.23.2, WSL2 kernel; suite=all, completed=1. This is published local evidence, not a CI run.

The available main unittest log explicitly reports all three AdminSplitRuntimeTests methods as ok. Pytest reports 43 passed; all 37 JavaScript commands returned zero. Compilation and server import returned zero. The overall exit code is 1: unittest and the connection audit failed. The complete audit log reports 1,022 tests with two monster-name minimum-width failures (137.265625 versus 137.281 CSS px at 768/375 viewports) and 673 opened connections with zero without explicit close. The main unittest log was truncated by the connector before its final failure summary, so no claim that its only failures were those two is made.

### Delivered layout-test correction

The user requested fixes and a GitHub push after reviewing the failed run. The test-only correction replaces exact minimum-width comparison with a bounded 1/32 CSS px tolerance plus finite/positive measurement guards. Seven added numeric guard tests cover the observed values, exact/wider widths, the tolerance boundary, just-beyond-boundary rejection, real deficits, nonfinite values and zero minimum. They passed in isolation during preparation; browser/full-suite validation came from the subsequent evidence below. Production CSS and accepted SG-TODO-007 layout behaviour remain unchanged.

### Successful validation and acceptance - 2026-11-06

- Local evidence commit: f584f4394cf155e37d7f8214f7da0afc78d89542.
- Local run: local-tests-df16cc0/run-20261106T105201Z-HwuKfD, covering df16cc0ee798a07b5c219c3db06de54c913cb84f.
- Reviewed summary.tsv: all commands returned zero, including syntax/import, unittest, pytest, 37 JavaScript scripts and six standalone checks. exit-code.txt is 0. The connection audit reports 1,029 tests, OK, 673 opened connections and zero without explicit close.
- CI: Branch tests run 42205835274, attempt 1, exact head df16cc0ee798a07b5c219c3db06de54c913cb84f, completed/success. The tests job and every configured dependency-installation and test step report success.
- CI evidence commit: 715ad2d6e22f88e8708e2cf9e3ae49069f9aa495, folder ci-results-42205835274-attempt-1.
- CI reader index maps workflow.log to reader-chunks/file-000007. Parts 5 and 10 show installation from requirements-test.txt with Python 3.14.10 and resolved httpx2 2.16.0, httpcore2 2.16.0, playwright 1.64.1, pytest 9.2.0, FastAPI 0.162.0 and Starlette 1.10.0. Node setup reports 22.23.4.

Completed acceptance checklist:

- [x] Verify CI installation from shared test requirements and record resolved versions. The installation log is not a complete package inventory proving legacy httpx absent; closure accepts direct HTTPX2 usage with no declared/explicit legacy-httpx test installation, not an environment-purity guarantee.
- [x] Observe all three migrated AdminSplitRuntimeTests methods pass in published local output, with subsequent successful covering suites.
- [x] Validate the corrected name-layout fixture through successful local and CI unittest runs; its existing viewport/name/activity cases remain in the test.
- [x] Review a complete successful local command summary and connection audit against the corrective commit.
- [x] Review successful CI installation and configured test-step conclusions against that same commit.

These are automated fixture/suite results, not authenticated deployed-server testing, proof that every runner package was inventoried, or a Python-version compatibility matrix. HTTPX2 client cleanup is exercised by completed fixture tests; the SQLite connection audit's explicit-close count is a separate check, not an HTTP-client connection audit. Expected mocked exception logs do not turn successful commands into test failures. The user's 2026-11-06 close-out request accepts completion within the stated scope and limitations.

### Documentation close-out

TODO.md and the testing handover are updated with this closure. No application, test or workflow code is changed and no tests are rerun for the documentation-only close-out. The commit includes [skip ci] as explicitly requested; no workflow is separately dispatched, and no workflow-run state for the close-out commit is inferred from the marker. README and HANDOVER.md retain accurate descriptions/index links and remain unchanged. SG-TODO-009 remains independently proposed.

See [testing handover](../handover/020-ci-and-tests.md#verified-localci-success-and-sg-todo-010-close-out---2026-11-06).

## Connection-lifetime audit maintenance - 2026-11-11

Status: in progress; module-isolation repair and seven focused regression cases
prepared and passed locally; exact GitHub approval/delivery and full repository
validation remain pending. This independent maintenance correction does not reopen
the accepted SG-TODO-010 migration or close any Stage 2/009.7 work.

Preserve the failed-PRAGMA closure assertion, all unittest module discovery and
explicit-close leak detection. Run each discovered test*.py module in a fresh
process with tracking installed before imports; retain nonzero status for setup,
import, assertion or leak failures and continue later modules. No browser skip,
event-loop monkeypatch in production audit, application change or workflow edit.

Acceptance still requires review of the full connection audit on the revised
repository, including real storage/async/browser fixtures and per-module leak
counts. Successful equivalent local or hosted evidence is sufficient for its
covered scope; both are not required. Missing Chromium remains a separate failure,
not a passing or waived browser test. [Repair evidence and limits](../handover/021-connection-lifetime-audit.md).
