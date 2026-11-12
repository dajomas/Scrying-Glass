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

## Current state - 2026-11-11

018, 009.5, 015 and 009.6 remain closed for accepted scopes; 340/350/360/370 retain
all CI, failure/correction, manual-check, publication/merge identities and limits.
009.7/both feedback deliverables remain open; 4A.1-4A.13 bounded units are closed.
4A.11 evidence, failures/corrections and acceptance limits remain in
[440](docs/handover/440-battle-action-global-feedback.md).
4A.12 implementation 981ffe61a9bb4da162944707b42132d384eea1ad is covered by
successful Branch tests 42949763708 attempt 1, job 130291065704; publication
488997aacb50ed44d785c9738457fab1b854ad90. Detailed Join/server/browser/source
results were reconciled after the user's 2026-11-11 close-out request; no blocking
failure was found in reviewed evidence. Bounded acceptance closes 4A.12 only.
[450 evidence and limits](docs/handover/450-join-reporting.md#4a12-bounded-close-out---2026-11-11);
[task plan](docs/todo/097-feedback-delivery-plan.md).

4A.13 is closed for the accepted bounded global reconciliation scope following
reviewed covering CI and the user's 2026-11-11 finish request. Final tested revision
413822d82bc1dd5894b139946b5caf054e24f39d has successful Branch tests 42973631914
attempt 1, job 130367559943; publication 6c77d9fe069fffc34dd3335294e20ea90e8097f9.
Direct review confirms all eight reconciliation cases, four complete-Admin Chromium
scenarios, three inventory methods and corrected header-layout test passed; all
main stages succeeded. Failed runs 42969807025 and 42971464667 are preserved with
both test corrections. Global compatibility is retired; explicit global feedback
and pane compatibility remain. The 19-identity/171-pair matrix is API coverage,
not 171 actual handler combinations. [470 close-out/evidence/limits](docs/handover/470-global-feedback-close-out.md)
supersedes older pending/blocked 4A.13 notes in 460/465/467 while retaining history.

This documentation-only close-out uses [skip ci], executes no new tests and changes
or dispatches no workflow. No new human visual/manual, screen-reader, authenticated
live-server or exhaustive accessibility acceptance is inferred. Local producer/pane
integration, D2 connection/recovery/polling/field association and wider 009.7 gates
remain open. Neither feedback deliverable nor phase 009.7 closes. No prior bounded
acceptance or agreed order changes. README and TODO root remain unchanged.
016/017 and SG-TODO-019 remain proposed. No merge/deployment.
Longer index history is preserved in the [pre-checkpoint index](https://github.com/dajomas/Scrying-Glass/blob/9d05e129cc2b85099cf0e3bf394a1fe398d0af24/HANDOVER.md)
and numbered sections, not deleted acceptance evidence.

## Maintenance

Update relevant numbered sections, preserve capitalization/ordering and links;
update this index when adding/renaming/reordering/removing sections. Follow
[maintenance rules](docs/handover/040-maintenance-rules.md) and live instructions;
never expand this index into a monolithic handover.
