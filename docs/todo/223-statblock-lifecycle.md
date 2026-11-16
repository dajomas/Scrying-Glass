# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Current handover](../handover/140-viewer-ownership-fixtures.md#2d-bounded-close-out---2026-11-16)

## Status and delivery rules - 2026-11-16

Bounded 2D is completed and accepted for the agreed selected/life-filtered private
setup-import scope by approval of this exact close-out payload. Bounded 2B/2C and
022.02 remain accepted/closed. SG-TODO-022.03 and overall 022 remain in progress/
unaccepted; their Stage 1/2 remain unaccepted. 022.04-022.16 remain pending. No
merge/deployment/release or whole-feature closure. Stage 3 private bundles are next.

Each external write needs exact-payload approval. Normal push CI applies to subsequent
code/test work: the intermediate-2C skip instruction ended with the final code/test
covering run, not a standing exception for 2D/Stage 3 or future fixes. Documentation-only
commits, including this close-out, retain [skip ci], no workflow edit/manual dispatch.
Do not weaken assertions or equate fixtures/static checks with deployed-server proof.

## Preserved history and contracts

[Complete pre-2C-close-out lifecycle record](https://github.com/dajomas/Scrying-Glass/blob/dae492f2e95bc378d73425f22dd5e85d9c681215/docs/todo/223-statblock-lifecycle.md)
and [complete handover/continuity record](https://github.com/dajomas/Scrying-Glass/blob/dae492f2e95bc378d73425f22dd5e85d9c681215/docs/handover/140-viewer-ownership-fixtures.md)
retain every increment/correction identity, exact count, failed-run diagnosis, harness
limit, 2B criterion map and four 2C preparation/delivery records, with earlier immutable
archives. Current reconciliation supersedes supported 2C open/prepared/unexecuted/
CI-pending wording, never discards later requirements or promotes isolated checks.
Older scope/fixture/parent status notes describe dated deliveries, not new contracts.

Snapshots stay encounter/combatant-scoped and private. PrivateEncounterState metadata
stays outside JSON/through deepcopy; serialized/plain dict attributes confer no
private authority. Trusted stored reads use permissive budgets; incoming preparation/
imports use operator limits. Digests exclude revision/time/self-digest; recovery
fingerprints include metadata. Ordinary omission rejects, removed rows cascade,
clearing stays trusted recovery-only. Header-only protocols cannot clear. Clear/re-add
and counter-only rebuilds preserve monotonic durable ledgers/hidden bindings;
ordinary input/corruption rejects. No public clear flag, new permission or provenance
promotion. Raw SQLiteStorage.save_setup remains tracker-only, not a source-copy channel.

<a id="2c3b-save-handler-integration---2026-11-16"></a>

Protected Save As uses transactional_handler/AdminSetupsMixin.save_setup and
save_setup_with_private/save_new_setup. New ownership/time/revision is independent;
same-owner stale guards and existing-destination owner/ledger continuity remain.
Roster/reference writes and stored metadata refresh precede changed()/final flush;
omission never clears. Source/runtime isolation, reload and late rollback remain.

## CI correction series - 2026-11-16

All nine corrections, SHAs, failed run totals and isolated/native distinctions stay
in the complete record. Failed module counts alone were not leak proof. Correction 8
retains protected Save As/raw tracker semantics. Correction 9,
14ad1d3075f4e737c38270ea2a9734fd1f5b9ad3, delivers selected/life-filtered imports
using actual ID maps/operator ModelLimits, retaining destination graphs, independent
ownership and source counter isolation. Full life-filter/scope/limit/rollback/privacy/
reference/remapping/native evidence stays archived. 2D was delivered by correction 9;
its bounded acceptance below supersedes earlier pending status, not its contracts.
[Detailed import record](../handover/130-accounts-migration-fixture.md#private-setup-import-correction---2026-11-16).

## Covering CI and request-type follow-up - 2026-11-16

de3f69bb6453553704df2a68cc73511f69c21dff retains actual Request forwarding,
injection/post-lock auth and original assertions without object/empty misrouting.
Green 43893014815 attempt 1 and earlier failures/harness limits remain archived,
not confused with final covering evidence or wider acceptance.

## Green evidence reconciliation and 2B boundaries - 2026-11-16

Bounded 2B stays accepted at bcb55bb4f6542ac99d95684a247ffadeb05f3a32 after
criterion review and green 43899670266 attempt 1. Its full map remains archived.
Native core plus eleven actual-route/exhaustion/notification methods closed its
gaps; constrained-SQLite/mocked checks stay supplementary, not ordinary clear authority.

## 2C.3c first combined-operation slice - 2026-11-16

8482acf420fa18051d56a429a6853515b9ff5202 supplies two protected sequence/rollback
methods; both pass final CI. Atomicity is per request, not rollback of prior commits.

## 2C.3c Save As authorization slice - 2026-11-16

601699ce07735baf3fac09d2b5dc9fb01284eefb supplies five actual selected-route auth/
sequence/post-lock revocation methods. All pass; observers preserve real decisions.

## 2C.3c production-notification slice - 2026-11-16

86e2112586db84a7ec944cddec0616f24256056c supplies three production-deferral methods;
all pass. Unchanged explicit Save retains one refresh at unchanged revision, true
no-op is silent. No production behavior/permission/workflow changes were needed.

## 2C bounded acceptance reconciliation - 2026-11-16

Tested revision 7c703c4d66f63bd765a780f8e5ed6a2cd465521c; successful push-triggered
Branch tests 43933600072 attempt 1; publication
 dae492f2e95bc378d73425f22dd5e85d9c681215. Main unittest: 1,956 OK; selected pytest:
43 passed. Syntax/server import, JavaScript, standalone browser/audit and visual
artifact upload stages passed. Audit: 218 modules, zero failed, explicit PASS that
all audited modules passed/closed tracked connections. All thirteen 2C.3c methods
explicitly report OK: two combined, five auth, three notifications, three continuity.
Included in 1,956, not an extra/unique aggregate with pytest or standalone reruns.

Reconciliation uses inspected production/test bodies plus exact run/head/attempt,
workflow entries in parts 121-123, 131-133, 136, 139-140 and audit 298. Native continuity
covers sequential runtime checkpoint/undo, destination overwrite/same-owner/stale/
checkpoint/undo history and counter-only reopen/overwrite/exhaustion after transfers.

| Agreed criterion | Assertion-level evidence and disposition |
|---|---|
| Independent clone/copy ownership and graph fidelity | PrivateCloneKernelTests, SetupPrivateCopyTests, ProtectedSetupCopyTests: independent owners/graphs/revision/time, complete ordered private content/references/provenance/credits, immutable source/input, counter-only exclusion and occupied/mismatched rejection. Passed. |
| Existing transfer rules and atomic rejection | Stored/protected copy/move and transfer tests retain returned collision names, canonical references, roster/effect cleanup, scope/missing-source rejection, destination isolation and outer rollback. Passed. |
| Stable moved ownership and exclusive runtime | SetupPrivateMoveTests/LoadedSetupMoveTests retain moved owner/metadata/ledger, collision/last-setup isolation, reopen/MAX_REVISION, independent fresh runtime, obsolete-runtime retirement, shared-owner rejection and background/copy bypass. Passed. |
| New/existing Save As and authority | Kernel/handler/combined tests retain live/runtime content, independent new ownership, source isolation, same-owner stale guards, other-owner counter continuity, raw tracker-only behavior, omission rejection, roster/reference/live refresh and reload. Passed. |
| Combined recovery/revision continuity | CombinedSetupOperationTests/SetupRecoveryContinuityTests retain full operation sequence, saved owners/bindings/checkpoints, missing-source rejection, monotonic sequential undo, overwrite/stale guards, counter-only reopen and atomic exhaustion. Passed. |
| Actual authorization/post-lock rechecks | TransferHTTPTests plus five SetupSavingHTTPTests retain real installers/models/AuthService/ownership/SQLite, owner/superadmin policy, session/role/owner/origin/campaign/malformed denials and post-lock revocation, preserving full SQL/private/history/live state. Passed. |
| Production notifications/no-op semantics | Three SetupNotificationTests retain actual broadcast/deferral/viewer projection: one final committed frame, no copy-only emission, late rollback suppression, unchanged explicit Save's one refresh at unchanged revision, silent true no-op. Passed. |
| Late rollback and projection privacy | Kernel/service/transfer/combined/notification failures restore SQL/ledgers/references/live state without partial notification; private graphs/markers stay out of ordinary/public/client/sent JSON. Earlier committed requests survive final-request rollback. Passed. |

Disposition: bounded 2C completed/accepted by approval of this payload. No outstanding
agreed 2C criterion was identified. Not exhaustive scheduling/platform certification.
Seeded-session selected-route ASGI is not login/full application startup; recording
sockets are not network/browser verification. Injected denial/mocks/static/extracted
harnesses are supplementary, not real-auth/native proof. No new viewer/listener/
provider, deployed-server, human visual/screen-reader, live-provider or exhaustive
E2E acceptance. Existing unrelated Admin/Client permissions remain unchanged.

## 2D bounded acceptance reconciliation - 2026-11-16

2D is completed and accepted for its agreed selected/life-filtered private setup-import
scope by user approval of this exact close-out payload. No outstanding agreed 2D
criterion was identified. Existing implementation is correction 9 at
14ad1d3075f4e737c38270ea2a9734fd1f5b9ad3; boundary completion at
ecd56957f9f147ac36d5196c23aec96d8889129c retained it and all eleven native methods
unchanged, adding six actual-route/notification methods and a handover record.

Successful push-triggered Branch tests 43941792616 attempt 1 covers exactly
ecd56957f9f147ac36d5196c23aec96d8889129c; evidence publication
0742d36fa6186b3764d9b3c6e4153c20f6071b08. Main unittest: 1,962 tests OK; selected
pytest: 43 passed. Syntax/server import, JavaScript, standalone browser/audit and
visual-artifact upload stages passed. Audit: 219 modules, zero failed, explicit PASS
that all audited modules passed and closed tracked connections. All seventeen import-
specific methods explicitly report OK in the same run: eleven retained native and
six new boundaries, included in 1,962, not an extra/unique aggregate with other suites.

Review combines the inspected helper/handler/test bodies and exact run/head/attempt
with workflow parts 120-121, 132, 139-141 and 300. Criterion disposition:

| Agreed 2D criterion | Assertion-level evidence and disposition |
|---|---|
| Selection, scoping and identity remapping | Core life-filter/subset/empty/allocation cases plus actual same/cross/runtime route imports retain alive/dead/all selection, the handler's exact clone map, valid unique participant identities, rejection of missing/colliding allocations and existing effect/reference rules. Passed. |
| Private content fidelity and authority | Rich definitions/nodes/facts/warnings/provenance/credits survive import and reload. Serialized private sources reject; plain-dict attributes confer no authority. Existing graphs stay destination-owned and source counter-only history is not exported. Passed. |
| Independent ownership/revisions and source preservation | Core clone edit/row/header cases and new owned/runtime/superadmin cases retain independent rows, fresh clone revision 1/time, unchanged original graph/ledger bindings, immutable distinct source and saved-setup isolation for runtime writes. Passed. |
| Operator limits versus trusted reads | Defaults/overrides/invalid configuration and lowered incoming limits reject atomically without deleting/blocking trusted stored reads or losing existing destination graphs. Passed. |
| Actual authorization and post-lock checks | Actual selected installer/model/AuthService/ownership/SQLite covers owner and existing superadmin policy, unauthenticated/client/source-owner/destination-owner/origin/model/missing-source denials, and queued source/destination ownership/role/session revocation with exact unchanged SQL/private/history/live state. Passed. |
| Production notifications, history, rollback and privacy | Actual broadcast/deferral/viewer projection observes one final post-commit clone frame and revision, prior undo cleared at the existing import boundary, checkpoints/source retained, and exact late private/history failure rollback with no emission. Zero selection preserves graph/IDs/revisions/undo and the handler's existing one refresh; response/public/client/sent JSON remains private. Passed. |

Acceptance is bounded to those criteria/evidence, not inferred solely from CI success.
Seeded-session ASGI is not login/full application startup; recording sockets are not
real-network/browser delivery. Spies preserve actual decisions/deferral, native writes
seed fixtures, and no provider fetch/new viewer/listener/import UI, exhaustive platform/
concurrency, deployed-server, human visual/screen-reader or exhaustive E2E proof is
claimed. No new permission, clearing authority, provenance promotion or changed
zero-selection semantics. Additional production changes were not needed for completion.
No tests rerun or fresh CI claimed by this documentation-only close-out.

## Remaining gates and delivery order

1. 022.02 and bounded 2B/2C/2D stay closed. SG-TODO-022 Stage 1/2, 022.03 and overall
   022 remain unaccepted; later viewer/provider/listener units remain pending.
2. Stage 3 is next: implement/test actual private bundle representation/roundtrip,
   aggregate/snapshot/member limits, malformed/untrusted input, provenance and rollback.
   No silent loss at 10 MiB manifest/archive limits: explicit aggregate rejection or
   separately validated reference members. Private-content bundles stay unimplemented,
   distinct from existing tracker-only bundles.
3. Final covering validation and every parent acceptance criterion remain mandatory.
   No incomplete later requirement is deleted by this bounded close-out.

Schema stays 9. Keep matching complete code/storage/config/media backups; never roll
older code alone over ledger-bearing data. No merge/deployment/release. Documentation-
only [skip ci], no tests rerun/fresh CI claimed/workflow edit/manual dispatch.
README/HANDOVER.md index remain applicable; TODO.md changes only related 022.03 status.
