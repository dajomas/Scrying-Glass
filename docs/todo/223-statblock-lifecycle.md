# 223 - Statblock lifecycle integration

[Back to TODO index](../../TODO.md) · [Parent contract](220-admin-statblock-viewer.md) · [Storage handover](../handover/240-sqlite-storage-split.md#02203-stage-1-private-adapter---2026-11-15)

## Task and staging - 2026-11-15

SG-TODO-022.03 is in progress. The user approved the staged delivery order at
13:59 CET: (1) storage/private state, (2) recovery/reset/copy, (3) bundles.
Each stage may use bounded commits with its tests/documentation and its own
write approval. Normal CI applies to code commits; the earlier 022.02 skip-CI
sequence ended at activation. 022.02 remains accepted and closed.

Stage 1 first increment includes an opt-in PrivateEncounterStorage adapter,
recursive private-payload projection and six regression tests. Covering CI is
pending; tests were prepared/reviewed, not executed locally. Normal application
storage, StateService normalization, endpoints and transports are not wired to
it yet. Do not describe this increment as complete Stage 1 or user-facing support.

The internal `_statblocks` map is keyed by monster combatant ID within a verified
encounter, never by database row ID or display name. Before-row snapshots are
captured under the transaction and reattached if the backend rebuilds rows.
Ordinary content-preserving saves keep revision/time/digest; replacements bump
the logical instance's revision. Missing legacy maps preserve existing content.
Explicit maps that omit an existing surviving snapshot fail closed; clearing/
restore semantics remain Stage 2, not a new partially implemented clear API.
Deleted monster bindings cascade; unrelated encounter IDs are rejected.

Adapter defaults are for trusted stored-state round trips, preserving content
accepted under larger operator limits. New untrusted preparations/imports must
supply validated server-controlled ModelLimits and enforce their full budgets.
The adapter is not an authorization or network boundary. Canonicalization and
graph validation precede the save transaction; SQL failures roll back tracker
edits and content together. Projection tests are utility tests, not proof that
existing HTTP/WebSocket response boundaries have been integrated or tested.

## Remaining gates

- Stage 1 follow-ups: wire the existing plain encounter and private normalized
  state boundaries without recursive delegation; preserve authoritative-setup
  fallback/restart behavior; keep private data out of ordinary Admin replies,
  Client Display and transports. Test actual service paths, stale ownership,
  deletion/replacement, rollback and lowered-limit stored-state preservation.
- Stage 2: reset, undo/checkpoint capture/restore, setup copy/move and imported
  monster local-ID remapping; independent destination ownership/revisions and
  explicit missing-content restoration, without silent loss or source promotion.
- Stage 3: choose/test the bundle representation, aggregate/snapshot/member
  limits, malformed input, attribution/untrusted provenance and atomic rollback.
  Existing 10 MiB manifest and archive limits must not silently discard content.

Keep 022.03 and overall SG-TODO-022 open until all agreed stages, covering CI and
acceptance are satisfied. No provider adapter, statblock UI or listener is added
by this increment. No new migration, merge, deployment or release operation.

## Helper increment and CI deferral - 2026-11-15

The user's 14:14 instruction supersedes normal-CI wording above for intermediate
022.03 pushes: use [skip ci] until the final Stage 3 code push, which must omit
it. Do not modify workflows or separately dispatch CI.

This bounded increment adds scrying_glass_statblock_state.py and four tests in
test_statblock_state.py. Helpers reject the reserved key in ordinary input,
validate separately supplied snapshots against normalized monster identities,
and recursively project private keys out of copied payloads. Invalid falsey
maps are rejected rather than silently treated as empty. This does not activate
application normalization, storage, responses or transports. Adapter corrections
and production wiring remain Stage 1 work, not delivered fixes in this commit.

The four repository tests are prepared, not executed. Earlier disposable stub
experiments are not evidence that these exact tests or the real model passed.
Full model/storage/service/privacy and covering CI validation remain pending.

## Adapter correction increment - 2026-11-15

The helper increment was pushed as 34d9d417246ebff4c3481056d425ef2bbd54f6a7.
This next bounded increment replaces post-save revision patching on rebuilt
monster rows with a direct, validated typed-row reattachment under the existing
transaction. Unchanged content retains the original metadata; changed content
advances the encounter-local revision once. Supplied stale revisions are rejected
before plain tracker writes. It adds six regression methods for rebuilt metadata,
changed rebuilds, stale writes, encounter isolation, tracker-only edits and rollback.
AST parsing passed for both proposed Python files; the tests have not executed.

Correction to earlier conversation: the real model digest explicitly excludes
revision, prepared_at and content_digest. Revision-only patching did not itself
corrupt that digest. Separate setup/runtime encounters are an integration
responsibility, not evidence that this explicitly encounter-scoped adapter
queries the wrong owner. No production wiring is activated here.
Stage 1 service/storage/privacy integration and covering CI remain pending.
