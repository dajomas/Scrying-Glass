# 097 - SG-TODO-009.7 feedback delivery plan

[Back to TODO index](../../TODO.md)

## Current status - 2026-11-11

009.7 and both deliverables remain open. 4A.1-4A.12 are closed for accepted scopes.
All original policy, seven-step criteria, implementation/run/publication and
acceptance identities, 009.6 safeguards and history remain authoritative in the
[preserved full plan](https://github.com/dajomas/Scrying-Glass/blob/9d05e129cc2b85099cf0e3bf394a1fe398d0af24/docs/todo/097-feedback-delivery-plan.md)
and numbered handovers. 4A.12 is closed after reviewed covering evidence and the
user's bounded close-out request. 4A.13 is in progress; wider gates stay open.
Priority, owner, deadline, SG-TODO-019 and delivery order are unchanged.
No unrelated unfinished task is closed.

## 4A.11 battle-action global notices - 2026-11-10

Completed and closed for the accepted bounded scope. On 2026-11-10, following
successful covering CI and detailed evidence reconciliation, the user explicitly
accepted 4A.11 with the stated evidence limits and requested close-out/push.
This is feature-scope acceptance, not a claim that unperformed manual checks ran.

Delivered scope: actor-specific eligibility errors/matching resolution;
independent active/living target errors/matching resolution; actor-specific
no-pending information; start-of-turn completion success with encounter-ticket,
actor and modal-session guards. Preserve modal-local feedback, payloads,
busy/duplicate safeguards, applied history and explicit retry; no automatic replay.

Implementation/evidence identities:
- Initial checkpoint: 00f065913d1068e4ed13df904cead507573f24eb.
- Core follow-up: 272cfd73aa4c39602ed2dad96c1bd2e02ba28348.
- Start-of-turn follow-up: 6e4bdd54f73df70bdb263493bf010ef3f0e9a0ad.
- Selection fixture repair: 886056da5f03beb750f2f620b2f02f26e73150f3.
- Attack-statistics fixture repair/final tested revision:
  1b621c3909e751affc356fbbb98acc53a3f588e3.
- Successful covering run: 42896405201 attempt 1, job 130110564256.
- Evidence publication: 477583dc63a6f88d7161bef913a27ca7a931f374.

Reconciled detailed evidence: eligibility 16 passes, core 6 passes, combined
follow-up 16 passes (overlapping core coverage, not unique requirement counts);
legacy Apply, selection, attack-statistics, reaction and turn-helper files pass;
full assembly/identity/reader/isolation, pins/tamper guard/runtime adapter and
relevant feedback/loading/rendering/workspace browser regressions pass.
Run/job metadata match the tested SHA and success. Runs 42891311319 and
42894039107 remain historical failures; both fixture corrections are verified by
the final covering run. [Detailed evidence, history and limits](../handover/440-battle-action-global-feedback.md#4a11-bounded-close-out---2026-11-10).
Earlier task snapshots remain in the [pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/477583dc63a6f88d7161bef913a27ca7a931f374/docs/todo/097-feedback-delivery-plan.md).

No new authenticated live-server exercise, human visual/manual combat workflow,
screen-reader test or exhaustive accessibility acceptance is inferred. The user
accepted the bounded unit on the stated evidence; wider validation gates remain
explicit and open rather than falsely recorded as passed. Its documentation-only
close-out used [skip ci], with no application/test/pin/workflow change or new
validation run/dispatch. README and TODO root remain accurate and unchanged.
4A.12 close-out follows below; 4A.13 reconciliation is tracked separately below
under preserved criteria; compatibility retires only after relevant callers migrate.
Neither feedback deliverable nor 009.7 closes. No merge/deployment or blanket
future write approval.

## 4A.12 Join reporting - 2026-11-11

Completed and closed for the accepted bounded scope. Delivered implementation:
981ffe61a9bb4da162944707b42132d384eea1ad. Successful covering Branch tests
42949763708 attempt 1, job 130291065704, matches that SHA. Evidence publication:
488997aacb50ed44d785c9738457fab1b854ad90. Detailed reconciliation supports the
user's 2026-11-11 request to reconcile, close and push; acceptance is limited to
Join reporting, not whole-deliverable or phase acceptance.

Accepted behavior: one global roster.join rejection across fetch/core single and
bulk paths; matching-success resolution, independent target/error preservation,
stale-result suppression; existing client/server gates, payloads, bulk success
wording and non-Join behavior retained, with no automatic mutation replay.
Near-field validation remains Deliverable 2, not an expansion of this unit.

Direct CI log review confirms new core/gate suite 26 passes and retained gate
suite 12 passes, zero failures/cancellations/skips in both; all 10 server initiative
gate tests passed. Relevant browser Join persistence/retry/stale-scope, rendering/
keyboard/narrow-layout and complete source/reader/runner/adapter checks passed.
[Detailed evidence matrix and limits](../handover/450-join-reporting.md#4a12-bounded-close-out---2026-11-11).
Preparation's syntax, 38 focused passes and four detected negative controls remain
separate historical evidence; covering CI supplies actual repository execution.
[Pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/488997aacb50ed44d785c9738457fab1b854ad90/docs/todo/097-feedback-delivery-plan.md)
preserves the then-pending status and criteria.

No new authenticated live-server, human visual/manual workflow, screen-reader or
exhaustive accessibility acceptance is claimed. Focused controller-adapter/mocked
checks and browser/server fixtures are not universal end-to-end coverage of every
Join path. Its documentation-only close-out used [skip ci], executed no new tests
and changed/dispatched no workflow; it did not infer a new run outcome. README
and TODO root remain accurate and unchanged. 4A.13, both feedback deliverables and
009.7 remain open under preserved criteria. No merge/deployment or future blanket
write approval.

## 4A.13 global reconciliation - 2026-11-11

Status: in progress, audit/regression checkpoint; not completed or accepted.
Baseline f68e40872e8f3657f6d203f372565c01531f4a68. This change set adds two test
guards and indexed handover/task updates, without runtime migration or global/pane
compatibility retirement. The core literal guard checks eight known calls and
replacement-source/template contracts, not a complete effective caller inventory.

Executed: Node syntax, real-controller/bootstrap suite 8 passes, zero failures/
skips, four detected negative controls and restored suite pass. The 136-pair
matrix covers 17 selected API operation identities; it is not 136 handler or
requirement acceptances. Actual End/Reset composition is one additional case.
Python guard compilation passed; its three full-repository-dependent tests have
not run locally. [460 preparation and limits](../handover/460-global-feedback-reconciliation.md).

Remaining: deliver the exact approved checkpoint with normal CI and review its
covering results; finish all loaded/injected/global/direct-writer caller mapping,
classify local/alert and later pane/Deliverable 2 dependencies, extend actual-handler
composition/combined coverage and migrate any remaining applicable global paths.
Retire global compatibility only when inventory and tests justify it; retain pane
compatibility until its migrations finish. The current global-compatibility test
is a deliberate baseline, not a permanent retirement veto. Complete evidence,
necessary corrections and explicit bounded acceptance are required before closure.
No prior green run covers these new tests; no new SHA or CI pass is invented.
4A.1-4A.12 remain closed; both deliverables and phase 009.7 stay open. No scope,
owner/deadline/priority/order change, workflow dispatch, merge or deployment.

## Closed-unit anchors

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

## Remaining scope and gates

Deliverable 2 connection/recovery persistence, polling deduplication and field/
combatant association remain unimplemented. Wider 009.7 destructive confirmations,
responsive/zoom/labels/contrast/focus/tab/menu/live announcements, nested tools and
independent panels retain all preserved-plan acceptance criteria. Accepted 009.6
workspace, tools/drafts/files, Start/failed-Start/refresh/Next reopening, lair/viewer/
roster, permission and combat safeguards remain mandatory. Both deliverables and
phase stay open. No blanket write approval or new commitment. Full histories and
criteria are cross-linked, not silently removed.
