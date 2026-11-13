# 580 - Activity log affected unit and resulting value

[Back to HANDOVER index](../../HANDOVER.md) · [SG-TODO-019 task](../todo/190-activity-log-result-details.md)

## SG-TODO-019 accepted close-out - 2026-11-13

Status: completed and closed for the agreed Activity log Details scope after the
user's explicit final acceptance/close-out request on 2026-11-13 at 09:04 CET:
"Proceed with final acceptance and close out SG-TODO-019". This supersedes earlier
CI/acceptance-pending notes; no further SG-TODO-019 acceptance request remains.
009/009.7 and all earlier accepted scopes remain closed and are not reopened.

Implementation: 4a1feb47654ea6665862ec44b3f52dc6a27458b8 on
features/perplexity. Successful covering Branch tests 43386246710 attempt 1,
job 131755311158; evidence publication 5b1a0a6270adea9e67ca9ffd1def534b875f1317,
directory ci-results-43386246710-attempt-1. Reviewed run.json/jobs.json agree on
branch, tested SHA, attempt, completed status and success. All configured Chromium
provisioning, syntax/import, main Python/browser, pytest regression, JavaScript and
standalone browser/audit stages succeeded. Run completion: 2026-11-13T07:40:39Z
(08:40 CET). This review did not individually re-review every test log/screenshot or
recount CI tests. Local preparation counts below are not promoted into CI totals.

Accepted scope and boundaries are detailed below and in [190](../todo/190-activity-log-result-details.md#coverage-decisions---2026-11-13):
affected unit/property/result in the existing Details/note field and exports for the
listed value-change producers; no mutation replay, schema/renderer change or rewrite
of older entries. Existing event-note exclusions and mixed old/new history remain.
No new authenticated live-server, human visual, screen-reader or exhaustive manual
verification is inferred; the user accepted the bounded feature on stated evidence.

This documentation-only close-out uses [skip ci], runs no new tests and changes/
dispatches no workflow. No application, tests, templates, assets, pins, schema,
permissions or source-assembly changes; no merge/deployment, new scope, owner,
deadline or blanket future write approval. No new commit SHA/run outcome is invented
before publication. No agreed SG-TODO-019 implementation/CI/acceptance action remains.

## Implementation - 2026-11-13

Implemented and published as the tested revision above; now accepted and closed.
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
- Unexpanded event notes: buff/debuff, effect added/removed/expired, concentration
  events/reminders, lair create/update/remove, undo, checkpoint restore and the
  instant-death note (it already states excess and maximum HP). Undo/restore do not
  gain per-value difference reports; this does not assert that they never change
  values. No fragment, template, asset version or workflow changed.

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

Historical local preparation results (not hosted CI and not rerun for this close-out)
remain in the [TODO validation entry](../todo/190-activity-log-result-details.md#validation---2026-11-13).
CI configuration at the tested SHA was reviewed and discovers test_*.py through the
assembled runner; CI success is recorded above without invented per-test totals.

<a id="limitations-and-pending"></a>

### Limitations

- No authenticated live-server, human visual or screen-reader review is newly claimed.
- Older entries are not rewritten; mixed old/new formats appear in existing logs.
- Notes are English text; the `amount` column remains the applied amount, not the result.
- Accepted coverage excludes new per-value reports for undo/checkpoint restore and
  the other event notes listed above. No extra coverage requirement is added now.

The former pending-CI limitation is superseded by the reviewed green covering run
and explicit final acceptance. This preserves limitations without leaving a false
outstanding SG-TODO-019 acceptance/CI action.
