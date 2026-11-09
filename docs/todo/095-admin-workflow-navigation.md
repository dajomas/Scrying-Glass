# 095 - Admin workflow navigation

[Back to TODO index](../../TODO.md)

## SG-TODO-009.5

- Status: in progress; implementation 1beff730580b17551ae5c95115ad31badf39b3f1 delivered with failed first CI. Corrective stage 1 delivered as c490943d5921b8abbec65fbeba0c012df39d2619; stage 2 prepared for exact-content approval. Corrected covering validation and user acceptance remain pending. This supersedes 090's earlier proposed wording for 009.5.
- Agreement: 2026-11-09, compact Campaign / Battle preparation / Live encounter views retaining original pane controls, DOM, drafts and native visibility state; user approved implementation and the two-commit correction split. No owner/deadline assigned.
- Baseline: features/perplexity after SG-TODO-018 merge b0630effbe99db8a40b27bb00cca007b198d4055.
- Evidence: failed run 42586178034 attempt 1 covers the implementation SHA, publication c01beaf5dcfdb931ab1c2a271e717f02cc7d4b6b. See [350 handover](../handover/350-admin-workflow-navigation.md#first-covering-ci-and-approved-correction-split---2026-11-09). No successful correction CI is claimed.

## Visibility mapping

Campaign contains selection/access/backups, Add character and Characters. Preparation contains setups/background/imports, Add monsters, both rosters and gated lair configuration. Live contains existing rosters, tools, gated lair and log. Battle/order/Danger zone and fixed header context/actions/feedback remain shared. No cloned/filtered rosters or 009.6 focused layout.

Tabs filter rendering independently of hidden/aria-expanded. Existing initial collapse, parent-child preferences, battle collapse/restoration, Has lair and tools restoration remain. Campaign is the initial per-page tab; no persistent tab setting, automatic navigation, form submit or encounter mutation is added.

## Approved corrective delivery

1. Stage 1 delivered: shared roster entry selects preparation through the actual UI after asserting Campaign startup; header explicitly selects Campaign; navigation retains untouched startup. Tools restoration establishes inactive baselines/both saved preferences and awaits refresh. Original roster/header assertions and production behavior remain. Four changed snippets passed AST parsing; full corrected execution/CI remains pending.
2. Stage 2 prepared: foundation/forms traverse actual destinations; retain blank/visible/expired notice, ARIA, focus/modal, CSS-state, required-label, geometry/screenshot, character/background/file draft, disclosure, idempotence, validation and save/rejection assertions. Secured Refresh adds preparation entry before its normal toggle; review/Apply/security/storage/HP/order assertions remain unchanged. Five helper/traversal snippets passed AST parsing; complete modules/browser/full suite were not executed locally.

Each stage requires its own exact write approval and normal CI with proportionate documentation. This stage is not task completion. No forced clicks, disabled navigation, skipped tests or discarded behavioral checks. [Prior task detail](https://github.com/dajomas/Scrying-Glass/blob/c490943d5921b8abbec65fbeba0c012df39d2619/docs/todo/095-admin-workflow-navigation.md) retains the stage-1 plan/history.

## Remaining acceptance

- Deliver stage 2 and review covering CI for both stages. Original failed results remain failed; classify any remaining failures against the tested revision.
- The supplied successful 42526295799 attempt 1 covers f5808a2 on features/perplexity-018 only, not either 009.5 correction.
- Preserve selection/bulk/Edit and 018 raw/bonus/total/source-refresh semantics; check initial/delayed/missing context, parent/child choices, start/end/reset, lair gating and tools restoration without tab stealing.
- Verify file/draft/modal/initiative continuation, keyboard/focus/viewport operation and absence of navigation mutations; review screenshots and obtain desktop/narrow user acceptance before closure.
- Snippet parsing/intercepted fixtures do not establish authenticated live-server, live-provider, process-restart or exhaustive accessibility validation.

009.6/009.7 remain proposed; overall 009 stays in progress. Existing 090 and indexed handovers retain previous redesign history.
