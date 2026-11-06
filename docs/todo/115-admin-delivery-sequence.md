# 115 - Agreed Admin delivery sequence

[Back to TODO index](../../TODO.md)

## Decision and scope

Status: original delivery sequence agreed by the user, 2026-11-06. The user accepted the mixed sequencing recommendation and requested storing it in TODO documentation. This is a planning decision, not a new task ID, implementation delivery or acceptance of unspecified design details. A later proposal extending the schedule to tasks 014-017 is recorded below at the user's request; it remains explicitly distinguished from the original agreement and does not change implementation statuses.

This section supplements the staged [SG-TODO-009 Admin redesign](090-admin-usability-redesign.md). The original agreement records where tasks 011-013 fit around the remaining redesign stages. It does not change the relative order of 009.4 through 009.7, their existing compatibility gates, or task-specific acceptance criteria. The agreement establishes delivery order, not an assertion that every step has a technical dependency on every preceding step. No priority relative to unrelated backlog work, owner or deadline is assigned.

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

Preferred coherent increments in the original agreement are: (1) 011 with its own tests and acceptance; (2) 009.4 plus 012; (3) 013 in the same coherent increment if manageable or immediately afterwards; then (4) 009.5, 009.6 and 009.7 in their existing order. Keep task IDs and acceptance evidence distinct even when implementation shares a commit. Each external write still requires its own complete bound confirmation, and each implementation increment includes appropriate tests and documentation.

At original recording, 009.1-009.3 were closed and overall SG-TODO-009 was in progress; stages 009.4-009.7 and tasks 011-013 remained proposed. That was a historical snapshot, not an override of later task updates. SG-TODO-011 has subsequently been completed after corrective validation and user acceptance; see its task and handover for evidence. The original sequence record itself did not start or complete implementation.

The original change updated TODO documentation only. README.md and HANDOVER.md were reviewed and remained accurate without changes; their runtime descriptions and handover index links were unaffected. No application, test or workflow code changed and no new tests were executed. The documentation-only commit included [skip ci]; no separate workflow dispatch or unverified workflow outcome was claimed.

## Proposed revised open-work sequence - 2026-11-06

Status: proposal recorded at the user's request after reassessment of the open backlog with 011 completed and 014-017 added. This records the assistant's recommendation; recording it is not approval of unspecified implementation decisions, new technical dependencies or changed task statuses. The original agreed core and all compatibility/acceptance gates above are retained. The existing 014-017 task documents state that they did not change the earlier agreed sequence when first added; this section records the subsequent reassessment, not a retroactive change to those additions.

| Proposed order | Work | Rationale and boundary |
|---|---|---|
| 1 | [SG-TODO-014 - Add Monsters source help text](140-monster-source-help-text.md) | Small separate correction making explanatory text match existing D&D Beyond-first/5e.tools no-match fallback behaviour. Do not change lookup behaviour or promise fallback after provider errors. |
| 2 | SG-TODO-009.4 with [SG-TODO-012](120-character-hp-editors.md) | Keep roster numeric presentation and character Current/Max HP editor consistency together to avoid redoing the same cells. Retain separate task acceptance evidence. |
| 3 | [SG-TODO-013 - Initiative keyboard navigation](130-initiative-keyboard-navigation.md) | Decide first/last and cross-panel behaviour at the start of 009.4; implement against the resulting roster, in the same coherent increment if manageable or immediately afterwards, before 009.5. |
| 4 | SG-TODO-009.5 - Workflow-based navigation | Proceed once roster presentation and keyboard behaviour are settled. Preserve the explicitly agreed visibility mapping. |
| 5 | [SG-TODO-015 - Battle Actions combatant statistics](150-battle-actions-combatant-statistics.md) | Add read-only available AC/current HP/HP MAX below target and Reaction source selectors before 009.6 so the live-workspace review uses the fuller combat workflow. Preserve missing-versus-zero handling and action resolution. |
| 6 | SG-TODO-009.6 - Focused live encounter workspace | Build and review against the roster improvements and Battle Actions summaries. |
| 7 | SG-TODO-009.7 - Feedback, responsive and accessibility hardening | Consolidate the redesign, not postpone basic checks required during each earlier increment. |
| 8 | Coordinated [SG-TODO-016 - Source-based selection](160-source-based-monster-selection.md) / [SG-TODO-017 - Open5e API source](170-open5e-monster-source.md) workstream | Keep feature implementation after 009.7 rather than block redesign on unverified catalog/API assumptions. Start this workstream with joint feasibility/design assessment; its exact delivery order depends on the findings. |

### Source-integration workstream: investigate before fixing delivery order

1. Assess 016's complete source-catalog enumeration requirements and 017's current API requirements together. D&D Beyond/5e.tools catalog completeness and Open5e API capabilities are not established by this planning note. Verify pagination, filtering, access limits, attribution/licensing, missing fields and image availability before making capability claims.
2. Agree the common representation of provider, source/document and monster identity, and what selecting a monster populates or overwrites in identity/statistics/image fields. Preserve selected-image continuity, upload precedence and stale-response protection.
3. Implement 017's provider integration first where it establishes the data contract needed by 016. Agree configuration/default enablement and its position, if any, in automatic fallback; do not infer these from the request to add a source.
4. Implement 016's selectors against verified capabilities. Its default None/manual workflow must remain usable. If a provider cannot supply all requested monsters through an acceptable mechanism, document the blocker and obtain agreement before narrowing scope or presenting an incomplete list as complete.
5. Recheck source help text, image previews, responsive layout and keyboard behaviour after integration. Finishing 009.7 does not exempt later features from their own hardening and regression acceptance.

This is not a claim that Open5e is technically required for existing-provider selectors. If investigation supports an independent coherent 016 increment, it can ship separately. A bounded early feasibility assessment may be performed before redesign completion only if the user elects that option; the proposal does not automatically insert research as a blocker before 014 or 009.4.

### Recording and delivery limits

The proposed additions are 014 before the existing core, 015 between 009.5 and 009.6, and coordinated 016/017 implementation after 009.7. The original core remains 009.4 with 012, then 013, then 009.5, 009.6 and 009.7. No task is started or completed by this proposal. No owner, deadline or priority relative to unrelated work is assigned; no accepted row-control design, initiative boundary behaviour, provider ordering or permission is silently replaced.

This revision changes only TODO.md and this existing sequencing document. README.md and HANDOVER.md were reviewed and remain accurate without edits because runtime behaviour and handover links do not change. Task documents retain their individual scopes and acceptance criteria, with this indexed section supplying the proposed cross-task schedule. No application, tests, dependencies or workflows change and no new tests are executed. The documentation-only commit includes [skip ci]; no separate workflow dispatch or unobserved workflow result is claimed.
