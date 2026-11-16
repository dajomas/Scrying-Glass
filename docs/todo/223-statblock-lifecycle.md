# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Current handover](../handover/140-viewer-ownership-fixtures.md#3b-boundary-implementation---2026-11-16)

## Status and delivery rules - 2026-11-16

022.02, bounded 2B/2C/2D and bounded 3A remain accepted/closed. 3B is in progress:
14 boundary methods and documentation are supplied, with native/ASGI execution,
covering CI and acceptance pending. Whole Stage 3, Stage 1/2, 022.03 and overall 022
remain unaccepted; 022.04-022.16 remain pending. No usable viewer/import UI, merge,
deployment, release or whole-feature closure. SG-TODO-023 stays ready for review;
it does not interrupt or replace this lifecycle sequence.

Every external write needs exact bound approval. This test/documentation delivery
runs normal push CI without [skip ci]; documentation-only writes retain [skip ci].
No workflow edit, manual dispatch or production behavior/permission change is included.

## Preserved history, accepted criterion maps and contracts

[Complete pre-3B lifecycle task](https://github.com/dajomas/Scrying-Glass/blob/070563ffc9ae4c1e8c35f8c39c8d387792ff10d6/docs/todo/223-statblock-lifecycle.md)
and [complete pre-3B handover](https://github.com/dajomas/Scrying-Glass/blob/070563ffc9ae4c1e8c35f8c39c8d387792ff10d6/docs/handover/140-viewer-ownership-fixtures.md)
retain all prior headings, diagnoses, failures, correction identities, local/CI
counts, criterion maps, acceptance decisions, limits and older immutable archives.
No unfinished requirement or accepted evidence is discarded by these current summaries.

Snapshots remain encounter/combatant-scoped and private. Serialized/plain-dict
attributes confer no authority. Trusted reads/export use permissive budgets; incoming
imports use server ModelLimits. Digests exclude revision/time/self-digest; recovery
fingerprints include metadata. Ordinary omission cannot clear, removed rows cascade,
trusted recovery alone can clear; durable ledgers remain monotonic. Raw save_setup
stays tracker-only. Bundles grant no verified online provenance/fetch authority.

## 2C bounded acceptance reconciliation - 2026-11-16

Accepted; all agreed 2C units and the complete eight-group map stay in the preceding
record. Tested 7c703c4d66f63bd765a780f8e5ed6a2cd465521c, green 43933600072 attempt 1.
No accepted clone/copy/move/Save-As work reopens.

## 2D bounded acceptance reconciliation - 2026-11-16

Accepted at e8546fb1ec14e4163faa89c326592948d6d81c46; complete six-group map remains
in the preceding record. Tested ecd56957f9f147ac36d5196c23aec96d8889129c, green
43941792616 attempt 1. Inactive owned sources, superadmin policy, zero-selection
refresh semantics and evidence limits are unchanged.

## 3A - complete private bundle roundtrip

Completed/accepted/closed for its bounded scope. Version-2 private representation,
legacy version-1 compatibility, independent imported setup/checkpoint ownership,
validated provenance/content, incoming limits and core DB/media rollback remain.
The complete description, nine-group assertion map and limitations remain in the
exact preceding task; this 3B delivery does not change that decision.

## Store harness correction and remaining validation - 2026-11-16

The first 3A run 43955177051 failed; fixture correction
26725005de3a1ed80ee06db5a23328f8ae33a0c0 retained production guards. Full diagnosis,
isolated 20-case result and mutation-probe limits remain in the preceding records.
No isolated result is promoted to real-auth/native-private proof.

## 3A bounded acceptance reconciliation - 2026-11-16

User requested formal close-out at 22:31 CET; record commit
070563ffc9ae4c1e8c35f8c39c8d387792ff10d6. Successful Branch tests 43958297280 attempt 1
covers 26725005de3a1ed80ee06db5a23328f8ae33a0c0; publication
e839ca64e44ce43b8528069d928c97999768aed1. All eight 3A methods explicitly OK within
1,973 main tests OK. Full criterion map and source/fixture/real-network limits remain
at the preceding-task link, not replaced by a green-badge-only acceptance.

## 3B boundary implementation and evidence map - 2026-11-16

Status: test implementation supplied; execution and covering validation pending.

| Required boundary | Prepared regression assertions |
|---|---|
| Actual export/import auth | Owner success/private ZIP/no-store; new campaign ownership and unchanged active state/history; client/no-session/origin/missing-file denials; existing regular-admin import and superadmin policy. |
| Post-lock rechecks | Actual AuthService observation while operation lock is held; revoke export owner or import role/session, then assert expected denial and unchanged SQL/private/ledger/live/files with no emission. |
| Manifest/archive/member limits | Real 10 MiB/25 MiB/100 MiB inclusive and one-over cases; 999 media plus manifest accepted, one more rejected; expanded metadata overflow rejects before read. Actual multipart upload rejects 25 MiB+1. |
| Operator snapshot budgets | snapshot_bytes, content_nodes, content_depth, text_value_bytes and supporting_definitions exact fixture allowance then one lower; incoming rejection atomic while stored reads/export survive. |
| Unsafe/untrusted input | Duplicate/unsafe/noncanonical/directory/empty/unsupported members and malformed ZIP; graph cycles, missing reference, unsafe credit URL, credential URL, forged verified field and duplicate monster ID reject atomically. |
| Late rollback | Fail after actual checkpoint write, created-owner assignment, history hook and partial media write; compare full SQL/live/private/bindings/file bytes and no notification. |
| Notification/history/privacy | Inactive campaign import emits nothing and leaves active undo/checkpoint/revision intact. Active private edit/restore/undo emits one final post-commit frame without private content. |
| Combined lifecycle | Actual export/import/activation, internal fixture private edit, actual restore/undo and re-export; independent original source, monotonic revisions, reload, FK integrity and final digest. |

The same production routes, transaction wrapper, AuthService, ownership, SQLite,
private persistence and notification service are used; no fabricated permission or
public private-edit endpoint. Import does not require active-campaign ownership under
existing policy; export does. Seeded-session selected-route ASGI is not password login,
full application startup, network WebSocket/browser or exhaustive platform proof.
The mutation inside the combined sequence is trusted fixture input, not an import UI.

Executed here: both test sources compiled, AST counted seven native plus seven HTTP
methods. Pure fixture-builder checks measured a real 10 MiB manifest and 25 MiB ZIP;
multipart CRLF constants were checked. Zero native/HTTP methods executed locally.
Those construction/syntax checks do not establish passing acceptance criteria.
Normal CI discovery includes both test_*.py modules; no workflow change is needed.
See the handover for exact assertions, counting basis and fixture limitations.

## Remaining gates and delivery order

1. Run/review all 14 methods and covering full configured CI for the exact delivered
   commit/attempt. Diagnose failures, change production only for demonstrated defects,
   obtain fresh approval for any corrective write and retain explicit unexecuted gaps.
   Neither a push nor compilation accepts 3B or whole Stage 3.
2. Reconcile every 3B criterion against actual assertions/results and obtain bounded
   acceptance. Existing 022.02/2B/2C/2D/3A remain closed. Then perform final lifecycle
   acceptance review, including the still-unaccepted Stage 1/2 and parent requirements.
3. SG-TODO-022.03 and overall 022 are not closed by this delivery. Later viewer/listener/
   provider/import-UI work and SG-TODO-023 remain separate pending tasks.

Schema remains 9. Keep matching complete code/storage/config/media backups; no older-
code-only rollback. README and root indexes remain applicable. No fresh CI success,
merge, deployment, release or wider acceptance is claimed.
