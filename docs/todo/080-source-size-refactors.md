# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: in progress; Admin activation delivered/CI verified; Storage five stages delivered; user reports manual runbook passed; activation CI failed on AST fixture compatibility; corrective tests/docs prepared.
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

### Storage sequence and validation

1. Fields: a9da32439b01529ab6deba8242b48593d95be594.
2. Schema/migration: 2a651004a7870de461cce32f5dcffd56b91a2aa6.
3. Records/encounters: 8ed072c3cd3be53474a77cc9267bd7708f0d7638.
4. Operations: 0c8f1c9a95763bf8729d775f4596de68835cabf6.
5. Native facade activation: 266487f8d8b605610db11e837f3f26fcdfc7f7f3.

Stages 1-4 left runtime unchanged; stage 5 activates native modules. Original 38
method bodies and seven field expressions are pinned; schema v8, SQL, transactions
and backups do not change. Each complete Storage source file <=20,000 UTF-8 bytes.

On 2026-11-03 the user reported successful manual Admin runbook execution. Inspected
CI run 41602398857 attempt 1 tested exact activation SHA above and failed: 1,004
unittest tests, 12 AST-reference failures. The standalone connection audit repeated
the same failures, with zero unclosed connections. Syntax/import, pytest and JS steps
passed; inspected v1/v2 migration and file-backed v8/reopen tests passed. Details:
[Storage handover](../handover/240-sqlite-storage-split.md). Evidence lives in
ci-results-41602398857-attempt-1 at 2e5d1d4ecedc3e88fa5bd3a565e49fbaa11660fb.

The fixed fingerprints depended on ast.dump's Python-version-specific treatment of
empty lists. Failure reproduced on 3.14. Prepared test-only stable serializer keeps
both original pins unchanged. Four regression methods passed on each of Python
3.12 and 3.14, including rejection of changed SQL/field definitions. This is eight
focused test executions, not a rerun of the full corrected CI/application suite.

- [x] Deliver all five agreed Storage stages.
- [x] Record user-reported successful manual runbook execution.
- [x] Inspect activation CI and diagnose the reference-fixture failure.
- [ ] Deliver test-only canonicalization fix after exact bound approval.
- [ ] Inspect corrected CI for its exact SHA; diagnose any remaining failures.
- [ ] Obtain final Storage acceptance after green CI; retain unfinished Admin checks.
- [ ] Review remaining oversized source files before closing SG-TODO-008.

Use normal CI; do not downgrade Python, replace accepted hashes, remove guards or
skip tests to obtain green results. No workflow dispatch or skip directive. Each
external write needs bound approval; no corrective SHA exists before delivery.
