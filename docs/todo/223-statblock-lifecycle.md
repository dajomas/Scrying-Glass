# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage handover](../handover/240-sqlite-storage-split.md) · [Validation/history](../handover/030-validation-and-next-steps.md)

## Status and delivery rules - 2026-11-15

022.03 and overall SG-TODO-022 remain in progress; 022.02 remains accepted/
closed. Stage 1 has not been accepted or fully validated. Approved order remains
storage/private state, recovery/reset/copy, then bundles. All intermediate
022.03 commits include [skip ci] by the 14:14 user instruction. Final Stage 3
code push must omit it; no workflow changes or separate dispatch. Each write
requires its own bound approval and relevant tests/documentation.

## Baseline and retained contracts

Latest 2A delivery: b1754d78ada3e66780b0b426b8bd70483c4d3f50. Earlier adapter,
service, privacy and contract-test history remains in linked handovers/Git,
including ten Stage 2 contracts at 831c94249de8ef057cdcdbd0ead673d97ef98923.
Prepared repository tests have not executed locally; AST parsing and isolated
JSON/deepcopy checks are not model/storage/service/transport or CI passes.

Snapshots remain typed, encounter/combatant-scoped and private. Raw serialized
_statblocks fields are not trusted. Internal PrivateEncounterState attributes
survive deepcopy, not ordinary JSON. Stored reads use permissive budgets so
reduced preparation settings do not erase accepted content; untrusted new
preparation/imports require server limits. Tracker edits preserve content metadata;
replacement revisions increase. The content digest excludes revision/time/itself.
Ordinary save omission fails closed; explicit recovery absence needs its own
trusted clear semantics. Deletion cascades. No source/provenance promotion.

## Stage 2 increments

2A supplies atomic checkpoint/undo capture/read using existing relations,
independent stored ownership, historical metadata and explicit empty maps.
Its ten tests are prepared; restore/apply was not delivered by 2A.

2B.1 adds canonical private metadata to production recovery fingerprints and
prunes removed-monster bindings during feature reconciliation. No-content hashes
retain the previous algorithm; logs and active-turn markers remain excluded.
Private revisions/preparation times are intentionally included in recovery
fingerprints even though excluded from the content digest. Nonmatching older
undo after_digest values stay stale, not rewritten or silently accepted.

A full state_changed helper also detects private differences but is not wired
into the transaction save gate yet. Nine tests cover legacy hashes, private-only
and metadata-only differences, canonical IDs/order, log exclusions, copy/privacy,
invalid input and pruning. Helper/test AST parsing passed; tests have not run.

Remaining 2B: trusted replacement/clear restoration, metadata-preserving
normalization, destination revision policy, transaction private-save integration
and live-metadata refresh. Do not merely activate comparison while ordinary
saves still ignore private attributes. Add undo, stale/cross-campaign/absence,
deletion/replacement and failure/rollback coverage.

2C: setup copy/Save As with independent ownership/revisions and unchanged source,
move preservation, canonical reference integrity and rollback. 2D: selected/
life-filtered imported-monster binding remapping and independent clone revisions.
Local strings are snapshot-scoped; stored ownership must remain independent.

## Open gates

- Stage 1: private save/normalization review and covering service, storage,
  migration/restart, limits and HTTP/WS privacy execution. Prepared fixture apps
  are not full registration/startup/password-login/network/browser coverage.
- Stage 2: complete and satisfy reset, checkpoint/undo, explicit absence, copy/
  move/Save As, import remapping and private-only changes. Remaining contracts
  can still fail; no assertions are skipped or weakened to claim completion.
- Stage 3: bundle representation, aggregate/snapshot/member limits, malformed
  data, untrusted provenance and rollback; no silent 10 MiB manifest/archive loss.

Covering final Stage 3 CI and acceptance remain pending. No schema/migration,
viewer/provider/listener, merge, deployment, release or whole-feature closure.
