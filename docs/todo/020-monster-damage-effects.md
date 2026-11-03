# 020 - Attack statistics reductions and restoration

[Back to TODO index](../../TODO.md)

## SG-TODO-002 - Manual attack statistics reductions and restoration

- Status: completed.
- Requested: 2026-11-01; agreed manual attack-screen scope refined 2026-11-02.
- Completed: 2026-11-02, at the user's request following their green-CI confirmation.
- Priority: not assigned.
- Owner: not assigned.
- Deadline: not assigned.
- Completion basis: delivered manual feature, restoration/layout correction and
  connection-cleanup correction; CI success reported by the user on 2026-11-02.

### Completed scope

The agreed implementation places Add statistics reduction in the Battle Actions
modal. Each row selects a target, Max HP or one of STR/DEX/CON/INT/WIS/CHA, and a
positive amount. Reductions resolve in order with the attack's damage/healing
rows. Original/base values remain separate from effective statistics; unknown
ability scores must be supplied rather than guessed. Reductions stack, persist
and recover manually, without duplicating damage or inferring monster-specific
consequences at zero.

Restore statistics beside character Reset (also available for monsters) restores
one or all affected statistics without healing current HP or reviving a creature.
Its readable table and selector show only affected statistics; original/base score
editing is a separate view. Persistence, transactions/audit, undo/checkpoints,
setups/rosters, reload, bundles and private player filtering are integrated.
The backup-reader explicit-close test correction is included in this delivered
feature's CI feedback history.

### Completion checklist — agreed manual scope

- [x] Battle Actions reduction rows: target, seven supported statistics and amount.
- [x] Ordered attack-batch resolution and applied-row replay protection.
- [x] Separate original/base/effective values, stacking and unknown-score validation.
- [x] Max-HP clamping without a second damage event or automatic special death rule.
- [x] Manual restoration beside Reset without healing/resurrection.
- [x] Affected-only restore table/options and a separate original-score editor.
- [x] Persistence, audit/undo/checkpoints, import/export and privacy integration.
- [x] Focused/regression/UI tests and the backup connection-cleanup correction.
- [x] User reported the CI workflow finished green and requested task completion.

### Validation provenance and completion decision

On 2026-11-02 at 14:47 CET the user stated: "The CI workflow finished green" and
explicitly requested completion of SG-TODO-002. This status update records that
confirmation; the successful run's ID, tested SHA and logs were not supplied in
this request and were not independently inspected for this documentation delivery.
No successful run number, new test counts or commit SHA is invented.

The previously analyzed run 41452426944 attempt 1 at
14404e34828ed5e4fed6828245250aaa348b4396 remains a historical FAILED run. It passed
the functional suites but found one backup connection without explicit close;
its outcome is not relabelled green. The follow-up correction wrapped that reader
in contextlib.closing and added isolated closure checks. The user's later green-CI
confirmation supersedes the task's pending-CI status and closes the agreed scope.

No tests or workflows were run for this documentation-only completion update.
A green configured workflow is not a claim that every possible deployment,
production-data migration or authenticated manual scenario was independently
verified here. Such operational checks remain prudent deployment practice, not
an assertion of unperformed testing or an open status for this accepted scope.

### Deferred ideas outside the completed scope

The original proposal also discussed versioned monster presets/rules editions,
automatic/preset recovery, save-dependent riders, typed compound damage, linked
attacker healing, direct-to-zero and explicit special death rules, recurrence,
healing prohibition and absorption. These are NOT implemented or validated by
marking this manual task complete. They are retained as future-work proposals
requiring separately agreed follow-up scope; no owner/deadline or new task ID is
invented for them. The historical design below preserves their details.

SG-TODO-001 remains proposed. SG-TODO-003 (Next inside Battle Actions) remains
proposed and is neither implemented nor completed by this update.

### Related documentation

- [Attack statistics and completion handover](../handover/180-attack-statistics-delivery.md)
- [Affected-only restoration layout](../handover/190-statistics-restoration-layout.md)
- [Next-button proposal](030-battle-actions-next.md)

## Historical proposal and delivery notes — superseded status

The material below is retained verbatim from the preceding task section for
traceability. Its former statuses, unchecked broad-design criteria and instructions
not to close the task describe earlier stages. They are not the current acceptance
criteria for the manual scope completed above. Deferred mechanics remain proposals,
not features silently marked done. Use the completion record above as authoritative.

<details>
<summary>Original broader proposal and pre-completion implementation/CI notes</summary>

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

</details>
