# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Current handover](../handover/140-viewer-ownership-fixtures.md#whole-stage-3-accepted-close-out---2026-11-17)

## Current status - 2026-11-17

Whole Stage 3 is reconciled, accepted and closed at the user's explicit 05:59 CET
request to reconcile, close and push accepted 3A+3B. Bounded 022.02, 2B/2C/2D,
3A and 3B acceptances remain unchanged. Whole Stage 1/2, 022.03 and overall 022
remain unaccepted. 022.04-022.16 and SG-TODO-023 remain separate pending work.
No merge, deployment, release or usable statblock viewer/import UI is claimed.

This docs-only close-out uses [skip ci]. No code, tests, workflow, permissions or
schema change; no fresh test execution or new covering CI result is claimed.
Every external write still requires exact bound approval.

## Preserved contracts and complete evidence

The following immutable records retain the complete earlier headings, assertions,
failures, correction history, criterion maps, counts, acceptance decisions and
limitations. They are preserved evidence and requirements, not discarded backlog.

- [Complete accepted 3A task and nine-group map](https://github.com/dajomas/Scrying-Glass/blob/070563ffc9ae4c1e8c35f8c39c8d387792ff10d6/docs/todo/223-statblock-lifecycle.md).
- [Complete accepted 3B task and eight-group map](https://github.com/dajomas/Scrying-Glass/blob/bb4cbae45ddc7448734a5f0224074633c1c6bf37/docs/todo/223-statblock-lifecycle.md).
- [Complete preceding handover](https://github.com/dajomas/Scrying-Glass/blob/bb4cbae45ddc7448734a5f0224074633c1c6bf37/docs/handover/140-viewer-ownership-fixtures.md).

The 3A task also retains original Stage 3 delivery order and links to the accepted
2B/2C/2D records. Dated pending-Stage-3 wording is superseded only for Stage 3;
no unfinished parent criterion is removed.

## Whole Stage 3 reconciliation - 2026-11-17

Scope: actual campaign-bundle representation, private setup/runtime/checkpoint
roundtrip and compatibility, safe independent import, validation and aggregate
limits, rollback, actual-route authorization, notification/privacy and combined
lifecycle boundary evidence. This is not final acceptance of all lifecycle paths.

| Stage 3 requirement | Combined accepted evidence and disposition |
|---|---|
| Actual chosen representation | 3A exports/imports version-2 campaign.json statblocks setup and encounter maps; actual roundtrip tests the chosen format. Version-1 tracker-only compatibility and empty export remain. Satisfied. |
| Content and provenance fidelity | 3A compares digest, definitions, nodes, facts, warnings and provenance/credits. Validation rejects unsafe URLs, credentials and forged authority; no verified online/fetch authority is granted. Satisfied with 3B hostile-input checks. |
| Independent ownership and source isolation | 3A asserts distinct destination encounter, revision 1 and unchanged source; imported revision/time are not trusted. 3B actual routes check created campaign ownership, unchanged active state/history and preserved superadmin policy. Satisfied. |
| Saved/runtime/checkpoint continuity | 3A preserves distinct saved setup and detached runtime private images and restores/reloads the imported checkpoint. 3B actual activation, trusted private edit, actual restore/undo/re-export verifies monotonic revisions, reload, source isolation, final digest and foreign keys. Satisfied. |
| Incoming validation and operator budgets | 3A rejects invalid maps, targets, digests, versions and private-field smuggling. 3B adds graph/identity failures and exact/beyond checks for all five snapshot budgets while stored reads/export survive lower incoming limits. Satisfied. |
| Explicit aggregate/archive/member admission | 3A rejects aggregate overflow rather than dropping private content. 3B measures real 10 MiB manifest, 25 MiB ZIP and 100 MiB expanded equality/one-over boundaries, 1,000 total members, unsafe/duplicate members, metadata-before-read rejection and actual upload cap. Satisfied. |
| Protected transaction and late rollback | 3A injects failure after real private setup persistence and during partial media write. 3B adds post-checkpoint, post-owner, post-history and partial-media faults; SQL/live/private/bindings/files restored with no emission and valid foreign keys. Satisfied. |
| Actual route and post-lock security | 3B selected production routes exercise owner/admin/superadmin policy, missing session/client/origin/multipart denials and ownership/role/session revocation after waiting for the operation lock. Satisfied. |
| Notification, history and privacy | 3A checks ordinary/public/client projection privacy. 3B inactive import emits nothing and preserves active history/revision; active recovery produces one post-commit frame checked for private markers, with metadata/persistence consistency assertions. Satisfied within recorded fixture scope. |

No blocking uncovered Stage 3 requirement was identified. The reconciliation
closes the union of agreed 3A implementation/core evidence and 3B boundary evidence,
not merely two green badges. No further Stage 3 implementation increment is required
by this review; actual later-discovered defects remain defects to address.

## Exact accepted evidence identities

3A: original implementation ea8b4c7342ba2b86e8c2ca7b07892fdf4ce7f7b9; failed
run 43955177051 retained in history. Store-fixture correction
26725005de3a1ed80ee06db5a23328f8ae33a0c0 preserved production guards. Successful
Branch tests 43958297280 attempt 1 covers that correction; publication
e839ca64e44ce43b8528069d928c97999768aed1. All eight PrivateBundleTests methods
explicitly OK within 1,973 main tests. Formal bounded acceptance
070563ffc9ae4c1e8c35f8c39c8d387792ff10d6.

3B: implementation 0d1cec345b187f7ecbbb1b959fd185927c18c046; successful Branch
tests 43963574986 attempt 1; publication 7aeb144b1e6adb3d28a08bc0e3262975742bed1b.
All 14 new methods explicitly OK within 1,987 main Python tests in 259.975s;
configured syntax/import, selected pytest, JavaScript and standalone Python
browser/audit stages succeeded. Formal bounded acceptance
bb4cbae45ddc7448734a5f0224074633c1c6bf37.

The reviewed 3B implementation tree retains tests/test_statblock_bundles.py's eight
3A methods alongside the seven native and seven HTTP 3B methods. These are 22
distinct Stage 3 test methods, not 22 additional tests beyond the suite counts.
Do not add totals from separate CI runs or claim unique totals across reruns.

## Retained limitations and operational contract

Seeded-session selected-route ASGI is not password login/full startup; recording
sockets exercise production notification logic, not browser/network WebSockets.
Private edit in the combined sequence is trusted fixture input, not a public API.
Real-size manifest padding measures aggregate bytes; supported-extension media
fixtures do not test decoding. Separately injected late faults are not exhaustive
simultaneous-fault, process-crash or power-loss proof. Marker-based privacy checks
are not a general information-flow proof. Provider authenticity, provider adapters,
separate viewer/listener, import UI and exhaustive platform coverage are not accepted
by Stage 3. Earlier Store harness results remain supplementary only.

Private graphs remain encounter/combatant-scoped. Ordinary serialization conveys no
private authority; ordinary omission cannot clear; trusted recovery alone may clear.
Durable ledgers remain monotonic. Raw save_setup remains tracker-only. Trusted stored
reads/export use permissive budgets; new imports use server limits. Bundles grant no
verified provenance/fetch authority. Schema remains 9; retain matching complete
code/storage/config/media backups, never older-code-only rollback.

## Remaining gates

1. Final 022.03 lifecycle reconciliation, including still-unaccepted whole Stage 1/2
   and parent requirements. Reuse accepted 2B/2C/2D and whole Stage 3 evidence without
   reopening bounded accepted work; address only actual uncovered requirements.
2. Obtain and record final lifecycle acceptance before closing 022.03. Overall 022
   and later 022.04-022.16 units remain separate. SG-TODO-023 is not a prerequisite
   introduced by this close-out. No merge, deployment or release is authorized.
