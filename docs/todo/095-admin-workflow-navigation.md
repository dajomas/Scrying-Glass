# 095 - Admin workflow navigation

[Back to TODO index](../../TODO.md)

## SG-TODO-009.5

- Status: in progress; implementation 1beff730580b17551ae5c95115ad31badf39b3f1 and corrective stages c490943d5921b8abbec65fbeba0c012df39d2619 / ef07efbc9373fb62fecaeab727e4996acdd58660 are delivered. Covering unittest/audit suites pass, but run 42590952958 attempt 1 remains failed in the standalone smoke. Smoke follow-up prepared; corrected complete CI and user acceptance pending. This supersedes 090's earlier proposed wording for 009.5.
- Agreement: 2026-11-09, compact Campaign / Battle preparation / Live encounter views retaining original pane controls, DOM, drafts and native visibility state; user approved implementation, the two-commit correction split and subsequently requested the standalone smoke fix. No owner/deadline assigned.
- Baseline: features/perplexity after SG-TODO-018 merge b0630effbe99db8a40b27bb00cca007b198d4055.
- Evidence: original failed run 42586178034 attempt 1 covers implementation 1beff730, publication c01beaf5dcfdb931ab1c2a271e717f02cc7d4b6b. Run 42590952958 attempt 1 covers ef07efbc, publication 86a515cd5bb2d94abce7aa7c2715cdc2018a7279: 1,416 main tests OK and repeated 1,416-test audit OK, 764 connections/zero unclosed; standalone smoke still fails. See [350 handover](../handover/350-admin-workflow-navigation.md#covering-stage-2-ci-and-standalone-smoke-follow-up---2026-11-09). No overall successful correction CI is claimed.

## Visibility mapping

Campaign contains selection/access/backups, Add character and Characters. Preparation contains setups/background/imports, Add monsters, both rosters and gated lair configuration. Live contains existing rosters, tools, gated lair and log. Battle/order/Danger zone and fixed header context/actions/feedback remain shared. No cloned/filtered rosters or 009.6 focused layout.

Tabs filter rendering independently of hidden/aria-expanded. Existing initial collapse, parent-child preferences, battle collapse/restoration, Has lair and tools restoration remain. Campaign is the initial per-page tab; no persistent tab setting, automatic navigation, form submit or encounter mutation is added.

## Corrective delivery and smoke follow-up

1. Stage 1 delivered: shared roster entry selects preparation through the UI after asserting Campaign startup; header selects Campaign; navigation retains untouched startup. Tools restoration establishes inactive baselines/both saved preferences and awaits refresh. Original roster/header assertions and production behavior remain.
2. Stage 2 delivered: foundation/forms traverse destinations and retain notices/ARIA, focus/modal, CSS-state, required-label, geometry/screenshot, drafts/files, disclosure, idempotence, validation and save/rejection checks. Secured Refresh adds preparation entry; existing review/Apply/security/storage/HP/order assertions remain. Covering main unittest and repeated audit execution pass; this does not make the overall failed run successful.
3. Standalone smoke fix prepared: wait for navigation readiness, assert Campaign startup, click preparation and assert it selected before the existing conditional monster-pane toggle/select-all. Assert pane visibility afterward. Five added lines, all original 12 assertions retained (15 total), users/client suffix unchanged. Complete corrected file AST/compile, assertion-retention and original blob identity checks passed; actual corrected browser execution remains pending.

Each external write requires exact approval and normal CI. No forced clicks, disabled navigation, skipped tests or discarded behavioral assertions. [Prior stage-1 task detail](https://github.com/dajomas/Scrying-Glass/blob/c490943d5921b8abbec65fbeba0c012df39d2619/docs/todo/095-admin-workflow-navigation.md) retains earlier plan/history.

## Remaining acceptance

- Deliver the requested standalone smoke correction and review complete covering CI, including the later users/client checks that were not reached in the failed standalone execution. Both historical failed runs remain failed.
- The successful 42526295799 attempt 1 covers f5808a2 on features/perplexity-018 only, not 009.5.
- Preserve selection/bulk/Edit and 018 raw/bonus/total/source-refresh semantics; check initial/delayed/missing context, parent/child choices, start/end/reset, lair gating and tools restoration without tab stealing.
- Verify file/draft/modal/initiative continuation, keyboard/focus/viewport operation and absence of navigation mutations; review screenshots and obtain desktop/narrow user acceptance before closure.
- Static parsing and intercepted fixtures do not establish authenticated live-server, live-provider, process-restart or exhaustive accessibility validation.

009.6/009.7 remain proposed; overall 009 stays in progress. Existing 090 and indexed handovers retain previous redesign history.
