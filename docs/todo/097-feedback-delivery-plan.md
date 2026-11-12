# 097 - SG-TODO-009.7 feedback delivery plan

[Back to TODO index](../../TODO.md)

## Current status - 2026-11-12

Stages 1-4, accepted 4A.1-4A.13 units and Deliverable 2 are completed and closed
for their agreed scopes. Whole Deliverable 1 integrated evidence review/acceptance
and final integrated 009.7/009 evidence, documentation and user acceptance remain
open. No new scope, owner, deadline, priority, order or acceptance gate is introduced.
Earlier dated pending/preparation notes are superseded for these closed scopes,
not reopened work. Do not request their acceptance again.

Stage 1 user acceptance: 2026-11-12 at 19:45 CET; Step 1 was recorded closed at
7eecdc7adc5873c671e70389feed30333cc37002, and whole-stage close-out at
37ea8c99b8c0e4133b4462e7f5b970694a313d2e. [530 evidence/limits](../handover/530-setup-operation-feedback.md#stage-1-accepted-close-out---2026-11-12).
Stage 2 remains closed on its separately accepted green local evidence, not a new
hosted-CI claim. [510 close-out](../handover/510-bulk-join-pane-feedback.md#stage-2-bounded-close-out---2026-11-12).
Stage 3 user acceptance: 2026-11-12 at 20:48 CET; tested
 d17b5885baea02821224d811dffc070d6a7d33a4, green run 43291659600 attempt 1,
publication db2daf8a473ebf77ff1626a8709a6a745e45b0b7, close-out
93be54ace5a9efb45265668a56d54f7f053817cd. [540 evidence/limits](../handover/540-local-feature-feedback.md#stage-3-accepted-close-out---2026-11-12).
Cancelled run 43284682854 on a5aebc34 remains historical, not covering evidence or
an outstanding failure. Current bounded acceptance does not invent unperformed
manual, authenticated live-server, screen-reader or exhaustive accessibility checks.

## Deliverable 2 accepted close-out - 2026-11-12

The user explicitly requested "Accept and close Deliverable 2" on 2026-11-12 at
22:43 CET following the green covering-CI review. Completed and closed for the
agreed Admin persistent connection/recovery warning, polling deduplication and
near-field field/combatant association scope, with the limits in
[560 close-out](../handover/560-connection-field-feedback.md#deliverable-2-accepted-close-out---2026-11-12).

Implementation 8da0657325818c69fc82dc1234995a5146e88ebc on
features/perplexity-009.7 has successful Branch tests 43310602854 attempt 1,
job 131505374358; publication dbb78d3057a2d38527bd612b948a6566a1a741e3, directory
ci-results-43310602854-attempt-1. Reviewed run.json and jobs.json agree on branch,
tested SHA, attempt and completed/success. All configured Chromium provisioning,
syntax/import, main Python/browser, pytest, JavaScript and standalone browser/audit
stages succeeded. Review did not individually re-review every test log/screenshot
or recount tests. No new manual/live-server/screen-reader/exhaustive accessibility
evidence is claimed. Earlier archive/publication/CI/acceptance-pending notes are
superseded; no further Deliverable 2 acceptance request remains.

This documentation-only close-out uses [skip ci], runs no new tests and changes/
dispatches no workflow. It closes Deliverable 2 only, not whole Deliverable 1 or
009.7/009. No merge, deployment or blanket future write approval.

## Deliverable 2 implementation - 2026-11-12

Originally delivered in SG-TODO-009.7-D2.zip on 52061a68; now published, covered
by green CI and accepted as above. Policy items 5-8:

- One persistent page-lane global `connection.poll`/`server` warning; repeated
  identical failures add no record/announcement; matching recovery resolves only it.
- Explicit `field` selectors associate validation/Join feedback with the affected
  control, using aria-invalid, a preserved aria-describedby and an adjacent non-live
  hint; cleanup on dismissal/resolution/replacement/scope change and re-association
  after re-render.
- Existing initiative/server gates, API/payloads, combat, permissions, drafts and
  selections retained; eight fragments below 20,000 bytes; script inventory 44.

[560](../handover/560-connection-field-feedback.md) retains full design, test names,
asset versions and limits. The user requested Deliverable 2 before the whole
Deliverable 1 integrated review; that review/acceptance remains open and is not
satisfied by Deliverable 2 implementation or acceptance.

## Stage 4 accepted close-out - 2026-11-12

Accepted 2026-11-12 at 21:49 CET for agreed integration/accessibility hardening and
approved compatibility retirement. Tested 535af6f350fdcb0a473d4d43133e0d8ac7c0b50e;
green Branch tests 43302214845 attempt 1, job 131476065294; publication
3bfa218c1ecd0b93c3a7278f88dd811ea4380540; close-out
52061a68312a80af7182335db71f851b57536bb4. [550 scope/history/evidence limits](../handover/550-integration-accessibility-hardening.md#stage-4-accepted-close-out---2026-11-12).
Original archive SG-TODO-009.7-S4.zip and earlier compatibility-retirement approval
remain historical. No Stage 4 implementation/publication/CI/acceptance action remains.

## Stage 1 accepted close-out - 2026-11-12

Step 1 was already accepted, with green run 43237771405 attempt 1 testing
4f0127b56550cacb821ae2c62cb2057265eaea2a. Step 2 publication
3adf212646aa8956ca6a42870c23075d5c482c9b has green run 43272584707 attempt 1,
evidence 1a6e562474fe3fb82d2a9f37b6d5493a70d2307c. Final Step 3/integrated
Stage 1 implementation cc0b67b177772e314b608817f6f51cecc322a065 has green run
43279736032 attempt 1, job 131397505642, publication
97eedc6da52abcfa94526fee25a3c321f0626844. Whole-stage acceptance included Steps 2/3;
[530](../handover/530-setup-operation-feedback.md#stage-1-accepted-close-out---2026-11-12)
retains all scope, publication and evidence-review limits. No new test execution
or individual re-review is claimed here.

## Stage 1 Step 2 setup-operation delivery split - 2026-11-12

Completed/accepted stable IDs: SG-TODO-009.7-S1-2A (new empty setup),
SG-TODO-009.7-S1-2B (save), SG-TODO-009.7-S1-2C (load/switch),
SG-TODO-009.7-S1-2D (rename), SG-TODO-009.7-S1-2E (delete/replacement/default).
Cumulative packaging replaced the original one-operation-per-archive order at the
user's request for that delivery only; no new requirement or acceptance gate.
Existing name/duplicate validation, confirmations/no-confirmation load, prompt
cancel/blank/unchanged no-ops, save/overwrite and server-selected replacement
behavior remain. Step 3 copy/move/background scope is also closed. Full details
remain in [530](../handover/530-setup-operation-feedback.md) and the
[pre-Deliverable-2-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/dbb78d3057a2d38527bd612b948a6566a1a741e3/docs/todo/097-feedback-delivery-plan.md).

## Remaining scope and gates

Stages 1-4 and Deliverable 2 are closed. The existing remaining sequence is:

1. Whole Deliverable 1 integrated evidence review, documentation and bounded
   acceptance. Do not reopen accepted units or infer whole-D1 acceptance from D2.
2. Final integrated evidence/corrections, documentation reconciliation and user
   acceptance of 009.7, then overall 009 close-out.

These are existing agreed areas, not new requirements. Preserve all original
criteria, 009.6 safeguards and limits from the
[preserved full plan](https://github.com/dajomas/Scrying-Glass/blob/9d05e129cc2b85099cf0e3bf394a1fe398d0af24/docs/todo/097-feedback-delivery-plan.md)
and numbered handovers. Source-selection/Open5e, SG-TODO-019 and unrelated backlog
are not prerequisites; test-suite cleanup stays deferred until after 009.
No blanket approval for future external writes, merges, deployment or dispatch.

## Approved policy and required Deliverable 1 steps

Global success 5s, pane success 3s; actionable errors persist until dismissal or
matching resolution/replacement. Explicit severity/identity/scope/order; stale
tickets/timers cannot overwrite or clear current/unrelated feedback. Preserve
API/combat/authorization and drafts/selections. Full ten-point policy retained.

1. Finish actual integration inventory, destinations, scope/retry mapping.
2. Controller/accessibility: deadlines, persistent independent errors, safe text,
   matching resolution, keyboard dismissal/focus and stale guards.
3. Actual Admin loading: asset order, bypass writers, expiry, eight UTF-8 fragments,
   size/identity/assembly/marker and UI preservation.
4. Migrate every agreed producer; validation/Join gates remain. Connection/recovery
   and field association are Deliverable 2, not silently folded into this unit.
5. Unit/full-Admin regressions: identity/timers/isolation, actual loaded handlers,
   lookup/keyboard/focus and accepted 009.6; no weakening unrelated assertions.
6. Complete code/test/doc/status payload review, truthful evidence/deferred work;
   CI-first when local checks unavailable, not a false substitution or blocker.
7. Exact nonempty write approval, exact push/real SHA, covering CI/correction
   review; mixed commits normal CI, documentation-only commits [skip ci].

Implementation archives remain the agreed workflow unless explicitly changed: the
user applies, commits and pushes; Patch is archive-only and must not be staged;
never use newzip.sh unchanged. Preserve complete required handover/TODO context,
replacement files, base/file verification and COMMIT_MESSAGE. No extra full-suite
acceptance gate per archive; focused checks and covering review follow the existing
sequence. Future code uses normal CI unless explicitly directed otherwise.

## 4A.11 battle-action global notices - 2026-11-10

Accepted/closed. Full behavior, implementation/correction/run/publication identities,
counts and limitations remain in [440](../handover/440-battle-action-global-feedback.md#4a11-bounded-close-out---2026-11-10)
and the permanently linked pre-close-out task record above.

## 4A.12 Join reporting - 2026-11-11

Accepted/closed for global reporting/server gates. Detailed identities, evidence and
limits remain in [450](../handover/450-join-reporting.md#4a12-bounded-close-out---2026-11-11)
and the pre-close-out task record. Deliverable 2 adds association without reopening it.

## 4A.13 global reconciliation - 2026-11-11

Accepted/closed. Global compatibility retirement was followed by accepted Stage 4
pane/local retirement. Deliverable 2 is separately accepted; whole Deliverable 1
remains open. [470](../handover/470-global-feedback-close-out.md#4a13-bounded-close-out---2026-11-11)
and the pre-close-out task record retain full implementations, failures/corrections,
runs, counts and limits.

## 4A.13 browser fixture correction - 2026-11-11

Historical failure/correction superseded by green covering evidence and accepted
4A.13 close-out. [467 history](../handover/467-bundle-import-feedback.md#retirement-ci-failure-and-browser-fixture-correction---2026-11-11)
and the pre-close-out task record retain the complete history.

## 4A.13 Node assertion correction - 2026-11-11

Historical failure/correction superseded by green covering evidence and accepted
4A.13 close-out. [467 history](../handover/467-bundle-import-feedback.md#browser-ci-verified-and-node-assertion-correction---2026-11-11)
and the pre-close-out task record retain the complete history.

## Closed-unit anchors

<a id="current-status---2026-11-11"></a>
<a id="4a1-implementation-checkpoint---2026-11-10"></a>
<a id="4a2-startrestart-request-feedback---2026-11-10"></a>
<a id="4a3-start-validation-feedback---2026-11-10"></a>
<a id="4a4-stage-2-shared-next-feedback---2026-11-10"></a>
<a id="4a4-next-turn-feedback---stage-1-fixture-preparation---2026-11-10"></a>
<a id="4a5-end-battle-feedback---2026-11-10"></a>
<a id="4a6-reset-all-feedback---2026-11-10"></a>
<a id="4a7-individual-combatant-reset-feedback---2026-11-10"></a>
<a id="4a8-global-removal-fallback-feedback---2026-11-10"></a>
<a id="4a9-activity-log-clear-feedback---2026-11-10"></a>
<a id="4a10-viewer-font-adjustment-feedback---2026-11-10"></a>
<a id="4a11-close-out---2026-11-10"></a>
<a id="4a12-close-out---2026-11-11"></a>

Retained headings/anchors preserve incoming links. Compacted closed-unit detail is
preserved permanently at the pre-close-out task link; no unfinished task or criterion
is removed, no historical failure is relabelled, and no accepted scope is reopened.
