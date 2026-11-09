# 095 - Admin workflow navigation

[Back to TODO index](../../TODO.md)

## SG-TODO-009.5

- Status: in progress, user acceptance pending. Navigation corrections through 7df8cbe have successful covering CI; form refinement 8262863cc0a226e02b040eafb6827fb96af736a4 is delivered with validation not established by the earlier run. The subsequent agreed overwrite change is prepared, not pushed or validated.
- Agreement: 2026-11-09, compact workflow navigation and subsequent Add Monsters UI refinements. No owner/deadline assigned. Branch: features/perplexity, retaining the merged 018 baseline.
- Evidence/history: [350 handover](../handover/350-admin-workflow-navigation.md). Successful run 42594146455 attempt 1 covers 7df8cbe only; failed historical runs stay failed. No closure or new CI outcome is inferred.

## Scope

Campaign: selection/access/backups, Add character and Characters. Preparation: setups/background/imports, Add monsters, both rosters and gated lair. Live: existing rosters, tools, lair and log. Header/actions/context/feedback and Battle/order/Danger zone remain shared. Preserve initial/manual/dependent/battle collapse, lair/tools restoration, drafts/files, source/bonus/total rules and keyboard operation. No automatic tab switching, persistent view preference, roster filtering or 009.6 workspace is introduced.

8262863 delivers bonus-help removal, Combat statistics placement between HP Range end and Quantity, and species-blur filling of a currently blank name without replacing existing names. [Immutable prior task detail](https://github.com/dajomas/Scrying-Glass/blob/8262863cc0a226e02b040eafb6827fb96af736a4/docs/todo/095-admin-workflow-navigation.md) preserves earlier requests/history and acceptance requirements.

## Agreed overwrite follow-up

- Loaded checkbox label: Overwrite AC, HP range and initiative bonus with source values. Missing initiative bonus defaults to 0.
- With overwrite enabled, available bonuses replace existing values; explicitly missing/null bonuses clear the field to the existing default-zero path, without source-bonus attribution. Keep candidate identity, and distinguish default zero from explicit source zero.
- With overwrite disabled, retain existing bonuses; available bonuses may fill blanks. Invalid/ambiguous/malformed data, failed/empty/cancelled/stale lookup and intervening edits must not clear or overwrite the bonus.
- Retain edit/revert and chooser/HTTP revision guards. Do not change bulk Refresh's missing-field preservation or explicit Apply, backend/schema/provider calculations, completed 018 scope or delivered field/name behavior.
- Prepared tests: provider/checkbox/value fallback matrix, missing prior-offer removal, failure/no-match preservation, invalid protection, missing/available chooser and delayed edit/revert, actual loaded label and absent help at desktop/narrow widths.

Changed-block JavaScript syntax and missing-matrix-snippet Python AST parsing passed during preparation. Complete final-module/browser/full-suite execution and covering CI remain pending. Normal CI and exact-content approval apply; do not claim earlier green CI covers these application edits.

## Remaining acceptance

Deliver this follow-up, review covering CI and any remaining failures, and obtain desktop/narrow visual/workflow acceptance including overwrite/default-zero, candidate/manual creation, form order/name default, draft/file retention, keyboard/focus, context/battle/lair/tools restoration and modal/initiative continuation. No live provider/login/process-restart or exhaustive accessibility audit is claimed by static/intercepted checks. Overall 009 stays in progress; 009.6/009.7 remain proposed.
