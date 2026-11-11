# 097 - SG-TODO-009.7 feedback delivery plan

[Back to TODO index](../../TODO.md)

## Current status - 2026-11-11

009.7 and both deliverables remain open. 4A.1-4A.11 are closed for accepted scopes.
All original policy, seven-step criteria, implementation/run/publication and
acceptance identities, 009.6 safeguards and history remain authoritative in the
[preserved full plan](https://github.com/dajomas/Scrying-Glass/blob/9d05e129cc2b85099cf0e3bf394a1fe398d0af24/docs/todo/097-feedback-delivery-plan.md)
and numbered handovers. 4A.12 is in progress, awaiting covering CI and acceptance.
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
4A.12 preparation follows below; 4A.13 reconciliation remains proposed under
preserved criteria; compatibility retires only after the respective callers migrate.
Neither feedback deliverable nor 009.7 closes. No merge/deployment or blanket
future write approval.

## 4A.12 Join reporting - 2026-11-11

Status: in progress. This change set supplies Join-only reporting integration and
regressions; delivery identity, covering CI review and explicit bounded acceptance
are not invented or treated as completed by preparation. Baseline e633ca34d7dd651594470f7f6e64a3f9a3742da9.

One global roster.join rejection across the fetch gate and core single/bulk Join
paths, matching-success resolution, independent target/error preservation and
stale-result suppression. Retain client/server initiative gates, payloads, bulk
success wording, non-Join behavior and no automatic mutation replay. Near-field
validation remains Deliverable 2, not an expansion of this unit.

Preparation: runtime syntax passed; new 26-case suite and retained 12-case gate
suite passed, restored combined run 38/38, zero failures/skips; four negative
controls detected. These are prior focused production-controller/scoped-adapter
and copied-core-function results with mock DOM/transport, not full-Admin/bootstrap,
browser, authenticated live-server or accessibility acceptance. The legacy fixture
adds lifecycle accommodation without changing original behavioral assertions.
[Implementation, evidence and limits](../handover/450-join-reporting.md).

Acceptance remaining: exact approved delivery, normal covering CI for the actual
implementation SHA, review both Join suites plus relevant server/browser/full-source
regressions, correction review as needed, and explicit bounded acceptance. Earlier
4A.11 success does not cover 4A.12. No workflow edit/dispatch or skip marker in
this mixed implementation commit. 4A.13 and all wider gates remain open.

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
