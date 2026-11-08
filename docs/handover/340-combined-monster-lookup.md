# 340 - Combined monster lookup activation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-08. [SG-TODO-018 correction plan](../todo/185-monster-correction-plan.md). Status: completed and closed at the user's explicit request after review of remaining actions. Branch features/perplexity-018; no merge or other-branch write. Detailed historical records, preparation checks, original anchors and failed/passing evidence are preserved in the [immutable pre-close-out record](https://github.com/dajomas/Scrying-Glass/blob/17932b9b5ac1f02ccdc4cb53e39277fb589e6d96/docs/handover/340-combined-monster-lookup.md).

## Runtime and compatibility

Combined candidate lookup queries enabled D&D Beyond and configured 5e.tools books. Versions retain separate statistics and signed identities. Missing mappings, malformed data, failed fetches and incomplete book searches block candidates/signing, not partial selectable results. Unconfigured books are excluded. Exact retained Refresh identities are never silently replaced. fivetools_fallback independently enables candidate search; legacy stats/image fallback remains unchanged. No account/permission/schema change.

## Evidence and limits

Backend activation 5414f1359808fdc07c75b94b1ca3ffe15c078d70 had failed run 42503436253; correction e2d06aac12dabbdc7d4febe7be1efc3b3a2b2b29 has successful 42504619218 attempt 1, publication ce44afba0e12cd4b46125e735e935753ccb41be0. Earlier failed results remain failed. Help/config wording was aligned without changing configuration values or creation/import form contracts. Original static/local/CI evidence remains archived.

## Remaining gate

No agreed SG-TODO-018 acceptance gate remains after the explicit overall close-out direction recorded below. This is not authorization to merge or a claim that unexecuted live audits occurred.

## Commit 5 initiative overwrite follow-up - 2026-11-08

7c760064aaa3484974362fb423f89245e4eb55fa removed only the separate bonus confirmation. Candidate choice/cancel and Refresh Apply remain. Available bonus fills blanks or replaces populated values under the AC/HP overwrite option; intervening edits, including edit/revert, are preserved. Missing/invalid bonuses never overwrite; signed offers retain exact selected identity and clear on later edits/reset/selection changes. Covering 42514703672 attempt 1 succeeded; publication 8c7ce113ee00548ac3126744dd98a6c25d2a3579. Earlier deployed checklists are not a new manual execution log.

## A.3 sole-candidate Refresh - 2026-11-08

Implementation c62d203d3b92aa277eb7e34f4c90da789ab0e58b resolves one usable signed candidate automatically, multiple through explicit choice, zero unresolved. Failed exact-source/identity/token checks do not substitute candidates. Continuation preserves other rows and field choices. No fields auto-check, live statistics mutate or HP rolls occur before explicit Apply. Authentication/scope/revision/configuration/expiry/single-use/transaction guards remain.

## A.3 first covering CI and fixture correction - 2026-11-08

42516636403 attempt 1 failed because a chooser fixture supplied one candidate. Correction 1c289d485bffcf8197fb32238349729e52b822ed supplies two and adds assembled Chromium/secured-ASGI/SQLite sole-candidate review/Apply coverage at 1440/375. Historical failure is not relabelled.

## Corrective CI and A.2/A.3 acceptance - 2026-11-08

42517614512 attempt 1 succeeded for exact 1c289d485bffcf8197fb32238349729e52b822ed; publication 73183fd70d6111083b2ca0048c6a029c0c04fed8. The user manually tested and signed off A.2/A.3 on 2026-11-08. A.1 acceptance remains in [335](335-fivetools-initiative-correction.md).

## Stage B roster presentation - 2026-11-08

Initial 11f104058efb2a56365b0309ce8c6ee829d84c18 removes visible Roll/legacy text, retains raw accessible labels and Total output, maps standing to alive only for display, and uses fixed AC/HP/Init captions with boolean-state PATCH handling and aria-pressed. Colour-only controls supersede initial minus/check decorations. Selection, other actions and underlying initiative/life rules remain unchanged.

## Stage B CI failure and colour-only/single-line follow-up - 2026-11-08

42520146312 attempt 1 remains failed for waiting on rejection feedback in a collapsed pane. The fixture opens that pane through normal UI before asserting feedback/unchanged state; production notification placement is unchanged and can still be hidden when its pane is closed. Colour-only/single-line correction 1d4815d8f0e89840687ba13136ce88b3b631b9f3 and spacing 9cfcbb26106fa95c5e28f58cba45e7234b47220f have successful covering 42522294918 attempt 1. Later alignment/corrected wrapping geometry is recorded in [310](310-admin-rosters.md).

## SG-TODO-018 close-out - 2026-11-08

Final correction: f5808a2dfbc9b8d8bd4de9706956dbe8312815a5. Branch tests 42526295799 attempt 1 completed successfully on features/perplexity-018. Evidence publication 790a32b0f86eb60a86319d7c3158f9a7c22f489b, ci-results-42526295799-attempt-1. The corrected test_primary_centres_and_compact_status_after_refresh explicitly reports OK. Failed alignment run 42525208958 remains failed. Evidence-publication/documentation SHAs are not the tested implementation SHA.

The user confirmed the roster visual check successful and, after review identified documentation reconciliation, remaining workflow acceptance and overall closure as the three actions, explicitly requested all three actions to close out SG-TODO-018. This direction is recorded as overall acceptance of the agreed scope, alongside prior A.1/A.2/A.3 sign-offs, not as a fabricated checklist-by-checklist manual run. No new defect or unmet implementation item was identified by that review.

Reconciled coverage: stage-B fixtures check labels, stored/display life-state distinction, retained raw/legacy Total semantics, repeated refresh/read-only behaviour, short/long-name status geometry, colour/glyph states, keyboard fixed-toggle exact PATCHes and rejection preservation. Other existing test families retain selection/bulk/Edit/statistics, ordering/ties/turn/round, bonus provenance and Refresh review/apply checks. The reviewed assembled Refresh fixture forwards browser requests into secured ASGI and real SQLite, checking selective Apply, unchanged other rows, HP once only on Apply, order/round/turn preservation, storage reopen, stale review and health-conflict rejection.

Limitations remain: stage-B HTTP is intercepted; Refresh sessions are seeded, provider transport and HP operations mocked, and database reopen is not a new OS process. No new password-login, TCP/live-server, live-provider, exhaustive accessibility or process-restart audit was executed during close-out. Visual acceptance is user-reported. These limitations are disclosed, not silently converted into passing manual tests or a new implementation backlog. Historical fixture failures remain failed in the linked immutable records.

This seven-file documentation-only close-out reconciles task/plan, relevant handovers and root indexes. README and existing maintenance guidance remain accurate and unchanged. No code/test/runtime/dependency/workflow change, new test execution, workflow dispatch, merge or other-branch write. Commit message: docs: close SG-TODO-018 after CI and user acceptance [skip ci].
