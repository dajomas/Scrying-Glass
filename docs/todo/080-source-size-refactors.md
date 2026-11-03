# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: in progress; Admin activation delivered/CI verified; Storage stages 1-3 delivered; operations stage 4 prepared, delivery/CI pending.
- Requested and five-commit Admin plan approved: 2026-11-02.
- Activation: 9f1b14ae99d3b297f4557f05f7f72485ab674d56 on features/perplexity.
- Priority, owner and deadline: not assigned.

All eight Admin fragments are committed below 20,000 bytes. Increment 5 activates
one identical classic-script response at /static/admin.js, adjusts both static
mounts and source-reading test infrastructure, and replaces the tracked monolith
with a small marker. Legacy fixtures use an assembled temporary checkout; separate
HTTP tests exercise the production adapter. Details, hashes and earlier commit
identities: [handover](../handover/050-admin-script-split.md).

### Acceptance and remaining work

- [x] Deliver eight unchanged parts; verify their blobs and exact original reassembly.
- [x] Deliver activation and verify run 41584927496 attempt 1 reports success for its exact SHA.
- [ ] Review detailed static HTTP and browser/startup evidence as needed for acceptance.
- [ ] Verify deployed permissions and complete source-reader/test compatibility.
- [ ] Obtain acceptance before declaring the Admin refactor completed.
- [ ] Finish and separately validate python/scrying_glass_storage.py splitting.

Seven source/reader/runner methods passed locally during preparation. FastAPI HTTP
fixtures compiled but were not run locally. On 2026-11-03 the assistant inspected
ci-results-41584927496-attempt-1/run.json at 430574c584162099c61168cd680b0422479c1541:
workflow and tests job completed/success, head SHA 9f1b14ae99d3b297f4557f05f7f72485ab674d56.
Syntax/import, unittest, pytest, JavaScript and standalone browser/audit steps report
success. This is inspected workflow metadata, not a claim that every individual
log assertion or authenticated live path was reviewed. No new CI dispatch is needed.

The reported dependent-button issue reopens SG-TODO-005 separately; see its task.
SG-TODO-006's descriptive-label stage remains undelivered despite the user's
completion wording; do not confuse its scope with the Admin split. SG-TODO-004
remains on hold. Manifest, documentation and CI logs are not code-refactor targets.
Each external write still needs bound approval.

### Approved Storage sequence - 2026-11-03

1. Shared fields and five preparation tests: delivered as
   a9da32439b01529ab6deba8242b48593d95be594; unused by runtime.
2. Schema/migration and seven preparation tests: delivered as
   2a651004a7870de461cce32f5dcffd56b91a2aa6; unused by runtime.
3. Typed records/encounters and eight preparation tests: delivered as
   8ed072c3cd3be53474a77cc9267bd7708f0d7638; unused by runtime.
4. Campaign/roster/setup/application-state operations and tests: prepared; unused.
5. Activate small SQLiteStorage facade with native modules, compatibility exports,
   integrated regressions and operational docs; pending.

Local tests passed during preparation of delivered stages; no Storage CI evidence
has been inspected. Those limited fixtures do not cover constructor/file backups,
populated legacy migration, effects/lair persistence or later v4-v8 upgrades fully.
Do not infer full storage validation from source equivalence or successful delivery.

Stage 4 prepares a 12,218-byte operations mixin with 20 original bodies/signatures
unchanged. Eight local methods passed: AST/source/dependency guards; campaigns,
rosters/savepoints, setup naming/ordering/deletion, checkpoint rename, empty setup
copy/move/identity conflicts, mocked-boundary effect rewrites, application state.
Real SQLite fixtures bypass constructor and use original v3 base schema with the
actual snapshot table DDL for rename only, not a complete v5/v8 database. The
mocked effects test is not persistence/integration evidence. Details and hashes:
[Storage handover](../handover/240-sqlite-storage-split.md).

Every new code file <=20,000 UTF-8 bytes. Original 39,486-byte storage and callers
remain authoritative through stages 1-4. No SQL/schema/transaction/migration behavior
changes are authorized. Use normal CI, no workflow dispatch or skip directive.

- [ ] Review Storage CI for exact stage 1-3 commits.
- [ ] Deliver operations after exact bound approval, then review its CI.
- [ ] Activate facade, preserve public/underscore methods, field exports and lazy imports.
- [ ] Adapt preparation guards at activation; keep complete code files below the limit.
- [ ] Validate full storage/migrations/backups/transactions and service integration.
- [ ] Obtain final acceptance before closing SG-TODO-008; retain unfinished Admin checks.
