# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Current handover](../handover/140-viewer-ownership-fixtures.md#3b-bounded-accepted-close-out---2026-11-17)

## Status and delivery rules - 2026-11-17

022.02 and bounded 2B/2C/2D/3A/3B are accepted/closed. The user's explicit
2026-11-17 05:55 CET request formally accepts bounded 3B after criterion and
covering-CI review; the decision and limits are recorded below. Whole Stage 3,
whole Stage 1/2, 022.03 and overall 022 remain unaccepted; 022.04-022.16 remain
pending. No usable viewer/import UI, merge, deployment, release or whole-feature
closure. SG-TODO-023 stays separate and ready for review.

Every external write needs exact bound approval. This documentation-only close-out
uses [skip ci]; the successful implementation run remains the covering CI evidence.
No workflow, production behavior, permission, schema or test changes are made here.

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
exact preceding task; this 3B decision does not change that acceptance.

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

Implementation 0d1cec345b187f7ecbbb1b959fd185927c18c046 adds seven native
archive/model and seven selected-route ASGI methods. The tests run against SQLite,
actual production feature/AdminAPI installers, seeded AuthService sessions, real
transaction/ownership/private-persistence and production notification logic.

| Required boundary | Reconciled passing regression assertions |
|---|---|
| Actual export/import auth | Owner export includes private ZIP and no-store; new import ownership and unchanged active campaign/history; no-session/client/origin/missing-file denials; regular-admin import without active-campaign access and retained superadmin policy. |
| Post-lock rechecks | AuthService observation while operation lock is held; revoked export owner or import role/session denied after the wait with SQL/private/ledger/live/files unchanged and no emission. |
| Manifest/archive/member limits | Real 10 MiB manifest, 25 MiB ZIP, 100 MiB expanded bytes inclusive and one over; 999 media plus manifest accepted, one more rejected; oversized expanded metadata denied before reads; actual multipart upload denies 25 MiB+1. |
| Operator snapshot budgets | snapshot_bytes, content_nodes, content_depth, text_value_bytes and supporting_definitions exact fixture allowances then one lower; import rejection atomic while trusted stored reads/export survive. |
| Unsafe/untrusted input | Duplicate/unsafe/noncanonical/directory/empty/unsupported members and malformed ZIP; cycle, unresolved reference, unsafe credit URL, credential endpoint, forged verified field and duplicate monster ID reject atomically. |
| Late rollback | Faults after real checkpoint save, owner assignment, history hook and during partial media write preserve complete SQL/live/private/bindings/file bytes, no frame, and valid foreign keys. |
| Notification/history/privacy | Inactive import sends nothing and preserves active checkpoint/undo/revision. Active private edit, checkpoint restore and undo produce one final post-commit frame per mutation, checked for private markers. |
| Combined lifecycle | Actual export/import/activation, internal trusted private edit, actual restore/undo and re-export preserve original source, monotonic revisions, reload, foreign keys and final digest. |

## 3B bounded accepted close-out - 2026-11-17

The user explicitly requested formal 3B acceptance at 05:55 CET after the
criterion-by-criterion review. Branch tests run 43963574986 attempt 1 (push)
completed successfully for the exact implementation head
0d1cec345b187f7ecbbb1b959fd185927c18c046; immutable result publication
7aeb144b1e6adb3d28a08bc0e3262975742bed1b. Both log segments explicitly show
all seven native plus seven HTTP 3B methods `ok` within 1,987 main Python tests
`OK` (259.975s). The syntax/server-import, selected pytest, JavaScript and
standalone Python browser/audit workflow steps also succeeded. This is covering
CI, not a claimed local execution or a new run for this docs-only commit.

The eight required boundaries above were reconciled against the actual assertions,
inherited SQL/private/notification fixture and test log, not merely a green badge.
No blocking gap was identified within bounded 3B; accept and close 3B only.
No production modification or corrective test commit was needed.

Scope of evidence: selected-route ASGI and seeded sessions, not password login,
full application startup or network/browser WebSocket. Recording sockets exercise
production notification logic. The private edit is a trusted internal fixture
transaction, not a public edit API or import UI. The 10 MiB import manifest uses
inert top-level padding; media admission fixtures use supported file extensions,
not image decoding. Four separately injected late faults are not exhaustive
simultaneous faults or crash/power-loss proof. Privacy assertions inspect selected
markers, not a general information-flow proof. The native expanded-size and
member/limit checks demonstrate their measured boundaries, not all possible ZIPs.
These limitations do not widen 3B acceptance into broader feature acceptance.

## Remaining gates and delivery order

1. Reconcile bounded accepted 3A plus 3B against the complete agreed Stage 3
   contract and record whole Stage 3 acceptance only if satisfied. Do not treat
   bounded acceptance as automatic acceptance of the whole stage.
2. Perform final 022.03 lifecycle acceptance review including still-unaccepted
   whole Stage 1/2 and parent requirements. Reuse accepted 2B/2C/2D/3A/3B evidence;
   address only actual uncovered gaps, then obtain formal lifecycle acceptance.
3. 022.03 and overall 022 remain open. 022.04-022.16 viewer/listener/provider/
   import-UI units and SG-TODO-023 are separate pending tasks.

Schema remains 9. Keep matching complete code/storage/config/media backups; no older-
code-only rollback. README and root indexes remain applicable. No merge, deployment,
release or wider acceptance is claimed.
