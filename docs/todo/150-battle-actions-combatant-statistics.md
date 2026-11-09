# 150. Battle Actions combatant statistics

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-015
- Status: in progress; live selector/row implementation inspection started, 2026-11-09, after the user's 009.5 sign-off and explicit request to move to the next scheduled item. Application/test implementation and validation remain outstanding.
- Recorded: 2026-11-06; commencement updated 2026-11-09.
- Priority: next in the [agreed Admin delivery sequence](115-admin-delivery-sequence.md), after closed 018/009.5 and before 009.6. No owner/deadline assigned.
- Dependencies: preserve accepted navigation/initiative/row-control work; no backend/schema change established.

## Requested change

In the Battle Actions modal, when a target is selected, show its available AC, current HP and HP MAX immediately below the target dropdown. Show the same information immediately below the Reaction source dropdown for its selected combatant. These are read-only summaries, not extra editors.

## Acceptance criteria

- Both selected target and Reaction source show available AC, HP and HP MAX below their own dropdowns.
- Update on selection changes and clear when no combatant is selected; never retain a previous combatant's values.
- Preserve missing versus zero: do not invent absent data or display it as zero; valid zero HP/statistics remain visible.
- Do not mutate combatant statistics or alter eligibility, action/reaction resolution, Apply locking, modal drafts, Next from Battle Actions, permissions or persistence.
- Keep dynamic ordinary/reaction/statistics-reduction rows consistent where they use target selectors; inspect actual loaded enhancements before choosing integration points.

## Inspection commenced - 2026-11-09

Read live static/admin/060-source.js. activeBattleTargets uses active monsters/characters, sorted by name. addBattleActionRow creates data-action-target for ordinary/reaction rows and data-action-source only for reactions, with explicit empty selected placeholders. addStatisticsReductionRow separately creates a data-action-target selector for eligible living targets. Row removal, action amount/critical controls and battleActionsApplying guards already exist and must stay intact.

Continue inspecting actual latest-state/statistics contracts, modal template/styles, load/rerender and application/Node/browser tests, source-size/assembly constraints and loaded enhancement order. Establish reliable summary updates/clearing across selection changes, Apply refresh, row creation/removal, scope changes and modal reopen without submitting actions or overwriting drafts. Initial inspection is not an implementation delivery or validation result.

## Validation and delivery requirements

Prepare targeted regressions for both selectors, initial/changed/cleared selection, partial/absent data, zero HP, characters/monsters, independent multiple rows, refresh and desktop/narrow placement/readability. Retain existing combat/modal/Apply/Next tests. Browser/intercepted fixtures are not authenticated live-server evidence. Review covering CI and obtain task-specific visual/workflow acceptance before closure.

The present transition updates documentation only and executes no tests; it includes [skip ci], modifies no workflow and makes no dispatch. The later coherent application/test/documentation delivery must use normal CI unless explicitly instructed otherwise and requires its own complete bound write approval. See [009.5 close-out and transition](../handover/350-admin-workflow-navigation.md#next-scheduled-item-and-documentation-only-transition).
