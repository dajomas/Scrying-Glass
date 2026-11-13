# 360 - Battle Actions combatant statistics

[Back to handover index](../../HANDOVER.md)

Updated: 2026-11-09. Task: [SG-TODO-015](../todo/150-battle-actions-combatant-statistics.md). Status: completed and closed after covering CI, explicit user sign-off and the user's request to commit the TODO close-out.

## User workflow

In Battle Actions, selecting a Target shows its available AC, HP and HP MAX immediately beneath that dropdown. Reaction source has an independent summary; reaction targets and statistics-reduction targets use the same behavior. Missing fields are omitted, not filled with invented zeroes; actual numeric zero remains visible. The figures are current Admin-state fields, not original/base HP, temporary HP, provider values or player-projection visibility flags. No extra edits or saves are introduced.

Cleared selection, deleted combatants and entirely unavailable statistics leave no summary. Same-scope state refresh updates displayed figures, including after Apply, without changing pending selections/amounts, existing Applied locks or submit behavior. Closing/reopening creates fresh empty summaries. A campaign/setup change suppresses summaries from the old modal session, complementing the existing statistics module's scope-close behavior. Native eligibility and resolution remain authoritative.

## Implementation and compatibility

static/battle-action-statistics.js and .css load after existing enhancements in 190_document_end.html. The module uses original selectors/labels, adds a text-only paragraph immediately after each target/source select, and preserves existing aria-describedby references. Each summary is a polite atomic status region. Where no explicit selector name exists, Target/Reaction source aria-label preserves that name instead of letting statistics become part of the label. Existing explicit aria-label/labelledby is retained.

A WeakMap owns one summary per selector and monotonically assigned IDs avoid collisions. Delegated changes and row/option observers cover dynamic rows and selection updates; observers disconnect around their own render to avoid recursive DOM churn. Modal visibility tracks sessions. The module composes scryingLairsRender, preserving original context/arguments/return, to consume authoritative load snapshots; it catches up from latest when initial load already completed. It filters to finite numeric ac/hp/max_hp and checks campaign/setup identity. Missing roots leave prior UI intact; installation is guarded. No fetch/polling, input/selection/disabled writes, cloned/replaced controls or action serialization changes.

No backend, API, permissions, SQLite, provider, combat rules or initiative behavior changes. Eight Admin source fragments, assembly adapter and tracked failure marker remain unchanged. Preserve 009.5 closure and the user's cfc7b0f1 lookup wording. Deploy matching template/static files, restart the correct process for assembled HTML and reload Admin; no migration/configuration change.

## Alignment correction - 2026-11-09

The user reported misalignment after selector statistics were added. Live inspection confirmed the summary was already inside the selector's existing label, not a separate action-row grid item. The previous assistant's wrapper diagnosis/preparation was not a delivered change. The correction delivered in d8f4f57b26325623fa662388102094cc1cb35fcd uses CSS only: shared label/control/summary tracks via row subgrid, equal 2.5rem control heights, Critical hit and Remove on the control track, and Applied on its own full-width track. Target and Reaction source summaries stay directly below their original selectors, including wrapped or missing summaries. At 700px and below, natural single-column field stacking resumes. No wrappers, JavaScript/control moves, handlers, drafts, disabled states or action payload changes are introduced. Modern-browser CSS subgrid is used.

## Preparation history and regression scope

Preparation included JavaScript syntax, CSS parsing and Python AST checks, plus isolated Chromium tests of summary behavior and ordinary/reaction geometry at 1440/375. Those synthetic checks were not full-Admin/backend verification. The detailed dated preparation record, including exact file sizes and originally pending gates, is retained in the [pre-close-out handover](https://github.com/dajomas/Scrying-Glass/blob/1214020a14e9e99b75a9ce8444eb7ce6051b2671/docs/handover/360-battle-actions-combatant-statistics.md). Its pending-CI/acceptance wording is superseded by the close-out below, not retroactively claimed as results available during preparation.

tests/test_battle_action_statistics.py uses the assembled Admin/intercepted-HTTP fixture and production assets/native helpers for ordinary/reaction/reduction selectors, independent rows, selection clearing, missing/invalid/zero/deleted values, idempotence, expected Apply JSON, refreshed locked drafts, reopen, scope suppression, removal and desktop/narrow summary placement/descriptions. tests/test_battle_action_alignment.py adds desktop control geometry for empty/selected/longer summaries, reaction/reduction rows and hidden critical/amount fields, plus narrow field grouping. The existing workflow discovers these test modules and uploads configured visual fixtures; no workflow changes were needed.

## Close-out - 2026-11-09

- Implementation/alignment SHA: d8f4f57b26325623fa662388102094cc1cb35fcd on features/perplexity.
- Covering workflow: Branch tests, run 42624239041, attempt 1; run.json confirms completed/success on that exact SHA and branch.
- Publication SHA: 1214020a14e9e99b75a9ce8444eb7ce6051b2671.
- Evidence directory: [ci-results-42624239041-attempt-1](../../ci-results-42624239041-attempt-1/).
- Reviewed evidence: [run.json](../../ci-results-42624239041-attempt-1/run.json) and [jobs.json](../../ci-results-42624239041-attempt-1/jobs.json). The job report confirms successful syntax/server import, Python suite including browser fixtures, pytest regression modules, JavaScript tests, standalone Python browser/audit checks and visual-artifact upload.
- User acceptance: explicit SG-TODO-015 sign-off on 2026-11-09, followed by a request to update and commit the TODO list with skip CI.

The covering-CI and task-specific user-acceptance gates are resolved for the agreed scope. CI job metadata and intercepted fixtures are not password-login, live TCP/provider, process-restart or exhaustive accessibility verification; user sign-off is not an invented checklist of individually performed manual checks. No new tests are executed for this documentation-only close-out. The proposed commit contains [skip ci]; no workflow is modified or separately dispatched and no close-out workflow outcome is inferred.

The TODO index/task and handover index/section are updated together. README was reviewed and left unchanged because runtime/deployment descriptions remain accurate. The dated sequence document remains a historical agreement; its order is unchanged. Overall 009 remains in progress and 009.6/009.7 remain proposed. 009.6 is next in the agreed sequence; this close-out neither starts it nor approves an implementation payload. No unrelated task is closed.
