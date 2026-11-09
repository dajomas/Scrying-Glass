# 350 - Admin workflow navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.5](../todo/095-admin-workflow-navigation.md). Status: in progress, user acceptance pending. Navigation through 7df8cbe67b62b4df772dd192f2ac38d19c4cfad8 has covering successful CI. Form refinement 8262863cc0a226e02b040eafb6827fb96af736a4 is delivered; its validation is not established by that earlier run. The subsequent overwrite refinement is prepared for exact approval and normal CI; no new success or closure is claimed.

## Workflow and retained history

Campaign contains selection/access/backups, Add character and Characters. Preparation contains setups/background/imports, Add monsters, both rosters and independently gated lair configuration. Live contains existing rosters, tools, lair and log. Battle/order/Danger zone and fixed header context/actions/feedback stay shared. Tabs preserve native collapse/preferences, DOM, drafts/files, selection, lair/tools restoration and source assembly. Campaign is the initial per-page view; refresh/battle changes do not steal the selected tab. Roving tab focus, Left/Right/Home/End, labelled workspace and local narrow scrolling remain. No 009.6 focused layout or roster filtering is delivered.

Implementation 1beff730, corrections c490943 / ef07efbc and smoke follow-up 7df8cbe remain delivered. Failed runs 42586178034 and 42590952958 remain failed historical evidence. Successful run 42594146455 attempt 1 covers exact 7df8cbe on features/perplexity; publication 07b12ed92b2d1c292381685611a41a7e9c1ded90 reports configured-step success, 1,416 main/repeated tests OK, audit 764/0 connections, 43 pytest passes and full mocked-HTTP/WS smoke with no page errors. Twenty-four fixture images include six navigation views; upload is not visual acceptance. Earlier successful 018 run 42526295799 covers f5808a2 only.

Full prior diagnosis, evidence paths and preparation limitations remain in the [immutable form-refinement handover](https://github.com/dajomas/Scrying-Glass/blob/8262863cc0a226e02b040eafb6827fb96af736a4/docs/handover/350-admin-workflow-navigation.md). This update corrects stale prepared-only delivery wording, not historical outcomes.

## Delivered form refinement

8262863 removes the entire bonus-help paragraph/reference, places the original optional signed bonus editor between HP Range end and Quantity in raw markup and the rendered Combat statistics group, and fills a currently empty/whitespace-only name from trimmed nonempty species on blur. Existing names remain editable and are never overwritten; no typing-only fill or automatic save is introduced. Static/native and assembled regressions retain creation/import/FormData/source contracts. Its preparation checked changed-block JS syntax and changed test snippets, not a full application/browser run.

## Overwrite refinement - prepared 2026-11-09

The user explicitly changed Add Monster's missing-bonus rule: when overwrite is enabled, a successfully selected candidate explicitly reporting status=missing with null/absent bonus clears the field. Blank uses the existing backend default-zero path without source-bonus attribution. Source identity/selection remains bound to the candidate, but no bonus-offer token is submitted. A valid explicit source zero still copies as zero with its genuine source offer. Existing populated bonuses remain unchanged with overwrite disabled; blank fields still accept available bonuses.

Invalid/ambiguous/malformed or inconsistent candidate data, lookup failures, no candidates, cancel, stale responses, scope/checkbox changes and values edited during lookup/chooser (including edit/revert) are not reasons to clear the bonus. Existing generation and value/revision guards protect both replacement and fallback. The change is Add Monster only: bulk Refresh's missing-field preservation and explicit Apply contract remain unchanged. No schema/backend/provider/initiative calculation change.

The loaded candidate enhancement updates the existing checkbox label to: Overwrite AC, HP range and initiative bonus with source values. Missing initiative bonus defaults to 0. Raw template markup is not changed in this increment; the operational label is set by the same enhancement that owns source bonus behavior. Its optional help-node compatibility text is aligned without recreating the removed production paragraph.

Prepared regressions preserve all existing bonus tests, move missing-only cases into a 16-case provider/checkbox/current-value matrix, retain invalid/ambiguous protection, check prior-offer removal and failed/empty lookup preservation, and extend chooser and delayed HTTP edit/revert checks to missing bonuses. An assembled desktop/narrow test checks the loaded label and continued absence of the long help paragraph. These use mocked transport/tokens, not live signing/provider evidence.

Executed preparation: Node syntax check of the changed label/overwrite block and Python AST parsing of the missing-matrix snippet passed. Complete final modules, browser/full-suite runs and covering CI for this refinement have not been executed here. Existing unittest discovery covers the changed regression module; CI tree is unchanged. README's outdated help/missing-value descriptions are updated. Root indexes and other reviewed docs retain applicable links/contracts without edits. Historical missing-value preservation statements apply before this explicit Add Monster change.

Deploy the changed static asset and reload Admin; no migration/configuration change or core bundle edit. Review covering CI and user desktop/narrow/source/manual workflows before closure. Seeded/intercepted fixtures and storage reopen are not password login, live TCP/provider, new-process restart or exhaustive accessibility validation.
