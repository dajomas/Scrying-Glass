# Scrying Glass handover

This is the index; substantive handover lives in numbered docs/handover sections.

## Index

1. [Scope and current state](docs/handover/010-scope-and-state.md)
2. [CI workflow and test coverage](docs/handover/020-ci-and-tests.md)
   - [Connection-lifetime audit isolation](docs/handover/021-connection-lifetime-audit.md)
   - [Automatic CI evidence publication](docs/handover/025-automatic-ci-publication.md)
3. [Open validation and next steps](docs/handover/030-validation-and-next-steps.md)
4. [Maintaining this handover](docs/handover/040-maintenance-rules.md)
5. [Admin script source split](docs/handover/050-admin-script-split.md)
6. [WebSocket regression fixture repair](docs/handover/060-websocket-regression-fixture.md)
7. [Display-connection fixture repair](docs/handover/070-display-connection-fixture.md)
8. [Monster lookup diagnostics repair](docs/handover/080-monster-lookup-diagnostics.md)
9. [Stats fallback fixture repair](docs/handover/090-stats-fallback-fixture.md)
10. [TODO tracking initialization](docs/handover/100-todo-tracking.md)
11. [Composed campaign router tests](docs/handover/110-composed-campaign-routers.md)
12. [Pytest module imports and execution](docs/handover/120-pytest-module-imports.md)
13. [Accounts migration fixture repair](docs/handover/130-accounts-migration-fixture.md)
14. [Viewer ownership fixture repairs](docs/handover/140-viewer-ownership-fixtures.md)
15. [Renderer VM window fixture repair](docs/handover/150-renderer-vm-window.md)
16. [Standalone audit and smoke fixtures](docs/handover/160-standalone-audit-and-smoke.md)
17. [Manual reductions restart plan](docs/handover/170-manual-reductions-restart.md)
18. [Attack statistics archive implementation](docs/handover/180-attack-statistics-delivery.md)
19. [Restore statistics readability and affected-only display](docs/handover/190-statistics-restoration-layout.md)
20. [Monster candidate selection](docs/handover/200-monster-candidate-selection.md)
21. [Next from Battle Actions](docs/handover/210-battle-actions-next.md)
22. [Initial Admin input visibility](docs/handover/220-admin-initial-visibility.md)
23. [Configurable 5e.tools source stages](docs/handover/230-fivetools-sources.md)
24. [SQLite storage source split](docs/handover/240-sqlite-storage-split.md)
25. [Single-line monster row controls](docs/handover/250-monster-button-layout.md)
26. [Admin visual foundations](docs/handover/260-admin-visual-foundations.md)
27. [Admin header and action hierarchy](docs/handover/270-admin-header-hierarchy.md)
28. [Consistent Admin panels and forms](docs/handover/280-admin-panel-forms.md)
29. [Add Monsters image previews](docs/handover/290-monster-image-previews.md)
30. [Add Monsters source help text](docs/handover/300-monster-source-help-text.md)
31. [Admin roster presentation](docs/handover/310-admin-rosters.md)
32. [Initiative keyboard navigation](docs/handover/320-initiative-keyboard-navigation.md)
33. [Monster initiative and refresh foundations](docs/handover/330-monster-initiative-foundations.md)
34. [5e.tools initiative correction](docs/handover/335-fivetools-initiative-correction.md)
35. [Combined lookup, Refresh and roster correction](docs/handover/340-combined-monster-lookup.md)
36. [Admin workflow navigation](docs/handover/350-admin-workflow-navigation.md)
37. [Battle Actions combatant statistics](docs/handover/360-battle-actions-combatant-statistics.md)
38. [Focused live encounter workspace](docs/handover/370-live-encounter-workspace.md)
39. [Feedback delivery plan and continuity](docs/handover/380-feedback-delivery-plan.md)
   - [Feedback foundations and CI history](docs/handover/381-feedback-foundations-and-ci-history.md)
   - [Start feedback history](docs/handover/382-start-feedback-history.md)
   - [Next and End feedback history](docs/handover/383-next-and-end-feedback-history.md)
   - [State-load feedback](docs/handover/385-state-load-feedback.md)
40. [Reset-all feedback](docs/handover/390-reset-all-feedback.md)
41. [Individual combatant reset feedback](docs/handover/400-individual-reset-feedback.md)
42. [Global removal fallback feedback](docs/handover/410-global-removal-fallback-feedback.md)
43. [Activity-log clear feedback](docs/handover/420-activity-log-clear-feedback.md)
44. [Viewer font adjustment feedback](docs/handover/430-viewer-font-feedback.md)
45. [Battle-action feedback: 4A.11 bounded close-out](docs/handover/440-battle-action-global-feedback.md)
46. [Join reporting: 4A.12 bounded close-out](docs/handover/450-join-reporting.md)
47. [Global feedback reconciliation: audit history](docs/handover/460-global-feedback-reconciliation.md)
   - [Statistics-open feedback](docs/handover/465-statistics-open-feedback.md)
   - [Campaign-bundle import, composition, retirement and corrections](docs/handover/467-bundle-import-feedback.md)
48. [Global feedback reconciliation: 4A.13 bounded close-out](docs/handover/470-global-feedback-close-out.md)

49. [Stage 2 character Edit feedback](docs/handover/480-character-edit-feedback.md)
50. [Stage 2 monster raw-roll feedback](docs/handover/490-monster-raw-roll-feedback.md)
51. [Stage 2 select-dead feedback](docs/handover/500-select-dead-feedback.md)
52. [Stage 2 bulk Join pane feedback](docs/handover/510-bulk-join-pane-feedback.md)

53. [Stage 1 campaign-operation feedback](docs/handover/520-campaign-operation-feedback.md) - Step 1 accepted/closed 2026-11-12; covering CI 43237771405 attempt 1 for 4f0127b56550cacb821ae2c62cb2057265eaea2a. Historical remaining-Stage-1 notes are superseded by the whole-stage close-out below.
54. [Stage 1 accepted close-out and setup-operation history](docs/handover/530-setup-operation-feedback.md#stage-1-accepted-close-out---2026-11-12) - all agreed campaign/setup/transfer/background work completed and closed, user acceptance 2026-11-12 at 19:45 CET. Final tested revision cc0b67b177772e314b608817f6f51cecc322a065; successful Branch tests 43279736032 attempt 1; evidence 97eedc6da52abcfa94526fee25a3c321f0626844. Historical wider-gate notes are superseded by final close-out 570.
55. [Stage 3 accepted local-feature feedback close-out](docs/handover/540-local-feature-feedback.md#stage-3-accepted-close-out---2026-11-12) - completed/closed for encounter tools, lairs/lair-action dialog, has-lair and selected-campaign viewer access; user accepted 2026-11-12 at 20:48 CET. Tested d17b5885baea02821224d811dffc070d6a7d33a4; successful Branch tests 43291659600 attempt 1; evidence db2daf8a473ebf77ff1626a8709a6a745e45b0b7. Earlier pending notes are superseded.
56. [Stage 4 accepted integration/accessibility close-out](docs/handover/550-integration-accessibility-hardening.md#stage-4-accepted-close-out---2026-11-12) - completed/closed for the agreed compatibility retirement and hardening scope; user accepted 2026-11-12 at 21:49 CET. Tested 535af6f350fdcb0a473d4d43133e0d8ac7c0b50e; successful Branch tests 43302214845 attempt 1; evidence 3bfa218c1ecd0b93c3a7278f88dd811ea4380540. Earlier publication/CI/acceptance-pending notes are superseded.
57. [Deliverable 2 accepted close-out](docs/handover/560-connection-field-feedback.md#deliverable-2-accepted-close-out---2026-11-12) - agreed Admin persistent connection/recovery, polling deduplication and near-field association completed/closed; user accepted 2026-11-12 at 22:43 CET. Tested 8da0657325818c69fc82dc1234995a5146e88ebc; successful Branch tests 43310602854 attempt 1; evidence dbb78d3057a2d38527bd612b948a6566a1a741e3. Historical whole-D1/final-pending notes are superseded by 570.
58. [Final Deliverable 1, 009.7 and overall 009 close-out](docs/handover/570-final-0097-close-out.md) - completed/closed for the agreed scope after final user acceptance 2026-11-12 at 22:58 CET; integrated evidence, unchanged code identity, criterion mapping and limits recorded. No new scope, test run, merge or deployment.
59. [Activity log affected unit and resulting value](docs/handover/580-activity-log-result-details.md) - SG-TODO-019 implemented on features/perplexity 2026-11-13 after the 009.7 branch merge; local results recorded; CI validation and user acceptance pending.

<a id="current-state---2026-11-11"></a>

## Current state - 2026-11-12

Whole Deliverable 1 and Deliverable 2, SG-TODO-009.7 and parent SG-TODO-009 are
completed and closed following the final 22:58 CET user acceptance/close-out request.
009.1-009.6, Stages 1-4, global units 4A.1-4A.13 and coordinated previously accepted
scopes remain closed. [570 final evidence/limits](docs/handover/570-final-0097-close-out.md)
is the current authority over dated whole-deliverable/final-review-pending notes in
earlier records; their evidence, failure histories and limitations remain historical.
Do not request their acceptance again or treat deferred optional work as a blocker.

Final integrated application revision 8da0657325818c69fc82dc1234995a5146e88ebc is
covered by successful Branch tests 43310602854 attempt 1; publication
 dbb78d3057a2d38527bd612b948a6566a1a741e3. Direct review confirms main Python
1,583 tests OK and pytest 43 passes plus selected feedback/integration/browser
results. All configured stages succeeded; not every result or screenshot was
individually reviewed. Git root identities show unchanged application, assets,
templates, tests, tooling and workflows through 2eb3b4d8a35b8a97761c1479f1ef68275652a01d.
No new authenticated live-server, human visual, screen-reader or exhaustive
accessibility verification is inferred from bounded final acceptance.

No agreed 009.7/009 implementation, validation or acceptance action remains.
Test-suite cleanup remains separate post-009 work; 016/017 remain proposed, not
closure prerequisites. SG-TODO-019 was implemented 2026-11-13 on features/perplexity
(the 009.7 branch is merged there); see [580](docs/handover/580-activity-log-result-details.md), CI pending. The agreed sequence in 115
is unchanged; its dated rationale is history. No new owner/deadline or blanket
future-write/merge/deployment approval.

This final close-out changes documentation only and uses [skip ci]. No application,
test, template, asset, pin or workflow change, no fresh tests and no separate workflow
dispatch. Earlier index history is preserved in the [pre-final-close-out index](https://github.com/dajomas/Scrying-Glass/blob/2eb3b4d8a35b8a97761c1479f1ef68275652a01d/HANDOVER.md)
and numbered handovers. Existing order, links and old anchors are retained.

## Maintenance

Update relevant numbered sections, preserve capitalization/ordering and links;
update this index when adding/renaming/reordering/removing sections. Follow
[maintenance rules](docs/handover/040-maintenance-rules.md) and live instructions;
never expand this index into a monolithic handover.
