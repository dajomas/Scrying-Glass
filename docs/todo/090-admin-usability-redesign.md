# 090 - Admin usability and visual redesign

[Back to TODO index](../../TODO.md)

## SG-TODO-009 - Professional, task-focused Admin interface

- Status: completed and closed for the agreed scope, 2026-11-12 at 22:58 CET, following final user acceptance of Deliverable 1, 009.7 and overall 009. SG-TODO-009.1-009.7 and coordinated SG-TODO-012 are closed. No further agreed 009 work remains.
- Requested: 2026-11-06; incremental redesign with staged deliveries and task-specific agreements. 009.6 renewed sign-off: 2026-11-09; final 009.7/009 acceptance: 2026-11-12.
- Priority: incremental usability improvement; no priority relative to unrelated work agreed. Owner/deadline not assigned.
- Scope: Admin presentation, navigation and interaction clarity; preserve encounter rules, API semantics, permissions and persistence unless an explicitly reviewed task requires a change.

[570 final integrated evidence, acceptance and limits](../handover/570-final-0097-close-out.md)
supersedes the old inspection/scoping and final-review-pending notes. Full prior
phase details, all implementation/correction/run/publication identities, manual-check
boundaries and history remain in the [pre-final-close-out parent checklist](https://github.com/dajomas/Scrying-Glass/blob/2eb3b4d8a35b8a97761c1479f1ef68275652a01d/docs/todo/090-admin-usability-redesign.md)
and the numbered phase handovers. Original earlier history also remains in the
[pre-009.5 plan](https://github.com/dajomas/Scrying-Glass/blob/cfc7b0f16f929041bc6107dd1f895d24492261c5/docs/todo/090-admin-usability-redesign.md)
and [pre-009.6 task](https://github.com/dajomas/Scrying-Glass/blob/a7c7614f23acb7a502c3e8c48f579faacfe1fc12/docs/todo/090-admin-usability-redesign.md).
No historical failure is relabelled and no accepted earlier scope is reopened.

## Compatibility and processing order

Preserve accepted dark/gold identity, fixed context/actions/feedback, original
forms/drafts/files/selections, full-width rosters, local scrolling and source
assembly/size constraints. Closed 005 initial collapse is retained where not
explicitly superseded by 009.6. Independent Campaign/Preparation panels and the
on-demand tools dialog replace the earlier parent-dependent/inline tools behavior;
lair eligibility remains independent. Closed 007 row controls and 008 failure-marker
boundaries remain. Permissions, persistence and combat/initiative rules are unchanged.

| Order | Subtask | Status | Dependencies |
|---|---|---|---|
| 1 | SG-TODO-009.1 | Shared foundations - closed | Baseline inspection |
| 2 | SG-TODO-009.2 | Header/action hierarchy - closed | 009.1 |
| 3 | SG-TODO-009.3 | Panels/forms - closed | 009.1/009.2 |
| 4 | SG-TODO-009.4 | Rosters/bulk actions - closed | 009.3 |
| 5 | SG-TODO-009.5 | Workflow navigation - closed | Agreed navigation/initiative baseline |
| 6 | SG-TODO-009.6 | Full-width workspace, dialog and independent controls - closed 2026-11-09 | Closed 009.5/015 baseline |
| 7 | SG-TODO-009.7 | Both feedback deliverables and final usability hardening - closed 2026-11-12 | Closed 009.1-009.6 |

The [agreed sequence](115-admin-delivery-sequence.md) remains 018, 009.5, 015,
009.6, 009.7, coordinated 016/017. 018, 009.5, 015, 009.6 and 009.7 are now closed.
016/017 remain proposed, not prerequisites inside 009 and not started by this
close-out. Deferred test-suite cleanup and SG-TODO-019 stay separate. No new
owner/deadline or delivery order.

### SG-TODO-009.1 - Shared visual foundations

Accepted/closed 2026-11-06. [260](../handover/260-admin-visual-foundations.md)
and the pre-final parent record retain token/surface/focus behavior, exact
implementation/correction identities and evidence limits.

### SG-TODO-009.2 - Header and action hierarchy

Accepted/closed 2026-11-06. [270](../handover/270-admin-header-hierarchy.md)
retains fixed context/actions/feedback, More, Next emphasis, End/Reset distinction
and implementation/correction/acceptance evidence.

### SG-TODO-009.3 - Consistent panels and forms

Accepted/closed 2026-11-06. [280](../handover/280-admin-panel-forms.md)
retains original-node grouping, labels, disclosures, values, validation, IDs and
handlers, with full delivery/evidence history.

### SG-TODO-009.4 - Scannable rosters and contextual bulk actions

Accepted/closed 2026-11-06 with coordinated 012. [310](../handover/310-admin-rosters.md)
retains read-only roster HP/Edit-dialog editing, counts/Clear selection, contextual
availability and local scrolling. Search/filter, row expansion and replacement
menus were excluded, not unfinished requirements. Exact deliveries and evidence
remain in 310 and the pre-final parent record.

### SG-TODO-009.5 - Workflow-based navigation

Accepted/closed 2026-11-09. [095 contract](095-admin-workflow-navigation.md)
and [350](../handover/350-admin-workflow-navigation.md) retain context/drafts/files/
selections and lair gating, all run/publication identities and the accepted-copy
coverage limitation. Later 009.6 explicitly superseded inline tools and parent-
dependent controls without reopening this phase. Earlier successful CI and the
later accepted copy are not falsely presented as one identical tested revision.

### SG-TODO-009.6 - Focused live encounter workspace

Accepted/closed 2026-11-09 on corrective CI and renewed sign-off, superseding the
earlier revocation of Admin-page verification. [370 close-out](../handover/370-live-encounter-workspace.md#sg-todo-0096-close-out---2026-11-09)
retains full implementation, failed/corrected CI, acceptance and manual-scenario
limits. Accepted layout: full-width Battle/Characters/Monsters/Activity; on-demand
tools dialog using original nodes/drafts/files, closed by default, no auto-opening;
independent Campaign/Preparation panels and separate lair eligibility; successful
Start/restart collapses native panes, failed Start preserves them, refresh/Next keeps
manual reopening. Native End/Reset, Battle Actions/Next, 015 summaries, roster
scrolling, permissions and assembly guards remain. No human scenario is newly
claimed executed by this final close-out.

### SG-TODO-009.7 - Feedback and final usability hardening

Completed and closed for both deliverables and agreed final scope after the user's
2026-11-12 22:58 CET request "Proceed with final acceptance and close out".
[097](097-feedback-delivery-plan.md) retains the approved policy/execution criteria;
[570](../handover/570-final-0097-close-out.md) records final criterion/evidence mapping,
code identity, limits and whole-Deliverable-1/phase/parent acceptance.

Accepted scope includes persistent actionable errors and matching resolution,
five-second global/three-second pane successes, explicit operation/target/scope
identity and stale/timer isolation; campaign/setup/roster/local/lair/viewer producer
migration; compatibility retirement; connection/recovery and polling deduplication;
field/combatant association; targeted destructive confirmations and responsive/
keyboard/focus/dialog/announcement hardening. Existing server/Join/initiative gates,
API payloads, authorization, combat rules and original drafts/context remain.

Final integrated implementation 8da0657325818c69fc82dc1234995a5146e88ebc has green
Branch tests 43310602854 attempt 1, publication dbb78d3057a2d38527bd612b948a6566a1a741e3.
The review confirms main Python 1,583 tests OK, pytest 43 passes, successful configured
JS/standalone stages and selected logged integration/browser results. Matching
runtime/test/workflow identities through 2eb3b4d8a35b8a97761c1479f1ef68275652a01d
justify reusing that covering run for this documentation-only closure. No new run
or exhaustive individual log/screenshot review is claimed. Overall acceptance is
bounded, not proof of unperformed live-server/manual/screen-reader verification.

## Documentation transition and validation limits

This final close-out changes human-readable documentation only, with [skip ci].
No application, tests, assets, pins, templates, dependencies or workflows change;
no fresh tests or separate dispatch. Earlier 009.7 inspection/scoping preparation
is historical and superseded; no agreed 009 implementation/acceptance action
remains. Evidence limits remain explicit under 570. This closes overall 009,
not unrelated tasks, merges, deployments or future external writes. The sequencing
record 115 was reviewed and left unchanged as a dated agreement/rationale; the
current task/index status above supersedes historical in-progress wording.
