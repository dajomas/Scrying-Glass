# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: in progress; Admin activation delivered and CI outcome verified; live acceptance and SQLite split pending.
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
