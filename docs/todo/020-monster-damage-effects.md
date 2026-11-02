# 020 - Non-standard monster damage and mechanical effects

[Back to TODO index](../../TODO.md)

## SG-TODO-002 - Support non-standard monster damage and mechanical effects

- Status: in progress; attack-statistics increment and UI correction delivered as archives, live validation pending.
- Requested: 2026-11-01.
- Priority: not assigned.
- Owner: not assigned.
- Deadline: not assigned.
- Implementation and validation: attack-statistics increment implemented; current UI correction has mocked and Chromium fixture coverage. Broader automation and live validation remain open.

### Requested change

Track the proposed support for monster attacks that alter more than current HP, beginning with wight maximum-HP reduction and shadow Strength reduction. The user requested a TODO entry for the preceding design discussion, not implementation in this commit. The scope and sequencing below are proposals to refine before implementation, not separately approved implementation commitments.

### Proposed scope and sequencing

1. Structured mechanical effects: maximum-HP and ability-score reductions, separate base/effective statistics, effect removal and preset-specific recovery. Start with maximum HP and Strength; require a known base ability score rather than inventing one.
2. Compound attack resolution: typed damage components, manually entered saving-throw outcomes, conditional riders and linked attacker healing. Examples for source verification include wight/specter/wraith Life Drain, shadow drain and vampire/vampire-spawn bite.
3. Exceptional and recurring effects: healing prohibition, in-game-time recurring reductions, direct-to-zero HP, explicit death triggers and optional damage absorption. Examples for source verification include mummy rot, banshee Wail and clay golem abilities.

Use reusable mechanics composed by versioned attack presets rather than monster-name conditionals. Verify each preset against the selected stat block and rules edition; do not combine 2014 and revised rules. Keep dice, attack rolls, saves and mitigation GM-assisted unless a later scope explicitly adds automation.

### Design requirements to resolve

- Preserve base maximum HP and ability scores separately from active reductions. Retain effective values for the existing UI and health engine. Define editing/import behavior while reductions are active.
- Do not apply a maximum-HP reduction as a second damage event. Clamp current HP only when it exceeds the new effective maximum. Removing a reduction must not itself heal or resurrect a combatant.
- Define per-preset ordering and damage basis. Distinguish entered damage, resolved damage after agreed mitigation, temporary HP consumed and actual current-HP loss; do not assume the existing apply_hp result named damage is correct for every rider. Verify temporary-HP interactions against the chosen rules.
- Distinguish ordinary damage, direct-to-zero HP and explicit death. Preserve concentration cleanup, life-state transitions, death saves, reaction handling and battle-order continuity.
- Support recovery policies per effect, such as manual removal, qualifying rest, curse removal or specified restoration magic. Verify eligibility from the selected stat block rather than applying a universal rest rule.
- Advance recurring effects using explicit in-game time, not elapsed server wall-clock time.
- Resolve compound changes to target and source atomically, including persistence, grouped logging and undo. Validation or storage failure must not leave partial damage, reduction or attacker healing.
- Extend effect validation and normalized persistence with a migration and backup strategy. Include snapshots, campaign rosters, encounter/setup behavior and import/export compatibility.
- Provide a GM preview and show effective versus base statistics and active reductions. Preserve public/private effect filtering and avoid leaking private mechanics to the player display.

### Acceptance criteria

- [ ] Agree the first implementation increment and verify its versioned stat-block presets.
- [ ] Maximum-HP and Strength reductions can be applied, stacked, inspected and removed without losing base statistics. Missing ability scores produce a clear validation outcome.
- [ ] Save-dependent riders apply only on the required outcome, while ordinary damage is handled independently.
- [ ] Damage components can drive the correct rider and linked healing without using unrelated components.
- [ ] Maximum-HP reduction does not double-subtract damage; current HP respects the effective maximum. Effect removal neither heals nor resurrects by itself.
- [ ] Rest/recovery removes only qualifying effects; non-restoration effects survive ordinary healing and unrelated rests.
- [ ] Direct-to-zero effects do not masquerade as damage, consume temporary HP or trigger massive-damage death. Explicit death triggers use the selected preset's rules.
- [ ] Healing prohibition, recurrence and absorption are covered when their implementation increment is selected; explicit in-game time controls recurrence.
- [ ] Compound actions are atomic across all affected combatants and produce grouped audit/undo records.
- [ ] Reductions, base statistics and recovery metadata survive save/reload, snapshots, undo and supported campaign import/export; legacy data migrates safely.
- [ ] UI preview, base/effective values and public/private display behavior are verified.
- [ ] Existing ordinary damage/healing, temporary HP, death saves, concentration, initiative and reaction behavior remain covered by regression tests.

### Dependencies and validation plan

Inspect the current HP/effect rules, battle action schemas and handlers, feature service/storage, migrations, campaign bundles, reset/import paths and admin/client UI before implementation. The current effect validator permits descriptive and turn-timed effects but not the proposed mechanical fields; schema examples from the discussion must not be treated as implemented API contracts.

Add deterministic unit tests for stacking, recovery, rider amounts and order, damage versus HP-loss accounting, zero-stat/max-HP outcomes and bounds. Include integration tests for atomic rollback, migrations, persistence, snapshots, undo and import/export. Add UI tests for manual save outcomes, preview, effective/base statistics and visibility. Verify representative presets against their cited stat blocks during implementation, and distinguish mocked/offline checks from live-server validation.

The original TODO entry was documentation-only; subsequent archive deliveries implement the attack-statistics increment described below. No owner, priority or deadline is agreed.

### Related handover

See [TODO tracking and documentation-only delivery scope](../handover/100-todo-tracking.md).


### Current increment and UI correction — 2026-11-02

The user selected attack-window reduction rows with target, statistic (Max HP and
all six abilities) and amount, plus Restore statistics beside Reset. This replaces
the earlier Encounter tools design. The attack increment includes bases, manual
stacking/recovery, transactional persistence, undo/checkpoints/bundles and privacy.
Preset/edition verification is deferred for the manual-only increment.

The readability correction adds:

- [x] A readable affected-only restore table and matching filtered choices.
- [x] Show zero-valued statistics while reductions remain; omit unknown/unaffected
  abilities. Disable restore and show an empty message when no reductions remain.
- [x] Keep original-score setup in a separate editor, not the restore table.
- [x] Run mocked interaction tests and a Chromium responsive-layout fixture.
- [ ] Check the user's live running theme and authenticated restoration flow.

The backend/attack suites reported for the prior increment were not rerun for this
UI-only change. No new CI/commit outcome is claimed. Broader monster automation,
save/rider handling, linked healing, automatic recovery, special death/zero rules,
recurrence, prohibition and absorption remain open. See [UI handover](../handover/190-statistics-restoration-layout.md)
and [attack handover](../handover/180-attack-statistics-delivery.md). Do not mark the
whole SG-TODO-002 complete.


### CI feedback — backup connection cleanup, 2026-11-02

Run 41452426944 attempt 1 tested 14404e34828ed5e4fed6828245250aaa348b4396.
The functional suites passed, but connection auditing detected one unclosed backup
reader in test_v7_backup. The corrective archive uses contextlib.closing without
weakening assertions or changing application behavior.

- [x] Prepare explicit-close fix and isolated success/failure-path resource tests.
- [x] Run both isolated checks against fixed source and confirm they detect the
  original leak when run as negative controls.
- [ ] Rerun the actual test_attack_statistics module and full connection audit in
  the complete checkout; require zero connections without explicit close.
- [ ] Verify the corrected implementation in a new CI run; the old run remains failed.

See [CI correction handover](../handover/180-attack-statistics-delivery.md). This
does not complete SG-TODO-002 or implement the separate SG-TODO-003 Next shortcut.
