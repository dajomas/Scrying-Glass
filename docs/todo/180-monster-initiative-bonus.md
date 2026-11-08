# 180. Monster initiative bonus

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-018
- Status: completed and closed, 2026-11-08, at the user's explicit request after the remaining-work review.
- Branch: features/perplexity-018. No merge or other-branch write is included.
- Priority/history: 018 preceded 009.5 in the [agreed sequence](115-admin-delivery-sequence.md); closure does not start the next task. No owner/deadline assigned.
- Related: [initiative navigation](130-initiative-keyboard-navigation.md), [source selection](160-source-based-monster-selection.md), [Open5e](170-open5e-monster-source.md). 016/017 remain separate tasks.
- Evidence and limitations: [close-out](../handover/340-combined-monster-lookup.md#sg-todo-018-close-out---2026-11-08); [correction reconciliation](185-monster-correction-plan.md).

## Agreed initiative contract

Monsters have separate signed bonuses, set manually or from available selected source data and correctable at creation/.monster import. Missing defaults to 0 without blocking rolls; distinguish default from explicit zero internally. Reject malformed input; do not infer from Dexterity or invent source evidence. Characters retain announced final totals with no bonus UI or additional calculation.

Roster bonus is read-only between HP/Max HP and editable raw roll; calculated total is separate and orders turns. Existing-monster bonus editing belongs in Edit, not inline; reviewed source refresh is another replacement path. Each raw entry replaces the prior raw roll and adds bonus exactly once. Bonus edits with retained raw immediately recalculate total/order. Reload neither rerolls nor compounds. Unset raw means unset calculated total except retained legacy.

Old stored totals stay unchanged when defaulting bonus 0; never invent old rolls. Distinguish legacy total from unset raw input. Bonus change/refresh without raw preserves a legacy total; the next manual/automatic raw roll establishes calculation. Persist bonus/origin, raw and total semantics across reload/setup reuse. Shared initiative is one d20 raw roll plus individual selected bonuses, so totals/order may differ. Retain ties and keyboard navigation. Reordering preserves turn owner, round and unrelated state without advancing turns. No new gameplay roll bounds, dice roller, total override or fallback order is agreed. Historical final-total compatibility must not double-add bonuses.

Examples: 16+12=28; replace raw 10 gives 22; enter 16 again/reload gives 28; bonus edit 10 gives 26; raw 16 with -2/0 gives 14/16; shared 16 with 12/3/-2 gives 28/19/14. Adult Blue Dragon +12 is a user illustration, not verified provider/edition data.

## Agreed selected-monster refresh

Bulk Refresh from source is disabled without selection and operates only on originally selected monsters. Use retained exact source identity without silent edition/candidate substitution; otherwise resolve through candidate lookup. Exactly one usable signed candidate resolves automatically, multiple require selection, zero remain unresolved. Invalid retained identity cannot trigger substitution. Preserve other rows' choices.

One desktop review grid with equivalent narrow cards shows source/status and current-to-proposed initiative bonus, AC, Max HP and Current HP. Each available field has its own checkbox; missing/invalid/failed fields are disabled and cannot overwrite assigned data. Missing refreshed bonus cannot replace an assigned bonus with 0. Apply only checked fields for originally selected monsters. Current HP starts unchecked. Show HP dice formulas; generate one value per monster only on HP Apply, never review. HP/Max HP are independent; selecting both uses one value. Review and checkbox/header actions mutate no live state. Bonus refresh recalculates only with retained raw, otherwise preserves legacy.

Column headers select all enabled cells in their column, row headers their row. Fully selected headers clear; partial headers select remaining enabled cells. Preserve individual selection, skip disabled cells, expose unchecked/partial/checked state and keyboard/narrow equivalents. Explicit row/Current HP header action may select HP. Apply remains required; use one review rather than a one-monster-at-a-time wizard. Server-owned authenticated review retains scope/lifetime, stale/deleted/changed/replay guards and atomic health/statistics reconciliation.

## Delivered history and evidence

The old foundation-only backlog is superseded, not a list of missing features. Delivered implementation/test families cover import/manual creation, Edit bonus, read-only roster bonus, raw-roll composition/rules/handler/UI, order/shared rolls, signed provider provenance and secured Refresh review/apply. See [330](../handover/330-monster-initiative-foundations.md) and [340](../handover/340-combined-monster-lookup.md).

The complete earlier increment record, original acceptance checklist, commit identifiers and failed/passing evidence remain available in the [immutable pre-close-out record](https://github.com/dajomas/Scrying-Glass/blob/17932b9b5ac1f02ccdc4cb53e39277fb589e6d96/docs/todo/180-monster-initiative-bonus.md). This consolidation replaces obsolete current-status wording, not historical outcomes.

## Import and manual creation increments

Optional .monster initiative_bonus is strictly validated with import/default provenance; supplied origin cannot spoof a provider. Manual Add Monster distinguishes blank/default 0 from explicit/manual 0, validates before side effects, preserves quantity/image/scope handling and starts without an assigned raw roll/total. The earlier local FastAPI collection limitation is historical, not an outstanding implementation stage.

## Outstanding acceptance work

None remains in the agreed task scope after the user's 2026-11-08 direction to perform the reviewed reconciliation and close out SG-TODO-018. Existing A.1/A.2/A.3 sign-offs and roster visual acceptance are retained. Overall user acceptance is not a claim that every checklist item was separately manually executed or that a new live-server/provider/process-restart audit occurred. Fixture limitations remain in the linked close-out record. No additional code, test or workflow change is required by this close-out; merging is separate.
