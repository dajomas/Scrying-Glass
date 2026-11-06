# 115 - Agreed Admin delivery sequence

[Back to TODO index](../../TODO.md)

## Decision and scope

Status: delivery sequence agreed by the user, 2026-11-06. The user accepted the mixed sequencing recommendation and requested storing it in TODO documentation. This is a planning decision, not a new task ID, implementation delivery or acceptance of unspecified design details.

This section supplements the staged [SG-TODO-009 Admin redesign](090-admin-usability-redesign.md). It records where tasks 011-013 fit around the remaining redesign stages. It does not change the relative order of 009.4 through 009.7, their existing compatibility gates, or task-specific acceptance criteria. The agreement establishes delivery order, not an assertion that every step has a technical dependency on every preceding step. No priority relative to unrelated backlog work, owner or deadline is assigned.

## Agreed sequence

| Order | Work | Delivery intent |
|---|---|---|
| 1 | [SG-TODO-011 - Add Monsters image previews](110-monster-image-previews.md) | Deliver and validate image previews as a separate follow-up to the accepted 009.3 forms, before continuing with 009.4. |
| 2 | SG-TODO-009.4 - Scannable rosters, incorporating [SG-TODO-012 - Character HP editor consistency](120-character-hp-editors.md) | Design the roster presentation and character Current/Max HP editors together. Retain 012 as a separately tracked task with its own acceptance criteria. |
| 3 | [SG-TODO-013 - Initiative keyboard navigation](130-initiative-keyboard-navigation.md), within the 009.4 work | Settle navigation boundaries at the start of 009.4, then implement and test traversal against the resulting roster structure. Include it in the coherent 009.4 increment if manageable, or deliver it in an immediately following commit before 009.5. |
| 4 | SG-TODO-009.5 - Workflow-based navigation | Continue after the roster/editor/navigation increments. Preserve the agreed visibility and compatibility gates. |
| 5 | SG-TODO-009.6 - Focused live encounter workspace | Continue after 009.5, preserving existing combat workflows. |
| 6 | SG-TODO-009.7 - Feedback and final usability hardening | Consolidate responsive, keyboard and accessibility checks against the complete feature set, retaining regression coverage for 011-013. |

Do not postpone all of 011, 012 and 013 until after 009.7. Do not implement 012 as an isolated preliminary styling patch only to redesign the same HP cells again during 009.4. For 013, agree the intended traversal behaviour early but implement it against the resulting roster rather than an intermediate layout.

## Rationale and implementation gates

- 011 complements the Add Monsters fields and .monster disclosure accepted in 009.3 and is largely separate from roster restructuring. Inspect when provider images become available to the browser; provider previews must not be assumed to have the same implementation complexity as local-file previews. Preserve upload precedence, selected-image continuity and in-flight edit protection.
- 012 belongs with aligned numeric presentation and editing in 009.4. Preserve Current/Max HP editing, validation and persistence; do not change HP calculation, damage or healing semantics.
- 013 depends on a clear roster interaction design. First/last-field behaviour and whether traversal crosses panel boundaries remain unresolved and must be explicitly agreed before implementation. Cover forward/reverse focus movement, save-triggered rerenders and access to other controls without a keyboard trap.
- The accepted single-line monster-row controls under SG-TODO-007 are not authorised for replacement by this sequencing agreement. Any alternative action-menu design still requires explicit agreement under 009.4.
- Responsive and accessibility checks apply to each increment. The final 009.7 consolidation is not permission to defer basic usability until then.

## Delivery and acceptance

Preferred coherent increments are: (1) 011 with its own tests and acceptance; (2) 009.4 plus 012; (3) 013 in the same coherent increment if manageable or immediately afterwards; then (4) 009.5, 009.6 and 009.7 in their existing order. Keep task IDs and acceptance evidence distinct even when implementation shares a commit. Each external write still requires its own complete bound confirmation, and each implementation increment includes appropriate tests and documentation.

At recording, 009.1-009.3 are closed and overall SG-TODO-009 is in progress. Stages 009.4-009.7 and tasks 011-013 remain proposed, not started or completed by this document. Later implementation deliveries must update their respective task statuses and evidence.

This change updates TODO documentation only. README.md and HANDOVER.md were reviewed and remain accurate without changes; their runtime descriptions and handover index links are unaffected. The existing redesign plan and task documents retain their scope and acceptance criteria, with this indexed section supplying the agreed cross-task schedule. No application, test or workflow code is changed and no new tests are executed. The documentation-only commit includes [skip ci]; no separate workflow dispatch or unverified workflow outcome is claimed.
