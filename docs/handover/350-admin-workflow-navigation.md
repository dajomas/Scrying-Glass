# 350 - Admin workflow navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.5](../todo/095-admin-workflow-navigation.md). Status: in progress, user acceptance pending. Navigation through 7df8cbe67b62b4df772dd192f2ac38d19c4cfad8 has covering successful CI. Form refinement 8262863cc0a226e02b040eafb6827fb96af736a4 and overwrite refinement 2ec510c487453702dd1abe352b589125df44291a are delivered; their validation is not established by that earlier run. The concise lookup-text follow-up is prepared for exact approval and normal CI; no new success or closure is claimed.

## Workflow and retained history

Campaign contains selection/access/backups, Add character and Characters. Preparation contains setups/background/imports, Add monsters, both rosters and independently gated lair configuration. Live contains existing rosters, tools, lair and log. Battle/order/Danger zone and fixed header context/actions/feedback stay shared. Tabs preserve native collapse/preferences, DOM, drafts/files, selection, lair/tools restoration and source assembly. Campaign is the initial per-page view; refresh/battle changes do not steal the selected tab. Roving tab focus, Left/Right/Home/End, labelled workspace and local narrow scrolling remain. No 009.6 focused layout or roster filtering is delivered.

Implementation 1beff730, corrections c490943 / ef07efbc and smoke follow-up 7df8cbe remain delivered. Failed runs 42586178034 and 42590952958 remain failed historical evidence. Successful run 42594146455 attempt 1 covers exact 7df8cbe on features/perplexity; publication 07b12ed92b2d1c292381685611a41a7e9c1ded90 reports configured-step success, 1,416 main/repeated tests OK, audit 764/0 connections, 43 pytest passes and full mocked-HTTP/WS smoke with no page errors. Twenty-four fixture images include six navigation views; upload is not visual acceptance. Earlier successful 018 run 42526295799 covers f5808a2 only.

Full prior diagnosis, evidence paths and preparation limitations remain in the [immutable form-refinement handover](https://github.com/dajomas/Scrying-Glass/blob/8262863cc0a226e02b040eafb6827fb96af736a4/docs/handover/350-admin-workflow-navigation.md). This update corrects stale prepared-only delivery wording, not historical outcomes.

## Delivered form refinement

8262863 removes the entire bonus-help paragraph/reference, places the original optional signed bonus editor between HP Range end and Quantity in raw markup and the rendered Combat statistics group, and fills a currently empty/whitespace-only name from trimmed nonempty species on blur. Existing names remain editable and are never overwritten; no typing-only fill or automatic save is introduced. Static/native and assembled regressions retain creation/import/FormData/source contracts. Its preparation checked changed-block JS syntax and changed test snippets, not a full application/browser run.

## Overwrite refinement - delivered 2026-11-09

2ec510c487453702dd1abe352b589125df44291a implements the user's explicit Add Monster missing-bonus rule: with overwrite enabled, a successfully selected candidate explicitly reporting status=missing and null/absent bonus clears the field. Blank uses the existing backend default-zero path without source-bonus attribution. Candidate identity remains bound, but no bonus-offer token is submitted. Explicit source zero retains its genuine source offer. Unchecked overwrite preserves existing bonuses; blanks still accept available bonuses.

Invalid/ambiguous/malformed or inconsistent candidate data, failed/empty/cancelled/stale lookups and intervening edits (including edit/revert) do not clear the bonus. Existing generation/value/revision guards protect replacement and fallback. Bulk Refresh missing-field preservation and explicit Apply are unchanged; no schema/backend/provider/calculation change.

The loaded enhancement sets the agreed AC/HP/bonus checkbox label. Its compatibility help text does not recreate the removed paragraph. Tests cover the 16-case provider/checkbox/current-value matrix, invalid protection, old-offer removal, failure/no-match preservation, chooser/delayed edit guards and loaded label. Preparation checked changed-block JS syntax and one test snippet, not complete modules/browser execution. Historical missing-value preservation statements describe behavior before this explicit Add Monster change.

## Concise lookup copy - prepared 2026-11-09

The user identified the remaining lookup explanation as the last copy refinement. A separate monsterLookupHelp paragraph replaces the seven-sentence technical explanation with: Searches enabled D&D Beyond and configured 5e.tools sources. Choose a version when prompted. Failed or incomplete searches return no results—retry or enter stats manually. Uploaded images override source images.

The paragraph contains 29 whitespace-delimited words. Provider/configuration internals and the fivetools_fallback setting remain in detailed documentation rather than operational help. HP fixed/range/dice guidance, original form/input IDs, import controls, field order, species blur and lookup/overwrite mechanics remain unchanged. Raw checkbox text now matches the label already set by 2ec510c, preventing source/rendered-label mismatch without changing behavior.

Updated tests/test_monster_source_help_text.py checks the exact concise paragraph, a 40-word ceiling, unique IDs, absence of old fallback guidance, preserved configuration defaults/comments and real rendered desktop/narrow copy/checkbox with no mutations/page errors. The old browser expectation still named only AC/HP; this is corrected to the delivered label. No assertions concerning lookup mechanics are removed; verbose UI-copy assertions are replaced by the concise contract.

Executed preparation: HTML entity decoding/text round-trip and the 29-word check passed, as did Python AST parsing of the changed source-test snippet. Complete final template/test-module/browser/full-suite execution remains pending; no CI result is claimed for any unreviewed run. Existing unittest discovery covers this module; normal CI without a skip marker or workflow edits. README/indexes and relevant reviewed docs remain accurate without new edits.

Deploy matching HTML/static assets, restart the correct process for import-assembled HTML and reload Admin. No migration or core bundle edit. Review covering CI and user desktop/narrow/source/manual workflows before closure. Seeded/intercepted fixtures and storage reopen are not password login, live TCP/provider, new-process restart or exhaustive accessibility validation.
