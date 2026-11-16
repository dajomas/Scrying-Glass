# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Current handover](../handover/140-viewer-ownership-fixtures.md#3a-bounded-accepted-close-out---2026-11-16)

## Status and delivery rules - 2026-11-16

022.02 and bounded 2B/2C/2D remain accepted/closed. Bounded 3A is completed,
accepted and closed at the user's explicit 2026-11-16 22:31 CET formal close-out
request after criterion review and successful covering CI 43958297280 attempt 1
for 26725005de3a1ed80ee06db5a23328f8ae33a0c0. Increment 3B, whole Stage 3 and final
lifecycle acceptance remain required. SG-TODO-022 Stage 1/2, 022.03 and overall 022
remain unaccepted; 022.04-022.16 remain pending. No usable viewer/import UI, merge,
deployment, release or whole-feature completion is claimed. Earlier 3A pending/failure
wording below is historical and superseded by the bounded acceptance record.

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

Status: completed, accepted and closed for the bounded 3A scope on 2026-11-16.
The criterion map and evidence below supersede the earlier pending-delivery notes.

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

## 3A bounded acceptance reconciliation - 2026-11-16

The user explicitly requested formal close-out at 22:31 CET following the criterion
review. Bounded 3A is completed, accepted and closed; no outstanding agreed 3A criterion
was identified. This is not acceptance inferred solely from a green workflow.

Tested 26725005de3a1ed80ee06db5a23328f8ae33a0c0; successful push-triggered Branch tests
43958297280 attempt 1; evidence publication e839ca64e44ce43b8528069d928c97999768aed1.
Reviewed run.json/jobs.json establish exact head/attempt and all configured stages
successful. Workflow parts 121-122 explicitly report all eight PrivateBundleTests
methods OK. Part 140 reports 1,973 main tests OK in 199.059s, including those eight.
No unique aggregate with pytest/audit/Node reruns is claimed. Preparation-only/native-
unexecuted/CI-pending wording above describes earlier checkpoints and is superseded.
Original implementation ea8b4c7342ba2b86e8c2ca7b07892fdf4ce7f7b9 and failed covering
run 43955177051 remain recorded; the fixture correction did not change production code.

| Agreed 3A criterion | Inspected evidence and disposition |
|---|---|
| Actual representation/version handling | Production export/import use the version-2 statblocks envelope; roundtrip asserts version 2 and invalid-input cases reject unsupported versions and version-1 private smuggling. Satisfied. |
| Legacy tracker-only compatibility | legacy_bundle_import_and_empty_export confirms version-1 empty export and empty imported setup/checkpoint private maps. Satisfied. |
| Content/provenance fidelity | roundtrip compares digest, definitions, nodes, facts, warnings and provenance/fixture credits against source through assert_content; production validates rather than grants online authority. Satisfied. |
| Independent ownership/persistence | roundtrip asserts distinct destination encounter, revision 1, unchanged source and no active-campaign switch; production removes imported revision/time before save_new_setup. Satisfied. |
| Checkpoint restore/reload | roundtrip loads Imported encounter private image and destination reference, restores through recovery service, reloads, checks persisted content and foreign-key integrity. Satisfied. |
| Saved/runtime separation | runtime_private_content_is_separate_from_saved_setup checks original imported setup versus distinct detached runtime checkpoint content and absent active-setup reference. Satisfied. |
| Incoming validation/operator limits | invalid_private_input_is_atomic covers map/target/digest/URL/version/private-field errors; lowered_incoming_limit preserves stored reads/export and rejects import with unchanged state. Satisfied within 3A; exhaustive boundaries stay in 3B. |
| Explicit aggregate rejection | production counts private content toward manifest cap; aggregate_overflow test lowers the threshold and asserts 413 rather than omission. Satisfied mechanism; real-size combinations stay in 3B. |
| Core database/media rollback | late_private_database_failure and partial_media_failure inject after real private setup write/during partial media write, compare full SQL/live ordinary/private state/file inventories and verify no open transaction. Satisfied. |

Limits: service/native-SQLite fixtures, not authenticated HTTP/browser or real-network
WebSockets; projection assertions are not delivery proof. The aggregate test lowers
its constant, not all actual-size combinations. Imported provenance remains content,
not verified online authenticity/fetch authority. Store AST-harness results remain
supplementary. All distinct 3B and parent gates below remain mandatory.

## Remaining gates and delivery order

1. Bounded 3A and previously accepted 022.02/2B/2C/2D remain closed. No whole Stage 3,
   Stage 1/2, 022.03 or overall 022 acceptance is implied. SG-TODO-023 remains ready
   for review, separate from the agreed lifecycle order.
2. Increment 3B is next: actual-route authorization/post-lock checks, malformed/unsafe
   archives, aggregate/member/snapshot limit boundaries, late checkpoint/history/media
   failure combinations, notification/privacy checks and combined lifecycle regressions.
   Basic validation and rollback were part of accepted 3A, not deferred to 3B.
3. Final covering lifecycle review must reconcile every parent criterion, including
   Stage 1/2 and Stage 3, before any 022.03 acceptance. Overall 022 and later viewer,
   listener/provider/import-UI units remain separate pending work. No requirement is
   silently removed by this split or the retained historical maps.

Schema stays 9. Retain matching complete code/storage/config/media backups; never roll
older code alone over ledger-bearing data. README and HANDOVER index remain applicable.
This three-file close-out is documentation-only [skip ci]: no tests rerun, fresh CI
claimed, workflow change/manual dispatch, deployment, merge, release or wider acceptance.
