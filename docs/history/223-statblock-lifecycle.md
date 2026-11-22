# 223 - Statblock lifecycle integration

[Back to history index](../../HISTORY.md) · [Parent contract](220-admin-statblock-viewer.md) · [Current handover](../handover/140-viewer-ownership-fixtures.md#final-lifecycle-accepted-close-out---2026-11-17)

## Status - 2026-11-17

SG-TODO-022.03 is completed, accepted and closed. At 06:01 CET the user explicitly
requested closure of whole Stage 1, whole Stage 2 and 022.03 after whole Stage 3
acceptance. The final reconciliation below supports that decision; it is not an
automatic promotion of a green badge. Stage 1, Stage 2 and Stage 3 are now closed.
Existing 022.02 and bounded 2B/2C/2D/3A/3B acceptances remain unchanged.

Overall SG-TODO-022 remains open. 022.04-022.16 provider/viewer/listener/import-UI
work and SG-TODO-023 remain separate. No merge, deployment, release, usable private
statblock viewer/import UI or whole-feature acceptance is claimed. This current
lifecycle status supersedes older pending-022.03 summaries, not later requirements.

## Preserved complete records

[Whole Stage 3 map and evidence](https://github.com/dajomas/Scrying-Glass/blob/25b55cfbb6ba9fc25620d94e04ef21682db03414/docs/todo/223-statblock-lifecycle.md)
and [preceding handover](https://github.com/dajomas/Scrying-Glass/blob/25b55cfbb6ba9fc25620d94e04ef21682db03414/docs/handover/140-viewer-ownership-fixtures.md)
retain complete 3A/3B maps, failed-run/correction history, exact counts and evidence
limitations through immutable links.

[Accepted 2B map](https://github.com/dajomas/Scrying-Glass/blob/dae492f2e95bc378d73425f22dd5e85d9c681215/docs/todo/223-statblock-lifecycle.md)
and [accepted 2C/2D maps](https://github.com/dajomas/Scrying-Glass/blob/e8546fb1ec14e4163faa89c326592948d6d81c46/docs/todo/223-statblock-lifecycle.md)
retain all earlier lifecycle contracts and archived implementation history.
No unfinished requirement, failed evidence or limitation is deleted by this summary.

## Final criterion reconciliation

| Lifecycle gate | Evidence and final disposition |
|---|---|
| Stage 1: encounter/combatant ownership and ordinary save preservation | ProductionStatblockSaveTests checks real setup/runtime row rebuilds, retained graphs, plain load/get projections, legacy ID allocation without input mutation, selected-encounter deletion cascade and late reattachment rollback. All six explicitly OK in final workflow part 129. Satisfied. |
| Stage 1: trusted loading, restart and independent state | ServicePrivateLoadTests checks saved setup fallback versus nonempty runtime, deepcopy isolation, unsaved restart/subsequent save, lower preparation defaults, failed-read live-state preservation and source loading without live mutation. All seven explicitly OK in final workflow part 133. Satisfied. |
| Stage 1: private authority and transport projection | Ordinary save rejects serialized private envelopes; trusted carrier metadata stays outside JSON. Service loading and StatblockTransportPrivacyTests exercise actual serializers, scoped admin/client HTTP and in-process WebSocket initial/resync/heartbeat/broadcast/revocation paths. No ordinary/private-authority promotion. Satisfied within fixture limits. |
| Stage 2A/2B: recovery, reset, history and revision continuity | Accepted 2B map covers independent capture, explicit absence, fingerprint/pruning, reset preservation, replacement/reload, sequential undo and stale predecessors, monotonic durable counters, trusted clearing, exhaustion preflight, rollback and notification coalescing. Core protected private saves and production restore have explicit final-run passes in part 128; capture/kernel/counter passes in parts 129-132. Satisfied. |
| Stage 2C: copy/move/Save As | Accepted eight-group map covers independent clone ownership, stable moved bindings, detached runtime, new/existing Save As, source/counter isolation, references/rosters/collision rules, overwrite/stale guards, combined recovery sequences, actual authorization/post-lock checks and rollback/privacy/notifications. Satisfied; bounded accepted work is not reopened. |
| Stage 2D: selected/life-filtered import | Accepted six-group map covers actual ID remapping, independent content/revision, source and runtime isolation, incoming operator limits, actual-route authorization/post-lock checks, history/notifications/rollback/privacy and zero-selection semantics. Satisfied. |
| Whole Stage 3: actual bundles | Accepted nine-group map at 25b55cfbb6ba9fc25620d94e04ef21682db03414 covers chosen version-2 representation, version-1 compatibility, full private setup/runtime/checkpoint fidelity, safe ownership/provenance, real archive/model boundaries, route security, rollback and combined lifecycle. Satisfied unchanged. |
| Parent lifecycle preservation requirement | Reset, ordinary saves/rebuilds, runtime/restart, recovery/checkpoint/undo, copy/move/Save As, selected imports and actual bundle roundtrip are reconciled above. Deletion cascades; serialization cannot grant authority; no silent aggregate loss. Provider conversion/display/listener/apply-UI requirements remain later units, not waived or accepted here. Satisfied for 022.03. |

No blocking unmet requirement was identified within the agreed 022.03 lifecycle
scope. Accept and close whole Stage 1 and Stage 2 and, with already accepted
whole Stage 3, SG-TODO-022.03. Later-discovered defects remain defects to address.

## Covering validation and acceptance identities

Final covering Branch tests run 43963574986 attempt 1 is completed/success for
0d1cec345b187f7ecbbb1b959fd185927c18c046; immutable publication
7aeb144b1e6adb3d28a08bc0e3262975742bed1b. Main Python suite: 1,987 tests OK
in 259.975s, including the 14 new 3B methods; configured syntax/import, selected
pytest, JavaScript and standalone Python browser/audit stages succeeded.
This review additionally inspected Stage 1 save/load test bodies and explicit
core passes in final workflow parts 128-133. No new test execution is claimed.

Earlier accepted evidence remains: 2B run 43899670266 attempt 1; 2C run
43933600072 attempt 1; 2D run 43941792616 attempt 1; 3A run 43958297280
attempt 1. Exact heads/publications/counting limits remain in linked maps.
3B acceptance bb4cbae45ddc7448734a5f0224074633c1c6bf37; whole Stage 3
acceptance 25b55cfbb6ba9fc25620d94e04ef21682db03414. Do not sum CI-run totals
or count reruns as unique coverage. No earlier isolated harness result is
promoted to native persistence, actual authorization or live-network evidence.

## Retained limitations and operational rules

Selected-route seeded-session ASGI is not password login/full application startup.
In-process WebSocket and recording-socket notification tests are not browser/network
delivery proof. Internal fixture edits are not a public private-edit API. Padded
manifest/media-size fixtures are admission tests, not image decoding. Individual
late fault injections are not exhaustive simultaneous-fault, crash or power-loss
proof. Marker/privacy assertions are not a general information-flow proof. No
live-provider, exhaustive platform/scheduling, deployed-server or human visual/
screen-reader acceptance is inferred. Those limits do not waive later units.

Private graphs remain encounter/combatant-scoped; ordinary omission cannot clear.
Trusted recovery alone may clear; durable ledgers remain monotonic. Raw save_setup
is tracker-only. Trusted stored reads/export use permissive budgets; new imports
use operator limits. Bundles grant no verified online provenance/fetch authority.
Schema remains 9. Keep matching complete code/storage/config/media backups; never
roll older code alone over ledger-bearing data.

This exact-approved close-out is documentation-only [skip ci]: no production,
test, workflow, permission or schema changes; no fresh CI claimed or dispatched.
Next work belongs to still-pending 022.04-022.16, not another lifecycle acceptance
gate. Overall 022 remains open; no merge/deployment/release is authorized.
