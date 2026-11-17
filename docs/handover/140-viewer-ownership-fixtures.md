# 140 - Viewer ownership fixture repairs

[Back to handover index](../../HANDOVER.md)

## Current state - 2026-11-17

Whole Stage 3 (accepted 3A+3B) is reconciled, accepted and closed following the
user's explicit 05:59 CET reconcile/close/push request. Bounded 022.02 and
2B/2C/2D/3A/3B remain accepted unchanged. Whole Stage 1/2, SG-TODO-022.03 and
overall 022 remain open. Later 022.04-022.16 and SG-TODO-023 remain separate.
No merge, deployment, release or usable statblock viewer/import UI is claimed.

## Preserved evidence and historical sections

[Complete preceding handover](https://github.com/dajomas/Scrying-Glass/blob/bb4cbae45ddc7448734a5f0224074633c1c6bf37/docs/handover/140-viewer-ownership-fixtures.md)
and [complete preceding lifecycle task](https://github.com/dajomas/Scrying-Glass/blob/bb4cbae45ddc7448734a5f0224074633c1c6bf37/docs/todo/223-statblock-lifecycle.md)
retain all prior headings, failures, correction identities, acceptance records,
assertion maps, counts and limitations, plus links to earlier immutable archives.
No unfinished requirement or prior evidence is discarded. Only the whole Stage 3
pending gate is superseded by this decision.

## Whole Stage 3 accepted close-out - 2026-11-17

The [whole-stage criterion map](../todo/223-statblock-lifecycle.md#whole-stage-3-reconciliation---2026-11-17)
reconciles the actual bundle format against the parent requirement and accepted
3A implementation/core evidence plus 3B boundary evidence. All nine combined
groups are satisfied within recorded limits: representation/version compatibility;
content/provenance; independent ownership/source isolation; saved/runtime/checkpoint
continuity; validation/operator limits; aggregate/archive/member admission; protected
transaction/late rollback; actual-route/post-lock security; notification/history/privacy.
No blocking agreed Stage 3 gap was identified. Whole Stage 3 is accepted and closed,
not inferred automatically from bounded acceptances or green badges.

3A: covering commit 26725005de3a1ed80ee06db5a23328f8ae33a0c0, successful Branch
tests 43958297280 attempt 1; publication e839ca64e44ce43b8528069d928c97999768aed1.
Eight explicit private-bundle methods OK within 1,973 main tests. Bounded acceptance
070563ffc9ae4c1e8c35f8c39c8d387792ff10d6. Original failed run and Store-fixture
correction remain in the immutable preceding records; production guards were retained.

3B: covering commit 0d1cec345b187f7ecbbb1b959fd185927c18c046, successful Branch
tests 43963574986 attempt 1; publication 7aeb144b1e6adb3d28a08bc0e3262975742bed1b.
Seven native and seven HTTP methods explicitly OK within 1,987 main tests in
259.975s; other configured syntax/import, pytest, JavaScript and standalone
browser/audit stages succeeded. Bounded acceptance
bb4cbae45ddc7448734a5f0224074633c1c6bf37. The 3B tree retains the eight 3A
methods: 22 distinct Stage 3 methods, included in suite counts, not added to them.

The chosen version-2 campaign.json envelope explicitly carries private setup and
encounter maps; version-1 tracker-only compatibility remains. Imported content
is independent, revalidated and not promoted to online authority. Aggregate
overflow is rejected, never silently truncated. 3B supplies real-size boundaries
and actual selected-route lifecycle/security checks beyond 3A's native service tests.
No production correction was needed for the Stage 3 close-out.

Limitations remain: seeded sessions/selected-route ASGI, not password login/full
startup; recording sockets, not browser/network WebSocket; trusted internal edit,
not public private-edit API; padded manifest admission, not all possible archives;
supported-extension media, not decoding; individually injected faults, not exhaustive
simultaneous faults/crash recovery; marker checks, not general privacy proof. No
provider adapter, separate viewer/listener or import UI is accepted here.

This is a documentation-only [skip ci] decision. No code/test/workflow/schema/
permission changes, no rerun or fresh CI claim. Existing implementation CI is the
covering evidence. Schema 9 and matching complete code/storage/config/media backup
guidance remain unchanged; no older-code-only rollback.

## Next gate

Final 022.03 lifecycle reconciliation must cover still-unaccepted whole Stage 1/2
and parent requirements while reusing accepted bounded and whole Stage 3 evidence.
Obtain final lifecycle acceptance before closing 022.03. Overall 022 and subsequent
units remain open. SG-TODO-023 does not interrupt this sequence. No merge, deployment
or release is authorized by this close-out.
