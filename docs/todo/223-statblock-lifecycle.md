# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage handover](../handover/240-sqlite-storage-split.md#02203-stage-1-private-adapter---2026-11-15)

## Status and agreed staging - 2026-11-15

SG-TODO-022.03 and overall SG-TODO-022 remain in progress. 022.02 remains
accepted/closed. Approved delivery order: (1) storage/private state,
(2) recovery/reset/copy, (3) bundles. Each bounded commit requires its own
complete write approval, tests and documentation. Under the user's 14:14
instruction all intermediate 022.03 pushes use [skip ci]; the final Stage 3
code push must omit it. No workflow edits or separate CI dispatch.

Delivered preparation history is retained in the linked handover and commits:
- First opt-in encounter adapter and six tests; no production wiring then.
- Helpers/four tests: 34d9d417246ebff4c3481056d425ef2bbd54f6a7.
- Adapter revision correction/six tests: 7c721a5586bdc7a582edbb6467d1b0d0f1c4c6dc.
- Production save preservation/six tests: c76f2e1a6ccf85b3a172418839ba8db7c6104d45.

The adapter is internal and encounter-scoped, not an authorization/network
boundary. New untrusted preparation/imports require validated server ModelLimits.
Stored reads retain permissive budgets so reduced preparation settings do not
erase accepted data. Snapshots bind to combatant identity within an encounter,
not names or globally unique database row assumptions. Tracker edits preserve
content metadata; content replacement increments logical revisions. Explicit
omission of surviving snapshots fails closed; removed monster bindings cascade.
The real content digest excludes revision/prepared_at/content_digest: the earlier
claim that revision-only patching necessarily corrupted it was incorrect.

## Private service-loading increment

PersistenceService now loads private content for saved setups and runtime.
SQLite reads resolve the exact campaign/name or singleton runtime encounter
inside a transaction and check the plain/private views agree. Non-SQLite test
doubles keep their existing plain loader protocol; there is no provider/source
fallback. Campaign authorization remains before setup reads.

Internal PrivateEncounterState keeps the map in its _statblocks attribute, not
in dictionary fields or monster tracker dictionaries. Deepcopy retains it;
ordinary JSON does not. Existing raw _statblocks input remains rejected. The
normalizer used by service loads validates private content separately with stored
read limits and attaches it after tracker normalization. Loading a setup as an
import source does not replace live state or its metadata.

Empty-runtime fallback takes private content from the same setup supplying
monsters. Nonempty runtime retains its own metadata, never the setup's copy.
State assignment occurs only after successful restoration. Existing database
save-preservation still handles ordinary saves; this increment does not serialize
private metadata into JSON or implement source-to-destination copying.

Seven prepared service tests cover setup/privacy/deepcopy, fallback, runtime
precedence, unsaved restart/save, stored text above preparation defaults, failed
read atomicity and non-mutating source loads. Helper/test AST parsing passed;
these repository tests have not executed. Earlier stub passes are not evidence
for these tests, the real model or production services. Covering CI is pending.

## Remaining acceptance gates

- Stage 1: finish/review private save/normalization lifecycle and real HTTP/WS
  response-boundary privacy tests, stale ownership, deletion/replacement,
  rollback, migration/restart and stored-limit coverage. Do not mark complete
  from helper/source review or a push. No statblock viewer/provider/listener yet.
- Stage 2: reset, undo/checkpoints, setup copy/move/Save As, local-ID remapping,
  independent destination ownership/revisions and explicit missing-content
  restoration. JSON recovery does not preserve the internal attribute yet;
  normalizing outside the integrated load paths may also lose it. Implement
  this explicitly, without silently retaining the wrong current snapshot.
- Stage 3: bundle representation, aggregate/snapshot/member budgets, malformed
  input, attribution/untrusted provenance, atomic rollback. Existing 10 MiB
  manifest/archive limits must not silently discard content or metadata.

All stages, final covering CI and acceptance remain open. No schema change,
migration, merge, deployment, release or whole-feature completion is claimed.

## HTTP/WebSocket privacy validation preparation - 2026-11-15

Service loading was pushed in 737bd81b2400cef6d172429a88feaeffd24f22e4.
Seven in-process ASGI regression methods are prepared for ordinary Admin HTTP,
live/saved Client HTTP, auth/grant error responses, WS initial/resync/heartbeat,
broadcast/revocation, denied selections, and unauthenticated/cross-origin WS.
They seed distinct private markers in real SQLite snapshots and load through
production services, mount production handlers/auth/serialization in small test
apps, and check public identity/HP filtering as positive controls. They do not
construct the full application or run password login, lifespan or network servers.

Test source AST parsing passed. FastAPI import failed in the preparation
environment, so none of these transport tests executed. Four isolated checks
of the exact state-class body passed for standard-library JSON omission,
metadata presence, deepcopy retention and independence; these are not transport,
model/storage integration or repository-suite evidence. No privacy leak was
confirmed or ruled out by execution. Final Stage 3 CI and Stage 1 review remain
pending; no production auth/routes/projections or workflow changes here.
