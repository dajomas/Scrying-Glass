# 740 - Test consolidation (SG-TODO-023 second half)

[Back to HANDOVER index](../../HANDOVER.md)

Implementation group 5 on `features/claude`, 2026-11-22, after group 4 closed (CI
44964454668, e2e 20261122T073821Z: 137 passed). The full disposition table is in
[230 - Second half](../todo/230-test-suite-necessity-review.md#second-half-dispositions-2026-11-22).

## Changes

- `tests/test_statblock_setup_saving.py`: the Save As live-content test also asserts that
  the source setup's tracker rows keep their HP and the new setup has the live HP.
- `tests/test_statblock_stage2_contracts.py`: removed
  `test_save_as_uses_unsaved_live_content_without_replacing_source`, now fully covered by the
  test above; a comment points there.
- `tests/test_admin_asset_wiring.py`: removed `test_review_asset_has_no_untyped_pane_calls`
  (a text ban); behaviour tests cover it; a comment says where.

## Evidence

- Mutant 1 (Save As also overwrites the source setup's rows): the surviving test before the
  change passes, after the change fails (`1 != 12`).
- Mutants 2-4 (`monster-refresh-review.js` review-load error, apply error, success message
  sent with `paneNotification`): each fails the refresh-review browser tests; the script was
  restored byte for byte afterwards.
- Normalized-AST scan of all `test_*` bodies: no identical bodies.
- Full unittest suite here: 2,155 tests (from 2,157), no new failures; connection check clean
  for the three changed modules; pytest and Node unchanged.
- CI pending. No runner or workflow change; no speed-up claimed.
