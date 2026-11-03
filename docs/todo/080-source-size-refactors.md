# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: in progress; Admin activation delivered/CI verified; Storage fields increment 1 delivered; schema increment 2 prepared, approval/CI pending.
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
- [ ] Prepare and separately validate python/scrying_glass_storage.py splitting next.

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

1. Stage scrying_glass_storage_fields.py and field equivalence/isolation tests;
   original storage and all callers remain unchanged.
2. Stage schema/migration module with extraction-equivalence tests; unused.
3. Stage typed-record/encounter module with equivalence tests; unused.
4. Stage campaign/setup/application-state module with equivalence tests; unused.
5. Activate the small SQLiteStorage facade using native Python modules, preserve
   original imports/field exports, add integration regressions and update operations.

The user approved this five-commit sequence and requested increment 1 on 2026-11-03.
Every new code file must be at most 20,000 UTF-8 bytes. The original 39,486-byte
module stays authoritative through increments 1-4; it is replaced at activation.
No schema version, SQL, transaction or migration behavior changes are authorized.

Storage increment 1 was delivered as a9da32439b01529ab6deba8242b48593d95be594.
Its seven field definitions and five preparation tests remain unchanged. Their
local preparation checks passed, but no Storage CI result has been inspected.

Current increment 2 stages a 10,076-byte StorageSchemaMixin with the original
_create_schema, convert_campaign_references and _upgrade bodies/signatures/static
decorator unchanged. Seven local tests passed: AST/descriptor parity, real SQLite
base-schema parity, empty v1/v2-to-v3 upgrade parity, post-DDL migration rollback,
reference deep-copy/error parity and size/dependency/original-source guards.
The constructor, backup files, populated legacy migration and later v4-v8 upgrades
are not covered by these new local fixtures. Full CI/activation coverage is pending.

- [ ] Review fields increment CI for its exact commit.
- [ ] Deliver and review schema increment CI for its exact commit.
- [ ] Stage records and operations with unchanged method bodies/equivalence checks.
- [ ] Activate compatibility facade and keep complete source files below the limit.
- [ ] Validate full storage/migration/transaction/service behavior and obtain acceptance.

See [Storage handover](../handover/240-sqlite-storage-split.md) for evidence and
activation constraints. Runtime and consumers remain unchanged in increment 2.
Use normal CI; each stage needs its own bound approval. This does not complete SG-TODO-008.
