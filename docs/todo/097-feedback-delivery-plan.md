# 097 - SG-TODO-009.7 feedback delivery plan

[Back to TODO index](../../TODO.md)

## Current status - 2026-11-12

Stage 1 is completed and closed for the agreed campaign/setup/transfer/background
scope. On 2026-11-12 at 19:45 CET the user explicitly requested: "Accept and close
Stage 1 now, finish documentation and push to github". This accepts the whole
Stage 1 scope, including Step 2 (2A-2E) and Step 3; do not ask for their acceptance
again. [530 close-out, evidence and limits](../handover/530-setup-operation-feedback.md#stage-1-accepted-close-out---2026-11-12).

Stages 1-4 and accepted 4A.1-4A.13 scopes are closed. Both whole feedback
deliverables, 009.7 and overall 009 remain open. No new scope, owner, deadline,
priority, delivery-order change or acceptance gate is introduced. Earlier dated
pending/preparation statements are superseded for closed scopes, not reopened work.

Stage 3 local-feature/lair/selected-campaign viewer feedback is completed and closed
following explicit user acceptance on 2026-11-12 at 20:48 CET. Implementation
 d17b5885baea02821224d811dffc070d6a7d33a4 is covered by successful Branch tests
43291659600 attempt 1, job 131439168185; evidence publication
 db2daf8a473ebf77ff1626a8709a6a745e45b0b7, directory ci-results-43291659600-attempt-1.
Reviewed run/job metadata match the branch, implementation SHA, attempt and success;
all configured validation stages succeeded. No individual re-review of every test
log/screenshot or new manual/live-server/accessibility evidence is claimed. Scope,
accepted boundaries and limits: [540 close-out](../handover/540-local-feature-feedback.md#stage-3-accepted-close-out---2026-11-12).
Earlier Stage 3 archive/publication/CI/acceptance-pending wording is superseded;
do not request acceptance again. Cancelled run 43284682854 on a5aebc34 remains
historical and is not covering evidence. This documentation-only close-out uses
[skip ci], runs no tests and changes/dispatches no workflow.

## Deliverable 2 implementation - 2026-11-12

Implemented for the agreed Deliverable 2 scope (policy items 5-8) and delivered as
archive SG-TODO-009.7-D2.zip on 52061a68 at the user's request "Now that stage 4 is
closed, please implement Deliverable 2 and provide an archive". Publication, covering
CI and acceptance are pending; no commit SHA, run or acceptance is claimed.
[560 scope, design, tests and limits](../handover/560-connection-field-feedback.md).

- Persistent, deduplicated background-poll connection warning: one page-lane global
  `connection.poll` identity with explicit `warning` severity; identical failures add
  no notice/announcement; a successful refresh resolves only that identity.
- Near-field validation: explicit `field` selectors on validation/Join tickets mark the
  control `aria-invalid`, describe it with an adjacent non-live hint and clear on
  dismissal/resolution/replacement/scope change, re-associating after re-renders.
- Existing initiative/server gates, endpoints, payloads, combat, permissions, drafts and
  selections are unchanged; eight fragments under 20,000 bytes; inventory 44.

Ordering note: Deliverable 2 was implemented before the whole Deliverable 1
integrated evidence review at the user's request; that review/acceptance remains
open and is not satisfied by Deliverable 2. Acceptance criteria for Deliverable 2:
reviewed covering CI on the published implementation and explicit user acceptance.

## Stage 4 accepted close-out - 2026-11-12

Completed and closed for the agreed integration/accessibility hardening and approved
compatibility-retirement scope. On 2026-11-12 at 21:49 CET the user explicitly
requested "Accept and close stage 4, update documentation and push with skip ci".
Implementation 535af6f350fdcb0a473d4d43133e0d8ac7c0b50e has successful covering
Branch tests 43302214845 attempt 1, job 131476065294; evidence publication
3bfa218c1ecd0b93c3a7278f88dd811ea4380540 under ci-results-43302214845-attempt-1.
Run/job metadata match branch features/perplexity-009.7, tested SHA, attempt and
completed/success; all configured validation stages succeeded. Review did not
individually re-review every test log/screenshot or recount tests. No new human
visual, authenticated live-server, screen-reader or exhaustive accessibility
verification is inferred. [550 scope, history and limits](../handover/550-integration-accessibility-hardening.md#stage-4-accepted-close-out---2026-11-12).

Earlier Stage 4 archive/publication/CI/acceptance-pending notes are superseded;
no Stage 4 action or further acceptance request remains. This closes Stage 4 only,
not either whole deliverable or 009.7/009. It changes documentation only, uses
[skip ci], runs no new tests and changes/dispatches no workflow.

## Stage 1 accepted close-out - 2026-11-12

- Step 1 campaign create/edit/switch/delete was accepted and recorded closed at
  7eecdc7adc5873c671e70389feed30333cc37002; its covering run 43237771405 attempt 1
  tested 4f0127b56550cacb821ae2c62cb2057265eaea2a.
- Step 2 (2A-2E) publication: 3adf212646aa8956ca6a42870c23075d5c482c9b; successful
  CI 43272584707 attempt 1; evidence 1a6e562474fe3fb82d2a9f37b6d5493a70d2307c.
- Final Step 3/integrated Stage 1 revision: cc0b67b177772e314b608817f6f51cecc322a065;
  successful Branch tests 43279736032 attempt 1, job 131397505642; evidence
  publication 97eedc6da52abcfa94526fee25a3c321f0626844, directory
  ci-results-43279736032-attempt-1. Run/job metadata match the implementation SHA
  and all configured validation stages succeeded.
- Review covered run/job outcomes, not individual re-review of every test log or
  screenshot. Preparation fixtures, hosted CI and user acceptance remain distinct.
  No new authenticated live-server, human visual, screen-reader or exhaustive
  accessibility verification is inferred. This documentation-only close-out runs no
  tests, uses [skip ci] and modifies/dispatches no workflow.

## Stage 1 Step 2 setup-operation delivery split - 2026-11-12

All five stable IDs below are completed and accepted within Stage 1. The original
five-delivery plan was superseded for delivery packaging only at the user's request:
2A-2E were published together in one cumulative archive. This was not five new
requirements or acceptance gates. Step 3 copy/move and background controls is also
accepted and closed; no Stage 1 implementation/validation/acceptance action remains.

| ID | Accepted scope |
|---|---|
| SG-TODO-009.7-S1-2A | Create and save a new empty setup; existing name/duplicate validation, confirmation, selection/opening and refresh behavior. |
| SG-TODO-009.7-S1-2B | Save the current setup; existing name/save/overwrite/list/state behavior. |
| SG-TODO-009.7-S1-2C | Load/switch via the effective setup-switch.js owner for dropdown/Load; already-loaded no-op, no confirmation, request-failure selection restoration and busy behavior. |
| SG-TODO-009.7-S1-2D | Rename; existing prompt cancel/blank/unchanged no-ops and correct loaded/selected-name updates. |
| SG-TODO-009.7-S1-2E | Delete; existing confirmation and server-selected replacement/default-setup behavior. |

Detailed endpoints, payloads, operation identities, guards, byte identities,
negative controls, local/CI counts and archive instructions remain in the
[pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/todo/097-feedback-delivery-plan.md)
and [530 history](../handover/530-setup-operation-feedback.md). This concise current
record supersedes pending notes without deleting the historical evidence.

The Stage 4 implementation was originally delivered in archive SG-TODO-009.7-S4.zip
on 93be54ac. The user's request "Stage 3 is closed, now please implement Stage 4 and
provide an archive" authorized the compatibility retirement reserved for Stage 4.
Publication, covering CI and bounded acceptance are now complete as recorded above.

## Remaining scope and gates

Stages 1-4 are closed for their agreed scopes. No Stage 4 implementation,
publication, covering-CI or acceptance action remains. The existing remaining
sequence is:

1. Deliverable 1 integrated evidence review, documentation and bounded acceptance.
2. Deliverable 2: persistent connection-loss/recovery feedback, background-polling
   deduplication and validation associated with its affected field/combatant.
   Implemented in archive SG-TODO-009.7-D2.zip (see above); publication, covering CI
   and acceptance pending.
3. Final integrated evidence/corrections, documentation reconciliation and user
   acceptance of 009.7, then overall 009 close-out.

These are the existing agreed areas, not new requirements. Preserve all original
criteria, 009.6 safeguards and limits from the
[preserved full plan](https://github.com/dajomas/Scrying-Glass/blob/9d05e129cc2b85099cf0e3bf394a1fe398d0af24/docs/todo/097-feedback-delivery-plan.md)
and numbered handovers. SG-TODO-019, source-selection/Open5e and unrelated backlog
items are not prerequisites; test-suite cleanup stays deferred until after 009.
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

Completed and closed for its accepted bounded scope. Detailed behavior, all
implementation/correction/run/publication identities, evidence counts and limits
remain in [440](../handover/440-battle-action-global-feedback.md#4a11-bounded-close-out---2026-11-10)
and the [pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/todo/097-feedback-delivery-plan.md#4a11-battle-action-global-notices---2026-11-10).

## 4A.12 Join reporting - 2026-11-11

Completed and closed for its accepted bounded scope, preserving global reporting
and server gates. Detailed identities/evidence/limits remain in
[450](../handover/450-join-reporting.md#4a12-bounded-close-out---2026-11-11)
and the [pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/todo/097-feedback-delivery-plan.md#4a12-join-reporting---2026-11-11).

## 4A.13 global reconciliation - 2026-11-11

Completed and closed for its accepted bounded scope. Global compatibility was
retired at that checkpoint; subsequent pane/local migration and compatibility
retirement are now completed and accepted within Stages 1-4. Deliverable 2 remains
separate. [470](../handover/470-global-feedback-close-out.md#4a13-bounded-close-out---2026-11-11)
and the [pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/todo/097-feedback-delivery-plan.md#4a13-global-reconciliation---2026-11-11)
preserve full implementations, failures/corrections, runs, counts and limitations.

## 4A.13 browser fixture correction - 2026-11-11

Historical failure/correction superseded by the green covering run and accepted
4A.13 close-out; [467 history](../handover/467-bundle-import-feedback.md#retirement-ci-failure-and-browser-fixture-correction---2026-11-11)
and the [pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/todo/097-feedback-delivery-plan.md#4a13-browser-fixture-correction---2026-11-11).

## 4A.13 Node assertion correction - 2026-11-11

Historical failure/correction superseded by the green covering run and accepted
4A.13 close-out; [467 history](../handover/467-bundle-import-feedback.md#browser-ci-verified-and-node-assertion-correction---2026-11-11)
and the [pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/docs/todo/097-feedback-delivery-plan.md#4a13-node-assertion-correction---2026-11-11).

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

These retained anchors and headings preserve incoming links. They do not reopen
closed units; their full history is permanently linked above.
