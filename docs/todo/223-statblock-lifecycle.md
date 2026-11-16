# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Current handover](../handover/140-viewer-ownership-fixtures.md#3a-private-bundle-roundtrip---2026-11-16)

## Status and delivery rules - 2026-11-16

022.02 and bounded 2B/2C/2D remain accepted/closed. Increment 3A is in progress:
implementation and eight native regression methods were delivered, but first covering
CI 43955177051 attempt 1 failed. The isolated Store harness correction below passes
locally; corrected covering CI and acceptance remain pending. Increment 3B and final
lifecycle acceptance remain required. SG-TODO-022 Stage 1/2, 022.03 and overall 022
remain unaccepted; 022.04-022.16 remain pending. No usable viewer/import UI, merge,
deployment, release or whole-feature completion is claimed.

This current 3A status supersedes dated unimplemented-bundle/next-Stage-3 wording in
the TODO index and preceding delivery records, not any unfinished criterion.
Code/test deliveries run normal push CI without [skip ci]. Every external write
requires its own complete bound approval. The old intermediate-2C skip instruction
is not an exception for 3A, 3B or corrections. Documentation-only writes keep [skip ci].

## Preserved history, accepted criterion maps and contracts

[Complete preceding lifecycle task](https://github.com/dajomas/Scrying-Glass/blob/e8546fb1ec14e4163faa89c326592948d6d81c46/docs/todo/223-statblock-lifecycle.md)
and [complete preceding handover](https://github.com/dajomas/Scrying-Glass/blob/e8546fb1ec14e4163faa89c326592948d6d81c46/docs/handover/140-viewer-ownership-fixtures.md)
retain all dated increment/correction identities, failures, counts, original headings,
2B/2C/2D criterion maps, assertion-level evidence and limits, including earlier immutable
archives. These records are retained requirements/evidence, not deleted backlog.

Private graphs remain encounter/combatant-scoped. Internal metadata stays outside
ordinary JSON and survives deepcopy; serialized fields/plain-dict attributes confer
no authority. Trusted stored reads are permissive; new imports use operator limits.
Digests exclude revision/time/self-digest, recovery fingerprints include metadata.
Ordinary omission cannot clear; removed rows cascade; explicit trusted recovery alone
can clear. Header-only protocols cannot clear. Durable ledgers/hidden bindings remain
monotonic through clear/re-add and counter-only rebuilds. Raw SQLiteStorage.save_setup
remains tracker-only, not a source-copy channel. No public clear flag, new permission
or provenance promotion is added by bundles.

## 2C bounded acceptance reconciliation - 2026-11-16

Accepted for 2C.1, 2C.2a-b, 2C.2c.1-3 and 2C.3a-c. Tested
7c703c4d66f63bd765a780f8e5ed6a2cd465521c; green Branch tests 43933600072 attempt 1;
publication dae492f2e95bc378d73425f22dd5e85d9c681215. Thirteen 2C.3c methods OK,
1,956 main unittest OK, 43 selected pytest passes; audit 218 modules, zero failed.
The eight-group assertion map and original evidence limits remain at the exact
preceding-task link above. This bounded acceptance is not expanded or reopened.

## 2D bounded acceptance reconciliation - 2026-11-16

Accepted close-out e8546fb1ec14e4163faa89c326592948d6d81c46, correction 9 implementation
14ad1d3075f4e737c38270ea2a9734fd1f5b9ad3 and boundaries
 ecd56957f9f147ac36d5196c23aec96d8889129c. Green Branch tests 43941792616 attempt 1;
publication 0742d36fa6186b3764d9b3c6e4153c20f6071b08. Seventeen import methods OK within
1,962 main tests; 43 selected pytest passes; audit 219 modules, zero failures.
The six-group assertion map remains at the exact preceding-task link above. Seeded-
session ASGI is not login/full startup; recording sockets are not real network/browser
proof; native fixture writes, observational spies and mocked/static checks retain
all recorded limitations. Inactive owned sources, existing superadmin policy and
zero-selection refresh semantics remain unchanged. No wider acceptance is inferred.

## 3A - complete private bundle roundtrip

Status: implementation and tests delivered; first covering CI failed; correction and
its covering validation remain pending. No 3A acceptance is recorded.

- Actual representation: version-2 campaign.json statblocks envelope with exact setup
  maps and encounter map. Version-1 tracker-only imports and empty exports remain.
- Validate incoming identities, graph structure, digests and provenance/credit URLs
  under server ModelLimits before allocating records. No request limit overrides.
- Fresh independent setup ownership and revision 1; remove imported revision/time;
  retain content/provenance/credits without online authenticity or fetch authority.
- Save the runtime private image into the Imported encounter checkpoint; restore
  through existing trusted recovery, preserve distinct saved/runtime graphs, reload,
  source isolation and ordinary/public/client projection privacy.
- Explicit aggregate rejection at 10 MiB including private content, never silent loss.
  Existing archive/media budgets remain. No separately referenced members chosen.
- Protected outer transaction plus late private DB failure/partial media-write cleanup.
- Eight new native service/SQLite test methods cover these paths. Local compile() passed
  for both complete Python sources; AST inventory counted eight. Zero native methods
  were executed here. Existing CI unittest discovery includes the new module; no
  workflow edit or manual dispatch is required. Await and inspect actual results.

The aggregate overflow regression lowers the manifest constant to exercise rejection;
it is not a measurement of all real-size boundary combinations. No HTTP/auth, real
WebSocket, exhaustive scheduling/platform, browser/E2E, provider or human visual proof
is claimed by the 3A fixture preparation. Full details: current handover above.

## Store harness correction and remaining validation - 2026-11-16

Covering run 43955177051 attempt 1 for ea8b4c7342ba2b86e8c2ca7b07892fdf4ce7f7b9
failed in main Python and standalone/audit stages. Inspected Store.connection errors
come from the isolated ZIP harness, which omitted new collaborators/transaction state.
Correction updates tests/test_bughunt_130f875.py only, plus these documentation records;
production transaction checks and private persistence remain unchanged.

Retain all original corruption/media/version checks, move the unsupported version to
3, retain version-2 missing-envelope rejection separately, assert guard enforcement
before writes and make the private carrier fixture refuse nonempty graphs. Locally,
20 isolated cases passed, 0 failures/errors/skips, against the exact blob-verified
production source. One separate guard-removal mutation produced the expected failing
regression. Compilation passed. These are isolated ZIP/media tests, not native/private/
HTTP/rollback proof. Full failure inventory, other possible failures, native suites and
corrected covering CI are still to be reviewed; do not declare the entire CI repaired.
[Exact preparation/execution evidence](../handover/140-viewer-ownership-fixtures.md#3a-store-zip-harness-correction---2026-11-16).
SG-TODO-023 remains separate; no tests are removed or CI workflow optimized here.

## Remaining gates and delivery order

1. Review covering 3A CI for the exact pushed commit/attempt; diagnose failures and
   obtain fresh bound approval for corrective writes. Do not accept 3A from a push
   or syntax check alone. Accepted 022.02 and bounded 2B/2C/2D stay closed.
2. Increment 3B remains: actual-route authorization/post-lock checks, malformed/unsafe
   archives, aggregate/member/snapshot limit boundaries, late checkpoint/history/media
   failure combinations, notification/privacy checks and combined lifecycle regressions.
   Basic validation and rollback are already part of 3A, not deferred to 3B.
3. Final covering lifecycle review must reconcile every parent criterion, including
   Stage 1/2 and Stage 3, before any 022.03 acceptance. Overall 022 and later viewer,
   listener/provider/import-UI units remain separate pending work. No requirement is
   silently removed by this split or the retained historical maps.

Schema stays 9. Retain matching complete code/storage/config/media backups; never roll
older code alone over ledger-bearing data. README and HANDOVER index remain applicable.
No deployment, merge, release, fresh CI success or wider acceptance is claimed.
