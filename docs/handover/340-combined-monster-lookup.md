# 340 - Combined monster lookup activation

[Back to handover index](../../HANDOVER.md)

2026-11-08. [SG-TODO-018 correction A.2](../todo/185-monster-correction-plan.md).
Branch features/perplexity-018. All four A.2 implementation increments included;
covering commit-4 CI and A.2 manual acceptance pending. A.1 remains accepted.
No overall close-out, merge or write-back is authorized.

## Runtime and compatibility

Candidate lookup queries both enabled providers, even when D&D Beyond succeeds.
Configured books are enumerated; missing mappings, malformed data, fetch failures
and limits block all candidates/signing. Unconfigured entry sources are excluded.
Versions keep separate statistics and source-bound selection/bonus offers. Exact
retained Refresh identities are not silently replaced. Keys/defaults stay intact;
fivetools_fallback independently enables 5e.tools candidates while legacy stats/
image fallback behavior is unchanged. No permissions/schema/account changes.

Commit 4 replaces fallback-only Admin help and clarifies config comments without
changing values. Existing overwrite/image labels and both creation/import form
blocks are byte-identical. README no longer advertises an interim wording mismatch.
No Admin JavaScript/bundle/marker or selection/Apply behavior changes. A.3's sole-
candidate Refresh auto-resolution and stage B remain excluded.

## Evidence and limits

Activation 5414f1359808fdc07c75b94b1ca3ffe15c078d70 had failed CI 42503436253 attempt 1:
1,391 main/repeated executions with the same two stale locked-page assertions.
That run remains failed. Test correction e2d06aac12dabbdc7d4febe7be1efc3b3a2b2b29 has
verified successful run 42504619218 attempt 1; publication
ce44afba0e12cd4b46125e735e935753ccb41be0 / ci-results-42504619218-attempt-1.
Every listed job/cleanup step succeeded for that exact tested SHA, not commit 4.
Detailed earlier records remain in the
[pre-finalization snapshot](https://github.com/dajomas/Scrying-Glass/blob/ce44afba0e12cd4b46125e735e935753ccb41be0/docs/handover/340-combined-monster-lookup.md).

Two static help/config tests passed in commit-4 preparation. Original template/
help-test/config blobs were verified; both form blocks and all non-comment YAML
lines are unchanged. Both test modules parse/compile and remain below 20,000 bytes.
The full-Admin intercepted-HTTP browser fixture retains 1440/375 widths, labels,
IDs, no-page-error and no-mutation checks; it was not executed locally.
Four new secured ASGI/real-SQLite methods retain production parsing/signing/creation/
Refresh paths with mocked synthetic provider transport, HP generation and pre-
seeded sessions. They cover both chosen sources/reopen, either-provider failure
without signing/mutation, explicit Refresh choice/apply with raw16+7=23 and unchanged
HP/unselected state, retained identity, and disabled providers/empty sources.
These methods were prepared, not executed locally: FastAPI is absent. No framework
stand-in or browser-to-server, password login, TCP, live-provider or OS-restart proof.
Existing CI discovers both modules normally; new covering results/manual workflow
acceptance remain pending. Historical data is linked rather than discarded.

## Remaining gate

Review commit-4 CI, fix any failures, then obtain deployed desktop/narrow acceptance
for both provider versions, chosen-source persistence/Refresh and fail-closed
lookup without partial offers. Only then reconcile A.2 status. No A.3, stage B,
SG-TODO-018 completion or merge is inferred from this delivery.
