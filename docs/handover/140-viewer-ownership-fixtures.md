# 140 - Viewer ownership fixture repairs

[Back to handover index](../../HANDOVER.md)

## Current state - 2026-11-17

Whole lifecycle Stages 1, 2 and 3 and SG-TODO-022.03 are accepted and closed.
The user requested Stage 1/2 and 022.03 close-out at 06:01 CET following whole
Stage 3 acceptance. Existing 022.02 and bounded 2B/2C/2D/3A/3B decisions stand.
Overall SG-TODO-022 remains open, with 022.04-022.16 and SG-TODO-023 separate.
No merge, deployment, release or usable statblock viewer/import UI is claimed.

## Preserved complete evidence

[Complete preceding handover](https://github.com/dajomas/Scrying-Glass/blob/25b55cfbb6ba9fc25620d94e04ef21682db03414/docs/handover/140-viewer-ownership-fixtures.md)
and [complete Stage 3/task record](https://github.com/dajomas/Scrying-Glass/blob/25b55cfbb6ba9fc25620d94e04ef21682db03414/docs/todo/223-statblock-lifecycle.md)
retain original criterion maps, earlier acceptance identities, failures/corrections,
counts and limits through immutable archives. No pending later requirement is
removed. Dated Stage 1/2/022.03 pending wording is superseded by this decision only.

## Final lifecycle accepted close-out - 2026-11-17

[Final criterion reconciliation](../history/223-statblock-lifecycle.md#final-criterion-reconciliation)
maps whole Stage 1 native save/loading/privacy, Stage 2 recovery/reset/counter/
copy/move/Save As/import, and accepted whole Stage 3 bundles to the lifecycle
preservation contract. No blocking unmet agreed 022.03 requirement was found.
Accept/close Stage 1 and Stage 2 and, with Stage 3, SG-TODO-022.03. This is
criterion-based acceptance, not promotion from a green badge.

Additional final-review inspection: six ProductionStatblockSaveTests methods
cover native setup/runtime rebuild preservation, ordinary input rejection, legacy
ID allocation, scoped deletion and late rollback; seven ServicePrivateLoadTests
cover private carrier loading/JSON/deepcopy, setup/runtime precedence, restart,
trusted-read budgets, failed-read atomicity and source/live isolation. Their
explicit final-run passes are in workflow parts 129 and 133. Actual in-process
HTTP/WebSocket projection assertions were reviewed in StatblockTransportPrivacyTests.
Core protected private flush/restore/capture/kernel/counter passes are in parts
128-133. Accepted 2B/2C/2D maps and Stage 3 map supply the remaining lifecycle
assertion-level evidence without reopening closed bounded work.

Final covering run: Branch tests 43963574986 attempt 1, success for
0d1cec345b187f7ecbbb1b959fd185927c18c046; publication
7aeb144b1e6adb3d28a08bc0e3262975742bed1b. Main suite 1,987 OK in 259.975s;
other configured syntax/import, selected pytest, JavaScript and standalone Python
browser/audit stages succeeded. Earlier covering runs and exact identities remain
in the task archives; totals are not added across runs. Whole Stage 3 acceptance
25b55cfbb6ba9fc25620d94e04ef21682db03414 remains unchanged.

This docs-only [skip ci] close-out reruns no tests and claims no fresh CI. No
production/test/workflow/schema/permission change. Seeded-session selected ASGI,
in-process WebSocket and recording sockets are not password login/full-startup/
browser/network proof. Internal edits are fixture inputs, not public APIs. Size
fixtures do not certify decoding; injected faults/privacy markers are not exhaustive
crash/scheduling/information-flow proof. No provider adapter, listener/viewer or
import UI is accepted. Earlier isolated/mocked checks remain supplementary.

Schema 9; matching complete code/storage/config/media backups remain required,
not older-code-only rollback. Ordinary omission cannot clear private content;
trusted recovery and durable counters retain their contracts. No online provenance
authority is granted. Next work is pending 022.04-022.16; overall 022 stays open.
SG-TODO-023 is separate. No merge, deployment or release is authorized.
