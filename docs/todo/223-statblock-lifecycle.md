# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Current handover](../handover/130-accounts-migration-fixture.md#private-setup-import-correction---2026-11-16)

## Status and delivery rules - 2026-11-16

SG-TODO-022.03, 2B, 2C and overall 022 remain in progress, not validated or
accepted. Stage 1/2 remain unaccepted; 022.02 stays accepted/closed. Approved order
remains private storage, recovery/reset/copy, then bundles. 022.04-022.16 remain
pending. No merge, deployment, release or whole-feature closure is authorized.

Corrections 1-8 were pushed with [skip ci]. Correction 9 was pushed without it;
its covering run failed and the diagnosed request-type follow-up below is prepared.
Follow-up code commits use configured push CI, with no [skip ci], manual dispatch
or workflow edit. The earlier nine-commit skip agreement does not extend to fixes
required by that failed covering run.
Each write needs complete exact-payload approval. Review the covering commit/run/
attempt before claiming the series passes. Further failures require diagnosis and
freshly approved fixes; never skip/weaken assertions. A green configured suite is
not acceptance of Stage 1/2, 022.03 or 022. Documentation-only commits still skip CI.

## Preserved history and contracts

[Complete correction-8 baseline lifecycle record](https://github.com/dajomas/Scrying-Glass/blob/8162e812c3cb2e90df4e427bfa76d1d115f8a276/docs/todo/223-statblock-lifecycle.md)
retains every dated increment, test count, correction diagnosis, commit and evidence
limit previously recorded here. This current-state reconciliation supersedes only
its correction-8-prepared/correction-9-unimplemented wording. Its linked pre-2C.3b
archives and [scope](../handover/010-scope-and-state.md), [validation](../handover/030-validation-and-next-steps.md),
[fixture](../handover/130-accounts-migration-fixture.md) and [ownership](../handover/140-viewer-ownership-fixtures.md)
handovers remain historical evidence; no earlier pass is promoted and no unfinished
requirement is removed by this consolidation.

Snapshots remain encounter/combatant-scoped and private. PrivateEncounterState
carries metadata outside JSON and through deepcopy; serialized input and attributes
on ordinary dicts confer no private authority. Trusted stored reads use permissive
budgets; incoming preparation/imports use operator budgets. Digests exclude revision/
time/self-digest; recovery fingerprints include metadata. Ordinary omission fails
closed, removed combatants cascade and clearing remains trusted recovery-only.
There is no public clear flag, new route/permission or provenance promotion.

Raw SQLiteStorage.save_setup stays tracker-only: it preserves destination-owned
content but does not infer source ownership from a carrier or matching combatant ID.
Save As uses transactional_handler(context, AdminSetupsMixin.save_setup), routing
through save_setup_with_private/save_new_setup. Correction 8 retained all four
original preservation assertions, added ownership/live/reload checks and four native
cases. The original import-remapping contract is unchanged by correction 9.

## CI correction series - 2026-11-16

Historical Branch tests 43846424270 attempt 1 covers implementation
812de5ae6717f8a7f34892e0031858a0a3e089c6; publication
355598a1a571095b7f2bde58637a1fe2249bfd05. Overall failure: main unittest
1,896 tests, three failures, fourteen errors. Reader parts 135-146 contain failures;
part 130 records all six 2C.3b save-handler methods passing. Standalone connection
audit: 211 modules, six failed. Duplicate failures alone do not demonstrate leaks.
Those six baseline passes do not validate corrections 1-9.

One issue per corrective commit; delivered corrections:

1. Request forwarding: 4935fddbcdf14fe241ed052f4f81ff63275b4370.
2. Service AST extraction harness: 293376ea594eadb8077f97c1b076f7b36b3d1cd1.
3. Snapshot AST extraction harness: d68cccc128c8444d7fd6b917d7970820e857a17f.
4. Revision-test mutation producer: c69db3b112cf675ac9ba0c6c08afcc2fa2b7e904.
5. Facade mocked-copy boundary: 5109e0c152d99a2e2c9e33101c43e0e0739ced9c.
6. Native/legacy facade-copy fixture: c093d772513051f5c88623af1b72c63d89cde19a.
7. Facade dispatch guards: f2d4fa699e2ef1a56d56332e4c37a0d94057f8d6.
8. Protected Save As contract: 8162e812c3cb2e90df4e427bfa76d1d115f8a276.
   This reconciles the pushed payload's earlier prepared wording. Its contract
   methods passed in the failed covering run below; five preparation-time isolated
   checks were not native persistence/rollback/authorization evidence.
9. Private setup-import remapping: delivered at
   14ad1d3075f4e737c38270ea2a9734fd1f5b9ad3; eleven native methods passed
   in the failed covering run below, not acceptance. Exact handler map drives graph
   remapping to clone IDs. Existing destination metadata is retained; incoming
   graphs face the five ModelLimits budgets from CONFIG.statblocks.limits. Incoming
   revision/time is removed; existing flush allocates destination ownership and
   fresh revision/time, without source counters/tombstones. Tracker/reset/effect
   mapping and the existing protected transaction remain. No serialized authority,
   clearing, provenance promotion, route, permissions, schema or workflow changes.

Correction 9 adds eleven native methods covering same-setup/cross-campaign alive,
dead/all filters, graphs/references/facts/warnings/provenance/credits, independent
rows/revisions/edit isolation, unsaved-runtime import/reload, lowered limits,
tracker-save and post-private-flush/history rollback, commit-only notification,
privacy, serialized/plain input, bad maps/missing source, counter-only absence,
subset/empty maps and configuration. They and the unchanged original Stage 2
contract passed in the covering CI below; they were not run locally. At preparation,
three Python files compiled/AST-parsed; the
attachment matches the live admin blob and reverse replacement preserves its bytes;
unrelated methods are AST-identical. Eleven isolated exact-helper check groups
passed with capture/validation/carrier/limit doubles, not real model/SQLite/
transaction integration. Service fixtures and emitter seams do not establish
actor/HTTP authorization or actual WebSocket delivery. [Detailed current handover](../handover/130-accounts-migration-fixture.md#private-setup-import-correction---2026-11-16).

## Covering CI and request-type follow-up - 2026-11-16

Run 43889177129 attempt 1 covers 14ad1d3075f4e737c38270ea2a9734fd1f5b9ad3;
evidence publication/current baseline: 7ca39865274281bf02b3c7ad6da663b84af147a5.
Overall failure: 1,928 main tests, one failure and nine errors; standalone audit
213 modules, three failed (not proof of leaks). Syntax/server import, selected
pytest and JavaScript steps passed. Reviewed workflow parts 130-132 show all eleven
new setup-import methods, all fourteen Stage 2 contracts and six save-handler
methods passing. These passes do not establish a green combined corrective suite.

Prepared follow-up: only concrete Request types may suppress wrapper injection.
The object placeholder used by ownership/viewer/lair fixtures otherwise matches
ordinary annotations and inspect.Parameter.empty, misrouting campaign IDs/payloads
into authentication. Exclude object as the Request type and empty annotations;
retain concrete subtype forwarding and post-lock auth. Transaction body, failing
fixtures and original route/auth assertions remain unchanged. Four regressions
are added to the seven retained serialized-request methods. Production/test AST
and compile checks pass; six exact selected methods passed in an extracted wrapper
harness with Request/HTTP/ownership doubles, versus two failures with the old
wrapper. An isolated inspected-lair-installer check preserves all five routes and
auth/origin dependencies, restoring injection on all five; service/dependency
collaborators were doubled. FastAPI/Starlette are absent locally; no native ASGI/full fixture/module
or follow-up CI pass is claimed. Delivery awaits exact-payload approval; use normal
push CI and inspect its actual results before proceeding. [Diagnosis/history/limits](../handover/140-viewer-ownership-fixtures.md#generic-request-placeholder-follow-up---2026-11-16).

## Remaining gates and delivery order

The correction-9 covering run is reviewed above and failed. Deliver/review the
separately approved follow-up and resolve demonstrated failures before continuing
the lifecycle order. Do not infer that these selected passing suites close every
remaining lifecycle or authorization gate.

1. 2B: execute/review recovery capture, fingerprints/pruning, replacement and service
   restore, counter-ledger/all-writer, trusted-clear and protected-flush suites.
   Retain scope/restart/lowered-limit, sequential undo, stale/unrelated predecessor,
   rollback, private projection, clear/reopen/tombstone, no-op/late notification and
   exhaustion gates. Header-only protocols cannot clear; actual clear advances a
   durable counter and re-addition advances beyond it. Counter-only rebuilds must
   preserve hidden markers/bindings; ordinary inputs/corruption reject. Earlier
   isolated SQL/double passes and prepared suites do not close these gates.
2. 2C: execute/review clone, stored-copy, move-preservation, protected transfer,
   loaded-move detachment and Save As suites (2C.1/2C.2a-b/2C.2c.1-3/2C.3a-b).
   Check independent rows/destination revisions, immutable source/counters, fresh
   ownership/time without counter-only export, canonical references, collision/
   naming/roster rules, matching bindings, shared-runtime-owner rejection and late
   rollback. 2C.3c still requires combined protected Save As/copy/move operations,
   recovery/history/revision/notifications/privacy, actual authorization coverage
   and acceptance reconciliation. Seeded-session selected-route ASGI is not full
   server/login/browser/socket coverage. Same-owner stale-save and different-owner
   overwrite counter continuity remain required; omission is not clearing.
3. 2D: correction 9 supplies selected/life-filtered import implementation, not
   acceptance. Execute/review its native cases and reconcile remaining scope,
   authorization, independent revisions, source preservation, runtime, limits,
   rollback and privacy after 2B/2C. Do not label delivered work unimplemented.
4. Stage 3: implement/test the actual bundle representation and roundtrip, aggregate/
   snapshot/member limits, malformed/untrusted input, provenance and rollback.
   No silent loss at 10 MiB manifest/archive limits; report aggregate rejection or
   use separately validated reference members. Bundles remain unimplemented here.
5. Final covering validation and reconciliation of every parent acceptance
   criterion remain mandatory. Keep Stage 1/2, 022.03 and overall 022 unaccepted
   until their separate gates are met. Later viewer/provider/listener units remain
   pending; this corrective series does not complete the feature.

Schema stays 9; no migration/DDL. Deploy matching complete code/data only after
validation/acceptance. Older code lacks marker/filter handling: do not roll code
back alone over ledger-bearing data. Keep matching storage/config/media/code backups.
README/root index links remain applicable and unchanged.
