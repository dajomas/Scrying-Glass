# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage handover](../handover/240-sqlite-storage-split.md) · [Validation](../handover/030-validation-and-next-steps.md)

## Status and delivery rules - 2026-11-15

SG-TODO-022.03 and overall SG-TODO-022 remain in progress. 022.02 remains
accepted/closed. Approved order: Stage 1 storage/private state; Stage 2 recovery/
reset/copy; Stage 3 bundles. Stage 1 is not accepted or fully validated by the
user's request to advance Stage 2 test preparation. Each bounded write requires
its own complete approval, implementation/tests as applicable and documentation.
Intermediate 022.03 commits use [skip ci] by the user's 14:14 instruction; final
Stage 3 code push must omit it. No workflow edits or separate dispatch.

## Delivered baseline and evidence limits

Detailed dated history remains in the linked handovers and Git history:
- Opt-in encounter adapter/six tests; schema/model activation remains separate 022.02.
- Private-state helpers/four tests: 34d9d417246ebff4c3481056d425ef2bbd54f6a7.
- Revision reattachment/six tests: 7c721a5586bdc7a582edbb6467d1b0d0f1c4c6dc.
- Production save preservation/six tests: c76f2e1a6ccf85b3a172418839ba8db7c6104d45.
- Service loading/seven tests: 737bd81b2400cef6d172429a88feaeffd24f22e4.
- Transport privacy/seven tests: a208e3410507555e22e0d82b50e0d81708f54ffe.
- Mutation privacy/five tests: 5ecf122b7e9a2c7decde8dd26167d93c7e4711d0.
- Stage 2 contracts/ten tests: 831c94249de8ef057cdcdbd0ead673d97ef98923.

These repository regressions were prepared, not executed locally. Source AST
checks and four isolated standard-library JSON/deepcopy checks do not prove
model/storage/service/HTTP/WS behavior. FastAPI was absent from the preparation
environment. No observed privacy pass/leak or new covering CI result is claimed.
The Stage 2 tests are ordinary assertions, not skipped/expected-failure tests;
unfinished restore/copy/import/fingerprint contracts may still fail until built.

## Current private-state contract

The internal adapter binds snapshots by encounter-local monster combatant ID,
not display name or a guessed global row owner. It is not an authorization or
network boundary. Untrusted preparations/imports require validated server limits.
Trusted stored reads must survive lowered preparation settings. Ordinary tracker
saves preserve current content, metadata and revisions; replacements advance
logical revisions. Explicit omission of surviving content fails closed in the
ordinary adapter; deleting a monster cascades. The digest excludes revision,
prepared_at and content_digest; earlier claims to the contrary were corrected.

PrivateEncounterState carries _statblocks as an internal attribute, not a JSON
field or monster field. Deepcopy retains it; plain JSON does not. Service loads
authorize/setup-scope reads, retain runtime metadata for nonempty runtime, and
take setup metadata only with the empty-runtime monster fallback. Import-source
loads do not change live state. Raw serialized _statblocks fields stay rejected.
Private-only changes are not yet covered by ordinary dictionary equality.

## Stage 2 implementation increments

2A captures/reloads checkpoint and undo private content using existing typed
relations. Private graphs validate before capture writes; capture/load have
transaction boundaries. Captured rows are independent from the source and keep
historical revision/time/digest, not a current-destination restore revision. Empty
recovery content loads as an explicit empty attribute map without guessing the
source setup's current content. Campaign/kind scoping precedes private loads.
No schema change or serialized payload column is introduced.

Ten focused 2A tests cover round trips/references/full metadata, explicit absence,
independent ownership, pre-write invalid-graph/raw-field rejection, direct and
nested rollback, scope/ID guards, pruning/cascades and larger accepted text.
The helper (2,347 bytes), storage module (7,641 bytes) and tests (8,000 bytes)
AST-parse. These ten tests have not executed. Capture implementation is not
restore/apply completion; the earlier ten Stage 2 contracts remain unchanged.

2B remains: trusted replacement/explicit-clear restoration, metadata-preserving
normalization, private-aware fingerprints/transaction change detection, increasing
destination revisions and undo/checkpoint apply. Prevent silently retaining the
wrong current snapshot. Add stale confirmation, cross-campaign rejection, absent
content, deletion/replacement and rollback tests.

2C remains: independently owned setup copies and Save As, move preservation,
source immutability, local graph integrity and atomic failure. 2D remains:
selected/life-filtered imported-monster binding remapping and independent clone
revisions without provenance promotion. Copied local strings need only be unique
within their own canonical snapshot; relational IDs/ownership must be independent.

## Remaining acceptance gates

- Stage 1: finish private save/normalization lifecycle review and execute the
  prepared service/privacy suites, including representative mutation replies,
  rollback, scoped ownership, restart/migration and stored-limit checks. Fixture
  apps are not full registration/startup/password-login/network/browser coverage.
- Stage 2: satisfy reset, checkpoint/undo, copy/move/Save As, import remapping,
  missing-content restoration and metadata-only change contracts. 2A does not
  make current restore/normalize/copy/bundle paths preserve the attribute.
- Stage 3: select/test bundle representation, aggregate/snapshot/member budgets,
  malformed data, untrusted provenance and atomic rollback. Existing 10 MiB
  manifest/archive limits must not silently discard content or metadata.

Covering final Stage 3 CI and acceptance remain pending. No viewer/provider/
listener feature, merge, deployment, release or whole-feature completion claimed.
