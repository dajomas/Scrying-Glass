# 222 - Statblock persistence delivery

[Back to history index](../../HISTORY.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage foundation](../handover/240-sqlite-storage-split.md#statblock-storage-foundation---2026-11-15) · [Accepted close-out](../handover/030-validation-and-next-steps.md#sg-todo-02202-accepted-close-out---2026-11-15)

## Task and status - accepted close-out, 2026-11-15

SG-TODO-022.02, including 022.02a model/validation and 022.02b persistence/
migration/startup activation, is completed and closed for its agreed bounded
scope. The user explicitly signed off and requested close-out on 2026-11-15
at 13:48 CET, after the covering activation CI was reviewed. This acceptance
is user-reported; no step-by-step live command output or additional manual
test results were supplied, and no assistant live-server execution is claimed.

Overall SG-TODO-022 remains in progress and is not yet a usable statblock
viewer/import feature. 022.03 is the next planned unit and remains unimplemented;
022.03-022.16 are not closed by this acceptance. All work remains on
features/perplexity-statblock. No merge, deployment or release is authorized
by this documentation close-out. No owner/deadline assigned.

This progress/acceptance record supersedes earlier 022.02-ready/in-progress/
activation-CI-pending notes in the parent, index and dated handovers. The
parent's model, typed-table, migration, limit and remaining lifecycle contracts
are unchanged; unfinished work has not been silently removed or relabelled done.

## Delivered scope and history

- 022.02a model/validation: b26ccc8acbfc0774c984b66afc75c98cf09b7578;
  publication-allowlist regression correction at
  0ed81a834d0973179c2c030eb84bb36b35c7e325. Earlier covering run 43707384985
  attempt 1 succeeded; this remains model history, not activation evidence.
- Storage foundation: 4a3f930cb4a0df109b06259bd9ca9a23f01638ee. Covering
  Branch tests 43709292836 attempt 1 succeeded, with 1,704 main Python tests OK
  including all eight storage tests. Seven typed relations, callable backed-up
  8-to-9 upgrade, atomic save/load/replacement, revisions, references and scalar
  optional-field presence were delivered without startup activation.
- Preparation A: 6f8e44dfe7e1d9de166e21d61b697d34e3c89679 supplied the
  test-only v8 fixture helper, its five tests and setup-lair v6 fixture.
- Preparation B: a44727ef76f810ab593305033947c84eb9af26ae supplied lair-v5
  and feature-v4 fixtures with backup/account/FK assertions.
- Preparation C: 1ccd5c36afb88a99b812b79bacd5a63c7c194654 supplied attack-v7
  backup and AST-extracted resource cleanup checks. Earlier local preparation
  executed four isolated helper tests and three isolated lifetime tests; they
  were never treated as complete production migration or live-server evidence.
- Final startup activation: 28d75d08febf5b595afe8145b4097410eb987986.
  SQLiteStorage.SCHEMA_VERSION is 9, both constructor version guards include 9,
  and upgrade_statblocks runs after statistics migration. Strict facade schema
  assertions require 9, not a range or skipped assertion. Seven production-
  constructor methods cover fresh/reopen, versions 1-8, original backup reuse,
  account/setup preservation, statblock save/reopen, collision, DDL/backup
  failure, constructor cleanup and future-version refusal.

The initial 12:25 foundation/activation split was refined by the user's 13:00
authorization for bounded direct-GitHub preparations A-C with [skip ci] until
final code activation. The final activation omitted the skip marker and ran
configured CI. No workflow change or separate dispatch was used for skipping.

## Covering validation - verified

Branch tests run 43713643326 attempt 1 tested
28d75d08febf5b595afe8145b4097410eb987986 on features/perplexity-statblock
and completed successfully at 2026-11-15 12:35:16 UTC / 13:35:16 CET.
Evidence is published in ci-results-43713643326-attempt-1. Main unittest ran
1,717 tests and finished OK. Detailed log review confirmed all seven new
startup methods and all eight storage-foundation methods passed. Syntax/server
import, main Python, pytest regression, JavaScript and standalone browser/audit
stages all reported success. Full-log and artifact downloads succeeded; artifacts
are run-scoped, not guaranteed attempt-specific. No exhaustive artifact review
or new local/full-suite execution is claimed for this close-out.

Current implementation, test and workflow tree identities were compared with
the tested activation revision during close-out preparation and match. This
documentation-only commit does not change runtime, tests, configuration or
workflows and does not constitute a new validation run. The covering CI gate
and user's explicit 13:48 CET acceptance satisfy this unit's closure gates.

## Retained operational guidance and remaining work

Startup automatically upgrades supported existing databases. Stop the process
and back up full storage, configuration and media before deploying matching
code. Automatic SQLite backups are not full installation backups. Existing
versions 1-8 retain the original pre-chain backup; fresh databases reach 9
without an upgrade backup; ordinary v9 reopen must not make another one.
The last 8-to-9 step is transactional with FK checks. Earlier successful legacy
steps can already be committed when a later step fails. Rollback restores
matching original code and data, never merely lowers user_version.

The legacy-fixture helper remains single-threaded test tooling: it suppresses
only statblock migration during disposable fixture construction, verifies v8/no
statblock tables, restores the function and closes invalid results. Real reopen
and normal startup are unpatched. Earlier local/runtime evidence limits remain.

No statblock UI, listener, provider adapter, public projection or complete
lifecycle wiring is delivered by 022.02. Runtime/setup/recovery/undo/checkpoint/
copy/bundle preservation and identity remapping remain 022.03. Private snapshots
must not enter public Client Display payloads or overwrite SG-owned fields.
Source adapters, runtime configuration/limits, preparation/apply authorization
and viewer work retain their later units. Do not infer completion of overall
SG-TODO-022, deployment acceptance for unspecified environments, or exhaustive
authenticated/browser/provider verification.

This close-out uses [skip ci] under the standing documentation-only policy.
No tests were rerun, no workflow was separately dispatched and no new CI outcome
is predicted or required merely for this unchanged-code acceptance record.
