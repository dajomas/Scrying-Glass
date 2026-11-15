# 030 - Open validation and next steps

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-15. Earlier dated sections retain their historical scope.

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

## Statblock startup activation - 2026-11-15

[Current task and gates](../todo/222-statblock-persistence.md) · [Storage foundation](240-sqlite-storage-split.md#statblock-storage-foundation---2026-11-15).
This record supersedes earlier dated SG-TODO-022 notes saying startup remains
schema 8 or activation is not wired. Other task history above is not reopened.

Final activation sets SQLiteStorage.SCHEMA_VERSION=9, extends both constructor
version guards through 9 and calls upgrade_statblocks after upgrade_statistics.
Existing v1-v8 migration ordering, transaction/savepoint helpers, scalar field
exports and base-v3 _create_schema remain. Fresh installs create all seven typed
statblock tables without a migration backup. Existing databases keep the
original pre-chain database backup; the new step reuses it instead of backing
up an already-upgraded intermediate version. Ordinary v9 reopen is idempotent
and must not recreate users/account_migration or generate another backup.
Historical staging comments in foundation modules describe their original
delivery state; the facade constructor is authoritative for activation wiring.

Stop the single process and back up the entire storage directory, configuration
and media before deploying the complete matching Python tree. Startup upgrades
existing supported databases automatically. Automatic SQLite backups alone are
not a full installation backup. If the new step fails, its DDL/version roll
back and constructor error handling closes the connection. Earlier successful
steps in a legacy migration chain can already be committed: full rollback
restores matching original code/data from the original backup, not a lowered
user_version. A failed backup must prevent the new migration from starting.

Preparation commits A 6f8e44dfe7e1d9de166e21d61b697d34e3c89679,
B a44727ef76f810ab593305033947c84eb9af26ae and
C 1ccd5c36afb88a99b812b79bacd5a63c7c194654 used [skip ci] as requested.
This final code commit omits that marker and relies on configured normal push
CI. No workflow change or separate dispatch. Review the actual covering commit,
attempt and complete stage conclusions; do not infer success from publication.

Strict facade schema assertions move from 8 to 9; no range/skip replaces them.
Seven new production-constructor test methods exercise fresh/reopen, all
supported legacy versions 1-8 with original backups, account/setup preservation,
statblock persistence over reopen, backup-file collision, injected DDL rollback
and constructor cleanup, backup denial and future-version rejection. Preparatory
helper/resource checks retain their narrower scopes. New and changed activation
tests were reviewed but not executed locally; neither syntax review nor earlier
foundation run 43709292836 attempt 1 validates this activation. Full CI, including
the connection audit and preparations A-C, is pending. No live deployment,
authenticated HTTP/browser or provider coverage is claimed.

No statblock UI, provider conversion, public-state projection or whole lifecycle
preservation is delivered here. The internal API accepts stored monster-row IDs;
future callers must enforce campaign/encounter authorization. Runtime/setup/
recovery/undo/checkpoint/copy/bundle integration remains 022.03. SG-TODO-022.02b
and parent 022.02 remain in progress until the activation evidence is reviewed.
README backup/runtime guidance and root index links remain accurate and unchanged;
indexed task 222 carries the current operational/status details.

## SG-TODO-022.02 accepted close-out - 2026-11-15

The user explicitly signed off on 022.02 and requested closure/documentation
on 2026-11-15 at 13:48 CET. 022.02, including 022.02a model/validation and
022.02b typed persistence/migration/startup activation, is completed and closed
for its agreed bounded scope. This entry and the [accepted task record](../todo/222-statblock-persistence.md)
supersede only the earlier 022.02 pending/ready/in-progress notes in the parent,
indexes and dated handovers, including the activation-pending paragraphs above.
Their original evidence and limitations remain historical, not reopened gates.

Covering Branch tests 43713643326 attempt 1 tested activation revision
28d75d08febf5b595afe8145b4097410eb987986 on features/perplexity-statblock
and completed successfully at 2026-11-15 12:35:16 UTC / 13:35:16 CET.
Published evidence is ci-results-43713643326-attempt-1. Main Python ran 1,717
tests OK. Detailed log review verified all seven new production startup methods
and all eight storage methods passed; syntax/server import, Python, pytest,
JavaScript and standalone browser/audit stages all succeeded. Full logs and
artifacts downloaded successfully. Artifacts are run-scoped, not necessarily
attempt-specific; no exhaustive artifact/screenshot review is claimed.

Code/test/workflow identities compared during close-out match the tested
activation revision, including python/ tree 3aeca9cdf0164a7622d5abace1e7590750a3d73f,
tests/ tree 3f8e04641f800e96fd9a68e5b1e3d9c6d1636afc and .github/ tree
76cf2730ff173cb654012206b05c2fa9e29f1d14. No new runtime, test, configuration,
dependency or workflow change is included in this documentation close-out.
No tests were rerun or fresh CI outcome inferred. The commit contains [skip ci]
under the standing documentation-only policy; no separate workflow dispatch.

The sign-off is explicit user acceptance, not assistant live-environment
execution. No step-by-step live command output, additional manual results,
exhaustive authenticated/browser/provider verification, merge, release or actual
deployment operation is implied. Schema-9 backup/rollback guidance above remains
applicable: restore matching pre-upgrade code/data, never lower user_version.

Overall SG-TODO-022 remains in progress; no usable statblock viewer/import UI,
provider conversion or complete lifecycle preservation is claimed. 022.03 is
the next planned unit and remains unimplemented; runtime/setup/recovery/undo/
checkpoint/copy/bundle preservation and local-ID remapping stay there.
022.03-022.16 remain open/pending with their existing requirements intact.
README runtime/capability descriptions and HANDOVER index links were reviewed
against unchanged live identities and remain accurate; no cosmetic edits.

## 022.03 Stage 2 validation preparation - 2026-11-15

The user requested Stage 2 validation/tests at 15:35 CET after mutation-privacy
test delivery 5ecf122b7e9a2c7decde8dd26167d93c7e4711d0. This advances test
preparation, not Stage 1 acceptance. Dated 022.03-unimplemented notes above are
history; current partial wiring and gates are in the [lifecycle task](../todo/223-statblock-lifecycle.md).

Ten new contract tests specify reset, checkpoint capture/replace/explicit absence,
copy/move/Save As, imported binding remapping, private-aware fingerprinting and
restore rollback. A supporting-definition/reference graph exercises more than a
header-only snapshot. Copy checks independent stored ownership and source
immutability; restore checks increasing destination revision rather than blindly
reusing historical revision. Move is tested as preservation of the moved existing
encounter, not creation of a second owner. This is not complete undo/access/limit
or HTTP/browser coverage. No production implementation changes are included.

Executed: AST parsing of the 9,286-byte test file, containing ten ordinary test
methods. Tests have not run. Source inspection identifies unfinished capture/
restore/copy/import/fingerprint paths; expected failures are predictions, not
observed run results. Tests have no skip/expected-failure decorators and must
be satisfied by implementation, not suppressed. No Stage 2 or Stage 1 pass or
completion is claimed. See the task for implementation order and remaining gates.

Intermediate [skip ci] instruction remains in force until the final Stage 3
code push. No workflow change, dispatch, schema change, deployment or merge.
README runtime guidance and existing HANDOVER/TODO index links remain applicable
and unchanged. 022.02 remains accepted/closed; 022.03 and overall 022 remain open.

## 022.03 Increment 2A recovery capture - 2026-11-15

Contract baseline: 831c94249de8ef057cdcdbd0ead673d97ef98923. Increment 2A
wires FeatureStorage capture/load for both checkpoint and undo images to typed
private content. A new recovery helper validates internal attribute maps before
the capture transaction and inserts independent snapshot rows using the existing
typed writers. Captured historical revision/time/digest are retained, not reset
or confused with the later current-destination restore revision policy.

FeatureStorage.save_snapshot now owns a transaction/savepoint covering encounter,
metadata, tracker rows, private graph, character snapshot rows and pruning. Load
owns a consistent scoped transaction; campaign/kind/ID rejection precedes private
reads. Explicit empty recovery maps are retained even with no statblock rows.
Ordinary serialized private fields are not accepted as trusted capture input.
Pre-statblock empty reads are compatible; private writes still require schema 9.
No new relations, migration, auth policy, HTTP payload or listener is introduced.

Ten prepared regression methods cover checkpoint/undo full metadata and reference
round trips, explicit absence without source guessing, independent ownership,
invalid-graph/raw-field rejection, late-write and nested rollback, scope/ID guards,
pruning/deletion cascades and text above default preparation limits. Executed
checks: AST parsing for helper (2,347 bytes), storage module (7,641 bytes) and
tests (8,000 bytes). Tests have not executed; no live model/storage/service/HTTP/
WS/browser or CI pass is claimed. Existing Stage 2 contract tests are unchanged.

2A does not implement restore/apply, explicit live-content clearing, fingerprints
or private-only change detection, setup copy/Save As or import remapping. Those
remain 2B-2D and some existing contracts can still fail until implemented. Capture
code delivery is distinct from validation or Stage 1/2 acceptance. Final Stage 3
covering CI remains pending; intermediate message includes [skip ci] by instruction.
No workflow change/dispatch, merge, deployment, release or whole-feature closure.

The lifecycle task is consolidated without removing remaining gates; earlier
preparation history stays in handovers/Git. README and root-index identities were
verified unchanged and remain applicable; deploy the complete matching Python
tree only after the staged feature's required validation/acceptance.

## 022.03 Increment 2B.1 fingerprints - 2026-11-15

2A baseline: b1754d78ada3e66780b0b426b8bd70483c4d3f50. This bounded first
2B increment routes production recovery fingerprints through canonical validated
private metadata and prunes removed-monster bindings at feature reconciliation.
Legacy no-content hashes retain their algorithm; activity logs/turn markers stay
excluded. Recovery hashes intentionally include private revision/prepared_at,
unlike the content digest. Equivalent snapshot-local IDs/order canonicalize alike.
Older undo after_digest values that no longer match are stale, not rewritten.

A private-aware full comparison helper is supplied for the later transaction
save integration, not activated in the save gate here. Restore/apply, explicit
clearing, metadata-preserving restore normalization, destination revisions and
private writes/live-metadata refresh remain pending. Merely detecting private
changes is not sufficient to claim they persist through ordinary saves.

Nine prepared tests cover legacy hashes, private-only/metadata differences,
canonical IDs/order, log exclusions, copy/privacy isolation, bad input and pruning.
Executed: helper/test AST parsing (1,782 and 5,374 bytes). Tests have not executed;
no repository/model/storage/service/transport/CI pass claimed. No new schema,
auth policy, public snapshot payload, workflow edit/dispatch or deployment.

The task is condensed with prior history retained here/Git and all unfinished
gates explicit. Existing README/index guidance remains applicable. Intermediate
[skip ci] remains required; covering final Stage 3 CI and acceptance are pending.
Stage 1, Stage 2 and 022.03 are not complete or accepted by this delivery.

## 022.03 Increment 2B.2 replacement kernel - 2026-11-15

Baseline: 1214bed0833ee312f305ce88937dae8f7d60170f. The new internal kernel
accepts validated PrivateEncounterState recovery images and checks exact
encounter-local row/revision descriptors under the write transaction. It removes
historical revision fields before invoking the existing destination writer. Changed
content receives the current destination's next revision; identical content keeps
current metadata. Tracker and reference writes roll back together on failure.
Deleting a monster still cascades, but surviving-content clearing is rejected
before tracker writes. This is not production FeaturesService restoration wiring.

Clearing exposed a dependency: durable revision counters must be honored by all
private writers to avoid reusing an old revision after a clear. Ledger/counter
prototypes were explored during preparation but are not part of this write. The
first bounded kernel deliberately fails closed for unsupported absence instead
of claiming safe clearing. Coordinated counter/clear/writer behavior, service
authorization/confirmation, character-roster persistence, live-state refresh and
transaction save-gate integration remain pending. No new HTTP restore channel.

Nine prepared tests cover historical replacement, unchanged metadata, rejected
clearing, stale/foreign bindings, failed content-write rollback, monster deletion,
raw input and invalid graphs. Executed: AST parsing of kernel/test source (2,960
and 5,251 bytes). Tests have not run; no model/storage/service/HTTP/WS/browser/CI
pass claimed. No schema, migration, auth-policy or workflow changes. Existing
Stage 2 contract assertions remain unchanged and can still fail until completion.

The existing lifecycle task records the bounded scope and remaining gates.
README and index guidance remain applicable. This intermediate commit contains
[skip ci]; final Stage 3 covering validation and Stage 1/2 acceptance remain open.
No merge, deployment, release or whole-feature completion is implied.
