# 097 - SG-TODO-009.7 feedback delivery plan

[Back to TODO index](../../TODO.md)

## Stage 1 Step 2 setup-operation delivery split - 2026-11-12

Status: planned, implementation not started. On 2026-11-12 the user requested
smaller deliveries for Stage 1 Step 2 and publication of this plan. The current
base is 7eecdc7adc5873c671e70389feed30333cc37002. Campaign Stage 1 Step 1 is
accepted and closed in that commit; Stage 2 and accepted 4A units stay closed.
These are setup-operation delivery labels, not Stage 2 or the seven parent
Deliverable 1 process steps. No new scope, owner, deadline or acceptance gate.

| ID | Delivery | Preserved behavior and focused boundary |
|---|---|---|
| SG-TODO-009.7-S1-2A | Create a new empty setup | Migrate existing name/duplicate validation, POST /api/setups/new feedback, selection/opening and refresh outcomes. Creation already saves the new empty setup; do not combine this with the separate Save operation. |
| SG-TODO-009.7-S1-2B | Save the current setup | Migrate POST /api/setups/save validation/request/success and subsequent list/state refresh feedback; retain existing name, save/overwrite and selection semantics. |
| SG-TODO-009.7-S1-2C | Load/switch setups | Migrate the effective static/setup-switch.js owner for both dropdown and Load button. Preserve already-loaded no-op, busy/disabled behavior, request-failure selection restoration and current effective confirmation behavior; do not revive the obsolete 050 handler's confirmation. |
| SG-TODO-009.7-S1-2D | Rename a setup | Migrate selection/prompt/request/success and refresh feedback for POST /api/setups/rename. Preserve cancel/blank/unchanged-name no-ops and correct loaded/selected-name updates. |
| SG-TODO-009.7-S1-2E | Delete a setup | Migrate selection/confirmation/DELETE/success and refresh feedback. Preserve server-selected replacement setup and creation/opening of an empty default when the last setup is deleted. |

Delivery order is 2A, 2B, 2C, 2D, 2E.

2A status (2026-11-12): implementation archive prepared on
1b54a2c4c47644c9ac0f72939043652d818cf337; not yet published, CI-covered or
accepted. 2B is next after the published 2A SHA is verified.
[2A scope, evidence and limits](../handover/530-setup-operation-feedback.md).

Original plan text: These five replace the combined
Step 2 delivery, not five new requirements. Each is one usable operation end to
end, including persistent actionable validation/request errors, explicit campaign/
setup/operation/scope identity, matching resolution, three-second pane success,
completed-mutation versus failed-refresh guidance, newer-input/selection/session/
registry and obsolete-timer/result guards, legitimate transition handling, busy
protection through refresh and disabled-state restoration. Never replay mutations.
Preserve existing endpoints/payloads/auth, confirmations, drafts/files/selections,
setup and combat behavior; add no new server rules or Deliverable 2 field validation.

Each operation includes focused Node/full-Admin regression coverage as applicable,
necessary fragment/digest/size/cache-version reconciliation and proportional task/
handover updates. Reuse existing guarded state/helper plumbing only where needed
for the current operation. No separate foundation-only delivery, unrelated cleanup,
workflow edit, ninth fragment or unapproved compatibility retirement. Preserve the
eight-fragment assembly/order, 20,000-byte code limits and tracked failure marker.
Check late handlers/overrides rather than migrating only an overridden legacy path.

Use the existing implementation-archive workflow: complete replacement files,
required README/TODO and complete handover/TODO context, archive-only Patch with
COMMIT_MESSAGE, exact change manifest/base verification and safe application notes.
The user applies, commits and pushes, then supplies the published SHA for verification
before the next archive. Never stage Patch; do not use newzip.sh unchanged. Direct
assistant writes still require their own exact-content approval if later requested.

No extra full-suite acceptance gate is imposed per archive. Focused checks accompany
each delivery; configured CI and covering correction/review follow the existing
sequence, with combined setup regressions completed with 2E. Bounded Step 2 acceptance
follows integrated evidence, not a mandatory new sign-off loop for every substep.
Future code deliveries use normal CI unless the user explicitly directs otherwise;
the old intermediate skip instruction ended with campaign Step 1. This PLAN-ONLY
commit uses [skip ci], executes no tests and does not modify/dispatch workflows.

Setup copy/move between campaigns and background controls remain separate Stage 1
work, not silently included here. Already-migrated setup/CSV imports, accepted
campaigns and Stage 2 are not reopened. General lair/viewer integration, compatibility
retirement, Deliverable 2 connection/recovery/polling/field association and deferred
test-suite cleanup stay outside this split. Completing 2A-2E does not close all of
Stage 1, either whole deliverable, 009.7 or 009. No implementation/test result is
claimed by recording this plan. Further subdivisions require reporting an actual
boundary/problem and obtaining agreement before changing this five-delivery plan.

## Current status - 2026-11-11

009.7 and both deliverables remain open. 4A.1-4A.13 are closed for accepted scopes.
All original policy, seven-step criteria, implementation/run/publication and
acceptance identities, 009.6 safeguards and history remain authoritative in the
[preserved full plan](https://github.com/dajomas/Scrying-Glass/blob/9d05e129cc2b85099cf0e3bf394a1fe398d0af24/docs/todo/097-feedback-delivery-plan.md)
and numbered handovers. 4A.12 and 4A.13 are closed after reviewed covering evidence
and bounded user close-out requests. Wider gates stay open. Priority, owner,
deadline, SG-TODO-019 and delivery order are unchanged.
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
and TODO root remain accurate and unchanged. Its close-out did not close 4A.13,
both feedback deliverables or 009.7; 4A.13 closes separately below. No merge/
deployment or future blanket write approval.

## 4A.13 global reconciliation - 2026-11-11

Completed and closed for the accepted bounded scope. Following the verified green
covering run and stated limits, the user requested 'Finish 4a.13 please' on
2026-11-11. Exact close-out approval records bounded acceptance, not whole-feedback-
deliverable or phase acceptance. [470 close-out/evidence/limits](../handover/470-global-feedback-close-out.md#4a13-bounded-close-out---2026-11-11).

Delivered: source/caller classification; statistics-open persistent targeted errors
and matching resolution; bundle-import success with complete recovery guidance;
actual full-page/late-wrapper composition coverage; global compatibility retirement
with explicit global feedback and pane compatibility retained. Preserve action
payloads, busy guards, request/refresh distinctions, drafts/selections and no replay.

Final tested revision 413822d82bc1dd5894b139946b5caf054e24f39d has successful
Branch tests 42973631914 attempt 1, job 130367559943. Evidence publication:
6c77d9fe069fffc34dd3335294e20ea90e8097f9. Matching run/job metadata and individual
results confirm all eight reconciliation cases, four full-page Chromium scenarios,
three inventory checks and corrected header-layout test passed. All main stages
succeeded; not every retained regression was individually re-reviewed. The matrix
covers 19 selected identities/171 unordered API pairs, not actual handler combinations.

Retirement e15ad2b18f308d116fab288e058b24f7842f8c98 is retained unchanged with
browser correction c76b52e4d6f29e28c1726db940d29cbd223ee2a5 and Node correction
413822d82bc1dd5894b139946b5caf054e24f39d. Failed runs 42969807025 and
42971464667 remain historical; the final covering run verifies both repairs.
[Detailed migration/composition/failure history](../handover/467-bundle-import-feedback.md).
[Pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/6c77d9fe069fffc34dd3335294e20ea90e8097f9/docs/todo/097-feedback-delivery-plan.md)
preserves the audit, migration, correction identities and then-open gates in full.

No new authenticated live-server, human visual/manual, screen-reader or exhaustive
accessibility acceptance is inferred. Full-page intercepted-HTTP fixtures do not
prove every dynamic caller or live backend. Bounded acceptance resolves this unit
on its stated evidence, not unperformed wider validation. Pane consumers and local
feature/lair/selected-campaign viewer integration remain open; D2 connection/
recovery persistence, polling deduplication and field/combatant association remain
open. The documented producer dispositions are not whole-D1 acceptance.

This close-out is documentation only with [skip ci]; no new tests, runtime/test/
pin/markup/workflow changes or workflow dispatch. It invents no new CI outcome.
README and TODO root remain unchanged. 4A.1-4A.13 stay closed for accepted scopes;
both feedback deliverables and phase 009.7 stay open. No merge/deployment, changed
owner/deadline/priority/order or future blanket write approval.

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

## 4A.13 browser fixture correction - 2026-11-11

Historical correction and failed-run details remain in the
[pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/6c77d9fe069fffc34dd3335294e20ea90e8097f9/docs/todo/097-feedback-delivery-plan.md#4a13-browser-fixture-correction---2026-11-11)
and [467](../handover/467-bundle-import-feedback.md#retirement-ci-failure-and-browser-fixture-correction---2026-11-11).
The final covering run and bounded close-out above supersede the historical blocker.

## 4A.13 Node assertion correction - 2026-11-11

Historical correction and failed-run details remain in the
[pre-close-out task record](https://github.com/dajomas/Scrying-Glass/blob/6c77d9fe069fffc34dd3335294e20ea90e8097f9/docs/todo/097-feedback-delivery-plan.md#4a13-node-assertion-correction---2026-11-11)
and [467](../handover/467-bundle-import-feedback.md#browser-ci-verified-and-node-assertion-correction---2026-11-11).
The final covering run and bounded close-out above supersede the historical blocker.
