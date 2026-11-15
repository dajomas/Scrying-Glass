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
- 2B.3: 8e4d625d7785275c935a3c40b5f45323de329801 wires the kernel to checkpoint
  and undo restoration after campaign/reference/roster validation. Private metadata
  survives normalization, including empty maps, and refreshes from saved output.
  Seven prepared service tests, not executed. Existing protected transactions own
  surrounding roster/runtime/audit/history/version persistence and rollback.
- 2B.4: durable stored-row revision counters use an existing typed attribute row,
  hidden from ordinary loaded dictionaries and rejected as ordinary input. The
  production StatblockStorage writer allocates from max(header,counter), validates
  final metadata and records the counter in the same transaction. Existing header-
  only protocol fixtures retain their old behavior; clearing must not be enabled
  on a protocol lacking durable-counter support. No clear API is enabled here.

Undo continuation from 2B.3 may update only the immediate predecessor whose digest
matches that recovery image and whose restored tracker/content checks agree.
Unrelated stale/foreign history remains stale; no general digest migration exists.

## Validation and unfinished work

Eight new ledger tests passed in an isolated namespace against real in-memory
SQLite, executing the exact new ledger helpers/test methods with representative
tables. They cover bootstrap, absence, integer/decrease/overflow guards, rollback,
ownership/cascade, private decoding/input rejection and corrupt/colliding markers.
This is not production facade/model/service validation. Five additional production
writer tests are prepared, not executed: bootstrap, absent-header tracker save/
privacy, forbidden input, failed/nested rollback and reopen. Their simulated header
deletions test counters only, not an implemented service clearing contract. The
new module, test module and changed writer snippet AST-parse; full import and
covering repository suites remain pending. Earlier staged suites remain unexecuted.

Remaining 2B, in order: coordinate adapter reattachment and ordinary row-rebuild
preservation, including counter-only monsters; implement trusted clearing with
stale/scope checks and fresh live metadata; integrate arbitrary private-only saves
with comparison, persistence and refresh; expand/run undo/absence/scope/restart/
limits/rollback coverage. The current explicit-empty checkpoint contract still
fails closed. No 2B/Stage 1/Stage 2 acceptance or completion is claimed.

2C: independent setup copy/Save As ownership/revisions, source immutability, move
preservation, canonical references and rollback. 2D: selected/life-filtered import
binding remapping and independent clone revisions. Stage 3: actual bundle
representation, aggregate/snapshot/member limits, malformed input, untrusted
provenance and rollback; no silent 10 MiB manifest/archive loss. All remain open.

The user requested the rest of 022.03 at 18:20 CET; preparation proceeds in that
order, with separate bound approvals for coherent writes. Final Stage 3 covering
CI remains deferred by instruction. Existing unittest discovery includes the new
test file. No dispatch or workflow edit. Keep matching code/data backups: schema
9 is unchanged, but older readers do not understand the private ledger kind.
Do not deploy this partial feature or roll code back alone over ledger-bearing
data. README whole-tree/backup guidance remains applicable. No viewer/provider/
listener, schema migration, merge/deployment/release or feature closure is implied.
