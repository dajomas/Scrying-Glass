# 095 - Admin workflow navigation

[Back to TODO index](../../TODO.md)

## SG-TODO-009.5

- Status: in progress; implementation delivered in 1beff730580b17551ae5c95115ad31badf39b3f1, first covering CI failed. Corrective stage 1 of 2 prepared; corrected validation and user acceptance pending. This entry supersedes the proposed status for 009.5 in the historical [090 redesign plan](090-admin-usability-redesign.md).
- Agreement: 2026-11-09, compact Campaign / Battle preparation / Live encounter views retaining original pane controls, DOM, drafts and native visibility state. User requested implementation and subsequently approved the two-commit correction split.
- Baseline: features/perplexity after SG-TODO-018 merge b0630effbe99db8a40b27bb00cca007b198d4055. 018 is no longer an outstanding prerequisite on this branch. No new owner/deadline assigned.
- Evidence: failed Branch tests 42586178034 attempt 1, exact implementation SHA above; publication c01beaf5dcfdb931ab1c2a271e717f02cc7d4b6b. See [350 handover](../handover/350-admin-workflow-navigation.md#first-covering-ci-and-approved-correction-split---2026-11-09) for reviewed results, diagnosis and limitations. No corrective commit SHA or successful corrective CI result is invented.

## Visibility mapping

Campaign contains campaign selection/access/backups, Add character and Characters. Preparation contains setups/background/imports, Add monsters, both rosters for initiative/participation and gated lair configuration. Live contains existing rosters, tools, gated lair and log. Battle/order/Danger zone and fixed header actions/context/feedback remain shared. Rosters are not cloned or filtered. Focused encounter layout is 009.6, not this increment.

Tabs filter rendered destinations independently of pane.hidden and aria-expanded. Existing per-page collapse, parent-child preferences, automatic battle collapse/restoration, independent Has lair gate and tools restoration remain. Campaign is the initial tab; selecting another tab is per-page only. No automatic battle navigation, persistent tab setting, form submit or encounter mutation is introduced. Current-view pane controls remain discoverable in View panels.

## Approved corrective delivery

1. Stage 1: shared roster fixtures select preparation through the UI after asserting Campaign startup; header fixtures explicitly select Campaign; navigation fixtures retain startup without synthetic selection. Tools restoration uses inactive baselines, both saved preferences, awaited real refresh and desktop/narrow view changes. Original roster/header assertions remain. Production behavior is unchanged. Four changed method/signature snippets passed Python AST parsing; complete corrected modules/browser/full suite and covering CI remain unexecuted.
2. Stage 2: foundation/form assertions traverse their actual workflow destinations, retaining drafts, selected files, notices, focus, validation, save/rejection and geometry checks. The secured Refresh fixture selects preparation before its existing controls and retains all review/Apply/security/persistence assertions. Not included in stage 1.

Each stage has its own exact-content write approval, normal CI and proportionate documentation. Stage 1 is intentionally partial and may still have failing full-suite results until stage 2. Do not force hidden controls, disable navigation, skip tests or remove behavioral assertions to obtain green CI.

## Acceptance and remaining work

- Deliver the approved stages and review covering CI. The original failed run remains failed, not closure evidence.
- Preserve selection/bulk/Edit and SG-TODO-018 raw/bonus/total/source-refresh semantics.
- Check initial/delayed state, campaign/setup absent/present, parent/child manual choices, start/end/reset, lair enabled/disabled and tools restoration without tab stealing.
- Check drafts/file values, modal and initiative-focus continuation, no navigation requests/mutations, accessible active/focus state and keyboard/viewport behavior.
- Obtain user desktop/narrow visual/workflow acceptance before closure. Snippet parsing and intercepted fixtures do not establish authenticated live-server or exhaustive accessibility validation.

009.6 and 009.7 remain proposed. This entry does not close overall SG-TODO-009 or reopen completed phases. Previous redesign history remains in 090 and linked handovers.
