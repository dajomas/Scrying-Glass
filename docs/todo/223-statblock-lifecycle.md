# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Current handover](../handover/140-viewer-ownership-fixtures.md#2b-bounded-close-out---2026-11-16)

## Status and delivery rules - 2026-11-16

2B is completed and accepted for its bounded recovery/reset/private-lifecycle scope
by approval of this exact close-out payload. SG-TODO-022.03, 2C and overall 022
remain in progress and unaccepted. Stage 1/2 remain unaccepted; 022.02 stays closed.
022.04-022.16 remain pending. No merge, deployment, release or whole-feature closure.

Delivery order remains 2C/2C.3c, 2D reconciliation, Stage 3 bundles and final lifecycle
acceptance. Implementation or configured CI success alone never closes wider gates.
Each external write requires complete exact-payload approval. Code/test commits use
normal push CI, without [skip ci], unless explicitly instructed otherwise. The earlier
nine-commit skip agreement does not extend to subsequent fixes. Documentation-only
commits, including this close-out, always use [skip ci], with no workflow edit/manual
dispatch. Do not weaken assertions or infer live-server evidence from fixtures.

## Preserved history and contracts

[Complete pre-close-out lifecycle record](https://github.com/dajomas/Scrying-Glass/blob/3126dfed318158d3e6bc1fc2cbed878e1921c360/docs/todo/223-statblock-lifecycle.md)
retains every increment/correction identity, exact local/CI count, failed-run diagnosis,
harness limitation and boundary preparation record, together with its earlier archives.
This reconciliation preserves section anchors and all remaining requirements while
superseding stale prepared/unexecuted/CI-pending/2B-in-progress wording. Older notes in
scope, fixture and parent documents describe dated deliveries; this task controls
current lifecycle status, not a change to the parent's feature contract.

Snapshots remain encounter/combatant-scoped and private. PrivateEncounterState
carries metadata outside JSON and through deepcopy; serialized input and attributes
on ordinary dicts confer no private authority. Trusted stored reads use permissive
budgets; incoming preparation/imports use operator budgets. Digests exclude revision/
time/self-digest; recovery fingerprints include metadata. Ordinary omission fails
closed, removed combatants cascade and clearing remains trusted recovery-only.
Header-only protocols cannot clear. Actual clear advances a durable counter;
re-addition advances beyond it. Counter-only rebuilds preserve hidden markers and
bindings. Ordinary input/corruption rejects. No public clear flag, new permission,
serialized authority or provenance promotion is introduced.

Raw SQLiteStorage.save_setup stays tracker-only: it preserves destination-owned
content but never infers source ownership from a carrier or matching combatant ID.
Protected Save As uses transactional_handler(context, AdminSetupsMixin.save_setup)
and save_setup_with_private/save_new_setup. Same-owner saves retain stale guards;
other existing destinations retain their own counter history and rebase incoming
revision/time, never reset owner/ledger. Omission is not clearing.

<a id="2c3b-save-handler-integration---2026-11-16"></a>

Protected Save As saves roster/references and refreshes live destination metadata
before changed()/final flush. New destinations have independent ownership and fresh
revision/time. Runtime/source isolation, reload and late rollback remain required.
The original preservation and import-remapping assertions are not relaxed.

## CI correction series - 2026-11-16

Corrections 1-8 were pushed with [skip ci]; correction 9 was pushed without it.
Failed run 43846424270 attempt 1 covered 812de5ae6717f8a7f34892e0031858a0a3e089c6:
1,896 main tests, three failures/fourteen errors; audit 211 modules/six failed.
Failed run 43889177129 attempt 1 covered correction 9,
14ad1d3075f4e737c38270ea2a9734fd1f5b9ad3: 1,928 tests, one failure/nine errors;
audit 213 modules/three failed. Failed-module counts alone do not demonstrate leaks.
All nine delivered correction SHAs and the exact diagnoses remain in the complete
record. These failed totals are historical, not current combined-suite results.

Correction 8 preserves the protected Save As contract, including raw tracker-only
semantics. Correction 9 implements selected/life-filtered setup imports using the
handler's exact ID map and operator ModelLimits budgets. Existing destination graphs
are retained, incoming revision/time stripped and destination ownership/revision/time
allocated by protected flush. Source counter-only history is not exported. Native
cases cover same/cross-campaign alive/dead/all, graphs/references/facts/warnings/
provenance/credits, independent edits, runtime/reload, lowered limits, tracker-save
and late-history rollback, privacy, plain/serialized input, invalid/missing maps and
counter-only absence. It is delivered and tested, not unimplemented; 2D acceptance
still requires reconciliation after 2C. [Detailed import record](../handover/130-accounts-migration-fixture.md#private-setup-import-correction---2026-11-16).

## Covering CI and request-type follow-up - 2026-11-16

Follow-up de3f69bb6453553704df2a68cc73511f69c21dff rejects catch-all object and
inspect.Parameter.empty as concrete Request detection while preserving subtype
forwarding, requestless injection and post-lock authorization. Transaction body,
original failing fixtures and route/auth assertions remain. Four added regressions
retain the original seven methods. Earlier extracted/harness checks are not native
integration; their exact counts and missing-import corrections stay archived.

Green Branch tests 43893014815 attempt 1 covers that follow-up; publication
51a2fe7a8b9b06a6b9d23fc82843f39d1f55db01: 1,932 main tests OK, selected pytest
43 passed and all configured stages passed. Audit: 213 modules, zero failed, all
tracked connections closed. This supersedes the combined-corrective-suite failure/
CI-pending status, not its historical evidence limitations or wider acceptance gates.

## Green evidence reconciliation and 2B boundaries - 2026-11-16

Boundary delivery 5d1165ea12d361833558ee5e9dd021c3a1078668 adds
 tests/test_statblock_2b_boundaries.py and documentation only, no production changes.
Covering push-triggered Branch tests 43899670266 attempt 1 completed successfully;
evidence publication 3126dfed318158d3e6bc1fc2cbed878e1921c360. Main unittest:
1,943 tests OK; selected pytest: 43 passed. Syntax/server import, JavaScript,
standalone browser/audit and visual-artifact upload steps passed. run.json/jobs.json
establish exact coverage; workflow part 120 explicitly records all eleven new
methods OK. Parts 125-129 and 138-139 supply reviewed core entries and suite totals.

### 2B criterion-to-evidence reconciliation

| Agreed gate | Evidence and disposition |
|---|---|
| Capture, fingerprints, pruning, private history | RecoveryCaptureTests and Stage 2 contract assertions preserve full metadata/definitions/references, explicit empty capture, private-aware fingerprints, snapshot independence, pruning/cascades and wrong-scope/kind/ID rejection. Native passing evidence, not earlier capture doubles. |
| Restore, reset, scope, reload and lowered trusted-read limits | RestoreKernelTests, ProductionRestoreTests and Stage 2 contracts exercise stored replacement, reset preservation, saved/runtime isolation, restart/reload, oversized trusted stored content and configured preparation-limit separation. Native pass evidence from reviewed core suites and prior source/assertion reconciliation. |
| Sequential undo and stale predecessors | ProductionRestoreTests explicitly passes two private replacements undone in sequence, tracker undo, mismatched predecessor rejection and runtime isolation. Private-only metadata changes remain fingerprint-significant. |
| Durable counters, all-writer preservation and trusted clearing | ProductionRevisionTests, counter-writer/restore suites and prior assertion review retain hidden counters/bindings through rebuild/reopen, clear/re-add history, stale/digest/corruption rejection, and rollback. Constrained-SQLite ClearSqlTests and mocked TransactionDetectionTests remain supplementary, not native proof. |
| Protected flush, live refresh, rollback and projection privacy | PrivateTransactionSaveTests, ProductionRestoreTests, mutation/transport privacy and Stage 2 assertions cover tracker/private write order, one revision advance, unchanged/tracker-only metadata, final refresh, history rollback, source/runtime separation and no private JSON fields. |
| Actual recovery-route authorization | Six new RecoveryRouteBoundaryTests pass with the actual feature installer, AuthService, ownership and SQLite: owner restore/undo, existing superadmin policy, missing/client/non-owner/origin denials, foreign/kind-confused snapshots, confirmation/stale revision and stale undo ID/digest. Rejections preserve complete SQL/live/private/history state and send no frame. |
| Native mixed-clear exhaustion | Two new NativeClearExhaustionTests pass for saved and detached-runtime destinations. A second clear binding at MAX_REVISION rejects mixed clear/replace before tracker/counter writes, preserving exact SQL/bindings/live/source state and emitting nothing. |
| Production notification coalescing | Three new NotificationBoundaryTests pass through real broadcast/deferral and viewer projection: handler/private-flush requests coalesce into one post-commit frame with final metadata/revision/history; late rollback and true no-op send nothing. |

Disposition: completed/accepted for bounded 2B by approval of this payload. No
outstanding agreed 2B criterion was identified in the reconciliation. This does not
claim exhaustive schedules/cases or substitute green CI for criterion review.
Seeded-session in-process ASGI is not password login/full application startup;
recording sockets are not real-network WebSockets or browser delivery. No new
live-server, human visual, provider, listener or exhaustive E2E proof. No tests ran
locally for this documentation update and no fresh CI is claimed or dispatched.

## Remaining gates and delivery order

1. 2B is closed only for the bounded scope/evidence above. Do not reopen accepted
   022.02 or mark Stage 1/2, 022.03 or overall 022 accepted from this decision.
2. 2C/2C.3c is next and remains in progress. Existing clone, stored-copy, move,
   protected transfer, loaded-move detachment and Save As suites now have passing
   native/selected-ASGI evidence; do not retain blanket unexecuted labels. Reconcile
   independent rows/destination revisions, immutable source/counters, fresh ownership/
   time without counter-only export, references/collisions/naming/rosters, matching
   bindings, shared-runtime rejection and rollback. Prepare combined protected Save
   As -> copy -> loaded move -> runtime Save As sequences with recovery/history,
   final revision/live metadata, production notifications, private projections and
   actual Save As authorization/denials. Preserve same-owner stale-save and other-
   owner overwrite counter continuity; omission never clears. Keep seeded-session
   ASGI distinct from full login/server/browser/socket coverage. Production changes
   only if new regressions demonstrate a defect; exact approval and covering CI
   review precede 2C acceptance.
3. 2D: reconcile delivered correction-9 imports after 2C: scope, authorization,
   independent revisions, immutable source, runtime, limits, rollback and privacy.
   Do not label delivered selected/life-filtered import work unimplemented or accepted.
4. Stage 3: implement/test the actual private bundle representation and roundtrip,
   aggregate/snapshot/member limits, malformed/untrusted input, provenance and
   rollback. No silent loss at 10 MiB manifest/archive limits: explicit aggregate
   rejection or separately validated reference members. This private-content bundle
   work remains unimplemented, distinct from existing tracker-only bundles.
5. Final covering validation and every parent acceptance criterion remain mandatory.
   Stage 1/2, 022.03 and overall 022 remain unaccepted; later viewer/provider/listener
   units remain pending. No incomplete later requirement is deleted by this close-out.

Schema stays 9; no migration/DDL. Deploy matching complete code/data only after
validation/acceptance. Keep matching storage/config/media/code backups; never roll
older code alone over ledger-bearing data. README and HANDOVER.md index links stay
unchanged. TODO.md updates only the obsolete 022.03 initial-adapter/CI-pending index
summary. This is a documentation-only [skip ci] close-out, not a new test delivery.

## 2C.3c first combined-operation slice - 2026-11-16

Status: prepared for exact-payload approval; native execution and covering CI pending.
Two methods in tests/test_statblock_combined_setup_operations.py use actual protected
Save As/copy/move handlers, SQLite, private adapters and recovery/history services.
The successful sequence checks unsaved live content through Save As -> copy -> loaded
move -> runtime Save As, independent/fresh destination ownership and metadata, exact
preserved source/copy/moved bindings, collision naming, live/last-setup references,
checkpoint preservation, reload, missing-source checkpoint rejection and privacy.
The failure sequence runs real final-Save-As history processing before raising and
asserts exact SQL/live/private/history/reference rollback, preserving earlier commits.

Preparation checks: Python compilation and AST parsing pass; two test methods found.
Zero native methods ran locally because FastAPI is absent. No new native/CI pass or
full 2C.3c acceptance is claimed; no production, existing-test or workflow change.
Push this mixed test/documentation increment without [skip ci], then review its
covering CI and fix demonstrated failures with fresh approval. Remaining 2C.3c
authorization, production-notification and revision/recovery reconciliation gates
above remain open; 2B stays closed and later stages are not advanced.
[Scope and limits](../handover/140-viewer-ownership-fixtures.md#2c3c-first-combined-operation-slice---2026-11-16).
