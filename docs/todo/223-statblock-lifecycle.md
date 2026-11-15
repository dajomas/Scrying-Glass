# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage handover](../handover/240-sqlite-storage-split.md) · [Validation/history](../handover/030-validation-and-next-steps.md)

## Status and delivery rules - 2026-11-15

SG-TODO-022.03 and overall 022 remain in progress. 022.02 stays accepted/closed.
Stage 1 remains unvalidated/unaccepted. Approved order remains private storage,
recovery/reset/copy, then bundles. Intermediate 022.03 commits include [skip ci];
only the final Stage 3 code push omits it. No workflow edits or separate dispatch.
Each write requires bound approval, implementation tests and documentation.

## Retained contracts

Typed snapshots remain encounter/combatant-scoped and private. Raw serialized
_statblocks input is not trusted. PrivateEncounterState keeps metadata outside
ordinary JSON; deepcopy retains it. Trusted stored-state validation uses permissive
read budgets; new untrusted preparation/imports require server limits. Tracker-only
edits preserve metadata; replacement uses destination revisions. Content digests
exclude revision/prepared_at/itself; recovery fingerprints include those metadata.
Ordinary omission fails closed, deletion cascades, and explicit recovery absence
requires a separate trusted clear contract. No source/provenance promotion.

## Delivery history and current implementation

- Stage 1: normalization/filter helpers, adapter corrections, ordinary save
  preservation, private loading and response/privacy tests supplied; covering
  validation and acceptance still pending. Earlier handovers/Git retain details.
- Stage 2 contracts: ten tests at 831c94249de8ef057cdcdbd0ead673d97ef98923;
  assertions are not skipped or weakened to claim completion.
- 2A: b1754d78ada3e66780b0b426b8bd70483c4d3f50 captures/loads checkpoint and undo
  images with independent typed ownership, historical metadata and explicit empty
  maps. Ten prepared tests, not executed.
- 2B.1: 1214bed0833ee312f305ce88937dae8f7d60170f adds production private-aware
  fingerprints and reconciliation pruning, plus an unwired full comparison helper.
  Nine prepared tests, not executed. Older mismatching undo digests remain stale.
- 2B.2: 5c8b4776c72a949cbecfef0f00194064a07fdc46 adds a replacement-only kernel
  with exact stored-row/revision binding checks and atomic tracker/reference
  writes. Nine prepared tests, not executed. It rejects surviving-content clearing.
- 2B.3: FeaturesService.restore_state now calls that kernel for checkpoint and undo
  recovery after the existing campaign/reference/roster validation. Internal
  recovery metadata survives normalization, including an explicit empty map.
  Setup destinations resolve by active campaign/name; unsaved encounters resolve
  the singleton runtime binding. Live private metadata refreshes from saved output.
  Existing endpoint authorization, confirmation and outer transaction still own
  roster/runtime/audit/undo/version persistence and rollback; no new route exists.

Undo may update only the immediate predecessor whose existing after_digest equals
that exact recovery image's fingerprint, and only when restored tracker content
and private content digests match. This accounts for fresh destination metadata;
foreign/stale/nonmatching entries are not rewritten or made actionable. Tracker-only
undo keeps current snapshot metadata. No general stale-digest migration is added.

## Validation and unfinished work

Seven additional prepared service tests cover kernel invocation/live refresh and
JSON projection, sequential private undo, nonmatching predecessor rejection,
tracker-only undo metadata, rejected clearing, late save rollback and unsaved
runtime/setup isolation. Changed method snippets and the test module AST-parse;
no full module/server import, repository tests, HTTP/WS/browser or CI execution
is claimed. Existing configured unittest discovery includes test_*.py; no workflow
changes or separate dispatch. Final Stage 3 covering CI remains pending.

Remaining 2B: coordinated durable counter/clear/all-writer behavior; complete
service and transaction private-save integration for arbitrary private-only edits;
undo/absence/stale/scope/restart/limits and rollback validation. Merely activating
the full comparison helper is insufficient while ordinary saves ignore attributes.
The explicit-empty checkpoint contract still fails closed until clearing exists.
This production replacement wiring is not completion or acceptance of 2B/Stage 2.

2C: independent setup copy/Save As ownership/revisions and source immutability,
move preservation, canonical references and rollback. 2D: selected/life-filtered
import binding remapping and independent clone revisions. Local IDs are snapshot-
scoped, not shared stored ownership. Stage 3: bundle representation, aggregate/
snapshot/member limits, malformed input, untrusted provenance and rollback; no
silent 10 MiB manifest/archive loss. All remain pending.

Stage 1 still needs covering service/storage/migration/restart/limit/HTTP/WS privacy
execution; fixture apps do not prove full startup/authenticated/browser behavior.
No viewer/provider/listener, schema/migration, merge/deployment/release or overall
feature completion is implied. README and root index links remain applicable.
