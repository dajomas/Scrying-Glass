# Scrying Glass handover

This file is the handover index. Detailed sections live in `docs/handover/`; do not expand this index into a monolithic handover document.

## Index

1. [Scope and current state](docs/handover/010-scope-and-state.md)
2. [CI workflow and test coverage](docs/handover/020-ci-and-tests.md)
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

34. [5e.tools initiative extraction correction: A.1 accepted, historical A.2 preparation](docs/handover/335-fivetools-initiative-correction.md)
35. [Combined lookup, Refresh and roster correction delivery/validation](docs/handover/340-combined-monster-lookup.md)
36. [Admin workflow navigation: closed after CI and user sign-off](docs/handover/350-admin-workflow-navigation.md)
37. [Battle Actions combatant statistics: closed after CI and user sign-off](docs/handover/360-battle-actions-combatant-statistics.md)
38. [Focused live encounter workspace: closed after corrective CI and renewed sign-off](docs/handover/370-live-encounter-workspace.md)
39. [Feedback delivery plan and continuity](docs/handover/380-feedback-delivery-plan.md)
   - [State-load feedback: bounded 4A.1 acceptance](docs/handover/385-state-load-feedback.md)
40. [Reset-all feedback: scoped 4A.6 delivery and validation](docs/handover/390-reset-all-feedback.md)
41. [Individual combatant reset feedback: scoped 4A.7 delivery and validation](docs/handover/400-individual-reset-feedback.md)
42. [Global removal fallback feedback: scoped 4A.8 delivery and validation](docs/handover/410-global-removal-fallback-feedback.md)
43. [Activity-log clear feedback: scoped 4A.9 delivery and validation](docs/handover/420-activity-log-clear-feedback.md)

## Current validation status - 2026-11-09

SG-TODO-018 is completed and closed at the user's explicit request after review of the remaining actions. A.1/A.2/A.3 acceptance remains; corrective CI 42526295799 attempt 1 and the user's successful roster visual check cover the final correction. See the [completed contract](docs/todo/180-monster-initiative-bonus.md), [reconciled correction plan](docs/todo/185-monster-correction-plan.md) and [close-out evidence and limitations](docs/handover/340-combined-monster-lookup.md#sg-todo-018-close-out---2026-11-08). The completed branch was subsequently merged into features/perplexity at b0630effbe99db8a40b27bb00cca007b198d4055; the earlier close-out itself did not perform that merge. No new merge-CI result is claimed here.

SG-TODO-009.5 is completed/closed on the user's 2026-11-09 sign-off and request to close. Successful CI 42616924220 attempt 1 covers c7c51725, including the form/overwrite/copy refinements. The accepted later manual copy revision cfc7b0f1 updates template and matching test expectation; no separate covering CI result for that revision was supplied. See [350](docs/handover/350-admin-workflow-navigation.md) for historical evidence and limits. Overall SG-TODO-009 remains in progress; phases 009.1-009.6 are closed and 009.7 preparation is authorized at the user's request.

SG-TODO-015 is completed/closed after successful CI 42624239041 attempt 1 covering d8f4f57b26325623fa662388102094cc1cb35fcd on features/perplexity, including the alignment correction, and the user's explicit 2026-11-09 sign-off and TODO close-out request. Evidence was published at 1214020a14e9e99b75a9ce8444eb7ce6051b2671 under ci-results-42624239041-attempt-1. See [360 close-out and evidence limits](docs/handover/360-battle-actions-combatant-statistics.md#close-out---2026-11-09). The documentation-only close-out included [skip ci] and claimed no new test execution.

SG-TODO-009.6 is completed/closed on renewed user sign-off and explicit close/move-on request, 2026-11-09. Successful corrective Branch tests 42654298154 attempt 1 covers e512dd24a42dde0141193e860b383125248f2f06 on features/perplexity, published at a7c7614f23acb7a502c3e8c48f579faacfe1fc12 under ci-results-42654298154-attempt-1. All configured validation stages passed. The earlier failed run 42649656592 remains failed; the window-global fixture correction and subsequent success resolve that gate. See [370 close-out](docs/handover/370-live-encounter-workspace.md#sg-todo-0096-close-out---2026-11-09) for accepted scope, revocation/renewal history and evidence limits.

SG-TODO-009.7 remains in progress/open. The user approved a two-deliverable feedback split and requested that the seven Deliverable 1 steps and Deliverable 2 target be stored before starting step 1. See the [current delivery plan](docs/todo/097-feedback-delivery-plan.md) and [continuity record](docs/handover/380-feedback-delivery-plan.md). These supersede earlier pending-policy/inspection-only wording, but deliver no application implementation or changed runtime message-expiry behavior. This documentation-only commit includes [skip ci], runs no automated tests and does not modify or dispatch a workflow. 016/017 remain proposed after 009.7.

## Required update convention

All future handover additions must follow the same indexed structure: update the relevant existing section or create a numbered Markdown file under `docs/handover/`, and update this index in the same commit. Read the [maintenance rules](docs/handover/040-maintenance-rules.md) before making changes.
