# 095 - Admin workflow navigation

[Back to TODO index](../../TODO.md)

## SG-TODO-009.5

- Status: in progress, user acceptance pending. Navigation through 7df8cbe has successful covering CI. Form refinement 8262863cc0a226e02b040eafb6827fb96af736a4 and overwrite refinement 2ec510c487453702dd1abe352b589125df44291a are delivered; earlier green navigation CI does not cover them. The remaining concise lookup-copy change is prepared for exact approval and normal CI.
- Agreement: 2026-11-09, workflow navigation and subsequent Add Monsters UI refinements. No owner/deadline assigned. Branch: features/perplexity, retaining merged 018 baseline.
- History/evidence: [350 handover](../handover/350-admin-workflow-navigation.md). Successful 42594146455 attempt 1 covers 7df8cbe only; historical failed runs stay failed. No new validation result or closure is inferred.

## Retained scope

Campaign contains selection/access/backups, Add character and Characters. Preparation contains setups/background/imports, Add monsters, both rosters and gated lair; Live contains existing rosters, tools, lair and log. Header/context/actions/feedback and Battle/order/Danger zone remain shared. Preserve native initial/manual/dependent/battle collapse, tools/lair restoration, drafts/files, source/bonus/total rules and keyboard operation. No automatic tab switching, persistent view preference, roster filtering or 009.6 workspace.

8262863 delivers bonus-help removal, Combat statistics placement between HP Range end and Quantity, and species-blur filling of a currently blank name without overwriting existing names. 2ec510c delivers the AC/HP/bonus checkbox label and missing-source-bonus fallback to default zero when checked, preserving invalid/failure/edit guards, candidate identity and distinct explicit-zero provenance. Bulk Refresh is unchanged. [Immutable prior task detail](https://github.com/dajomas/Scrying-Glass/blob/2ec510c487453702dd1abe352b589125df44291a/docs/todo/095-admin-workflow-navigation.md) preserves full earlier requirements and preparation limits.

## Remaining copy refinement

- Replace the technical lookup explanation with one concise paragraph: enabled D&D Beyond/configured 5e.tools, prompted version choice, fail-closed search with retry/manual entry, uploaded-image precedence. No settings/internal-provider detail in operational copy.
- Keep HP-entry guidance and behavior unchanged; align raw checkbox wording with the already delivered runtime label.
- Prepared regressions cover exact source/rendered copy, 40-word ceiling, IDs, current accessible checkbox label, unchanged configuration defaults/comments and desktop/narrow no-mutation behavior.

HTML text/entity round-trip, 29-word count and changed Python source-test-snippet AST parsing passed. Complete final modules/browser/full-suite and covering CI remain pending. This mixed template/test/documentation commit runs normal CI, without [skip ci].

## Acceptance

Deliver this copy refinement and review covering CI for the current application changes. Confirm concise help, label, overwrite/default-zero, manual/source creation, field order/name default, keyboard/focus, draft/file retention, context/battle/lair/tools restoration and modal/initiative continuation. Obtain desktop/narrow visual/workflow acceptance before closure. No live provider/login/process-restart or exhaustive accessibility audit is claimed by static/intercepted checks. Overall 009 stays in progress; 009.6/009.7 remain proposed.
