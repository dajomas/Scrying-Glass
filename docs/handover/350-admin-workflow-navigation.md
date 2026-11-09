# 350 - Admin workflow navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.5](../todo/095-admin-workflow-navigation.md).
Status: implementation 1beff730580b17551ae5c95115ad31badf39b3f1 delivered; its first CI failed. Corrective stage 1 delivered as c490943d5921b8abbec65fbeba0c012df39d2619; stage 2 prepared, awaiting exact write approval. Corrected covering execution/CI and user acceptance remain pending. No closure is claimed.

## Agreed approach and destinations

The user accepted compact workflow tabs while retaining original DOM, form drafts and pane controllers. Baseline: features/perplexity after SG-TODO-018 merge b0630effbe99db8a40b27bb00cca007b198d4055.

- Campaign: campaign selection/access/backups, Add character and Characters.
- Battle preparation: setups/background/imports, Add monsters, both rosters for initiative/participation and gated lair configuration.
- Live encounter: existing rosters, encounter tools, gated lair controls and activity log. No roster filtering or 009.6 focused layout is implemented.
- Shared: Battle/order/Danger zone and fixed header context, Start/Next/End, More/logout/viewer controls and global feedback. View panels exposes the current destination's existing toggles; parent/child and lair gating still apply.

Campaign remains the per-page initial view. Tabs do not submit, save, mutate encounters, open collapsed panes or auto-switch on battle transitions. View filtering uses data-workflow-excluded, not controller-owned hidden/aria-expanded; original nodes/listeners, file inputs, drafts and selections remain. Existing initial and battle collapse/restoration and independent encounter-tools preference restoration remain authoritative.

Tabs have roving tabindex, aria-selected, Left/Right wrapping and Home/End. The existing main is the shared labelled tabpanel; scroll positions are per-page/per-view. Narrow tabs scroll locally. Installation is idempotent and leaves legacy UI intact when prerequisites are missing. Assets load after existing enhancements and install at DOMContentLoaded. Deploy matching HTML/static files, restart the correct serving process for assembled HTML and reload Admin. Core fragments/assembly/failure marker, API, security, persistence and combat semantics are unchanged.

Detailed original preparation, compatibility decisions and stage-1 diagnosis are retained in the [immutable stage-1 handover](https://github.com/dajomas/Scrying-Glass/blob/c490943d5921b8abbec65fbeba0c012df39d2619/docs/handover/350-admin-workflow-navigation.md). This current summary supersedes obsolete prepared-only delivery wording, not historical failures or validation limitations.

## First covering CI and approved correction split - 2026-11-09

Run 42586178034 attempt 1 completed/failure on exact 1beff730580b17551ae5c95115ad31badf39b3f1, features/perplexity. Evidence: c01beaf5dcfdb931ab1c2a271e717f02cc7d4b6b, ci-results-42586178034-attempt-1. Main and repeated audit suites each report 1,416 tests, 31 failures and 31 errors; repeated failures are not additional independent defects. Audit: 762 connections, zero without explicit close. Dependencies, syntax/server import, pytest and JavaScript steps succeeded. Eighteen images were uploaded, including six 009.5 fixtures; upload is not assistant visual acceptance.

Inspected failures include out-of-view controls, zero visible roster counts/geometry, cross-view notice/focus assumptions and secured Refresh navigation. Four of five new navigation methods passed; tools restoration sampled an already battle-forced visible value instead of a known inactive preference. The entire failed run is not labelled fixture-only without corrective coverage.

The user approved two corrective commits. Stage 1 selects preparation through the real shared-fixture UI after asserting Campaign startup, with explicit Campaign entry for header tests and untouched startup for navigation tests. It covers both inactive tools preferences, awaited real refresh, active rounds/off-view filtering and restoration at desktop/narrow widths. Original roster/header assertions remain and no production navigation is blocked. Four changed snippets passed AST parsing; no corrected full-module/browser/CI pass was claimed.

## Corrective stage 2 preparation - 2026-11-09

Stage 2 changes tests/test_admin_foundations.py, tests/test_admin_panel_forms.py and tests/test_monster_refresh_end_to_end.py plus this handover/task record. Foundation and panel fixtures visit Campaign and preparation through actual tabs, open parents before children and assert rendered visibility before notice, focus, required-label and group-geometry checks. All four notices retain blank collapse, readable success, ARIA and expiry assertions, tested in destination pairs rather than an impossible simultaneous all-view layout.

Character drafts are entered in Campaign; background/file drafts and disclosures in preparation. Traversal verifies retention before refresh; refresh is awaited; character/file and common-action assertions remain in the correct views. Required validation, rejected/successful character submission, invalid monster HP, idempotent original node/form/handler identity, panel geometry and screenshot coverage remain. The secured ASGI/SQLite fixture selects preparation before its normal monster toggle. Its review/explicit Apply, selective update, HP-once, order/round/turn, storage reopen, sole/multiple candidate, stale review and health-conflict assertions are unchanged. No forced interaction, disabled production navigation, skipped test or removed behavioral check is introduced.

Executed stage-2 preparation: Python AST parsing passed for five changed helper/traversal snippets (foundation entry, notice traversal, panel setup, panel geometry and async Refresh entry). Complete replacement modules and actual browser/full-suite tests were not executed here. Existing CI unittest discovery and screenshot upload cover these modules/images; no workflow edits or skip marker are proposed. Both stages need covering CI review before claiming the failed suite corrected.

The supplied run 42526295799 attempt 1 was rechecked via run.json at publication 790a32b0f86eb60a86319d7c3158f9a7c22f489b: completed/success for f5808a2dfbc9b8d8bd4de9706956dbe8312815a5 on features/perplexity-018. It is historical 018 evidence, not coverage of 009.5, c490943 or this stage. No new stage-1/2 CI result is inferred.

Pending: corrected full-suite/CI results, remaining failure classification, screenshot review and user desktop/narrow workflow acceptance, including initial/delayed context, battle start/end/reset, enabled/disabled lair/dependencies, modal/initiative continuation and file/draft behavior. Fixtures use intercepted transport and seeded sessions/mock provider/HP data; storage reopen is not a new OS process. No password-login, live TCP/provider, process-restart or exhaustive accessibility audit is claimed.

README, root indexes and relevant existing docs were reviewed/reused with unchanged identities where applicable; no link/runtime-description change requires editing them for this test-only stage. Prior detailed history remains linked above.
