# 080 - Source-size refactors

[Back to TODO index](../../TODO.md)

## SG-TODO-008 - Split oversized code without behavior changes

- Status: in progress; four Admin source-pair increments delivered; activation prepared, approval/CI/live acceptance pending.
- Requested and five-commit Admin plan approved: 2026-11-02.
- Current preparation base: 76f9f7ffa9f28ccfcedb2570c413b76052e1fe11.
- Branch: features/perplexity. Priority, owner and deadline: not assigned.

All eight Admin fragments are committed below 20,000 bytes. Increment 5 activates
one identical classic-script response at /static/admin.js, adjusts both static
mounts and source-reading test infrastructure, and replaces the tracked monolith
with a small marker. Legacy fixtures use an assembled temporary checkout; separate
HTTP tests exercise the production adapter. Details, hashes and earlier commit
identities: [handover](../handover/050-admin-script-split.md).

### Acceptance and remaining work

- [x] Deliver eight unchanged parts; verify their blobs and exact original reassembly.
- [ ] Deliver activation and confirm generated HTTP bytes match the original.
- [ ] Review full CI, static HTTP and browser/startup evidence for the activation SHA.
- [ ] Verify deployment permissions and complete source-reader/test compatibility.
- [ ] Obtain acceptance before declaring the Admin refactor completed.
- [ ] Prepare and separately validate python/scrying_glass_storage.py splitting next.

Seven local source/reader/runner methods passed. FastAPI is absent locally; HTTP
fixture tests are prepared and compiled, not executed. Full suite and live behavior
remain pending. Normal CI must run; no workflow dispatch or skip is requested.
SG-TODO-006 stage 2 is paused; SG-TODO-004 remains on hold. Manifest, documentation
and CI logs are not code-refactor targets. Each external write needs bound approval.
