# 230 - Test-suite necessity and execution review

[Back to TODO index](../../TODO.md) · [Previous cleanup](200-test-suite-cleanup.md) · [Previous cleanup evidence](../handover/600-test-suite-cleanup.md)

## Task and status

SG-TODO-023 - ready for review, requested 2026-11-16. Record and investigate the
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
