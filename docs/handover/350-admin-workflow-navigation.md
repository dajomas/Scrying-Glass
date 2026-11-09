# 350 - Admin workflow navigation

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-009.5](../todo/095-admin-workflow-navigation.md). Status: completed and closed at the user's explicit sign-off/request. Overall 009 remains in progress. Next scheduled work is [SG-TODO-015](../todo/150-battle-actions-combatant-statistics.md), with live inspection started but no application delivery in this close-out.

## Delivered workflow

Campaign: campaign selection/access/backups, Add character and Characters. Preparation: setups/background/imports, Add monsters, both rosters and independently gated lair configuration. Live: existing rosters, tools, lair and log. Battle/order/Danger zone and fixed header context/actions/feedback stay shared. Tabs preserve native collapse/preferences, original DOM, drafts/files, selections, independent lair/tools restoration and source assembly. Campaign is the per-page default; refresh/battle changes do not steal the tab. Keyboard/ARIA and local narrow scrolling are included; no roster filtering or 009.6 focused workspace is delivered.

Accepted form refinements remove bonus help/reference, place the optional signed bonus field between HP Range end and Quantity in Combat statistics, and fill only a currently blank name from trimmed nonempty species on blur. Add Monster overwrite covers AC/HP/bonus; selected missing/null bonus clears to blank/default zero without source-bonus attribution, while explicit source zero retains genuine offer provenance. Invalid/ambiguous/malformed, failed/empty/cancelled/stale lookup and intervening edits are protected. Bulk Refresh's missing-field and explicit Apply rules remain unchanged. No backend/schema/provider/initiative-calculation change.

The final lookup paragraph is the user's cfc7b0f16f929041bc6107dd1f895d24492261c5 wording: While entering Monster species, D&D Beyond and configured 5e.tools sources will be searched. Choose a version when prompted. Uploaded images override source images. Both template and LOOKUP_HELP expectation match. Preserve that manual edit.

## Delivery history

- Initial navigation: 1beff730580b17551ae5c95115ad31badf39b3f1.
- User-approved fixture corrections: c490943d5921b8abbec65fbeba0c012df39d2619 and ef07efbc9373fb62fecaeab727e4996acdd58660.
- Independent smoke correction: 7df8cbe67b62b4df772dd192f2ac38d19c4cfad8.
- Bonus/name form refinement: 8262863cc0a226e02b040eafb6827fb96af736a4.
- Missing-bonus overwrite and label: 2ec510c487453702dd1abe352b589125df44291a.
- Concise copy/template label/regressions: c7c51725c5ac7724fc78ffd1931173cd1d19e0b8.
- Later user template/test wording: cfc7b0f16f929041bc6107dd1f895d24492261c5.

Full earlier scope decisions, failed-run diagnosis, staged preparation checks and evidence paths remain in the [immutable pre-close-out handover](https://github.com/dajomas/Scrying-Glass/blob/cfc7b0f16f929041bc6107dd1f895d24492261c5/docs/handover/350-admin-workflow-navigation.md). Historical runs 42586178034 and 42590952958 remain failed; later successful coverage does not relabel them. Prior green 42594146455 covers 7df8cbe, not later application edits; the covering c7c51725 run below establishes the subsequent gate.

## SG-TODO-009.5 close-out - 2026-11-09

Successful Branch tests 42616924220 attempt 1 completed on exact c7c51725c5ac7724fc78ffd1931173cd1d19e0b8, features/perplexity. Publication 1c1c6323b119b1a7e71a93571985c214183819de contains ci-results-42616924220-attempt-1. Reviewed run.json/jobs.json report workflow/job and all configured steps successful. Reader workflow file-000032 part-000114 reports 1,421 main tests OK; part-000156 reports repeated 1,421 tests OK, 766 connections and zero without explicit close, plus completed Admin select-all, users Edit selection, client disconnect/reconnect identity and mobile-layout smoke with no page errors. Part-000116 reports 43 pytest passes; JavaScript, syntax/import, standalone and artifact steps succeed. Fixture artifact index contains 24 images including six navigation views; upload/collection is not assistant visual inspection.

The user explicitly signed off 009.5 and requested closure/moving to the next scheduled item. This supplies overall workflow acceptance, not a claim that every manual scenario was individually executed or that an assistant performed authenticated live-server checks. The later cfc7b0f1 edit is accepted user copy with matching source/test text; the successful run above tests c7c51725 only. No separate post-copy covering CI result has been supplied or invented. This evidence boundary is retained in the task and root index rather than misrepresenting the accepted revision as directly CI-tested.

Tests use intercepted HTTP/WS, seeded sessions/provider/HP mocks or fixture data as documented; storage reopen is not a new OS process. No fresh password-login, live TCP/provider, process-restart or exhaustive accessibility audit accompanies close-out. No implementation defect or outstanding agreed acceptance request is identified by the user sign-off; 009.5 closes for its accepted scope without closing overall 009 or starting 009.6.

## Next scheduled item and documentation-only transition

The agreed sequence is 018, 009.5, 015, 009.6, 009.7, coordinated 016/017. On the user's request, 015 inspection began with live static/admin/060-source.js: activeBattleTargets, dynamic action/reaction rows, data-action-target/data-action-source placeholders and statistics-reduction target rows. Existing application/test/refresh/style inspection must continue before implementation. 015 adds read-only available AC/current HP/HP MAX below the selected target and Reaction source, with correct zero/missing/cleared-selection handling and unchanged resolution.

This close-out changes documentation only, runs no new tests and uses [skip ci] without workflow modification/dispatch or inferred run state. README/User Guide and indexed maintenance guidance were reviewed/reused and remain accurate without edits; root indexes are updated because task/validation status changed. Existing application, tests, assets and the user's copy remain untouched.
