# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: in progress; Admin activation delivered/CI verified; Storage stages 1-4 delivered; activation stage 5 prepared, delivery/CI pending.
- Requested and five-commit Admin plan approved: 2026-11-02.
- Admin activation: 9f1b14ae99d3b297f4557f05f7f72485ab674d56, features/perplexity.
- Priority, owner and deadline: not assigned.

All eight Admin fragments are below 20,000 bytes. Activation serves one identical
classic-script response at /static/admin.js using both static mounts. The tracked
monolith is a marker; legacy source-reading fixtures use an assembled temporary
checkout and separate HTTP tests exercise the production adapter. Details and hashes:
[Admin handover](../handover/050-admin-script-split.md).

### Admin acceptance remains separate

- [x] Deliver eight unchanged parts and verify exact original reassembly.
- [x] Verify run 41584927496 attempt 1 reports success for exact Admin activation SHA.
- [ ] Review detailed static HTTP/browser/startup evidence for acceptance.
- [ ] Verify deployed permissions and complete source-reader/test compatibility.
- [ ] Obtain final Admin refactor acceptance.

Seven local source/reader/runner methods passed; FastAPI HTTP fixtures only compiled
locally. On 2026-11-03 run.json at
430574c584162099c61168cd680b0422479c1541/ci-results-41584927496-attempt-1 reported
workflow/tests-job success for 9f1b14ae99d3b297f4557f05f7f72485ab674d56. Syntax/import,
unittest, pytest, JavaScript and standalone browser/audit steps report success.
This is inspected workflow metadata, not review of every assertion/authenticated path.
No new CI dispatch is needed. SG-TODO-005 is separately reopened for dependent-button
visibility. SG-TODO-006 descriptive labels remain undelivered here; SG-TODO-004 stays
on hold. Manifest, documentation and CI logs are not code-refactor targets.

### Storage sequence and activation

1. Fields: a9da32439b01529ab6deba8242b48593d95be594.
2. Schema/migration: 2a651004a7870de461cce32f5dcffd56b91a2aa6.
3. Records/encounters: 8ed072c3cd3be53474a77cc9267bd7708f0d7638.
4. Operations: 0c8f1c9a95763bf8729d775f4596de68835cabf6.
5. Native compatibility facade and adapted/integrated tests: prepared, approval and CI pending.

Stages 1-4 left runtime unchanged; stage 5 intentionally activates the staged methods.
Original 38 method bodies and seven field definitions remain pinned to pre-split ASTs;
SCHEMA_VERSION=8, SQL, transaction boundaries and backup order do not change.
New test-only reference builder replaces monolith blob guards; production uses native
imports/inheritance only. Each complete Storage source file is <=20,000 UTF-8 bytes.

Thirteen local methods passed: eleven consolidated preparation methods, native
dispatch/file-size checks and constructor-failure cleanup. The new file-backed v8
persistence/reopen test compiled but was not run locally. Existing full migration,
backup, feature, SQLite/domain and service suites remain configured in normal CI.
No Storage CI evidence has been inspected. Limited fixtures and mocked effect
boundaries are not full application or migration acceptance.

- [ ] Deliver stage 5 after exact bound approval; record actual SHA after success.
- [ ] Inspect activation CI for its exact SHA, including migration/backup and v8 tests.
- [ ] Diagnose/fix failures through separately approved corrective commits.
- [ ] Verify deployed whole-tree startup, persistence and upgrade behavior.
- [ ] Obtain Storage acceptance and retain unfinished Admin checks.
- [ ] Review remaining oversized source files before closing SG-TODO-008.

See [Storage handover](../handover/240-sqlite-storage-split.md) for architecture,
fixture limitations, deployment instructions and validation evidence. Use normal CI;
no skip directive or workflow dispatch. Each external write needs bound approval.
