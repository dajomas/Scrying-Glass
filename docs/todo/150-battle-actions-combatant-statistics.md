# 150. Battle Actions combatant statistics

[Back to TODO index](../../TODO.md)

- Task: SG-TODO-015
- Status: in progress; implementation, targeted regressions and documentation prepared for exact GitHub approval. Full-Admin execution, covering CI and user acceptance remain pending; not completed.
- Recorded: 2026-11-06; implementation preparation 2026-11-09 after 009.5 closure and the user's explicit request to implement/push.
- Priority: current in the [agreed sequence](115-admin-delivery-sequence.md), after closed 018/009.5 and before 009.6. No owner/deadline assigned.
- Delivery/evidence: [360 handover](../handover/360-battle-actions-combatant-statistics.md). No implementation SHA or successful covering CI is invented before delivery.

## Implemented scope in this proposal

Show available AC, current HP and HP MAX immediately below each selected Battle Actions target and Reaction source. Ordinary/reaction/statistics-reduction target rows share the same enhancement. Example: AC 14 · HP 0 · HP MAX 20. Omit unavailable/null/undefined/non-numeric/non-finite fields; preserve numeric zero. Empty selection, removed combatant, all-unavailable data, hidden modal and a changed campaign/setup clear the summary rather than retaining stale values.

Summaries are read-only text, linked descriptions/live regions with stable selector names. Selection changes, dynamic rows, same-scope state refresh, Apply refresh and modal reopen are handled without rebuilding controls, changing selected values, disabled/Applied state, input drafts, action payloads, eligibility or resolution. Existing native scope-close behavior remains; the enhancement also suppresses cross-scope statistics until a new modal session. No backend/API/schema/persistence/provider/initiative change, core fragment edit or failure-marker overwrite.

## Inspection and preparation

Reviewed live action/reaction/reduction row builders in static/admin/060-source.js, core load/Apply behavior, modal markup, admin/modal styles, statistics scope-close and lair render hooks, battle-turn and Next extensions, existing browser fixtures, asset ordering and CI discovery. New deferred assets compose the existing scryingLairsRender hook, preserving its arguments/context/return, and use bounded DOM observers with self-observation disconnected. No polling, network requests or control-value writes.

Executed checks: complete new JavaScript module Node syntax check; new stylesheet parsing; AST parsing of the complete six-method regression module. Isolated real Chromium checks passed for partial/missing/zero fields, independent selectors, clearing, refresh, scope suppression, draft/disabled retention, existing description preservation, hook return, idempotence, dynamic row insertion/removal and below-selector geometry at 1440/375, with no page errors. These are simplified synthetic DOM/state fixtures, not the full Admin/backend.

Prepared full-Admin intercepted-HTTP coverage uses production assets and native row/open/Apply helpers: selection/clearing, reaction/reduction rows, missing/invalid/zero/deleted cases, idempotence, actual Apply payload plus refreshed locked row/draft retention, scope/reopen/removal and desktop/narrow placement/description/screenshot checks. The six methods (one source, five browser) were not executed as a complete module locally. Existing unittest/standalone audit discovery and SG_VISUAL_ARTIFACTS upload include them; no workflow edits required.

## Acceptance and delivery gates

- Approve/deliver the complete implementation/test/documentation payload on features/perplexity with normal CI, without [skip ci].
- Review covering full-suite/CI results and fixture screenshots; fix any regressions while retaining existing Apply/Next/modal/turn/security tests.
- Manually verify readable placement for character/monster selections, multiple independent rows, missing and zero values, selection changes/clearing, refresh/Apply locking and narrow keyboard operation.
- Obtain task-specific user visual/workflow acceptance before closure. Simplified/intercepted fixtures are not password-login, live TCP/provider, database/process-restart or exhaustive accessibility evidence.

The 009.5 transition was documentation-only and ran no tests; this mixed feature proposal supersedes inspection-only delivery status, not historical evidence. 009.5 stays closed. Overall 009 remains in progress and 009.6/009.7 stay proposed.
