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
54. [Stage 1 accepted close-out and setup-operation history](docs/handover/530-setup-operation-feedback.md#stage-1-accepted-close-out---2026-11-12) - all agreed campaign/setup/transfer/background work completed and closed, user acceptance 2026-11-12 at 19:45 CET. Final tested revision cc0b67b177772e314b608817f6f51cecc322a065; successful Branch tests 43279736032 attempt 1; evidence 97eedc6da52abcfa94526fee25a3c321f0626844. Step 2/3 pending notes are superseded; wider gates remain open.
55. [Stage 3 local-feature feedback](docs/handover/540-local-feature-feedback.md) - encounter tools, lair, lair-action dialog, has-lair and selected-campaign viewer-access outcomes moved to managed regions; archive prepared on 1aa85334, publication/CI/acceptance pending.

<a id="current-state---2026-11-11"></a>

## Current state - 2026-11-12

009.1-009.6, coordinated 012, 018, 015 and accepted global units 4A.1-4A.13 remain
closed. Stage 2 remains closed on its separately recorded bounded acceptance and
green local evidence; [510](docs/handover/510-bulk-join-pane-feedback.md#stage-2-bounded-close-out---2026-11-12)
retains scope/evidence limits. Stage 1 is now explicitly accepted and closed,
including Step 2 (2A-2E) and Step 3, with covering CI and limits in
[530](docs/handover/530-setup-operation-feedback.md#stage-1-accepted-close-out---2026-11-12).
Earlier preparation/publication/acceptance-pending notes are historical, not current
blockers or a reason to request Stage 1 acceptance again.

Stage 3 local-feature/lair/selected-campaign viewer feedback integration is
prepared ([540](docs/handover/540-local-feature-feedback.md)) and awaits publication,
covering CI and acceptance.
Stage 4 integration/responsive/accessibility hardening, approved compatibility
retirement, Deliverable 1 acceptance, Deliverable 2 connection/recovery/polling/field
association and final 009.7/009 acceptance remain open under the
[current task plan](docs/todo/097-feedback-delivery-plan.md). Neither whole feedback
deliverable nor phase 009.7 is closed. No optional scope or new acceptance gates.
Test-suite cleanup stays deferred until after 009; 016/017 and SG-TODO-019 remain
proposed, not prerequisites. No merge/deployment or blanket future write approval.

This close-out changes documentation only and uses [skip ci]. No new application
checks, authenticated live-server, human visual, screen-reader or exhaustive
accessibility evidence is claimed; no workflow is changed or separately dispatched.
Historical index details and earlier CI/failure/correction identities remain in the
[pre-close-out index](https://github.com/dajomas/Scrying-Glass/blob/97eedc6da52abcfa94526fee25a3c321f0626844/HANDOVER.md)
and numbered handovers. Existing section links/order and the old current-state
anchor are retained.

## Maintenance

Update relevant numbered sections, preserve capitalization/ordering and links;
update this index when adding/renaming/reordering/removing sections. Follow
[maintenance rules](docs/handover/040-maintenance-rules.md) and live instructions;
never expand this index into a monolithic handover.
