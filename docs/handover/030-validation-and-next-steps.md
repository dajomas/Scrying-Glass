# 030 - Open validation and next steps

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01.

## Inspected CI evidence

| Run, attempt 1 | Tested commit | Main Python tests | Failures | Errors |
|---|---|---:|---:|---:|
| 41295839260 | 72e1ae7023bb33e47aee3fe8b554786717d1fb1f | 861 | 35 | 10 |
| 41297160008 | aefa5457fcfa84bf918890660ab2f782901a1679 | 866 | 24 | 8 |
| 41298125937 | 897f07907ea9c2e3ddf17f992827590cd3af724a | 873 | 16 | 7 |
| 41298914669 | 0c55cabb37002c4424c46adeacc3b91a00cb2ca4 | 881 | 7 | 7 |
| 41301945996 | 0bbdecc5f7c5e7d5dcb70ea2448f01324e0974bd | 887 | 3 | 7 |
| 41315942451 | 8b2a3fac577522e0860a3fe32bd13443bbac94c1 | 888 | 0 | 5 |
| 41318275558 | f031ccf9185ad0ab0e9ad7b4673adf1f7fb5f7ad | 888 | 0 | 4 |
| 41319342579 | 7b0967c06913272856e83eb0d675850f3c430ae5 | 889 | 0 | 0 |
| 41320226799 | 8dc2a0f239699935432c126fbdc5ca6433e73b90 | 889 | 0 | 0 |

All listed workflows concluded failure. Dependency installation and syntax/server import checks passed. Main unittest discovery passed in the latest two runs. In run 41320226799, unittest ran 889 tests in 36.869s, pytest passed 43 cases in 1.46s, and the entire JavaScript stage passed. Only standalone Python browser/audit checks failed. Audit rediscovery repeats tests; it is not another set of unique cases.

## Evidence provenance

Historical run 41301945996 evidence was at `96680deb1d84321043a99bde242b85f4ac18e8e9`. Run 41315942451 was inspected at `6fbe4c1578a7b4f7725a87adb2c1ea2613946e76`, including selected parts 65-71; its full 101-part log was not reconstructed. Pytest passed 43 cases in 0.90s.

Run 41318275558 was inspected at `1cfb256cb090ca3834eb2f61d12eca23ce67d4f9`, including parts 18-19 and 70. All 13 account tests passed; pytest passed 43 cases in 1.09s. Its full 100-part log was not reconstructed.

Run 41319342579 was inspected at `8f07bbf8a936794c9aa46ac234625a760b845231`: selected parts 46-49 and 65-66 verified viewer tests and Python results. JavaScript investigation inspected parts 67-88, identifying the two missing-window fixture failures. Pytest passed 43 cases in 1.03s. Its full 91-part log was not reconstructed.

Latest evidence: `ci-results-41320226799-attempt-1/` at `e70ca3a63de7cfe03fef116e157b832904517d0d`. The preceding inspections read reader metadata/index, run metadata and selected parts, including Python summaries in 65-66, repaired JavaScript checks in 77 and 84, and the complete standalone-stage region in 85-87. No full 88-part log reconstruction or SHA-256 verification is claimed.

The connection audit rediscovered 889 passing tests but reported `Connections opened: 611; without explicit close: 3` and returned failure. Browser smoke failed its Default campaign-heading assertion. Log-clear and round-three audits explicitly passed; the message-timeout browser script reported no failure. See [standalone diagnosis](160-standalone-audit-and-smoke.md).

## Historical intermediate result

The continuation request supplied run 41305437829, attempt 1, tested `5159b33d3f86f7e9bf027d8b8650970cdce47661`: 890 main tests, zero assertion failures, seven errors; ten composed-router unit tests passed; overall workflow failed. That summary was not independently reconstructed in the pytest repair preparation. Later inspected runs supersede its counts.

## Focused repair status

- [WebSocket fixture](060-websocket-regression-fixture.md): 35 module tests passed in run 41297160008.
- [Display connection](070-display-connection-fixture.md): 18 module tests passed in run 41298125937.
- [Lookup diagnostics](080-monster-lookup-diagnostics.md): 17 diagnostic and 15 provider tests passed in run 41298914669.
- [Stats fallback](090-stats-fallback-fixture.md): 12 class tests passed in run 41301945996.
- [Composed routers](110-composed-campaign-routers.md): ten unit tests passed in run 41319342579; production routing unchanged.
- [Pytest execution](120-pytest-module-imports.md): verified by the latest passing 43-case step; pending-CI note superseded.
- [Accounts migration](130-accounts-migration-fixture.md): 13 account tests passed in run 41318275558; pending-CI note superseded.
- [Viewer ownership fixtures](140-viewer-ownership-fixtures.md): browser, real lifespan and ACL tests passed in run 41319342579; pending-CI note superseded.
- [Renderer VM window](150-renderer-vm-window.md): eight recovery and 14 lair-presentation checks passed in run 41320226799; entire JavaScript stage passed; pending-CI note superseded.
- [Standalone fixtures](160-standalone-audit-and-smoke.md): explicit-close and complete viewer-snapshot repair; focused local evidence only, full audit and Chromium execution pending CI.

## Remaining validation

Inspect normal push-triggered CI. Require the connection audit to report zero connections without explicit close and retain its nonzero exit on any leak/test failure. Require the smoke test to complete the campaign-heading, reconnect identity, mobile layout and final page-error checks. Do not infer those later checks passed from a payload-only local reproduction.

Continue verifying clean unittest, pytest and JavaScript stages. No passing full workflow or repaired audit connection total is predicted. If further failures appear, investigate rather than suppressing assertions or the audit.

[SG-TODO-001](../todo/010-monster-lookup.md) and [SG-TODO-002](../todo/020-monster-damage-effects.md) remain proposed and unrelated. The broader source split remains unfinished and inactive. Use normal CI, no skip marker and no extra workflow dispatch.

## Stage 2 modal-import integration - 2026-11-11

Earlier sections preserve November 1 history, not current phase/task closure.
The last verified covering run 43082738853 attempt 1 succeeds for
8841bf0b99d3e48352f3f785819b759b4e180624; it does not validate this later change.

The effective CSV and saved-setup import owners now live in complete 040. CSV
retains both success destinations with distinct region-aware targets; setup JSON,
filters, fallback campaign and confirmation wording remain. Errors persist and
recover by matching identity; success lasts 3s, and update failures have separate
persistent no-replay guidance. Sessions protect close/reopen and pending opens;
revision tracking keeps newer files/options. Busy guards span request and refresh,
while Cancel and editing remain usable. Already-sent imports cannot be revoked.

The earlier physical-move draft is superseded: 030 is unchanged, and its older
setup assignments/CSV closer source remain inactive after 040's explicit bindings
and later function definition. This is effective runtime migration, not removal
of every inactive legacy producer; inventory/retirement reconciliation stays open.
No new asset, script count, template, workflow, Join/server-rule or 060 changes.
The tail from exportActivityLogCsv onward is byte-for-byte preserved. 040 is
17,595 bytes, SHA-256
9b33377efa3980e60d7400ae4ad525802f87c711cecc28d9ad39e5d9e5c9416b.
Only 040's digest and bundle length (125,031) change in the pin test; all other
pins, eight-part order, UTF-8/size/tamper guards and admin.js marker remain.

Ten grouped Node cases passed with complete 040 and the exact production feedback
controller (blob c4a82d73b21f4657da651ce45f76003c3348a6ef), scoped adapter,
mock DOM/FormData/transport and deterministic timers. Four removed safeguards
(duplicate, scope, revision, region target) caused assertion failures; restored
run passed 10/10. Fragment syntax passed; original reconstruction matched blob
13931d020bc8fee49915c45b7701641e8cca4b5f. The earlier 15 draft cases are not added
to this current grouped count. Native form validity/serialization/events, actual
030/040 composition, browser focus, full bundle/reader/runner/tamper, live-server,
manual/accessibility and covering repository validation were not executed here.
Registry-loader setups() error ownership is unchanged. Existing CI discovers the
new .cjs and retains browser suites, but that is not new-path native acceptance.

Normal push-triggered CI applies without a skip marker or separate dispatch.
Complete approval/delivery, covering results/corrections and bounded acceptance
remain pending. README and root indexes retain accurate links/open scopes and are
unchanged. Stage 2 and both deliverables remain open; no merge/deployment or
unobserved CI/commit identity is claimed. [Current tasks](../todo/098-character-edit-feedback.md).
