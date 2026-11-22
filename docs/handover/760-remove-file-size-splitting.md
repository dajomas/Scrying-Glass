# 760 - Remove the 20,000-byte file splitting (SG-TODO-035)

[Back to HANDOVER index](../../HANDOVER.md) · [Task 350](../todo/350-remove-file-size-splitting.md) · [050 Admin split (history)](050-admin-script-split.md) · [240 Storage split (history)](240-sqlite-storage-split.md)

On `features/claude`, 2026-11-22. The 20,000-byte limit was imposed for the Perplexity git
connector; the user asked to roll all splitting back. Decisions: categories A-E of the
inventory in task 350, category F left as it is, one commit.

## Changes

- **Admin script.** `static/admin.js` is the eight former fragments joined unchanged
  (132,480 bytes, byte-identical to the bundle the server assembled), with five comments
  that named fragments by number reworded. It is served as a plain static file:
  `python/scrying_glass_admin_source.py` and `_admin_static.py` are removed and the three
  `/static` mounts use `StaticFiles`. `static/admin/` is removed.
- **Test runner.** `tools/run_split_tests.py` is removed. CI (`tests.yml`) and
  `tools/runlocaltests.sh` run the commands directly; both already set `PYTHONPATH` to the
  root and `tests/`.
- **Tests that ran one fragment.** 14 Node files (3 of them shared fixtures) and 3 Python
  browser tests ran a single
  fragment against a mocked DOM. They now take the same lines from `admin.js` between two
  marker lines (the first lines of the former fragments), through the new helpers
  `tests/admin-source.cjs` and `tests/admin_source.py`; a marker must occur once and start
  a line. Tests that only search the text read the whole file. `test_admin_source.py` and
  `test_admin_split_runtime.py` (fragment order, size and adapter tests) are removed.
- **Storage.** Fields, schema, records and operations are back in
  `python/scrying_glass_storage.py` (40,246 bytes) as one class, `SQLiteStorageBase`.
  `SQLiteStorage` is the statblock revision mixin, the statblock save mixin and that base, in
  this order, because both mixins wrap base methods through `super()`;
  `StatblockOperationsMixin` no longer inherits the operations. All 43 attributes of
  `SQLiteStorage` resolve to the same bytecode as before (checked by comparing every
  attribute before and after). `tests/test_storage_facade.py` drops its split checks.
- **Documents.** `docs/Technical-Documentation.md` holds the three former topic files
  again (`docs/technical/` removed, links rebased; `test_technical_documentation_split.py`
  removed). Handover 380 holds the 17 sections that had moved to 381, 382 and 383 again,
  each at its former stub; 381-383 are removed. All links into both files resolve.
- **CI evidence chunks.** `tools/chunk_ci_evidence.py` is removed, with its calls in
  `tools/publish_ci_results.sh` and `tools/getworkflow.sh`. The publish workflow runs the
  collector scripts from `main`, so publish commits keep their `reader-chunks/` until this
  change is on `main`; nothing breaks before that.
- **Size checks.** The 20,000-byte assertions are removed from ten test files.
- **Docs.** README, DEPLOYMENT, task 080 (policy withdrawn), 350, TODO, handovers 025, 050,
  084 and 240.

Not changed: the October module split and `templates/admin/` fragments (they predate the
limit), `monster-image-choice.js` and the statblock service mixins (decision F), and the
historical handover texts that mention the old runner or the fragments.

## Evidence

- Full unittest suite here: 2,160 tests (2,170 before; the removed split tests). The same 92
  known FastAPI failures as before.
- Node: 84 files, all pass (here 10 of them failed before, as they read the 254-byte marker
  without the runner).
- Connection audit: 259 modules, the same 46 FastAPI module failures and connection counts
  as before.
- `compileall` of the server, `python/`, `web_html/`, `tests/` and `tools/` passes; shell
  scripts pass `bash -n`.

## Close-out - 2026-11-22

Delivered in dad62d4. Closed: CI 45048291349 green (2,372 tests; connection audit 259 modules, 0 failed); e2e 20261122T171600Z on dad62d4 and 20261122T183509Z on cbef741 (its results commit, same code): 137 passed, 0 failed each (Chromium and Firefox). CI ran the tests without the split runner for the
first time; e2e confirms the Admin page with `admin.js` served as a plain static file.
