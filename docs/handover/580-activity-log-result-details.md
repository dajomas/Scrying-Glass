# 580 - Activity log affected unit and resulting value

[Back to HANDOVER index](../../HANDOVER.md) · [SG-TODO-019 task](../todo/190-activity-log-result-details.md)

## Implementation - 2026-11-13

Status: implemented on `features/perplexity`; CI validation and user acceptance pending.
The user requested implementation and a GitHub push on 2026-11-13, after merging
`features/perplexity-009.7` back into `features/perplexity`.

### Behavior

Value-change Activity log entries now put the affected unit, the changed property
and its resulting value into the existing `note` field, shown in the Details column
and included unchanged in the CSV/JSON exports. The Target column and
`target_combatant_id` are unchanged.

| Producer | Action | Details format |
| --- | --- | --- |
| Battle Actions damage/heal (`apply_battle_actions`) | `damage`, `heal` | `Goblin - 2: HP 12 → 10/12[; temporary HP 4 → 0][; life state standing → down]` |
| Inline character/monster HP delta (`update_character`, `update_monster`) | `damage`, `heal` | same HP format |
| Lair action damage | `damage` | `Tremor; Hero: HP 24 → 12/24` (action name kept first) |
| Encounter-features edit | `combat-features` | `Cleric: HP 20 → 0; Life state standing → down` (label colons removed) |
| Death-save failure (battle, inline, lair) | `death-save-failure` | `Cleric: death-save failures now 1/3; damage at 0 HP[ (critical hit)]` |
| Attack statistic reduction | `statistic-reduced` | `Goblin: STR 12 → 10; source: Cleric`; Max HP reductions add the clamped `HP 12 → 7` |
| Restore / base statistics edit | `statistics-restore`, `statistics-bases` | existing prefix, then `; Goblin: Max HP 7 → 12; STR 10 → 12` |

HP results always show the new maximum. Each row describes its own target, so
multi-target batches and identically named species (`Goblin - 1`, `Goblin - 2`)
remain distinguishable. Several rows on one target each report their own
before/after values in submission order.

### Design and preserved behavior

- `python/scrying_glass_activity_details.py` only formats data. Callers take a
  plain snapshot before the operation they already perform; formatting does not
  mutate or re-apply anything.
- Handlers import the helper inside the function (the existing absolute
  `python.` pattern), so the class-only AST test loaders keep working. The new
  arguments are passed positionally to stay compatible with the existing test doubles.
- Combat rules, HP arithmetic, permissions, endpoints, payloads, storage schema
  and the Admin renderer are unchanged. Details are still escaped text. Existing
  log entries keep their original text; there is no migration.
- Unchanged (no value change): buff/debuff, effect added/removed/expired,
  concentration events and reminders, lair create/update/remove, undo, checkpoint
  restore and the instant-death note (it already states excess and maximum HP).
  No fragment, template, asset version or workflow changed.

### Tests

- New `tests/test_activity_log_result_details.py` has 15 tests. Seven are formatter
  tests. Eight use the real battle, inline-edit, features and statistics handlers
  with real SQLite storage, covering multiple goblins, a temporary HP pool,
  death-save failures, reductions/restores, persistence/reload and untouched history.
- New `tests/test_activity_log_result_render.py` (2, Playwright) renders
  handler-produced entries through the production `renderActivityLog` in the
  loaded Admin with intercepted HTTP, and checks escaping. This is not live-server evidence.
- Expected-text updates: `tests/test_feature_logging.py` (no label colons) and
  `tests/test_lair_damage_logging.py` (`Tremor; Hero: HP 24 → 12/24`).
- Negative control at `d20c3910`, with only the formatter module added: 8 of the
  17 new tests fail (all producer/render behavior tests). The formatter, buff and
  escaping tests pass as expected.

Local results (this environment, not CI): see the commit's validation summary in
the [TODO entry](../todo/190-activity-log-result-details.md#validation---2026-11-13).

### Limitations and pending

- CI has not been checked for this commit; no workflow-run identifier is recorded yet.
- No authenticated live-server, human visual or screen-reader review.
- Older entries are not rewritten; mixed old/new formats appear in existing logs.
- Notes are English text; the `amount` column remains the applied amount, not the result.
