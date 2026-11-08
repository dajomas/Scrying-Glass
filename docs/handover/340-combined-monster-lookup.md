# 340 - Combined monster lookup activation

[Back to handover index](../../HANDOVER.md)

2026-11-08. [SG-TODO-018 correction plan](../todo/185-monster-correction-plan.md).
Branch features/perplexity-018. All four A.2 implementation increments and commit 5
are delivered; covering commit-5 CI is verified below. A.2 manual acceptance remains
pending. A.3 implementation is delivered as c62d203d3b92aa277eb7e34f4c90da789ab0e58b;
first covering CI failed on a stale browser expectation. Fixture correction is
prepared below; corrective CI and manual acceptance remain pending. A.1 remains
accepted. No overall close-out, merge or write-back authorized.

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
No Admin JavaScript/bundle/marker or selection/Apply behavior changes in commit 4.
A.3 and stage B were excluded from that delivery.

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
Existing CI discovers both modules normally; the later commit-5 run below covers
the branch containing these tests. Manual workflow acceptance remains pending.
Historical data is linked rather than discarded.

## Remaining gate

Obtain deployed desktop/narrow acceptance for both provider versions, chosen-source
persistence/Refresh and fail-closed lookup without partial offers. Only then
reconcile A.2 status. No stage B, SG-TODO-018 completion or merge is inferred.
A.3 has its separate implementation and validation record below.

## Commit 5 initiative overwrite follow-up - 2026-11-08

Prepared before A.3: remove only the Add Monster initiative-bonus confirmation.
Keep the source/version chooser, its cancellation/focus behavior, and Refresh
review/Apply. Available bonuses fill blanks or replace existing values when the
existing AC/HP overwrite checkbox is enabled. Initiative help explains this shared
option without changing template IDs or checkbox labels. Missing/invalid bonuses
never fill or overwrite. Lookup-start value and edit-revision guards preserve edits,
including edit then revert. Bind the exact signed offer after application events;
later edits, reset, changed species/selection or a new lookup clear attribution.
Unsigned copies remain manual. Server authentication/signature checks are unchanged.
The existing AC/HP handler remains responsible for its own assignments.

Preparation validation: Node syntax passed; seven candidate, eleven source-offer
and three typing/focus Chromium methods passed (21 methods, subcases not counted
as separate methods). Tests use intercepted HTTP, opaque offer tokens and copied
production lookup/listener code in isolated fixtures. This is not full Admin/CSS,
browser-to-server, authentication, live-provider, persistence or deployed desktop/
narrow acceptance. Initial preparation exposed fixture issues: modal-inert fields
needed explicit programmatic edit events; the delayed-response test must intercept
fetch rather than the already wrapped request. Corrected fixtures passed; no
production assertion was relaxed to accept overwriting intervening bonus edits.

README was updated. Root HANDOVER/TODO indexes and workflow were reviewed and left
unchanged at commit 5: existing links and overall in-progress status remained
accurate. Normal push CI applied, without skip/workflow changes/dispatch.
Implementation SHA 7c760064aaa3484974362fb423f89245e4eb55fa has verified successful
Branch tests run 42514703672 attempt 1. Evidence was read at publication SHA
8c7ce113ee00548ac3126744dd98a6c25d2a3579 / ci-results-42514703672-attempt-1.
Run/job metadata agrees on the branch, attempt and exact tested SHA; all listed
steps including cleanup succeeded, none skipped. Main suite: 1,398 tests OK;
connection-audit repeat: 1,398 tests OK, 752 connections opened/0 without explicit
close. Repetition is not unique tests. Syntax/import, pytest, JavaScript, standalone
browser/audit and artifact-upload steps succeeded. Inspected error-labelled
tracebacks are negative-path logging followed by passing assertions, not failing
checks. No setup/collection failure is reported; individual test-level skips were
not independently enumerated across the entire log. Historical failures stay failed.
Deployed acceptance remains pending; see the [commit-5 gate](../todo/185-monster-correction-plan.md#commit-5-initiative-overwrite-follow-up---2026-11-08).

## A.3 sole-candidate Refresh - 2026-11-08

Implementation delivered as c62d203d3b92aa277eb7e34f4c90da789ab0e58b.
Identity-less Refresh rows resolve exactly one candidate through the existing
signed snapshot validation and exact-source fetch. Multiple candidates retain
explicit choice; zero remain unavailable with an unresolved status. Failed combined
lookup offers no partial candidates. Invalid retained identity is fail-closed, and
a signed choice conflicting with a retained identity is rejected. No provider, book,
edition or candidate substitution is introduced. Invalid/expired/wrong-species or
identity-less tokens cannot resolve a row. An exact-fetch failure remains failed.

Review continuation resolves only explicitly updated row IDs and preserves all
other server-held rows, including automatic and earlier explicit candidates and
proposals. Reload review starts fresh; failed rows require reload to retry lookup.
The unchanged browser retains individual selections across continuation. No fields
are auto-checked; no live statistics/image change or HP generation occurs in review.
Explicit Apply and all existing authorization, scope/revision/state/configuration,
expiry, signed identity, single-use and transactional guards remain. Add Monster
commit-5 code, Admin assets, schema and CI workflows are unchanged.

Preparation validation: four prepared Python code/test files compiled and parsed.
Framework application and browser tests were not executed locally: FastAPI and
HTTPX2 are absent. Updated source tests and new secured ASGI/SQLite plus intercepted-
Chromium tests are discovered by existing normal CI. They cover sole/multiple/zero,
identity/token safety, unaffected automatic/explicit rows, checkbox choices, no
review mutation, HP only on explicit Apply, storage reopen, replay, malformed IDs,
stale response/configuration/expiry and 1440/375 review behavior. Provider transport/
HP and browser endpoints are mocked as described in fixtures; no live-provider,
password-login, browser-to-server, new-process restart or deployed acceptance claim.
The first covering A.3 run failed as recorded below; corrective CI and manual
acceptance remain pending, not passed by delivery.
README and correction-plan status were updated together. Existing index links remain
unchanged; their A.3 pending wording is a validation/acceptance gate, not a claim
that this increment is absent. See the [A.3 gate](../todo/185-monster-correction-plan.md#a3-implementation-and-validation---2026-11-08).
Stage B, overall SG-TODO-018 close-out, merging and other-branch writes are excluded.

## A.3 first covering CI and fixture correction - 2026-11-08

Run 42516636403 attempt 1 failed on exact tested SHA
c62d203d3b92aa277eb7e34f4c90da789ab0e58b, branch features/perplexity-018.
Evidence read at publication 5c8cd561b46a8694fe3da267771927f31ff7b45c /
ci-results-42516636403-attempt-1. Run and job metadata agree. Main suite and
connection-audit repeat each ran 1,406 tests with one error: the same assembled
Chromium method test_real_candidate_resolution_keeps_other_checks_and_unchecked_hp
timed out waiting for Source candidate for Alpha. Two executions are not two
independent defects. The fixture supplied one candidate, so A.3 correctly omitted
the redundant chooser. This is a stale browser expectation, not setup/collection
failure or evidence of a production auto-resolution defect. The five new A.3
ASGI/isolated-browser methods explicitly report OK. Syntax/server import, pytest,
JavaScript, artifact upload and checkout cleanup succeeded. Node/Python post-setup
cleanup steps were skipped. Connection tracking reports 759 opened/0 without
explicit close, but the audit step remains failed because its repeated suite failed.
Subsequent standalone log/round audits and browser smoke completed; smoke reports
no page errors. No deployed/manual or live-provider acceptance was executed by CI.

Correction changes tests only: give the explicit-choice fixture two distinct
provider URLs/edition flags, assert both candidates and unchecked HP, retain
other-row checkbox and no-review-mutation assertions. Add an assembled Chromium
1440/375 sole-candidate method forwarded through the real secured ASGI/SQLite
review/apply path: no chooser, no automatic checks, no state/persistence mutation
or HP generation during review, one preview request, explicit AC Apply, exact
source identity and unchanged other row/HP. Existing stale/apply/health checks
remain. No production, Add Monster, asset, schema or workflow changes.

Correction preparation: reconstructed original test matches live blob
1b583d9dada1cb3aee7ddc85f1bf196f5d3a3e82; revised 16,382-byte module compiles
and parses. Its five methods were not executed locally: FastAPI/HTTPX2 absent.
Normal CI discovers it; no skip marker/workflow edit/dispatch. Corrective delivery
and covering results remain separate; no new SHA/run is invented. README and
root index links/overall open status need no change for this fixture correction.
All failed runs above remain failed historical evidence.
