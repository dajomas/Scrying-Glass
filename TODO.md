# Scrying Glass TODO

This file is the task index. Detailed tasks live in numbered Markdown sections under `docs/todo/`; do not expand this index into a monolithic backlog.

## Index

1. [Monster lookup accounts and candidate selection](docs/todo/010-monster-lookup.md) - SG-TODO-001, completed (agreed public-provider candidate-selection scope; verified green CI and user-confirmed manual checks, 2026-11-02).
2. [Attack statistics reductions and restoration](docs/todo/020-monster-damage-effects.md) - SG-TODO-002, completed (agreed manual scope; user-confirmed green CI, 2026-11-02).

3. [Next combatant from Battle Actions](docs/todo/030-battle-actions-next.md) - SG-TODO-003, completed (verified green corrective CI; user-requested close-out, 2026-11-02).
4. [Cancelled D&D Beyond account access](docs/todo/040-dndbeyond-account-access.md) - SG-TODO-004, cancelled (user concluded the investigated integration options were not viable for this project; no account-backed implementation delivered, 2026-11-03).
5. [Initial Admin section visibility](docs/todo/050-admin-initial-visibility.md) - SG-TODO-005, completed (dependent-button correction delivered; covering CI verified; user-requested close-out, 2026-11-03).
6. [5e.tools sources and descriptive names](docs/todo/060-fivetools-source-configuration.md) - SG-TODO-006, completed (configuration and notification/popup labels delivered; combined CI verified; user-requested close-out, 2026-11-03).
7. [Single-line monster buttons](docs/todo/070-monster-button-layout.md) - SG-TODO-007, completed (original closure 2026-11-03; subsequent Turn-control removal has verified local/CI results and user acceptance, 2026-11-06).
8. [Source-size refactors](docs/todo/080-source-size-refactors.md) - SG-TODO-008, completed (Admin and Storage accepted by user; no code above the existing-file allowance, 2026-11-03).
9. [Admin usability and visual redesign](docs/todo/090-admin-usability-redesign.md) - SG-TODO-009, in progress (009.1-009.4 closed; 009.4 and coordinated 012 accepted after covering local/CI verification; 009.5-009.7 remain proposed, 2026-11-06). See [roster close-out](docs/handover/310-admin-rosters.md).
10. [HTTPX2 test migration](docs/todo/100-httpx2-test-migration.md) - SG-TODO-010, completed (verified successful local run and covering CI run 42205835274 attempt 1; user-requested close-out, 2026-11-06).
11. [Add Monsters image previews](docs/todo/110-monster-image-previews.md) - SG-TODO-011, completed (corrective local validation and CI run 42251417154 attempt 1 verified; user visual/workflow acceptance and close-out request, 2026-11-06).
12. [Admin delivery sequence](docs/todo/115-admin-delivery-sequence.md) - current remaining-work order agreed 2026-11-06: 018; 009.5; 015; 009.6; 009.7; coordinated 016/017 workstream. Earlier agreement/proposal retained as linked history; sequencing does not start or complete tasks.
13. [Character HP editor consistency](docs/todo/120-character-hp-editors.md) - SG-TODO-012, completed (option 2: read-only roster HP and Edit-dialog editing; covering local/CI verification and explicit user acceptance/close-out, 2026-11-06).
14. [Initiative keyboard navigation](docs/todo/130-initiative-keyboard-navigation.md) - SG-TODO-013, completed (user-directed feature acceptance retained; corrective commit 3709341 has verified successful local suite/audit and CI run 42292006888 attempt 1; validation exception resolved, 2026-11-06).
15. [Add Monsters source help text](docs/todo/140-monster-source-help-text.md) - SG-TODO-014, completed (covering CI run 42261491777 attempt 1 verified; user completion request and wording acceptance recorded, 2026-11-06).
16. [Battle Actions combatant statistics](docs/todo/150-battle-actions-combatant-statistics.md) - SG-TODO-015, proposed (show available AC, HP and HP MAX below the selected target and Reaction source dropdowns, 2026-11-06).
17. [Source-based monster selection](docs/todo/160-source-based-monster-selection.md) - SG-TODO-016, proposed (source dropdown defaulting to None and a dependent dropdown of all available monsters from the selected source, 2026-11-06).
18. [Open5e API monster source](docs/todo/170-open5e-monster-source.md) - SG-TODO-017, proposed (add Open5e.com through its API as a monster source, 2026-11-06).
19. [Monster initiative bonus](docs/todo/180-monster-initiative-bonus.md) - SG-TODO-018, in progress on features/perplexity-018; user declined close-out after reporting provider/UI defects, 2026-11-08. Implementation corrections and acceptance remain pending; the earlier foundation-only summary is historical.
20. [Monster provider and roster correction plan](docs/todo/185-monster-correction-plan.md) - SG-TODO-018 follow-up and adjacent lookup/roster actions, planned (provider extraction, combined-source search and single-candidate Refresh first; compact/consistent roster presentation second; validation and acceptance before close-out, 2026-11-08).

## Maintenance

Follow `PERPLEXITY_INSTRUCTIONS.md`. Add or update task details under `docs/todo/`, preserve stable task identifiers, and update this index in the same commit when sections are added, renamed, removed or reordered. Every section must link back to this index. Do not mark tasks complete before their acceptance criteria and required validation are satisfied.
