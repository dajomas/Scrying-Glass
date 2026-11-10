# 380 - Feedback delivery plan and continuity

[Back to handover index](../../HANDOVER.md)

## 4A.1 implementation checkpoint - 2026-11-10

Prepared for this commit on features/perplexity-009.7: state-load migration in static/admin/030-source.js and static/admin-feedback-admin.js, plus tests/admin-state-load-feedback.test.cjs. The [4A.1 task status](../todo/097-feedback-delivery-plan.md#4a1-implementation-checkpoint---2026-11-10) keeps the unit, deliverable and phase open pending covering validation. No merge or deployment-ready claim is made.

The existing request-start sequence is retained, with an encounter epoch rejecting responses whose original scope changed. load() verifies accepted sequence/epoch before assigning latest or rendering. Persistent errors use the explicit state.load identity; matching successful rendering silently resolves only that operation. A legitimate accepted scope transition rebinds its original ticket. The no-battle early return and strict load(true) original-error rethrowing remain intact, including stale failures whose notices are suppressed. Current malformed scope data produces an actionable reload error instead of rendering or silently resolving an error.

Executed during preparation: two JavaScript syntax checks; 15 passing Node VM regressions using the real controller/bootstrap and production request/load slices; and four detected temporary negative controls for error expiry, unrelated clearing, old-scope acceptance and broken rethrowing. Reconstructed unchanged 030, bootstrap and controller contents matched their live Git blob identities before modification. Modified 030-source.js is 19,565 UTF-8 bytes; the bootstrap is 6,630 bytes. Eight-part source order and the tracked admin.js failure marker are unchanged.

Evidence limits: mocked network/DOM slices, not a complete checkout, full-Admin browser, authenticated/live-server or assistive-technology verification. The local request function was reconstructed from the verified prior read; no complete local 010-file identity is claimed. Existing bundle-identity/legacy-fixture reconciliation, final combined regressions and covering CI review remain pending. Historical preparation results are not a new test run for this approval. The existing JavaScript CI discovery includes the new test. No commit SHA, workflow result or acceptance is invented before evidence exists.

Background uploads, character editing, Start/restart and other producers remain outside 4A.1; Deliverable 2 is unchanged. README and root TODO/HANDOVER were reviewed against unchanged live identities and remain accurate without unrelated edits. This mixed commit uses normal CI without [skip ci]. The older documentation-only and checkpoint-2 skip notes below are historical, not instructions to skip this implementation commit.

## Current status - 2026-11-09

SG-TODO-009.7 and Deliverable 1 remain in progress/open. The [seven-step plan and ten-point policy](../todo/097-feedback-delivery-plan.md) remain authoritative. The user explicitly approved two work-in-progress checkpoints on features/perplexity-009.7 before continuing step 4. This is not a complete integrated feedback delivery or phase acceptance. The accepted [009.6 baseline](370-live-encounter-workspace.md#sg-todo-0096-close-out---2026-11-09) must remain intact.

The original planning record and detailed checkpoint-1 preparation history remain in [this section at checkpoint 1](https://github.com/dajomas/Scrying-Glass/blob/51e3e3bfcc8e56176b8bcc2559e74bee46e5f493/docs/handover/380-feedback-delivery-plan.md). Live instructions were read before preparation; previously complete reads were reused against verified commit/file identities, not assumed temporary execution files.

## User-approved checkpoint 1 of 2 - 2026-11-09

Committed as 51e3e3bfcc8e56176b8bcc2559e74bee46e5f493 on features/perplexity-009.7. It saves the controller, view, CSS, 25-test Node suite and 14-test isolated Chromium suite, plus status documents. Its workflow change adds this branch to Branch tests while preserving existing branch targets and test steps. No [skip ci] marker was included. A covering CI run has not been checked; no workflow completion or success is claimed.

Historical local preparation: both JavaScript syntax checks, 25 Node tests, 14 Chromium component tests and Python AST parsing passed. Four temporary negative controls detected error expiry, unrelated clearing, stale-attempt acceptance and unsafe HTML rendering. These are not full-Admin, screen-reader or authenticated-server verification.

## User-requested checkpoint 2 of 2 - 2026-11-09

Committed as 8ba97701a76328909b9570a8bfbf523e80abf4f6 on features/perplexity-009.7 with [skip ci]. This checkpoint saves the prepared Admin bootstrap, header asset order, first core fragment, lookup/Join-gate routing, guarded obsolete timeout asset and loading fixture. It intentionally activates incomplete wiring on the topic branch only. No production deployment or merge is requested. The tracked admin.js failure marker, eight-part reader/order, permissions, server validation and combat rules are unchanged. The shared request helper observes state with request-start sequencing; older responses cannot select the feedback scope. The 030 fragment remains unchanged.

Incomplete behavior is explicit: remaining helper callers temporarily use persistent neutral info feedback, not final success/error metadata or complete stale-result protection. legacyRegions() exposes those destinations. Step 4 must eliminate production use of that route, migrate tools/lair/viewer direct writers, distinguish candidate cancellation/no-match/provider failure and reconcile duplicate Join reporting. Modal-only notices and persistent state/ownership guidance are not blanket success timers. Do not deploy this checkpoint as completed Deliverable 1.

Original step-3 preparation passed six JavaScript syntax checks and 15 real Chromium loading-slice tests; a temporary negative control detected the old timeout observer clearing managed errors. Original live-file blob identities and reconstructed component SHA-256 identities were checked. This checkpoint factors the loading fixture's repeated assertions/setup into helpers; that factored test file has not been rerun for this approval. Its prior 15-test result is historical, not a claimed result for the refactored file. Complete assembled Admin, existing suites, actual assistive-technology/live-server validation and covering CI remain pending.

The user explicitly requested [skip ci] for checkpoint 2. Its proposed/approved/actual message must contain that marker; no workflow configuration is changed or separately dispatched. No skipped-run state or test success is inferred from the marker, and no new checkpoint SHA is invented before the write. Normal CI applies again to subsequent implementation commits unless separately instructed.

README now identifies its fixed bundle hash as the accepted pre-009.7 baseline rather than the modified checkpoint. Bundle-identity assertions and legacy VM fixture contracts remain intentionally pending until the full producer migration is reconciled; do not describe the repository suite as passing. The current TODO index already records both checkpoint scopes and leaves 009.7 open, so no unrelated index change is needed.

## Continuation and remaining work

After this checkpoint is written, resume Deliverable 1 step 4 on features/perplexity-009.7 using the live source. Preserve original controls/drafts, independent panels/lairs, Start/restart collapse and failed-Start visibility, manual reopening, native roster/local scrolling and tools-dialog keyboard/focus/busy/nested behavior. Complete producer migration, full-Admin regressions, identity/fixture updates, documentation/TODO reconciliation, exact-payload review and bound approval.

Deliverable 2 remains connection failure/recovery warnings, polling deduplication, field/combatant-associated validation, scope/retry handling and combined keyboard/responsive regressions. Destructive-confirmation review and broader responsive/accessibility hardening remain open after both feedback deliverables.

## Bounded 4A planning reference - 2026-11-09

The user reported repeated interrupted attempts whose displayed output/artifacts disappeared, then requested smaller group-4A sub-tasks and asked that the suggestions be saved as documentation only. The cause of those interruptions has not been verified; do not label them a proven connector-size limit, timeout or temporary-file cleanup. Do not count disappeared output as durable implementation or validation evidence. The verified checkpoint above remains the continuation baseline.

The [13 proposed 4A execution units and per-task boundaries](../todo/097-feedback-delivery-plan.md#bounded-group-4a-sub-tasks---2026-11-09) are now recorded in the existing delivery plan, without creating new deliverables or changing the approved feedback policy. All 4A.1-4A.13 remain proposed/not completed by this update. The first bounded unit is 4A.1, state-load feedback only. Live source/effective handlers must be verified before implementation; unrelated operations sharing a file must not be pulled into the same task.

Each bounded unit should reach a reviewed result with focused executed checks and explicit dependencies before another begins. Every subsequent external write still needs complete bound approval and its relevant tests/documentation. Focused tests are not full-Admin or CI acceptance; temporary artifacts are not the sole recovery point. The normal implementation CI rule resumes after checkpoint 2's one-off skip.

This update changes only the existing task and handover documents and includes [skip ci]. Links, branch/checkpoint references and the proposed scope were reviewed. README and root TODO/HANDOVER were reviewed/reused against the verified baseline and remain accurate without edits. No automated tests were executed, no workflow was modified/dispatched and no 4A implementation or phase closure is claimed.
