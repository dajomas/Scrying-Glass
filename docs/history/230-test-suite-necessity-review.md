# 230 - Test-suite necessity and execution review

[Back to history index](../../HISTORY.md) · [Previous cleanup](200-test-suite-cleanup.md) · [Previous cleanup evidence](../handover/600-test-suite-cleanup.md)

## Task and status

SG-TODO-023 - first half (items 1 and 2) delivered 2026-11-21; second half (items 3 to 7)
delivered 2026-11-22 on `features/claude` ([handover 740](../handover/740-test-consolidation.md));
completed and closed 2026-11-22 after CI 45001741568. See below.
Requested 2026-11-16. Record and investigate the
initial test-review suggestions; this task is not an instruction to delete tests
or change CI immediately. No owner, deadline, deletion target or speedup target is
assigned. This is the next numbered TODO, not an agreed interruption of the current
[SG-TODO-022 lifecycle delivery order](223-statblock-lifecycle.md).
SG-TODO-020 remains completed/closed; its accepted removals and evidence stand.

## Baseline and evidence limits

The initial read-only review examined selected source at
 ea8b4c7342ba2b86e8c2ca7b07892fdf4ce7f7b9, including .github/workflows/tests.yml,
tests/audit_connection_lifetime.py, tests/test_connection_lifetime_audit.py,
tests/test_statblock_stage2_contracts.py, tests/test_statblock_setup_saving.py,
tests/test_statblock_setup_saving_http.py, tests/test_admin_asset_wiring.py and
tests/test_death_save_validation_2ba6607.py. It was not a full per-test necessity
audit. No timing measurements, safe deletion count, percentage reduction, fresh
suite execution or 3A CI conclusion was established by that review.

The preceding reviewed main-suite baseline was 1,962 unittest tests for
 ecd56957f9f147ac36d5196c23aec96d8889129c in Branch tests 43941792616 attempt 1.
That is not a verified count/result for the newer 3A commit. Keep unique test cases,
parameter cases, modules, repeated executions and separate runner totals distinct.
Do not add unittest, pytest, audit reruns and Node/browser totals as unique coverage.

## Review work

1. Inventory and measure first. Establish an exact commit and collection inventory
   for unittest, pytest, Node, standalone/browser/audit and separately run E2E.
   Record per-stage and useful per-module/test durations, setup/subprocess/browser
   overhead, skips, failures and execution multiplicity. Compare under matching
   environments; do not infer runtime savings from test count alone.
2. Review duplicate CI execution first. Ordinary unittest discovery runs before the
   standalone step invokes audit_connection_lifetime.py, which reruns unittest
   modules in isolated subprocesses with SQLite tracking. Evaluate one authoritative
   connection-audited pass with individual results and a smaller combined-process
   interference check. This is a proposal, not a decision to remove either pass.
   Preserve import-time/test-body leak detection, failed-initialization closure,
   async/browser isolation, import/setup failure reporting and nonzero exit status.
3. Consolidate genuinely overlapping service-level scenarios. Compare
   test_statblock_stage2_contracts.py Save As preservation/unsaved-live-content cases
   with test_statblock_setup_saving.py's new-destination/live-content/metadata-refresh
   scenario. Map every useful assertion to its surviving test before removal;
   preserve graph/reference fidelity, HP, revision, ownership/bindings, source
   isolation, active/last-setup reference, reload and rollback assertions.
4. Keep distinct layers distinct. Route tests add registration/model validation,
   real authorization decisions, origin checks and post-lock ownership/role/session
   rechecks; service tests do not replace them. Preserve production notification,
   transaction/rollback, privacy, persistence/migration and revision-exhaustion gates.
5. Review brittle implementation-text assertions individually. In
   test_admin_asset_wiring.py, investigate the literal paneNotification( ban against
   surviving behavioral feedback tests. Do not classify all static tests as obsolete:
   asset existence, uniqueness, dependency order and agreed file-size limits still
   protect current contracts. Compare normalized ASTs to find exact bodies, then
   inspect semantics; matching names or overlapping lines alone are insufficient.
6. Preserve pytest-only collection. test_death_save_validation_2ba6607.py contains
   parametrized function tests not executed as unittest cases. Review overlap between
   malformed-counter matrices and atomicity examples without losing transition
   precedence, type/range validation or validation-before-target-access assertions.
   Inspect the other explicit pytest module too before any workflow consolidation.
7. Build on the previous cleanup. Its removed self-derived oracles, frozen hashes,
   version/count pins and exact duplicates must not return. Historical bug-hunt
   filenames or old preparation docstrings alone do not prove tests are unnecessary.

## First half: measurements and decision (2026-11-21)

Implementation group 2 on `features/claude` ([handover 680](../handover/680-ci-parallel-audit.md)).
Measured on green CI 44888887657 (commit 13d36ef, one `ubuntu-latest` job, 13.4 minutes of
steps):

| Stage | Inventory | Duration |
| --- | --- | --- |
| Setup (checkout, Python, Node, dependencies, Chromium, syntax/import) | - | 27 s |
| Combined unittest pass (`discover`, one process) | 2,308 tests, 13 skipped | 327 s |
| Pytest regression modules | 2 modules, 43 cases (pytest-only) | 3 s |
| JavaScript tests (`node --test`, one process per file) | 83 files, 665 tests | 46 s |
| Connection audit (`audit_connection_lifetime.py`) | the same 2,308 tests in 254 module processes | 393 s |
| Other standalone scripts | 2 scripts | 1 s |
| E2E (`tools/run_e2e.sh`, run separately by the user) | 137 tests, Chromium and Firefox | 17 min |

The audit is a second complete execution of every unittest case, not extra coverage.
Its output is one OK/FAILED line and a connection count per module, not per-test lines.

Both passes have caught failures the other could not:

- CI 43636503802 failed only in the combined pass:
  `test_monster_source_image.test_edit_rejects_a_tampered_token` passed in its own process
  but failed after other modules had run (state leaking between modules).
- CI 44885862376 failed only in the audit: `test_statblock_import_workers.py` left two
  SQLite connections open (skip in `setUp` after the fixture opened the database).

Options put to the user: keep as is; two parallel jobs; audit as the only pass plus a small
combined check; full audit less often. **Decision (user, 2026-11-21): two parallel jobs.**
Both passes stay complete. `.github/workflows/tests.yml` now has a `connection-audit` job
with its own setup that runs only the audit, in parallel with the `tests` job, whose
standalone step skips the audit script. Expected wall time is about 7.5 instead of 13.5
minutes, for about one extra minute of runner setup; to be confirmed by the first run.

The second half (items 3 to 7: consolidation) stays open and follows the feature work.

## Second half: dispositions (2026-11-22)

Implementation group 5 on `features/claude` ([handover 740](../handover/740-test-consolidation.md)).
Before: 2,157 unittest tests (local run of c725ae5); after: 2,155 (two removed, none added);
pytest modules and Node files unchanged. A normalized-AST scan of every `test_*` body
(docstrings dropped, one-liners ignored) found no identical test bodies, so the previous
cleanup's removals have not returned (item 7).

| Item | Path / test | Disposition | Rationale and surviving assertions |
| --- | --- | --- | --- |
| 3 | `test_statblock_stage2_contracts` `test_save_as_uses_unsaved_live_content_without_replacing_source` | **Consolidated** into `test_statblock_setup_saving` `test_new_save_as_uses_live_content_and_refreshes_destination_metadata`, then removed | Every assertion now lives in the surviving test: live private content and revision 1 in the new setup, source private content unchanged, live state equals the saved content; the one it lacked (the source setup's tracker rows keep HP 12, the new setup has the live HP) was added. A mutant whose Save As also overwrote the source rows passes the old surviving test and fails the new one (`1 != 12`). |
| 3 | `test_statblock_stage2_contracts` `test_save_as_preserves_content_in_the_new_setup` | Keep | Only test that unedited content with its reference graph, digest and supporting definitions is copied intact, with the exact result payload and the source unchanged after a reload. |
| 3 | other `test_statblock_setup_saving` tests (ordinary save, existing destination, omission, rollback after roster/live refresh) | Keep | Distinct scenarios: owner history and stale metadata, destination revision history, omission refusal, rollback. |
| 4 | route/HTTP tests vs service tests (for example `test_statblock_setup_saving_http`) | Keep | Different layers: registration and model validation, authorization, origin and post-lock rechecks are not covered by service tests. |
| 5 | `test_admin_asset_wiring` `test_review_asset_has_no_untyped_pane_calls` | **Removed** | A text ban on `paneNotification(` in `monster-refresh-review.js`. Behaviour already covers it: switching the review-load error, the apply error or the success message to `paneNotification` each fails `test_monster_refresh_review_browser`/`test_monster_refresh_startup_browser` (2 failures + 1 error, 1 error, 1 failure). |
| 5 | other `test_admin_asset_wiring` tests (asset existence, uniqueness, size limits) | Keep | Current contracts, as the task says. |
| 6 | `test_death_save_validation_2ba6607` (pytest) | Keep | `test_counter_contract` (18 cases) is type/range per field; `test_invalid_counters_rejected_without_side_effects` (8 cases) mostly pairs a valid with an invalid counter and checks state and database stay unchanged; plus valid transitions and validation before target access. Merging would save about two cases and blur precedence coverage. |
| 6 | `test_slug_truncation_82860c4` (pytest) | Keep | The only check that a truncated slug stays canonical at the 80-character boundary for both slug kinds, plus loadability; `test_bughunt_round3` covers unique suffixes only. |

Not done, by design: no broad per-module audit beyond the named paths, no runner change
(the CI layout was decided in the first half), no speed-up claimed (two fast service tests).

## Acceptance and validation requirements

- Produce a path/test-level keep, consolidate, replace or remove disposition with
  rationale, surviving assertions and explicit uncovered gaps. No arbitrary goal of
  getting below 2,000 tests; fewer methods alone is not a coverage improvement.
- For any removal/consolidation, demonstrate the relevant regression still fails
  when the protected behavior is broken, where practical, or document the limitation.
  Keep security and data-loss protections unless an equivalent replacement is proven.
- Before runner/CI changes, demonstrate useful per-test reporting, correct collection,
  no silent omission and failure propagation for leaks, import/setup failures and
  async/browser failures. Retain combined-process checks where they detect distinct
  interference that per-module isolation would hide.
- Compare before/after case inventories and measured durations, separating eliminated
  executions from eliminated cases. Do not claim a speedup until measured.
- Run affected focused checks and the covering full configured suites for any later
  implementation; record exact commit/run/attempt, results, skips and checks not run.
  Changes to tests/tools/workflows are not documentation-only and normally run CI.
- Update relevant TODO/handover evidence with any implementation; obtain exact-payload
  approval for each later write. No tests/workflows are changed by registering this
  task, and no existing acceptance or SG-TODO-022 status is changed.

## Registration scope

This registration changes only this Markdown task and its TODO.md index entry.
README and the handover index remain applicable; link to the previous cleanup rather
than duplicate or reopen its history. Documentation-only commit uses [skip ci]; no
tests are rerun, workflow edited or manually dispatched, or fresh CI success claimed.
