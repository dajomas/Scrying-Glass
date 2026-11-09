# 095 - Admin workflow navigation

[Back to TODO index](../../TODO.md)

## SG-TODO-009.5

- Status: in progress; implementation and targeted regressions prepared, not yet pushed or validated. This current entry supersedes the proposed status for 009.5 in the historical [090 redesign plan](090-admin-usability-redesign.md).
- Agreement: 2026-11-09, compact Campaign / Battle preparation / Live encounter views retaining original pane controls, DOM, drafts and native visibility state. User explicitly requested proceeding and implementation.
- Baseline: features/perplexity after SG-TODO-018 merge b0630effbe99db8a40b27bb00cca007b198d4055. 018 is no longer an outstanding prerequisite on this branch. No new owner/deadline assigned.
- Delivery/evidence: [350 handover](../handover/350-admin-workflow-navigation.md). No implementation commit SHA or CI outcome exists for this proposal.

## Visibility mapping

Campaign contains campaign selection/access/backups, Add character and Characters. Preparation contains setups/background/imports, Add monsters, both rosters for initiative/participation and gated lair configuration. Live contains existing rosters, tools, gated lair and log. Battle/order/Danger zone and fixed header actions/context/feedback remain shared. Rosters are not cloned or filtered. Focused encounter layout is 009.6, not this increment.

Tabs filter rendered destinations independently of pane.hidden and aria-expanded. Existing per-page collapse, parent-child preferences, automatic battle collapse/restoration, independent Has lair gate and tools restoration remain. Campaign is the initial tab; selecting another tab is per-page only. No automatic battle navigation, persistent tab setting, form submit or encounter mutation is introduced. Current-view pane controls remain discoverable in View panels.

## Acceptance and remaining work

- Review the exact write payload and approve delivery to features/perplexity with normal CI.
- Execute targeted and existing regressions; adapt older all-panel tests with explicit destination selection where required, not forced visibility, assertion deletion or disabling navigation.
- Review covering CI, screenshots and actual desktop/narrow operation. Preserve successful/failed form-save behavior, selection/bulk/Edit and SG-TODO-018 raw/bonus/total/source-refresh semantics.
- Check initial/delayed state, campaign/setup absent/present, parent/child manual choices, start/end/reset, lair enabled/disabled, tools pre-battle restoration and refresh without tab stealing.
- Check drafts/file values, modal and initiative-focus continuation, no navigation requests/mutations, accessible active/focus state and tab keyboard/viewport behavior.
- Obtain user visual/workflow acceptance before closure. No checks have been executed during preparation; no new test pass or CI result is claimed.

009.6 and 009.7 remain proposed. This entry does not close overall SG-TODO-009 or reopen completed phases. The complete previous redesign history is retained in 090 and its linked handovers.
