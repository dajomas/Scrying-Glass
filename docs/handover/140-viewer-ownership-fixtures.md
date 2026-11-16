# 140 - Viewer ownership fixture repairs

[Back to handover index](../../HANDOVER.md)

## Current state - 2026-11-16

022.02, bounded 2B/2C/2D and bounded 3A remain accepted/closed. 3B boundary-test
implementation is included in this delivery with execution/CI/acceptance pending.
Whole Stage 3, Stage 1/2, 022.03 and overall 022 remain unaccepted. No merge,
deployment or release. SG-TODO-023 remains separate and ready for review.

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

Fourteen new methods: seven native archive/model boundaries in
 tests/test_statblock_3b_boundaries.py and seven actual selected-route methods in
 tests/test_statblock_3b_http.py. The latter imports the non-TestCase fixture through
a module alias, avoiding rediscovery of the native TestCase as an imported class.

Coverage prepared: real 10 MiB manifest, 25 MiB stored ZIP and 100 MiB expanded
admission boundaries (inclusive and one byte over); 1,000 total members including
manifest; malformed/duplicate/unsafe members; forged expanded metadata rejected
before reads; all five operator ModelLimits at/over the fixture boundary; graph/
identity/credential/false-verification rejection; actual multipart upload cap.
The 10 MiB import fixture uses inert top-level padding for aggregate byte admission;
the export mechanism also checks exact computed manifest size and one byte below it.
The real-size media fixtures use supported extensions, not a media-decoder test.

Actual feature/AdminAPI installers, AuthService, ownership, SQLite and production
notification logic are retained. Import is intentionally permitted for a regular
admin without access to the active campaign because it creates a new campaign owned
by that caller; export still requires active-campaign access. Existing superadmin
policy is retained. Tests cover no-session/client/origin/multipart/corrupt denials,
post-lock export ownership and import role/session revocation, unchanged SQL/private/
ledger/live/history/files and zero notifications for inactive-campaign import.

Late failure injection occurs after real checkpoint, owner assignment, history hook
and partial media write. Combined export/import/actual activation/trusted private
edit/actual checkpoint restore/undo/re-export asserts monotonic revisions, preserved
source, reload and one final post-commit private-free frame per active mutation.
The private edit is an internal fixture transaction, not a new public private-edit API.

Executed in this environment: compile() passed for both complete test sources; AST
inventory found 14 methods. Pure ZIP builder checks verified a 10,485,760-byte
manifest and a valid 26,214,400-byte ZIP; multipart literal CRLF was inspected.
These checks did not execute any native/ASGI regression: zero of the 14 ran here.
No checkout/full suite/browser/network verification or fresh CI result is claimed.
Existing unittest discovery includes both modules. Push runs normal CI without
[skip ci]; await covering results before 3B/Stage 3 acceptance. No production change
is included without an executed regression demonstrating a defect.

README, TODO index, HANDOVER index and workflow were reviewed/reused at verified
identities and remain applicable; parent scope/3B acceptance stay pending. Detailed
3B implementation status supersedes older next-3B wording, not any gate. Schema 9
and matching complete code/storage/config/media backup guidance remain unchanged.
[Task and remaining acceptance](../todo/223-statblock-lifecycle.md).
