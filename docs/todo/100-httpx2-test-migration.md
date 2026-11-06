# 100 - HTTPX2 test migration

[Back to TODO index](../../TODO.md)

## SG-TODO-010 - Migrate HTTP-client tests to HTTPX2

- Status: in progress; implementation prepared for this delivery, validation pending.
- Requested: 2026-11-06, including [skip ci] for the migration push.
- Priority, owner and deadline: not assigned.
- Scope: direct HTTPX2 ASGI fixtures, shared test requirements and CI/local setup documentation. Runtime requirements and Python 3.10 application support remain unchanged; test environment requires Python 3.11+.
- Dependency: install requirements-test.txt and Playwright Chromium in the selected test environment; CI remains Python 3.14/Node 22.

### Prepared changes

Replace FastAPI TestClient in test_admin_split_runtime.py with httpx2.AsyncClient/ASGITransport and isolated async unittest methods, retain existing assertions and add HTTPX2 type assertions. Add requirements-test.txt and use it for CI dependency installation and cache inputs. No sys.modules patch, alias_httpx call, fallback to legacy httpx, runtime change or separate CI dispatch is introduced.

### Acceptance and validation remaining

- [ ] Install requirements-test.txt in a fresh Python 3.11+ environment without explicitly installing legacy httpx; record interpreter and resolved dependency versions.
- [ ] Run the three AdminSplitRuntimeTests methods through tools/run_split_tests.py and verify all assertions and resource cleanup.
- [ ] Run bash runlocaltests.sh --python <test-environment-python> --no-publish and inspect all five suite summaries/logs, including skipped checks.
- [ ] Confirm configured future CI can install the shared requirements and execute the migrated fixture; the requested skip means no covering CI outcome is claimed for this push.
- [ ] Review actual results and resolve failures before marking completed; attach tested commit/result locations when available.

Preparation reviewed live sources, the static adapter, CI setup and existing assertions; no installation, syntax execution or test run was performed for this migration. Unavailable execution does not mean tests passed. See [testing handover](../handover/020-ci-and-tests.md#httpx2-test-migration---2026-11-06). SG-TODO-009 remains independently proposed.
