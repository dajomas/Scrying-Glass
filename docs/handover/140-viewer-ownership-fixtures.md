# 140 - Viewer ownership fixture repairs

[Back to handover index](../../HANDOVER.md)

## Current state - 2026-11-17

022.02 and bounded 2B/2C/2D/3A/3B are accepted/closed. The user explicitly
requested formal bounded 3B acceptance at 05:55 CET after passing covering CI
and criterion review; details and limits follow. Whole Stage 3, whole Stage 1/2,
022.03 and overall 022 remain unaccepted. No merge, deployment or release.
SG-TODO-023 remains separate and ready for review.

## Preserved evidence and historical sections

[Complete pre-3B handover](https://github.com/dajomas/Scrying-Glass/blob/070563ffc9ae4c1e8c35f8c39c8d387792ff10d6/docs/handover/140-viewer-ownership-fixtures.md)
retains all earlier diagnoses, preparation/failed-run/correction records, exact
counts, criterion maps, accepted close-outs and prior immutable archives. None
of their evidence limits or unfinished requirements is removed by this delivery.

## 2B bounded close-out - 2026-11-16

Accepted; full criterion map, 43899670266 attempt 1 evidence and limits remain
in the complete preceding handover and its linked immutable archives.

## 2C bounded close-out - 2026-11-16

Accepted; full criterion map and successful 43933600072 attempt 1 evidence remain
in the complete preceding handover. No accepted clone/copy/move/Save-As scope reopens.

## 2D bounded close-out - 2026-11-16

Accepted at e8546fb1ec14e4163faa89c326592948d6d81c46; full criterion map and
43941792616 attempt 1 evidence remain in the preceding handover.

## 3A private bundle roundtrip - 2026-11-16

Version-2 private campaign bundles, version-1 compatibility, trusted checkpoint
capture, independent ownership, validation and core rollback remain implemented.
The complete representation and operational description remains in the preceding
handover under this same heading. No representation/schema change is made in 3B.

## 3A Store ZIP-harness correction - 2026-11-16

Correction 26725005de3a1ed80ee06db5a23328f8ae33a0c0 retained the production transaction
guard. Its isolated 20-case run and guard-removal probe are supplementary, not native
private persistence proof. Full failed-run/correction history remains archived above.

## 3A bounded accepted close-out - 2026-11-16

Accepted/closed at the user's explicit 22:31 CET request, recorded by
070563ffc9ae4c1e8c35f8c39c8d387792ff10d6. Successful Branch tests 43958297280 attempt 1
covers 26725005de3a1ed80ee06db5a23328f8ae33a0c0; publication
e839ca64e44ce43b8528069d928c97999768aed1. Eight 3A methods explicitly OK within
1,973 main tests OK. Full nine-group criterion reconciliation and limits remain
in the exact preceding lifecycle/handover records, not widened by this delivery.

## 3B boundary implementation - 2026-11-16

Fourteen methods at 0d1cec345b187f7ecbbb1b959fd185927c18c046: seven native
archive/model boundaries in tests/test_statblock_3b_boundaries.py and seven
selected-route ASGI methods in tests/test_statblock_3b_http.py. The latter
imports the non-TestCase fixture through a module alias, avoiding rediscovery
of the native TestCase as an imported class. No production change was required.

Real 10 MiB manifest, 25 MiB stored ZIP and 100 MiB expanded boundaries accept
at equality and reject one byte over; 1,000 total members including manifest,
unsafe/duplicate members, forged expanded metadata before read, five operator
ModelLimits, bad graph/identity/URL/verification and actual multipart upload
limit are tested. The 10 MiB manifest uses inert top-level padding; export
checks its own computed-size boundary. Supported-extension media fixtures do
not test media decoding.

Production feature/AdminAPI installers, seeded AuthService, ownership, SQLite,
transaction wrapper and production notification logic are retained. Export
requires active-campaign access; regular admin import creates a new owned
campaign without active-campaign access. Superadmin policy is preserved. Denials
include missing session, client, origin, missing multipart field, corrupt ZIP
and post-lock ownership/role/session revocation, checked for atomicity.

Failures after real checkpoint, owner assignment, history hook and partial media
write restore SQL/private/ledger/live/bindings/media without notification.
Combined export/import/actual activation/trusted internal private edit/actual
checkpoint restore/undo/re-export checks source isolation, final post-commit
private-free frames, monotonic revisions, reload, foreign keys and final digest.
That edit is not a public private-edit endpoint.

## 3B bounded accepted close-out - 2026-11-17

The user explicitly requested formal acceptance at 05:55 CET following the
criterion reconciliation. Successful Branch tests run 43963574986 attempt 1
covered exact implementation commit 0d1cec345b187f7ecbbb1b959fd185927c18c046;
immutable results published at 7aeb144b1e6adb3d28a08bc0e3262975742bed1b.
Both archived log chunks show all 14 3B methods `ok` (seven native, seven HTTP)
within the 1,987-test main Python suite `OK` in 259.975s. Workflow syntax/
server-import, selected pytest, JavaScript and standalone Python browser/audit
steps succeeded. No native/ASGI method ran locally before CI. This docs-only
record has no new covering CI run and does not claim one.

The eight groups in the [criterion map](../todo/223-statblock-lifecycle.md#3b-boundary-implementation-and-evidence-map---2026-11-16)
were reviewed against assertions, inherited fixture and explicit test results.
No blocking bounded-3B gap remains. Accept/close 3B only, preserving the
selected-route/seeded-session/recording-socket limitation, no browser/network
WebSocket or full-startup/password-login claim, no import UI or public private
edit endpoint, no image-decoder assurance, no simultaneous-fault or process-crash
proof and no general privacy-information-flow proof. Previous bounded
acceptances are unchanged.

Whole Stage 3, Stage 1/2, SG-TODO-022.03 and overall 022 remain open. Next:
whole-Stage-3 reconciliation of accepted 3A+3B, then final lifecycle/parent
acceptance review. SG-TODO-022.04-022.16 and SG-TODO-023 are separate. No merge,
deployment or release is authorized by bounded acceptance. Schema 9 and matching
complete code/storage/config/media backup guidance remain unchanged.
[Task and remaining acceptance](../todo/223-statblock-lifecycle.md).
