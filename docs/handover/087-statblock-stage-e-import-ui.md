# 087 - SG-TODO-022 Stage E: Edit Monster and bulk statblock import (022.13-022.14)

[Back to handover index](../../HANDOVER.md) · [Stage D](086-statblock-stage-d-viewer.md) · [TODO 220](../todo/220-admin-statblock-viewer.md)

Date: 2026-11-17. Baseline: `4f51b26d70e568478e12b6add5617d987d7bd417` on
`features/claude-statblock`. Delivered as a zip archive; commit SHA not yet known.
This is the last planned code stage of SG-TODO-022, so its commit message omits
`[skip ci]` and CI runs (`CLAUDE_INSTRUCTIONS.md`, "Commit messages"). 022.15/022.16
(integrated verification, corrections, acceptance) follow.

## Delivered

### 022.13 - Edit Monster (`static/monster-statblock-edit.js`)

- A Statblock section in the monster Edit dialog shows the saved state (`Statblock saved
  (revision n)`, `No statblock`, loading/unavailable) and offers **Find statblock** and
  **Upload .monster file**.
- Find searches all enabled sources for the species currently in the form (so a species
  edit and a new statblock can be saved together); the original tracker source is listed
  first, disabled providers are not offered, incomplete/failed/cooling-down providers and
  omitted 5e.tools versions are stated in the chooser.
- The choice is prepared (progress, Cancel stops and releases the job) and previewed with
  the statblock renderer using the dialog's current name, species, AC and HP. **Use this
  statblock** stages it in hidden fields; **Keep current statblock** removes it again.
  Nothing is saved until **Save monster**, which saves the edit and the statblock in one
  transaction (C1 contract). Cancelling a chooser discards its unconfirmed choice;
  closing or cancelling Edit releases the staged preparation.
- Every monster save now sends `expected_values` with the previous values of the fields the
  user changed; if someone else changed one of them meanwhile the save is rejected (409)
  instead of overwriting it. Unchanged fields are not checked.
- Failures (not found, no public statblock, deadline, file errors) are shown in the chooser.

### 022.14 - selected-monster bulk import (`static/monster-statblock-bulk.js`)

- **Load statblocks** in the Monster bulk dropdown opens one row per selected monster with
  the saved state, its own choice (Keep current by default, any discovered candidate or a
  `.monster` file) and per-row notes (incomplete sources, no species, no results).
- Discovery runs in batches of at most 50 monsters, one lookup per species and source on
  the server, with progress. Rows are prepared one after another, at most two at a time;
  each row shows waiting (not yet submitted), preparing (accepted, deadline running),
  ready (with an optional preview) or failed (with Retry). Changing a row releases its
  previous preparation.
- **Apply statblocks (n)** sends only ready rows, in batches of at most 50, each atomic and
  retry-safe (operation ID). A rejected batch marks its rows with the server's reasons and
  leaves earlier batches saved; the dialog stays open for Retry. Success closes it, reloads
  the Admin state and reports the result; Cancel stops all unfinished work.
- Shared client code: `static/monster-statblock-common.js` (envelope errors, discovery,
  queue-full retry, job polling/cancel, labels). Styles: `static/monster-statblock-import.css`;
  the Admin also loads `statblocks.css` and `statblocks-render.js` for previews.

### Server

- `POST /api/statblocks/discover` accepts an optional `species` (1-100 characters) to search
  for; candidates stay bound to the saved species and tracker source, which apply checks.

## Decisions

- Discovery for Edit uses the species typed in the form; bulk uses each monster's saved species.
- The bulk dialog submits preparations itself (two at a time) rather than holding the
  server queue; a full queue is retried after a second.
- A dismissed file picker no longer closes the bulk dialog (its bubbling `cancel` event is ignored).

## Validation (Python 3.13.18, Chromium via local Google Chrome)

- `tests/test_statblock_import_browser.py` (7 tests, real scripts with an intercepted fake
  API: Edit find/preview/stage, cancel paths and released jobs, failures and file upload,
  bulk independent rows with keep-current and atomic apply, prepare failure/Retry and a
  rejected batch, row file upload, 55 monsters in discovery batches of 50 and cancel): pass.
- `tests/test_statblock_import_service.py`: new search-species test; 19 tests pass.
- `e2e/test_statblock_import.py` (real server: Edit Monster `.monster` import with the save,
  bulk import of two files shown in the statblock viewer): **not run** here (FastAPI/uvicorn
  missing). Earlier FastAPI/e2e modules from C1-D are also still unrun locally.
- Whole-module regression comparison against `4f51b26` (every `tests/test_*.py` run separately here):
  164 of 247 modules pass before and the same 164 plus the new browser module after; the rest fail
  identically (FastAPI, aiohttp, httpx2 or PyYAML missing, or browser fixtures that also time out at
  the baseline here). The full Admin page with all scripts loads in Chrome without page errors.

## Open work (022.15/022.16)

- Review this CI run, the FastAPI route tests (C1/C2) and the e2e suite including axe for the
  statblock page in both browsers; correct findings in narrow follow-ups.
- Agreement still needed on the proposed engineering safeguards (C1) and Stage A's `dataset_files` (agreed 2026-11-20, see TODO 220).
- 5e.tools `_versions` candidates and generated magic-item variants (04e.2) remain open
  (moved to SG-TODO-033 on 2026-11-20; not required for SG-TODO-022).
