# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: completed for the agreed Admin/Storage code-refactor scope; user accepted both as done on 2026-11-03.
- Requested and five-commit Admin plan approved: 2026-11-02.
- Priority, owner and deadline: not assigned.

### Delivered code and acceptance

Admin activation: 9f1b14ae99d3b297f4557f05f7f72485ab674d56. Eight ordered UTF-8
fragments remain below the native 20,000-byte reader cap, with one classic-script
response and a tracked failure marker. Legacy source-reading tests use a disposable
assembled checkout. See [Admin handover](../handover/050-admin-script-split.md).

Storage sequence:

1. Fields: a9da32439b01529ab6deba8242b48593d95be594.
2. Schema: 2a651004a7870de461cce32f5dcffd56b91a2aa6.
3. Records: 8ed072c3cd3be53474a77cc9267bd7708f0d7638.
4. Operations: 0c8f1c9a95763bf8729d775f4596de68835cabf6.
5. Activation: 266487f8d8b605610db11e837f3f26fcdfc7f7f3.

The activation's AST-reference fixture failure was corrected in
75b870ef9a204981bc778ccbaaea23f96b3fcb56; continuity records report successful
corrective CI run 41608182802 against that SHA. The user reported the Storage
Admin runbook passed and subsequently accepted both refactors. This update does
not invent new authenticated/deployed checks or a fresh review of every assertion.
See [Storage handover](../handover/240-sqlite-storage-split.md). The earlier
prepared/undelivered-fix and final-acceptance checklist entries are superseded.

### Size policy and final code audit

New code files: maximum 20,000 bytes. Existing code files: tolerated up to 25,000
bytes; the 5,000-byte margin is tolerance, not a target. The native Admin reader
still requires at most 20,000 bytes per fragment.

The live audit at 9703102f1929aedd1887c17f1d7b4a8996dfc04b found no code above
25,000 bytes. Existing service_state.py (20,578) and test_sqlite_storage.py
(22,281) are within tolerance and need no size-only split. CI logs are temporary
evidence, not code-refactor targets. No additional code refactor remains in the
accepted scope; SG-TODO-004 remains on hold.

### Follow-up documentation and packaging maintenance

The user requested the technical-document split and retirement/removal of the
historical package manifest in a separately agreed two-commit maintenance
sequence. The documentation index and three topic files preserve the original
content/anchors; runtime preflight no longer depends on any manifest. Its physical
deletion is a separately bound housekeeping action, not unfinished Admin/Storage
refactoring. Four mocked preflight methods passed locally; documentation
reassembly/anchor checks were performed during preparation. New regression tests
are included, but full application/CI/live validation was not rerun for this
maintenance. Both agreed maintenance commits explicitly use [skip ci].
See [current-state handover](../handover/010-scope-and-state.md).
