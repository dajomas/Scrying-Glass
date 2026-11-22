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

[SG-TODO-001](../history/010-monster-lookup.md) and [SG-TODO-002](../history/020-monster-damage-effects.md) remain proposed and unrelated. The broader source split remains unfinished and inactive. Use normal CI, no skip marker and no extra workflow dispatch.

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
unobserved CI/commit identity is claimed. [Current tasks](../history/098-character-edit-feedback.md).

## Statblock startup activation - 2026-11-15

[Current task and gates](../history/222-statblock-persistence.md) · [Storage foundation](240-sqlite-storage-split.md#statblock-storage-foundation---2026-11-15).
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
for its agreed bounded scope. This entry and the [accepted task record](../history/222-statblock-persistence.md)
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

Ten unchanged Stage 2 contract tests at 831c94249de8ef057cdcdbd0ead673d97ef98923
specify reset, capture/restore/absence, copy/move/Save As, import remapping, private
fingerprints and rollback. They are not skips/expected failures and have not run
in this work. Stage 1 remains unvalidated. [Full historical preparation details](https://github.com/dajomas/Scrying-Glass/blob/5c8b4776c72a949cbecfef0f00194064a07fdc46/docs/handover/030-validation-and-next-steps.md)
retain exact earlier AST byte counts, test scopes and limitations; the following
summaries consolidate only this task's Stage 2 history, retaining section anchors.

## 022.03 Increment 2A recovery capture - 2026-11-15

b1754d78ada3e66780b0b426b8bd70483c4d3f50 provides typed checkpoint/undo
capture/load with independent owners, historical metadata and explicit empty maps,
scoped consistent reads, transaction/savepoint rollback and pruning/cascades.
Ten prepared tests were AST-parsed, not executed. Ordinary serialized private input
is not trusted. Capture is not restore/apply or full Stage 2 acceptance.

## 022.03 Increment 2B.1 fingerprints - 2026-11-15

1214bed0833ee312f305ce88937dae8f7d60170f routes recovery fingerprints through
canonical private metadata and prunes removed bindings. No-content hashes retain
the legacy algorithm; logs/turn markers stay excluded, revisions/times included.
Nine prepared tests were AST-parsed, not executed. The full comparison helper
remains unwired for arbitrary private-only transaction persistence. Older stale
undo digests are not automatically migrated.

## 022.03 Increment 2B.2 replacement kernel - 2026-11-15

5c8b4776c72a949cbecfef0f00194064a07fdc46 supplies an internal replacement-only
kernel, stored-row/revision checks and atomic tracker/reference writes. Historical
revisions do not replace destination revisions; unchanged content keeps metadata.
Nine prepared tests were AST-parsed, not executed. Surviving-content clearing is
rejected before tracker writes; durable counters and all-writer coordination remain
pending. Counter/ledger prototypes were not delivered. No production service was
wired by 2B.2. Source/caller authorization and confirmation remain service duties.

## 022.03 Increment 2B.3 production restoration - 2026-11-15

Baseline: 5c8b4776c72a949cbecfef0f00194064a07fdc46. FeaturesService now passes
trusted recovery images through the kernel for both checkpoint restore and undo.
The existing campaign/reference/retained-roster checks still precede writes.
Normalization retains private metadata via an explicit internal carrier, including
empty maps. The destination is the campaign/name setup or singleton unsaved-runtime
encounter, never a recovery row. Saved private metadata refreshes live state only
after kernel success; outer production transactions still own roster/runtime saves,
audit, history, feature revisions and memory/DB rollback. No new HTTP route,
permission policy, schema/migration, provider or workflow is introduced.

Repeated private restores advance destination revisions. Undo therefore rebases
only the immediate predecessor whose old after_digest matches the exact recovery
image, and only if restored tracker fields and private content digests match that
image. The SQL update is ID/campaign/kind/old-digest guarded and stays inside the
outer transaction. Nonmatching stale/foreign history stays stale; this is not a
general rewrite of older undo digests. Tracker-only undo preserves metadata.

Seven new regression methods cover kernel invocation/live refresh/JSON projection,
sequential private undo, mismatching predecessor rejection, tracker-only metadata,
clear rejection, late runtime-save rollback and unsaved runtime/setup isolation.
Executed: AST parsing of the two changed method snippets and new test module.
These tests have not run; no full-module/server import, model/storage/service,
authenticated HTTP/WS/browser or covering CI pass is claimed. Existing CI unittest
discovery includes the file, but this intermediate [skip ci] push intentionally
defers covering execution until the final Stage 3 code push. No separate dispatch.

Surviving-content clearing still fails closed with a conflict; the explicit-absence
contract is not claimed satisfied. Durable counter/clear/all-writer handling,
arbitrary private-only transaction save integration, expanded scope/restart/limit/
rollback execution, 2C/2D and Stage 3 remain open. Stage 1/2/022.03 are not complete
or accepted. README deployment guidance and existing root index links remain
applicable; deploy the matching complete tree only after required validation and
acceptance. No merge, deployment, release or whole-feature closure is implied.

## 022.03 Increment 2B.4 revision-counter foundation - 2026-11-15

Baseline: 8e4d625d7785275c935a3c40b5f45323de329801. This first increment
under the user's 18:20 request for remaining 022.03 adds durable per-stored-monster
counters to existing monsters_attributes rows, with a reserved private field and
versioned private scalar kind. No table, DDL, schema-version or migration changes.
The facade hides/validates these rows on reads, forbids ordinary counter input
and preserves them during stable-row attribute updates. Non-monster attributes
retain the old dispatch. Header revisions bootstrap older records lazily.

StatblockStorage uses paired optional allocation/recording hooks. Production
SQLite allocates max(header,counter)+1 after its existing ownership/revision checks,
revalidates complete final metadata and records the counter under the same save
transaction. Partial hook protocols fail; the original minimal header-only protocol
fixtures remain supported without gaining clearing capability. Overflow/decrease,
malformed private markers and ordinary reserved-field input fail closed.

Eight exact new ledger unit methods passed against real in-memory SQLite in an
isolated namespace using representative tables. They cover legacy bootstrap,
header absence, invalid integers/decrease/overflow, rollback, owner/cascade/FKs,
hidden decoding/input rejection and malformed/colliding marker rejection. These
are not production constructor/model/storage/service passes. Five additional
production tests are prepared, not run, for lazy bootstrap, header-absence tracker
preservation/privacy, prohibited input, failed/outer rollback and reopen. Header
deletions are controlled test simulations, not service clearing. New module/test
source and changed writer snippet AST-parse; full imports and covering suites
have not run. This updates the earlier blanket no-tests-executed wording only
for these eight isolated ledger methods, not any previous staged suite.

Adapter reattachment and counter-only row rebuild preservation remain next,
followed by trusted clear activation and arbitrary private-only save integration.
The current restore kernel still rejects surviving-content clearing. Do not claim
all writers or Stage 2 are complete. 2C/2D, bundles and covering final Stage 3 CI
remain open. Existing discovery includes the tests. Intermediate [skip ci] policy
remains; no dispatch, workflow edit, deployment or merge. 022.02 stays closed and
Stage 1 unvalidated. Parent/index status wording predating these increments remains
historical; the lifecycle task is the current detailed progress record.

Deploy only matching complete code/data after validation/acceptance. Older code
cannot decode the private ledger kind despite the unchanged schema number; do not
roll back code alone over ledger-bearing data. Retain full matching code/storage/
configuration/media backups. README whole-tree/backup instructions and existing
index links remain applicable; no cosmetic README/index edits are included.
