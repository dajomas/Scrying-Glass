# 222 - Statblock persistence delivery

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage foundation](../handover/240-sqlite-storage-split.md#statblock-storage-foundation---2026-11-15) · [Activation/validation](../handover/030-validation-and-next-steps.md#statblock-startup-activation---2026-11-15)

## Task and status - 2026-11-15

SG-TODO-022.02b remains in progress with activation implementation included in
this delivery and covering CI pending. The 12:25 foundation/activation split
was refined by the user's 13:00 authorization for smaller direct-GitHub
preparatory commits with [skip ci] until the final activation commit. This is
that final code activation, with normal push CI and no skip marker. All work
stays on features/perplexity-statblock. No owner/deadline assigned. The parent's
model, typed-table, migration and lifecycle contracts are unchanged.

## Foundation and preparations

- Foundation 4a3f930cb4a0df109b06259bd9ca9a23f01638ee: covering Branch tests
  43709292836 attempt 1 succeeded; 1,704 main Python tests OK including all
  eight storage tests. Evidence is ci-results-43709292836-attempt-1. This is
  foundation evidence, not validation of activation.
- A: 6f8e44dfe7e1d9de166e21d61b697d34e3c89679 supplied the test-only v8
  constructor helper, its five tests and setup-lair v6 fixture. Four isolated
  helper checks passed locally; full production fixture validation is pending.
- B: a44727ef76f810ab593305033947c84eb9af26ae supplied lair-v5 and feature-v4
  fixture preparation, backup/account/FK assertions. Not executed locally.
- C: 1ccd5c36afb88a99b812b79bacd5a63c7c194654 supplied attack-v7 backup and
  AST cleanup preparation. Three isolated lifetime checks passed locally;
  they are not production migration or complete attack-suite verification.
- All three preparations intentionally used [skip ci]. Their complete combined
  validation is delegated to this final code commit's configured suites and
  connection audit. No separate workflow dispatch or workflow change.

## Activation implementation - supplied, validation pending

SQLiteStorage.SCHEMA_VERSION becomes 9. Both the accepted-version whitelist
and pre-account-schema guard include 9, so reopen does not recreate user tables.
The constructor calls upgrade_statblocks after statistics migration. Fresh
databases reach 9 without an upgrade backup; existing supported versions 1-8
retain the original pre-chain backup via the existing upgrade helpers. The
last 8-to-9 step is transactional with FK checks. Backup failure blocks that
step; failed DDL rolls back its new tables and version. Existing earlier
migration functions and base-v3 _create_schema fixtures remain unchanged.

Strict facade assertions require schema 9, not a range or skipped assertion.
Seven new production-constructor methods cover fresh/reopen, versions 1-8,
original backup reuse, account/setup preservation, statblock save/reopen,
backup-name collision, injected DDL/backup failure and future-version refusal.
These new/updated activation tests have not been executed locally. Source
review is not a pass. Inspect the actual covering run before closing 022.02b.

## Operational and acceptance gates

Startup now automatically upgrades supported existing databases. Stop the
application and back up the full storage directory, configuration and media
before deploying the complete matching python/ tree. Automatic SQLite backups
do not include all installation files. Ordinary v9 reopen must not make another
migration backup. Never roll back by lowering user_version: restore matching
pre-upgrade code and data. A failed late upgrade may follow committed earlier
steps in a legacy chain; retain and use its original backup for full rollback.

Require covering CI to pass all configured stages, including preparations A-C,
production startup tests, existing legacy/account/storage suites and the
explicit-close audit. Verify each result's commit and attempt. Until then this
unit and parent 022.02 remain in progress, not completed or fully validated.
Earlier dated notes saying startup remains 8 are historical and superseded by
this activation record; their evidence limits remain intact.

The fixture helper suppresses only statblock migration while constructing a
disposable old database, validates version 8/no statblock tables, restores the
function and closes invalid results. It remains single-threaded test tooling;
the migration test's real reopen and normal application startup are unpatched.

No statblock UI, listener, provider adapter, public projection or lifecycle
wiring is added. Runtime/setup/recovery/undo/checkpoint/copy/bundle preservation
and identity remapping remain 022.03. Source-model/cache/configuration and
authorization work retain their later units. No whole SG-TODO-022 closure.
Model history remains run 43707384985 attempt 1 at
0ed81a834d0973179c2c030eb84bb36b35c7e325, not activation evidence.
