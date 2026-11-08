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

## Current validation status - 2026-11-08

SG-TODO-018 remains open pending overall close-out reconciliation. Do not push the rejected close-out draft. Follow the [correction plan](docs/todo/185-monster-correction-plan.md). A.1 remains accepted; the user manually tested and signed off A.2 and A.3 on 2026-11-08. Their covering corrective CI 42517614512 attempt 1 succeeded for exact 1c289d485bffcf8197fb32238349729e52b822ed.

Stage B corrective automated validation is now satisfied: Branch tests 42526295799 attempt 1 completed successfully on features/perplexity-018 for exact f5808a2dfbc9b8d8bd4de9706956dbe8312815a5. Published evidence: 790a32b0f86eb60a86319d7c3158f9a7c22f489b, ci-results-42526295799-attempt-1. The workflow log explicitly records test_primary_centres_and_compact_status_after_refresh as OK. The user confirmed the roster visual check successful on 2026-11-08. This is user-reported visual acceptance, not assistant-executed live-server or persistence verification, and does not independently enumerate every workflow acceptance check. These current CI/visual statuses supersede the earlier pending statements in [310](docs/handover/310-admin-rosters.md), [340](docs/handover/340-combined-monster-lookup.md) and [185](docs/todo/185-monster-correction-plan.md); their delivery-time evidence and remaining workflow criteria stay historical/actionable respectively. Failed run 42525208958 remains failed. No overall completion, merge or other-branch write is authorized by this update.

This update changes documentation only. No new tests are executed, no workflow is edited or dispatched, and no new workflow outcome is inferred. The commit message contains [skip ci].

## Required update convention

All future handover additions must follow the same indexed structure: update the relevant existing section or create a numbered Markdown file under `docs/handover/`, and update this index in the same commit. Read the [maintenance rules](docs/handover/040-maintenance-rules.md) before making changes.
