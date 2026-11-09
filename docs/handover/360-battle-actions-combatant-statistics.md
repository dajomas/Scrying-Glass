# 360 - Battle Actions combatant statistics

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-015](../todo/150-battle-actions-combatant-statistics.md). Status: implementation prepared for GitHub delivery; covering full-Admin execution/CI and user acceptance pending. No completed status, implementation commit SHA or workflow outcome is claimed before it exists.

## User workflow

In Battle Actions, selecting a Target shows its available AC, HP and HP MAX immediately beneath that dropdown. Reaction source has an independent summary; reaction targets and statistics-reduction targets use the same behavior. Missing fields are omitted, not filled with invented zeroes; actual numeric zero remains visible. The figures are current Admin-state fields, not original/base HP, temporary HP, provider values or player-projection visibility flags. No extra edits or saves are introduced.

Cleared selection, deleted combatants and entirely unavailable statistics leave no summary. Same-scope state refresh updates displayed figures, including after Apply, without changing pending selections/amounts, existing Applied locks or submit behavior. Closing/reopening creates fresh empty summaries. A campaign/setup change suppresses summaries from the old modal session, complementing the existing statistics module's scope-close behavior. Native eligibility and resolution remain authoritative.

## Implementation and compatibility

New static/battle-action-statistics.js and .css load after existing enhancements in 190_document_end.html. The module uses original selectors/labels, adds a text-only paragraph immediately after each target/source select, and preserves existing aria-describedby references. Each summary is a polite atomic status region. Where no explicit selector name exists, Target/Reaction source aria-label preserves that name instead of letting statistics become part of the label. Existing explicit aria-label/labelledby is retained.

A WeakMap owns one summary per selector and monotonically assigned IDs avoid collisions. Delegated changes and row/option observers cover dynamic rows and selection updates; observers disconnect around their own render to avoid recursive DOM churn. Modal visibility tracks sessions. The module composes scryingLairsRender, preserving original context/arguments/return, to consume authoritative load snapshots; it catches up from latest when initial load already completed. It filters to finite numeric ac/hp/max_hp and checks campaign/setup identity. Missing roots leave prior UI intact; installation is guarded. No fetch/polling, input/selection/disabled writes, cloned/replaced controls or action serialization changes.

No backend, API, permissions, SQLite, provider, combat rules or initiative behavior changes. Eight Admin source fragments, assembly adapter and tracked failure marker remain unchanged. Preserve 009.5 closure and the user's cfc7b0f1 lookup wording. Deploy matching template/static files, restart the correct process for assembled HTML and reload Admin; no migration/configuration change.

## Executed preparation

- Node --check passed for the complete new 4,137-byte JavaScript module.
- Stylesheet parsing passed for the complete 350-byte stylesheet.
- Python AST parsing passed for the complete 9,891-byte regression module (six methods: one source contract and five browser methods).
- Simplified real Chromium fixtures passed partial/zero statistics, independent target/source selection, clearing, refreshed fields, scope suppression, retained draft, preserved prior-hook return and idempotence, with no page errors. Further fixtures at 1440/375 passed dynamic insertion, all-zero values, existing description preservation, below-selector geometry, disabled/draft retention and row removal, with no page errors.

These browser checks load the actual new module but use synthetic minimal DOM/state and representative grid CSS, not the whole application or backend. They do not validate real Apply, native row builders, authenticated state, full modal layout or live-server behavior.

## Prepared full-Admin regressions and CI

tests/test_battle_action_statistics.py reuses the existing assembled Admin/intercepted-HTTP fixture with production assets and native open/row/Apply helpers. It checks ordinary/reaction/reduction selectors, independent rows, initial/cleared selection, character/monster values, partial/invalid/zero/deleted data, idempotence, expected Apply JSON, refreshed locked-row/draft retention, reopen, scope suppression, row removal and desktop/narrow selector-summary geometry/descriptions. Two 015-WIDTH-summaries.png fixtures write to SG_VISUAL_ARTIFACTS for existing artifact collection. 

The complete new full-Admin regression module, existing suite and covering CI were not executed during preparation. Actual .github/workflows/tests.yml discovers test_*.py, JavaScript scripts and standalone browser/audit checks and uploads the configured visual directory; no workflow changes are needed. Normal CI applies to this mixed delivery. Fixture capture/upload is not user visual acceptance.

## Remaining gates and reviewed documentation

Review covering CI/test outcomes, screenshot appearance and user desktop/narrow operation; preserve existing Apply/Next/turn/row/security assertions if corrections are needed. Require task-specific user acceptance before closure. No password-login, real TCP session, provider, process restart or exhaustive accessibility audit has been performed here.

README/User Guide and existing indexed docs were reviewed/reused; existing combat contracts remain accurate without edits. This section documents the additive user workflow. HANDOVER.md gains this numbered section and current 015 state; TODO/task status changes accompany the feature. No unrelated 009.6/009.7 or source-integration work is included.
