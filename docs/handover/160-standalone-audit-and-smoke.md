# 160 - Standalone audit and smoke fixtures

[Back to handover index](../../HANDOVER.md)

Last updated: 2026-11-01. Preparation baseline: `e70ca3a63de7cfe03fef116e157b832904517d0d`.

## Observed failures

Run 41320226799, attempt 1, tested `8dc2a0f239699935432c126fbdc5ca6433e73b90`. Main unittest, pytest and JavaScript stages passed; the standalone step failed on two scripts. The connection audit rediscovered 889 passing tests but found three connections without explicit close among 611 allocations. Browser smoke failed at the Default campaign-heading assertion after its card assertions succeeded.

## Explicit SQLite closure

Pinned source inspection located two nonclosing in-memory connections in `test_bughunt_210aac8.py` (Unicode roundtrip and surrogate binding) and one executed connection in `test_bughunt_3d5b2d4.py` (last-valid-round binding). SQLite's connection context manager controls a transaction but does not explicitly close the connection. The audit retains strong references, so these omissions remain observable.

Add `contextlib.closing` around those connections and retain the connection's own transaction context using `with closing(sqlite3.connect(...)) as db, db:`. Apply the same protection to the round test's fallback binding branch, which normally returns before allocation because production raises the expected overflow HTTP error. Preserve every validation assertion.

Search results were used only to locate candidate paths; actual decisions used files retrieved at the pinned working-branch commit. Original blobs: `851550899a862aa76d5b1d73dddbea65e269536b` and `c2e3b3ada042eb614eadb15d781b14b61ad05437`. The unchanged audit still fails on any leak or failed test and closes leftovers only after recording its result. No production lifetime change or audit relaxation is included.

## Complete mocked viewer payload

Original smoke blob: `f9f8c18b45a561966fca4b40b397dabbde182540`. The fixture calls `display_state`, a player-safe projection that has campaign identity but lacks the viewer-selection envelope normally added by the campaign viewer service. The actual viewer-selection script treats missing `viewer_campaigns` as no authorization choices and replaces the heading with No campaign access.

After constructing display state, assert its campaign is Default and explicitly supply the matching one-campaign viewer list, `viewer_selection_required=False` and an empty access message. This remains a mocked HTTP/WebSocket fixture, not production authorization coverage. Preserve the original heading assertion, disconnect/reconnect identity checks, mobile layout check and final page-error assertion. Production client behavior is unchanged.

## Local evidence and limits

Python 3.12.8 / SQLite 3.46.1: focused copies of the three executed SQL allocation patterns reproduced three unclosed connections with the audit's tracked-connection approach, and zero after explicit closure. Unicode, surrogate rejection and signed-64-bit binding checks remained intact. This did not execute the complete modules, model validation, production turn progression or full connection audit; matching the observed count is not a full-suite allocation trace.

The preceding investigation executed the hash-matched viewer-selection script (`63b1fd514ef72fdca94441d8d40b9e5450e5bd57`) in a Node VM with DOM doubles. A campaign-only state produced No campaign access; the matching viewer list retained Campaign: Default. This was not Chromium execution.

FastAPI and Starlette are absent locally; Playwright is importable but the full browser smoke was not run. Complete checkout, Python 3.14, zero leaks across the entire suite and the smoke test's later checks remain unverified. CI must establish those results. No passing full workflow is claimed.

## Delivery and continuity

Normal push-triggered CI is required; no skip marker or extra dispatch. README, handover index/maintenance and TODO index were reviewed. No unrelated feature-task status or application runtime changes are needed. The broader source split remains unfinished and inactive. See [validation next steps](030-validation-and-next-steps.md).
