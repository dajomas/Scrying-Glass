# 600 - Test-suite cleanup (SG-TODO-020)

[Back to handover index](../../HANDOVER.md)

Requested by the user on 2026-11-13: "Please clean up the tests, remove obsolete or double tests, if tests are no longer needed, remove them, see if tests can be consolidated or improved and make sure only those tests are in the suite that are still relevant". This is the deferred post-009 test-suite cleanup. The workflow is not changed.

## Baseline

From [Branch tests run 43419501886](https://github.com/dajomas/Scrying-Glass/actions/runs/43419501886) (for `7e2579ef`, success): unittest discovery ran 1644 tests with no skips; `tests/` held 280 test, fixture and script files. Every test in the suite was reviewed by file purpose. Duplicated test bodies were found by comparing function ASTs, and hash/count/version pins by searching for literal digests and sizes.

## Removed (obsolete)

- **Storage split oracle.** `tests/storage_split_reference.py` built an "original" storage class from the current storage modules, pinned by AST hash, and the six `test_storage_*_preparation`/`reference_canonical`/`split_runtime` modules compared the production class with that copy. Because both sides came from the same files, the parity checks could not fail on behaviour, and any storage edit broke the hash pins. The behaviour assertions are kept, run against `SQLiteStorage` only, in `tests/test_storage_facade.py`; the pins, the canonical-dump tests and the method-surface count are removed.
- **Admin fragment digests.** `test_admin_source_preparation.py` and `test_admin_source_complete.py` pinned the SHA-256 of each of the eight fragments and the assembled byte count, so every Admin change needed new hashes. They are replaced by `tests/test_admin_source.py`, which keeps the fragment inventory and order, the 20,000-byte limit, UTF-8, reader bounds, the runner/marker check and Node syntax checks.
- **Frozen content hashes.** The technical-documentation content hash and byte count (`test_technical_documentation_split.py`; the markers, size limit and index links are still checked) and the `#monsterUpload` form hash from SG-TODO-018 (`test_manual_monster_bonus_form.py`).
- **Asset version and count pins.** Pages get a fresh cache-busting token per render (`python/scrying_glass_asset_cache.py`), so `?v=N` pins and the fixed Admin script count (46) protected nothing. `test_candidate_review_asset_wiring.py` is replaced by `tests/test_admin_asset_wiring.py` (every local script/stylesheet in the Admin templates and `templates/users.html` exists and is included once; dependency order; every static file and template fragment is at most 20,000 bytes, except the assembled `static/admin.js`). The composition inventory now compares the loaded page with the template script tags instead of a count; the five tests that only tested that helper are removed.
- **Duplicates.** `test_bughunt_round13.py::test_unrelated_value_error_keeps_its_type` repeated `test_bughunt_round10.py` exactly. `tests/admin-message-timeout-browser.py` repeated `admin-message-timeout.test.cjs` with a real 5-second wait and test-only CSS.

## Converted to unittest

Standalone scripts that ran outside unittest reporting are now regular modules:

- `tests/audit_log_clear.py` (needed a `patched` argument) -> `tests/test_activity_log_clear.py`, calling the production `AdminActivityMixin.clear_activity_log` instead of an AST copy. It is the only coverage of clearing the activity log.
- `tests/audit_round3_check.py` -> two classes in `tests/test_bughunt_round3.py` (setup-name suffixes, malformed/duplicate log entries, stable log IDs, CSV validation, monster HP bounds), using the production `scrying_glass_monster_csv` functions. The unknown-nested-state check already exists in `test_sqlite_storage.py` and was not copied.
- `tests/browser_smoke_272cc73.py` -> `tests/test_browser_smoke.py`. It is the only browser coverage of the Client display page and the User management page.

## Consolidated

- Six `test_campaign_*_feedback_composition.py` files -> `tests/test_campaign_feedback_composition.py` (21 tests).
- Three setup composition files -> `tests/test_setup_feedback_composition.py` (10 tests).

## Kept

The bug-hunt regression modules, feedback Node tests, browser fixtures and provider tests still test current behaviour and are kept. `test_death_save_validation_2ba6607.py` and `test_slug_truncation_82860c4.py` use pytest-style functions and are named in the workflow's pytest step, so they cannot be renamed or merged without a workflow change (not allowed). `runlocaltests.sh` and the workflow still carry an unused `patched` special case for the removed `audit_log_clear.py`; it has no effect.

## Result and validation (local, 2026-11-13)

Unittest discovery collects 1638 tests (was 1644) with no import failures; `tests/` holds 265 files (was 280). Executed through `tools/run_split_tests.py`: `tests/audit_connection_lifetime.py` ran every unittest module (179 modules, 0 failed, all tracked SQLite connections closed), and the new or changed modules passed under pytest. Node tests were not changed and not rerun. CI and user acceptance are pending.
