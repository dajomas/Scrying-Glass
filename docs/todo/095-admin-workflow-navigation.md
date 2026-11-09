# 095 - Admin workflow navigation

[Back to TODO index](../../TODO.md)

## SG-TODO-009.5

- Status: in progress; navigation and all test corrections delivered with successful covering CI on 7df8cbe67b62b4df772dd192f2ac38d19c4cfad8. Subsequent user-requested Add Monsters form refinement prepared; its delivery/validation and user acceptance remain pending. This supersedes 090's earlier proposed wording for 009.5.
- Agreement: 2026-11-09, compact Campaign / Battle preparation / Live encounter views retaining original controls, DOM, drafts and native visibility. User approved implementation/corrections and subsequently requested the form changes below. No owner/deadline assigned.
- Baseline: features/perplexity after SG-TODO-018 merge b0630effbe99db8a40b27bb00cca007b198d4055.
- Evidence: successful run 42594146455 attempt 1 covers exact 7df8cbe; publication 07b12ed92b2d1c292381685611a41a7e9c1ded90. Main/repeated suites 1,416 tests OK, audit 764/0 connections, 43 pytest passes, configured steps and full smoke successful. This does not cover the new form refinement. See [350 handover](../handover/350-admin-workflow-navigation.md).

## Scope and retained history

Campaign contains selection/access/backups, Add character and Characters. Preparation contains setups/background/imports, Add monsters, both rosters and gated lair configuration. Live contains existing rosters, tools, gated lair and log. Battle/order/Danger zone and fixed header context/actions/feedback remain shared. Native initial/parent-child/battle collapse, Has lair and tools restoration remain; no automatic tab switching, persistent tab preference or navigation mutation. No cloned/filtered rosters or 009.6 focused workspace.

Implementation 1beff730, user-approved corrective stages c490943 / ef07efbc and smoke follow-up 7df8cbe are delivered. Failed runs 42586178034 and 42590952958 remain failed historical evidence; the later successful covering run resolves their CI gate, not user acceptance. [Immutable prior task record](https://github.com/dajomas/Scrying-Glass/blob/7df8cbe67b62b4df772dd192f2ac38d19c4cfad8/docs/todo/095-admin-workflow-navigation.md) and linked handovers retain full diagnosis/history.

## Requested form refinement - 2026-11-09

- Remove the complete initiative-bonus help paragraph and its input reference.
- Put Initiative bonus between HP Range end and Quantity in raw markup and the rendered Combat statistics group; retain original input identity and signed optional/default semantics.
- On species blur, copy trimmed nonempty species into a currently blank/whitespace-only Monster name. Preserve existing names and allow later editing; do not copy on typing alone or mutate/save an encounter.
- Prepare static/native and assembled desktop/narrow regressions for absence/order/grouping, idempotence, blank/custom/repeated/whitespace blur behavior and no accidental mutation. Preserve original import/FormData/backend/source-offer contracts.

The implementation/tests and proportionate handover updates are prepared for exact write approval and normal CI. Changed JavaScript block syntax and changed Python-test-snippet AST checks passed; complete modules/browser/full-suite execution remains pending. No new corrective CI or acceptance is claimed.

## Remaining acceptance

- Deliver this refinement and review its covering CI; prior navigation CI is not coverage of application edits.
- Confirm desktop/narrow field placement, keyboard flow and species-to-name behavior, alongside drafts/files, pane preferences, initial/delayed context, battle/lair/tools restoration and modal/initiative continuation.
- Retain selection/bulk/Edit and 018 source/bonus/raw/total semantics. Review source/manual monster creation without regressions.
- Obtain user visual/workflow acceptance before closing 009.5. Static/intercepted fixtures do not establish authenticated live-server, live-provider, restart or exhaustive accessibility validation.

009.6/009.7 remain proposed; overall 009 stays in progress. Original 090 and indexed handovers retain previous redesign history.
